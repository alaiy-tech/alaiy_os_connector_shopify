# Products

Bidirectional product sync between Shopify products/variants and Alaiy OS Items. Code lives in the `shopify/product/` package; `product_sync.py` and `product_import.py` are thin compatibility shims re-exporting it (so `hooks.py` doc_event strings and `frappe.enqueue` paths keep resolving).

Tags, Categories, Collections and Sales Channels are product-adjacent domains with their own docs: [Tags](tags.md), [Categories](categories.md), [Collections](collections.md), [Sales Channels](sales-channels.md).

---

## Item custom fields

| Field | Type | Notes |
|---|---|---|
| `sh_shopify_product_id` | Data, read-only, indexed | Legacy copy; the Listing's own copy is now the primary lookup, this is the fallback (see below). |
| `sh_shopify_variant_id` | Data, read-only, indexed | Legacy copy; same fallback relationship with the Listing Variant row's own copy. |
| `sh_shopify_status` | Select (Active/Draft) | Product visibility; template-level, variants inherit. |
| `sh_shopify_product_type` | Data | Shopify `productType`; kept separate from Item Group. |
| `sh_shopify_category` | Link → Shopify Category | Standard Product Taxonomy node ([Categories](categories.md)). |
| `sh_shopify_tags` | Table MultiSelect → Item Shopify Tag | ([Tags](tags.md)). |
| `sh_shopify_collections` | Table MultiSelect → Item Shopify Collection | ([Collections](collections.md)). |
| `sh_seo_title` / `sh_seo_description` | Data / Small Text | Product SEO; default to item name / description. |

Scalar fields (`sh_shopify_product_type`, `sh_shopify_category`, `sh_shopify_status`) use `fetch_from` + `read_only_depends_on` so variants inherit and can't be edited independently. The two Table-MultiSelect fields (tags, collections) can't use `fetch_from`, so variant inheritance is copied explicitly on the Item `validate` hook.

---

## Product Listings (per-marketplace)

`Shopify Product Listing` (`shopify/product/listing.py`, `listing_hooks.py`) is the per-marketplace abstraction over Item. One Listing per **template** Item holds the fields that can differ per sales channel — `listing_title`, `listing_description`, `listing_price`, `listing_category`, `listing_product_type`, `images` (child `Shopify Listing Image`, incl. AI-enhanced), and `variants` (child `Shopify Listing Variant`: per-variant `is_enabled` + `variant_price` + `variant_image`) — plus `is_enabled`, which is now the **sole gate** for whether the product is live on Shopify (it replaces `Item.sync_to_shopify` as the switch).

**Blank = inherit.** A blank Listing field falls back to the Item's current value at push time (`listing.effective_title/description/price/category/product_type/images/variant_image`), so an un-diverged listing stores no duplicate data. The resolver is the single place every export read routes through, and the fingerprint hashes the **resolved** (post-fallback) values — so an Item-level change a blank Listing is inheriting still re-pushes.

`listing_price` is documented simple/no-variant-products-only and is hidden (`depends_on`) on a Listing with more than one variant row, where it's meaningless — each variant's own `variant_price` is the real per-variant price. Shows a real backfilled number for genuinely simple products instead of Frappe's Currency-field blank-as-0.00 display.

A blank override field used to read as "nothing will be sent" when it actually means "inherited from the Item" — most visible on SEO, where both boxes could sit empty while a push still sent a real enriched title/description. The Listing form (`public/js/shopify_product_listing.js::show_effective_values`) now shows the resolved value as each field's description (title, description, product type, category, both SEO fields), and says "Overridden" once filled — shown rather than written in, so it keeps tracking a later Item change instead of freezing it. `listing.effective_values` resolves every one of these through the exact same resolvers the push itself uses, so the form can't disagree with what actually goes to Shopify.

**Item saves no longer push.** Editing an Item is inert for Shopify; only saving/enabling its Listing pushes. Brand, tags, and UOM stay Item-level (not part of the abstraction this phase) — category and product type moved into the Listing abstraction (see below).

**IDs live on the Listing, Item is the fallback.** `Shopify Product Listing.sh_shopify_product_id` and `Shopify Listing Variant.sh_shopify_variant_id` are real, independently-writable columns (not `fetch_from`) — every read site (order matching, inventory push, importer idempotency, export write-back, collections) resolves the Listing's copy first via `listing.py`'s lookup helpers (`item_by_variant_id`, `template_by_product_id`, `variant_id_of_item`, `variant_shopify_id`), falling back to the Item's own copy only if the Listing's is blank. Every write path dual-writes both sides (`listing.set_product_id`/`set_variant_id`), so the two stay in step. The Item columns remain purely as a fallback safety net for now — dropping them entirely is a separate, deliberately deferred step, held back for a longer confidence window in production.

