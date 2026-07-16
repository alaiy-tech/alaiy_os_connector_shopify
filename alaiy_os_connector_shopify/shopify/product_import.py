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

from alaiy_os_connector_shopify.shopify.sync_guard import (
    load_or_create_log, has_active_sync, append_log as _append_log,
)
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
        tags
        category {
          name
          fullName
        }
        seo {
          title
          description
        }
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
            compareAtPrice
            inventoryItem {
              unitCost {
                amount
              }
              measurement {
                weight {
                  value
                  unit
                }
              }
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

    settings = frappe.get_single("Shopify Connector Settings")
    try:
        settings.lock(timeout=1800)  # Lock settings document to prevent concurrent import runs
    except frappe.DocumentLockedError:
        log.status = "skipped"
        log.finished_at = now_datetime()
        log.error_message = "Skipped: another products sync/import is running (Settings document locked)."
        log.save(ignore_permissions=True)
        frappe.db.commit()
        return log.name

    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    try:
        # Wipe phase
        if wipe_existing:
            _wipe_all_items()
            _append_log(log, "Wiped all Items for a fresh import.")

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
    finally:
        try:
            settings.unlock()
        except Exception:
            pass

    return log.name


def _wipe_all_items():
    """
    Full destructive wipe of every previously-imported Shopify Item (any
    Item with sh_shopify_product_id set) before a fresh import -- but
    NOT genuinely local/manual items, which are left untouched. Per
    explicit decision: re-importing should always start Shopify-linked
    data from zero, without disturbing anything created directly in
    ERPNext.

    Deliberately scoped to Items and their direct child tables only:
    Sales Orders, Delivery Notes, Stock Entries, Stock Ledger Entries, and
    GL Entries are never touched here -- those are real transactional/
    financial records, and this function has no business deciding they
    should disappear. A Stock Entry referencing a since-deleted item_code
    is left as a harmless dangling reference rather than destroyed; the
    fresh import recreates the Item under the same item_code (SKU) and
    its own new opening-stock Stock Entry.

    Raw SQL throughout: going through frappe.delete_doc one Item at a time
    triggers on_item_delete, which enqueues a re-push-to-Shopify job per
    variant -- confirmed live to flood the job queue past its cap on a
    large catalog. Raw DELETE bypasses that entirely.
    """
    shopify_item = "(SELECT name FROM `tabItem` WHERE sh_shopify_product_id IS NOT NULL AND sh_shopify_product_id != '')"

    # Opening-stock Stock Entries are ones _set_opening_stock itself
    # creates (Material Receipt, exactly one Shopify item per entry) --
    # only those get cleared, matched by that exact shape (single line
    # item), never a manually-created multi-item Material Receipt that
    # just happens to include one of these items among others.
    own_stock_entries = """
        SELECT sed.parent FROM `tabStock Entry Detail` sed
        JOIN `tabStock Entry` se ON se.name = sed.parent
        WHERE se.stock_entry_type = 'Material Receipt'
          AND sed.item_code IN {shopify_item}
        GROUP BY sed.parent
        HAVING COUNT(*) = 1
    """.format(shopify_item=shopify_item)

    frappe.db.sql(f"DELETE FROM `tabGL Entry` WHERE voucher_type = 'Stock Entry' AND voucher_no IN ({own_stock_entries})")
    frappe.db.sql(f"DELETE FROM `tabStock Ledger Entry` WHERE voucher_type = 'Stock Entry' AND voucher_no IN ({own_stock_entries})")
    frappe.db.sql(f"DELETE FROM `tabStock Entry Detail` WHERE parent IN ({own_stock_entries})")
    frappe.db.sql(f"DELETE FROM `tabStock Entry` WHERE name IN ({own_stock_entries})")
    frappe.db.sql(f"UPDATE `tabBin` SET actual_qty = 0, projected_qty = 0, reserved_qty = 0 WHERE item_code IN {shopify_item}")

    frappe.db.sql(f"DELETE FROM `tabItem Price` WHERE item_code IN {shopify_item}")
    frappe.db.sql("DELETE FROM `tabShopify Synced Entity` WHERE entity_type = 'product'")
    frappe.db.sql(f"DELETE FROM `tabItem Default` WHERE parent IN {shopify_item}")
    frappe.db.sql(f"DELETE FROM `tabItem Variant Attribute` WHERE parent IN {shopify_item}")
    frappe.db.sql(f"DELETE FROM `tabItem Barcode` WHERE parent IN {shopify_item}")
    frappe.db.sql("DELETE FROM `tabItem` WHERE sh_shopify_product_id IS NOT NULL AND sh_shopify_product_id != ''")
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
            variants, images, settings, option_names, node
        )

    # Case 2: Single variant → simple item (no variants table)
    elif len(variants) == 1:
        return _import_simple_product(
            product_id, title, description, vendor, item_group,
            variants[0], images, settings, node
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
    variant: dict, images: list, settings, product_meta: dict = None
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
    item.sh_shopify_product_type = item_group
    item.brand = _ensure_brand(vendor)
    item.stock_uom = "Nos"  # Default; can be configured per variant
    item.is_stock_item = 1
    item.include_item_in_selling = 1
    item.include_item_in_buying = 1

    # Link to Shopify
    item.sh_shopify_product_id = product_id
    item.sh_shopify_variant_id = variant.get("legacyResourceId")

    default_warehouse_row = _default_warehouse_row(settings)
    if default_warehouse_row:
        item.append("item_defaults", default_warehouse_row)

    if product_meta:
        _apply_product_meta(item, product_meta)
    _apply_variant_physical(item, variant)

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
    compare_at_price = flt(variant.get("compareAtPrice") or 0)
    if compare_at_price > 0:
        _set_item_compare_at_price(item_name, compare_at_price, settings)
    _set_item_variant_cost(item_name, variant, settings)

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
    variants: list, images: list, settings, option_names: list, product_meta: dict = None
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
    template.sh_shopify_product_type = item_group
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

    if product_meta:
        _apply_product_meta(template, product_meta)

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
        _apply_variant_physical(variant_item, variant)

        default_warehouse_row = _default_warehouse_row(settings)
        if default_warehouse_row:
            variant_item.append("item_defaults", default_warehouse_row)

        if product_meta:
            _apply_product_meta(variant_item, product_meta)

        variant_item.flags.from_shopify_sync = True
        variant_item.flags.ignore_permissions = True
        variant_item.insert()

        # Set pricing
        price = flt(variant.get("price") or 0)
        if price > 0:
            _set_item_price(variant_name, price, settings)
        compare_at_price = flt(variant.get("compareAtPrice") or 0)
        if compare_at_price > 0:
            _set_item_compare_at_price(variant_name, compare_at_price, settings)
        _set_item_variant_cost(variant_name, variant, settings)

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


def _upsert_item_price(item_code: str, price_list: str, rate: float, buying: bool = False):
    """
    Get-or-create the Item Price row for (item_code, price_list) and set its
    rate. Shared by the selling / compare-at / cost setters, which differ
    only in which list they target and whether they pre-create it.
    """
    try:
        filters = {"item_code": item_code, "price_list": price_list}
        if buying:
            filters["buying"] = 1
        item_price = frappe.get_value("Item Price", filters, "name")
        if item_price:
            frappe.db.set_value("Item Price", item_price, "price_list_rate", rate)
        else:
            ip = frappe.new_doc("Item Price")
            ip.item_code = item_code
            ip.price_list = price_list
            ip.price_list_rate = rate
            if buying:
                ip.buying = 1
                ip.selling = 0
            ip.flags.ignore_permissions = True
            ip.insert()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Failed to set price ({price_list}) for {item_code}",
            message=frappe.get_traceback(),
        )


