"""
Refund/return sync -- Shopify refund webhook -> Sales Return (Delivery Note,
is_return=1) + Credit Note (Sales Invoice, is_return=1) + refund Payment Entry.

Shopify's refund object is the only place a return shows up at all -- there
is no separate "return" resource on the REST/GraphQL API a merchant creates
first. refunds/create fires once the merchant (or Shopify Returns flow)
finalizes a refund, carrying which line items and how much money moved.
"""

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.order.utils import _as_administrator, _resolve_item_code
from alaiy_os_connector_shopify.shopify.order.upsert import get_active_sales_order
from alaiy_os_connector_shopify.shopify.order.warehouse import _resolve_default_warehouse
from alaiy_os_connector_shopify.shopify.order.delivery_notes import _fill_expense_accounts
from alaiy_os_connector_shopify.shopify.order.invoice import _fill_item_accounts, _resolve_bank_cash_account


def handle_refund_webhook(topic, payload):
    """refunds/create -- payload is the Shopify Refund object (REST-shaped)."""
    try:
        _process_refund(payload)
    except Exception:
        frappe.log_error(
            title=f"Shopify: refund webhook {topic} failed",
            message=frappe.get_traceback(),
        )


def _process_refund(refund):
    refund_id = str(refund.get("id") or "")
    if not refund_id:
        return
    # Idempotent: Shopify redelivers webhooks, and a merchant edit on an
    # already-processed refund shouldn't create a second return.
    if frappe.db.exists("Delivery Note", {"sh_shopify_refund_id": refund_id}):
        return

    order_id = str(refund.get("order_id") or "")
    so_name = get_active_sales_order(order_id)
    if not so_name or frappe.db.get_value("Sales Order", so_name, "docstatus") != 1:
        return

    qty_by_item = {}
    for rli in refund.get("refund_line_items") or []:
        li = rli.get("line_item") or {}
        item_code = _resolve_item_code({
            "sku": li.get("sku"), "variant_id": li.get("variant_id"), "title": li.get("title"),
        })
        if not item_code:
            continue
        qty_by_item[item_code] = qty_by_item.get(item_code, 0) + flt(rli.get("quantity", 0))

    refund_amount = sum(flt(t.get("amount")) for t in (refund.get("transactions") or [])
                         if t.get("kind") == "refund")

    with _as_administrator():
        dn_name = _make_sales_return(so_name, qty_by_item, refund_id)
        si_name = _make_credit_note(so_name, qty_by_item, refund_id)
        if si_name and refund_amount > 0:
            _refund_payment_entry(si_name, refund_amount)
    frappe.db.commit()


def _trim_return_items(doc, qty_by_item):
    """
    make_return_doc() maps every remaining line at its full (negative)
    quantity -- keep only the items and quantities this specific refund
    actually covers, same shape as delivery_notes.py's per-fulfillment trim.
    """
    kept = []
    for row in doc.items:
        refunded_qty = qty_by_item.get(row.item_code, 0)
        if refunded_qty <= 0:
            continue
        row.qty = -min(abs(row.qty), refunded_qty)
        kept.append(row)
    doc.items = kept
    return bool(doc.items)


def _land_return_in_warehouse(dn):
    """
    sh_return_warehouse if configured, else the connector's Default
    Warehouse -- same self-heal shape as warehouse.py's
    _force_valid_warehouse, kept separate here since a return's landing
    spot is deliberately allowed to differ from where orders normally ship
    FROM. Whatever's downstream (a supplier portal's own returns routing,
    a manual quality check) decides where the item really ends up from
    here -- this just gives it somewhere valid to land first.
    """
    settings = frappe.get_single("Shopify Connector Settings")
    warehouse = settings.sh_return_warehouse or _resolve_default_warehouse(settings)
    for item in dn.items:
        item.warehouse = warehouse
    dn.set_warehouse = warehouse


def _make_sales_return(so_name, qty_by_item, refund_id):
    dn_name = frappe.db.get_value(
        "Delivery Note Item", {"against_sales_order": so_name, "docstatus": 1}, "parent")
    if not dn_name:
        return None  # nothing shipped yet -- no stock to bring back

    try:
        from erpnext.controllers.sales_and_purchase_return import make_return_doc
        dn = make_return_doc("Delivery Note", dn_name)
        if not _trim_return_items(dn, qty_by_item):
            return None
        _land_return_in_warehouse(dn)
        for row in dn.items:
            row.allow_zero_valuation_rate = 1
        _fill_expense_accounts(dn)
        dn.sh_shopify_refund_id = refund_id
        dn.flags.ignore_permissions = True
        dn.insert()
        dn.submit()
        return dn.name
    except Exception:
        frappe.log_error(
            title=f"Shopify: Sales Return failed for refund {refund_id}",
            message=f"Sales Order: {so_name}\n{frappe.get_traceback()}",
        )
        return None


def _make_credit_note(so_name, qty_by_item, refund_id):
    si_name = frappe.db.get_value(
        "Sales Invoice Item", {"sales_order": so_name, "docstatus": 1}, "parent")
    if not si_name:
        return None  # not invoiced yet -- nothing to credit

    try:
        from erpnext.controllers.sales_and_purchase_return import make_return_doc
        settings = frappe.get_single("Shopify Connector Settings")
        si = make_return_doc("Sales Invoice", si_name)
        if not _trim_return_items(si, qty_by_item):
            return None
        si.update_stock = 0  # stock already returned via the Sales Return above
        _fill_item_accounts(si, settings)
        si.sh_shopify_refund_id = refund_id
        si.flags.from_shopify_sync = True
        si.flags.ignore_permissions = True
        si.insert()
        si.submit()
        return si.name
    except Exception:
        frappe.log_error(
            title=f"Shopify: Credit Note failed for refund {refund_id}",
            message=f"Sales Order: {so_name}\n{frappe.get_traceback()}",
        )
        return None


def _refund_payment_entry(si_name, refund_amount):
    """
    Shopify already sent the money back to the customer -- book a Payment
    Entry against the Credit Note so it doesn't sit open, mirroring
    invoice.py's _mark_invoice_paid on the forward side.
    """
    try:
        from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
        si = frappe.get_doc("Sales Invoice", si_name)
        paid_from = _resolve_bank_cash_account(si.company)
        if not paid_from:
            frappe.log_error(
                title=f"Shopify: no bank/cash account to refund {si_name}",
                message="Set a Default Cash/Bank Account on the Company to auto-settle Shopify refunds.",
            )
            return
        pe = get_payment_entry("Sales Invoice", si_name)
        pe.paid_from = paid_from
        pe.reference_no = si_name
        pe.posting_date = si.posting_date
        pe.reference_date = si.posting_date
        pe.flags.from_shopify_sync = True
        pe.flags.ignore_permissions = True
        pe.insert()
        pe.submit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: refund Payment Entry failed for {si_name}",
            message=frappe.get_traceback(),
        )
