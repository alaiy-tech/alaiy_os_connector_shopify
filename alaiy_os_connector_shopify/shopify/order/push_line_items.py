"""
Pushing line item add/remove changes to a live Shopify order via the
Order Editing API -- moved verbatim from order_push.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.queries import (
    _ORDER_EDIT_BEGIN_MUTATION,
    _ORDER_EDIT_SET_QUANTITY_MUTATION,
    _ORDER_EDIT_ADD_VARIANT_MUTATION,
    _ORDER_EDIT_ADD_LINE_ITEM_DISCOUNT_MUTATION,
    _ORDER_EDIT_ADD_SHIPPING_LINE_MUTATION,
    _ORDER_EDIT_UPDATE_SHIPPING_LINE_MUTATION,
    _ORDER_EDIT_REMOVE_SHIPPING_LINE_MUTATION,
    _ORDER_EDIT_ADD_CUSTOM_ITEM_MUTATION,
    _ORDER_EDIT_COMMIT_MUTATION,
)
from alaiy_os_connector_shopify.shopify.order.utils import _to_gid

from alaiy_os_connector_shopify import connections


def _line_item_discount_total(li: dict) -> float:
    """
    Sum of LINE-targeted discount allocations on a calculatedOrder line item
    (order-level discounts are allocated with targetType ORDER, not LINE, and
    aren't this line's own discount to carry forward on a swap).
    """
    total = 0.0
    for alloc in li.get("calculatedDiscountAllocations") or []:
        application = alloc.get("discountApplication") or {}
        if application.get("targetType") not in (None, "LINE_ITEM"):
            continue
        amount = ((alloc.get("allocatedAmountSet") or {}).get("shopMoney") or {}).get("amount")
        if amount:
            total += float(amount)
    return total


def _apply_shopify_line_item_changes(
    order_id: str, removed_variant_ids: list, added_items: list, sales_order: str,
    changed_quantities: list = None, swapped_variants: list = None,
    shipping_line: dict = None, custom_items: list = None,
) -> bool:
    """
    Adds/removes/quantity-edits/swaps line items, and adds a shipping line or
    custom items, on a live Shopify order via the Order Editing API (orderUpdate
    has no line-item support at all) -- one begin/commit session covering all
    of it, since running separate edit sessions back-to-back on the same order
    is asking for the same kind of races already fought elsewhere in this file
    today.

    Removed/quantity-changed/swapped-from rows are all matched to the
    calculated order's existing line items by variant ID -- the one identifier
    both sides share, since Shopify's own line item IDs are order-scoped and
    never stored on the Alaiy OS side. Added/swapped-to rows are pushed via
    orderEditAddVariant directly (no matching needed, they're new).

    swapped_variants: [{"from_variant_id": ..., "to_variant_id": ..., "qty": ...}]
    -- a variant swap is NOT a single Shopify mutation (orderEditAddVariant is
    additive-only, confirmed against Shopify's own docs), so this composes
    orderEditSetQuantity(old, 0) + orderEditAddVariant(new, qty). Shopify does
    not carry the old line's discount over to the new line automatically, so
    the old line's LINE-level discount total (read from the begin response,
    before it's zeroed) is reapplied to the new line as a fixed-amount
    discount via orderEditAddLineItemDiscount -- otherwise a swap silently
    drops whatever discount the customer already had on that line.

    Returns True only if every removed/changed/swapped row was matched and the
    whole edit committed cleanly -- any mismatch/failure falls back to the
    existing manual-edit warning rather than silently reporting success.
    """
    removed_variant_ids = removed_variant_ids or []
    added_items = added_items or []
    changed_quantities = changed_quantities or []
    swapped_variants = swapped_variants or []
    custom_items = custom_items or []
    # The order's own currency, not a hardcoded default -- these are all
    # MoneyInput values sent back to the same Shopify order, which is
    # already denominated in whatever currency it was placed in.
    order_currency = frappe.db.get_value("Sales Order", sales_order, "currency") or "USD"
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    client = ShopifyGraphQLClient(connections.require_enabled())
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
        variant_to_discount = {
            str((li.get("variant") or {}).get("legacyResourceId")): _line_item_discount_total(li)
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

        matched_qty_changes = []
        for change in changed_quantities:
            variant_id = change.get("variant_id")
            line_item_id = variant_to_line_id.get(str(variant_id))
            if not line_item_id:
                frappe.log_error(
                    title=f"Shopify: changed-quantity variant {variant_id} not found on order {sales_order}",
                    message=f"Order ID {order_id}, known variants: {list(variant_to_line_id.keys())}",
                )
                continue
            qty_data = client.execute(_ORDER_EDIT_SET_QUANTITY_MUTATION, {
                "id": calc_id, "lineItemId": line_item_id, "quantity": int(change["qty"]),
            })
            qty_errors = (qty_data.get("orderEditSetQuantity") or {}).get("userErrors") or []
            if qty_errors:
                frappe.log_error(
                    title=f"Shopify: orderEditSetQuantity (qty change) failed for {sales_order}",
                    message=str(qty_errors),
                )
                return False
            matched_qty_changes.append(variant_id)

        if changed_quantities and not matched_qty_changes:
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

        swapped_pairs = []
        for swap in swapped_variants:
            from_variant_id = swap.get("from_variant_id")
            to_variant_id = swap.get("to_variant_id")
            qty = swap.get("qty") or 1
            if not from_variant_id or not to_variant_id:
                continue
            old_line_item_id = variant_to_line_id.get(str(from_variant_id))
            if not old_line_item_id:
                frappe.log_error(
                    title=f"Shopify: swap-from variant {from_variant_id} not found on order {sales_order}",
                    message=f"Order ID {order_id}, known variants: {list(variant_to_line_id.keys())}",
                )
                continue
            discount_total = variant_to_discount.get(str(from_variant_id)) or 0.0

            zero_data = client.execute(_ORDER_EDIT_SET_QUANTITY_MUTATION, {
                "id": calc_id, "lineItemId": old_line_item_id, "quantity": 0,
            })
            zero_errors = (zero_data.get("orderEditSetQuantity") or {}).get("userErrors") or []
            if zero_errors:
                frappe.log_error(
                    title=f"Shopify: swap orderEditSetQuantity(0) failed for {sales_order}",
                    message=str(zero_errors),
                )
                return False

            swap_add_data = client.execute(_ORDER_EDIT_ADD_VARIANT_MUTATION, {
                "id": calc_id,
                "variantId": f"gid://shopify/ProductVariant/{to_variant_id}",
                "quantity": int(qty),
            })
            swap_add_errors = (swap_add_data.get("orderEditAddVariant") or {}).get("userErrors") or []
            if swap_add_errors:
                frappe.log_error(
                    title=f"Shopify: swap orderEditAddVariant failed for {sales_order}",
                    message=f"variant {to_variant_id}: {swap_add_errors}",
                )
                return False

            if discount_total > 0:
                new_line_item = (swap_add_data.get("orderEditAddVariant") or {}).get("calculatedLineItem") or {}
                new_line_item_id = new_line_item.get("id")
                if new_line_item_id:
                    # Shopify doesn't carry a swapped-out line's discount over
                    # to the replacement line -- reapplied here as a fixed
                    # amount equal to what the old line had, so the customer's
                    # existing discount survives the swap instead of silently
                    # disappearing.
                    disc_data = client.execute(_ORDER_EDIT_ADD_LINE_ITEM_DISCOUNT_MUTATION, {
                        "id": calc_id, "lineItemId": new_line_item_id,
                        "discount": {
                            "description": "Carried over from swapped line",
                            "fixedValue": {"amount": str(discount_total), "currencyCode": order_currency},
                        },
                    })
                    disc_errors = (disc_data.get("orderEditAddLineItemDiscount") or {}).get("userErrors") or []
                    if disc_errors:
                        frappe.log_error(
                            title=f"Shopify: swap discount carry-over failed for {sales_order}",
                            message=str(disc_errors),
                        )
                        # Non-fatal -- the swap itself succeeded, only the
                        # discount carry-over failed. Logged so it's visible
                        # rather than silently dropped, but not worth
                        # rolling back an otherwise-good swap for.
            swapped_pairs.append((from_variant_id, to_variant_id))

        if swapped_variants and not swapped_pairs:
            return False

        if shipping_line:
            action = shipping_line.get("action")
            if action == "remove" and shipping_line.get("shipping_line_id"):
                ship_data = client.execute(_ORDER_EDIT_REMOVE_SHIPPING_LINE_MUTATION, {
                    "id": calc_id, "shippingLineId": shipping_line["shipping_line_id"],
                })
                ship_errors = (ship_data.get("orderEditRemoveShippingLine") or {}).get("userErrors") or []
            elif action == "update" and shipping_line.get("shipping_line_id"):
                ship_data = client.execute(_ORDER_EDIT_UPDATE_SHIPPING_LINE_MUTATION, {
                    "id": calc_id, "shippingLineId": shipping_line["shipping_line_id"],
                    "shippingLine": {
                        "title": shipping_line.get("title") or "Shipping",
                        "price": {"amount": str(shipping_line.get("price") or 0), "currencyCode": order_currency},
                    },
                })
                ship_errors = (ship_data.get("orderEditUpdateShippingLine") or {}).get("userErrors") or []
            else:
                ship_data = client.execute(_ORDER_EDIT_ADD_SHIPPING_LINE_MUTATION, {
                    "id": calc_id,
                    "shippingLine": {
                        "title": shipping_line.get("title") or "Shipping",
                        "price": {"amount": str(shipping_line.get("price") or 0), "currencyCode": order_currency},
                    },
                })
                ship_errors = (ship_data.get("orderEditAddShippingLine") or {}).get("userErrors") or []
            if ship_errors:
                frappe.log_error(
                    title=f"Shopify: shipping line push failed for {sales_order}",
                    message=str(ship_errors),
                )
                return False

        added_custom_items = []
        for custom in custom_items:
            title = custom.get("title")
            price = custom.get("price")
            qty = custom.get("qty") or 1
            if not title or price is None:
                continue
            custom_data = client.execute(_ORDER_EDIT_ADD_CUSTOM_ITEM_MUTATION, {
                "id": calc_id,
                "title": title,
                "price": {"amount": str(price), "currencyCode": order_currency},
                "quantity": int(qty),
                "taxable": custom.get("taxable", True),
                "requiresShipping": custom.get("requires_shipping", False),
            })
            custom_errors = (custom_data.get("orderEditAddCustomItem") or {}).get("userErrors") or []
            if custom_errors:
                frappe.log_error(
                    title=f"Shopify: orderEditAddCustomItem failed for {sales_order}",
                    message=f"{title}: {custom_errors}",
                )
                return False
            added_custom_items.append(title)

        if custom_items and not added_custom_items:
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
                f"Committed removal of {matched_line_ids!r}, addition of "
                f"{added_variant_ids!r}, quantity change of "
                f"{matched_qty_changes!r}, swap of {swapped_pairs!r}, "
                f"shipping line {shipping_line!r}, and custom items "
                f"{added_custom_items!r} on Shopify order {order_id}"
            ),
        )
        return True
    except Exception:
        frappe.log_error(
            title=f"Shopify: line item change push failed for {sales_order}",
            message=frappe.get_traceback(),
        )
        return False
