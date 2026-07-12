import frappe

WEBHOOK_TOPICS = [
    "orders/create",
    "orders/updated",
    "orders/cancelled",
    "orders/fulfilled",
]

_CREATE_MUTATION = """
mutation CreateWebhook($topic: WebhookSubscriptionTopic!, $input: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $input) {
    webhookSubscription {
      id
    }
    userErrors {
      field
      message
    }
  }
}
"""

_LIST_QUERY = """
query ListWebhooks($after: String) {
  webhookSubscriptions(first: 50, after: $after) {
    edges {
      node {
        id
        callbackUrl
        topic
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

_DELETE_MUTATION = """
mutation DeleteWebhook($id: ID!) {
  webhookSubscriptionDelete(id: $id) {
    deletedWebhookSubscriptionId
    userErrors {
      field
      message
    }
  }
}
"""


def _topic_to_graphql_enum(topic: str) -> str:
    return topic.upper().replace("/", "_")


def get_webhook_address():
    site_url = frappe.utils.get_url().rstrip("/")
    return f"{site_url}/api/method/alaiy_os_connector_shopify.api.webhooks.handle_webhook"


def register_webhooks():
    """Register all required webhooks on Shopify. Returns list of registered records."""
    address = get_webhook_address()
    registered = []
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    client = ShopifyGraphQLClient()
    for topic in WEBHOOK_TOPICS:
        try:
            data = client.execute(_CREATE_MUTATION, {
                "topic": _topic_to_graphql_enum(topic),
                "input": {"uri": address, "format": "JSON"},
            })
            result = data.get("webhookSubscriptionCreate") or {}
            errors = result.get("userErrors") or []
            if errors:
                raise RuntimeError(f"userErrors: {errors}")
            wh = result.get("webhookSubscription") or {}
            if wh.get("id"):
                registered.append({"topic": topic, "webhook_id": wh["id"]})
        except Exception:
            frappe.log_error(
                title=f"Shopify: failed to register webhook {topic}",
                message=frappe.get_traceback(),
            )
    return registered


def unregister_webhooks():
    """Remove all webhooks pointing to this site's handle_webhook endpoint."""
    try:
        from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
        client = ShopifyGraphQLClient()
        address = get_webhook_address()
        variables = {"after": None}
        for page_nodes in client.execute_paginated(_LIST_QUERY, variables, ["webhookSubscriptions"]):
            for wh in page_nodes:
                if wh.get("callbackUrl") != address:
                    continue
                try:
                    data = client.execute(_DELETE_MUTATION, {"id": wh["id"]})
                    errors = (data.get("webhookSubscriptionDelete")
                              or {}).get("userErrors") or []
                    if errors:
                        frappe.log_error(
                            title="Shopify: webhook delete userErrors",
                            message=str(errors),
                        )
                except Exception:
                    pass
    except Exception:
        frappe.log_error(
            title="Shopify: failed to unregister webhooks",
            message=frappe.get_traceback(),
        )
