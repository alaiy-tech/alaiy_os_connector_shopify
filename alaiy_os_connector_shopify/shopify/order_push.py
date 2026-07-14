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

# NOTE: orderCreate's exact input shape (OrderCreateOrderInput) should be
# double-checked against Shopify's live 2026-07 schema reference before
# relying on this in production -- this wasn't verified against a live
# introspection/sandbox call, only against the general shape Shopify's
# GraphQL Admin API has documented for this mutation historically.
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


def _to_gid(shopify_order_id: str) -> str:
    return f"gid://shopify/Order/{shopify_order_id}"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _detect_items_changed(doc) -> bool:
    """
    Check if Sales Order's items have been added, removed, or modified.
    Returns True if any items field changed, False if only status/metadata changed.
    """
    if not doc.get("items"):
        return False

    # Get the original items from database (before any changes in this session)
    try:
        original_so = frappe.get_doc("Sales Order", doc.name)
        original_items = {
            (item.item_code, item.qty, item.rate) for item in original_so.items
        }
        current_items = {
            (item.item_code, item.qty, item.rate) for item in doc.items
        }
        return original_items != current_items
    except Exception:
        # If we can't fetch original, assume no change to avoid false positives
        return False


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

    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_push.push_order_update",
        queue="short",
        timeout=60,
        order_id=doc.sh_shopify_order_id,
        sales_order=doc.name,
        status=doc.status,
        items_changed=items_changed,
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

def push_order_update(order_id: str, sales_order: str, status: str, items_changed: bool = False):
    """
    Pushes order status updates to Shopify. If line items changed on the SO,
    check state guard: if Delivery Notes exist (shipment started), reject the
    update and log a clear error since the Shopify order can't be modified at
    that point anyway. Otherwise, log a warning that manual order edit is needed
    on Shopify since orderUpdate mutation doesn't support line-item changes.
    """
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

        # Items changed but no shipment yet - warn user that Shopify needs manual edit
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
