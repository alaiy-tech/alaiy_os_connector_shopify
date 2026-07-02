import frappe
from frappe.utils import flt, now_datetime


def run_inventory_push(trigger="manual"):
    """
    Push current ERPNext bin quantities to Shopify inventory levels
    for all items that have a sh_shopify_variant_id set.
    """
    log_name = _open_log("inventory", trigger)
    try:
        from alaiy_os_shopify_connector.shopify.client import ShopifyClient
        client = ShopifyClient()
        settings = frappe.get_single("Shopify Connector Settings")
        warehouse = settings.sh_default_warehouse

        if not warehouse:
            _close_log(log_name, "failed", error="No default warehouse configured")
            return

        location_id = _get_primary_location_id(client)
        if not location_id:
            _close_log(log_name, "failed", error="No Shopify location found")
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
                    continue

                client.post("inventory_levels/set.json", {
                    "location_id": location_id,
                    "inventory_item_id": inventory_item_id,
                    "available": int(qty),
                })
                updated += 1
            except Exception:
                failed += 1
                frappe.log_error(
                    title=f"Shopify inventory push failed for {item.name}",
                    message=frappe.get_traceback(),
                )

        _close_log(log_name, "success", processed=processed, created=updated, failed=failed)
    except Exception:
        _close_log(log_name, "failed", error=frappe.get_traceback())
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


def _open_log(sync_type, trigger):
    log = frappe.new_doc("Shopify Sync Log")
    log.sync_type = sync_type
    log.trigger = trigger
    log.status = "running"
    log.started_at = now_datetime()
    log.insert(ignore_permissions=True)
    frappe.db.commit()
    return log.name


def _close_log(log_name, status, processed=0, created=0, failed=0, error=""):
    frappe.db.set_value("Shopify Sync Log", log_name, {
        "status": status,
        "finished_at": now_datetime(),
        "items_processed": processed,
        "items_created": created,
        "items_failed": failed,
        "error_message": (error or "")[:500],
    })
    frappe.db.commit()
