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
            _ensure_round_off_account(si.company)
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
    cost_center = _resolve_cost_center(si.company, settings.sh_cost_center)
    for row in si.items:
        if income and not row.income_account:
            row.income_account = income
        if cost_center and not row.cost_center:
            row.cost_center = cost_center


def _resolve_cost_center(company, configured):
    """
    Same self-heal shape as _resolve_income_account/_resolve_bank_cash_account:
    a configured sh_cost_center or Company.cost_center that turns out to be a
    GROUP cost center is invalid for any real transaction ("Cost Center X is a
    group cost center and group cost centers cannot be used in transactions")
    -- confirmed live, this crashed every auto Sales Invoice on a real site.
    Falls back to the same leaf-resolving self-heal product import already
    uses for opening stock, instead of requiring a manual settings fix.
    """
    if configured and not frappe.db.get_value("Cost Center", configured, "is_group"):
        return configured
    company_default = frappe.get_cached_value("Company", company, "cost_center")
    if company_default and not frappe.db.get_value("Cost Center", company_default, "is_group"):
        return company_default
    from alaiy_os_connector_shopify.shopify.product.masters import _ensure_cost_center
    return _ensure_cost_center(company)


def _ensure_round_off_account(company):
    """
    Self-heal, same shape as _resolve_income_account/_resolve_cost_center:
    ERPNext requires a Round Off Account on the Company to post the tiny
    precision-loss GL entry a submitted invoice can carry -- confirmed live,
    a Company with none configured crashes every auto Sales Invoice with
    "Please mention Round Off Account". Reuse an existing one if the
    Company (or the standard Chart of Accounts) already has it, else
    create one, rather than requiring a manual Company settings edit
    before Shopify orders can invoice at all.
    """
    if frappe.get_cached_value("Company", company, "round_off_account"):
        return
    existing = frappe.db.get_value(
        "Account",
        {"company": company, "account_name": ["like", "Round Off%"], "is_group": 0, "disabled": 0},
        "name",
    )
    if not existing:
        existing = frappe.db.get_value(
            "Account",
            {"company": company, "root_type": "Expense", "account_type": "Round Off", "is_group": 0},
            "name",
        )
    if not existing:
        abbr = frappe.db.get_value("Company", company, "abbr")
        parent = frappe.db.get_value(
            "Account", {"company": company, "is_group": 1, "root_type": "Expense",
                        "account_name": ["like", "Indirect Expenses%"]}, "name"
        ) or frappe.db.get_value("Account", {"company": company, "is_group": 1, "root_type": "Expense"}, "name")
        if not parent:
            frappe.log_error(
                title=f"Shopify: no Expense group to create a Round Off account under for {company}",
                message="Set a Round Off Account on the Company to enable auto Sales Invoice.",
            )
            return
        try:
            acc = frappe.new_doc("Account")
            acc.account_name = "Round Off"
            acc.parent_account = parent
            acc.company = company
            acc.account_type = "Round Off"
            acc.is_group = 0
            acc.insert(ignore_permissions=True)
            existing = acc.name
        except Exception:
            frappe.log_error(
                title=f"Shopify: failed to auto-create Round Off account for {company}",
                message=frappe.get_traceback(),
            )
            return
    frappe.db.set_value("Company", company, "round_off_account", existing)
    frappe.db.commit()


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
