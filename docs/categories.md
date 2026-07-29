# Categories (Standard Product Taxonomy)

Shopify's **Standard Product Taxonomy** — the fixed category tree ("Apparel & Accessories > Clothing > Shirts") — cached locally as a tree DocType and assigned to products. Code: `shopify/product/taxonomy.py`.

---

## DocType

`Shopify Category` — a **tree** DocType (nested set). Fields: `shopify_category_name`, `shopify_category_id` (the Shopify taxonomy GID), `parent_shopify_category`.

`Item.sh_shopify_category` is a Link to it (template-level, variants inherit via `fetch_from`).

---

## Import — cache the taxonomy tree

`fetch_shopify_taxonomy()`:
- Runs on the **daily** scheduler and via dashboard → **Sync Categories** (`api.sync.refresh_shopify_taxonomy`).
- `taxonomy.categories()` (`_TAXONOMY_TREE_QUERY`) only ever returns Shopify's 26 ROOT (level-1) categories — confirmed live via introspection, not a flat connection over the whole tree despite supporting `first`/`after`. The real ~25,000-node tree is only reachable by walking each node's `childrenIds` recursively, so `fetch_shopify_taxonomy` does a BFS from those 26 roots, batch-fetching each next level via Shopify's bulk `nodes(ids:)` lookup (`_TAXONOMY_NODES_BY_ID_QUERY`, up to 250 ids/call) until every leaf is reached.
- The final `rebuild_tree("Shopify Category")` call (fixing every node's nested-set `lft`/`rgt`) is the real bottleneck for a tree this size — Frappe's default implementation does one UPDATE per node, not a bulk operation, so a full run can take many hours even though the BFS walk itself finishes in under two. Not a bug to "fix" by re-running; genuinely needs a faster custom rebuild (single-pass compute + bulk write) if this becomes a recurring pain point.
- A tree this size is very rarely 100% complete at any given moment — individual leaf nodes can be missing from a transient lock-wait save failure during the walk (retried 3x then logged and skipped, not retried again automatically). `ensure_shopify_category(full_name)` (below) and any GID-driven fetch code should always be prepared to fetch a single missing node live rather than assume the local tree is exhaustive.

`ensure_shopify_category(full_name)` creates/links a category node on demand during product import (from the product's `category.fullName`).

---

## Export — category on push

`_product_set_input` (`canonical.py`) reads the effective category via `listing_resolver.effective_category(listing, item)` — Listing's own `listing_category` override if set, else the Item's `sh_shopify_category`. It's a Link to the `Shopify Category` doctype, so the GID is read straight off that doc's own `shopify_category_id` field (`frappe.db.get_value("Shopify Category", category, "shopify_category_id")`) — **not** resolved via a live taxonomy search anymore (the old `_resolve_category_id`/`_TAXONOMY_SEARCH_QUERY` path is import-time only, used when first linking a category from Shopify's product data; it never runs on push).

---

## Relationship to Item Group

The category taxonomy is also the source for the Alaiy OS **Item Group hierarchy** on import — see [Products → Product type & Item Group](products.md). The category itself (`sh_shopify_category`) and the Item Group are kept as separate concepts: the category is the Shopify taxonomy node, the Item Group is the Alaiy OS reporting tree derived from it.

Products Shopify never assigned a category to fall back onto a flat, root-level Item Group named after the raw `productType` string instead of a real nested taxonomy path -- confirmed live to create a real mess (near-duplicate groups like "Backpack" vs "Backpacks", since `productType` is free text with no canonical form). Two one-off scripts (`scripts/audit_item_groups.py`, `scripts/suggest_category_mapping.py`) audit the current state and propose a real taxonomy mapping (via Shopify's own taxonomy search) for each messy group, for manual review before any migration -- neither script changes any product.

### Junk/standalone category nodes

A `Shopify Category` node can end up standalone (`parent_shopify_category` blank, no real Shopify GID) as an artifact of `ensure_shopify_category` having been called with just a bare leaf name somewhere, before the full path was known. `scripts/reparent_item_groups_from_shopify_taxonomy.py`'s matching logic (and `resolve_shopify_category_gid`, see below) treats a name match against ONE of these standalone junk nodes as ambiguous/no-match if a real nested node with the same leaf name also exists, rather than silently reusing the junk one — confirmed live this exact pattern created 2,778+ Items pointing at junk categories on commerce.os.alaiy.com, traced back to an incomplete taxonomy fetch at original import time.

### CSV bulk import: `sh_shopify_category_gid`

A bulk product-CSV import's `category_ID`/`category_id` column can mix three formats row to row: an exact `Shopify Category` doc name, a real Shopify taxonomy GID, or a bare leaf category name. Since `sh_shopify_category` is a Link field, Frappe's Data Import tool pre-validates a raw value against existing doc names BEFORE a row ever reaches any validate hook — a GID or bare name in that field fails import outright. `sh_shopify_category_gid` (a plain Data staging field on Item, no such pre-check) is where a CSV column should map instead; `resolve_shopify_category_gid` (`shopify/product/item_hooks.py`, wired as an Item validate hook) resolves whichever format it turns out to be into the real `sh_shopify_category` Link and clears the staging field. Throws a clear error only on genuine ambiguity (2+ real nested matches for a bare name); never fabricates a node.

The separate `alaiy_os_commerce` upload script (`upload_scripts/upload.py`) has its own, similar `_ensure_shopify_category`/`_resolve_categories` doing the same three-format resolution for its own `category_ID` CSV column, plus a live Shopify API fetch when a GID isn't synced locally yet (`_fetch_and_insert_gid`) rather than falling back to the raw GID string as an Item Group label.

### Ancestor Item Groups must stay `is_group=1`

Any code building a nested Item Group chain (`_ensure_item_group_path` in `masters.py`, or a one-off reparent script's own local ensure-helper) must force an **already-existing** ancestor group to `is_group=1` if it isn't already — reusing a group that happens to already exist (created earlier as some other product's real leaf category, `is_group=0`) without flipping that flag means a newly-nested child never shows up in the Desk tree at all, since a non-group node can't display children. Confirmed live: "Components" stayed a leaf after "Converters" was correctly reparented under it, hiding the fix from the tree view entirely.
