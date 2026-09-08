import base64
import hashlib
import hmac
import json

import frappe

from alaiy_os_connector_shopify import connections


@frappe.whitelist(allow_guest=True)
def handle_webhook():
    """
    HMAC-validated webhook endpoint. Shopify calls this for registered topics.
    Validates the signature then enqueues the appropriate handler.

    Which store a delivery is for comes from X-Shopify-Shop-Domain, and the
    signature is then checked against THAT store's secrets and no others. On a
    bench holding several connections, trying every store's secret in turn
    would make any one seller's secret enough to have a payload accepted and
    processed as any other seller's order -- the header is the only thing in
    the request that says whose store it is, so it has to pick the key rather
    than merely be recorded.
    """
    request = frappe.request
    topic = request.headers.get("X-Shopify-Topic", "")
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")
    shop_domain = request.headers.get("X-Shopify-Shop-Domain", "")
    raw_body = request.data

    connection = connections.by_shop(shop_domain) if shop_domain else None
    if connection is None and len(connections.names()) == 1:
        # A bench whose one connection has no shop domain saved yet still
        # works, because there is only one store it could be. Deliberately not
        # `resolve_optional`, which would also answer with the *default* on a
        # bench holding several -- an unattributable delivery there has to be
        # refused, since nothing in the request says whose order it is and the
        # default store is just a guess wearing a flag.
        connection = connections.resolve_optional()

    if connection is None:
        # 401, not 503: an unattributable delivery is not a transient
        # condition Shopify could retry its way out of. Either the header
        # named a store this bench does not hold, or it named none and the
        # bench holds several. Retrying would produce the same answer, so
        # refuse outright rather than keeping it in Shopify's queue for 48
        # hours. The payload is not kept: with no connection resolved there
        # is no store to attribute it to, and an unauthenticated request
        # must not be able to write arbitrary bytes into the Error Log.
        frappe.log_error(
            title="Shopify webhook rejected: unknown store",
            message=f"topic={topic!r} shop={shop_domain!r}",
        )
        frappe.response.status_code = 401
        return {"ok": False, "reason": "unknown store"}

    if not connection.is_enabled:
        # 503, not 200. A 2xx tells Shopify the event was delivered, so it is
        # dropped from their queue and never retried -- and there is no
        # scheduled order pull to find it later, so every order, refund and
        # fulfillment arriving while the connector was switched off was lost
        # permanently, with nothing written down anywhere.
        #
        # Shopify retries a 5xx on its own schedule over roughly 48 hours, so a
        # brief disable (a deploy, a credential rotation) now catches up by
        # itself once the connector is back on. Beyond that window the event is
        # still lost, which is why the payload is recorded here as well: a
        # human can replay it from the Error Log.
        #
        # Reached only once the store IS attributed, so the log names it --
        # on a bench holding several connections, "which store was off" is
        # the first thing anyone replaying this needs to know.
        frappe.log_error(
            title=f"Shopify: webhook {topic} refused, connection disabled",
            message=(
                "The connection is disabled, so this event was refused with 503 for Shopify to "
                "retry. If it stays disabled past Shopify's retry window the event is gone, so "
                "the raw payload is kept here to be replayed by hand.\n\n"
                f"Connection: {connection.name}\nTopic: {topic}\n\n{(raw_body or b'')[:5000]}"
            ),
        )
        frappe.response.status_code = 503
        return {"ok": False, "reason": "connector disabled"}

    # Fail CLOSED: this endpoint is allow_guest -- at least one secret must
    # be configured, or every request is rejected, never silently accepted.
    #
    # Two independent delivery mechanisms hit this same endpoint, each
    # signed with its own secret: webhooks registered via the GraphQL
    # Admin API (webhookSubscriptionCreate) are signed with the app's
    # Client Secret, while webhooks configured on the legacy
    # Settings > Notifications page are signed with a separate secret
    # shown on that page. Confirmed live: "Order edit" (orders/edited)
    # is only ever delivered via the Notifications-page mechanism --
    # Shopify has no GraphQL-subscribable topic for order-edit diffs --
    # so both secrets must be accepted, not just one. Both belong to the
    # one store resolved above.
    candidate_secrets = [
        connection.get_password("sh_client_secret", raise_exception=False),
        connection.get_password("sh_webhook_secret", raise_exception=False),
    ]
    candidate_secrets = [s for s in candidate_secrets if s]
    if not candidate_secrets:
        frappe.log_error(
            title="Shopify webhook rejected: no secret configured",
            message=f"connection={connection.name!r}",
        )
        frappe.response.status_code = 401
        return {"ok": False, "reason": "no secret configured"}

    valid = False
    for secret in candidate_secrets:
        computed = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).digest()
        expected = base64.b64encode(computed).decode("utf-8")
        if hmac_header and hmac.compare_digest(expected, hmac_header):
            valid = True
            break
    if not valid:
        frappe.log_error(
            title="Shopify webhook rejected: HMAC mismatch (diagnostic)",
            message=f"topic={topic!r} connection={connection.name!r}",
        )
        frappe.response.status_code = 401
        return {"ok": False, "reason": "HMAC validation failed"}

    try:
        payload = json.loads(raw_body)
    except Exception:
        frappe.log_error(
            title="Shopify webhook rejected: invalid JSON (diagnostic)",
            message=f"topic={topic!r} raw_body[:200]={raw_body[:200]!r}",
        )
        frappe.response.status_code = 400
        return {"ok": False, "reason": "invalid JSON"}

    # The handlers resolve the enabled store themselves. That is the same
    # document as `connection` -- only one connection may be enabled at a time,
    # and this delivery was checked against that one above.
    _dispatch(topic, payload, connection.name)

    frappe.response.status_code = 200
    return {"ok": True}


