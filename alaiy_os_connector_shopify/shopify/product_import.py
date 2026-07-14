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
            weight
            weightUnit
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

        for page_nodes in client.execute_paginated(_PRODUCTS_QUERY, variables, ["products"]):
            pages += 1
            for node in page_nodes:
                processed += 1
                try:
                    if _import_product(node):
                        created += 1
                    else:
                        skipped += 1
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
    Delete all Item records that DON'T have a sh_shopify_product_id.
    These are local items from previous imports or manual creation.
    Items with sh_shopify_product_id are from Shopify and will be updated.
    """
    # Find all items without shopify linkage
    unlinked = frappe.get_all(
        "Item",
        filters={"sh_shopify_product_id": ["is", "not set"]},
        pluck="name"
    )

    for item_code in unlinked:
        try:
            frappe.delete_doc("Item", item_code, force=1, ignore_permissions=True)
        except Exception as exc:
            frappe.log_error(
                title=f"Shopify import: failed to delete unlinked item {item_code}",
                message=str(exc)
            )

    frappe.db.commit()


def _import_product(node: dict) -> bool:
    """
    Import a single Shopify product (template + variants) as ERPNext Item(s).

    Returns:
        True if created, False if skipped (already exists)
    """
    product_id = str(node.get("legacyResourceId", ""))
    if not product_id:
        return False

    # Check if already imported (via Synced Entity)
    existing_entity = entities.get_by_external_id("product", product_id)
    if existing_entity:
        return False  # Already imported

    settings = frappe.get_single("Shopify Connector Settings")
    title = node.get("title", f"Product {product_id}").strip()
    description = node.get("bodyHtml", "")
    vendor = node.get("vendor", "")
    item_group = node.get("productType", "")

    variants = node.get("variants", {}).get("nodes", [])
    images = [img.get("src") for img in (node.get("images", {}).get("nodes", []) or []) if img.get("src")]

    # Case 1: Product has multiple variants → template + variant items
    if len(variants) > 1:
        return _import_product_with_variants(
            product_id, title, description, vendor, item_group,
            variants, images, settings
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
        return False


def _import_simple_product(
    product_id: str, title: str, description: str, vendor: str, item_group: str,
    variant: dict, images: list, settings
) -> bool:
    """
    Import a single-variant product as a simple Item (no variants table).
    """
    sku = (variant.get("sku") or "").strip()
    if not sku:
        sku = f"SH-{product_id}"  # Fallback to Shopify ID if no SKU

    # Check if Item with this SKU already exists
    if frappe.db.exists("Item", sku):
        return False  # SKU conflict; skip

    item_name = sku

    item = frappe.new_doc("Item")
    item.item_code = item_name
    item.item_name = variant.get("title", title).strip() or title
    item.description = description
    item.item_group = item_group or "All Item Groups"
    item.brand = vendor
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

    return True


def _import_product_with_variants(
    product_id: str, title: str, description: str, vendor: str, item_group: str,
    variants: list, images: list, settings
) -> bool:
    """
    Import a multi-variant product as a template Item + variant Items.
    """
    template_name = title.replace(" ", "-").lower()[:100]

    # Check if template already exists
    if frappe.db.exists("Item", template_name):
        return False  # Template conflict; skip

    # Create template Item
    template = frappe.new_doc("Item")
    template.item_code = template_name
    template.item_name = title
    template.description = description
    template.item_group = item_group or "All Item Groups"
    template.brand = vendor
    template.stock_uom = "Nos"
    template.has_variants = 1
    template.is_stock_item = 0  # Templates aren't stocked
    template.include_item_in_selling = 1
    template.include_item_in_buying = 1

    # Link to Shopify
    template.sh_shopify_product_id = product_id

    # See matching comment in _import_simple_product: without this flag,
    # the after_insert hook would immediately re-archive this template on
    # Shopify because sync_to_shopify defaults unchecked on a fresh import.
    template.flags.from_shopify_sync = True
    template.flags.ignore_permissions = True
    template.insert()
    frappe.db.commit()

    # Detect variant attributes (e.g., Size, Color)
    # For now, use a simple heuristic: variant titles as fallback attributes
    # In production, this should be enhanced to parse Shopify's options field

    # Create variant Items
    for idx, variant in enumerate(variants):
        sku = (variant.get("sku") or "").strip()
        if not sku:
            sku = f"{template_name}-{idx+1}"  # Fallback naming

        # Check for SKU conflict
        if frappe.db.exists("Item", sku):
            continue  # Skip this variant if SKU exists elsewhere

        variant_name = sku

        variant_item = frappe.new_doc("Item")
        variant_item.item_code = variant_name
        variant_item.item_name = variant.get("title", f"{title} - {idx+1}").strip()
        variant_item.variant_of = template_name
        variant_item.description = description
        variant_item.stock_uom = "Nos"
        variant_item.is_stock_item = 1
        variant_item.include_item_in_selling = 1
        variant_item.include_item_in_buying = 1

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

    return True


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
    except Exception as exc:
        frappe.log_error(
            title=f"Failed to set price for {item_code}",
            message=str(exc)
        )


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
    except Exception as exc:
        frappe.log_error(
            title=f"Failed to download image for {item_code}",
            message=f"URL: {image_url}\nError: {str(exc)}"
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

    except Exception as exc:
        frappe.log_error(
            title=f"Failed to create slideshow for {item_code}",
            message=str(exc)
        )


def _append_log(log, message: str):
    """
    Append a line to sync log without saving.
    """
    existing = log.log_messages or ""
    log.log_messages = (existing + "\n" + message).strip()
