"""
Alaiy OS -> Shopify fulfillment push (outbound direction). delivery_notes.py
already pulls Shopify fulfillments IN as Delivery Notes (including tracking,
via _sync_tracking); nothing pushed a Delivery Note created here back OUT to
Shopify -- create, tracking edits, and cancel were all a ground-up gap. This
module builds all three, reusing the same sh_tracking_number/sh_tracking_company
fields _sync_tracking already writes for the inbound direction.

Gated by Shopify Connector Settings.sh_fulfillment_sync_direction: creating a
NEW Shopify fulfillment from a Delivery Note submit only happens when that
setting is "Alaiy OS -> Shopify (two-way)" (default is inbound-only, byte-
for-byte unchanged from before this module existed). Once a fulfillment has
actually been pushed (sh_shopify_fulfillment_id is set on the Delivery Note),
editing its tracking or cancelling it keeps working even if the setting is
later switched back -- that fulfillment already exists on Shopify because of
something this app did; the setting only gates creating new ones.
"""

import frappe

from alaiy_os_connector_shopify.shopify.order.queries import (
    _FULFILLMENT_ORDERS_QUERY, _FULFILLMENT_CREATE_MUTATION,
    _FULFILLMENT_CANCEL_MUTATION, _FULFILLMENT_TRACKING_UPDATE_MUTATION,
)
from alaiy_os_connector_shopify.shopify.order.utils import _to_gid
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver

_TWO_WAY = "Alaiy OS → Shopify (two-way)"


def _fulfillment_gid(fulfillment_id: str) -> str:
    """sh_shopify_fulfillment_id is always stored as the plain legacy
    numeric id -- rebuild the GID Shopify's mutations actually require."""
    return f"gid://shopify/Fulfillment/{fulfillment_id}"


def _sales_order_of(dn):
    for item in dn.items:
        if item.against_sales_order:
            return item.against_sales_order
    return None


def _open_fulfillment_order_line_items(client, order_gid):
    """
    Walks the full fulfillmentOrders connection (an order can have more than
    one -- prior partial fulfillments, multiple locations) and returns every
    OPEN line item with remainingQuantity > 0, keyed by fulfillment order id,
    alongside the location each fulfillment order is assigned to.
    """
    by_fulfillment_order = {}
    location_by_fulfillment_order = {}
    after = None
    while True:
        data = client.execute(_FULFILLMENT_ORDERS_QUERY, {"id": order_gid, "after": after})
        connection = ((data.get("order") or {}).get("fulfillmentOrders")) or {}
        for node in connection.get("nodes") or []:
            if node.get("status") != "OPEN":
                continue
            open_lines = [
                li for li in (node.get("lineItems") or {}).get("nodes", [])
                if (li.get("remainingQuantity") or 0) > 0
            ]
            if open_lines:
                by_fulfillment_order[node["id"]] = open_lines
                location_by_fulfillment_order[node["id"]] = (
                    ((node.get("assignedLocation") or {}).get("location") or {}).get("id")
                )
        page_info = connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
    return by_fulfillment_order, location_by_fulfillment_order


def _match_dn_items_to_fulfillment_orders(dn, open_by_fulfillment_order):
    """
    Matches each Delivery Note item to the Shopify fulfillment-order line
    item it corresponds to (by variant id first, SKU as fallback -- same as
    push.py's own push_order_create), and caps the quantity requested at the
    smaller of what the DN actually shipped and what Shopify still has open.
    Only lines the DN really has get pushed -- this is what makes partial/
    warehouse-scanned shipments correct instead of blindly fulfilling
    everything still open on the order.

    Returns (fulfillment_input_per_order: dict, unmatched_item_codes: list).
    """
    qty_by_item = {}
    for item in dn.items:
        qty_by_item[item.item_code] = qty_by_item.get(item.item_code, 0) + item.qty

    remaining_needed = dict(qty_by_item)
    result = {}
    for fulfillment_order_id, line_items in open_by_fulfillment_order.items():
        matched = []
        for li in line_items:
            variant_id = str((li.get("variant") or {}).get("legacyResourceId") or "")
            item_code = listing_resolver.item_by_variant_id(variant_id) if variant_id else None
            if not item_code:
                sku = (li.get("sku") or "").strip()
                if sku and frappe.db.exists("Item", sku):
                    item_code = sku
            if not item_code or remaining_needed.get(item_code, 0) <= 0:
                continue
            qty = min(remaining_needed[item_code], li.get("remainingQuantity") or 0)
            if qty <= 0:
                continue
            matched.append({"id": li["id"], "quantity": int(qty)})
            remaining_needed[item_code] -= qty
        if matched:
            result[fulfillment_order_id] = matched

    unmatched = [code for code, qty in remaining_needed.items() if qty > 0]
    return result, unmatched