def _dispatch(topic, payload, connection=None):
    """
    Hand the event to the right background job, naming the store it came from.

    The receiver above has already established which store this is -- the shop
    domain in the header is what the HMAC was checked against, and a delivery
    it cannot attribute is refused outright. Passing that name down is what
    lets the handlers scope their lookups: a Shopify order id is only unique
    inside one shop, so a refund for store B's order 1001 must not resolve
    store A's Sales Order and post a credit note against their books.

    A name rather than the document, because a document does not survive being
    serialised onto the queue.
    """
    # Order webhooks (inbound order sync)
    order_topics = {
        "orders/create", "orders/updated", "orders/edited",
        "orders/cancelled", "orders/fulfilled", "orders/paid", "orders/delete",
        "draft_orders/create", "draft_orders/update", "draft_orders/delete",
    }
    if topic in order_topics:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.order_sync.handle_order_webhook",
            queue="short",
            timeout=300,
            topic=topic,
            payload=payload,
            connection=connection,
        )

    # Refund webhooks (returns/credit notes, inbound)
    refund_topics = {"refunds/create"}
    if topic in refund_topics:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.order_sync.handle_refund_webhook",
            queue="short",
            timeout=300,
            topic=topic,
            payload=payload,
            connection=connection,
        )

    # Fulfillment webhooks (tracking number create/update)
    fulfillment_topics = {"fulfillments/create", "fulfillments/update"}
    if topic in fulfillment_topics:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.order_sync.handle_fulfillment_webhook",
            queue="short",
            timeout=300,
            topic=topic,
            payload=payload,
            connection=connection,
        )

    # Product webhooks (bidirectional product sync - inbound)
    product_topics = {
        "products/create", "products/update", "products/delete",
    }
    if topic in product_topics:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.handle_product_webhook",
            queue="short",
            timeout=300,
            topic=topic,
            payload=payload,
            connection=connection,
        )

    # Collection webhooks (bidirectional collection sync - inbound)
    collection_topics = {
        "collections/create", "collections/update", "collections/delete",
    }
    if topic in collection_topics:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.handle_collection_webhook",
            queue="short",
            timeout=300,
            topic=topic,
            payload=payload,
            connection=connection,
        )

    # Inventory webhooks (inbound leg of the bidirectional inventory sync)
    inventory_topics = {"inventory_levels/update"}
    if topic in inventory_topics:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.inventory_sync.handle_inventory_level_webhook",
            queue="short",
            timeout=120,
            topic=topic,
            payload=payload,
            connection=connection,
        )
