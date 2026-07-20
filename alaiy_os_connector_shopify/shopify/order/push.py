"""
Background job bodies for Alaiy OS -> Shopify order push-back -- moved
verbatim from order_push.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.queries import (
    _ORDER_UPDATE_MUTATION, _ORDER_CREATE_MUTATION, _ORDER_CANCEL_MUTATION,
)
from alaiy_os_connector_shopify.shopify.order.utils import _to_gid
from alaiy_os_connector_shopify.shopify.order.push_line_items import _apply_shopify_line_item_changes


def push_order_update(order_id: str, sales_order: str, status: str, items_changed: bool = False, removed_variant_ids: list = None, added_items: list = None):
    """
    Pushes order status updates to Shopify. If line items changed on the SO,
    check state guard: if Delivery Notes exist (shipment started), reject the
    update and log a clear error since the Shopify order can't be modified at
    that point anyway. Otherwise, if any of the changed rows were outright
    added or removed (not just a qty/rate edit on a surviving row), push
    that via Shopify's Order Editing API. Pure qty/rate edits on an
    existing row still have no Shopify-side equivalent (orderUpdate
    doesn't support them) and fall back to the manual-edit warning.
    """
    removed_variant_ids = removed_variant_ids or []
    added_items = added_items or []
    frappe.log_error(
        title=f"Shopify DEBUG: push_order_update {sales_order}",
        message=(
            f"items_changed={items_changed} removed_variant_ids={removed_variant_ids!r} "
            f"added_items={added_items!r}"
        ),
    )

    # State guard: reject line item changes if fulfillment has started
    if items_changed:
        has_delivery_notes = frappe.db.exists(
            "Delivery Note Item", {"against_sales_order": sales_order})
        if has_delivery_notes:
            frappe.log_error(
                title=f"Shopify: cannot sync line item changes for {sales_order}",
                message=(
                    f"Order {sales_order} has started shipping (Delivery Note exists). "
                    "Line items are locked. Create a follow-up order for additional items."
                ),
            )
            return

        if (removed_variant_ids or added_items) and _apply_shopify_line_item_changes(
            order_id, removed_variant_ids, added_items, sales_order
        ):
            return

        # Items changed but no shipment yet, and either nothing was
        # add/removed (just a qty/rate edit) or the push itself failed --
        # warn user that Shopify needs manual edit
        frappe.log_error(
            title=f"Shopify: line items changed for {sales_order}, manual edit needed",
            message=(
                f"Items were added/removed/changed in {sales_order}, but Shopify's "
                "orderUpdate API doesn't support line-item changes. "
                "Please manually adjust the order in Shopify admin or create a follow-up order."
            ),
        )
        return

    # No item changes - proceed with status push
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    # Status used to also overwrite Shopify's note field with an
    # auto-generated string ("Alaiy OS: ... status = ...") -- that would
    # fight with a genuine bidirectional notes field, so status now lives
    # in tags only, and note carries the real user-editable content.
    notes = frappe.db.get_value("Sales Order", sales_order, "sh_shopify_notes") or ""

    try:
        client = ShopifyGraphQLClient()
        data = client.execute(_ORDER_UPDATE_MUTATION, {
            "input": {
                "id": _to_gid(order_id),
                "note": notes,
                "tags": [f"alaiy-os-status:{status}"],
            },
        })
        errors = (data.get("orderUpdate") or {}).get("userErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: order update push failed for {sales_order}",
                message=str(errors),
            )
    except Exception:
        frappe.log_error(
            title=f"Shopify: order update push failed for {sales_order}",
            message=frappe.get_traceback(),
        )


def push_order_create(sales_order: str):
    """
    Builds an orderCreate mutation from a Sales Order's own items/customer.
    Line items without a linked sh_shopify_variant_id are skipped (and
    logged) rather than failing the whole push -- a partially-representable
    order on Shopify is more useful than none at all, but skipped lines are
    flagged loudly since Shopify's total won't match Alaiy OS's.
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    so = frappe.get_doc("Sales Order", sales_order)

    line_items = []
    skipped = []
    for item in so.items:
        variant_id = frappe.db.get_value("Item", item.item_code, "sh_shopify_variant_id")
        if not variant_id:
            skipped.append(item.item_code)
            continue
        line_items.append({
            "variantId": f"gid://shopify/ProductVariant/{variant_id}",
            "quantity": int(item.qty),
        })

    if not line_items:
        frappe.log_error(
            title=f"Shopify: order create push skipped for {sales_order}",
            message="No line item on this Sales Order has a linked Shopify variant.",
        )
        return

    customer_email = frappe.db.get_value("Customer", so.customer, "email_id")

    try:
        client = ShopifyGraphQLClient()
        order_input = {
            "lineItems": line_items,
            "financialStatus": "PENDING",
        }
        if customer_email:
            order_input["email"] = customer_email

        data = client.execute(_ORDER_CREATE_MUTATION, {
            "order": order_input,
            "options": {"sendReceipt": False, "sendFulfillmentReceipt": False},
        })
        result = data.get("orderCreate") or {}
        errors = result.get("userErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: order create push failed for {sales_order}",
                message=str(errors),
            )
            return

        order = result.get("order") or {}
        if order.get("legacyResourceId"):
            frappe.db.set_value("Sales Order", sales_order, {
                "sh_shopify_order_id": order["legacyResourceId"],
                "sh_shopify_order_name": order.get("name", ""),
            })
            frappe.db.commit()

        if skipped:
            frappe.log_error(
                title=f"Shopify: order create push for {sales_order} skipped some items",
                message=f"No Shopify variant linked for: {', '.join(skipped)}",
            )
    except Exception:
        frappe.log_error(
            title=f"Shopify: order create push failed for {sales_order}",
            message=frappe.get_traceback(),
        )


def push_order_cancel(order_id: str, sales_order: str):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    try:
        client = ShopifyGraphQLClient()
        data = client.execute(_ORDER_CANCEL_MUTATION, {
            "orderId": _to_gid(order_id),
            "reason": "OTHER",
            "refund": False,
            "restock": False,
            "notifyCustomer": False,
        })
        errors = (data.get("orderCancel") or {}).get("orderCancelUserErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: order cancel push failed for {sales_order}",
                message=str(errors),
            )
    except Exception:
        frappe.log_error(
            title=f"Shopify: order cancel push failed for {sales_order}",
            message=frappe.get_traceback(),
        )