def _ensure_price_list(name: str, settings, buying: bool = False):
    """Auto-create one of our synthetic price lists, inheriting the currency
    of the configured selling list."""
    if frappe.db.exists("Price List", name):
        return
    pl = frappe.new_doc("Price List")
    pl.price_list_name = name
    pl.currency = frappe.db.get_value(
        "Price List", settings.sh_selling_price_list or "Standard Selling", "currency") or "INR"
    if buying:
        pl.buying = 1
    else:
        pl.selling = 1
    pl.flags.ignore_permissions = True
    pl.insert()
    frappe.db.commit()


def _set_item_price(item_code: str, price: float, settings):
    """Set the item's selling price in the configured price list."""
    price_list = settings.sh_selling_price_list or "Standard Selling"
    # The configured selling list is a real, admin-managed list -- unlike our
    # synthetic compare-at/cost lists, we don't auto-create it.
    if not frappe.db.exists("Price List", price_list):
        frappe.log_error(
            title=f"Price list {price_list} not found",
            message=f"Item {item_code} will not have pricing set"
        )
        return
    _upsert_item_price(item_code, price_list, price)


_COMPARE_AT_PRICE_LIST = "Shopify Compare At"


def _set_item_compare_at_price(item_code: str, price: float, settings):
    """
    Compare-at price has no dedicated field on ERPNext's Item -- reusing
    the existing Item Price / Price List mechanism (same pattern as
    _set_item_price) in a second, auto-created price list keeps this a
    plain ERPNext concept instead of a bespoke Currency field that every
    other price-list-aware report/screen wouldn't know about.
    """
    _ensure_price_list(_COMPARE_AT_PRICE_LIST, settings)
    _upsert_item_price(item_code, _COMPARE_AT_PRICE_LIST, price)


