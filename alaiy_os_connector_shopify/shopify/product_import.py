"""
Shopify → ERPNext product import (one-time full sync).

One-time import of all products from Shopify into ERPNext as Items.
Wipes existing product mappings (Item records without sh_shopify_product_id)
and imports fresh from Shopify source of truth.

Handles:
- Templates and variants (creates Item + item variants)
- Images (main + slideshow)
- Pricing (uses configured price list)
- Stock tracking setup
- Edge cases: missing data, duplicate SKUs, image failures, etc.
"""

from collections import Counter

import frappe
from frappe.utils import now_datetime, flt

from alaiy_os_connector_shopify.shopify.sync_guard import load_or_create_log, has_active_sync
from alaiy_os_connector_shopify.shopify.sync_engine import entities


_PRODUCTS_COUNT_QUERY = """
query { productsCount { count } }
"""

_PRODUCTS_QUERY = """
query PullProducts($after: String) {
  products(first: 50, after: $after, sortKey: CREATED_AT) {
    edges {
      node {
        legacyResourceId
        title
        bodyHtml
        vendor
        productType
        options {
          name
          values
        }
        images(first: 10) {
          nodes {
            id
            src
          }
        }
        variants(first: 100) {
          nodes {
            legacyResourceId
            sku
            title
            price
            inventoryItem {
              inventoryLevels(first: 1) {
                nodes {
                  quantities(names: ["available"]) {
                    quantity
                  }
                }
              }
            }
            selectedOptions {
              name
              value
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""


def run_full_product_import(trigger="manual", log_name=None, wipe_existing=True):
    """
    One-time import of all products from Shopify into ERPNext.

    Args:
        trigger: "manual", "scheduled", or "webhook"
        log_name: Optional existing log to reuse
        wipe_existing: If True, deletes non-linked Items to prevent duplicates

    Returns:
        Log name (for tracking progress)
    """
    log = load_or_create_log("products", trigger, log_name)

    # Concurrency check
    if has_active_sync("products", exclude_name=log.name):
        log.status = "skipped"
        log.finished_at = now_datetime()
        log.error_message = "Skipped: another products sync is already running."
        log.save(ignore_permissions=True)
        frappe.db.commit()
        return log.name

    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    try:
        # Wipe phase
        if wipe_existing:
            _wipe_unlinked_products()
            _append_log(log, "Wiped unlinked products from previous imports.")

        # Import phase
        from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
        client = ShopifyGraphQLClient()
        variables = {"after": None}

        processed = created = skipped = failed = pages = 0
        skip_reason_counts = Counter()
        skip_examples = []  # capped list of "title: reason" strings for the log

        for page_nodes in client.execute_paginated(_PRODUCTS_QUERY, variables, ["products"]):
            pages += 1
            for node in page_nodes:
                processed += 1
                try:
                    was_created, reason = _import_product(node)
                    if was_created:
                        created += 1
                    else:
                        skipped += 1
                        skip_reason_counts[reason] += 1
                        if len(skip_examples) < 30:
                            product_name = node.get("title", "Unknown")
                            skip_examples.append(f"{product_name}: {reason}")
                except Exception as exc:
                    failed += 1
                    product_name = node.get("title", "Unknown")
                    _append_log(log, f"ERROR product={product_name}: {str(exc)[:200]}")
                    frappe.log_error(
                        title=f"Shopify: product {product_name} import failed",
                        message=frappe.get_traceback(),
                    )

        log.status = "success"
        log.items_processed = processed
        log.items_created = created
        log.items_failed = failed
        log.pages_done = pages
        log.finished_at = now_datetime()
        summary = f"Imported {created} products from Shopify"
        if skipped:
            summary += f"; {skipped} skipped"
        if failed:
            summary += f"; {failed} failed"
        _append_log(log, summary)
        if skip_reason_counts:
            _append_log(log, "Skip reasons: " + ", ".join(
                f"{reason} ({count})" for reason, count in skip_reason_counts.most_common()
            ))
        for line in skip_examples:
            _append_log(log, f"SKIPPED {line}")
        log.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception:
        log.status = "failed"
        log.error_message = frappe.get_traceback()[:500]
        log.finished_at = now_datetime()
        log.save(ignore_permissions=True)
        frappe.db.commit()
        raise

    return log.name


def _wipe_unlinked_products():
    """
    Delete Item records that aren't a *completed* Shopify import:

    - Items with no sh_shopify_product_id at all -- local/manual items,
      or leftovers from an import that predates that field being set.
    - Items with sh_shopify_product_id set but no matching Shopify Synced
      Entity row -- partial leftovers from a run that inserted the
      template/item and committed, then crashed before it could finish
      (e.g. on a later variant, or before the final entities.save()).
      A Synced Entity is only ever written at the very end of a
      successful _import_product() call, so its absence means "this Item
      exists in the database but the import that created it never
      completed." Without this second pass, _import_product_with_variants
      / _import_simple_product's "does this SKU/template already exist"
      check permanently mistakes that leftover for an already-imported
      product and skips it on every future run.
    """
    unlinked = frappe.get_all(
        "Item",
        filters={"sh_shopify_product_id": ["is", "not set"]},
        pluck="name"
    )

    linked = frappe.get_all(
        "Item",
        filters={"sh_shopify_product_id": ["is", "set"]},
        fields=["name", "sh_shopify_product_id"],
    )
    synced_product_ids = set(frappe.get_all(
        "Shopify Synced Entity",
        filters={"entity_type": "product"},
        pluck="external_id",
    ))
    orphaned = [row.name for row in linked if row.sh_shopify_product_id not in synced_product_ids]

    for item_code in unlinked + orphaned:
        try:
            frappe.delete_doc("Item", item_code, force=1, ignore_permissions=True)
        except Exception:
            frappe.log_error(
                title=f"Shopify import: failed to delete unlinked item {item_code}",
                message=frappe.get_traceback()
            )

    frappe.db.commit()


def _import_product(node: dict) -> tuple:
    """
    Import a single Shopify product (template + variants) as ERPNext Item(s).

    Returns:
        (created: bool, reason: str) -- reason is always populated, even on
        success, so the caller can log exactly what happened per product
        instead of only a bare count. Skips previously vanished into a
        single aggregate number with no way to tell "already imported"
        (fine) apart from "SKU collision" (worth investigating).
    """
    product_id = str(node.get("legacyResourceId", ""))
    if not product_id:
        return False, "missing product_id"

    # Check if already imported (via Synced Entity)
    existing_entity = entities.get_by_external_id("product", product_id)
    if existing_entity:
        return False, "already imported"

    settings = frappe.get_single("Shopify Connector Settings")
    title = node.get("title", f"Product {product_id}").strip()
    description = node.get("bodyHtml", "")
    vendor = node.get("vendor", "")
    item_group = node.get("productType", "")

    variants = node.get("variants", {}).get("nodes", [])
    images = [img.get("src") for img in (node.get("images", {}).get("nodes", []) or []) if img.get("src")]

    # Case 1: Product has multiple variants → template + variant items
    if len(variants) > 1:
        option_names = [
            opt.get("name") for opt in (node.get("options") or []) if opt.get("name")
        ]
        return _import_product_with_variants(
            product_id, title, description, vendor, item_group,
            variants, images, settings, option_names
        )

    # Case 2: Single variant → simple item (no variants table)
    elif len(variants) == 1:
        return _import_simple_product(
            product_id, title, description, vendor, item_group,
            variants[0], images, settings
        )

    else:
        # No variants? Shopify always returns at least one
        frappe.log_error(
            title=f"Shopify import: product {title} has no variants",
            message=f"Product ID: {product_id}"
        )
        return False, "product has zero variants"


def _import_simple_product(
    product_id: str, title: str, description: str, vendor: str, item_group: str,
    variant: dict, images: list, settings
) -> tuple:
    """
    Import a single-variant product as a simple Item (no variants table).
    """
    sku = (variant.get("sku") or "").strip()
    if not sku:
        sku = f"SH-{product_id}"  # Fallback to Shopify ID if no SKU

    # Check if Item with this SKU already exists
    if frappe.db.exists("Item", sku):
        existing_id = frappe.db.get_value("Item", sku, "sh_shopify_product_id")
        return False, f"SKU '{sku}' already used by product_id={existing_id}"

    item_name = sku

    # A single-variant product has no real options, so Shopify names its
    # lone variant the literal placeholder "Default Title" -- using that
    # (as a naive `variant.get("title") or title` would) replaces the
    # actual product name with a meaningless generic string. There's
    # nothing distinguishing to add here, so just use the product title.
    item = frappe.new_doc("Item")
    item.item_code = item_name
    item.item_name = title
    item.description = description
    item.item_group = _ensure_item_group(item_group)
    item.brand = _ensure_brand(vendor)
    item.stock_uom = "Nos"  # Default; can be configured per variant
    item.is_stock_item = 1
    item.include_item_in_selling = 1
    item.include_item_in_buying = 1

    # Link to Shopify
    item.sh_shopify_product_id = product_id
    item.sh_shopify_variant_id = variant.get("legacyResourceId")

    # Without this flag, Item's after_insert hook (on_item_change) sees a
    # freshly-linked item whose sync_to_shopify checkbox is still unchecked
    # by default, and mistakes that for "flag was just turned off" --
    # immediately re-archiving the product we just imported back on
    # Shopify. Setting the flag makes on_item_change no-op for this insert,
    # same as it does for inbound webhook updates.
    item.flags.from_shopify_sync = True
    item.flags.ignore_permissions = True
    item.insert()
    frappe.db.commit()

    # Set pricing
    price = flt(variant.get("price") or 0)
    if price > 0:
        _set_item_price(item_name, price, settings)

    # Set opening stock from Shopify's current available quantity
    qty = _variant_available_qty(variant)
    if qty > 0:
        _set_opening_stock(item_name, qty, settings)

    # Download and set images
    if images:
        _set_item_image(item_name, images[0])
        if len(images) > 1:
            _set_item_slideshow(item_name, images, settings)

    # Create Synced Entity record
    entities.save(
        entities.get_or_new("product", "Item", item_name, product_id),
        erpnext_doctype="Item",
        erpnext_name=item_name,
        external_id=product_id,
        erpnext_fingerprint="",  # Empty for initial import
    )

    return True, "created"


def _import_product_with_variants(
    product_id: str, title: str, description: str, vendor: str, item_group: str,
    variants: list, images: list, settings, option_names: list
) -> tuple:
    """
    Import a multi-variant product as a template Item + variant Items.
    """
    # Suffixing with the Shopify product_id guarantees uniqueness -- using
    # the title alone (as before) meant two genuinely different Shopify
    # products that happen to share a title (very common in real
    # catalogs -- duplicate names across colorways/collections) collided
    # on the same item_code, so only the first ever got imported and
    # every later one was skipped forever, mistaken for "already
    # imported." item_name (set below) still carries the human title.
    slug = "".join(
        ch for ch in title.lower().replace(" ", "-") if ch.isalnum() or ch == "-"
    ).strip("-")[:60]
    template_name = f"{slug}-{product_id}" if slug else f"sh-{product_id}"

    # Check if template already exists -- since template_name is now
    # product_id-suffixed, this can only be true if the exact same
    # product_id was seen twice in this run (e.g. a pagination overlap).
    if frappe.db.exists("Item", template_name):
        return False, f"template '{template_name}' already exists (duplicate product_id in feed)"

    # ERPNext requires a has_variants=1 template to declare at least one
    # attribute (e.g. Size, Color), and every variant must carry a value
    # for each -- "Attribute table is mandatory" otherwise. Shopify's own
    # `options` field is the source of truth for the names; fall back to
    # the union of each variant's selectedOptions if that's ever empty,
    # and to a single synthetic attribute keyed off variant title as a
    # last resort so we never end up with zero attribute rows.
    if not option_names:
        seen = []
        for v in variants:
            for opt in (v.get("selectedOptions") or []):
                name = opt.get("name")
                if name and name not in seen:
                    seen.append(name)
        option_names = seen
    if not option_names:
        option_names = ["Title"]

    def _resolved_values(variant: dict) -> dict:
        """Same {option_name: value} resolution used both to pre-register
        Item Attribute Values and to set each variant's own attribute row
        -- must stay identical or a variant could get a value that was
        never registered on the attribute, which ERPNext also rejects."""
        selected = {
            opt.get("name"): opt.get("value")
            for opt in (variant.get("selectedOptions") or [])
        }
        resolved = {}
        for name in option_names:
            value = selected.get(name) or (variant.get("title") if name == "Title" else None)
            resolved[name] = (value or "").strip() or "Default"
        return resolved

    values_by_option = {name: [] for name in option_names}
    for v in variants:
        for name, value in _resolved_values(v).items():
            if value not in values_by_option[name]:
                values_by_option[name].append(value)

    for name in option_names:
        _ensure_item_attribute(name, values_by_option[name])

    # Create template Item
    template = frappe.new_doc("Item")
    template.item_code = template_name
    template.item_name = title
    template.description = description
    template.item_group = _ensure_item_group(item_group)
    template.brand = _ensure_brand(vendor)
    template.stock_uom = "Nos"
    template.has_variants = 1
    template.is_stock_item = 0  # Templates aren't stocked
    template.include_item_in_selling = 1
    template.include_item_in_buying = 1

    for name in option_names:
        template.append("attributes", {"attribute": name})

    # Link to Shopify
    template.sh_shopify_product_id = product_id

    # See matching comment in _import_simple_product: without this flag,
    # the after_insert hook would immediately re-archive this template on
    # Shopify because sync_to_shopify defaults unchecked on a fresh import.
    template.flags.from_shopify_sync = True
    template.flags.ignore_permissions = True
    template.insert()
    frappe.db.commit()

    # Create variant Items
    for idx, variant in enumerate(variants):
        sku = (variant.get("sku") or "").strip()
        if not sku:
            sku = f"{template_name}-{idx+1}"  # Fallback naming

        # Check for SKU conflict
        if frappe.db.exists("Item", sku):
            existing_id = frappe.db.get_value("Item", sku, "sh_shopify_product_id")
            frappe.log_error(
                title=f"Shopify import: variant SKU '{sku}' skipped (already used by product_id={existing_id})",
                message=f"Product ID: {product_id}, template: {template_name}",
            )
            continue  # Skip this variant if SKU exists elsewhere

        variant_name = sku

        # Shopify's own variant "title" is just the bare option value(s)
        # (e.g. "M", or "38") -- fine inside one product's own variant
        # list on Shopify, but meaningless on its own in a flat ERPNext
        # Item list next to hundreds of other variants. Build a name that
        # carries the parent product title along with the actual
        # attribute values instead of relying on Shopify's title field.
        resolved = _resolved_values(variant)
        variant_label = " / ".join(resolved.values()) if resolved else f"Variant {idx+1}"

        variant_item = frappe.new_doc("Item")
        variant_item.item_code = variant_name
        variant_item.item_name = f"{title} - {variant_label}"
        variant_item.variant_of = template_name
        variant_item.item_group = template.item_group
        variant_item.brand = template.brand
        variant_item.description = description
        variant_item.stock_uom = "Nos"
        variant_item.is_stock_item = 1
        variant_item.include_item_in_selling = 1
        variant_item.include_item_in_buying = 1

        for name, value in resolved.items():
            variant_item.append("attributes", {"attribute": name, "attribute_value": value})

        # Link to Shopify
        variant_item.sh_shopify_product_id = product_id
        variant_item.sh_shopify_variant_id = variant.get("legacyResourceId")

        variant_item.flags.from_shopify_sync = True
        variant_item.flags.ignore_permissions = True
        variant_item.insert()

        # Set pricing
        price = flt(variant.get("price") or 0)
        if price > 0:
            _set_item_price(variant_name, price, settings)

        # Set opening stock from Shopify's current available quantity
        qty = _variant_available_qty(variant)
        if qty > 0:
            _set_opening_stock(variant_name, qty, settings)

    frappe.db.commit()

    # Set images on template
    if images:
        _set_item_image(template_name, images[0])
        if len(images) > 1:
            _set_item_slideshow(template_name, images, settings)

    # Create Synced Entity record
    entities.save(
        entities.get_or_new("product", "Item", template_name, product_id),
        erpnext_doctype="Item",
        erpnext_name=template_name,
        external_id=product_id,
        erpnext_fingerprint="",
    )

    return True, "created"


def _ensure_brand(name: str) -> str:
    """
    Item.brand is also a mandatory-shaped Link field (to the Brand
    doctype), not free text -- Shopify's vendor string fails the same way
    productType does if no Brand of that exact name exists yet.
    """
    name = (name or "").strip()
    if not name:
        return None
    if frappe.db.exists("Brand", name):
        return name
    try:
        doc = frappe.new_doc("Brand")
        doc.brand = name
        doc.flags.ignore_permissions = True
        doc.insert()
        frappe.db.commit()
        return name
    except Exception:
        frappe.log_error(
            title=f"Shopify import: failed to create Brand {name}",
            message=frappe.get_traceback(),
        )
        return None


def _ensure_item_group(name: str) -> str:
    """
    Item.item_group is a mandatory Link field, not free text -- inserting
    Shopify's productType string directly (e.g. "Demo Item Group") fails
    outright if no Item Group of that exact name exists yet. Creates one
    under the root "All Item Groups" if needed, and falls back to that
    root itself if the name is blank or the create fails for any reason.
    """
    name = (name or "").strip()
    if not name:
        return "All Item Groups"
    if frappe.db.exists("Item Group", name):
        return name
    try:
        doc = frappe.new_doc("Item Group")
        doc.item_group_name = name
        doc.parent_item_group = "All Item Groups"
        doc.is_group = 0
        doc.flags.ignore_permissions = True
        doc.insert()
        frappe.db.commit()
        return name
    except Exception:
        frappe.log_error(
            title=f"Shopify import: failed to create Item Group {name}",
            message=frappe.get_traceback(),
        )
        return "All Item Groups"


def _make_attribute_abbr(value: str, existing_abbrs: set) -> str:
    """Item Attribute Value rows require a short, unique-per-attribute
    `abbr` alongside the display value -- derive one from the value itself
    and disambiguate on collision."""
    base = "".join(ch for ch in value.upper() if ch.isalnum())[:5] or "VAL"
    abbr = base
    i = 1
    while abbr in existing_abbrs:
        i += 1
        abbr = f"{base}{i}"
    return abbr


def _ensure_item_attribute(attribute_name: str, values: list):
    """
    Ensure an Item Attribute exists with this name, and that every value
    in `values` is registered in its allowed Item Attribute Value list --
    ERPNext rejects a variant whose attribute_value isn't pre-registered
    on the attribute, separately from the template needing the attribute
    declared at all.
    """
    if frappe.db.exists("Item Attribute", attribute_name):
        doc = frappe.get_doc("Item Attribute", attribute_name)
    else:
        doc = frappe.new_doc("Item Attribute")
        doc.attribute_name = attribute_name

    existing_values = {row.attribute_value for row in (doc.item_attribute_values or [])}
    existing_abbrs = {row.abbr for row in (doc.item_attribute_values or [])}
    changed = False
    for value in values:
        if not value or value in existing_values:
            continue
        abbr = _make_attribute_abbr(value, existing_abbrs)
        doc.append("item_attribute_values", {"attribute_value": value, "abbr": abbr})
        existing_values.add(value)
        existing_abbrs.add(abbr)
        changed = True

    if doc.is_new():
        doc.flags.ignore_permissions = True
        doc.insert()
        frappe.db.commit()
    elif changed:
        doc.flags.ignore_permissions = True
        doc.save()
        frappe.db.commit()


def _set_item_price(item_code: str, price: float, settings):
    """
    Set the item's selling price in the configured price list.
    """
    price_list = settings.sh_selling_price_list or "Standard Selling"

    # Ensure price list exists
    if not frappe.db.exists("Price List", price_list):
        frappe.log_error(
            title=f"Price list {price_list} not found",
            message=f"Item {item_code} will not have pricing set"
        )
        return

    try:
        item_price = frappe.get_value(
            "Item Price",
            {"item_code": item_code, "price_list": price_list},
            "name"
        )

        if item_price:
            # Update existing
            frappe.db.set_value("Item Price", item_price, "price_list_rate", price)
        else:
            # Create new
            ip = frappe.new_doc("Item Price")
            ip.item_code = item_code
            ip.price_list = price_list
            ip.price_list_rate = price
            ip.flags.ignore_permissions = True
            ip.insert()

        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Failed to set price for {item_code}",
            message=frappe.get_traceback()
        )


def _variant_available_qty(variant: dict) -> float:
    """
    Extract available quantity from the inventoryItem.inventoryLevels
    shape requested in _PRODUCTS_QUERY. Takes the first location Shopify
    returns -- fine for the common single-location shop this bulk import
    is aimed at; a multi-location shop's true total is a sum across
    inventory_sync.py's own inventory push, not this one-time import.
    """
    levels = ((variant.get("inventoryItem") or {}).get("inventoryLevels") or {}).get("nodes") or []
    if not levels:
        return 0
    quantities = levels[0].get("quantities") or []
    return flt(quantities[0].get("quantity")) if quantities else 0


def _set_opening_stock(item_code: str, qty: float, settings):
    """
    Record Shopify's current available quantity as this Item's opening
    stock via a Material Receipt Stock Entry -- the standard ERPNext way
    to set an initial stock balance (Bin.actual_qty is derived from the
    stock ledger, not directly writable). Without this, every imported
    item lands in ERPNext with zero stock regardless of what's actually
    available on Shopify.
    """
    warehouse = settings.sh_default_warehouse
    if not warehouse:
        frappe.log_error(
            title="Shopify import: no default warehouse configured",
            message=f"Item {item_code} imported with qty {qty} but no opening stock entry could be made"
        )
        return
    if not frappe.db.exists("Warehouse", warehouse):
        frappe.log_error(
            title=f"Shopify import: warehouse {warehouse} not found",
            message=f"Item {item_code} will not have opening stock set"
        )
        return

    company = frappe.db.get_value("Warehouse", warehouse, "company") or frappe.defaults.get_global_default("company")
    if not company:
        frappe.log_error(
            title="Shopify import: no company resolved for opening stock",
            message=f"Item {item_code} will not have opening stock set"
        )
        return

    cost_center = _ensure_cost_center(company)
    if not cost_center:
        frappe.log_error(
            title=f"Shopify import: no usable Cost Center for company {company}",
            message=f"Item {item_code} will not have opening stock set"
        )
        return

    # Confirmed live: a real site had zero "Stock Entry Type" master
    # records at all (Material Receipt/Issue/etc.), which is standard
    # ERPNext seed data -- every Stock Entry insert failed with
    # "Could not find Stock Entry Type: Material Receipt" regardless of
    # warehouse/cost center being correct. Self-heal the one type we
    # actually need rather than requiring console setup per client.
    if not frappe.db.exists("Stock Entry Type", "Material Receipt"):
        frappe.get_doc({
            "doctype": "Stock Entry Type",
            "name": "Material Receipt",
            "purpose": "Material Receipt",
        }).insert(ignore_permissions=True)
        frappe.db.commit()

    try:
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Receipt"
        se.company = company
        se.append("items", {
            "item_code": item_code,
            "qty": qty,
            "t_warehouse": warehouse,
            "cost_center": cost_center,
        })
        se.flags.ignore_permissions = True
        se.insert()
        se.submit()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Failed to set opening stock for {item_code}",
            message=frappe.get_traceback()
        )


def _ensure_cost_center(company: str) -> str:
    """
    Return a usable leaf Cost Center for this company, self-healing broken
    setups instead of requiring manual console fixes on every client site.

    Confirmed live: a real site's root Cost Center had its own
    parent_cost_center dangling (pointing at "<company>", a plain string
    that isn't itself a Cost Center -- the real root is always named
    "<company> - <abbr>"), which corrupted its lft/rgt to 0/0 and made
    every attempt to create a child fail with "Item cannot be added to
    its own descendants". A root's parent must be blank, not a dangling
    reference, for the nested-set tree to be valid -- clear it and
    rebuild before trying to create anything.
    """
    company_default = frappe.db.get_value("Company", company, "cost_center")
    if company_default and not frappe.db.get_value("Cost Center", company_default, "is_group"):
        return company_default

    existing_leaf = frappe.db.get_value(
        "Cost Center", {"company": company, "is_group": 0}, "name"
    )
    if existing_leaf:
        frappe.db.set_value("Company", company, "cost_center", existing_leaf)
        return existing_leaf

    abbr = frappe.db.get_value("Company", company, "abbr")
    root = f"{company} - {abbr}" if abbr else None
    if not root or not frappe.db.exists("Cost Center", root):
        return None

    parent = frappe.db.get_value("Cost Center", root, "parent_cost_center")
    if parent and parent != root and not frappe.db.exists("Cost Center", parent):
        frappe.db.set_value("Cost Center", root, "parent_cost_center", "")

    root_lft = frappe.db.get_value("Cost Center", root, "lft")
    if not root_lft:
        from frappe.utils.nestedset import rebuild_tree
        rebuild_tree("Cost Center")

    try:
        cc = frappe.new_doc("Cost Center")
        cc.cost_center_name = "Main"
        cc.parent_cost_center = root
        cc.company = company
        cc.is_group = 0
        cc.insert(ignore_permissions=True)
        frappe.db.set_value("Company", company, "cost_center", cc.name)
        frappe.db.commit()
        return cc.name
    except Exception:
        frappe.log_error(
            title=f"Shopify import: failed to auto-create Cost Center for {company}",
            message=frappe.get_traceback(),
        )
        return None


def _set_item_image(item_code: str, image_url: str):
    """
    Download image from URL and set as Item's main image.
    """
    if not image_url:
        return

    try:
        from frappe.integrations.utils import download_file
        from frappe.utils import get_url

        # Download and attach image
        file_url = download_file(image_url)
        frappe.db.set_value("Item", item_code, "image", file_url)
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Failed to download image for {item_code}",
            message=f"URL: {image_url}\n{frappe.get_traceback()}"
        )


def _set_item_slideshow(item_code: str, image_urls: list, settings):
    """
    Create a Website Slideshow from multiple images and link to Item.
    """
    if len(image_urls) < 2:
        return

    try:
        slideshow_name = f"{item_code}-images"

        # Check if slideshow already exists
        if frappe.db.exists("Website Slideshow", slideshow_name):
            return  # Don't overwrite

        slideshow = frappe.new_doc("Website Slideshow")
        slideshow.name = slideshow_name

        for image_url in image_urls[1:]:  # First image is already set as main
            file_url = None
            try:
                from frappe.integrations.utils import download_file
                file_url = download_file(image_url)
            except Exception:
                continue  # Skip failed images

            if file_url:
                slideshow.append("slideshow_items", {
                    "image": file_url,
                    "image_url": image_url,
                })

        if slideshow.slideshow_items:
            slideshow.flags.ignore_permissions = True
            slideshow.insert()

            # Link to Item
            frappe.db.set_value("Item", item_code, "slideshow", slideshow_name)
            frappe.db.commit()

    except Exception:
        frappe.log_error(
            title=f"Failed to create slideshow for {item_code}",
            message=frappe.get_traceback()
        )


def _append_log(log, message: str):
    """
    Append a line to sync log without saving.
    """
    existing = log.log_messages or ""
    log.log_messages = (existing + "\n" + message).strip()
