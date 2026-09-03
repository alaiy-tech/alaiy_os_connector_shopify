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


# A cancel racing a concurrent orders/updated webhook for the same order can
# lose that race more than once, so one retry is not enough -- but the loser
# must also roll back before reloading, or every retry re-reads the same stale
# row. Both halves confirmed live.
_MAX_TIMESTAMP_RETRIES = 3


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
        with _as_administrator():
            _cancel_sales_order(so_name)


def _cancel_sales_order(so_name, _timestamp_retries=0, _po_retry_done=False, _si_retry_done=False):
    """Cancel this Sales Order, working around the real failure modes
    seen live on a genuine Shopify cancellation:

    - TimestampMismatchError: another job (e.g. line_items.py's own
      _sync_order_line_items, firing concurrently off a related
      orders/updated webhook for the same order) saved the document in
      between -- reload and retry against the fresh copy rather than
      treating a real, expected race as a hard failure.

      The retry MUST roll back first. Confirmed live on an order
      (a Sales Order): the failed cancel left its own aborted
      transaction open, so the reload inside the retry read the same stale
      timestamp and raised again 30ms later, and the order stayed
      Completed against an order Shopify had cancelled hours earlier.
      Retried a few times, not once: the racing writer is another webhook
      for the same order, and one retry can lose the race twice.
    - LinkExistsError: a Sales Invoice or Purchase Order already linked
      against this order blocks the Sales Order's own cancel. If either
      is still safe to cancel itself (nothing paid/received/billed
      against it yet), cancel it first and retry; if it's already past
      that point, don't guess -- log it for a human. Confirmed live:
      this exact gap (only the PO side was ever handled, never a linked
      Sales Invoice) left 72 real customer orders stuck permanently
      "active" for months after they were genuinely cancelled+refunded
      on Shopify, since every retry hit the same unhandled Sales Invoice
      link and gave up for good.

    Each failure mode gets its own one-shot retry, independent of the
    others, so one retry doesn't consume another's.
    """
    so = frappe.get_doc("Sales Order", so_name)
    if so.docstatus != 1:
        return
    # See _upsert_order's note on from_shopify_sync -- this cancel came FROM
    # Shopify, so the on_cancel push-back hook must not try to cancel the
    # same order on Shopify again. This webhook runs as Guest
    # (allow_guest=True endpoint) -- confirmed live, so.cancel() hit a real
    # PermissionError without this flag, same class of bug already fixed on
    # every other webhook-driven save in this file.
    so.flags.from_shopify_sync = True
    so.flags.ignore_permissions = True
    try:
        so.cancel()
        frappe.db.commit()
    except frappe.TimestampMismatchError:
        # Roll back the aborted transaction before reloading -- without this
        # the retry re-reads the same stale row and fails identically.
        frappe.db.rollback()
        if _timestamp_retries >= _MAX_TIMESTAMP_RETRIES:
            frappe.log_error(
                title=f"Shopify: cannot cancel {so_name} -- lost the write race {_timestamp_retries} times",
                message=frappe.get_traceback(),
            )
            return
        _cancel_sales_order(
            so_name,
            _timestamp_retries=_timestamp_retries + 1,
            _po_retry_done=_po_retry_done,
            _si_retry_done=_si_retry_done,
        )
    except frappe.LinkExistsError:
        if not _si_retry_done and _cancel_linked_sales_invoices(so_name):
            _cancel_sales_order(so_name, _timestamp_retries=_timestamp_retries, _po_retry_done=_po_retry_done, _si_retry_done=True)
            return
        if not _po_retry_done and _cancel_linked_purchase_orders(so_name):
            _cancel_sales_order(so_name, _timestamp_retries=_timestamp_retries, _po_retry_done=True, _si_retry_done=_si_retry_done)
            return
        frappe.log_error(
            title=f"Shopify: cannot cancel {so_name} -- Sales Invoice or Purchase Order already linked",
            message=frappe.get_traceback(),
        )


def _cancel_linked_sales_invoices(so_name):
    """Cancel every submitted Sales Invoice against this Sales Order, so
    the Sales Order's own cancel can then proceed.

    Returns False (nothing done, caller falls back to the PO check / a
    log entry) the moment any Sales Invoice is itself blocked -- e.g.
    already has a Payment Entry against it, meaning the customer already
    paid against a since-cancelled order, which is a real situation
    needing a human decision, not an automatic cancel.
    """
    si_names = frappe.get_all(
        "Sales Invoice Item", filters={"sales_order": so_name}, pluck="parent", distinct=True
    )
    si_names = frappe.get_all("Sales Invoice", filters={"name": ["in", si_names], "docstatus": 1}, pluck="name")
    if not si_names:
        return False

    for si_name in si_names:
        si = frappe.get_doc("Sales Invoice", si_name)
        si.flags.ignore_permissions = True
        try:
            si.cancel()
        except frappe.LinkExistsError:
            frappe.log_error(
                title=f"Shopify: cannot cancel Sales Invoice {si_name} for cancelled order {so_name}",
                message=frappe.get_traceback(),
            )
            return False
    frappe.db.commit()
    return True


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
