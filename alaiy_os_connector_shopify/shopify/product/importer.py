"""
Shopify → ERPNext product import (one-time full sync) -- moved verbatim
from product_import.py, unchanged.

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

from alaiy_os_connector_shopify.shopify.product.queries import _PRODUCTS_QUERY
from alaiy_os_connector_shopify.shopify.product.masters import _ensure_brand, _ensure_item_group, _ensure_item_attribute
from alaiy_os_connector_shopify.shopify.product.pricing import _set_item_price, _set_item_compare_at_price
from alaiy_os_connector_shopify.shopify.product.variants import _apply_variant_physical, _set_item_variant_cost, _variant_available_qty
from alaiy_os_connector_shopify.shopify.product.stock import _set_opening_stock, _default_warehouse_row
from alaiy_os_connector_shopify.shopify.product.media import _set_item_image, _set_item_slideshow
from alaiy_os_connector_shopify.shopify.product.taxonomy import ensure_shopify_category
from alaiy_os_connector_shopify.shopify.product.tags import _normalize_tags, _set_item_tags


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


def _apply_existing_variant_content(item_code: str, variant: dict, settings, product_meta: dict = None, images: list = None):
    """
    Populate price/stock/cost/weight (and, for a genuinely standalone
    item, tags/category/SEO/images) on an Item that was auto-linked to
    Shopify rather than freshly created. Auto-linking only ever wrote the
    Shopify IDs, so without this an auto-linked item showed as "synced"
    with none of Shopify's actual content ever pulled in.
    """
    item = frappe.get_doc("Item", item_code)
    _apply_variant_physical(item, variant)
    if product_meta:
        _apply_product_meta(item, product_meta)
    item.flags.from_shopify_sync = True
    item.flags.ignore_permissions = True
    item.save()
    frappe.db.commit()

    price = flt(variant.get("price") or 0)
    if price > 0:
        _set_item_price(item_code, price, settings)
    compare_at_price = flt(variant.get("compareAtPrice") or 0)
    if compare_at_price > 0:
        _set_item_compare_at_price(item_code, compare_at_price, settings)
    _set_item_variant_cost(item_code, variant, settings)

    qty = _variant_available_qty(variant)
    if qty > 0:
        _set_opening_stock(item_code, qty, settings)

    if images:
        _set_item_image(item_code, images[0])
        if len(images) > 1:
            _set_item_slideshow(item_code, images, settings)


def _apply_existing_template_content(template_name: str, product_meta: dict, images: list, settings):
    """Same idea as _apply_existing_variant_content but for the template
    side of an auto-link -- tags/category/SEO/images describe the
    product as a whole, so they land on the template, not the variant."""
    template = frappe.get_doc("Item", template_name)
    _apply_product_meta(template, product_meta)
    template.flags.from_shopify_sync = True
    template.flags.ignore_permissions = True
    template.save()
    frappe.db.commit()

    if images:
        _set_item_image(template_name, images[0])
        if len(images) > 1:
            _set_item_slideshow(template_name, images, settings)


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
        if not existing_id:
            # Auto-link the existing item -- e.g. one already created by
            # another connector (Cloudstore) importing the same product
            # by SKU before Shopify ever linked it.
            variant_of = frappe.db.get_value("Item", sku, "variant_of")
            from alaiy_os_connector_shopify.shopify.sync_engine import entities

            # If it's part of a template structure, the product-level meta
            # (tags/category/SEO/images) describes the PRODUCT, so it
            # belongs on the template, not this leaf variant.
            if variant_of:
                frappe.db.set_value("Item", variant_of, "sh_shopify_product_id", product_id)
                if product_meta:
                    _apply_existing_template_content(variant_of, product_meta, images, settings)
                entity = entities.get_or_new("product", "Item", variant_of, product_id)
                entities.save(entity, external_id=product_id, erpnext_name=variant_of)

            # Link the item itself
            frappe.db.set_value("Item", sku, "sh_shopify_product_id", product_id)
            frappe.db.set_value("Item", sku, "sh_shopify_variant_id", variant.get("legacyResourceId"))

            # Auto-linking only ever wrote the Shopify IDs -- without this,
            # an auto-linked item showed "synced" with none of Shopify's
            # actual price/stock/weight (and, for a genuinely standalone
            # item, tags/category/SEO/images) ever pulled in.
            _apply_existing_variant_content(
                sku, variant, settings,
                product_meta=None if variant_of else product_meta,
                images=None if variant_of else images,
            )

            # Save Synced Entity mapping for the simple item if no parent template
            if not variant_of:
                entity = entities.get_or_new("product", "Item", sku, product_id)
                entities.save(entity, external_id=product_id, erpnext_name=sku)

            frappe.db.commit()
            return True, f"Auto-linked existing SKU '{sku}' (and template if present) to Shopify product '{product_id}'"
        else:
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

    # Some variant SKUs may already exist under a template created by
    # another connector (e.g. Cloudstore) before Shopify ever linked
    # them. Reuse that template instead of blindly creating a second,
    # empty one -- otherwise the new Shopify template steals the
    # sh_shopify_product_id while the real content stays orphaned on the
    # original template no one links to anymore.
    reused_template_name = None
    for v in variants:
        v_sku = (v.get("sku") or "").strip()
        if not v_sku or not frappe.db.exists("Item", v_sku):
            continue
        existing_pid = frappe.db.get_value("Item", v_sku, "sh_shopify_product_id")
        # A variant already linked to THIS SAME product_id is a stale/
        # incomplete prior import (e.g. its Synced Entity row went
        # missing) -- still a valid reuse anchor. Only a different
        # product_id means it's genuinely claimed elsewhere.
        if existing_pid and existing_pid != product_id:
            continue
        existing_parent = frappe.db.get_value("Item", v_sku, "variant_of")
        if not existing_parent:
            continue
        if reused_template_name and reused_template_name != existing_parent:
            frappe.log_error(
                title=f"Shopify import: variants of product {product_id} map to multiple existing templates",
                message=f"Found both '{reused_template_name}' and '{existing_parent}' -- keeping '{reused_template_name}'.",
            )
            continue
        reused_template_name = existing_parent

    if reused_template_name:
        template_name = reused_template_name
        template = frappe.get_doc("Item", template_name)
        if not template.sh_shopify_product_id:
            frappe.db.set_value("Item", template_name, "sh_shopify_product_id", product_id)
        if product_meta:
            _apply_existing_template_content(template_name, product_meta, images, settings)
        from alaiy_os_connector_shopify.shopify.sync_engine import entities as _entities
        entity = _entities.get_or_new("product", "Item", template_name, product_id)
        _entities.save(entity, external_id=product_id, erpnext_name=template_name)
    else:
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
            if not existing_id:
                # Auto-link the existing variant
                variant_of = frappe.db.get_value("Item", sku, "variant_of") or template_name
                frappe.db.set_value("Item", sku, "sh_shopify_product_id", product_id)
                frappe.db.set_value("Item", sku, "sh_shopify_variant_id", variant.get("legacyResourceId"))
                frappe.db.set_value("Item", sku, "variant_of", variant_of)

                # Also link its parent template to Shopify
                frappe.db.set_value("Item", variant_of, "sh_shopify_product_id", product_id)

                # Auto-linking only ever wrote the Shopify IDs -- pull in
                # this variant's own price/stock/weight the same as a
                # freshly-created variant would get.
                _apply_existing_variant_content(sku, variant, settings)

                # Create Synced Entity pairing for the template/product
                from alaiy_os_connector_shopify.shopify.sync_engine import entities
                entity = entities.get_or_new("product", "Item", variant_of, product_id)
                entities.save(entity, external_id=product_id, erpnext_name=variant_of)
                continue
            elif existing_id == product_id:
                # Already correctly linked to this same product (e.g. a
                # stale/incomplete prior import) -- just make sure it's
                # under the reused template, no error needed.
                variant_of = frappe.db.get_value("Item", sku, "variant_of")
                if variant_of != template_name:
                    frappe.db.set_value("Item", sku, "variant_of", template_name)
                continue
            else:
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

    # Set images on template -- skipped when reusing an existing template,
    # since _apply_existing_template_content already handled images (and,
    # for a reused template, product_meta) above.
    if images and not reused_template_name:
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


def _apply_product_meta(item, node: dict):
    """Apply product meta to Item -- status, tags, category, collections, SEO."""
    status = (node.get("status") or "").upper()
    if status in ("ACTIVE", "DRAFT"):
        item.sh_shopify_status = "Draft" if status == "DRAFT" else "Active"
    tags = _normalize_tags(node.get("tags"))
    if tags:
        _set_item_tags(item, tags)
    collection_titles = [
        n.get("title") for n in ((node.get("collections") or {}).get("nodes") or [])
        if n.get("title")
    ]
    if collection_titles:
        from alaiy_os_connector_shopify.shopify.product.collections import _set_item_collections
        _set_item_collections(item, collection_titles)
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
