import frappe
from frappe.utils import flt, now_datetime

from alaiy_os_connector_shopify.shopify.sync_guard import (
    has_active_sync, load_or_create_log,
    append_log as _append_log, close_log as _close_log,
)

_LOCATIONS_QUERY = """
{
  locations(first: 50) {
    nodes {
      id
      isActive
    }
  }
}
"""

_VARIANT_INVENTORY_QUERY = """
query VariantInventoryItem($id: ID!, $locationId: ID!) {
  productVariant(id: $id) {
    inventoryItem {
      id
      inventoryLevel(locationId: $locationId) {
        quantities(names: ["available"]) {
          quantity
        }
      }
    }
  }
}
"""


_INVENTORY_SET_MUTATION = """
mutation SetInventory($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
  inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
    userErrors {
      field
      message
    }
  }
}
"""


def _backfill_missing_default_warehouse(warehouse):
    """
    One-time-per-item heal for stock items imported before Item Defaults
    were set at import time (see product_import._default_warehouse_row) --
    without it, ERPNext has no warehouse to suggest on any document
    created directly in the desk UI, forcing it to be typed in by hand
    every time. Runs on every scheduled inventory push (already the one
    place that iterates every Shopify-linked stock item); capped per run
    so a large backlog heals over several runs instead of one slow one.
    """
    company = frappe.db.get_value("Warehouse", warehouse, "company")
    if not company:
        return
    missing = frappe.db.sql("""
        SELECT i.name FROM `tabItem` i
        WHERE i.sh_shopify_variant_id IS NOT NULL AND i.sh_shopify_variant_id != ''
          AND i.is_stock_item = 1
          AND NOT EXISTS (
            SELECT 1 FROM `tabItem Default` d
            WHERE d.parent = i.name AND d.company = %s AND d.default_warehouse = %s
          )
        LIMIT 200
    """, (company, warehouse), as_dict=True)
    for row in missing:
        try:
            item = frappe.get_doc("Item", row.name)
            item.append("item_defaults", {"company": company, "default_warehouse": warehouse})
            item.flags.ignore_permissions = True
            item.save()
        except Exception:
            frappe.log_error(
                title=f"Shopify: failed to backfill default warehouse for {row.name}",
                message=frappe.get_traceback(),
            )
    if missing:
        frappe.db.commit()


