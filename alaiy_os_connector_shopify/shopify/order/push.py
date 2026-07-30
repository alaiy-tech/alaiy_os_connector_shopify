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
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver


def _address_to_shopify_input(address_fields: dict) -> dict:
    """Maps Alaiy OS's Address fields to Shopify's MailingAddressInput shape."""
    return {
        "address1": address_fields.get("address_line1") or "",
        "address2": address_fields.get("address_line2") or "",
        "city": address_fields.get("city") or "",
        "province": address_fields.get("state") or "",
        "zip": address_fields.get("pincode") or "",
        "country": address_fields.get("country") or "",
        "phone": address_fields.get("phone") or "",
    }


def push_order_update(order_id: str, sales_order: str, status: str, items_changed: bool = False, removed_variant_ids: list = None, added_items: list = None, changed_quantities: list = None, shipping_address: dict = None):
    """
    Pushes order status/note/tags/shipping-address updates to Shopify, and
    (if line items changed) adds/removes/quantity edits via Shopify's Order
    Editing API in one session. If Delivery Notes exist (shipment started),
    item changes are rejected -- the Shopify order can't be modified at that
    point anyway -- but status/note/tags/address still push regardless,
    since those aren't blocked by a started shipment. Rate-only edits on a
    surviving row (no qty change) still have no Shopify-side equivalent and
    fall back to the manual-edit warning, same as anything the Order
    Editing API call itself fails to apply cleanly.
    """
    removed_variant_ids = removed_variant_ids or []
    added_items = added_items or []
    changed_quantities = changed_quantities or []
    frappe.log_error(
        title=f"Shopify DEBUG: push_order_update {sales_order}",
        message=(
            f"items_changed={items_changed} removed_variant_ids={removed_variant_ids!r} "
            f"added_items={added_items!r} changed_quantities={changed_quantities!r} "
            f"shipping_address_changed={shipping_address is not None}"
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
        elif (removed_variant_ids or added_items or changed_quantities) and _apply_shopify_line_item_changes(
            order_id, removed_variant_ids, added_items, sales_order, changed_quantities
        ):
            pass  # line item edit committed cleanly -- status/note/tags/address below still run
        else:
            # Items changed but either nothing was add/removed/qty-changed
            # or the push itself failed -- warn user that Shopify needs
            # manual edit. Status/note/tags/address below still run.
            frappe.log_error(
                title=f"Shopify: line items changed for {sales_order}, manual edit needed",
                message=(
                    f"Items were added/removed/changed in {sales_order}, but Shopify's "
                    "orderUpdate API doesn't support line-item changes. "
                    "Please manually adjust the order in Shopify admin or create a follow-up order."
                ),
            )

    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    # Status used to also overwrite Shopify's note field with an
    # auto-generated string ("Alaiy OS: ... status = ...") -- that would
    # fight with a genuine bidirectional notes field, so status now lives
    # in tags only, and note carries the real user-editable content.
    notes = frappe.db.get_value("Sales Order", sales_order, "sh_shopify_notes") or ""

    try:
        client = ShopifyGraphQLClient()
        order_input = {
            "id": _to_gid(order_id),
            "note": notes,
            "tags": [f"alaiy-os-status:{status}"],
        }
        if shipping_address:
            order_input["shippingAddress"] = _address_to_shopify_input(shipping_address)
        data = client.execute(_ORDER_UPDATE_MUTATION, {"input": order_input})
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
        # Listing Variant's copy first, Item as fallback.
        variant_id = listing_resolver.variant_id_of_item(item.item_code)
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
