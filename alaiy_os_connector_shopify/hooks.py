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

# Extra rows under this connector's own top-level sidebar section (Dashboard
# is always added automatically by alaiy_os).
alaiy_os_sidebar_connector_items = [
    {
        "connector_id": "shopify",
        "link_type": "DocType",
        "link_to": "Shopify Product Listing",
        "label": "Listings",
        "icon": "list",
    },
    {
        "connector_id": "shopify",
        "link_type": "DocType",
        "link_to": "Shopify Category",
        "label": "Categories",
        "icon": "layers",
    },
    {
        "connector_id": "shopify",
        "link_type": "DocType",
        "link_to": "Shopify Collection",
        "label": "Collections",
        "icon": "folder",
    },
    {
        "connector_id": "shopify",
        "link_type": "DocType",
        "link_to": "Shopify Location",
        "label": "Locations",
        "icon": "map-pin",
    },
    {
        "connector_id": "shopify",
        "link_type": "DocType",
        "link_to": "Shopify Tag",
        "label": "Tags",
        "icon": "tag",
    },
]

scheduler_events = {
    "cron": {
        "* * * * *": [
            "alaiy_os_connector_shopify.shopify.sync_jobs.check_and_enqueue"
        ]
    },
    "hourly": [
        "alaiy_os_connector_shopify.shopify.product_sync.push_changed_items_only",
        # PULL leg: drain queued inventory_levels/update quantities into audited
        # Stock Reconciliations. The webhook only queues them -- it must never
        # write Bin directly (see inventory_sync.apply_pulled_stock). Inbound
        # only; the outbound push is run_inventory_push, scheduled separately
        # via sync_jobs and gated by its own interval setting.
        "alaiy_os_connector_shopify.shopify.inventory_sync.run_inventory_pull",
    ],
    "daily": [
        "alaiy_os_connector_shopify.shopify.product_sync.sync_shopify_tags",
        "alaiy_os_connector_shopify.shopify.product_sync.sync_shopify_collections",
        "alaiy_os_connector_shopify.shopify.inventory_sync.sync_shopify_locations",
        # Full inventory sweep, the backstop under the webhook. A dropped
        # webhook (or one that arrived while the connector was disabled)
        # otherwise leaves local stock silently wrong forever, since nothing
        # else ever re-asks Shopify. Daily, not hourly: the webhook is the
        # fast path, this only catches what it missed.
        # Enqueued rather than run inline: a scheduled_events entry executes in
        # the scheduler's own worker on a 300s death penalty, and a full
        # catalogue sweep cannot finish in that. Confirmed live -- every daily
        # run died with JobTimeoutException having written nothing, so the one
        # backstop under the webhook never actually ran.
        "alaiy_os_connector_shopify.shopify.inventory_sync.enqueue_reconcile_inventory",
    ],
    # Shopify's Standard Product Taxonomy is a fixed, versioned reference
    # tree Shopify itself only revises a couple of times a year -- confirmed
    # live, a daily run re-walked the entire ~14,600-node tree from scratch
    # every single day (no change-detection short-circuit exists in
    # fetch_shopify_taxonomy) for a tree that was already fully synced.
    # Weekly is still far more often than the tree actually changes.
    "weekly": [
        "alaiy_os_connector_shopify.shopify.product_sync.scheduled_fetch_shopify_taxonomy",
    ],
}

doc_events = {
    "Item": {
        # Item saves NO LONGER push to Shopify -- the Shopify Product Listing
        # is the push trigger and enable gate now (see product.listing_hooks).
        # Only tags/collections/UOM validation (Item-level concepts) stay here.
        # UOM dedupe has to run BEFORE the doctype's own validate(), not with
        # the other hooks after it. Frappe runs Item.validate() first, so
        # ERPNext's validate_conversion_factor threw "Unit of Measure ...
        # entered more than once" and the heal registered on `validate` never
        # got a turn -- it only ever appeared to work because the import path
        # calls it explicitly before saving.
        #
        # Measured live: 1,860 of 3,517 items carry a duplicated UOM row, so
        # over half the catalogue could not be saved from Desk or the supplier
        # portal at all, including editing a title or description.
        "before_validate": [
            "alaiy_os_connector_shopify.shopify.product_sync.validate_item_uoms",
        ],
        "validate": [
            "alaiy_os_connector_shopify.shopify.product_sync.resolve_shopify_category_gid",
            "alaiy_os_connector_shopify.shopify.product_sync.copy_template_tags_to_variant",
            "alaiy_os_connector_shopify.shopify.product_sync.copy_template_collections_to_variant",
        ],
        # Data-upkeep only (never a direct push): keep a desk-added/deleted
        # variant in sync with its template's Listing, which then pushes.
        # ensure_listing_for_new_item gives every new TEMPLATE Item a
        # disabled Listing straight away (no-op for a variant).
        "after_insert": [
            "alaiy_os_connector_shopify.shopify.product_sync.ensure_listing_for_new_item",
            "alaiy_os_connector_shopify.shopify.product.listing_hooks.sync_new_variant_to_listing",
        ],
        "on_trash": "alaiy_os_connector_shopify.shopify.product.listing_hooks.remove_variant_from_listing",
    },
    # Enabling the connector has to backfill the Listings that
    # ensure_listing_for_new_item skipped while it was off.
    "Shopify Connector Settings": {
        "on_update": "alaiy_os_connector_shopify.shopify.product.item_hooks.backfill_listings_on_enable",
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
    "Delivery Note": {
        "on_submit": "alaiy_os_connector_shopify.shopify.order.fulfillment_push.on_delivery_note_submit",
        "on_update_after_submit": "alaiy_os_connector_shopify.shopify.order.fulfillment_push.on_delivery_note_update_after_submit",
        "on_cancel": "alaiy_os_connector_shopify.shopify.order.fulfillment_push.on_delivery_note_cancel",
    },
}

doctype_list_js = {
    "Sales Order": "public/js/sales_order_list.js",
    "Shopify Product Listing": "public/js/shopify_product_listing_list.js",
}

doctype_js = {
    "Item": "public/js/item.js",
    "Shopify Product Listing": "public/js/shopify_product_listing.js",
}
