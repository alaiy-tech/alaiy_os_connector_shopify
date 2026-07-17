"""
ERPNext -> Shopify order push-back ("vice versa" half of order sync).

Supports both directions: line item modifications are only allowed before any
fulfillment starts (state guard). Once a Delivery Note is created, line items
are locked to prevent stock/refund mismatches. Shopify's orderUpdate mutation
doesn't support line-item changes (would need Order Edit session API), so if
items changed, we reject the update and guide user to create a follow-up order
instead. Status pushes (notes/tags) still work regardless.

Both doc_events check doc.flags.from_shopify_sync first: a save/cancel that
originated FROM a Shopify webhook/pull must never be echoed straight back to
Shopify, or every webhook would trigger an infinite ping-pong.
"""

import frappe

_ORDER_UPDATE_MUTATION = """
mutation PushOrderUpdate($input: OrderInput!) {
  orderUpdate(input: $input) {
    order {
      id
    }
    userErrors {
      field
      message
    }
  }
}
"""

_ORDER_CANCEL_MUTATION = """
mutation PushOrderCancel($orderId: ID!, $reason: OrderCancelReason!, $refund: Boolean!, $restock: Boolean!, $notifyCustomer: Boolean!) {
  orderCancel(orderId: $orderId, reason: $reason, refund: $refund, restock: $restock, notifyCustomer: $notifyCustomer) {
    job {
      id
    }
    orderCancelUserErrors {
      field
      message
    }
  }
}
"""

_ORDER_CREATE_MUTATION = """
mutation PushOrderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
  orderCreate(order: $order, options: $options) {
    order {
      id
      legacyResourceId
      name
    }
    userErrors {
      field
      message
    }
  }
}
"""

# orderUpdate has no line-item support at all -- removing a line requires
# Shopify's separate Order Editing API (begin a calculated edit session, set
# the line's quantity to 0, commit).
_ORDER_EDIT_BEGIN_MUTATION = """
mutation BeginOrderEdit($id: ID!) {
  orderEditBegin(id: $id) {
    calculatedOrder {
      id
      lineItems(first: 100) {
        nodes {
          id
          variant {
            legacyResourceId
          }
        }
      }
    }
    userErrors {
      field
      message
    }
  }
}
"""

_ORDER_EDIT_SET_QUANTITY_MUTATION = """
mutation SetOrderEditQuantity($id: ID!, $lineItemId: ID!, $quantity: Int!) {
  orderEditSetQuantity(id: $id, lineItemId: $lineItemId, quantity: $quantity) {
    calculatedOrder {
      id
    }
    userErrors {
      field
      message
    }
  }
}
"""

_ORDER_EDIT_COMMIT_MUTATION = """
mutation CommitOrderEdit($id: ID!, $notifyCustomer: Boolean) {
  orderEditCommit(id: $id, notifyCustomer: $notifyCustomer) {
    order {
      id
    }
    userErrors {
      field
      message
    }
  }
}
"""


def _to_gid(shopify_order_id: str) -> str:
    return f"gid://shopify/Order/{shopify_order_id}"


def _remove_shopify_line_items(order_id: str, removed_variant_ids: list, sales_order: str) -> bool:
    """
    Removes line items from a live Shopify order via the Order Editing API
    (orderUpdate has no line-item support at all). Matches removed ERPNext
    rows to the calculated order's line items by variant ID -- the one
    identifier both sides share, since Shopify's own line item IDs are
    order-scoped and never stored on the ERPNext side.

    Returns True only if every removed row was matched and the edit
    committed cleanly -- any mismatch/failure falls back to the existing
    manual-edit warning rather than silently reporting success.
    """
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

        if not matched_line_ids:
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

        commit_data = client.execute(_ORDER_EDIT_COMMIT_MUTATION, {"id": calc_id, "notifyCustomer": False})
        commit_errors = (commit_data.get("orderEditCommit") or {}).get("userErrors") or []
        if commit_errors:
            frappe.log_error(
                title=f"Shopify: orderEditCommit failed for {sales_order}",
                message=str(commit_errors),
            )
            return False
        return True
    except Exception:
        frappe.log_error(
            title=f"Shopify: line item removal push failed for {sales_order}",
            message=frappe.get_traceback(),
        )
        return False


# ── Helpers ──────────────────────────────────────────────────────────────────

