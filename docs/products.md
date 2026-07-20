# Products

Bidirectional product sync between Shopify products/variants and Alaiy OS Items. Code lives in the `shopify/product/` package; `product_sync.py` and `product_import.py` are thin compatibility shims re-exporting it (so `hooks.py` doc_event strings and `frappe.enqueue` paths keep resolving).

Tags, Categories, Collections and Sales Channels are product-adjacent domains with their own docs: [Tags](tags.md), [Categories](categories.md), [Collections](collections.md), [Sales Channels](sales-channels.md).

---

## Item custom fields

| Field | Type | Notes |
|---|---|---|
| `sh_shopify_product_id` | Data, read-only, indexed | Set on import/first push. Variants fetch it from their template. |
| `sh_shopify_variant_id` | Data, read-only, indexed | Shopify variant id for this Item. |
| `sync_to_shopify` | Check (default 0) | Master push switch. On a **template** it controls the whole product; on a **variant** it's a per-variant include flag. |
| `sh_shopify_status` | Select (Active/Draft) | Product visibility; template-level, variants inherit. |
| `sh_shopify_product_type` | Data | Shopify `productType`; kept separate from Item Group. |
| `sh_shopify_category` | Link → Shopify Category | Standard Product Taxonomy node ([Categories](categories.md)). |
| `sh_shopify_tags` | Table MultiSelect → Item Shopify Tag | ([Tags](tags.md)). |
| `sh_shopify_collections` | Table MultiSelect → Item Shopify Collection | ([Collections](collections.md)). |
| `sh_seo_title` / `sh_seo_description` | Data / Small Text | Product SEO; default to item name / description. |

Scalar fields (`sh_shopify_product_type`, `sh_shopify_category`, `sh_shopify_status`) use `fetch_from` + `read_only_depends_on` so variants inherit and can't be edited independently. The two Table-MultiSelect fields (tags, collections) can't use `fetch_from`, so variant inheritance is copied explicitly on the Item `validate` hook.

---

## Import (Shopify → Alaiy OS)

`shopify/product/importer.py`, entry point `run_full_product_import()` (dashboard → **Import Products**, or `api.sync.trigger_product_import`, 4h timeout).

- **Wipe phase** (`_wipe_all_items`) — deletes only Items that carry a `sh_shopify_product_id` (previously imported), plus their own single-line opening-stock Stock Entries. Manually-created local Items and all transactional docs (Sales Orders, Delivery Notes, GL/Stock Ledger) are never touched. Uses raw SQL to avoid firing `on_item_delete` per row.
- **Paginated fetch** — `_PRODUCTS_QUERY` via the GraphQL client's cursor pagination.
- **Per product** (`_import_product`):
  - 1 variant → `_import_simple_product` (single Item).
  - >1 variant → `_import_product_with_variants` (template Item + variant Items, with Item Attributes).
  - Pre-existing Items (matched by SKU/variant id) get content merged via `_apply_existing_variant_content` / `_apply_existing_template_content` rather than duplicated.
- **Applied per product**: pricing (price / compare-at / cost), images (main + slideshow), tags, category, collections membership, SEO, product type, Active/Draft status, opening stock, Item-group hierarchy.
- Progress + skip reasons are written to a `Shopify Sync Log` (sync_type `products`).

Concurrency is guarded by a lock on the Settings Single and a `has_active_sync` check.

---

## Export (Alaiy OS → Shopify)

`shopify/product/export.py`. Opt-in via `Item.sync_to_shopify`.

