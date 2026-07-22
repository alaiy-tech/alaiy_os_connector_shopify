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
| `<external>_product_id` | Data, read-only | The marketplace's product id |
| `last_synced_at` | Datetime, read-only | Last successful push |

**Child — Listing Variant:** `item_variant` (Link Item), `is_enabled`,
`variant_price` (blank inherits), `<external>_variant_id`.
**Child — Listing Image:** `image`, `source` (Original / AI Enhanced),
`sort_order`, `generated_by_agent`.

Connector-specific extras live **only** on that connector's doctype (e.g. Amazon:
`bullet_point_1..5`, `specs`, `asin`, `product_type`; Shopify: `sh_shopify_status`).
They never leak into the shared contract.

---

## 3. The registry seam (how the agent finds the doctype)

Each connector declares its listing doctype in `connector_meta`:

```python
"listing_doctype": "Shopify Product Listing"   # Amazon: "Amazon Product Listing"
```

This upserts into **OS Connector Registry** (core `alaiy_os`). An enrichment
agent reads the registry, learns "for connector X, write into doctype Y", and
fills `listing_title` / `listing_description` / `images` there — **no
connector-specific code in the agent**. Requires the `listing_doctype` field to
exist on `OS Connector Registry` (core change, once).

---

## 4. Division of responsibility

```
Enrichment agent (shared, connector-agnostic)
  reads Item + raw data -> writes enriched title/desc/images into
  the connector's listing doctype (via registry pointer). Caches
  expensive content per (product, variant); never caches price/stock.

Each connector (owns its own push)
  reads its listing -> builds the marketplace payload -> submits.
  Shopify: productSet (forgiving, one call).
  Amazon:  SP-API + validate/reject/fix loop (strict), Excel fallback.
```

The agent orchestrates *what* to enrich; the connector owns *how* to submit.
Marketplace strictness (Amazon's reject-and-fix loop) stays inside that
connector — it never becomes the agent's or another connector's problem.

---

## 5. Rules that keep new connectors friction-free

1. **Never gate on Item fields.** The listing's `is_enabled` is the only switch.
   (Shopify's old `Item.sync_to_shopify` was removed for this reason.)
2. **Blank inherits, filled overrides** — everywhere, no exceptions.
3. **Price/stock resolved live**, never cached, even with cached enriched content.
4. **IDs owned by the listing** (or Item, if a connector defers that) — but one
   source of truth, never a drifting mirror.
5. **One listing per (product, connector)**, keyed to the template Item.
6. **Fingerprint/idempotency on resolved values** so an inherited Item change
   still triggers a re-push, and redelivered work is a no-op.
7. **Connector extras stay on the connector's doctype**, never in the shared set.

Follow these and a new connector = a new doctype matching the contract + its own
push method + a `listing_doctype` line. The agent, the Item model, and the UX
pattern all work unchanged.
