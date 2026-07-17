"""
Small shared order helpers -- moved verbatim from order_sync.py and
order_push.py, unchanged.
"""

import contextlib

import frappe
from frappe.utils import flt


@contextlib.contextmanager
def _as_administrator():
    """
    handle_webhook is allow_guest=True, so frappe.session.user is "Guest"
    for the whole request AND the background job it enqueues (RQ workers
    inherit the enqueuing request's user). make_delivery_note()'s internal
    get_mapped_doc() checks create-permission on the mapped doc BEFORE we
    ever get a chance to set ignore_permissions on it -- Guest fails that
    check outright, unlike a plain doc.insert() where our own
    flags.ignore_permissions actually takes effect. Elevate just for this
    one call, then restore -- RQ workers reuse the same process across
    multiple jobs, so leaving this elevated would leak into unrelated ones.
    """
    original_user = frappe.session.user
    frappe.set_user("Administrator")
    try:
        yield
    finally:
        frappe.set_user(original_user)


def _order_node_to_rest_shape(node: dict) -> dict:
    """
    Reshape a GraphQL order node into the same REST-style dict that
    _upsert_order/_cancel_order/_resolve_item_code already consume.
    Webhook payloads are still REST-shaped JSON regardless of the GraphQL
    mutation used to register the subscription (Shopify sends the classic
    resource representation to webhook endpoints either way) -- keeping one
    shared internal shape means the webhook and pull code paths below don't
    need to diverge.
    """
    customer = node.get("customer") or {}
    line_items = []
    for li in (node.get("lineItems") or {}).get("nodes", []):
        variant = li.get("variant") or {}
        money = (li.get("originalUnitPriceSet") or {}).get("shopMoney") or {}
        line_items.append({
            "sku": li.get("sku"),
            "title": li.get("title"),
            "quantity": li.get("quantity"),
            "variant_id": variant.get("legacyResourceId"),
            "price": money.get("amount"),
        })
    return {
        "id": node.get("legacyResourceId"),
        "name": node.get("name"),
        "customer": {
            "id": customer.get("legacyResourceId"),
            "first_name": customer.get("firstName"),
            "last_name": customer.get("lastName"),
            "email": customer.get("email"),
        } if customer.get("legacyResourceId") else {},
        "line_items": line_items,
        "note": node.get("note") or "",
        "financial_status": (node.get("displayFinancialStatus") or "").lower(),
        "fulfillment_status": (node.get("displayFulfillmentStatus") or "").lower(),
    }


def _line_item_qty(li: dict) -> float:
    """
    Shopify webhook line items carry BOTH "quantity" (the order's original,
    pre-edit quantity) and "current_quantity" (the true post-edit quantity --
    0 if the line was removed via Order Editing). "quantity" never changes
    once the order is placed, even after an edit removes the line entirely --
    confirmed live: an edited order still showed "quantity": 1 on a line the
    merchant had just deleted, only "current_quantity": 0 revealed the
    removal. Reading "quantity" alone meant edits that removed items were
    silently invisible to line-item reconciliation. current_quantity is only
    present on webhook payloads (not the GraphQL pull query), so fall back
    to "quantity" when it's absent.
    """
    if "current_quantity" in li:
        return flt(li.get("current_quantity", 0))
    return flt(li.get("quantity", 1))


def _resolve_item_code(line_item):
    sku = (line_item.get("sku") or "").strip()
    if sku and frappe.db.exists("Item", sku):
        return sku

    variant_id = str(line_item.get("variant_id") or "")
    if variant_id:
        by_variant = frappe.db.get_value(
            "Item", {"sh_shopify_variant_id": variant_id}, "name"
        )
        if by_variant:
            return by_variant

    title = (line_item.get("title") or "").strip()
    if title and frappe.db.exists("Item", title):
        return title

    return None


def _to_gid(shopify_order_id: str) -> str:
    return f"gid://shopify/Order/{shopify_order_id}"
