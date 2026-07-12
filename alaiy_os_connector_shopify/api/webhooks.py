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

    # Fail CLOSED: this endpoint is allow_guest -- an unset secret must
    # reject every request, not silently accept everything unverified.
    webhook_secret = settings.get_password(
        "sh_webhook_secret", raise_exception=False)
    if not webhook_secret:
        frappe.log_error(
            title="Shopify webhook rejected: no secret configured")
        frappe.response.status_code = 401
        return {"ok": False, "reason": "webhook secret not configured"}

    computed = hmac.new(
        webhook_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).digest()
    expected = base64.b64encode(computed).decode("utf-8")
    if not hmac_header or not hmac.compare_digest(expected, hmac_header):
        frappe.response.status_code = 401
        return {"ok": False, "reason": "HMAC validation failed"}

    try:
        payload = json.loads(raw_body)
    except Exception:
        frappe.response.status_code = 400
        return {"ok": False, "reason": "invalid JSON"}

    _dispatch(topic, payload)

    frappe.response.status_code = 200
    return {"ok": True}


def _dispatch(topic, payload):
    order_topics = {"orders/create", "orders/updated",
                    "orders/cancelled", "orders/fulfilled"}
    if topic in order_topics:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.order_sync.handle_order_webhook",
            queue="short",
            timeout=300,
            topic=topic,
            payload=payload,
        )
