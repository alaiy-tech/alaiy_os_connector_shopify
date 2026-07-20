"""
Applying an inbound orders/updated (or orders/fulfilled) webhook to an
existing Sales Order -- moved verbatim from order_sync.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.locking import _acquire_order_lock, _release_order_lock
from alaiy_os_connector_shopify.shopify.order.upsert import get_active_sales_order, _upsert_order_unlocked
from alaiy_os_connector_shopify.shopify.order.line_items import _sync_order_line_items
from alaiy_os_connector_shopify.shopify.order.delivery_notes import _sync_fulfillments


def _update_order(order):
    """
    Acquires the SAME per-order lock _upsert_order uses (see
    _acquire_order_lock's docstring) before doing anything, then defers to
    _update_order_unlocked.
    """
    order_id = str(order.get("id", ""))
    if not order_id:
        return False
    if not _acquire_order_lock(order_id):
        frappe.log_error(
            title=f"Shopify order {order_id}: update lock timed out",
            message="Another process held this order's lock for 30s+ -- skipped this update.",
        )
        return False
    try:
        return _update_order_unlocked(order, order_id)
    finally:
        _release_order_lock(order_id)


def _update_order_unlocked(order, order_id):
    """
    Applies an orders/updated or orders/fulfilled webhook to an existing
    Sales Order. Updates status-tracking fields always. If the order hasn't
    shipped yet (no fulfillment_status indicating fulfilled/partially_fulfilled),
    also reconciles line items (add/update/remove) to match Shopify's current
    state. Falls back to a full create if we've never seen this order (e.g.
    Shopify redelivered orders/updated before orders/create ever arrived).
    """
    so_name = get_active_sales_order(order_id)
    if not so_name:
        # Already holding this order_id's lock -- call the unlocked upsert
        # directly rather than _upsert_order, which would try (harmlessly,
        # since MySQL's GET_LOCK is reentrant per-session, but needlessly)
        # to acquire the same lock again.
        return _upsert_order_unlocked(order, order_id)

    financial_status = order.get("financial_status") or ""
    fulfillment_status = order.get("fulfillment_status") or ""

    # Always update status fields
    updates = {}
    if financial_status:
        updates["sh_financial_status"] = financial_status
    if fulfillment_status:
        updates["sh_fulfillment_status"] = fulfillment_status
    if "note" in order:
        # Not gated on truthiness like the status fields above -- clearing
        # a note to empty on Shopify is a legitimate edit that should sync
        # too, not get silently ignored.
        updates["sh_shopify_notes"] = order.get("note") or ""

    if updates:
        for field, value in updates.items():
            frappe.db.set_value("Sales Order", so_name, field, value)
        frappe.db.commit()

    # State guard: only sync line items if order hasn't shipped yet
    if _can_modify_order_items(fulfillment_status):
        _sync_order_line_items(so_name, order)

    _sync_fulfillments(so_name, order.get("fulfillments") or [])

    # Payment or fulfillment landed (orders/paid, orders/fulfilled, or an
    # orders/updated flipping either) -- create the Sales Invoice if the
    # trigger is now met and we haven't already.
    from alaiy_os_connector_shopify.shopify.order.invoice import create_sales_invoice_if_paid
    create_sales_invoice_if_paid(so_name, financial_status, fulfillment_status)
    return False


def _can_modify_order_items(fulfillment_status: str) -> bool:
    """
    State guard: return True if order hasn't shipped yet, so line items can be safely modified.
    Once an order is fulfilled or partially_fulfilled, no modifications allowed.
    """
    return fulfillment_status.lower() not in ("fulfilled", "partially_fulfilled")