def _bucket_by_location(fulfillment_input_per_order, location_by_fulfillment_order):
    """
    fulfillmentCreate requires every fulfillment order in one call to be
    assigned to the same Shopify location -- a Delivery Note whose items span
    locations (multi-warehouse setups) must become one fulfillmentCreate call
    per location, not one call mixing both. Unassigned/unknown locations
    (missing assignedLocation.location.id) fall into their own bucket rather
    than being merged with a real location, since Shopify would reject that
    mix too.
    """
    buckets = {}
    for fulfillment_order_id, line_items in fulfillment_input_per_order.items():
        location_id = location_by_fulfillment_order.get(fulfillment_order_id)
        buckets.setdefault(location_id, {})[fulfillment_order_id] = line_items
    return buckets


def push_delivery_note_fulfillment(delivery_note: str, tracking_number: str = None, carrier: str = None, tracking_url: str = None, notify_customer: bool = True):
    """
    Creates a real Shopify fulfillment for this Delivery Note's items and
    writes the resulting Shopify fulfillment id back onto the Delivery Note
    -- this is the same field the inbound path (_sync_fulfillments) checks
    before creating a Delivery Note for a fulfillment event, so when
    Shopify's own webhook echoes this fulfillment back, it's already
    accounted for and no duplicate Delivery Note is created.
    """
    dn = frappe.get_doc("Delivery Note", delivery_note)
    if dn.sh_shopify_fulfillment_id:
        frappe.throw(f"{dn.name} is already linked to a Shopify fulfillment ({dn.sh_shopify_fulfillment_id}).")

    so_name = _sales_order_of(dn)
    if not so_name:
        frappe.throw(f"{dn.name} has no Sales Order reference -- cannot resolve its Shopify order.")

    shopify_order_id = frappe.db.get_value("Sales Order", so_name, "sh_shopify_order_id")
    if not shopify_order_id:
        frappe.throw(f"{so_name} has no Shopify order linked -- nothing to push fulfillment to.")

    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    client = ShopifyGraphQLClient()
    order_gid = _to_gid(shopify_order_id)

    open_by_fulfillment_order, location_by_fulfillment_order = _open_fulfillment_order_line_items(client, order_gid)
    if not open_by_fulfillment_order:
        frappe.throw(f"Shopify order for {so_name} has no open fulfillment orders left to fulfill.")

    fulfillment_input_per_order, unmatched = _match_dn_items_to_fulfillment_orders(dn, open_by_fulfillment_order)
    if unmatched:
        frappe.log_error(
            title=f"Shopify: fulfillment push for {dn.name} could not match every item",
            message=f"Sales Order: {so_name}\nUnmatched item codes (no linked Shopify variant/SKU, or nothing left open there): {unmatched}",
        )
    if not fulfillment_input_per_order:
        frappe.throw(f"{dn.name}'s items could not be matched to any open Shopify fulfillment order line.")

    tracking_info = None
    if tracking_number:
        tracking_info = {"number": tracking_number, "company": carrier or ""}
        if tracking_url:
            tracking_info["url"] = tracking_url

    # fulfillmentCreate requires every fulfillment order named in one call to
    # be assigned to the same Shopify location -- a Delivery Note whose items
    # span locations (multi-warehouse setups) must become one call per
    # location, not one call mixing both (Shopify rejects the mix).
    buckets = _bucket_by_location(fulfillment_input_per_order, location_by_fulfillment_order)

    fulfillments = []
    for location_id, orders_in_bucket in buckets.items():
        # FulfillmentInput has no fulfillmentOrderId/fulfillmentOrderLineItems
        # fields of its own -- confirmed live against a real store ("Field is
        # not defined on FulfillmentInput"). The real shape wraps every
        # fulfillment order's line items into ONE lineItemsByFulfillmentOrder
        # array -- one call per location bucket, since Shopify requires every
        # entry in that array to share a location.
        fulfillment_input = {
            "lineItemsByFulfillmentOrder": [
                {"fulfillmentOrderId": fulfillment_order_id, "fulfillmentOrderLineItems": line_items}
                for fulfillment_order_id, line_items in orders_in_bucket.items()
            ],
            "notifyCustomer": notify_customer,
        }
        if tracking_info:
            fulfillment_input["trackingInfo"] = tracking_info

        data = client.execute(_FULFILLMENT_CREATE_MUTATION, {"fulfillment": fulfillment_input})
        result = data.get("fulfillmentCreate") or {}
        errors = result.get("userErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: fulfillment push failed for {dn.name}",
                message=f"Sales Order: {so_name}\nLocation: {location_id}\n{errors}",
            )
            frappe.throw(f"Shopify rejected the fulfillment push: {errors}")
        fulfillment = result.get("fulfillment") or {}
        if fulfillment:
            fulfillments.append(fulfillment)

    if fulfillments:
        # Stored as the plain legacy numeric id, matching every other
        # sh_shopify_*_id field in this app (e.g. Sales Order's
        # sh_shopify_order_id) and the INBOUND path's own convention
        # (_sync_tracking writes Shopify's plain webhook fulfillment id to
        # this same field). Confirmed live: storing the full GID here
        # instead broke the very next webhook echo -- fulfillmentTrackingInfoUpdate/
        # fulfillmentCancel need the GID form, so it's rebuilt from this at
        # call time (_fulfillment_gid) rather than stored that way.
        #
        # sh_shopify_fulfillment_id holds one id (a Delivery Note maps 1:1 to
        # one fulfillment event in the inbound direction), so when the DN's
        # items spanned more than one location bucket, only the FIRST created
        # fulfillment is linked/trackable there -- the others were still
        # created on Shopify, just logged rather than silently dropped, since
        # reflecting a Delivery Note split back across multiple Shopify
        # fulfillments isn't implemented.
        first = fulfillments[0]
        if first.get("legacyResourceId"):
            updates = {"sh_shopify_fulfillment_id": first["legacyResourceId"]}
            if tracking_number:
                updates["sh_tracking_number"] = tracking_number
                updates["sh_tracking_company"] = carrier or ""
            frappe.db.set_value("Delivery Note", dn.name, updates)
            frappe.db.commit()
        if len(fulfillments) > 1:
            frappe.log_error(
                title=f"Shopify: {dn.name} pushed across {len(fulfillments)} Shopify locations",
                message=(
                    f"Fulfillment ids created: {[f.get('legacyResourceId') for f in fulfillments]}\n"
                    f"Only the first ({first.get('legacyResourceId')}) is linked via sh_shopify_fulfillment_id."
                ),
            )

    return fulfillments


