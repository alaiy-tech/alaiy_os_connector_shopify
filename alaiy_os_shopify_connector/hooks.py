app_name = "alaiy_os_shopify_connector"
app_title = "Alaiy OS Shopify Connector"
app_publisher = "Alaiy OS"
app_description = "Shopify sales channel connector for AlaiyOS"
app_email = "dev@alaiy.com"
app_license = "MIT"

required_apps = ["alaiy_os_core", "erpnext"]

after_migrate = [
    "alaiy_os_shopify_connector.setup.install.sync_connector_registry"
]

alaiy_os_sidebar_log_items = [
    {
        "link_type": "DocType",
        "link_to": "Shopify Sync Log",
        "label": "Shopify Logs",
        "icon": "activity",
    }
]

scheduler_events = {
    "cron": {
        "* * * * *": [
            "alaiy_os_shopify_connector.shopify.sync_jobs.check_and_enqueue"
        ]
    }
}
