"""
Single source of truth for this connector's registration metadata.
Consumed by setup/install.py → upserted into alaiy_os's OS Connector Registry.
"""

# Columns of Shopify Sync Log, named the way the Connector Health page reads them.
# This log has no "updated" column; changed rows are counted in items_created.
_LOG_FIELDS = {
    "processed": "items_processed",
    "changed": "items_created",
    "failed": "items_failed",
    "error": "error_message",
}


def _health(key, label, direction, sync_type, interval_setting=None, expects_rows=True):
    entry = {
        "key": key,
        "label": label,
        "direction": direction,
        "log_doctype": "Shopify Sync Log",
        "log_filter": {"sync_type": sync_type},
        "fields": _LOG_FIELDS,
        "scheduled": bool(interval_setting),
        "expects_rows": expects_rows,
    }
    if interval_setting:
        entry["interval_setting"] = interval_setting
    return entry


connector_meta = {
    "connector_id": "shopify",
    "connector_name": "Shopify",
    "connector_app": "alaiy_os_connector_shopify",
    "connector_type": "channel",
    "description": "Shopify storefront",
    "icon": "shopping-bag",
    "icon_url": "/assets/alaiy_os_connector_shopify/images/shopify-icon.svg",
    "settings_doctype": "Shopify Connection",
    # The per-connector listing doctype a future AI listing agent writes to
    # for this marketplace. Consumed by OS Connector Registry (requires the
    # matching listing_doctype field on that doctype in alaiy_os).
    "listing_doctype": "Shopify Product Listing",
    "test_method": "alaiy_os_connector_shopify.api.test_connection.test_connection",
    "sync_categories_method": "alaiy_os_connector_shopify.api.sync.trigger_orders_sync",
    "sync_items_method": "alaiy_os_connector_shopify.api.sync.trigger_inventory_push",
    "sync_products_method": "alaiy_os_connector_shopify.api.sync.trigger_product_import",
    "sync_status_method": "alaiy_os_connector_shopify.api.sync.get_sync_status",
    "sync_categories_label": "Orders",
    "sync_items_label": "Inventory",
    "sync_products_label": "Products",
    "is_enabled": 0,
    "connection_status": "untested",
    "health": [
        _health("inventory_push", "Inventory push", "push", "inventory", "sh_inventory_sync_interval", expects_rows=False),
        _health("inventory_pull", "Inventory pull", "pull", "inventory_pull", "sh_inventory_pull_interval"),
        # Driven by webhooks and manual runs, so they can legitimately be idle.
        _health("orders", "Order pull", "pull", "orders", expects_rows=False),
        _health("products", "Product import", "pull", "products", expects_rows=False),
    ],
}