A one-time patch (`patches/create_shopify_product_listings.py` → `listing.ensure_listing`) backfills a Listing for every already-linked Item; a second patch (`patches/backfill_listing_ids.py`) fixes any Listing/Listing Variant row whose id field was still blank from before the dual-write existed. Inbound imports call `ensure_listing` so every linked product stays manageable. UI is a placeholder for now: a **Shopify Listing** button on the template Item form (`public/js/item.js`).

**Populate from Item** — a button on the Listing form (`add_populate_button`) that copies the Item's current title/description/category/product type/variant prices/variant images onto the Listing's override fields, for a merchant who wants to start from an editable snapshot rather than pure inheritance. Fixed to actually cover variant images and category/product type (both were silently skipped at first), and to fill variant price with the real resolved value instead of a blank/0.00 placeholder. The same fields (category, product type, variant price) are now also auto-filled at **Listing creation** time, not only when someone clicks the button — so a freshly-created Listing already reflects the Item's real values instead of sitting blank until a manual populate.

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
`shopify/product/seo.py` / `listing.py::effective_seo`. SEO now has its own **Listing-level override**, same as title/description/price/category/product type — previously only the Item carried `sh_seo_title`/`sh_seo_description`, the one per-channel field that couldn't actually differ per channel. `effective_seo(listing, item)` resolves three levels: the Listing's own override → the Item's `sh_seo_*` fields → the same default Shopify's own admin shows (product title, description as plain text). The 320-character cap applies to an override too, not just the fallback — an override long enough to be truncated by Shopify would otherwise go out whole and get silently cut on their side. Both the push payload and the fingerprint route through `effective_seo`, so a canonical computed differently from the payload can't cause an endless re-push or a missed real change.

