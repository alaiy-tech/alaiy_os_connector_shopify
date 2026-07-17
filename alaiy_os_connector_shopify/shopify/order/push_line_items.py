"""
Pushing line item add/remove changes to a live Shopify order via the
Order Editing API -- moved verbatim from order_push.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.queries import (
    _ORDER_EDIT_BEGIN_MUTATION,
    _ORDER_EDIT_SET_QUANTITY_MUTATION,
    _ORDER_EDIT_ADD_VARIANT_MUTATION,
    _ORDER_EDIT_COMMIT_MUTATION,
)
from alaiy_os_connector_shopify.shopify.order.utils import _to_gid


def _apply_shopify_line_item_changes(order_id: str, removed_variant_ids: list, added_items: list, sales_order: str) -> bool:
    """
    Adds/removes line items on a live Shopify order via the Order Editing
    API (orderUpdate has no line-item support at all) -- one begin/commit
    session covering both, since running two separate edit sessions
    back-to-back on the same order is asking for the same kind of races
    already fought elsewhere in this file today.

    Removed rows are matched to the calculated order's existing line items
    by variant ID -- the one identifier both sides share, since Shopify's
    own line item IDs are order-scoped and never stored on the ERPNext
    side. Added rows are pushed via orderEditAddVariant directly (no
    matching needed, they're new).

    Returns True only if every removed row was matched and the whole edit
    committed cleanly -- any mismatch/failure falls back to the existing
    manual-edit warning rather than silently reporting success.
    """
    removed_variant_ids = removed_variant_ids or []
    added_items = added_items or []
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    client = ShopifyGraphQLClient()
    try:
        begin_data = client.execute(_ORDER_EDIT_BEGIN_MUTATION, {"id": _to_gid(order_id)})
        begin = begin_data.get("orderEditBegin") or {}
        begin_errors = begin.get("userErrors") or []
        if begin_errors:
            frappe.log_error(
                title=f"Shopify: orderEditBegin failed for {sales_order}",
                message=str(begin_errors),
            )
            return False

        calc = begin.get("calculatedOrder") or {}
        calc_id = calc.get("id")
        if not calc_id:
            return False

        line_items = (calc.get("lineItems") or {}).get("nodes") or []
        variant_to_line_id = {
            str((li.get("variant") or {}).get("legacyResourceId")): li.get("id")
            for li in line_items if li.get("variant")
        }

        matched_line_ids = []
        for variant_id in removed_variant_ids:
            line_item_id = variant_to_line_id.get(str(variant_id))
            if not line_item_id:
                frappe.log_error(
                    title=f"Shopify: removed variant {variant_id} not found on order {sales_order}",
                    message=f"Order ID {order_id}, known variants: {list(variant_to_line_id.keys())}",
                )
                continue
            matched_line_ids.append(line_item_id)

        if removed_variant_ids and not matched_line_ids:
            return False

        for line_item_id in matched_line_ids:
            qty_data = client.execute(_ORDER_EDIT_SET_QUANTITY_MUTATION, {
                "id": calc_id, "lineItemId": line_item_id, "quantity": 0,
            })
            qty_errors = (qty_data.get("orderEditSetQuantity") or {}).get("userErrors") or []
            if qty_errors:
                frappe.log_error(
                    title=f"Shopify: orderEditSetQuantity failed for {sales_order}",
                    message=str(qty_errors),
                )
                return False

        added_variant_ids = []
        for item in added_items:
            variant_id = item.get("variant_id")
            qty = item.get("qty") or 1
            if not variant_id:
                continue
            add_data = client.execute(_ORDER_EDIT_ADD_VARIANT_MUTATION, {
                "id": calc_id,
                "variantId": f"gid://shopify/ProductVariant/{variant_id}",
                "quantity": int(qty),
            })
            add_errors = (add_data.get("orderEditAddVariant") or {}).get("userErrors") or []
            if add_errors:
                frappe.log_error(
                    title=f"Shopify: orderEditAddVariant failed for {sales_order}",
                    message=f"variant {variant_id}: {add_errors}",
                )
                return False
            added_variant_ids.append(variant_id)

        if added_items and not added_variant_ids:
            return False

        commit_data = client.execute(_ORDER_EDIT_COMMIT_MUTATION, {"id": calc_id, "notifyCustomer": False})
        commit_errors = (commit_data.get("orderEditCommit") or {}).get("userErrors") or []
        if commit_errors:
            frappe.log_error(
                title=f"Shopify: orderEditCommit failed for {sales_order}",
                message=str(commit_errors),
            )
            return False
        frappe.log_error(
            title=f"Shopify DEBUG: applied line item changes for {sales_order}",
            message=(
                f"Committed removal of {matched_line_ids!r} and addition of "
                f"{added_variant_ids!r} on Shopify order {order_id}"
            ),
        )
        return True
    except Exception:
        frappe.log_error(
            title=f"Shopify: line item change push failed for {sales_order}",
            message=frappe.get_traceback(),
        )
        return False
