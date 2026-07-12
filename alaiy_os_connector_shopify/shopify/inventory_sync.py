import frappe
from frappe.utils import flt, now_datetime

from alaiy_os_connector_shopify.shopify.sync_guard import has_active_sync, load_or_create_log

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
query VariantInventoryItem($id: ID!) {
  productVariant(id: $id) {
    inventoryItem {
      id
    }
  }
}
"""


def _inventory_set_mutation(idempotency_key: str) -> str:
    # @idempotent's key isn't documented as accepting a GraphQL variable, so
    # it's interpolated directly into the query text rather than passed
    # through `variables`.
    return f"""
    mutation SetInventory($input: InventorySetQuantitiesInput!) {{
      inventorySetQuantities(input: $input) @idempotent(key: "{idempotency_key}") {{
        userErrors {{
          field
          message
        }}
      }}
    }}
    """


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

        items = frappe.get_all(
            "Item",
            # NOT IN with a NULL in the list is a standard SQL trap: it
            # matches nothing, ever ("x <> NULL" is unknown, not true) --
            # "is set" is the safe way to say "non-empty".
            filters=[["sh_shopify_variant_id", "is", "set"]],
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

                inventory_item_id = _get_inventory_item_id(
                    client, item.sh_shopify_variant_id)
                if not inventory_item_id:
                    failed += 1
                    _append_log(
                        log, f"ERROR item={item.name}: no Shopify inventory_item_id for variant {item.sh_shopify_variant_id}")
                    continue

                data = client.execute(_inventory_set_mutation(new_idempotency_key()), {
                    "input": {
                        "name": "available",
                        "reason": "correction",
                        "quantities": [{
                            "inventoryItemId": inventory_item_id,
                            "locationId": location_id,
                            "quantity": int(qty),
                        }],
                    },
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


def _get_inventory_item_id(client, variant_id):
    variant_gid = f"gid://shopify/ProductVariant/{variant_id}"
    data = client.execute(_VARIANT_INVENTORY_QUERY, {"id": variant_gid})
    variant = data.get("productVariant") or {}
    inventory_item = variant.get("inventoryItem") or {}
    return inventory_item.get("id")  # GID


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
