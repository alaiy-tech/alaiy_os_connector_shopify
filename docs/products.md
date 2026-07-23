# Products

Bidirectional product sync between Shopify products/variants and Alaiy OS Items. Code lives in the `shopify/product/` package; `product_sync.py` and `product_import.py` are thin compatibility shims re-exporting it (so `hooks.py` doc_event strings and `frappe.enqueue` paths keep resolving).

Tags, Categories, Collections and Sales Channels are product-adjacent domains with their own docs: [Tags](tags.md), [Categories](categories.md), [Collections](collections.md), [Sales Channels](sales-channels.md).

---

## Item custom fields

| Field | Type | Notes |
|---|---|---|
| `sh_shopify_product_id` | Data, read-only, indexed | Set on import/first push. Variants fetch it from their template. |
| `sh_shopify_variant_id` | Data, read-only, indexed | Shopify variant id for this Item. |
| `sh_shopify_status` | Select (Active/Draft) | Product visibility; template-level, variants inherit. |
| `sh_shopify_product_type` | Data | Shopify `productType`; kept separate from Item Group. |
| `sh_shopify_category` | Link → Shopify Category | Standard Product Taxonomy node ([Categories](categories.md)). |
| `sh_shopify_tags` | Table MultiSelect → Item Shopify Tag | ([Tags](tags.md)). |
| `sh_shopify_collections` | Table MultiSelect → Item Shopify Collection | ([Collections](collections.md)). |
| `sh_seo_title` / `sh_seo_description` | Data / Small Text | Product SEO; default to item name / description. |

Scalar fields (`sh_shopify_product_type`, `sh_shopify_category`, `sh_shopify_status`) use `fetch_from` + `read_only_depends_on` so variants inherit and can't be edited independently. The two Table-MultiSelect fields (tags, collections) can't use `fetch_from`, so variant inheritance is copied explicitly on the Item `validate` hook.

---

## Product Listings (per-marketplace)

`Shopify Product Listing` (`shopify/product/listing.py`, `listing_hooks.py`) is the per-marketplace abstraction over Item. One Listing per **template** Item holds the fields that can differ per sales channel — `listing_title`, `listing_description`, `listing_price`, `images` (child `Shopify Listing Image`, incl. AI-enhanced), and `variants` (child `Shopify Listing Variant`: per-variant `is_enabled` + `variant_price`) — plus `is_enabled`, which is now the **sole gate** for whether the product is live on Shopify (it replaces `Item.sync_to_shopify` as the switch).

**Blank = inherit.** A blank Listing field falls back to the Item's current value at push time (`listing.effective_title/description/price/images`), so an un-diverged listing stores no duplicate data. The resolver is the single place every export read routes through, and the fingerprint hashes the **resolved** (post-fallback) values — so an Item-level change a blank Listing is inheriting still re-pushes.

**Item saves no longer push.** Editing an Item is inert for Shopify; only saving/enabling its Listing pushes. Category, brand, tags, and UOM stay Item-level (not part of the abstraction this phase).

**IDs stay on Item (this phase), single source of truth.** `sh_shopify_product_id` / `sh_shopify_variant_id` physically live on Item and are the sole lookup source for order matching, inventory push, importer idempotency, and collections. The Listing's own id fields are **read-only `fetch_from` views** of the Item — displayed, never written independently, so there's no drifting mirror (contract rule 4). Relocating id *ownership* onto the Listing (and dropping the Item columns) is a separate, verification-gated phase.

A one-time patch (`patches/create_shopify_product_listings.py` → `listing.ensure_listing`) backfills a Listing for every already-linked Item; inbound imports call the same `ensure_listing` so every linked product stays manageable. UI is a placeholder for now: a **Shopify Listing** button on the template Item form (`public/js/item.js`).

---

## Import (Shopify → Alaiy OS)

`shopify/product/importer.py`, entry point `run_full_product_import()` (dashboard → **Import Products**, or `api.sync.trigger_product_import`, 4h timeout).

