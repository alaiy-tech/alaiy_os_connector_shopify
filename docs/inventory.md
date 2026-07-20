# Inventory

One-directional stock push: Alaiy OS bin quantities → Shopify inventory levels. Single-location by default, multi-location when a warehouse→location map is configured. Code: `shopify/inventory_sync.py`.

---

## DocTypes

| DocType | Kind | Fields |
|---|---|---|
| `Shopify Location` | Cache (autoname hash) | `location_name`, `is_active`, `sh_location_id`, `sh_location_gid`, `last_synced`. |
| `Shopify Location Map` | Child table on Settings (`sh_location_map`) | `warehouse` (Link Warehouse), `shopify_location` (Link Shopify Location). |

---

## Sync locations

`sync_shopify_locations()` (dashboard → **Sync Locations**, or `api.sync.refresh_shopify_locations`) fetches every Shopify location (`_LOCATIONS_QUERY`) and caches it as a `Shopify Location` doc — the list the warehouse→location map picks from. Writes a `Shopify Sync Log` (sync_type `locations`).

---

## Stock push (`run_inventory_push`)

Triggered by dashboard **Sync Inventory** (`api.sync.trigger_inventory_push`) or the scheduler at `sh_inventory_sync_interval`.

1. **Resolve pairs** (`_resolve_location_pairs`): if `sh_location_map` has rows → one `(warehouse, location_gid)` pair per mapping (**multi-location**); otherwise a single pair of Default Warehouse → primary Shopify location (`_get_primary_location_id`).
2. For each pair (`_push_warehouse_to_location`):
   - Selects items with a `sh_shopify_variant_id`, narrowed to those whose **Bin changed since the last successful sync** (or, on first run, the last 24h) — avoids N+1 API calls on large, mostly-unchanged catalogs.
   - Reads the bin's `actual_qty` for that warehouse, fetches the current Shopify quantity (`_get_inventory_item_state`), and **skips the write if already equal** (Shopify no-op).
   - Otherwise calls `inventorySetQuantities` with `changeFromQuantity` (mandatory as of API 2026-04 — a concurrent-change race fails loudly rather than silently overwriting), using an idempotency key.
3. Counters (processed / updated / unchanged / failed) roll up into one `Shopify Sync Log` (sync_type `inventory`).

`_backfill_missing_default_warehouse` heals Item Defaults for items imported before defaults were set, capped per run.

---

## Import side

On product import, a variant's available quantity comes from Shopify's first inventory level (`product/variants.py::_variant_available_qty`) and seeds opening stock. Multi-location **import** (per-location stock into Alaiy OS) is not implemented — the map drives the **push** direction.

---

## Warehouse resolution

`shopify/order/warehouse.py::_resolve_default_warehouse` returns the configured `sh_default_warehouse` if it's a non-group leaf, else self-heals to the first real leaf warehouse under the company — a Group warehouse would otherwise break stock transactions.
