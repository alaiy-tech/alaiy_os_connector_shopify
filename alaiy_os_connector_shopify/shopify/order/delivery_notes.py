"""
Delivery Note / fulfillment creation -- moved verbatim from
order_sync.py, unchanged.
"""

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.order.utils import _as_administrator, _resolve_item_code
from alaiy_os_connector_shopify.shopify.order.warehouse import _force_valid_warehouse


def _fill_expense_accounts(dn):
    """
    Force a valid Expense Account onto every Delivery Note row missing one.
    Confirmed live: an Item with no expense_account of its own and no
    default configured anywhere crashes submit at the GL-entry step
    ("Expense Account not set for the Item ..."). Same self-heal shape as
    invoice.py's _fill_item_accounts/_resolve_income_account -- resolve one
    company-wide default rather than requiring the merchant to configure
    every Item by hand.
    """
    expense = _resolve_expense_account(dn.company)
    if not expense:
        return
    for row in dn.items:
        if not row.expense_account:
            row.expense_account = expense


def _resolve_expense_account(company):
    configured = frappe.get_cached_value("Company", company, "default_expense_account")
    if configured and not frappe.db.get_value("Account", configured, "is_group"):
        return configured
    return frappe.db.get_value(
        "Account",
        {"company": company, "account_type": "Cost of Goods Sold", "is_group": 0, "disabled": 0},
        "name",
    ) or frappe.db.get_value(
        "Account",
        {"company": company, "root_type": "Expense", "is_group": 0, "disabled": 0},
        "name",
    )


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
            # Self-heal, same shape as the invoice's income-account/cost-center
            # fixes: a Shopify item with no incoming stock/valuation rate ever
            # recorded locally (dropshipped, no purchase receipt in Alaiy OS)
            # crashes the stock ledger post with "Valuation Rate ... is
            # required" -- confirmed live. These items carry no real local
            # stock value to account for, so zero valuation is correct, not a
            # workaround.
            for row in dn.items:
                row.allow_zero_valuation_rate = 1
            _fill_expense_accounts(dn)
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
            for row in dn.items:
                row.allow_zero_valuation_rate = 1
            _fill_expense_accounts(dn)
            dn.flags.ignore_permissions = True
            dn.insert()
            dn.submit()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: auto Delivery Note failed for fulfillment {fulfillment_id}",
            message=f"Sales Order: {so.name}\n{frappe.get_traceback()}",
        )


def _sync_tracking(fulfillment):
    """
    fulfillments/create and fulfillments/update webhooks deliver the
    Fulfillment object directly (not wrapped in an order), carrying
    tracking_number/tracking_company/tracking_url(s) -- fields
    orders/fulfilled's payload doesn't reliably carry and which can also
    change AFTER the order is already marked fulfilled (a real, common
    flow: merchant adds/edits the tracking number later).

    Matches by sh_shopify_fulfillment_id first. Falls back to the order's
    own Delivery Note when that's blank -- confirmed live: an order marked
    fulfilled at create time (Shopify's one-click "Complete order") carries
    fulfillment_status=fulfilled but an EMPTY fulfillments array on the
    orders/create webhook payload, so _create_delivery_note_if_needed's
    full-order fallback creates the Delivery Note without ever tagging a
    fulfillment id. That's not a rare edge case -- it's how a quick manual
    order gets fulfilled -- so tracking must still be able to land on it.
    Also backfills the fulfillment id onto that Delivery Note so a second
    fulfillments/update webhook matches directly next time.

    No-ops if neither match finds a Delivery Note yet -- fulfillments/
    create can arrive before the order webhook finishes creating one;
    tracking is rarely set on the very first delivery anyway, and a later
    fulfillments/update webhook (or a manual backfill) catches it.
    """
    fulfillment_id = str(fulfillment.get("id") or "")
    if not fulfillment_id:
        return
    dn_name = frappe.db.get_value(
        "Delivery Note", {"sh_shopify_fulfillment_id": fulfillment_id}, "name")

    if not dn_name:
        order_id = str(fulfillment.get("order_id") or "")
        if not order_id:
            return
        from alaiy_os_connector_shopify.shopify.order.upsert import get_active_sales_order
        so_name = get_active_sales_order(order_id)
        if not so_name:
            return
        dn_name = frappe.db.get_value(
            "Delivery Note Item", {"against_sales_order": so_name}, "parent")
        if not dn_name:
            return
        frappe.db.set_value("Delivery Note", dn_name, "sh_shopify_fulfillment_id", fulfillment_id)

    tracking_number = fulfillment.get("tracking_number") or ",".join(fulfillment.get("tracking_numbers") or [])
    tracking_url = fulfillment.get("tracking_url") or ",".join(fulfillment.get("tracking_urls") or [])
    frappe.db.set_value("Delivery Note", dn_name, {
        "sh_tracking_number": tracking_number,
        "sh_tracking_company": fulfillment.get("tracking_company") or "",
        "sh_tracking_url": tracking_url,
    })
    frappe.db.commit()
