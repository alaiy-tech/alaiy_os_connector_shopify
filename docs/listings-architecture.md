# Marketplace Listings — cross-connector contract

Shared design so every connector (Shopify, Amazon, Myntra, …) exposes product
listings the **same way**, and one enrichment agent can serve all of them
without per-connector code. Shopify is the reference implementation
(`Shopify Product Listing`); Amazon/Myntra follow this contract.

---

## 1. The core rule

- **Item** = the marketplace-agnostic product (shared defaults: name, description,
  category, brand, variants). One per product, never connector-specific.
- **`<Connector> Product Listing`** = one record per product **per connector**,
  holding only what can differ on that marketplace.
- A blank listing field **inherits** the Item's value at push time. Filled =
  overrides just for that marketplace. No duplicated data.
- **Dynamic fields (price, stock) are resolved live** on every push — never
  frozen — even when enriched content is cached.

One Item → many listings (one per marketplace), each independently enabled and
independently overridable.

---

## 2. Shared field contract

Every connector's `<Connector> Product Listing` MUST have these, same names/meaning:

| Field | Type | Meaning |
|---|---|---|
| `item` | Link → Item (template), unique | The product this listing is for |
| `is_enabled` | Check (default 0) | **Sole** gate for whether the product is live on this marketplace |
| `listing_title` | Data | Blank → inherits `Item.item_name` |
| `listing_description` | Text Editor | Blank → inherits `Item.description` |
| `listing_price` | Currency | Blank → inherits the connector's price-list rate |
| `images` | Table → `<Connector> Listing Image` | Ordered; each row has `source` = Original / AI Enhanced + `generated_by_agent` |
| `variants` | Table → `<Connector> Listing Variant` | Per-variant `is_enabled` + `variant_price` (blank inherits) |
| `<external>_product_id` | Data, read-only from the desk UI, connector-writable | The marketplace's product id — the listing's own copy, set by the connector on push/import |
| `last_synced_at` | Datetime, read-only | Last successful push |

**Child — Listing Variant:** `item_variant` (Link Item), `is_enabled`,
`variant_price` (blank inherits), `<external>_variant_id`.
**Child — Listing Image:** `image`, `source` (Original / AI Enhanced),
`sort_order`, `generated_by_agent`.

Connector-specific extras live **only** on that connector's doctype (e.g. Amazon:
`bullet_point_1..5`, `specs`, `asin`, `product_type`; Shopify: `sh_shopify_status`).
They never leak into the shared contract.

---

## 3. Per-marketplace agents, not a shared registry seam

Superseded design note: an earlier plan had a single connector-agnostic
enrichment agent discover each connector's listing doctype via a
`listing_doctype` pointer on the core `OS Connector Registry`, so one agent
could write into any connector's listing doctype without connector-specific
code. That plan was dropped — each marketplace instead gets its own custom
agent (Shopify Agent, Amazon Agent, …), with its own doctype for
generated/draft listings that can carry validation errors and be reviewed
before pushing. The connector itself stays scoped to sync operations only
(pull/push/reconcile); anything beyond that — draft generation, AI
enrichment, review workflows — lives in the marketplace's own agent, not in
a shared cross-connector layer.

This doc's Section 2 field contract (Item vs Listing split, blank-inherits,
per-marketplace enable) still holds — that's a per-connector pattern worth
reusing, just not wired through a generic registry pointer anymore.

---

## 4. Division of responsibility

```
Marketplace agent (Shopify Agent, Amazon Agent, ... -- one per marketplace)
  reads Item + raw data -> writes enriched title/desc/images into
  that marketplace's own draft-listing doctype. Caches expensive
  content per (product, variant); never caches price/stock.

The connector (owns its own sync only)
  reads its listing -> builds the marketplace payload -> submits.
  Shopify: productSet (forgiving, one call).
  Amazon:  SP-API + validate/reject/fix loop (strict), Excel fallback.
```

Each marketplace's agent owns *what* to enrich for that marketplace; the
connector owns *how* to submit. Marketplace strictness (Amazon's
reject-and-fix loop) stays inside that connector — it never becomes another
connector's problem, and connectors stay scoped to credit/sync operations
only.

---

## 5. Rules that keep new connectors friction-free

1. **Never gate on Item fields.** The listing's `is_enabled` is the only switch.
   (Shopify's old `Item.sync_to_shopify` was removed for this reason.)
2. **Blank inherits, filled overrides** — everywhere, no exceptions.
3. **Price/stock resolved live**, never cached, even with cached enriched content.
4. **IDs owned by the listing.** Shopify's listing owns `sh_shopify_product_id`/
   `sh_shopify_variant_id` as real writable fields; the Item's own copy is kept
   only as a fallback (dual-written on every update) until it's eventually
   dropped — never a drifting mirror in the meantime.
5. **One listing per (product, connector)**, keyed to the template Item.
6. **Fingerprint/idempotency on resolved values** so an inherited Item change
   still triggers a re-push, and redelivered work is a no-op.
7. **Connector extras stay on the connector's doctype**, never in the shared set.

Follow these and a new connector = a new doctype matching the contract + its own
push method + a `listing_doctype` line. The agent, the Item model, and the UX
pattern all work unchanged.