def _detect_items_changed(doc) -> bool:
    """
    Check if Sales Order's items have been added, removed, or modified.
    Returns True if any items field changed, False if only status/metadata changed.

    Uses get_doc_before_save() -- NOT a fresh frappe.get_doc() re-fetch. By
    the time on_update fires, the DB row already reflects this save's new
    values, so re-fetching from the DB just compares the new state against
    itself and silently never detects anything (root cause of item removal
    never reaching Shopify at all: this always returned False in
    production, so push_order_update never even tried).
    """
    if not doc.get("items"):
        return False

    before = doc.get_doc_before_save()
    if not before:
        return False

    original_items = {
        (item.item_code, item.qty, item.rate) for item in before.items
    }
    current_items = {
        (item.item_code, item.qty, item.rate) for item in doc.items
    }
    return original_items != current_items


def _detect_removed_variant_ids(doc) -> list:
    """
    Shopify variant IDs for line item ROWS present before this save but
    missing after -- i.e. genuinely removed rows, not a qty/rate edit on a
    surviving row. This is what actually gets matched against Shopify's
    order line items for removal; item_code/qty/rate alone can't tell us
    WHICH item to remove on the Shopify side.
    """
    before = doc.get_doc_before_save()
    if not before:
        return []
    before_rows = {
        (item.item_code, item.get("sh_shopify_variant_id")) for item in before.items
    }
    after_rows = {
        (item.item_code, item.get("sh_shopify_variant_id")) for item in doc.items
    }
    removed = before_rows - after_rows
    return [variant_id for (_, variant_id) in removed if variant_id]


# ── Doc event entry points ───────────────────────────────────────────────────
# Never call Shopify inline inside a save/cancel transaction -- enqueue and
# return, same convention as product_sync.py.

def on_sales_order_update(doc, method=None):
    if doc.flags.from_shopify_sync:
        return
    if not doc.get("sh_shopify_order_id"):
        return

    # Detect if line items changed (added, removed, or quantity/rate modified)
    items_changed = _detect_items_changed(doc)
    removed_variant_ids = _detect_removed_variant_ids(doc) if items_changed else []

    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_push.push_order_update",
        queue="short",
        timeout=60,
        order_id=doc.sh_shopify_order_id,
        sales_order=doc.name,
        status=doc.status,
        items_changed=items_changed,
        removed_variant_ids=removed_variant_ids,
    )


def on_sales_order_submit(doc, method=None):
    """
    The one 'vice versa' direction that was genuinely missing: a Sales
    Order created directly in ERPNext (not from a Shopify pull/webhook)
    never had anything pushing it to Shopify at all. Only fires for orders
    with at least one Shopify-linked Item -- an order with zero Shopify
    products has nothing meaningful to create over there.
    """
    if doc.flags.from_shopify_sync:
        return
    if doc.get("sh_shopify_order_id"):
        return  # already a Shopify-origin order, nothing to push
    if not any(
        frappe.db.get_value("Item", item.item_code, "sh_shopify_variant_id")
        for item in doc.items
    ):
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_push.push_order_create",
        queue="short",
        timeout=120,
        sales_order=doc.name,
    )


def on_sales_order_cancel(doc, method=None):
    if doc.flags.from_shopify_sync:
        return
    if not doc.get("sh_shopify_order_id"):
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_push.push_order_cancel",
        queue="short",
        timeout=60,
        order_id=doc.sh_shopify_order_id,
        sales_order=doc.name,
    )


# ── Background job bodies ────────────────────────────────────────────────────

def push_order_update(order_id: str, sales_order: str, status: str, items_changed: bool = False, removed_variant_ids: list = None):
    """
    Pushes order status updates to Shopify. If line items changed on the SO,
    check state guard: if Delivery Notes exist (shipment started), reject the
    update and log a clear error since the Shopify order can't be modified at
    that point anyway. Otherwise, if any of the changed rows were outright
    removed (not just qty/rate edited), push that removal via Shopify's
    Order Editing API. Additions/qty/rate edits still have no Shopify-side
    equivalent (orderUpdate doesn't support them) and fall back to the
    manual-edit warning.
    """
    removed_variant_ids = removed_variant_ids or []

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

        if removed_variant_ids and _remove_shopify_line_items(order_id, removed_variant_ids, sales_order):
            return

        # Items changed but no shipment yet, and either nothing was removed
        # (just added/qty/rate edited) or the removal push itself failed --
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

    try:
        client = ShopifyGraphQLClient()
        data = client.execute(_ORDER_UPDATE_MUTATION, {
            "input": {
                "id": _to_gid(order_id),
                "note": f"Alaiy OS: {sales_order} status = {status}",
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
    flagged loudly since Shopify's total won't match ERPNext's.
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