### Product type & Item Group
- `sh_shopify_product_type` ⇄ Shopify `productType`. Listing has its own `listing_product_type` override (blank inherits the Item's), same fallback pattern as `listing_title`/`listing_description`/`listing_price` — `listing_resolver.effective_product_type(listing, item)` is what the push payload actually reads, not the Item field directly.
- **Item Group** follows the product's Shopify **category taxonomy** path — `_ensure_item_group_path` (`masters.py`) builds a nested Item Group tree from the category `fullName` ("Apparel & Accessories > Clothing > Shirts") and assigns the leaf; falls back to flat `productType` under "All Item Groups" only when a product has no category. See [Categories → Ancestor Item Groups must stay is_group=1](categories.md) for a real bug this hit.
- Category itself has the same Listing-override pattern: `listing_category` (blank inherits `sh_shopify_category`), read via `effective_category(listing, item)`. See [Categories doc](categories.md) for the CSV bulk-import GID/leaf-name resolver and the junk-node problem it fixes.

### Variant image
Shopify only accepts one media file per variant (separate from the product-level shared image set above) — `Shopify Listing Variant.variant_image` (Attach Image), read via `effective_variant_image(listing, variant_item_code)`, wired into `_variant_set_payload`'s `file` key and `_variant_canonical`'s fingerprint (`variants.py`). No Item-level fallback exists (Items don't carry a per-variant image field) — blank just means the variant shows the product's shared images instead of its own. The image path sent as Shopify's `originalSource` must be an absolute URL — a root-relative path (`/files/...`, what Frappe's Attach Image field actually stores) was being sent as-is and rejected; now resolved to a full URL before the push.

### Dimensions
`Item.weight_per_unit`/length/width/height push as a **per-variant metafield**, not a native Shopify field — Shopify's own variant object has no dimension fields beyond weight (`canonical.py`, `variants.py`).

### Country of origin & HS code
`sh_country_of_origin` (Link to Country) and `sh_harmonized_system_code` (Data), both on Item — pushed as `inventoryItem.countryCodeOfOrigin` (resolved to the Country doctype's own ISO 3166-1 alpha-2 `code` field) and `inventoryItem.harmonizedSystemCode` respectively (`_variant_inventory_item_payload`, `variants.py`). Neither existed anywhere in the export path before a full field-by-field audit against Shopify's API found the gap.

### Metafields
`shopify/product/metafields.py` — full fetch/push of Shopify product metafields (custom fields), stored on a `Shopify Product Metafield` child table on the Listing (namespace/key/type/value). Never on Item — metafields are marketplace-specific, same rule as every other Listing field.

- **Import**: runs from `_import_product`'s single chokepoint (`_sync_product_metafields`), so it fires on every create/update/skip pass, not just new products. `_PRODUCTS_QUERY` fetches `metafields(first: 250)` inline per product; `all_metafields_of` follows pagination past that for the rare product with more than 250. Full replace each run (Shopify is the source of truth — a metafield deleted there disappears from the Listing too, not left stale).
- **Export**: `push_listing_metafields` pushes every row on the Listing back via `metafieldsSet`, right after a successful `productSet` push. Best-effort — never fails the product push it rides on.
- **Backfill for already-imported products**: `backfill_all_product_metafields()` (whitelisted, `bench execute`) fetches metafields directly for every Listing that already has a Shopify product id, without re-running the full import/diff machinery — a normal `Import Products` re-run also picks up metafields for existing products (the sync step isn't gated by "changed"), but this is the lighter targeted option.

### Status: Active / Draft / Archived
- `sh_shopify_status` now models all three real Shopify statuses (Active/Draft/**Archived**), on both the Item field and the Listing — the import used to map only ACTIVE and DRAFT, so an archived product silently read back as Active (measured live on one real store: 8,721 archived products there, 8,408 of them reading Active locally). Worse than a wrong label: the canonical builder sent ACTIVE for anything not Draft, so a routine push could un-archive a product the merchant archived on purpose.
- `shopify/product/status.py` is the single module owning the Active/Draft/Archived translation both ways — the importer writing the field, the canonical builder deciding what a push sends, and the export mutation each used to hardcode their own "DRAFT if Draft else ACTIVE" independently, which is how Archived became unrepresentable in the first place.
- An **unmodelled status is logged and left alone**, never forced to a default — a real store returned `UNLISTED`, which isn't in Shopify's documented `ProductStatus` enum, so this had to be a real branch, not an assumption. (An earlier version of this same fix silently *excluded* an unrecognised status from import entirely, which is worse — that's fixed too.)
- **Six checkboxes** in Shopify Connector Settings choose which statuses each direction (import/export) moves, all on by default. A status excluded from import is counted as skipped-with-reason in the sync log, not silently dropped.
- **Import Products** / **Export Products** now open a dialog (Active/Draft/Archived, all ticked) so a merchant can choose per-run without leaving the page to edit settings first — the dialog's choice wins outright for that run only; the settings checkboxes remain the default for scheduled runs. No selection at all is refused, never treated as "everything."
- Pushing an Archived Listing unarchives it to DRAFT for the `productSet` call (Shopify ignores everything else in the payload while a product is archived), then archives it again — DRAFT rather than ACTIVE, so the product is never briefly visible on the storefront mid-push.
- **Archived** stays modeled the same way as before too: disabling (or trashing) the **Listing** archives the product on Shopify (`archive.py::archive_item`, which also clears the stored fingerprint on success); re-enabling unarchives (via `productUpdate`, see Export above) and re-pushes. Archived-on-Shopify (inbound) disables the **Listing**, never the Item — a per-marketplace state must not hide the product on every other connector too.
- **`query_audit.py` / `status_audit.py`** — introspection tooling, not part of the regular sync path: `query_audit.probe()` diffs the live GraphQL schema against the shipped product query (flags a deprecated field before an API bump breaks it outright, the way it did to `bodyHtml`/`images`/`taxCode`); `status_audit` reports where local status disagrees with Shopify, per-product agreement/disagreement with examples.

### Additional imported fields
A full field-by-field audit against Shopify's schema (`query_audit.py`) found real fields the product query had simply never asked for. Now pulled, read-only where the meaning needs interpretation:
- **Product**: `handle` (storefront slug — the only way to build a product's public URL from here), `publishedAt` (distinguishes never-published from published-then-hidden, which `status` alone can't), `createdAt`, `updatedAt`, `hasOnlyDefaultVariant`, `tracksInventory`, `totalInventory`.
- **Variant**: `barcode`, `position`, `taxable`, `availableForSale`, `inventoryPolicy`, `inventoryQuantity`.
- **Variant → inventoryItem**: `tracked`, `requiresShipping`, `countryCodeOfOrigin`, `harmonizedSystemCode` (the latter two already had custom fields and were already **pushed** — nothing had ever read them back until now, same one-directional gap as status).
- Seven read-only custom fields store the ones that change how a Shopify number should be read: `CONTINUE` inventory policy means stock there can go negative; `tracked=0` means an inventory push to that variant does nothing at all; `requiresShipping=0` marks a digital product that should never appear on a Delivery Note.
- An absent key in the response leaves the field untouched rather than writing a `0`/`False` — a payload that omits a field can't silently be read as "false."
- **Deprecated field migration**: `bodyHtml` → `descriptionHtml` (Shopify's own migration note — `bodyHtml` is how every product description was read, and a deprecated field passes validation right up until the API version where it doesn't, then fails outright, the way `giftCard` already did once). The fingerprint canonical's dict *key* deliberately stays `"bodyHtml"` even though the *value* now comes from `descriptionHtml` — renaming the key would have changed every product's hash and forced a spurious re-update across the whole catalogue (14k items on one store) for a value that didn't actually change. `taxCode` was dropped outright (Shopify: "not available in future versions", no consumer). `images` → `media` is a known, deliberately deferred gap — it changes response shape (a media union needs `... on MediaImage`) and touches variant images too, so it needs its own change and its own testing rather than riding along with this one.
- The query caps variants at 100 and images at 10 with no pagination past that, and Shopify reports no error when a product exceeds either — the import can look fully successful while silently truncating a large product. `variantsCount`/`mediaCount` are now compared against what actually arrived and logged when short. Reported, not fixed — following those cursors is a separate change.

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
