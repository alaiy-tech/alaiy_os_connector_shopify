app_name = "alaiy_os_connector_shopify"
app_title = "Alaiy OS Connector Shopify"
app_publisher = "Alaiy OS"
app_description = "Shopify sales channel connector for AlaiyOS"
app_email = "dev@alaiy.com"
app_license = "MIT"

required_apps = ["alaiy_os", "erpnext"]

after_migrate = [
    "alaiy_os_connector_shopify.setup.install.sync_connector_registry"
]

before_request = [
    "alaiy_os_connector_shopify.shopify.order_push.snapshot_before_update_child_qty_rate"
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
            "alaiy_os_connector_shopify.shopify.sync_jobs.check_and_enqueue"
        ]
    },
    "hourly": [
        "alaiy_os_connector_shopify.shopify.product_sync.push_changed_items_only"
    ],
    "daily": [
        "alaiy_os_connector_shopify.shopify.product_sync.fetch_shopify_taxonomy",
        "alaiy_os_connector_shopify.shopify.product_sync.sync_shopify_tags",
        "alaiy_os_connector_shopify.shopify.product_sync.sync_shopify_collections",
        "alaiy_os_connector_shopify.shopify.inventory_sync.sync_shopify_locations",
    ]
}

doc_events = {
    "Item": {
        # Item saves NO LONGER push to Shopify -- the Shopify Product Listing
        # is the push trigger and enable gate now (see product.listing_hooks).
        # Only tags/collections/UOM validation (Item-level concepts) stay here.
        "validate": [
            "alaiy_os_connector_shopify.shopify.product_sync.validate_item_uoms",
            "alaiy_os_connector_shopify.shopify.product_sync.copy_template_tags_to_variant",
            "alaiy_os_connector_shopify.shopify.product_sync.copy_template_collections_to_variant",
        ],
        # Data-upkeep only (never a direct push): keep a desk-added/deleted
        # variant in sync with its template's Listing, which then pushes.
        "after_insert": "alaiy_os_connector_shopify.shopify.product.listing_hooks.sync_new_variant_to_listing",
        "on_trash": "alaiy_os_connector_shopify.shopify.product.listing_hooks.remove_variant_from_listing",
    },
    "Shopify Product Listing": {
        "on_update": "alaiy_os_connector_shopify.shopify.product.listing_hooks.on_listing_update",
        "on_trash": "alaiy_os_connector_shopify.shopify.product.listing_hooks.on_listing_trash",
    },
    "Shopify Collection": {
        "on_update": "alaiy_os_connector_shopify.shopify.product_sync.on_shopify_collection_update",
        "on_trash": "alaiy_os_connector_shopify.shopify.product_sync.on_shopify_collection_trash",
    },
    "Sales Order": {
        "validate": "alaiy_os_connector_shopify.shopify.order_push.on_sales_order_validate",
        "on_submit": "alaiy_os_connector_shopify.shopify.order_push.on_sales_order_submit",
        "on_update": "alaiy_os_connector_shopify.shopify.order_push.on_sales_order_update",
        # Editing line items on an ALREADY-submitted Sales Order (Alaiy OS's
        # "Update Items" flow) fires on_update_after_submit, not on_update --
        # without this, item removal on a submitted/paid order silently
        # never reached our handler at all (confirmed live: zero Error Log
        # entries because the code never even ran).
        "on_update_after_submit": "alaiy_os_connector_shopify.shopify.order_push.on_sales_order_update",
        "on_cancel": "alaiy_os_connector_shopify.shopify.order_push.on_sales_order_cancel",
    },
    "Sales Invoice": {
        "on_submit": "alaiy_os_connector_shopify.shopify.order_sync.on_sales_invoice_submit",
    },
}

doctype_list_js = {
    "Sales Order": "public/js/sales_order_list.js",
}

doctype_js = {
    "Item": "public/js/item.js",
    "Shopify Product Listing": "public/js/shopify_product_listing.js",
}
