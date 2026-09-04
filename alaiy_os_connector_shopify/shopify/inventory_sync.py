import frappe
from frappe.utils import flt, now_datetime

from alaiy_os_connector_shopify.shopify.sync_guard import (
    has_active_sync, load_or_create_log, is_cancel_requested,
    append_log as _append_log, close_log as _close_log,
)

from alaiy_os_connector_shopify import connections

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

# fulfillmentServices hangs off shop, not off Location, and each service names the
# one location it serves -- so the mapping has to be built service-first and then
# looked up per location. There is no cursor here: Shopify returns the shop's
# services as a plain list, not a connection.
_FULFILLMENT_SERVICES_QUERY = """
query GetFulfillmentServices {
  shop {
    fulfillmentServices {
      id
      serviceName
      handle
      type
      location {
        id
        legacyResourceId
      }
    }
  }
}
"""


def _fulfillment_services_by_location(client, log=None):
    """({location legacyResourceId: service dict}, available) for the shop's services.

    A location's identity does not say who ships from it: a third-party warehouse
    (type GATEWAY) has to be routed differently from one the merchant packs
    (MANUAL). Shopify exposes that only through shop.fulfillmentServices.

    Best-effort on purpose -- a store whose API user lacks the scope for this
    field, or an older API version, must not break location caching, which is
    what the warehouse map depends on.

    The second return value separates "asked and the shop has none" from "could
    not ask at all". The caller must not blank a location's stored service on the
    second: a transient scope or network failure would otherwise erase routing
    data that is still correct.
    """
    try:
        data = client.execute(_FULFILLMENT_SERVICES_QUERY, {})
    except Exception:
        frappe.log_error(
            title="Shopify: could not read shop.fulfillmentServices",
            message=frappe.get_traceback(),
        )
        if log:
            _append_log(log, "fulfillment services unavailable; locations cached without them")
        return {}, False

    by_location = {}
    for service in ((data.get("shop") or {}).get("fulfillmentServices") or []):
        location = service.get("location") or {}
        legacy = str(location.get("legacyResourceId") or "")
        if not legacy:
            continue
        # Shopify gives a service exactly one location, but nothing in the schema
        # forbids two services naming the same one. Keep the first and say so
        # rather than letting the last silently win.
        if legacy in by_location:
            if log:
                _append_log(log, f"location {legacy} has more than one fulfillment service; "
                                 f"keeping {by_location[legacy].get('serviceName')!r}, "
                                 f"ignoring {service.get('serviceName')!r}")
            continue
        by_location[legacy] = service
    return by_location, True


