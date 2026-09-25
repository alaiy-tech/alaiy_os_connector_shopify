import frappe

WEBHOOK_TOPICS = [
    # Order webhooks (inbound order sync)
    "orders/create",
    "orders/updated",
    "orders/cancelled",
    "orders/fulfilled",
    "orders/paid",
    "orders/delete",

    "orders/edited",

    # Refund webhooks (returns/credit notes, inbound) -- Shopify has no
    # separate "return" resource, a refund IS the return record.
    "refunds/create",

    # Fulfillment webhooks (tracking number create/update) -- carries
    # trackingInfo the order-level webhooks don't; orders/fulfilled only
    # fires once, so a tracking number added or changed afterwards (a real,
    # common flow) needs its own subscription to ever reach us.
    "fulfillments/create",
    "fulfillments/update",

    # Product webhooks (bidirectional product sync - inbound)
    "products/create",
    "products/update",
    "products/delete",

    # Collection webhooks (bidirectional collection sync - inbound)
    "collections/create",
    "collections/update",
    "collections/delete",

    # Inventory webhooks (inbound leg of the bidirectional inventory sync --
    # outbound is the existing run_inventory_push scheduled job)
    "inventory_levels/update",
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
        uri
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


_RETRY_COOLDOWN_SECONDS = 60 * 60

# Which scope a topic needs, for topics whose scope isn't implied by the
# resource name alone (orders/products/collections webhooks all need the
# matching read_<resource> scope, checked generically below).
_TOPIC_SCOPE_OVERRIDES = {
    "inventory_levels/update": "read_inventory",
}


def _required_scope_for_topic(topic: str) -> str:
    resource = topic.split("/", 1)[0]
    return _TOPIC_SCOPE_OVERRIDES.get(topic, f"read_{resource}")


def _cooldown_cache_key(connection_name: str, topic: str) -> str:
    return f"shopify_webhook_register_failed::{connection_name}::{topic}"


def get_webhook_address():
    site_url = frappe.utils.get_url().rstrip("/")
    return f"{site_url}/api/method/alaiy_os_connector_shopify.api.webhooks.handle_webhook"


def ensure_webhooks_registered(connection=None):
    """
    Fill in any webhook topic that isn't currently registered for this
    site's address, without touching topics that already are.

    `connection` is the store to register with. Every bench points its topics
    at the one shared address; the receiver tells the deliveries apart by the
    shop domain Shopify sends with each of them.

    This is normally only ever called once, automatically, on the exact
    moment a Shopify Connection's Enable Shopify flips from unchecked to
    checked. If that single attempt fails for any reason
    (confirmed in production: the Shop URL field wasn't filled in yet at
    that instant, so ShopifyGraphQLClient's __init__ raised immediately),
    the failure is caught, logged to Error Log, and never retried --
    inbound sync then silently never works, with no visible symptom
    beyond "webhooks never fire," which is easy to mistake for an HMAC
    or timestamp bug instead of "nothing was ever registered." This is
    meant to be called periodically (see sync_jobs.py) as a cheap
    self-healing check: one read-only list query, then create calls only
    for whatever's actually missing.
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    client = ShopifyGraphQLClient(connection)
    address = get_webhook_address()

    existing_topics = set()
    variables = {"after": None}
    for page_nodes in client.execute_paginated(_LIST_QUERY, variables, ["webhookSubscriptions"]):
        for wh in page_nodes:
            if wh.get("uri") == address:
                existing_topics.add(wh.get("topic"))

    missing = [t for t in WEBHOOK_TOPICS if _topic_to_graphql_enum(t) not in existing_topics]
    if not missing:
        return []

    connection_name = client.connection.name
    missing_scopes = set(
        (getattr(client.connection, "sh_missing_scopes", None) or "").split(",")
    ) - {""}
    registered = []
    for topic in missing:
        # A topic whose scope is confirmed absent on Shopify's own
        # currentAppInstallation (sh_missing_scopes, refreshed every token
        # refresh -- see auth.store_granted_scopes) will fail identically
        # forever until someone edits the app's Admin API access config;
        # skip it outright rather than attempting, logging, and cooling
        # down a call that can't succeed. A store simply not granting
        # every REQUIRED_SCOPES entry is expected, not an error condition
        # -- every OTHER topic this store does have scope for still
        # registers normally.
        if _required_scope_for_topic(topic) in missing_scopes:
            continue

        # A topic that just failed for some other reason (transient API
        # issue, http-only site, etc) is failing for a structural reason a
        # minute's wait won't fix -- retry every minute forever, called
        # from a per-minute scheduler, floods Error Log with the same
        # traceback thousands of times a day and tells nobody anything
        # new. Skip silently until the cooldown lapses; a topic that
        # starts succeeding again clears its own cooldown key.
        cache_key = _cooldown_cache_key(connection_name, topic)
        if frappe.cache().get_value(cache_key):
            continue
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
                frappe.cache().delete_value(cache_key)
        except Exception:
            frappe.cache().set_value(cache_key, "1", expires_in_sec=_RETRY_COOLDOWN_SECONDS)
            frappe.log_error(
                title=f"Shopify: failed to re-register missing webhook {topic}",
                message=frappe.get_traceback(),
            )
    if registered:
        frappe.logger().info(f"Shopify: registered previously-missing webhooks: {registered}")
    return registered


def unregister_webhooks(connection=None):
    """Remove this store's webhooks pointing to this site's handle_webhook
    endpoint. Scoped to the one connection: on a bench with several, tearing
    down a store's subscriptions must not silence anybody else's."""
    try:
        from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
        client = ShopifyGraphQLClient(connection)
        address = get_webhook_address()
        variables = {"after": None}
        for page_nodes in client.execute_paginated(_LIST_QUERY, variables, ["webhookSubscriptions"]):
            for wh in page_nodes:
                if wh.get("uri") != address:
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
                    frappe.log_error(
                        title=f"Shopify: failed to delete webhook {wh.get('id')}",
                        message=frappe.get_traceback(),
                    )
    except Exception:
        frappe.log_error(
            title="Shopify: failed to unregister webhooks",
            message=frappe.get_traceback(),
        )
