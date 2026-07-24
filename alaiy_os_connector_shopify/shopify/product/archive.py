"""
Product archive-on-Shopify -- moved verbatim from product_sync.py,
unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
from alaiy_os_connector_shopify.shopify.product.queries import _PRODUCT_UPDATE_MUTATION
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver

LOCK_TIMEOUT_SECONDS = 30


def archive_item(item_code: str):
    """Called when the Listing is disabled/trashed -- or the Item disabled --
    on a template that's already linked. Archives the Shopify product
    (hidden from sales channels, order history intact) by setting its status
    to ARCHIVED via the productUpdate mutation."""
    item = frappe.get_doc("Item", item_code)
    if item.variant_of:
        return
    # Prefer the Listing's copy of the id (dual-written on every push),
    # fall back to Item's -- Item stays the ultimate owner until every read
    # site has moved, but reads now go through the Listing first.
    listing = listing_resolver.get_listing(item.name)
    product_id = (listing.sh_shopify_product_id if listing else None) or item.get("sh_shopify_product_id")
    if not product_id:
        return
    if listing_resolver.is_enabled(item):
        # Re-enabled before this job ran -- don't archive what should stay active.
        return

    try:
        item.lock(timeout=LOCK_TIMEOUT_SECONDS)
    except frappe.DocumentLockedError:
        return

    try:
        item = frappe.get_doc("Item", item.name)
        client = ShopifyGraphQLClient()

        data = client.execute(_PRODUCT_UPDATE_MUTATION, {
            "input": {
                "id": f"gid://shopify/Product/{product_id}",
                "status": "ARCHIVED",
            }
        })
        errors = (data.get("productUpdate") or {}).get("userErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: archive failed for {item.name}",
                message=str(errors),
            )
        else:
            # Clear fingerprint on successful archive so a subsequent push_item
            # (when re-enabled or unarchived) detects the status change and pushes.
            from alaiy_os_connector_shopify.shopify.sync_engine import entities
            entity = entities.get_by_erpnext("product", "Item", item.name)
            if entity:
                entity.erpnext_fingerprint = None
                entity.save(ignore_permissions=True)
                frappe.db.commit()
    finally:
        item.unlock()