@frappe.whitelist()
def push_fulfillment_for_delivery_note(delivery_note: str, tracking_number: str = None, carrier: str = None, tracking_url: str = None):
    """Whitelisted entry point -- called explicitly by carrier connectors
    (e.g. FedEx's create_shipment_for_delivery_note) once a real tracking
    number exists. Independent of the two-way setting: an explicit call like
    this is the caller opting in directly, not the generic on_submit hook.

    Routes by whether a Shopify fulfillment already exists for this
    Delivery Note -- confirmed live: a DN pushed out by the generic
    on_delivery_note_submit two-way hook already has sh_shopify_fulfillment_id
    set by the time a carrier connector calls this with a real tracking
    number, and push_delivery_note_fulfillment (create-only) throws outright
    on an already-linked DN. An existing fulfillment gets a tracking UPDATE
    instead of a second create attempt.
    """
    dn = frappe.get_doc("Delivery Note", delivery_note)
    if dn.sh_shopify_fulfillment_id:
        if not tracking_number:
            return []
        return [_push_tracking_update(_fulfillment_gid(dn.sh_shopify_fulfillment_id), tracking_number, carrier or "", delivery_note, raise_on_error=True)]
    return push_delivery_note_fulfillment(delivery_note, tracking_number, carrier, tracking_url)


def on_delivery_note_submit(doc, method=None):
    """
    Generic outbound hook for any Delivery Note submitted in Alaiy OS (e.g. a
    warehouse scanning items out against a Sales Order) -- gated by
    Shopify Connector Settings.sh_fulfillment_sync_direction so existing
    inbound-only installs see no behavior change by default.
    """
    if doc.flags.from_shopify_sync:
        return  # mirrors a fulfillment Shopify already knows about
    if doc.sh_shopify_fulfillment_id:
        return  # already linked (defensive -- from_shopify_sync should have caught this)
    if (frappe.db.get_single_value("Shopify Connector Settings", "sh_fulfillment_sync_direction") or "") != _TWO_WAY:
        return
    so_name = _sales_order_of(doc)
    if not so_name or not frappe.db.get_value("Sales Order", so_name, "sh_shopify_order_id"):
        return
    # enqueue_after_commit=True -- confirmed live: without it, a fast
    # worker could dequeue and start push_delivery_note_fulfillment_job
    # before the caller's own frappe.db.commit() (e.g. fulfill_order's,
    # right after dn.submit()) had made this DN visible to other DB
    # connections yet, raising DoesNotExistError on a real, correctly
    # submitted Delivery Note. Same idiom already used in
    # listing_hooks.py for this exact class of race.
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order.fulfillment_push.push_delivery_note_fulfillment_job",
        queue="short", timeout=120, delivery_note=doc.name,
        enqueue_after_commit=True,
    )


