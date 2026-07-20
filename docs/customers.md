# Customers

Customers are created/matched as a side effect of order import — there is no standalone customer sync. Code: `shopify/order/customer.py` and `shopify/order/address.py`.

---

## Custom field

**Customer:** `sh_shopify_customer_id` (Data, indexed) — the Shopify customer id, the dedup key.

---

## Create / match (`_get_or_create_customer`)

On order import, from the order's `customer` block:
1. **Match** by `sh_shopify_customer_id` first — if a Customer already carries it, reuse.
2. Otherwise build a name: `first_name + last_name` when both are present and last isn't the literal "None" (Shopify sends `first_name`/`last_name` as explicit `null` fairly often — handled so `.strip()` never crashes the webhook). Falls back to `first_name`, then email, then `Shopify <id>`.
3. If a Customer with that exact name exists, reuse it; else create one with `customer_group = sh_customer_group`, `territory = _resolve_default_territory(settings)`, and the Shopify id stored.

### Territory (`_resolve_default_territory`)
Self-heals a missing Territory master: configured `sh_default_territory` → "All Territories" if present → any existing Territory → create a root "All Territories" as a last resort. Order import never hard-fails on a missing Territory.

---

## Address (`address.py`)

`sync_order_address(order, customer_name)` creates/updates an Alaiy OS **Address** (type Shipping) from the order's shipping address (fallback billing), links it to the Customer, and returns its name for the Sales Order's `customer_address` / `shipping_address_name`.

- Country is a mandatory link — uses Shopify's country only if it's a real Country record, else the company's country (fallback "India").
- `ensure_default_address_template()` guarantees a default Address Template exists first — without one, Alaiy OS throws while rendering any address (and any Sales Order that references it), so this is called at the start of every order upsert.

> Scope: inbound (Shopify → Alaiy OS). Customer/address edits are not pushed back to Shopify.
