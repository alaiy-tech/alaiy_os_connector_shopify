"""
Delivery Note / fulfillment creation -- moved verbatim from
order_sync.py, unchanged.
"""

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.order.utils import _as_administrator, _resolve_item_code
from alaiy_os_connector_shopify.shopify.order.warehouse import _force_valid_warehouse


def _create_delivery_note_if_needed(so_name):
    """
    Full-order fallback for the one path that has no per-fulfillment
    breakdown to work with: an order pulled/imported that's already
    fulfilled on Shopify (historical import, or orders/create arriving
    after the order was already completed there) -- the GraphQL orders
    query used for pulls doesn't currently fetch the fulfillments
    connection, only the REST-shaped webhook payload does. Delivers the
    full order in one go; idempotent via the same against_sales_order
    check _sync_fulfillments's per-fulfillment-id check doesn't cover here.
    """
    if frappe.db.exists("Delivery Note Item", {"against_sales_order": so_name}):
        return

    so = frappe.get_doc("Sales Order", so_name)
    if so.docstatus != 1:
        return

    try:
        from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
        with _as_administrator():
            dn = make_delivery_note(so_name)
            _force_valid_warehouse(dn)
            dn.flags.ignore_permissions = True
            dn.insert()
            dn.submit()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: auto Delivery Note failed for {so_name}",
            message=frappe.get_traceback(),
        )


def _sync_fulfillments(so_name, fulfillments):
    """
    Each Shopify Fulfillment object (in the webhook's REST-shaped payload,
    not just the order-level fulfillment_status label) carries exactly
    which line items/quantities were shipped in that specific event -- this
    is what makes PARTIAL fulfillment trackable at all, not just the binary
    fulfilled/unfulfilled case. One Delivery Note per Shopify Fulfillment
    id, tagged with sh_shopify_fulfillment_id so a redelivered webhook for
    the same fulfillment event never creates a duplicate Delivery Note, and
    a second, later partial shipment creates its own separate one.
    """
    if not fulfillments:
        return

    so = frappe.get_doc("Sales Order", so_name)
    if so.docstatus != 1:
        return

    for fulfillment in fulfillments:
        fulfillment_id = str(fulfillment.get("id") or "")
        if not fulfillment_id:
            continue
        if frappe.db.exists("Delivery Note", {"sh_shopify_fulfillment_id": fulfillment_id}):
            continue
        _create_delivery_note_for_fulfillment(
            so, fulfillment_id, fulfillment.get("line_items") or [])


def _create_delivery_note_for_fulfillment(so, fulfillment_id, fulfillment_line_items):
    qty_by_item = {}
    for li in fulfillment_line_items:
        item_code = _resolve_item_code({
            "sku": li.get("sku"),
            "variant_id": li.get("variant_id"),
            "title": li.get("title") or li.get("name"),
        })
        if not item_code:
            continue
        qty_by_item[item_code] = qty_by_item.get(item_code, 0) + flt(li.get("quantity", 0))

    if not qty_by_item:
        frappe.log_error(
            title=f"Shopify: fulfillment {fulfillment_id} had no mappable items",
            message=f"Sales Order: {so.name}, line_items: {fulfillment_line_items}",
        )
        return

    try:
        from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
        with _as_administrator():
            dn = make_delivery_note(so.name)
            _force_valid_warehouse(dn)

            # make_delivery_note maps the full remaining quantity per item
            # by default -- trim each row down to only what THIS
            # fulfillment event covers, dropping rows it didn't touch.
            kept_items = []
            for dn_item in dn.items:
                fulfilled_qty = qty_by_item.get(dn_item.item_code, 0)
                if fulfilled_qty <= 0:
                    continue
                dn_item.qty = min(dn_item.qty, fulfilled_qty)
                kept_items.append(dn_item)
            dn.items = kept_items
            if not dn.items:
                return

            dn.sh_shopify_fulfillment_id = fulfillment_id
            dn.flags.ignore_permissions = True
            dn.insert()
            dn.submit()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: auto Delivery Note failed for fulfillment {fulfillment_id}",
            message=f"Sales Order: {so.name}\n{frappe.get_traceback()}",
        )
