"""
Order webhook routing and cancellation -- moved verbatim from
order_sync.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.utils import _as_administrator
from alaiy_os_connector_shopify.shopify.order.upsert import _upsert_order, get_active_sales_order
from alaiy_os_connector_shopify.shopify.order.update import _update_order
from alaiy_os_connector_shopify.shopify.order.delivery_notes import _sync_tracking


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


def handle_fulfillment_webhook(topic, payload):
    """fulfillments/create, fulfillments/update -- payload is the
    Fulfillment object itself, carrying tracking info. See _sync_tracking."""
    try:
        _sync_tracking(payload)
    except Exception:
        frappe.log_error(
            title=f"Shopify: fulfillment webhook {topic} failed",
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
                try:
                    so.cancel()
                    frappe.db.commit()
                except frappe.LinkExistsError:
                    # A Purchase Order already routed against this order
                    # (Solist's per-supplier PO routing) blocks the Sales
                    # Order's own cancel -- confirmed live, this crashed the
                    # whole webhook and left the order's status un-synced
                    # with Shopify's real cancellation. If the PO is still
                    # safe to cancel itself (nothing received/billed against
                    # it yet), cancel it first so the Sales Order's cancel
                    # can then go through cleanly; if the PO is already past
                    # that point, fall back to logging rather than guessing.
                    if not _cancel_linked_purchase_orders(so_name):
                        frappe.log_error(
                            title=f"Shopify: cannot cancel {so_name} -- Purchase Order already linked",
                            message=frappe.get_traceback(),
                        )
                        return
                    so.reload()
                    so.cancel()
                    frappe.db.commit()


def _cancel_linked_purchase_orders(so_name):
    """Cancel every submitted Purchase Order routed against this Sales
    Order, so the Sales Order's own cancel can then proceed.

    Returns False (nothing done, caller falls back to logging) the moment
    any PO is itself blocked -- e.g. already has a Purchase Receipt or
    Purchase Invoice against it, meaning the supplier already received or
    was billed for stock against a since-cancelled customer order, which
    is a real situation needing a human decision, not an automatic cancel.
    """
    po_names = frappe.get_all(
        "Purchase Order",
        filters={"os_sales_order": so_name, "docstatus": 1},
        pluck="name",
    )
    if not po_names:
        return False

    for po_name in po_names:
        po = frappe.get_doc("Purchase Order", po_name)
        po.flags.ignore_permissions = True
        try:
            po.cancel()
        except frappe.LinkExistsError:
            frappe.log_error(
                title=f"Shopify: cannot cancel Purchase Order {po_name} for cancelled order {so_name}",
                message=frappe.get_traceback(),
            )
            return False
    frappe.db.commit()
    return True
