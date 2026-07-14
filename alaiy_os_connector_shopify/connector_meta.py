"""
Single source of truth for this connector's registration metadata.
Consumed by setup/install.py → upserted into alaiy_os's OS Connector Registry.
"""

connector_meta = {
    "connector_id": "shopify",
    "connector_name": "Shopify",
    "connector_app": "alaiy_os_connector_shopify",
    "connector_type": "channel",
    "description": "Shopify storefront",
    "icon": "shopping-bag",
    "icon_url": "",
    "settings_doctype": "Shopify Connector Settings",
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
}
