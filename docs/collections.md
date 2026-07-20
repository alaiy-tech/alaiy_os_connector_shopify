# Collections

Bidirectional sync of **manual** Shopify collections. Smart (rule-based) collections are cached read-only — their membership is driven by Shopify's own rules, so products can't be added/removed from our side. Code: `shopify/product/collections.py`.

---

## DocTypes

| DocType | Kind | Key fields |
|---|---|---|
| `Shopify Collection` | Cache (autoname hash) | `collection_title`, `handle`, `is_smart`, `product_count`, `sh_collection_id`, `sh_collection_gid`, `description`, `image_url`, `last_synced`, plus form-only HTML fields `channels_html`, `members_html`. |
| `Item Shopify Collection` | Child table | `shopify_collection` (Link → Shopify Collection); backs `Item.sh_shopify_collections`. |

---

## Import — cache the collection list

`sync_shopify_collections()` (dashboard → **Sync Collections**, or `api.sync.refresh_shopify_collections`) pages every collection (`_COLLECTIONS_LIST_QUERY`, 100/page) into `Shopify Collection` docs. Sets `is_smart` when the collection has a `ruleSet`, stores `productsCount`, and writes a `Shopify Sync Log` (sync_type `collections`). Upsert keyed on `sh_collection_id`, flagged `from_shopify_sync` to avoid echo.

Product **membership** is imported with the product itself: the product pull query includes `collections { nodes { title } }`, and `_set_item_collections` links the Item's `sh_shopify_collections` to matching cached collections.

---

## Membership export (Alaiy OS → Shopify)

After each product push, `sync_item_collections(item, product_id, client)` reconciles the product's manual-collection membership on Shopify against the Item's `sh_shopify_collections` field:
- Desired = the Item's linked **manual** collections (smart excluded).
- Current = the product's collections on Shopify, narrowed to ones we know and manual.
- Diff → `collectionAddProducts` for additions, `collectionRemoveProducts` for removals.
- Best-effort — logs and continues; never fails the product push. Smart collections are never touched.

Variants inherit the template's collections via `copy_template_collections_to_variant` (Item `validate` hook).

---

## Collection CRUD export

`Shopify Collection` doc_events push changes back:
- `on_shopify_collection_update` → `push_collection` → `collectionCreate` (no gid yet) or `collectionUpdate`.
- `on_shopify_collection_trash` → `delete_collection` → `collectionDelete`.
- Skipped for smart collections and for saves flagged `from_shopify_sync`.

---

## Webhooks

`handle_collection_webhook` handles `collections/create|update|delete` — create/update upsert the cache doc, delete removes it.

---

## Collection form

`shopify_collection.js` renders, live-fetched on open:
- **Sales Channels** chips (see [Sales Channels](sales-channels.md)).
- **Products** grid — `get_collection_products` live-fetches the collection's products (title, image, price, sku, linked Item) and shows them as image cards like Shopify; also reconciles the stored `product_count` to the real fetched count.

The title is read-only once the collection is synced (`read_only_depends_on` on `sh_collection_gid`) — editable only when creating a new collection in Alaiy OS.
