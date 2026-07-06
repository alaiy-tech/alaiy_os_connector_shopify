import frappe
from frappe.utils import flt, now_datetime

from alaiy_os_shopify_connector.shopify.sync_guard import has_active_sync, load_or_create_log


def run_inventory_push(trigger="manual", log_name=None):
    """
    Push current ERPNext bin quantities to Shopify inventory levels
    for all items that have a sh_shopify_variant_id set.
    """
    log = load_or_create_log("inventory", trigger, log_name)
    if has_active_sync("inventory", exclude_name=log.name):
        _close_log(log, "skipped", error="Skipped: another inventory sync is already running.")
        return log.name

    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    try:
        from alaiy_os_shopify_connector.shopify.client import ShopifyClient
        client = ShopifyClient()
        settings = frappe.get_single("Shopify Connector Settings")
        warehouse = settings.sh_default_warehouse

        if not warehouse:
            _close_log(log, "failed", error="No default warehouse configured")
            return

        location_id = _get_primary_location_id(client)
        if not location_id:
            _close_log(log, "failed", error="No Shopify location found")
            return

        items = frappe.get_all(
            "Item",
            filters={"sh_shopify_variant_id": ["not in", ["", None]]},
            fields=["name", "sh_shopify_variant_id"],
        )

        processed = updated = failed = 0
        for item in items:
            processed += 1
            try:
                qty = flt(frappe.db.get_value(
                    "Bin",
                    {"item_code": item.name, "warehouse": warehouse},
                    "actual_qty",
                ) or 0)

                inventory_item_id = _get_inventory_item_id(client, item.sh_shopify_variant_id)
                if not inventory_item_id:
                    failed += 1
                    _append_log(log, f"ERROR item={item.name}: no Shopify inventory_item_id for variant {item.sh_shopify_variant_id}")
                    continue

                client.post("inventory_levels/set.json", {
                    "location_id": location_id,
                    "inventory_item_id": inventory_item_id,
                    "available": int(qty),
                })
                updated += 1
            except Exception as exc:
                failed += 1
                _append_log(log, f"ERROR item={item.name}: {exc}")
                frappe.log_error(
                    title=f"Shopify inventory push failed for {item.name}",
                    message=frappe.get_traceback(),
                )

        _close_log(log, "success", processed=processed, created=updated, failed=failed)
    except Exception:
        _close_log(log, "failed", error=frappe.get_traceback())
        raise


def _get_primary_location_id(client):
    resp = client.get("locations.json", {"fields": "id,name,active"})
    for loc in resp.get("locations", []):
        if loc.get("active"):
            return loc["id"]
    return None


def _get_inventory_item_id(client, variant_id):
    resp = client.get(f"variants/{variant_id}.json", {"fields": "id,inventory_item_id"})
    return resp.get("variant", {}).get("inventory_item_id")


def _append_log(log, message: str):
    """Append a line to log.log_messages without saving."""
    existing = log.log_messages or ""
    log.log_messages = (existing + "\n" + message).strip()


def _close_log(log, status, processed=0, created=0, failed=0, error=""):
    log.status = status
    log.finished_at = now_datetime()
    log.items_processed = processed
    log.items_created = created
    log.items_failed = failed
    if error:
        log.error_message = (error or "")[:500]
    log.save(ignore_permissions=True)
    frappe.db.commit()
