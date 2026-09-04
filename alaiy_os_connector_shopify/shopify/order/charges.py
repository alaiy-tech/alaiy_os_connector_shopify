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
    Apply Shopify's order-level total discount as an Alaiy OS Additional Discount
    on the net total. Per-line discounts already come through in each line's
    price, so this is only the order-level remainder Shopify reports separately.
    """
    disc = flt(order.get("total_discounts") or 0)
    if disc <= 0:
        return
    so.apply_discount_on = "Net Total"
    so.discount_amount = disc


def build_custom_line_item(li, warehouse, delivery_date=None):
    """
    A Shopify line item that maps to no Alaiy OS Item -- a one-off typed onto
    the order, or a product since deleted from Shopify -- represented by a
    placeholder Item of its own, named after the product.

    One placeholder PER PRODUCT, not one shared between them. ERPNext refuses
    two rows with the same item_code on a Sales Order, so a shared placeholder
    forced _merge_duplicate_item_rows to crush every unresolvable line into a
    single row: confirmed live, six distinct Damiani products worth $26,960
    arrived as one row of qty 6, and nothing downstream could tell them apart
    again. Returns a row dict, or None if it can't be built.
    """
    item_code = _ensure_custom_item(li)
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
        # Real getdate() object, not frappe.utils.today()'s string -- mixing
        # a str and a datetime.date across line item rows crashed ERPNext's
        # own validate_delivery_date() (max() can't compare str to date).
        "delivery_date": delivery_date or frappe.utils.getdate(),
    }


#: Every placeholder Item's code starts with this. Downstream code identifies
#: a placeholder line by the prefix rather than one exact name -- see
#: CUSTOM_LINE_ITEM in the client app's order_routing.
CUSTOM_ITEM_PREFIX = "Shopify Custom Item"


def _custom_item_code(li):
    """A stable, unique item_code for one unresolvable Shopify line.

    Keyed on whatever identifies the line, in order of how much it is worth
    trusting: the product id outlives its variant, the variant id is next, and
    a generated placeholder SKU (Shopify invents "sku-<digits>" for a line with
    no product at all) is last. The same product landing on two orders gets the
    same code both times, so its history stays together instead of scattering
    across a placeholder per order.
    """
    key = (
        str((li.get("product") or {}).get("legacyResourceId") or "")
        or str(li.get("product_id") or "")
        or str(li.get("variant_id") or "")
        or str(li.get("sku") or "")
    )
    if not key:
        # Nothing identifies this line at all. Fall back to the shared
        # placeholder rather than inventing a code that cannot be matched
        # again on a later import.
        return CUSTOM_ITEM_PREFIX
    return f"{CUSTOM_ITEM_PREFIX} {key}"[:140]


def _ensure_custom_item(li=None):
    """The placeholder Item for this line, created on first use.

    Non-stock, so it never touches the stock ledger -- there is no real
    inventory behind a product Shopify no longer has.
    """
    name = _custom_item_code(li or {})
    if frappe.db.exists("Item", name):
        return name
    try:
        item = frappe.new_doc("Item")
        item.item_code = name
        # The product's own title, so the Item is recognisable in a list
        # rather than reading as an opaque id.
        item.item_name = ((li or {}).get("title") or name)[:140]
        item.item_group = frappe.db.get_value("Item Group", {"is_group": 0}, "name") or "All Item Groups"
        item.stock_uom = "Nos"
        item.is_stock_item = 0
        item.flags.ignore_permissions = True
        item.insert()
        frappe.db.commit()
        return name
    except Exception:
        frappe.log_error(
            title=f"Shopify: failed to create placeholder Item {name}",
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
