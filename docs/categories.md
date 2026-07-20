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
- Pages the full taxonomy (`_TAXONOMY_TREE_QUERY`, 250/page — fully paginated; an earlier version capped at the first 250, now fixed) and builds/updates the `Shopify Category` tree by `level` / `fullName`.

`ensure_shopify_category(full_name)` creates/links a category node on demand during product import (from the product's `category.fullName`).

---

## Export — category on push

When a product with `sh_shopify_category` is pushed, `_resolve_category_id(client, category_name)` (`product/queries.py::_TAXONOMY_SEARCH_QUERY`) resolves the category's Shopify GID by searching the taxonomy, and the `productSet` payload sets `category` to that GID.

---

## Relationship to Item Group

The category taxonomy is also the source for the Alaiy OS **Item Group hierarchy** on import — see [Products → Product type & Item Group](products.md). The category itself (`sh_shopify_category`) and the Item Group are kept as separate concepts: the category is the Shopify taxonomy node, the Item Group is the Alaiy OS reporting tree derived from it.
