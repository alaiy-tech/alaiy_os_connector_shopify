import frappe
from frappe.utils import flt, now_datetime

from alaiy_os_connector_shopify.shopify.sync_guard import (
    has_active_sync, load_or_create_log,
    append_log as _append_log, close_log as _close_log,
)

_LOCATIONS_QUERY = """
query GetLocations($after: String) {
  locations(first: 250, after: $after) {
    nodes {
      id
      legacyResourceId
      name
      isActive
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""


@frappe.whitelist()
def sync_shopify_locations(trigger="manual", log_name=None):
    """
    Cache every Shopify location as a Shopify Location doc -- the list the
    warehouse-to-location map picks from. Logged (sync_type "locations").
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    log = load_or_create_log("locations", trigger, log_name)
    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    try:
        client = ShopifyGraphQLClient()
        has_next_page = True
        after_cursor = None
        total = 0

        while has_next_page:
            data = client.execute(_LOCATIONS_QUERY, {"after": after_cursor})
            loc_data = data.get("locations") or {}
            nodes = loc_data.get("nodes", [])

            for loc in nodes:
                legacy = str(loc.get("legacyResourceId") or "")
                if not legacy:
                    continue
                values = {
                    "location_name": loc.get("name") or f"Location {legacy}",
                    "is_active": 1 if loc.get("isActive") else 0,
                    "sh_location_id": legacy,
                    "sh_location_gid": loc.get("id") or "",
                    "last_synced": now_datetime(),
                }
                name = frappe.db.get_value("Shopify Location", {"sh_location_id": legacy}, "name")
                if name:
                    doc = frappe.get_doc("Shopify Location", name)
                    doc.update(values)
                else:
                    doc = frappe.get_doc(dict(doctype="Shopify Location", **values))
                doc.flags.ignore_permissions = True
                doc.save()
                total += 1

            page_info = loc_data.get("pageInfo") or {}
            has_next_page = page_info.get("hasNextPage", False)
            after_cursor = page_info.get("endCursor")

        frappe.db.commit()
        _close_log(log, "success", processed=total, created=total)
    except Exception:
        _close_log(log, "failed", error=frappe.get_traceback())
        raise
    return log.name

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
    without it, Alaiy OS has no warehouse to suggest on any document
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
    Push current Alaiy OS bin quantities to Shopify inventory levels
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
        from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
        client = ShopifyGraphQLClient()
        settings = frappe.get_single("Shopify Connector Settings")

        # Build the (warehouse, location_gid) pairs to push. If the merchant
        # mapped warehouses to Shopify locations, push each pair (multi-location);
        # otherwise fall back to Default Warehouse -> primary location.
        pairs = _resolve_location_pairs(settings, client)
        if not pairs:
            _close_log(log, "failed",
                       error="No warehouse/location to push. Set a Default Warehouse or map warehouses to Shopify locations.")
            return log.name

        last_success_time = frappe.db.get_value(
            "Shopify Sync Log",
            {"sync_type": "inventory", "status": "success"},
            "finished_at",
            order_by="finished_at desc",
        )

        totals = {"processed": 0, "updated": 0, "failed": 0, "unchanged": 0}
        for warehouse, location_id in pairs:
            _backfill_missing_default_warehouse(warehouse)
            _push_warehouse_to_location(
                client, warehouse, location_id, last_success_time, log, totals)

        _append_log(
            log,
            f"{totals['updated']} pushed, {totals['unchanged']} already in sync, "
            f"{totals['failed']} failed across {len(pairs)} location(s).")
        _close_log(log, "success", processed=totals["processed"],
                   created=totals["updated"], failed=totals["failed"])
    except Exception:
        _close_log(log, "failed", error=frappe.get_traceback())
        raise

    return log.name


def _resolve_location_pairs(settings, client):
    """
    List of (warehouse, location_gid) to sync. Mapped warehouses win
    (multi-location); else the single Default Warehouse -> primary location.
    """
    pairs = []
    for row in (settings.get("sh_location_map") or []):
        if not row.warehouse or not row.shopify_location:
            continue
        gid = frappe.db.get_value("Shopify Location", row.shopify_location, "sh_location_gid")
        if gid:
            pairs.append((row.warehouse, gid))
    if pairs:
        return pairs

    warehouse = settings.sh_default_warehouse
    location_id = _get_primary_location_id(client)
    if warehouse and location_id:
        return [(warehouse, location_id)]
    return []


