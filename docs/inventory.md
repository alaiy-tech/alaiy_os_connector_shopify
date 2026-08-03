# Inventory

One-directional stock push: Alaiy OS bin quantities → Shopify inventory levels. Single-location by default, multi-location when a warehouse→location map is configured. Code: `shopify/inventory_sync.py`.

---

## DocTypes

| DocType | Kind | Fields |
|---|---|---|
| `Shopify Location` | Cache (autoname hash) | `location_name`, `is_active`, `sh_location_id`, `sh_location_gid`, `fulfillment_service_name`, `fulfillment_service_handle`, `fulfillment_service_type`, `sh_fulfillment_service_gid`, `last_synced`. |
| `Shopify Location Map` | Child table on Settings (`sh_location_map`) | `warehouse` (Link Warehouse), `shopify_location` (Link Shopify Location). |

---

## Sync locations

`sync_shopify_locations()` (dashboard → **Sync Locations**, or `api.sync.refresh_shopify_locations`) fetches every Shopify location (`_LOCATIONS_QUERY`, cursor-paginated at 250/page via `pageInfo.hasNextPage`/`endCursor` — a store with more than 50 locations used to have the rest silently dropped by a flat `first: 50` fetch) and caches it as a `Shopify Location` doc — the list the warehouse→location map picks from. Writes a `Shopify Sync Log` (sync_type `locations`).

### Fulfillment services

The same run also reads `shop.fulfillmentServices` (`_FULFILLMENT_SERVICES_QUERY`) and stores each location's service name, handle and type on its `Shopify Location`. A location's identity does not say who ships from it — a third-party warehouse (`type` `GATEWAY`) has to be routed differently from one the merchant packs (`MANUAL`), and Shopify exposes that only here.

Three things about this that are not obvious from the schema:

- **`fulfillmentServices` hangs off `shop`, not off `Location`**, and each service names the one location it serves. So the mapping is built service-first (`_fulfillment_services_by_location`) and looked up per location, not fetched per location.
- **No pagination.** Shopify returns the shop's services as a plain list, not a connection — there is no cursor to follow.
- **Failure is not emptiness.** The helper returns `(mapping, available)`. On a failed query — missing scope, older API version, network — `available` is `False` and the sync leaves each location's stored service *untouched*, because blanking it would erase routing data that is still correct. When the query succeeds and a location genuinely has no service, the fields are cleared, so a service detached on Shopify stops being trusted here.

If two services ever name the same location, the first is kept and the second is noted in the sync log rather than silently overwriting it.

`check_fulfillment_service_mapping()` covers the mapping rules with no API or DB access:

```
bench --site <site> execute alaiy_os_connector_shopify.shopify.inventory_sync.check_fulfillment_service_mapping
```

---

## Stock push (`run_inventory_push`)

Triggered by dashboard **Sync Inventory** (`api.sync.trigger_inventory_push`) or the scheduler at `sh_inventory_sync_interval`.

1. **Resolve pairs** (`_resolve_location_pairs`): if `sh_location_map` has rows → one `(warehouse, location_gid)` pair per mapping (**multi-location**); otherwise a single pair of Default Warehouse → primary Shopify location (`_get_primary_location_id`).
2. For each pair (`_push_warehouse_to_location`):
   - Selects items with a `sh_shopify_variant_id`, then bulk-resolves each one's variant id preferring the Shopify Listing Variant row's own copy over Item's (one extra query up front, not per item), narrowed to those whose **Bin changed since the last successful sync** (or, on first run, the last 24h) — avoids N+1 API calls on large, mostly-unchanged catalogs.
   - Reads the bin's `actual_qty` for that warehouse. **A missing Bin record is skipped (logged), never pushed as 0** — no data means unknown, not confirmed zero. This is what caused a real incident (a Bin table wipe followed by a scheduled push overwrote real Shopify stock with false zeros); fixed by skipping instead of guessing.
   - Fetches the current Shopify quantity (`_get_inventory_item_state`), and **skips the write if already equal** (Shopify no-op).
   - Otherwise calls `inventorySetQuantities` with `changeFromQuantity` (mandatory as of API 2026-04 — a concurrent-change race fails loudly rather than silently overwriting), using an idempotency key. Every real push logs the item, variant, warehouse, and old → new quantity.
3. Counters (processed / updated / unchanged / failed) roll up into one `Shopify Sync Log` (sync_type `inventory`). Scheduled runs use a 3600s job timeout (raised from 600s, which was provably too short for a full catalog).

---

## Correcting local stock drift (`scripts/pull_stock_from_shopify.py`)

This connector never pulls stock *from* Shopify automatically -- product import only sets opening stock once, at creation (see [Products](products.md)). If local Alaiy OS stock ever drifts from Shopify's real numbers (e.g. after manual data cleanup, or recovering from an incident), a one-off script pulls Shopify's live quantity per item and applies the correction via a real, audited **Stock Reconciliation** (never touches sales/opening-stock history):

- Dry-run first (reports every mismatch, changes nothing), then apply for real once reviewed.
- Clamps a negative Shopify quantity (oversold variants) to 0 rather than writing a negative stock value.
- Skips disabled Items (a single disabled row otherwise fails the entire Stock Reconciliation batch) and reports them separately.
- Needs `allow_zero_valuation_rate` on each corrected row and an explicit `frappe.db.commit()` after submit -- both confirmed live as required, the same way opening stock's own creation path already needed the first one.

`_backfill_missing_default_warehouse` heals Item Defaults for items imported before defaults were set, capped per run. Updates the existing Item Default row for the company if one already exists (with a different warehouse), rather than appending a second one -- Alaiy OS allows only one Item Default per company per item, so appending a second row crashed with "Cannot set multiple Item Defaults for a company."

---

## Import side

On product import, a variant's available quantity comes from Shopify's first inventory level (`product/variants.py::_variant_available_qty`) and seeds opening stock. Multi-location **import** (per-location stock into Alaiy OS) is not implemented — the map drives the **push** direction.

---

## Warehouse resolution

`shopify/order/warehouse.py::_resolve_default_warehouse` returns the configured `sh_default_warehouse` if it's a non-group leaf, else self-heals to the first real leaf warehouse under the company — a Group warehouse would otherwise break stock transactions.
