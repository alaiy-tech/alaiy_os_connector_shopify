"""
Non-line-item order money: shipping charges, order-level discounts, and custom
(non-catalog) line items pulled from Shopify onto the Sales Order.
"""

import frappe
from frappe.utils import flt


def append_shipping_charge(so, order, settings):
    """
    Book each Shopify shipping line onto the Sales Order's Sales Taxes and
    Charges table as an Actual charge, against a self-healed income account.
    """
    lines = order.get("shipping_lines") or []
    total = sum(flt(sl.get("price") or 0) for sl in lines)
    if total <= 0:
        return
    account = _resolve_shipping_account(settings)
    if not account:
        frappe.log_error(
            title=f"Shopify order {so.sh_shopify_order_name or ''}: shipping skipped, no account",
            message="Could not resolve/create a shipping income account.",
        )
        return
    title = lines[0].get("title") if lines else "Shipping"
    so.append("taxes", {
        "charge_type": "Actual",
        "account_head": account,
        "description": title or "Shipping",
        "tax_amount": total,
    })


def apply_order_discount(so, order):
    """
    Apply Shopify's order-level total discount as an ERPNext Additional Discount
    on the net total. Per-line discounts already come through in each line's
    price, so this is only the order-level remainder Shopify reports separately.
    """
    disc = flt(order.get("total_discounts") or 0)
    if disc <= 0:
        return
    so.apply_discount_on = "Net Total"
    so.discount_amount = disc


def build_custom_line_item(li, warehouse):
    """
    A Shopify line item that maps to no ERPNext Item (custom/one-off product) --
    represent it with a single shared placeholder Item ("Shopify Custom Item"),
    carrying the real title in the row description so nothing is silently
    dropped. Returns a row dict, or None if it can't be built.
    """
    item_code = _ensure_custom_item()
    if not item_code:
        return None
    from alaiy_os_connector_shopify.shopify.order.utils import _line_item_qty
    qty = _line_item_qty(li)
    if qty <= 0:
        return None
    return {
        "item_code": item_code,
        "item_name": (li.get("title") or "Custom Item")[:140],
        "description": li.get("title") or "Custom Item",
        "qty": qty,
        "rate": flt(li.get("price", 0)),
        "warehouse": warehouse,
        "delivery_date": frappe.utils.today(),
    }


def _ensure_custom_item():
    """Single shared non-stock placeholder Item for Shopify custom line items."""
    name = "Shopify Custom Item"
    if frappe.db.exists("Item", name):
        return name
    try:
        item = frappe.new_doc("Item")
        item.item_code = name
        item.item_name = name
        item.item_group = frappe.db.get_value("Item Group", {"is_group": 0}, "name") or "All Item Groups"
        item.stock_uom = "Nos"
        item.is_stock_item = 0
        item.flags.ignore_permissions = True
        item.insert()
        frappe.db.commit()
        return name
    except Exception:
        frappe.log_error(
            title="Shopify: failed to create Shopify Custom Item placeholder",
            message=frappe.get_traceback(),
        )
        return None


def _resolve_shipping_account(settings):
    company = settings.sh_company or frappe.defaults.get_global_default("company")
    if not company:
        return None
    existing = frappe.db.get_value(
        "Account",
        {"company": company, "root_type": "Income", "is_group": 0, "disabled": 0},
        "name",
    )
    if existing:
        return existing
    return None
