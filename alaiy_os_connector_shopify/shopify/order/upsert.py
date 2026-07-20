"""
Sales Order creation from a Shopify order -- moved verbatim from
order_sync.py, unchanged.
"""

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.order.locking import _acquire_order_lock, _release_order_lock
from alaiy_os_connector_shopify.shopify.order.customer import _get_or_create_customer
from alaiy_os_connector_shopify.shopify.order.warehouse import _resolve_default_warehouse
from alaiy_os_connector_shopify.shopify.order.utils import _resolve_item_code
from alaiy_os_connector_shopify.shopify.order.delivery_notes import _sync_fulfillments, _create_delivery_note_if_needed
from alaiy_os_connector_shopify.shopify.order.tax import _append_tax_lines


def get_active_sales_order(order_id: str):
    """
    Look up the Sales Order for a Shopify order ID, preferring the latest
    non-cancelled document. Once _sync_order_line_items starts amending
    (cancel + recreate) a submitted order, the cancelled original and its
    amended replacement both carry the same sh_shopify_order_id -- a plain
    frappe.db.get_value with no docstatus/order_by picks whichever the DB
    happens to return first, which can silently resurrect the cancelled one.
    """
    return frappe.db.get_value(
        "Sales Order",
        {"sh_shopify_order_id": order_id, "docstatus": ["!=", 2]},
        "name",
        order_by="creation desc",
    )


def _upsert_order(order):
    """Acquires this order's lock, then defers to _upsert_order_unlocked."""
    order_id = str(order.get("id", ""))
    if not order_id:
        return False
    if not _acquire_order_lock(order_id):
        frappe.log_error(
            title=f"Shopify order {order_id}: upsert lock timed out",
            message="Another process held this order's lock for 30s+ -- skipped to avoid a duplicate.",
        )
        return False
    try:
        return _upsert_order_unlocked(order, order_id)
    finally:
        _release_order_lock(order_id)


def _upsert_order_unlocked(order, order_id):
    """Returns True if a new Sales Order was created, False if skipped."""
    if get_active_sales_order(order_id):
        return False  # already processed

    settings = frappe.get_single("Shopify Connector Settings")
    # A missing default Address Template makes Alaiy OS throw while rendering the
    # customer's address during Sales Order validate -- ensure one exists first.
    from alaiy_os_connector_shopify.shopify.order.address import ensure_default_address_template
    ensure_default_address_template()
    customer_name = _get_or_create_customer(
        order.get("customer") or {}, settings)
    warehouse = _resolve_default_warehouse(settings)

    from alaiy_os_connector_shopify.shopify.order.utils import _line_item_qty

    from alaiy_os_connector_shopify.shopify.order.charges import build_custom_line_item

    line_items = []
    for li in order.get("line_items", []):
        item_code = _resolve_item_code(li)
        if not item_code:
            # No catalog match -- keep it as a custom line item rather than
            # silently dropping it (Shopify allows one-off/custom products).
            custom = build_custom_line_item(li, warehouse)
            if custom:
                line_items.append(custom)
            continue
        qty = _line_item_qty(li)
        if qty <= 0:
            continue
        line_items.append({
            "item_code": item_code,
            "qty": qty,
            "rate": flt(li.get("price", 0)),
            "warehouse": warehouse,
            "delivery_date": frappe.utils.today(),
            "sh_shopify_variant_id": str(li.get("variant_id", "")),
        })

    if not line_items:
        frappe.log_error(
            title=f"Shopify order {order.get('name')}: no mappable items",
            message=str(order.get("line_items")),
        )
        return False

    so = frappe.new_doc("Sales Order")
    so.customer = customer_name
    so.company = settings.sh_company or frappe.defaults.get_global_default(
        "company")
    so.transaction_date = frappe.utils.today()
    so.delivery_date = frappe.utils.today()
    so.selling_price_list = settings.sh_selling_price_list or "Standard Selling"
    so.set_warehouse = warehouse
    if settings.sh_cost_center:
        so.cost_center = settings.sh_cost_center
    so.sh_shopify_order_id = order_id
    so.sh_shopify_order_name = order.get("name", "")
    so.sh_financial_status = order.get("financial_status", "")
    so.sh_fulfillment_status = order.get("fulfillment_status", "")
    so.sh_shopify_notes = order.get("note") or ""
    for li in line_items:
        so.append("items", li)

    # Shipping address
    from alaiy_os_connector_shopify.shopify.order.address import sync_order_address
    from alaiy_os_connector_shopify.shopify.order.charges import (
        append_shipping_charge, apply_order_discount,
    )
    addr = sync_order_address(order, customer_name)
    if addr:
        so.customer_address = addr
        so.shipping_address_name = addr

    _append_tax_lines(so, order.get("tax_lines"), order.get("taxes_included"), settings)
    append_shipping_charge(so, order, settings)
    apply_order_discount(so, order)

    # Set BEFORE insert/submit -- Sales Order's on_update/on_submit doc_events
    # check this flag to skip pushing back to Shopify, since this save
    # originated FROM Shopify (webhook or pull) and pushing it back would
    # just be echoing the same data Shopify already has.
    so.flags.from_shopify_sync = True
    so.flags.ignore_permissions = True
    so.insert()

    # Draft orders from Shopify should stay as draft in Alaiy OS until customer completes checkout.
    # Real orders are submitted immediately and ready for fulfillment.
    # Draft orders have Order # like #D9, #D10; real orders are numeric like #1015
    order_name = order.get("name", "")
    is_draft_order = order_name.startswith("#D")
    if not is_draft_order:
        so.submit()

    frappe.db.commit()

    if order.get("fulfillments"):
        _sync_fulfillments(so.name, order.get("fulfillments"))
    elif so.sh_fulfillment_status == "fulfilled":
        # GraphQL pull path has no per-fulfillment breakdown to work with
        # (see _create_delivery_note_if_needed's note) -- full-order fallback.
        _create_delivery_note_if_needed(so.name)

    # Orders often arrive already paid (and sometimes already fulfilled) at
    # create time -- invoice right away if the trigger is met.
    if not is_draft_order:
        from alaiy_os_connector_shopify.shopify.order.invoice import create_sales_invoice_if_paid
        create_sales_invoice_if_paid(
            so.name, order.get("financial_status", ""), order.get("fulfillment_status", ""))
    return True
