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
    Import products from Shopify. First run (nothing imported yet) wipes
    first as a safety net, then imports everything. Every run after that
    is a real create/update/skip sync -- no wipe -- see
    run_full_product_import's docstring for why.
    """
    return _enqueue_sync(
        "products",
        "alaiy_os_connector_shopify.shopify.product_import.run_full_product_import",
        # Was 1800s (30min) -- provably not enough anymore: each item now
        # also downloads an image, sets tags/SEO/cost/weight, and (for
        # Category) makes an extra taxonomy-search API call, confirmed live
        # to blow the old ceiling partway through a ~3000-item catalog.
        timeout=14400,  # 4 hours
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


@frappe.whitelist()
def get_location_map():
    """
    Every synced Shopify Location plus its current warehouse mapping (if
    any), for the dashboard's Location Map dialog -- lets a merchant map
    each Shopify location to any Alaiy OS warehouse by hand (independent
    names, no auto-create) without opening the raw child table on Settings.
    """
    locations = frappe.get_all(
        "Shopify Location",
        fields=["name", "location_name", "is_active"],
        order_by="location_name asc",
    )
    settings = frappe.get_single("Shopify Connector Settings")
    mapped = {row.shopify_location: row.warehouse for row in settings.sh_location_map}
    for loc in locations:
        loc["warehouse"] = mapped.get(loc["name"])
    return locations


@frappe.whitelist()
def save_location_map(mappings):
    """
    Replace the warehouse<->location map from the dashboard dialog.
    mappings: JSON list of {"shopify_location": ..., "warehouse": ...}.
    A row with no warehouse chosen is simply dropped (unmapped), not saved
    as an empty row.
    """
    import json
    if isinstance(mappings, str):
        mappings = json.loads(mappings)
    settings = frappe.get_single("Shopify Connector Settings")
    settings.set("sh_location_map", [])
    for m in mappings:
        if m.get("warehouse"):
            settings.append("sh_location_map", {
                "shopify_location": m["shopify_location"],
                "warehouse": m["warehouse"],
            })
    settings.flags.ignore_permissions = True
    settings.save()
    frappe.db.commit()
    return "ok"