_COST_PRICE_LIST = "Shopify Cost"

# Shopify's GraphQL WeightUnit enum <-> a plain ERPNext UOM name. ERPNext's
# weight_uom is a Link to UOM with no fixed seeded names, so these are
# auto-created (see _ensure_uom) rather than assumed to already exist.
_WEIGHT_UNIT_TO_UOM = {
    "GRAMS": "Gram", "KILOGRAMS": "Kg", "OUNCES": "Ounce", "POUNDS": "Pound",
}
_UOM_TO_WEIGHT_UNIT = {v: k for k, v in _WEIGHT_UNIT_TO_UOM.items()}

# Shopify's REST webhook payload uses a different, lowercase-abbreviation
# weight_unit string ("g"/"kg"/"oz"/"lb") than the GraphQL WeightUnit enum
# used everywhere else -- keeping this mapping separate rather than trying
# to normalize both into one dict avoids silently mixing up the two APIs'
# conventions.
_REST_WEIGHT_UNIT_TO_UOM = {
    "g": "Gram", "kg": "Kg", "oz": "Ounce", "lb": "Pound",
}


def _ensure_uom(name: str) -> str:
    if not frappe.db.exists("UOM", name):
        frappe.get_doc({"doctype": "UOM", "uom_name": name}).insert(ignore_permissions=True)
    return name


def _set_item_cost(item_code: str, cost: float, settings):
    """
    Shopify's per-variant unit cost has no dedicated ERPNext Item field --
    same reasoning as _set_item_compare_at_price: a second, auto-created
    Buying price list keeps this a plain ERPNext concept (usable in
    standard costing reports) instead of a bespoke Currency field.
    """
    _ensure_price_list(_COST_PRICE_LIST, settings, buying=True)
    _upsert_item_price(item_code, _COST_PRICE_LIST, cost, buying=True)


def _apply_variant_physical(doc, variant: dict):
    """
    Weight lives under Shopify's inventoryItem, not the variant itself.
    Sets plain Item fields -- call BEFORE insert. Unit cost is handled
    separately by _set_item_variant_cost since it requires the Item to
    already exist (Item Price validates item_code) -- call that one AFTER
    insert.
    """
    inv = variant.get("inventoryItem") or {}
    weight = (inv.get("measurement") or {}).get("weight")
    if weight and weight.get("value"):
        doc.weight_per_unit = flt(weight["value"])
        doc.weight_uom = _ensure_uom(_WEIGHT_UNIT_TO_UOM.get(weight.get("unit"), "Kg"))


def _set_item_variant_cost(item_code: str, variant: dict, settings):
    cost = flt(((variant.get("inventoryItem") or {}).get("unitCost") or {}).get("amount") or 0)
    if cost > 0:
        _set_item_cost(item_code, cost, settings)


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


def ensure_shopify_category(full_name: str) -> str:
    """
    Ensure the nested parent-child Shopify Category tree exists for a full name path
    (e.g., 'Apparel & Accessories > Clothing > Activewear > Sweatshirts').
    Returns the leaf node document name.
    """
    parts = [p.strip() for p in full_name.split(">") if p.strip()]
    if not parts:
        return None

    parent = None
    for i, part in enumerate(parts):
        # Unique node name is the path itself to prevent collision (e.g. Sweatshirts)
        path_name = " > ".join(parts[:i+1])
        
        if not frappe.db.exists("Shopify Category", path_name):
            doc = frappe.new_doc("Shopify Category")
            doc.shopify_category_name = part
            doc.name = path_name
            if parent:
                doc.parent_shopify_category = parent
            doc.insert(ignore_permissions=True)
            parent = doc.name
        else:
            parent = path_name
            
    return parent


def _apply_product_meta(item, node: dict):
    """Apply product meta to Item -- tags, category, and SEO fields."""
    tags = node.get("tags")
    if tags:
        item.sh_shopify_tags = ", ".join(tags) if isinstance(tags, list) else tags
    category = node.get("category")
    if category:
        cat_name = category.get("fullName") or category.get("name")
        if cat_name:
            item.sh_shopify_category = ensure_shopify_category(cat_name)
    seo = node.get("seo") or {}
    item.sh_seo_title = seo.get("title") or node.get("title") or item.item_name or ""
    
    desc_val = seo.get("description")
    if not desc_val:
        desc_val = node.get("bodyHtml") or item.description or ""
        if desc_val and "<" in desc_val:
            from frappe.utils import strip_html_tags
            desc_val = strip_html_tags(desc_val)
    item.sh_seo_description = desc_val