def run_inventory_push(trigger="manual", log_name=None):
    """
    Push current ERPNext bin quantities to Shopify inventory levels
    for all items that have a sh_shopify_variant_id set.
    """
    log = load_or_create_log("inventory", trigger, log_name)
    if has_active_sync("inventory", exclude_name=log.name):
        _close_log(log, "skipped",
                   error="Skipped: another inventory sync is already running.")
        return log.name

    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    try:
        from alaiy_os_connector_shopify.shopify.graphql_client import (
            ShopifyGraphQLClient, new_idempotency_key,
        )
        client = ShopifyGraphQLClient()
        settings = frappe.get_single("Shopify Connector Settings")
        warehouse = settings.sh_default_warehouse

        if not warehouse:
            _close_log(log, "failed", error="No default warehouse configured")
            return log.name

        location_id = _get_primary_location_id(client)
        if not location_id:
            _close_log(log, "failed", error="No Shopify location found")
            return log.name

        _backfill_missing_default_warehouse(warehouse)

        items = frappe.get_all(
            "Item",
            # NOT IN with a NULL in the list is a standard SQL trap: it
            # matches nothing, ever ("x <> NULL" is unknown, not true) --
            # "is set" is the safe way to say "non-empty".
            filters=[["sh_shopify_variant_id", "is", "set"]],
            fields=["name", "sh_shopify_variant_id"],
        )

        # Optimization: Only push items whose stock has changed since the last successful sync.
        # This avoids making N+1 HTTP API requests (which takes 10+ minutes and causes timeouts
        # on large catalogs) when most items haven't changed.
        last_success_time = frappe.db.get_value(
            "Shopify Sync Log",
            {"sync_type": "inventory", "status": "success"},
            "finished_at",
            order_by="finished_at desc"
        )
        
        if last_success_time:
            # Find item codes of bins modified since the last success run
            changed_items = frappe.db.get_all(
                "Bin",
                filters={
                    "modified": [">", last_success_time],
                    "warehouse": warehouse
                },
                pluck="item_code"
            )
            # Also get items created since last_success_time to be safe
            new_items = frappe.db.get_all(
                "Item",
                filters={
                    "creation": [">", last_success_time],
                    "sh_shopify_variant_id": ["is", "set"]
                },
                pluck="name"
            )
            changed_item_codes = set(changed_items + new_items)
            items = [i for i in items if i.name in changed_item_codes]
            _append_log(log, f"Optimization: checking {len(items)} items modified/created since {last_success_time}")
        else:
            # First sync run -- default to only checking bins modified in the last 24 hours
            # to prevent timeout on full catalogs that are already in sync.
            import datetime
            one_day_ago = now_datetime() - datetime.timedelta(days=1)
            changed_items = frappe.db.get_all(
                "Bin",
                filters={
                    "modified": [">", one_day_ago],
                    "warehouse": warehouse
                },
                pluck="item_code"
            )
            items = [i for i in items if i.name in changed_items]
            _append_log(log, f"Optimization: first run, checking {len(items)} items modified/created in last 24h")

        processed = updated = failed = unchanged = 0
        for item in items:
            processed += 1
            try:
                qty = flt(frappe.db.get_value(
                    "Bin",
                    {"item_code": item.name, "warehouse": warehouse},
                    "actual_qty",
                ) or 0)

                inventory_item_id, current_qty = _get_inventory_item_state(
                    client, item.sh_shopify_variant_id, location_id)
                if not inventory_item_id:
                    failed += 1
                    _append_log(
                        log, f"ERROR item={item.name}: no Shopify inventory_item_id for variant {item.sh_shopify_variant_id}")
                    continue

                # Already in sync -- setting to the same value is a Shopify
                # no-op, so skip the write round-trip entirely. On steady-state
                # runs this is most items, and halves the API calls/run.
                if int(qty) == int(current_qty):
                    unchanged += 1
                    continue

                data = client.execute(_INVENTORY_SET_MUTATION, {
                    "input": {
                        "name": "available",
                        "reason": "correction",
                        "quantities": [{
                            "inventoryItemId": inventory_item_id,
                            "locationId": location_id,
                            "quantity": int(qty),
                            # changeFromQuantity is mandatory as of API
                            # 2026-04 -- Shopify rejects a mismatch, so a
                            # genuine race with a concurrent change fails
                            # loudly here rather than silently overwriting
                            # it; the next scheduled run picks it up again.
                            "changeFromQuantity": int(current_qty),
                        }],
                    },
                    "idempotencyKey": new_idempotency_key(),
                })
                errors = (data.get("inventorySetQuantities")
                          or {}).get("userErrors") or []
                if errors:
                    raise RuntimeError(f"Shopify userErrors: {errors}")
                updated += 1
            except Exception as exc:
                failed += 1
                _append_log(log, f"ERROR item={item.name}: {exc}")
                frappe.log_error(
                    title=f"Shopify inventory push failed for {item.name}",
                    message=frappe.get_traceback(),
                )

        _append_log(
            log, f"{updated} pushed, {unchanged} already in sync, {failed} failed.")
        _close_log(log, "success", processed=processed,
                   created=updated, failed=failed)
    except Exception:
        _close_log(log, "failed", error=frappe.get_traceback())
        raise

    return log.name


def _get_primary_location_id(client):
    """Same behavior as the old REST lookup: first location Shopify reports
    as active, not necessarily the formal "primary" location."""
    data = client.execute(_LOCATIONS_QUERY)
    for loc in (data.get("locations") or {}).get("nodes", []):
        if loc.get("isActive"):
            return loc["id"]  # GID, used directly as locationId
    return None


def _get_inventory_item_state(client, variant_id, location_id):
    """Returns (inventory_item_id, current_available_quantity) -- the
    latter is required as changeFromQuantity on the set mutation below."""
    variant_gid = f"gid://shopify/ProductVariant/{variant_id}"
    data = client.execute(_VARIANT_INVENTORY_QUERY, {
        "id": variant_gid, "locationId": location_id,
    })
    variant = data.get("productVariant") or {}
    inventory_item = variant.get("inventoryItem") or {}
    inventory_item_id = inventory_item.get("id")
    if not inventory_item_id:
        return None, 0
    level = inventory_item.get("inventoryLevel") or {}
    quantities = level.get("quantities") or []
    current_qty = quantities[0].get("quantity") if quantities else 0
    return inventory_item_id, (current_qty or 0)