def push_delivery_note_fulfillment_job(delivery_note: str):
    """Enqueued body for on_delivery_note_submit -- runs outside the DN's own
    submit transaction, so a Shopify-side failure here logs but never rolls
    back or re-opens the (already successful) local submit."""
    dn = frappe.get_doc("Delivery Note", delivery_note)
    try:
        push_delivery_note_fulfillment(
            delivery_note, tracking_number=dn.sh_tracking_number or None, carrier=dn.sh_tracking_company or None,
        )
    except Exception:
        frappe.log_error(
            title=f"Shopify: two-way fulfillment push failed for {delivery_note}",
            message=frappe.get_traceback(),
        )


def on_delivery_note_update_after_submit(doc, method=None):
    """Editing sh_tracking_number/sh_tracking_company on a Delivery Note that
    already has a linked Shopify fulfillment pushes the change to Shopify."""
    if not doc.sh_shopify_fulfillment_id:
        return
    if not (doc.has_value_changed("sh_tracking_number") or doc.has_value_changed("sh_tracking_company")):
        return
    if not doc.sh_tracking_number:
        return  # nothing to push -- clearing tracking has no Shopify-side equivalent here
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order.fulfillment_push.push_tracking_update_job",
        queue="short", timeout=60,
        fulfillment_gid=_fulfillment_gid(doc.sh_shopify_fulfillment_id),
        tracking_number=doc.sh_tracking_number, carrier=doc.sh_tracking_company or "",
        delivery_note=doc.name,
    )


def push_tracking_update_job(fulfillment_gid: str, tracking_number: str, carrier: str, delivery_note: str):
    """Enqueued body for on_delivery_note_update_after_submit -- best-effort,
    logs and swallows rather than raising (nothing is awaiting a result)."""
    try:
        _push_tracking_update(fulfillment_gid, tracking_number, carrier, delivery_note, raise_on_error=False)
    except Exception:
        pass


def _push_tracking_update(fulfillment_gid: str, tracking_number: str, carrier: str, delivery_note: str, raise_on_error: bool):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    try:
        client = ShopifyGraphQLClient()
        data = client.execute(_FULFILLMENT_TRACKING_UPDATE_MUTATION, {
            "fulfillmentId": fulfillment_gid,
            "trackingInfoInput": {"number": tracking_number, "company": carrier},
            "notifyCustomer": True,
        })
        result = data.get("fulfillmentTrackingInfoUpdate") or {}
        errors = result.get("userErrors") or []
    except Exception:
        frappe.log_error(
            title=f"Shopify: tracking update push failed for {delivery_note}",
            message=frappe.get_traceback(),
        )
        if raise_on_error:
            raise
        return None

    if errors:
        frappe.log_error(
            title=f"Shopify: tracking update push failed for {delivery_note}",
            message=str(errors),
        )
        if raise_on_error:
            frappe.throw(f"Shopify rejected the tracking update: {errors}")
        return None
    return result.get("fulfillment") or {}


def on_delivery_note_cancel(doc, method=None):
    """Cancelling a Delivery Note that was pushed out as a Shopify
    fulfillment (this app's own two-way push, not an inbound mirror --
    from_shopify_sync is never set on those) cancels that fulfillment on
    Shopify too. Kept independent of the current sync-direction setting: the
    fulfillment exists on Shopify because of something this app already did,
    regardless of whether the setting has since been switched back."""
    if doc.flags.from_shopify_sync or not doc.sh_shopify_fulfillment_id:
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order.fulfillment_push.push_fulfillment_cancel_job",
        queue="short", timeout=60,
        fulfillment_gid=_fulfillment_gid(doc.sh_shopify_fulfillment_id), delivery_note=doc.name,
    )


def push_fulfillment_cancel_job(fulfillment_gid: str, delivery_note: str):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    try:
        client = ShopifyGraphQLClient()
        data = client.execute(_FULFILLMENT_CANCEL_MUTATION, {"id": fulfillment_gid})
        errors = (data.get("fulfillmentCancel") or {}).get("userErrors") or []
        if errors:
            # Most common benign case: fulfillment already delivered/closed
            # on Shopify's side, which rejects cancellation -- still logged
            # so it's visible, not silently swallowed.
            frappe.log_error(
                title=f"Shopify: fulfillment cancel push failed for {delivery_note}",
                message=str(errors),
            )
    except Exception:
        frappe.log_error(
            title=f"Shopify: fulfillment cancel push failed for {delivery_note}",
            message=frappe.get_traceback(),
        )
