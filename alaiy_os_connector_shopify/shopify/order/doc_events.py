"""
Sales Order doc_event entry points (update/submit/cancel) that enqueue
Shopify push-back jobs -- moved verbatim from order_push.py, unchanged.

Never call Shopify inline inside a save/cancel transaction -- enqueue and
return, same convention as product_sync.py.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.snapshot import (
    _items_before_cache_key, _detect_items_changed, _detect_removed_variant_ids, _detect_added_items,
)
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver


def on_sales_order_update(doc, method=None):
    # Plain logger, not frappe.log_error -- these are routine trace/skip
    # points, not failures. Confirmed live: leaving debug traces on
    # log_error made Error Log indistinguishable from real crashes for
    # anyone checking it (same mistake found in tags.py during the 21-07
    # audit).
    if doc.flags.from_shopify_sync:
        frappe.logger().debug(
            f"Shopify: on_sales_order_update {doc.name} skipped, from_shopify_sync flag set")
        return
    if not doc.get("sh_shopify_order_id"):
        frappe.logger().debug(
            f"Shopify: on_sales_order_update {doc.name} skipped, no sh_shopify_order_id")
        return

    # Detect if line items changed (added, removed, or quantity/rate modified)
    before_rows = frappe.cache().get_value(_items_before_cache_key(doc.name))
    items_changed = _detect_items_changed(doc)
    removed_variant_ids = _detect_removed_variant_ids(doc) if items_changed else []
    added_items = _detect_added_items(doc) if items_changed else []
    frappe.logger().debug(
        f"Shopify: on_sales_order_update {doc.name} before_snapshot={before_rows!r} "
        f"items_changed={items_changed} removed_variant_ids={removed_variant_ids!r} "
        f"added_items={added_items!r}")
    # Consumed -- clear so a later, genuinely separate edit within the 120s
    # expiry window doesn't accidentally diff against this stale snapshot.
    frappe.cache().delete_value(_items_before_cache_key(doc.name))

    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_push.push_order_update",
        queue="short",
        timeout=60,
        order_id=doc.sh_shopify_order_id,
        sales_order=doc.name,
        status=doc.status,
        items_changed=items_changed,
        removed_variant_ids=removed_variant_ids,
        added_items=added_items,
    )


def on_sales_order_submit(doc, method=None):
    """
    The one 'vice versa' direction that was genuinely missing: a Sales
    Order created directly in Alaiy OS (not from a Shopify pull/webhook)
    never had anything pushing it to Shopify at all. Only fires for orders
    with at least one Shopify-linked Item -- an order with zero Shopify
    products has nothing meaningful to create over there.
    """
    if doc.flags.from_shopify_sync:
        return
    if doc.get("sh_shopify_order_id"):
        return  # already a Shopify-origin order, nothing to push
    # #60: Listing Variant's copy first, Item as fallback.
    if not any(
        listing_resolver.variant_id_of_item(item.item_code)
        for item in doc.items
    ):
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_push.push_order_create",
        queue="short",
        timeout=120,
        sales_order=doc.name,
    )


def on_sales_order_cancel(doc, method=None):
    if doc.flags.from_shopify_sync:
        return
    if not doc.get("sh_shopify_order_id"):
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_push.push_order_cancel",
        queue="short",
        timeout=60,
        order_id=doc.sh_shopify_order_id,
        sales_order=doc.name,
    )
