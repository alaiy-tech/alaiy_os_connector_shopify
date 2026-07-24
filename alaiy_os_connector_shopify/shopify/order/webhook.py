"""
Order webhook routing and cancellation -- moved verbatim from
order_sync.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.utils import _as_administrator
from alaiy_os_connector_shopify.shopify.order.upsert import _upsert_order, get_active_sales_order
from alaiy_os_connector_shopify.shopify.order.update import _update_order


def handle_order_webhook(topic, payload):
    """
    Routes by topic for both real orders (orders/*) and draft orders
    (draft_orders/*), which both create/update/cancel Sales Orders.
    Draft orders are customer-facing real orders placed through the draft
    orders sales channel, not test/temporary objects.

    orders/create and draft_orders/create insert new Sales Orders.
    updated/fulfilled variants apply in-place (or fall back to create).
    cancelled/delete variants cancel, never hard-delete per Alaiy OS's docstatus.
    """
    try:
        if topic in ("orders/cancelled", "orders/delete", "draft_orders/delete"):
            _cancel_order(payload)
        elif topic in ("orders/create", "draft_orders/create"):
            _upsert_order(payload)
        else:
            # orders/updated, orders/fulfilled, draft_orders/update
            _update_order(payload)
    except Exception:
        frappe.log_error(
            title=f"Shopify: order webhook {topic} failed",
            message=frappe.get_traceback(),
        )


def _cancel_order(order):
    order_id = str(order.get("id", ""))
    so_name = get_active_sales_order(order_id)
    if so_name and not frappe.db.exists("Sales Order", so_name):
        # Mapping points at a Sales Order that no longer exists locally
        # (deleted directly, or the mapping otherwise went stale) -- nothing
        # to cancel, and retrying frappe.get_doc would just raise.
        frappe.logger().debug(
            f"Shopify: order cancel webhook for {order_id} skipped, "
            f"mapped Sales Order {so_name} no longer exists")
        return
    if so_name:
        so = frappe.get_doc("Sales Order", so_name)
        if so.docstatus == 1:
            # See _upsert_order's note on from_shopify_sync -- this cancel
            # came FROM Shopify, so the on_cancel push-back hook must not
            # try to cancel the same order on Shopify again. This webhook
            # runs as Guest (allow_guest=True endpoint) -- confirmed live,
            # so.cancel() hit a real PermissionError without this flag,
            # same class of bug already fixed on every other webhook-driven
            # save in this file.
            so.flags.from_shopify_sync = True
            so.flags.ignore_permissions = True
            with _as_administrator():
                so.cancel()
            frappe.db.commit()
