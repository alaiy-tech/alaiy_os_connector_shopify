"""
Item Price / Price List helpers (selling, compare-at, cost) -- moved
verbatim from product_import.py and product_sync.py, unchanged.
"""

import frappe
from frappe.utils import flt


def _upsert_item_price(item_code: str, price_list: str, rate: float, buying: bool = False):
    """
    Get-or-create the Item Price row for (item_code, price_list) and set its
    rate. Shared by the selling / compare-at / cost setters, which differ
    only in which list they target and whether they pre-create it.
    """
    try:
        filters = {"item_code": item_code, "price_list": price_list}
        if buying:
            filters["buying"] = 1
        item_price = frappe.get_value("Item Price", filters, "name")
        if item_price:
            frappe.db.set_value("Item Price", item_price, "price_list_rate", rate)
        else:
            ip = frappe.new_doc("Item Price")
            ip.item_code = item_code
            ip.price_list = price_list
            ip.price_list_rate = rate
            if buying:
                ip.buying = 1
                ip.selling = 0
            ip.flags.ignore_permissions = True
            ip.insert()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Failed to set price ({price_list}) for {item_code}",
            message=frappe.get_traceback(),
        )


def _ensure_price_list(name: str, settings, buying: bool = False):
    """Auto-create one of our synthetic price lists, inheriting the currency
    of the configured selling list."""
    if frappe.db.exists("Price List", name):
        return
    pl = frappe.new_doc("Price List")
    pl.price_list_name = name
    pl.currency = frappe.db.get_value(
        "Price List", settings.sh_selling_price_list or "Standard Selling", "currency") or "INR"
    if buying:
        pl.buying = 1
    else:
        pl.selling = 1
    pl.flags.ignore_permissions = True
    pl.insert()
    frappe.db.commit()


def _set_item_price(item_code: str, price: float, settings):
    """Set the item's selling price in the configured price list."""
    price_list = settings.sh_selling_price_list or "Standard Selling"
    # The configured selling list is a real, admin-managed list -- unlike our
    # synthetic compare-at/cost lists, we don't auto-create it.
    if not frappe.db.exists("Price List", price_list):
        frappe.log_error(
            title=f"Price list {price_list} not found",
            message=f"Item {item_code} will not have pricing set"
        )
        return
    _upsert_item_price(item_code, price_list, price)


_COMPARE_AT_PRICE_LIST = "Shopify Compare At"


def _set_item_compare_at_price(item_code: str, price: float, settings):
    """
    Compare-at price has no dedicated field on ERPNext's Item -- reusing
    the existing Item Price / Price List mechanism (same pattern as
    _set_item_price) in a second, auto-created price list keeps this a
    plain ERPNext concept instead of a bespoke Currency field that every
    other price-list-aware report/screen wouldn't know about.
    """
    _ensure_price_list(_COMPARE_AT_PRICE_LIST, settings)
    _upsert_item_price(item_code, _COMPARE_AT_PRICE_LIST, price)


_COST_PRICE_LIST = "Shopify Cost"


def _set_item_cost(item_code: str, cost: float, settings):
    """
    Shopify's per-variant unit cost has no dedicated ERPNext Item field --
    same reasoning as _set_item_compare_at_price: a second, auto-created
    Buying price list keeps this a plain ERPNext concept (usable in
    standard costing reports) instead of a bespoke Currency field.
    """
    _ensure_price_list(_COST_PRICE_LIST, settings, buying=True)
    _upsert_item_price(item_code, _COST_PRICE_LIST, cost, buying=True)


def _price_rate(item_code: str, price_list: str, buying: bool = False) -> float:
    filters = {"item_code": item_code, "price_list": price_list}
    if buying:
        filters["buying"] = 1
    return flt(frappe.db.get_value("Item Price", filters, "price_list_rate") or 0)


def _variant_price(item_code: str, settings) -> float:
    return _price_rate(item_code, settings.sh_selling_price_list or "Standard Selling")


def _variant_compare_at_price(item_code: str) -> float:
    return _price_rate(item_code, _COMPARE_AT_PRICE_LIST)


def _variant_cost(item_code: str) -> float:
    return _price_rate(item_code, _COST_PRICE_LIST, buying=True)
