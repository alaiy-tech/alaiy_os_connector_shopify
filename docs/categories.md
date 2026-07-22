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
- `taxonomy.categories()` (`_TAXONOMY_TREE_QUERY`) only ever returns Shopify's 26 ROOT (level-1) categories — confirmed live via introspection, not a flat connection over the whole tree despite supporting `first`/`after`. The real several-thousand-node tree is only reachable by walking each node's `childrenIds` recursively, so `fetch_shopify_taxonomy` does a BFS from those 26 roots, batch-fetching each next level via Shopify's bulk `nodes(ids:)` lookup (`_TAXONOMY_NODES_BY_ID_QUERY`, up to 250 ids/call) until every leaf is reached. Confirmed live: went from 165 cached categories (roots + a stale partial fetch) to 2650 after this fix.

`ensure_shopify_category(full_name)` creates/links a category node on demand during product import (from the product's `category.fullName`).

---

## Export — category on push

When a product with `sh_shopify_category` is pushed, `_resolve_category_id(client, category_name)` (`product/queries.py::_TAXONOMY_SEARCH_QUERY`) resolves the category's Shopify GID by searching the taxonomy, and the `productSet` payload sets `category` to that GID.

---

## Relationship to Item Group

The category taxonomy is also the source for the Alaiy OS **Item Group hierarchy** on import — see [Products → Product type & Item Group](products.md). The category itself (`sh_shopify_category`) and the Item Group are kept as separate concepts: the category is the Shopify taxonomy node, the Item Group is the Alaiy OS reporting tree derived from it.

Products Shopify never assigned a category to fall back onto a flat, root-level Item Group named after the raw `productType` string instead of a real nested taxonomy path -- confirmed live to create a real mess (near-duplicate groups like "Backpack" vs "Backpacks", since `productType` is free text with no canonical form). Two one-off scripts (`scripts/audit_item_groups.py`, `scripts/suggest_category_mapping.py`) audit the current state and propose a real taxonomy mapping (via Shopify's own taxonomy search) for each messy group, for manual review before any migration -- neither script changes any product.
