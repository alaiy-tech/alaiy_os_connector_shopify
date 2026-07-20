"""
Auto-create a Sales Invoice from a Shopify order once it's paid.

Shopify order -> Sales Order is the authoritative flow; this adds the billing
document. On financial_status "paid" we make + submit a Sales Invoice from the
submitted Sales Order (tax lines carry over via Alaiy OS's own mapping).

Gated by Shopify Connector Settings.sh_auto_sales_invoice (default on).
Idempotent: never a second invoice for a Sales Order already invoiced.
Non-stock invoice (update_stock=0) -- stock moves via the Delivery Note, not here.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.utils import _as_administrator, _to_gid
from alaiy_os_connector_shopify.shopify.order.queries import _ORDER_MARK_PAID_MUTATION


def create_sales_invoice_if_paid(so_name: str, financial_status: str, fulfillment_status: str = ""):
    """
    Best-effort: create + submit a Sales Invoice once the order meets the
    configured trigger. Logs and returns on any problem rather than breaking
    the webhook/pull that calls it.

    Trigger (Shopify Connector Settings.sh_invoice_trigger):
    - "Paid and Fulfilled" (default): invoice only when the order is paid AND
      shipped. This is what makes COD work correctly -- a COD order is pending
      until the merchant marks it paid on delivery, and only then (paid +
      fulfilled) does it invoice. Prepaid orders wait until shipped.
    - "Paid": invoice as soon as it's paid, regardless of fulfillment.
    """
    settings = frappe.get_single("Shopify Connector Settings")
    if not settings.get("sh_auto_sales_invoice"):
        return

    paid = (financial_status or "").lower() == "paid"
    fulfilled = (fulfillment_status or "").lower() in ("fulfilled", "partially_fulfilled")
    trigger = settings.get("sh_invoice_trigger") or "Paid and Fulfilled"
    if not paid:
        return
    if trigger == "Paid and Fulfilled" and not fulfilled:
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
            _fill_item_accounts(si, settings)
            # Mirrors every other webhook-driven save in this connector: mark
            # it as Shopify-originated and bypass the Guest permission checks
            # the allow_guest webhook context would otherwise fail.
            si.flags.from_shopify_sync = True
            si.flags.ignore_permissions = True
            si.insert()
            si.submit()
            # Shopify already collected the money -- book a Payment Entry so the
            # invoice shows Paid, not Unpaid.
            _mark_invoice_paid(si, settings)
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: auto Sales Invoice failed for {so_name}",
            message=frappe.get_traceback(),
        )


def _mark_invoice_paid(si, settings):
    """
    Full-payment Payment Entry against the invoice, so it reads Paid. Best-effort:
    the invoice still stands (as Unpaid) if payment booking fails.
    """
    try:
        from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
        paid_to = _resolve_bank_cash_account(si.company)
        if not paid_to:
            frappe.log_error(
                title=f"Shopify: no bank/cash account to mark {si.name} paid",
                message="Set a Default Cash/Bank Account on the Company to auto-mark Shopify invoices Paid.",
            )
            return
        pe = get_payment_entry("Sales Invoice", si.name)
        pe.paid_to = paid_to
        pe.reference_no = si.name
        pe.reference_date = frappe.utils.today()
        pe.flags.from_shopify_sync = True
        pe.flags.ignore_permissions = True
        pe.insert()
        pe.submit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: failed to mark invoice {si.name} paid",
            message=frappe.get_traceback(),
        )


def _resolve_bank_cash_account(company):
    for fieldname in ("default_cash_account", "default_bank_account"):
        acc = frappe.get_cached_value("Company", company, fieldname)
        if acc and not frappe.db.get_value("Account", acc, "is_group"):
            return acc
    return frappe.db.get_value(
        "Account",
        {"company": company, "account_type": ["in", ["Cash", "Bank"]], "is_group": 0, "disabled": 0},
        "name",
    )


def _fill_item_accounts(si, settings):
    """
    Force a valid Income Account (and cost center) onto every invoice row.
    Confirmed live: neither the Item nor the Company carried a default income
    account, so Alaiy OS rejected the invoice ("Income Account None does not
    belong to the company"). Self-heal one rather than making the merchant
    configure accounts by hand -- same pattern as warehouse/tax self-heal.
    """
    income = _resolve_income_account(si.company)
    cost_center = settings.sh_cost_center or frappe.get_cached_value(
        "Company", si.company, "cost_center")
    for row in si.items:
        if income and not row.income_account:
            row.income_account = income
        if cost_center and not row.cost_center:
            row.cost_center = cost_center


def _resolve_income_account(company):
    configured = frappe.get_cached_value("Company", company, "default_income_account")
    if configured and not frappe.db.get_value("Account", configured, "is_group"):
        return configured
    existing = frappe.db.get_value(
        "Account",
        {"company": company, "root_type": "Income", "is_group": 0, "disabled": 0},
        "name",
    )
    if existing:
        return existing
    return _create_income_account(company)


def _create_income_account(company):
    abbr = frappe.db.get_value("Company", company, "abbr")
    parent = None
    for candidate in (f"Direct Income - {abbr}", f"Income - {abbr}"):
        if abbr and frappe.db.exists("Account", candidate):
            parent = candidate
            break
    if not parent:
        parent = frappe.db.get_value(
            "Account", {"company": company, "is_group": 1, "root_type": "Income"}, "name")
    if not parent:
        frappe.log_error(
            title=f"Shopify: no Income group to create a Sales account under for {company}",
            message="Set a Default Income Account on the Company to enable auto Sales Invoice.",
        )
        return None
    try:
        acc = frappe.new_doc("Account")
        acc.account_name = "Shopify Sales"
        acc.parent_account = parent
        acc.company = company
        acc.account_type = "Income Account"
        acc.is_group = 0
        acc.insert(ignore_permissions=True)
        frappe.db.commit()
        return acc.name
    except Exception:
        frappe.log_error(
            title=f"Shopify: failed to auto-create Income account for {company}",
            message=frappe.get_traceback(),
        )
        return None


# ── Reverse direction: Alaiy OS Sales Invoice -> mark Shopify order paid ────────

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
    Submitting a Sales Invoice in Alaiy OS for a Shopify-originated order marks
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