def _default_warehouse_row(settings) -> dict:
    """
    Item Defaults row (company + default_warehouse) to append on every
    stocked Item at creation time. Without this, ERPNext has no warehouse
    to suggest when an Item is picked on any document created directly in
    the desk UI (not through our own webhook/import code, which always
    resolves a warehouse itself) -- confirmed live: manually creating a
    Sales Order for an imported item hit "Source warehouse required",
    forcing the warehouse to be typed in by hand every single time.
    """
    warehouse = settings.sh_default_warehouse
    if not warehouse or not frappe.db.exists("Warehouse", warehouse):
        return None
    company = frappe.db.get_value("Warehouse", warehouse, "company") or frappe.defaults.get_global_default("company")
    if not company:
        return None
    return {"company": company, "default_warehouse": warehouse}


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
    if frappe.db.get_value("Warehouse", warehouse, "is_group"):
        # Same class of bug order_sync._resolve_default_warehouse already
        # self-heals for orders -- confirmed live on a second client site
        # that this opening-stock path never got the same fallback, so a
        # Group Warehouse configured as default blocked every single
        # opening stock entry with "Group node warehouse is not allowed."
        leaf = frappe.db.get_value("Warehouse", {"is_group": 0, "company": frappe.db.get_value("Warehouse", warehouse, "company")}, "name")
        if not leaf:
            leaf = frappe.db.get_value("Warehouse", {"is_group": 0}, "name")
        if not leaf:
            frappe.log_error(
                title="Shopify import: Default Warehouse is a Group Warehouse, no leaf fallback found",
                message=f"Item {item_code} will not have opening stock set"
            )
            return
        warehouse = leaf

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

    # Same class of missing-company-default: ERPNext requires a Stock
    # Adjustment Account (or a per-entry Difference Account) for any
    # Material Receipt. Confirmed live: company had the account itself
    # but never had it set as the default. Pick any existing "Stock
    # Adjustment" account for this company rather than requiring
    # someone to configure it by hand on every client site.
    if not frappe.db.get_value("Company", company, "stock_adjustment_account"):
        fallback_account = frappe.db.get_value(
            "Account", {"company": company, "account_name": ["like", "%Stock Adjustment%"]}, "name"
        )
        if fallback_account:
            frappe.db.set_value("Company", company, "stock_adjustment_account", fallback_account)
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
            # Shopify's price is a selling price, not a cost basis -- we
            # have no real valuation rate to give this opening stock, and
            # ERPNext otherwise blocks submit with "Valuation Rate Missing"
            # on an item's very first stock-in.
            "allow_zero_valuation_rate": 1,
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


def _download_to_file(url: str, doctype: str, name: str) -> str:
    """
    Fetch an image URL and attach it as a File on (doctype, name); return the
    stored file_url. Raises on network/HTTP failure -- callers decide whether
    to skip or log.

    Fetches the bytes via requests (already a hard dependency, used the same
    way in graphql_client.py) and saves through save_file, a stable public
    Frappe API -- frappe.integrations.utils.download_file was removed/renamed
    in this Frappe version (confirmed live: ImportError on every image, so
    image sync was silently 100% broken), and internal module paths can move
    again.
    """
    import requests
    from frappe.utils.file_manager import save_file

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    filename = url.split("?")[0].rsplit("/", 1)[-1] or f"{name}.jpg"
    return save_file(filename, resp.content, doctype, name, is_private=0).file_url


def _set_item_image(item_code: str, image_url: str):
    """Download image from URL and set as Item's main image."""
    if not image_url:
        return
    try:
        file_url = _download_to_file(image_url, "Item", item_code)
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

    # "slideshow" is a core Item field on some ERPNext builds but not
    # others -- confirmed live on a second client site: "Unknown column
    # 'slideshow' in 'SET'" crashed every multi-image import outright.
    # Registering our own custom field with the same name risks colliding
    # with the real core field on sites where it DOES exist, so just skip
    # gracefully wherever the column itself is genuinely absent.
    if not frappe.get_meta("Item").has_field("slideshow"):
        return

    try:
        slideshow_name = f"{item_code}-images"

        # Check if slideshow already exists
        if frappe.db.exists("Website Slideshow", slideshow_name):
            return  # Don't overwrite

        slideshow = frappe.new_doc("Website Slideshow")
        # Website Slideshow autonames via "field:slideshow_name" -- setting
        # doc.name directly (the old code here) never satisfies that; only
        # setting the real slideshow_name field does. This was dormant the
        # entire time image download was broken (fixed earlier this
        # session) since insert() was never actually reached before now.
        slideshow.slideshow_name = slideshow_name

        for image_url in image_urls[1:]:  # First image is already set as main
            try:
                file_url = _download_to_file(image_url, "Website Slideshow", slideshow_name)
            except Exception:
                continue  # Skip failed images
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


