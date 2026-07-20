# Tags

Bidirectional sync of Shopify product tags, presented in Alaiy OS as a **multi-select of real cached tags** (no free typing). Code: `shopify/product/tags.py`.

---

## DocTypes

| DocType | Kind | Key fields |
|---|---|---|
| `Shopify Tag` | Cache (autoname `field:tag_name`, unique) | `tag_name`. |
| `Item Shopify Tag` | Child table | `shopify_tag` (Link → Shopify Tag); backs `Item.sh_shopify_tags`. |

`Item.sh_shopify_tags` is a **Table MultiSelect** (options: Item Shopify Tag).

---

## Import — cache the tag list

`sync_shopify_tags()` (dashboard → **Sync Tags**, or `api.sync.refresh_shopify_tags`) pages `productTags` (250/page) and upserts each into a `Shopify Tag` doc — the master list the multi-select picks from, so users choose real Shopify tags rather than inventing new ones.

Per-product tags arrive with the product: `_normalize_tags` splits both shapes (GraphQL list vs the comma-joined webhook string), and `_set_item_tags` sets the Item's `sh_shopify_tags`, self-healing any `Shopify Tag` master not yet cached.

---

## Export

On product push, `_item_tags(item)` reads the plain tag-name list from the Table MultiSelect and includes it in the `productSet` payload (and in the fingerprint, so tag changes re-push).

---

## Variant inheritance

`copy_template_tags_to_variant` (Item `validate` hook) copies the template's Item-Shopify-Tag rows onto each variant — Table-MultiSelect child data can't use `fetch_from`, so it's copied explicitly. `read_only_depends_on` keeps the grid non-editable on variants.