def _push_warehouse_to_location(client, warehouse, location_id, last_success_time, log, totals):
    """Push one warehouse's bin quantities to one Shopify location. Same
    change-detection + no-op-skip optimization as before, scoped per warehouse."""
    from alaiy_os_connector_shopify.shopify.graphql_client import new_idempotency_key

    items = frappe.get_all(
        "Item",
        filters=[["sh_shopify_variant_id", "is", "set"]],
        fields=["name", "sh_shopify_variant_id"],
    )

    # Only push items whose stock changed since the last successful sync,
    # avoiding N+1 API calls on large, mostly-unchanged catalogs.
    if last_success_time:
        changed = frappe.db.get_all(
            "Bin", filters={"modified": [">", last_success_time], "warehouse": warehouse},
            pluck="item_code")
        new_items = frappe.db.get_all(
            "Item", filters={"creation": [">", last_success_time], "sh_shopify_variant_id": ["is", "set"]},
            pluck="name")
        codes = set(changed + new_items)
        items = [i for i in items if i.name in codes]
        _append_log(log, f"[{warehouse}] checking {len(items)} items changed since last sync")
    else:
        import datetime
        one_day_ago = now_datetime() - datetime.timedelta(days=1)
        changed = frappe.db.get_all(
            "Bin", filters={"modified": [">", one_day_ago], "warehouse": warehouse},
            pluck="item_code")
        items = [i for i in items if i.name in changed]
        _append_log(log, f"[{warehouse}] first run, checking {len(items)} items changed in last 24h")

    for item in items:
        totals["processed"] += 1
        try:
            # A missing Bin means "no stock data recorded for this item/
            # warehouse", NOT "confirmed zero" -- treating it as 0 pushed a
            # false zero to Shopify the one time Alaiy OS's own Bin table was
            # emptied (e.g. by an unrelated cleanup), overwriting real Shopify
            # stock with a number Alaiy OS never actually knew. Skip instead
            # of guessing.
            bin_qty = frappe.db.get_value(
                "Bin", {"item_code": item.name, "warehouse": warehouse}, "actual_qty")
            if bin_qty is None:
                totals["failed"] += 1
                _append_log(
                    log, f"SKIPPED item={item.name}: no Bin record for warehouse {warehouse} -- not pushing an assumed zero")
                continue
            qty = flt(bin_qty)

            inventory_item_id, current_qty = _get_inventory_item_state(
                client, item.sh_shopify_variant_id, location_id)
            if not inventory_item_id:
                totals["failed"] += 1
                _append_log(
                    log, f"ERROR item={item.name}: no Shopify inventory_item_id for variant {item.sh_shopify_variant_id}")
                continue

            # Already in sync -- setting to the same value is a no-op; skip the write.
            if int(qty) == int(current_qty):
                totals["unchanged"] += 1
                continue

            data = client.execute(_INVENTORY_SET_MUTATION, {
                "input": {
                    "name": "available",
                    "reason": "correction",
                    "quantities": [{
                        "inventoryItemId": inventory_item_id,
                        "locationId": location_id,
                        "quantity": int(qty),
                        # changeFromQuantity is mandatory as of API 2026-04 --
                        # a genuine race with a concurrent change fails loudly
                        # here rather than silently overwriting it.
                        "changeFromQuantity": int(current_qty),
                    }],
                },
                "idempotencyKey": new_idempotency_key(),
            })
            errors = (data.get("inventorySetQuantities") or {}).get("userErrors") or []
            if errors:
                raise RuntimeError(f"Shopify userErrors: {errors}")
            totals["updated"] += 1
            _append_log(
                log,
                f"PUSHED item={item.name} variant={item.sh_shopify_variant_id} @ {warehouse}: "
                f"{int(current_qty)} -> {int(qty)}")
        except Exception as exc:
            totals["failed"] += 1
            _append_log(log, f"ERROR item={item.name} @ {warehouse}: {exc}")
            frappe.log_error(
                title=f"Shopify inventory push failed for {item.name}",
                message=frappe.get_traceback(),
            )


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


