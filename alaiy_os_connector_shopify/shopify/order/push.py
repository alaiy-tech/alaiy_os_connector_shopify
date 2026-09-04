"""
Background job bodies for Alaiy OS -> Shopify order push-back -- moved
verbatim from order_push.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.queries import (
    _ORDER_UPDATE_MUTATION, _ORDER_CREATE_MUTATION, _ORDER_CANCEL_MUTATION, _ORDER_TAGS_QUERY,
)
from alaiy_os_connector_shopify.shopify.order.utils import _to_gid
from alaiy_os_connector_shopify.shopify.order.push_line_items import _apply_shopify_line_item_changes
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver

from alaiy_os_connector_shopify import connections

_STATUS_TAG_PREFIX = "alaiy-os-status:"


def parse_tags(raw) -> list:
    """Shopify's REST webhook payload sends tags as one comma-separated
    string; the GraphQL API sends a list. Accepts either."""
    parts = raw if isinstance(raw, list) else (raw or "").split(",")
    return [t.strip() for t in parts if t.strip()]


def strip_status_tag(tags: list) -> list:
    return [t for t in tags if not t.startswith(_STATUS_TAG_PREFIX)]


def _merge_status_tag(client, gid: str, status: str, sales_order: str = None) -> list:
    """
    orderUpdate's `tags` input is a full replace, not additive -- confirmed
    live, every status push was silently wiping any real tag a human (or
    another app) had put on the Shopify order, leaving only our own status
    tag. Read the order's current tags first and union in Alaiy OS's own
    sh_shopify_order_tags field (what the user just edited locally, if
    anything) plus our status tag (replacing any previous
    alaiy-os-status:* entry), so a tag added on either side survives a
    push from the other.
    """
    try:
        data = client.execute(_ORDER_TAGS_QUERY, {"id": gid})
        current = (data.get("order") or {}).get("tags") or []
    except Exception:
        frappe.log_error(
            title=f"Shopify: failed to read current tags for {gid}",
            message=frappe.get_traceback(),
        )
        current = []
    kept = strip_status_tag(current)

    local_tags = []
    if sales_order:
        local_tags = parse_tags(frappe.db.get_value("Sales Order", sales_order, "sh_shopify_order_tags"))

    merged = list(kept)
    for t in local_tags:
        if t not in merged:
            merged.append(t)
    return merged + [f"{_STATUS_TAG_PREFIX}{status}"]


def _address_to_shopify_input(address_fields: dict, customer_name: str = "") -> dict:
    """
    Maps Alaiy OS's Address fields to Shopify's MailingAddressInput shape.
    Confirmed live: Shopify rejects the mutation outright without a last
    name ("Enter a last name") -- Alaiy OS's Address doctype has no
    person-name fields of its own, so split the Sales Order's customer
    name instead. A single-word name (e.g. a company name used as the
    customer) still needs SOME lastName value or Shopify rejects it, so
    it's used for both first and last in that case.
    """
    parts = (customer_name or "Customer").split(None, 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else parts[0]
    return {
        "firstName": first_name,
        "lastName": last_name,
        "address1": address_fields.get("address_line1") or "",
        "address2": address_fields.get("address_line2") or "",
        "city": address_fields.get("city") or "",
        "province": address_fields.get("state") or "",
        "zip": address_fields.get("pincode") or "",
        "country": address_fields.get("country") or "",
        "phone": address_fields.get("phone") or "",
    }


def push_order_update(order_id: str, sales_order: str, status: str, items_changed: bool = False, removed_variant_ids: list = None, added_items: list = None, changed_quantities: list = None, shipping_address: dict = None, swapped_variants: list = None, shipping_line: dict = None, custom_items: list = None):
    """
    Pushes order status/note/tags/shipping-address updates to Shopify, and
    (if line items changed) adds/removes/quantity edits/variant swaps/a
    shipping line/custom items via Shopify's Order Editing API in one
    session. If Delivery Notes exist (shipment started), item changes are
    rejected -- the Shopify order can't be modified at that point anyway --
    but status/note/tags/address still push regardless, since those aren't
    blocked by a started shipment. Rate-only edits on a surviving row (no
    qty change) still have no Shopify-side equivalent and fall back to the
    manual-edit warning, same as anything the Order Editing API call itself
    fails to apply cleanly.

    swapped_variants/shipping_line/custom_items have no automatic upstream
    detection yet (unlike removed/added/changed_quantities, which
    doc_events.py derives from a before/after item snapshot) -- callers
    pass these explicitly for now.
    """
    removed_variant_ids = removed_variant_ids or []
    added_items = added_items or []
    changed_quantities = changed_quantities or []
    swapped_variants = swapped_variants or []
    custom_items = custom_items or []
    frappe.log_error(
        title=f"Shopify DEBUG: push_order_update {sales_order}",
        message=(
            f"items_changed={items_changed} removed_variant_ids={removed_variant_ids!r} "
            f"added_items={added_items!r} changed_quantities={changed_quantities!r} "
            f"swapped_variants={swapped_variants!r} shipping_line={shipping_line!r} "
            f"custom_items={custom_items!r} shipping_address_changed={shipping_address is not None}"
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
        elif (
            removed_variant_ids or added_items or changed_quantities
            or swapped_variants or shipping_line or custom_items
        ) and _apply_shopify_line_item_changes(
            order_id, removed_variant_ids, added_items, sales_order, changed_quantities,
            swapped_variants=swapped_variants, shipping_line=shipping_line, custom_items=custom_items,
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
        client = ShopifyGraphQLClient(connections.require_enabled())
        gid = _to_gid(order_id)
        merged_tags = _merge_status_tag(client, gid, status, sales_order)
        order_input = {
            "id": gid,
            "note": notes,
            "tags": merged_tags,
        }
        if shipping_address:
            customer = frappe.db.get_value("Sales Order", sales_order, "customer_name")
            order_input["shippingAddress"] = _address_to_shopify_input(shipping_address, customer)
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
        client = ShopifyGraphQLClient(connections.require_enabled())
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
        client = ShopifyGraphQLClient(connections.require_enabled())
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
