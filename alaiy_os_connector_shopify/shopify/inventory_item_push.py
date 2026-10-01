"""
Push one item's stock for one warehouse to its live Shopify variant.

run_inventory_push walks every mapped warehouse and every changed Bin on a
schedule. This is the opposite: one item, one warehouse, now, for a caller that
has just changed that stock and needs the live product to agree. It never
enqueues, never takes the sync log, and never touches another item, so it can
run beside the bulk push without either blocking the other.

What it does that the bulk push does not:

  * Activates the variant at the location when Shopify has no level for it
    there. Setting a quantity at a location the variant is not stocked at is not
    the same as stocking it, and a read-back would show nothing.
  * Reports Shopify's own tracking flag. A quantity pushed to a variant Shopify
    does not track is ignored, so the caller needs to see that rather than a
    success. Switching tracking on changes how the live product sells, so it
    only happens when asked for (enable_tracking).
  * Reports a failure as a value, with a reason a person can read, instead of
    raising. Callers are request handlers that show the reason.
"""

import traceback

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify import connections
from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient, new_idempotency_key
from alaiy_os_connector_shopify.shopify.inventory_sync import _INVENTORY_SET_MUTATION
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver

_STATE_QUERY = """
query ItemStockState($id: ID!, $locationId: ID!) {
  productVariant(id: $id) {
    inventoryItem {
      id
      tracked
      inventoryLevel(locationId: $locationId) {
        quantities(names: ["available"]) {
          quantity
        }
      }
    }
  }
}
"""

_TRACK_MUTATION = """
mutation TrackInventory($id: ID!, $input: InventoryItemInput!) {
  inventoryItemUpdate(id: $id, input: $input) {
    inventoryItem {
      id
      tracked
    }
    userErrors {
      field
      message
    }
  }
}
"""

_ACTIVATE_MUTATION = """
mutation ActivateInventory($inventoryItemId: ID!, $locationId: ID!, $available: Int, $idempotencyKey: String!) {
  inventoryActivate(inventoryItemId: $inventoryItemId, locationId: $locationId, available: $available)
      @idempotent(key: $idempotencyKey) {
    inventoryLevel {
      id
    }
    userErrors {
      field
      message
    }
  }
}
"""


def push_item_stock(item_code, warehouse, connection=None, enable_tracking=False, client=None):
    """Make Shopify's available quantity for `item_code` at `warehouse`'s
    location equal the Bin quantity.

    Returns {ok, item_code, warehouse, location, action, before, after, tracked,
    verified, reason}. action is "set", "activated" or "unchanged". verified is
    False when the push was accepted but Shopify's read-back had not caught up.
    """
    try:
        return _push(item_code, warehouse, connection, enable_tracking, client)
    except Exception as exc:
        # format_exc, not frappe.get_traceback: the latter prints every local in
        # every frame, and the Shopify client holds the store's access token.
        frappe.log_error(
            title=f"Shopify single-item stock push failed for {item_code}",
            message=traceback.format_exc(),
        )
        return _result(item_code, warehouse, ok=False, reason=f"Request to Shopify failed ({type(exc).__name__}) -- see Error Log.")


