"""
Small shared order helpers -- moved verbatim from order_sync.py and
order_push.py, unchanged.
"""

import contextlib

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver


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

    Restores sid and session data too, not just the user. frappe.set_user does
    more than change who you are:

        local.session.user = username
        local.session.sid  = username      # the real sid is gone
        local.session.data = _dict()       # session data wiped

    so set_user(original_user) does not put a session back -- sid is left as
    the literal user name rather than the real session id, and the data empty.
    For a Guest webhook that costs nothing, since there is no session worth
    keeping. But these helpers also run inside a real signed-in request
    whenever a user submits a Delivery Note from a storefront portal, and there
    it signed that user out mid-task: the work committed, then the next request
    arrived as Guest. Nothing raises, which is why it reads as a cookie or
    cache problem rather than a permission one.
    """
    session = frappe.session
    original_user = session.user
    original_sid = session.sid
    original_data = session.data
    frappe.set_user("Administrator")
    try:
        yield
    finally:
        # set_user first so role and permission caches rebuild for the real
        # user, then restore the two fields it overwrites.
        frappe.set_user(original_user)
        session.sid = original_sid
        session.data = original_data


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
    tax_lines = []
    for tl in (node.get("taxLines") or []):
        amount = ((tl.get("priceSet") or {}).get("shopMoney") or {}).get("amount")
        tax_lines.append({
            "title": tl.get("title") or "Tax",
            "rate": tl.get("rate"),
            "price": amount,
        })
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
    def _addr(a):
        if not a:
            return None
        # GraphQL address fields already match the REST webhook shape 1:1.
        return {k: a.get(k) for k in
                ("name", "address1", "address2", "city", "province", "country", "zip", "phone")}

    ship_line = node.get("shippingLine") or {}
    shipping_lines = []
    if ship_line:
        amt = ((ship_line.get("originalPriceSet") or {}).get("shopMoney") or {}).get("amount")
        shipping_lines.append({"title": ship_line.get("title") or "Shipping", "price": amt})

    # Reshaped to the REST webhook's own fulfillments shape so the delivery
    # sync path doesn't have to care which source it came from. Now also
    # carries line_items (from fulfillmentLineItems) -- confirmed live that
    # an order shipped in more than one real Shopify fulfillment was being
    # collapsed into a single local Delivery Note by the full-order
    # fallback below, because this reshape used to drop per-fulfillment
    # line items entirely (a pull-only order never had them to route
    # through _sync_fulfillments). With line_items present, _upsert_order
    # can route these into _sync_fulfillments just like a webhook payload,
    # creating one Delivery Note per real fulfillment instead of one per
    # order.
    fulfillments = []
    for f in (node.get("fulfillments") or []):
        tracking = f.get("trackingInfo") or []
        first = tracking[0] if tracking else {}
        fulfillment_line_items = []
        for fli_node in ((f.get("fulfillmentLineItems") or {}).get("nodes") or []):
            li = fli_node.get("lineItem") or {}
            variant = li.get("variant") or {}
            fulfillment_line_items.append({
                "sku": li.get("sku"),
                "title": li.get("title"),
                "quantity": fli_node.get("quantity"),
                "variant_id": variant.get("legacyResourceId"),
            })
        fulfillments.append({
            "id": f.get("legacyResourceId"),
            "display_status": (f.get("displayStatus") or "").upper(),
            "tracking_number": ",".join(t.get("number") or "" for t in tracking).strip(","),
            "tracking_company": first.get("company") or "",
            "tracking_url": ",".join(t.get("url") or "" for t in tracking).strip(","),
            "line_items": fulfillment_line_items,
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
        "tax_lines": tax_lines,
        "taxes_included": bool(node.get("taxesIncluded")),
        "shipping_address": _addr(node.get("shippingAddress")),
        "billing_address": _addr(node.get("billingAddress")),
        "shipping_lines": shipping_lines,
        "fulfillments": fulfillments,
        "total_discounts": ((node.get("totalDiscountsSet") or {}).get("shopMoney") or {}).get("amount") or "0",
        "currency": node.get("currencyCode") or "",
        "note": node.get("note") or "",
        "tags": node.get("tags") or [],
        "created_at": node.get("createdAt") or "",
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
        # Listing Variant's copy first (owning row), Item as fallback --
        # same helper already used elsewhere for this exact reverse lookup.
        by_variant = listing_resolver.item_by_variant_id(variant_id)
        if by_variant:
            return by_variant

    title = (line_item.get("title") or "").strip()
    if title and frappe.db.exists("Item", title):
        return title

    # Nothing matched. Before giving up and letting the caller fall back to
    # the shared "Shopify Custom Item" placeholder, try importing the product
    # this line actually refers to.
    #
    # The catalogue import only takes the statuses the site asked for --
    # Active, typically -- but an order can reference a product that was
    # ARCHIVED or set to DRAFT after it sold. That is ordinary retail
    # behaviour for one-of-a-kind stock. Confirmed live: real jewellery lines
    # (a Roberto Coin earring, a Rapport London box) collapsed onto the
    # placeholder, which left the order with no supplier to pay, no cost, and
    # a fulfillment that could not be mapped to any line.
    #
    # An order referencing a product is proof it was real, so the status
    # filter does not apply here the way it does to a bulk sweep -- this
    # fetches exactly one product, only when an order needs it.
    if variant_id:
        imported = _import_product_for_order_line(variant_id)
        if imported:
            return imported

    return None


def _import_product_for_order_line(variant_id: str):
    """Import the single product owning variant_id, whatever its status.

    Returns the resolved item_code, or None. Never raises: an order import
    must not fail because a product fetch did.

    The product is left disabled, since it is archived or draft on Shopify and
    so is not for sale -- it exists here for order history, supplier
    attribution and fulfillment matching, not to be sold again.
    """
    try:
        from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
        from alaiy_os_connector_shopify.shopify.product import importer
        from alaiy_os_connector_shopify.shopify.product.queries import _PRODUCTS_QUERY

        client = ShopifyGraphQLClient()
        found = client.execute(
            """query($id: ID!){ productVariant(id:$id){ product{ legacyResourceId } } }""",
            {"id": f"gid://shopify/ProductVariant/{variant_id}"},
        )
        product_id = str(
            (((found or {}).get("productVariant") or {}).get("product") or {}).get("legacyResourceId") or ""
        )
        if not product_id:
            return None

        for page in client.execute_paginated(
                _PRODUCTS_QUERY, {"first": 5, "query": f"id:{product_id}"}, ["products"]):
            for node in page:
                if str(node.get("legacyResourceId")) != product_id:
                    continue
                # Bypasses _import_product's status gate deliberately: that
                # gate exists to keep a bulk sweep from dragging in dead
                # products, which is a different question from an order
                # needing the one product it actually sold.
                importer._import_product_inner(node)

        item_code = listing_resolver.item_by_variant_id(variant_id)
        if item_code:
            frappe.db.set_value("Item", item_code, "disabled", 1)
            frappe.log_error(
                title="Shopify: imported an out-of-catalogue product for an order line",
                message=f"variant {variant_id} -> product {product_id} -> Item {item_code}. "
                        "Imported disabled: it is archived or draft on Shopify, so it exists "
                        "for order history and supplier attribution, not for sale.",
            )
        return item_code
    except Exception:
        frappe.log_error(
            title=f"Shopify: could not import product for order line variant {variant_id}",
            message=frappe.get_traceback(),
        )
        return None


def _to_gid(shopify_order_id: str) -> str:
    return f"gid://shopify/Order/{shopify_order_id}"
