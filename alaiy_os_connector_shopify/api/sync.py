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
def get_sync_status(sync_type=None):
    filters = {}
    if sync_type:
        # "categories" maps to "orders", "items" maps to "inventory" in the UI labels
        type_map = {"categories": "orders", "items": "inventory"}
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
