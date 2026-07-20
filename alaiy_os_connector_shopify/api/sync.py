import frappe

from alaiy_os_connector_shopify.shopify.sync_guard import load_or_create_log


def _enqueue_sync(sync_type, method, timeout=600, **kwargs):
    # Log row created here (not inside the job) so it's visible as "queued"
    # immediately, even if the shared long queue is busy and the job itself
    # doesn't start running for a while.
    log = load_or_create_log(sync_type, "manual")
    frappe.enqueue(
        method,
        queue="long",
        timeout=timeout,
        trigger="manual",
        log_name=log.name,
        **kwargs,
    )
    return {"queued": True, "log_name": log.name}


@frappe.whitelist()
def trigger_orders_sync():
    return _enqueue_sync(
        "orders", "alaiy_os_connector_shopify.shopify.order_sync.run_orders_sync")


@frappe.whitelist()
def import_existing_orders(date_from=None, date_to=None):
    from alaiy_os_connector_shopify.shopify.order_sync import import_existing_orders as _import
    return _import(date_from=date_from, date_to=date_to)


@frappe.whitelist()
def trigger_inventory_push():
    return _enqueue_sync(
        "inventory", "alaiy_os_connector_shopify.shopify.inventory_sync.run_inventory_push")


@frappe.whitelist()
def trigger_product_import():
    """
    One-time import of all products from Shopify, wiping existing unlinked items.
    Enqueued as background job.
    """
    return _enqueue_sync(
        "products",
        "alaiy_os_connector_shopify.shopify.product_import.run_full_product_import",
        # Was 1800s (30min) -- provably not enough anymore: each item now
        # also downloads an image, sets tags/SEO/cost/weight, and (for
        # Category) makes an extra taxonomy-search API call, confirmed live
        # to blow the old ceiling partway through a ~3000-item catalog.
        timeout=14400,  # 4 hours
        wipe_existing=True,
    )


@frappe.whitelist()
def trigger_product_export():
    """
    Bulk push every local (not-yet-linked) product to Shopify in one go --
    for manually-created Alaiy OS Items that predate any Shopify connection.
    Enqueued as background job.
    """
    return _enqueue_sync(
        "product_export",
        "alaiy_os_connector_shopify.shopify.product_sync.run_bulk_export_to_shopify",
        timeout=1800,
    )


@frappe.whitelist()
def get_sync_status(sync_type=None):
    filters = {}
    if sync_type:
        # "categories" maps to "orders", "items" maps to "inventory", "products" maps to "products"
        type_map = {"categories": "orders", "items": "inventory", "products": "products"}
        filters["sync_type"] = type_map.get(sync_type, sync_type)
    return frappe.get_all(
        "Shopify Sync Log",
        filters=filters,
        fields=[
            "name", "sync_type", "trigger", "status",
            "started_at", "finished_at",
            "items_processed", "items_created", "items_failed",
            "pages_total", "pages_done",
            "error_message",
        ],
        order_by="started_at desc",
        limit=5,
    )


@frappe.whitelist()
def refresh_shopify_taxonomy():
    """
    Manually trigger a refresh of Shopify's Standard Product Taxonomy tree.
    Fetches the full taxonomy from Shopify GraphQL and populates/updates
    the Shopify Category doctype (tree structure).
    """
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product_sync.fetch_shopify_taxonomy",
        queue="long",
        timeout=300,
    )
    return {"queued": True}


@frappe.whitelist()
def refresh_shopify_tags():
    """
    Manually trigger a refresh of the cached Shopify Tag list -- every
    tag ever used across the store's products, paginated in from
    productTags. Populates the Shopify Tag doctype the tags multi-select
    field picks from.
    """
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product_sync.sync_shopify_tags",
        queue="long",
        timeout=300,
    )
    return {"queued": True}


@frappe.whitelist()
def refresh_shopify_collections():
    """
    Manually trigger a refresh of the cached Shopify Collection list -- every
    collection on the store, paginated in. Populates the Shopify Collection
    doctype the collections multi-select field picks from. Logged (sync_type
    "collections") so it shows in the dashboard like every other sync.
    """
    return _enqueue_sync(
        "collections",
        "alaiy_os_connector_shopify.shopify.product_sync.sync_shopify_collections",
    )


@frappe.whitelist()
def refresh_shopify_locations():
    """
    Manually refresh the cached Shopify Location list -- what the
    warehouse-to-location map picks from for multi-location inventory sync.
    """
    return _enqueue_sync(
        "locations",
        "alaiy_os_connector_shopify.shopify.inventory_sync.sync_shopify_locations",
    )
