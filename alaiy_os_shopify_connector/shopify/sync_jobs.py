import frappe
from frappe.utils import now_datetime, add_to_date

_INTERVAL_MINUTES = {
    "5 min": 5,
    "15 min": 15,
    "30 min": 30,
    "60 min": 60,
}


def check_and_enqueue():
    """
    Called every minute by the Frappe scheduler.
    Checks whether the inventory push is due and enqueues it if so.
    """
    if not frappe.db.exists("DocType", "Shopify Sync Log"):
        return

    settings = frappe.get_single("Shopify Connector Settings")
    if not settings.is_enabled:
        return

    _maybe_enqueue_inventory(settings.sh_inventory_sync_interval or "Disabled")


def _maybe_enqueue_inventory(interval_setting):
    interval_minutes = _INTERVAL_MINUTES.get(interval_setting)
    if not interval_minutes:
        return

    now = now_datetime()

    running = frappe.db.get_value(
        "Shopify Sync Log",
        {"sync_type": "inventory", "status": "running"},
        "started_at",
        order_by="started_at desc",
    )
    if running:
        elapsed = (now - running).total_seconds()
        if elapsed < 1800:
            return

    last_success = frappe.db.get_value(
        "Shopify Sync Log",
        {"sync_type": "inventory", "status": "success"},
        "started_at",
        order_by="started_at desc",
    )
    if last_success:
        due_at = add_to_date(last_success, minutes=interval_minutes)
        if now < due_at:
            return

    frappe.enqueue(
        "alaiy_os_shopify_connector.shopify.inventory_sync.run_inventory_push",
        queue="long",
        timeout=600,
        trigger="scheduled",
    )
