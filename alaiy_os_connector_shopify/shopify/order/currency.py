"""
Multi-currency support for Shopify orders whose currency differs from the
Company's default accounting currency (e.g. a USD Shopify store booking into
an INR company). Without this, Alaiy OS's own Sales Invoice validation throws
"Party Account ... currency (INR) and document currency (USD) should be same"
the moment financial documents are created, since the default Debtors account
is single-currency.
"""

import frappe


def resolve_order_currency(order, company):
    """
    The currency this order's amounts are denominated in (Shopify's
    currencyCode -- shopMoney amounts, which is everything this connector
    reads, are always in this currency). Falls back to the company's default
    currency when Shopify didn't report one (e.g. some webhook payload shapes).
    """
    currency = (order.get("currency") or "").strip().upper()
    if currency:
        return currency
    return frappe.get_cached_value("Company", company, "default_currency")


def ensure_customer_currency_account(customer_name, company, currency):
    """
    Make sure `customer_name` has a Receivable account in `currency` under
    `company`, and that it's registered as this customer's Party Account for
    that company (Customer.accounts child table) -- this is what Alaiy OS's
    own party-account resolution uses to pick a non-default receivable
    account, avoiding the single-currency default Debtors account.

    No-op if `currency` already matches the company's default currency --
    the default Debtors account already handles that case.
    """
    default_currency = frappe.get_cached_value("Company", company, "default_currency")
    if not currency or currency == default_currency:
        return

    account = _ensure_currency_receivable_account(company, currency)
    if not account:
        return

    customer = frappe.get_doc("Customer", customer_name)
    changed = False

    # Alaiy OS's own validation (validate_currency_for_receivable_payable_and_advance_account)
    # requires the receivable account's currency to match either the Customer's
    # own default_currency or the Company's default currency -- setting only the
    # Party Account row (below) isn't enough on its own.
    if customer.get("default_currency") != currency:
        customer.default_currency = currency
        changed = True

    account_row_found = False
    for row in customer.get("accounts") or []:
        if row.company == company:
            account_row_found = True
            if row.account != account:
                row.account = account
                changed = True
            break
    if not account_row_found:
        customer.append("accounts", {"company": company, "account": account})
        changed = True

    if changed:
        customer.flags.ignore_permissions = True
        customer.save()


def _ensure_currency_receivable_account(company, currency):
    """Find or create a Receivable-type Account in `currency` under `company`,
    named e.g. "Debtors USD - <abbr>", parented under the same group as the
    company's default Debtors account (or an Assets group as a fallback)."""
    abbr = frappe.get_cached_value("Company", company, "abbr")
    name = f"Debtors {currency} - {abbr}" if abbr else f"Debtors {currency}"
    if frappe.db.exists("Account", name):
        return name

    default_receivable = frappe.get_cached_value("Company", company, "default_receivable_account")
    parent = None
    if default_receivable:
        parent = frappe.db.get_value("Account", default_receivable, "parent_account")
    if not parent:
        parent = frappe.db.get_value(
            "Account", {"company": company, "is_group": 1, "root_type": "Asset"}, "name")
    if not parent:
        frappe.log_error(
            title=f"Shopify: no Asset group to create a {currency} Debtors account under for {company}",
            message=f"Create a {currency} Receivable account manually and add it to the customer's Party Accounts.",
        )
        return None

    try:
        acc = frappe.new_doc("Account")
        acc.account_name = f"Debtors {currency}"
        acc.parent_account = parent
        acc.company = company
        acc.account_type = "Receivable"
        acc.account_currency = currency
        acc.is_group = 0
        acc.insert(ignore_permissions=True)
        frappe.db.commit()
        return acc.name
    except Exception:
        frappe.log_error(
            title=f"Shopify: failed to auto-create {currency} Debtors account for {company}",
            message=frappe.get_traceback(),
        )
        return None


def get_order_exchange_rate(from_currency, to_currency, transaction_date=None):
    """
    Conversion rate from the order's currency to the company's currency, for
    Sales Order.conversion_rate. Uses Alaiy OS's own exchange-rate lookup
    (Currency Exchange records / configured provider); falls back to 1 if it
    can't be resolved rather than blocking order import over a missing rate.
    """
    if from_currency == to_currency:
        return 1.0
    try:
        from erpnext.setup.utils import get_exchange_rate
        rate = get_exchange_rate(from_currency, to_currency, transaction_date)
        return rate or 1.0
    except Exception:
        frappe.log_error(
            title=f"Shopify: could not resolve exchange rate {from_currency}->{to_currency}",
            message=frappe.get_traceback(),
        )
        return 1.0
