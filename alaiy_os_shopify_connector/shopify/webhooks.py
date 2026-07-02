import frappe

WEBHOOK_TOPICS = [
    "orders/create",
    "orders/updated",
    "orders/cancelled",
    "orders/fulfilled",
]


def get_webhook_address():
    site_url = frappe.utils.get_url().rstrip("/")
    return f"{site_url}/api/method/alaiy_os_shopify_connector.api.webhooks.handle_webhook"


def register_webhooks(client):
    """Register all required webhooks on Shopify. Returns list of registered records."""
    address = get_webhook_address()
    registered = []
    for topic in WEBHOOK_TOPICS:
        try:
            resp = client.post("webhooks.json", {
                "webhook": {"topic": topic, "address": address, "format": "json"}
            })
            wh = resp.get("webhook", {})
            if wh.get("id"):
                registered.append({"topic": topic, "webhook_id": str(wh["id"])})
        except Exception:
            frappe.log_error(
                title=f"Shopify: failed to register webhook {topic}",
                message=frappe.get_traceback(),
            )
    return registered


def unregister_webhooks():
    """Remove all webhooks pointing to this site's handle_webhook endpoint."""
    try:
        from alaiy_os_shopify_connector.shopify.client import ShopifyClient
        client = ShopifyClient()
        resp = client.get("webhooks.json")
        address = get_webhook_address()
        for wh in resp.get("webhooks", []):
            if wh.get("address") == address:
                try:
                    client.delete(f"webhooks/{wh['id']}.json")
                except Exception:
                    pass
    except Exception:
        frappe.log_error(
            title="Shopify: failed to unregister webhooks",
            message=frappe.get_traceback(),
        )
