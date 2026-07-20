import base64
import hashlib
import hmac
import json

import frappe


@frappe.whitelist(allow_guest=True)
def handle_webhook():
    """
    HMAC-validated webhook endpoint. Shopify calls this for registered topics.
    Validates the signature then enqueues the appropriate handler.
    """
    request = frappe.request
    topic = request.headers.get("X-Shopify-Topic", "")
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")
    raw_body = request.data

    settings = frappe.get_single("Shopify Connector Settings")

    if not settings.is_enabled:
        frappe.response.status_code = 200
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
    # so both secrets must be accepted, not just one.
    candidate_secrets = [
        settings.get_password("sh_client_secret", raise_exception=False),
        settings.get_password("sh_webhook_secret", raise_exception=False),
    ]
    candidate_secrets = [s for s in candidate_secrets if s]
    if not candidate_secrets:
        frappe.log_error(
            title="Shopify webhook rejected: no secret configured")
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
            message=f"topic={topic!r}",
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

    _dispatch(topic, payload)

    frappe.response.status_code = 200
    return {"ok": True}


def _dispatch(topic, payload):
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
        )