- **Wipe phase** (`_wipe_all_items`) — only runs automatically on the **first ever run** (no product `Shopify Synced Entity` exists yet), as a safety net against duplicates. Deletes only Items that carry a `sh_shopify_product_id` (previously imported), plus their own single-line opening-stock Stock Entries. Manually-created local Items and all transactional docs (Sales Orders, Delivery Notes, GL/Stock Ledger) are never touched. Uses raw SQL to avoid firing `on_item_delete` per row. Every run after the first does **not** wipe — see below.
- **Paginated fetch** — `_PRODUCTS_QUERY` via the GraphQL client's cursor pagination.
- **Per product** (`_import_product`), on every run after the first:
  - Not imported yet → create. 1 variant → `_import_simple_product` (single Item); >1 variant → `_import_product_with_variants` (template Item + variant Items, with Item Attributes).
  - Already imported, Shopify's data unchanged since last import (`_shopify_node_fingerprint` matches the stored `external_fingerprint` on its Synced Entity) → **skipped untouched**, no write at all.
  - Already imported, Shopify's data changed → **updated** in place (`_update_existing_product`): vendor, tags, category, SEO, Active/Draft status, and per-variant compare-at/cost/weight, matched by SKU. Title/description/images/price are **abstracted** fields: if the product has a Listing, they route onto it (`listing.apply_inbound_from_shopify`) instead of overwriting the Item (`skip_abstracted=True` on the Item-level apply helpers) -- a re-import can no longer clobber the marketplace-agnostic default. No Listing yet → same Item-level behavior as before. Deliberately does **not** touch stock/quantity (opening stock is a one-time Material Receipt at creation only — reapplying it on update would add Shopify's qty on top of the current balance instead of correcting it; `inventory_sync.py` only ever pushes Alaiy OS's qty out to Shopify, it never pulls the other way, so fixing a wrong local qty on an already-imported item needs the separate `scripts/pull_stock_from_shopify.py` one-off tool -- see [Inventory](inventory.md)).
  - A **variant added on Shopify** after the original import is no longer a manual-re-link case: `_ensure_variant_exists_locally` creates the missing Item variant (matching it to an existing sibling by attribute values first, to avoid `ItemVariantExistsError` if an older/differently-named variant already occupies that combination), and `listing.sync_listing_variants` adds it as an enabled `Shopify Listing Variant` row.
  - Pre-existing Items with no Shopify link yet (matched by SKU, e.g. created by another connector) get auto-linked and their content populated via `_apply_existing_variant_content` / `_apply_existing_template_content`, same as before.
  - Every import/re-import ends with `listing.ensure_listing` (create one if missing) + `listing.sync_listing_variants` (add any newly-created variant rows), so a linked product always has a manageable, current Listing.
- Progress, including per-run created/updated/skipped counts and skip reasons, is written to a `Shopify Sync Log` (sync_type `products`).

Concurrency is guarded by a lock on the Settings Single and a `has_active_sync` check.

---

## Export (Alaiy OS → Shopify)

`shopify/product/export.py`. Gated by the template's **Shopify Product Listing** `is_enabled` (`listing.is_enabled`), not `Item.sync_to_shopify`.

- `push_item(item_code)` — always operates at the **template** level. A variant push re-pushes its template.
- `_push_product()` takes a document lock on the template (`LOCK_TIMEOUT_SECONDS`) so concurrent pushes (import, webhook, hourly reconciliation) can't race into duplicate products.
- `_push_product_unlocked()`:
  - Loads the Listing and rebuilds the **full** variant set (`_variants_of` — variants whose `Shopify Listing Variant.is_enabled` is set) and the canonical payload (`_product_set_input`), sourcing title/description/price/images from the Listing (fallback to Item).
  - **Fingerprint guard** — if the canonical fingerprint matches the last successful push (stored on `Shopify Synced Entity`), it returns without calling the API. `archive_item` (below) and the inbound webhook both explicitly clear this fingerprint when a product gets archived/disabled -- otherwise a later re-enable would compute the same ACTIVE/DRAFT fingerprint it had before archiving and silently skip the very push meant to unarchive it.
  - If the product already has a Shopify id, calls `productUpdate` first to force its status back to ACTIVE/DRAFT -- `productSet` alone does not unarchive an ARCHIVED product, it ignores a status change on an already-archived product.
  - Calls `productSet` (`_PRODUCT_SET_MUTATION`) as the full desired state — Shopify creates new variants and updates existing ones in one call.
  - Self-heals stale variant ids (Shopify "variant ids do not exist" → clears them locally and retries).
  - Writes back `sh_shopify_product_id` and per-variant `sh_shopify_variant_id` (matched by SKU, not response order), then reconciles collection membership.
- `run_bulk_export_to_shopify()` (dashboard → **Export Products**) — creates + enables a Listing (all variant rows on) for every local, unlinked, non-disabled template and pushes it. One-off for pre-existing catalogs.
- `push_changed_items_only()` — hourly scheduler; re-pushes every template with an enabled Listing (each fingerprint-guarded, so unchanged items are no-ops).

