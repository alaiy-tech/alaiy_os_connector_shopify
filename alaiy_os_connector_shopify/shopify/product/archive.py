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
    if item.variant_of or not item.get("sh_shopify_product_id"):
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
                "id": f"gid://shopify/Product/{item.sh_shopify_product_id}",
                "status": "ARCHIVED",
            }
        })
        errors = (data.get("productUpdate") or {}).get("userErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: archive failed for {item.name}",
                message=str(errors),
            )
    finally:
        item.unlock()