@frappe.whitelist()
def sync_shopify_locations(trigger="manual", log_name=None, connection=None):
    """
    Cache every Shopify location as a Shopify Location doc -- the list the
    warehouse-to-location map picks from. Logged (sync_type "locations").
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    connection = connection or connections.require_enabled()
    log = load_or_create_log("locations", trigger, log_name, connection=connection)
    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    try:
        client = ShopifyGraphQLClient(connection)
        services, services_available = _fulfillment_services_by_location(client, log)
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
                if services_available:
                    # Blanks are written too: a service detached on Shopify has to
                    # clear here, or routing keeps trusting one that no longer
                    # ships from this location. Skipped entirely when the services
                    # query failed, so a transient error never erases good data.
                    service = services.get(legacy) or {}
                    values.update({
                        "fulfillment_service_name": service.get("serviceName") or "",
                        "fulfillment_service_handle": service.get("handle") or "",
                        "fulfillment_service_type": service.get("type") or "",
                        "sh_fulfillment_service_gid": service.get("id") or "",
                    })
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
            # ERPNext allows only ONE Item Default row per company -- if one
            # already exists (with a different warehouse), update it in
            # place instead of appending a second row for the same company,
            # which validate_item_defaults rejects outright.
            existing = next((d for d in item.item_defaults if d.company == company), None)
            if existing:
                existing.default_warehouse = warehouse
            else:
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


def run_inventory_push(trigger="manual", log_name=None, connection=None):
    """
    Push current Alaiy OS bin quantities to Shopify inventory levels
    for all items that have a sh_shopify_variant_id set.

    `connection` is the store to push to, defaulting to the one this bench has
    Shopify switched on for. Everything this walks -- Item.sh_shopify_variant_id,
    the Shopify Location rows, the warehouse map -- describes that one store.
    """
    connection = connection or connections.require_enabled()
    log = load_or_create_log("inventory", trigger, log_name, connection=connection)
    if has_active_sync("inventory", exclude_name=log.name, connection=connection):
        _close_log(log, "skipped",
                   error="Skipped: another inventory sync is already running.")
        return log.name

    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    try:
        from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
        settings = connections.resolve(connection)
        client = ShopifyGraphQLClient(settings)

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
            {
                "sync_type": "inventory",
                "status": "success",
                "connection": settings.name,
            },
            "finished_at",
            order_by="finished_at desc",
        )

        totals = {"processed": 0, "updated": 0, "failed": 0, "unchanged": 0}
        cancelled = False
        for warehouse, location_id in pairs:
            if is_cancel_requested(log.name):
                cancelled = True
                _append_log(log, "Stopped by user before finishing all location(s).")
                break
            _backfill_missing_default_warehouse(warehouse)
            cancelled = _push_warehouse_to_location(
                client, warehouse, location_id, last_success_time, log, totals)
            if cancelled:
                break

        _append_log(
            log,
            f"{totals['updated']} pushed, {totals['unchanged']} already in sync, "
            f"{totals['failed']} failed across {len(pairs)} location(s)."
            + (" (stopped early by user)" if cancelled else ""))
        _close_log(log, "cancelled" if cancelled else "success", processed=totals["processed"],
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
    # Listing Variant's copy wins where it has one -- bulk-resolved
    # (one query) rather than a per-item lookup, to keep this scan cheap.
    listing_ids = {
        r.item_variant: r.sh_shopify_variant_id
        for r in frappe.get_all(
            "Shopify Listing Variant",
            filters=[["sh_shopify_variant_id", "is", "set"]],
            fields=["item_variant", "sh_shopify_variant_id"],
        )
    }
    for item in items:
        item.sh_shopify_variant_id = listing_ids.get(item.name) or item.sh_shopify_variant_id

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

    for i, item in enumerate(items):
        if i % 25 == 0:
            if is_cancel_requested(log.name):
                _append_log(log, f"[{warehouse}] stopped by user after {totals['processed']}/{len(items)} items.")
                return True
            # Flush progress periodically, not just at the end -- same gap
            # already found and fixed for the product import/export jobs.
            log.items_processed = totals["processed"]
            log.items_created = totals["updated"]
            log.items_failed = totals["failed"]
            _append_log(log, f"[{warehouse}] ...{totals['processed']}/{len(items)} processed so far "
                              f"({totals['updated']} pushed, {totals['unchanged']} unchanged, {totals['failed']} failed)")
            log.save(ignore_permissions=True)
            frappe.db.commit()
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
    return False


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




def check_fulfillment_service_mapping():
    """Self-check for the fulfillment-service mapping. No API calls, no DB access.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.inventory_sync.check_fulfillment_service_mapping
    """
    class _Client:
        def __init__(self, payload):
            self.payload = payload

        def execute(self, query, variables=None):
            if isinstance(self.payload, Exception):
                raise self.payload
            return self.payload

    def services(*entries):
        return {"shop": {"fulfillmentServices": list(entries)}}

    manual = {"id": "gid://shopify/FulfillmentService/1", "serviceName": "Manual",
              "handle": "manual", "type": "MANUAL",
              "location": {"id": "gid://shopify/Location/9", "legacyResourceId": "9"}}
    gateway = {"id": "gid://shopify/FulfillmentService/2", "serviceName": "ShipBob",
               "handle": "shipbob", "type": "GATEWAY",
               "location": {"id": "gid://shopify/Location/8", "legacyResourceId": "8"}}

    mapped, available = _fulfillment_services_by_location(_Client(services(manual, gateway)))
    assert available
    assert set(mapped) == {"9", "8"}, mapped
    assert mapped["8"]["type"] == "GATEWAY"

    # A shop with no services is not the same as a failed query: the first lets
    # the caller clear stale values, the second must leave them untouched.
    mapped, available = _fulfillment_services_by_location(_Client(services()))
    assert mapped == {} and available is True
    mapped, available = _fulfillment_services_by_location(_Client(RuntimeError("403")))
    assert mapped == {} and available is False

    # A service with no location cannot be attached to one.
    orphan = dict(manual, location=None)
    mapped, _ = _fulfillment_services_by_location(_Client(services(orphan)))
    assert mapped == {}, mapped

    # Two services on one location: first wins, second is dropped, not overwritten.
    second = dict(gateway, serviceName="Other",
                  location={"id": "gid://shopify/Location/9", "legacyResourceId": "9"})
    mapped, _ = _fulfillment_services_by_location(_Client(services(manual, second)))
    assert mapped["9"]["serviceName"] == "Manual", mapped["9"]

    # A missing shop key must not raise.
    mapped, available = _fulfillment_services_by_location(_Client({}))
    assert mapped == {} and available is True

    print("fulfillment service mapping self-check passed")