def _push(item_code, warehouse, connection, enable_tracking, client):
    settings = connections.resolve(connection) if connection else connections.require_enabled()

    item = frappe.db.get_value("Item", item_code, ["name", "variant_of"], as_dict=True)
    if not item:
        return _result(item_code, warehouse, ok=False, reason="Item not found.")
    listing = listing_resolver.get_listing(item.variant_of or item.name)
    if not listing:
        return _result(item_code, warehouse, ok=False, reason="No Shopify Product Listing exists for this item yet.")
    variant_id = listing_resolver.variant_shopify_id(listing, item_code)
    if not variant_id:
        return _result(item_code, warehouse, ok=False, reason="This item has never been pushed to Shopify -- no variant id yet.")

    location_gid = _location_gid(settings, warehouse)
    if not location_gid:
        return _result(item_code, warehouse, ok=False, reason=f"Warehouse {warehouse} is not mapped to a Shopify location.")

    # No Bin means "no stock recorded", not "confirmed zero": pushing it would
    # replace real Shopify stock with a number Alaiy OS never knew.
    bin_qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
    if bin_qty is None:
        return _result(item_code, warehouse, ok=False, location=location_gid,
                       reason=f"No stock record for this item in {warehouse} -- not pushing an assumed zero.")
    qty = flt(bin_qty)
    if qty != int(qty) or qty < 0:
        return _result(item_code, warehouse, ok=False, location=location_gid,
                       reason=f"Shopify holds whole, non-negative units; the stock here is {qty:g}.")
    qty = int(qty)

    client = client or ShopifyGraphQLClient(settings)
    variables = {"id": f"gid://shopify/ProductVariant/{variant_id}", "locationId": location_gid}
    state = _read_state(client, variables)
    if not state.get("id"):
        return _result(item_code, warehouse, ok=False, location=location_gid,
                       reason="Shopify has no inventory item for this variant.")
    inventory_item_id = state["id"]
    tracked = bool(state.get("tracked"))

    if not tracked and enable_tracking:
        data = client.execute(_TRACK_MUTATION, {"id": inventory_item_id, "input": {"tracked": True}})
        errors = (data.get("inventoryItemUpdate") or {}).get("userErrors") or []
        if errors:
            return _result(item_code, warehouse, ok=False, location=location_gid, tracked=False,
                           reason=f"Shopify would not turn tracking on: {_messages(errors)}")
        tracked = True

    level = state.get("inventoryLevel")
    if level is None:
        before, action = None, "activated"
        data = client.execute(_ACTIVATE_MUTATION, {
            "inventoryItemId": inventory_item_id, "locationId": location_gid,
            "available": qty, "idempotencyKey": new_idempotency_key(),
        })
        errors = (data.get("inventoryActivate") or {}).get("userErrors") or []
    else:
        before = _available(level)
        if before == qty:
            return _result(item_code, warehouse, ok=True, location=location_gid, action="unchanged",
                           before=before, after=qty, tracked=tracked, verified=True)
        action = "set"
        data = client.execute(_INVENTORY_SET_MUTATION, {
            "input": {
                "name": "available",
                "reason": "correction",
                "quantities": [{
                    "inventoryItemId": inventory_item_id,
                    "locationId": location_gid,
                    "quantity": qty,
                    # Mandatory as of API 2026-04: a concurrent change fails
                    # here instead of being silently overwritten.
                    "changeFromQuantity": before,
                }],
            },
            "idempotencyKey": new_idempotency_key(),
        })
        errors = (data.get("inventorySetQuantities") or {}).get("userErrors") or []
    if errors:
        return _result(item_code, warehouse, ok=False, location=location_gid, action=action,
                       before=before, tracked=tracked, reason=f"Shopify refused the change: {_messages(errors)}")

    after_level = _read_state(client, variables).get("inventoryLevel")
    after = _available(after_level) if after_level is not None else None
    return _result(item_code, warehouse, ok=True, location=location_gid, action=action,
                   before=before, after=qty if after is None else after, tracked=tracked,
                   verified=after == qty)


def _location_gid(settings, warehouse):
    """The Shopify location a warehouse is mapped to, or None. The mapping lives
    on the Shopify Connection; Shopify Location carries no warehouse of its own."""
    for row in settings.get("sh_location_map") or []:
        if row.warehouse == warehouse and row.shopify_location:
            gid = frappe.db.get_value("Shopify Location", row.shopify_location, "sh_location_gid")
            if gid:
                return gid
    return None


def _read_state(client, variables):
    data = client.execute(_STATE_QUERY, variables)
    return ((data.get("productVariant") or {}).get("inventoryItem")) or {}


def _available(level):
    quantities = (level or {}).get("quantities") or []
    return int(quantities[0].get("quantity") or 0) if quantities else 0


def _messages(errors):
    return "; ".join(e.get("message", "") for e in errors)


def _result(item_code, warehouse, ok, reason=None, location=None, action=None,
            before=None, after=None, tracked=None, verified=False):
    return {
        "ok": ok, "item_code": item_code, "warehouse": warehouse, "location": location,
        "action": action, "before": before, "after": after, "tracked": tracked,
        "verified": verified, "reason": reason,
    }