- `push_item(item_code)` — always operates at the **template** level. A variant push re-pushes its template.
- `_push_product()` takes a document lock on the template (`LOCK_TIMEOUT_SECONDS`) so the cascade of `on_update` events Alaiy OS fires when a template is saved can't race into duplicate products.
- `_push_product_unlocked()`:
  - Rebuilds the **full** variant set (`_variants_of` — only variants with their own `sync_to_shopify` checked) and the canonical payload (`_product_set_input`).
  - **Fingerprint guard** — if the canonical fingerprint matches the last successful push (stored on `Shopify Synced Entity`), it returns without calling the API.
  - Calls `productSet` (`_PRODUCT_SET_MUTATION`) as the full desired state — Shopify creates new variants and updates existing ones in one call.
  - Self-heals stale variant ids (Shopify "variant ids do not exist" → clears them locally and retries).
  - Writes back `sh_shopify_product_id` and per-variant `sh_shopify_variant_id` (matched by SKU, not response order), then reconciles collection membership.
- `run_bulk_export_to_shopify()` (dashboard → **Export Products**) — opts every local, unlinked, non-disabled template into `sync_to_shopify` and pushes it. One-off for pre-existing catalogs.
- `push_changed_items_only()` — hourly scheduler; re-pushes every `sync_to_shopify` template (each fingerprint-guarded, so unchanged items are no-ops).

### Variants
`shopify/product/variants.py` — builds each variant's canonical + `productSet` payload: price, compare-at, cost, SKU, title, selected options, weight/dimensions (`_apply_variant_physical`), and inventory item payload.

### Pricing
`shopify/product/pricing.py` — price / compare-at / cost each map to a Price List. Selling price uses `sh_selling_price_list`; compare-at and cost use synthetic price lists auto-created (`_ensure_price_list`) inheriting the configured list's currency. See the currency note in [Architecture](architecture.md).

### Media
`shopify/product/media.py` — `_item_images` gathers `Item.image` + Website Slideshow images; `_download_to_file` pulls remote images into Frappe Files on import. Gated by `sh_push_images`.

### SEO
`shopify/product/seo.py` — `sh_seo_title` / `sh_seo_description`, defaulting to item name / (stripped) description when blank.

### Product type & Item Group
- `sh_shopify_product_type` ⇄ Shopify `productType`, gated by `sh_push_product_type`.
- **Item Group** follows the product's Shopify **category taxonomy** path — `_ensure_item_group_path` (`masters.py`) builds a nested Item Group tree from the category `fullName` ("Apparel & Accessories > Clothing > Shirts") and assigns the leaf; falls back to flat `productType` under "All Item Groups" only when a product has no category.

### Status: Active / Draft / Archived
- `sh_shopify_status` (Active/Draft) is pushed as the product `status` and is part of the fingerprint (so flipping it re-pushes). Imported back from `product.status`.
- **Archived** is separate: unchecking `sync_to_shopify` (or disabling the Item) archives the product on Shopify (`archive.py::archive_item`); re-checking unarchives and re-pushes. On import, an archived Shopify product disables the Item; draft does **not** disable it.

---

## Product webhooks (Shopify → Alaiy OS)

`shopify/product/webhooks.py::handle_product_webhook` routes `products/create|update|delete`:
- `_webhook_product_to_graphql_node` reshapes the REST webhook payload into the same GraphQL node shape the importer consumes.
- create → import; update → `_update_item_from_shopify` (title, description, vendor, product_type, status, tags, category); delete → archive the Item.

Inbound saves set `flags.from_shopify_sync` so the outbound `on_item_change` hook doesn't echo them back.

---

## Item doc_events & scheduler

| Hook | Function | Purpose |
|---|---|---|
| Item `validate` | `validate_item_uoms`, `copy_template_tags_to_variant`, `copy_template_collections_to_variant` | Dedup UOMs; copy template tags/collections onto variants. |
| Item `after_insert` / `on_update` | `on_item_change` | Enqueue push (or archive) when a synced Item changes; auto-check variants of a newly-enabled template. |
| Item `on_trash` | `on_item_delete` | Re-push the template so a deleted variant drops from Shopify. |
| Item Price `after_insert` / `on_update` | `on_item_price_change` | Push when the selling price list changes. |
| Scheduler `hourly` | `push_changed_items_only` | Reconciliation push. |
| Scheduler `daily` | `fetch_shopify_taxonomy` | Refresh category tree. |