### Variants
`shopify/product/variants.py` — builds each variant's canonical + `productSet` payload: price, compare-at, cost, SKU, title, selected options, weight/dimensions (`_apply_variant_physical`), and inventory item payload.

### Pricing
`shopify/product/pricing.py` — price / compare-at / cost each map to a Price List. Selling price uses `sh_selling_price_list`; compare-at and cost use synthetic price lists auto-created (`_ensure_price_list`) inheriting the configured list's currency. See the currency note in [Architecture](architecture.md).

### Media
`shopify/product/media.py` — `_item_images` gathers `Item.image` + Website Slideshow images; `_download_to_file` pulls remote images into Frappe Files on import. Always pushed (no toggle).

### SEO
`shopify/product/seo.py` — `sh_seo_title` / `sh_seo_description`, defaulting to item name / (stripped) description when blank.

### Product type & Item Group
- `sh_shopify_product_type` ⇄ Shopify `productType`, always synced (no toggle).
- **Item Group** follows the product's Shopify **category taxonomy** path — `_ensure_item_group_path` (`masters.py`) builds a nested Item Group tree from the category `fullName` ("Apparel & Accessories > Clothing > Shirts") and assigns the leaf; falls back to flat `productType` under "All Item Groups" only when a product has no category.

### Status: Active / Draft / Archived
- `sh_shopify_status` (Active/Draft) is pushed as the product `status` and is part of the fingerprint (so flipping it re-pushes). Imported back from `product.status`.
- **Archived** is separate: disabling (or trashing) the **Listing** archives the product on Shopify (`archive.py::archive_item`, which also clears the stored fingerprint on success); re-enabling unarchives (via `productUpdate`, see Export above) and re-pushes. Archived-on-Shopify (inbound) disables the **Listing**, never the Item -- a per-marketplace state must not hide the product on every other connector too.

---

## Product webhooks (Shopify → Alaiy OS)

`shopify/product/webhooks.py::handle_product_webhook` routes `products/create|update|delete`:
- `_webhook_product_to_graphql_node` reshapes the REST webhook payload into the same GraphQL node shape the importer consumes.
- create → import; update → `_update_item_from_shopify`; delete → archive the Item.

`_update_item_from_shopify` follows the same abstracted/Item-level split as the re-import path: title/description/images/variant-price go to the **Listing** when one exists (`listing.listing_title` etc, never the Item); vendor/`sh_shopify_product_type`/tags/category/status stay Item-level via `_apply_product_meta`. Archived status (or the Listing being disabled) explicitly clears the stored fingerprint (see Export above) and never disables the Item — only the Listing.

For each variant in the payload, `_ensure_variant_exists_locally` creates the Item variant if missing (matching an existing sibling by attribute values first, so an older/differently-named variant already occupying that attribute combination is reused instead of raising `ItemVariantExistsError`), and a matching enabled `Shopify Listing Variant` row is added inline if one doesn't already exist — a variant added on Shopify reaches the Listing on the very next webhook, not just on a later re-import.

Inbound saves set `flags.from_shopify_sync` so nothing echoes back. A product deleted on Shopify also disables + unlinks its Listing (so hourly reconciliation doesn't recreate it); a variant missing from an inbound payload has its `Shopify Listing Variant` row disabled (Item variant left intact).

---

## Item doc_events & scheduler

| Hook | Function | Purpose |
|---|---|---|
| Item `validate` | `validate_item_uoms`, `copy_template_tags_to_variant`, `copy_template_collections_to_variant` | Dedup UOMs; copy template tags/collections onto variants. |
| Item `after_insert` | `sync_new_variant_to_listing` | Data upkeep only: add a desk-created variant to its template's Listing (which then pushes). Never pushes directly. |
| Item `on_trash` | `remove_variant_from_listing` | Data upkeep only: drop a deleted variant's row from the Listing (which re-pushes). |
| Shopify Product Listing `on_update` | `on_listing_update` | Push the product when the Listing is enabled; archive it when just disabled. **The push trigger.** |
| Shopify Product Listing `on_trash` | `on_listing_trash` | Archive the product on Shopify. |
| Scheduler `hourly` | `push_changed_items_only` | Reconciliation push (every enabled Listing). |
| Scheduler `daily` | `fetch_shopify_taxonomy`, `sync_shopify_tags`, `sync_shopify_collections`, `sync_shopify_locations` | Refresh category tree, tags, collections, and locations caches. |
