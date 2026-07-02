import frappe


@frappe.whitelist()
def trigger_orders_sync():
    frappe.enqueue(
        "alaiy_os_shopify_connector.shopify.order_sync.run_orders_sync",
        queue="long",
        timeout=600,
        trigger="manual",
    )
    return {"queued": True}


@frappe.whitelist()
def trigger_inventory_push():
    frappe.enqueue(
        "alaiy_os_shopify_connector.shopify.inventory_sync.run_inventory_push",
        queue="long",
        timeout=600,
        trigger="manual",
    )
    return {"queued": True}


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
        limit=3,
    )
