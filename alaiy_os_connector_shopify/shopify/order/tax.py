"""
Booking Shopify order tax lines (CGST/SGST/VAT/etc.) onto the Sales Order's
Sales Taxes and Charges table.

Shopify's own computed per-line amount is used rather than recalculating from
rate on the Alaiy OS side, to avoid rounding drift between the two systems.

The Tax Account is self-healed the same way warehouse/cost-center/territory
are elsewhere in this connector: an explicit setting wins, else an existing
Tax-type leaf account under the company, else one is auto-created. This is
what makes tax work out of the box instead of silently skipping (the earlier
version required sh_tax_account to be set by hand, and got reverted on a site
whose Chart of Accounts had no tax account to point it at).
"""

import frappe
from frappe.utils import flt


def _resolve_tax_account(settings):
    """
    Return a usable (non-group, enabled) Tax-type Account for booking order
    tax lines against, self-healing instead of requiring manual config:
    configured setting -> existing Tax leaf under the company -> auto-create.
    Returns None only if there's no company or account creation fails.
    """
    configured = settings.get("sh_tax_account")
    if configured and not frappe.db.get_value("Account", configured, "is_group"):
        return configured

    company = settings.sh_company or frappe.defaults.get_global_default("company")
    if not company:
        return None

    existing = frappe.db.get_value(
        "Account",
        {"company": company, "account_type": "Tax", "is_group": 0, "disabled": 0},
        "name",
    )
    if existing:
        return existing

    return _create_tax_account(company)


def _create_tax_account(company):
    """
    Auto-create a 'Shopify Tax' Tax-type leaf account under the company's
    Duties and Taxes group (or, failing that, any Liability group), mirroring
    the cost-center/warehouse self-heal pattern used elsewhere.
    """
    abbr = frappe.db.get_value("Company", company, "abbr")
    parent = None
    if abbr and frappe.db.exists("Account", f"Duties and Taxes - {abbr}"):
        parent = f"Duties and Taxes - {abbr}"
    if not parent:
        parent = frappe.db.get_value(
            "Account",
            {"company": company, "is_group": 1, "root_type": "Liability"},
            "name",
        )
    if not parent:
        frappe.log_error(
            title=f"Shopify: no Liability group to create a Tax account under for {company}",
            message="Set 'Tax Account' on Shopify Connection manually to book order tax.",
        )
        return None

    try:
        acc = frappe.new_doc("Account")
        acc.account_name = "Shopify Tax"
        acc.parent_account = parent
        acc.company = company
        acc.account_type = "Tax"
        acc.is_group = 0
        acc.insert(ignore_permissions=True)
        frappe.db.commit()
        return acc.name
    except Exception:
        frappe.log_error(
            title=f"Shopify: failed to auto-create Tax account for {company}",
            message=frappe.get_traceback(),
        )
        return None


def _append_tax_lines(so, tax_lines, taxes_included, settings):
    """
    Book each Shopify tax line onto so.taxes.

    taxes_included=False (prices are pre-tax -- the common case, and the one
    behind "only total without tax is shown"): each line is an Actual charge
    added on top using Shopify's exact computed amount.

    taxes_included=True (item prices already contain the tax): booked as an
    "On Net Total" percentage flagged included_in_print_rate, so the tax
    breakup shows without inflating the grand total (Alaiy OS forbids Actual +
    included_in_print_rate, hence the percentage form here).
    """
    if not tax_lines:
        return
    account = _resolve_tax_account(settings)
    if not account:
        frappe.log_error(
            title=f"Shopify order {so.sh_shopify_order_name or ''}: tax skipped, no tax account",
            message="Could not resolve or create a Tax account -- order imported tax-free.",
        )
        return

    for tl in tax_lines:
        rate = flt(tl.get("rate") or 0)  # Shopify sends a decimal, e.g. 0.09
        title = tl.get("title") or "Tax"
        if taxes_included:
            if rate <= 0:
                continue
            so.append("taxes", {
                "charge_type": "On Net Total",
                "account_head": account,
                "description": f"{title} ({rate * 100:.2f}%)",
                "rate": rate * 100,
                "included_in_print_rate": 1,
            })
        else:
            amount = flt(tl.get("price") or 0)
            if amount <= 0:
                continue
            description = f"{title} ({rate * 100:.2f}%)" if rate else title
            so.append("taxes", {
                "charge_type": "Actual",
                "account_head": account,
                "description": description,
                "tax_amount": amount,
            })


_ROUNDING_TOLERANCE = 0.005


def apply_rounding_adjustment(so, order: dict, settings) -> float:
    """
    Correct a small gap between Shopify's own order total and Alaiy OS's
    recalculated one, once so.grand_total exists (after insert, before
    submit) -- Shopify's booking taxes/shipping/discount as separate rows
    and letting ERPNext sum them can land a cent or two off from the total
    Shopify itself already charged the customer, from floating point or a
    tax rate that doesn't divide evenly across line amounts.

    Shopify's total is what actually got paid, so it wins: the gap is
    booked as one more Actual tax row against a write-off account, not
    silently left as a discrepancy between what this order says and what
    the customer's card was really charged.

    Runs before so.submit(), not after -- the Sales Order's own item/tax
    tables are still open at that point, so this is one more row on the
    save already in flight rather than a second full document save.

    Returns the adjustment amount applied (0 if none was needed).
    """
    shopify_total = flt(order.get("total_price"))
    if not shopify_total:
        return 0.0

    difference = flt(shopify_total - so.grand_total, 2)
    if abs(difference) <= _ROUNDING_TOLERANCE:
        return 0.0

    account = settings.get("sh_rounding_write_off_account") or frappe.get_cached_value(
        "Company", so.company, "write_off_account"
    )
    if not account:
        frappe.log_error(
            title=f"Shopify order {so.sh_shopify_order_name or so.name}: rounding gap left uncorrected",
            message=(
                f"Shopify total {shopify_total} vs Alaiy OS total {so.grand_total} "
                f"(difference {difference}). Set a Rounding Write Off Account on "
                "the Shopify Connection, or a Write Off Account on the Company, "
                "to correct this automatically."
            ),
        )
        return 0.0

    so.append("taxes", {
        "charge_type": "Actual",
        "account_head": account,
        "description": "Rounding adjustment (Shopify total)",
        "tax_amount": difference,
    })
    return difference
