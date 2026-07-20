"""
Auto-create a Sales Invoice from a Shopify order once it's paid.

Shopify order -> Sales Order is the authoritative flow; this adds the billing
document. On financial_status "paid" we make + submit a Sales Invoice from the
submitted Sales Order (tax lines carry over via ERPNext's own mapping).

Gated by Shopify Connector Settings.sh_auto_sales_invoice (default on).
Idempotent: never a second invoice for a Sales Order already invoiced.
Non-stock invoice (update_stock=0) -- stock moves via the Delivery Note, not here.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.utils import _as_administrator, _to_gid
from alaiy_os_connector_shopify.shopify.order.queries import _ORDER_MARK_PAID_MUTATION


def create_sales_invoice_if_paid(so_name: str, financial_status: str):
    """
    Best-effort: create + submit a Sales Invoice for a paid order. Logs and
    returns on any problem rather than breaking the webhook/pull that calls it.
    """
    if (financial_status or "").lower() != "paid":
        return

    settings = frappe.get_single("Shopify Connector Settings")
    if not settings.get("sh_auto_sales_invoice"):
        return

    if frappe.db.get_value("Sales Order", so_name, "docstatus") != 1:
        return  # only submitted orders get invoiced (draft orders wait)

    # Idempotent: a Sales Invoice Item already pointing at this SO means it's
    # invoiced (covers a redelivered orders/paid webhook, Shopify redelivers).
    if frappe.db.exists("Sales Invoice Item", {"sales_order": so_name, "docstatus": ["<", 2]}):
        return

    try:
        from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
        with _as_administrator():
            si = make_sales_invoice(so_name)
            si.update_stock = 0
            # Mirrors every other webhook-driven save in this connector: mark
            # it as Shopify-originated and bypass the Guest permission checks
            # the allow_guest webhook context would otherwise fail.
            si.flags.from_shopify_sync = True
            si.flags.ignore_permissions = True
            si.insert()
            si.submit()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: auto Sales Invoice failed for {so_name}",
            message=frappe.get_traceback(),
        )


# ── Reverse direction: ERPNext Sales Invoice -> mark Shopify order paid ────────

def _linked_shopify_order_id(doc):
    """Shopify order id behind a Sales Invoice, via its items' Sales Order."""
    for row in (doc.items or []):
        so = row.get("sales_order")
        if not so:
            continue
        oid = frappe.db.get_value("Sales Order", so, "sh_shopify_order_id")
        if oid:
            return oid
    return None


def on_sales_invoice_submit(doc, method=None):
    """
    Submitting a Sales Invoice in ERPNext for a Shopify-originated order marks
    that order Paid on Shopify (orderMarkAsPaid). Skipped for invoices we
    ourselves auto-created from an already-paid Shopify order (from_shopify_sync)
    -- that order is already paid there, pushing back would just error.
    """
    if doc.flags.from_shopify_sync:
        return
    order_id = _linked_shopify_order_id(doc)
    if not order_id:
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_sync.push_order_paid",
        queue="short",
        timeout=60,
        order_id=order_id,
        sales_invoice=doc.name,
    )


def push_order_paid(order_id: str, sales_invoice: str):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    try:
        client = ShopifyGraphQLClient()
        data = client.execute(_ORDER_MARK_PAID_MUTATION, {"input": {"id": _to_gid(order_id)}})
        errors = (data.get("orderMarkAsPaid") or {}).get("userErrors") or []
        if errors:
            # Most common: order already fully paid on Shopify -- benign.
            frappe.log_error(
                title=f"Shopify: orderMarkAsPaid userErrors for {sales_invoice}",
                message=str(errors),
            )
    except Exception:
        frappe.log_error(
            title=f"Shopify: mark-as-paid push failed for {sales_invoice}",
            message=frappe.get_traceback(),
        )
