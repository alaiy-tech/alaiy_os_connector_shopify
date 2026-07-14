import frappe

from alaiy_os_connector_shopify.shopify.sync_guard import load_or_create_log


@frappe.whitelist()
def trigger_orders_sync():
    # Created here (not inside the job) so it's visible as "queued" in the
    # log immediately, even if the shared long queue is busy and the job
    # itself doesn't start running for a while.
    log = load_or_create_log("orders", "manual")
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_sync.run_orders_sync",
        queue="long",
        timeout=600,
        trigger="manual",
        log_name=log.name,
    )
    return {"queued": True, "log_name": log.name}


@frappe.whitelist()
def import_existing_orders():
    from alaiy_os_connector_shopify.shopify.order_sync import import_existing_orders as _import
    return _import()


@frappe.whitelist()
def trigger_inventory_push():
    log = load_or_create_log("inventory", "manual")
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.inventory_sync.run_inventory_push",
        queue="long",
        timeout=600,
        trigger="manual",
        log_name=log.name,
    )
    return {"queued": True, "log_name": log.name}


@frappe.whitelist()
def trigger_product_import():
    """
    One-time import of all products from Shopify, wiping existing unlinked items.
    Enqueued as background job.
    """
    log = frappe.new_doc("Shopify Sync Log")
    log.sync_type = "products"
    log.trigger = "manual"
    log.status = "queued"
    log.started_at = frappe.utils.now_datetime()
    log.insert(ignore_permissions=True)
    frappe.db.commit()

    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product_import.run_full_product_import",
        queue="long",
        timeout=1800,  # 30 minutes for large catalogs
        trigger="manual",
        log_name=log.name,
        wipe_existing=True,
    )
    return {"queued": True, "log_name": log.name}


@frappe.whitelist()
def trigger_product_export():
    """
    Bulk push every local (not-yet-linked) product to Shopify in one go --
    for manually-created ERPNext Items that predate any Shopify connection.
    Enqueued as background job.
    """
    log = frappe.new_doc("Shopify Sync Log")
    log.sync_type = "product_export"
    log.trigger = "manual"
    log.status = "queued"
    log.started_at = frappe.utils.now_datetime()
    log.insert(ignore_permissions=True)
    frappe.db.commit()

    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product_sync.run_bulk_export_to_shopify",
        queue="long",
        timeout=1800,
        trigger="manual",
        log_name=log.name,
    )
    return {"queued": True, "log_name": log.name}


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
