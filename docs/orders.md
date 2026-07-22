# Orders

Shopify orders sync into Alaiy OS as **Sales Orders**, with fulfillment → Delivery Note, payment → Sales Invoice + Payment Entry, and a set of outbound edits pushed back to Shopify. Code lives in the `shopify/order/` package; `order_sync.py` and `order_push.py` are compatibility shims re-exporting it.

The Sales Order is the single authoritative business document — Shopify has no separate "invoice" object, so the Sales Invoice is derived from the order's paid state.

---

## Custom fields

**Sales Order:** `sh_shopify_order_id` (indexed), `sh_shopify_order_name`, `sh_financial_status`, `sh_fulfillment_status`, `sh_shopify_notes` (bidirectional notes, allow-on-submit).
**Sales Order Item:** `sh_shopify_variant_id` (used for line-item reconciliation).
**Delivery Note:** `sh_shopify_fulfillment_id` (one Delivery Note per Shopify fulfillment; prevents duplicates).

Financial/Fulfillment status render as colored badges in the Sales Order list.

---

## Inbound: pull & webhooks (Shopify → Alaiy OS)

### Pull / import
`shopify/order/pull.py`:
- `run_orders_sync()` — routine pull, filtered by `sh_order_status_filter` + `financial_status:paid`.
- `import_existing_orders(date_from, date_to)` — dashboard **Import Orders** modal: all orders, or a date window. Pre-checks Shopify's order count vs already-linked to skip a no-op run.
- `run_full_import()` — full historical import (`status:any`), idempotent via the `sh_shopify_order_id` exists-check.
- `_run_orders_pull()` — shared paginated loop (`_ORDERS_QUERY`), owns the log transitions.

### Webhooks
`shopify/order/webhook.py::handle_order_webhook` routes by topic:

| Topic | Handler action |
|---|---|
| `orders/create`, `draft_orders/create` | `_upsert_order` (create Sales Order) |
| `orders/updated`, `orders/fulfilled`, `orders/paid`, `draft_orders/update` | `_update_order` (apply in place) |
| `orders/cancelled`, `orders/delete`, `draft_orders/delete` | `_cancel_order` |

`orders/edited` (line-item edits, delivered only via the legacy Notifications mechanism) also routes through the update path.

---

## Sales Order creation (`upsert.py`)

`_upsert_order` acquires a per-order MySQL advisory lock (`locking.py`, `GET_LOCK` shared between create + update paths) then `_upsert_order_unlocked`:
1. Ensures a default **Address Template** exists (`address.py::ensure_default_address_template`) — a fresh site without one otherwise crashes Sales Order validate.
2. Resolves/creates the **Customer** ([Customers](customers.md)) and the leaf **warehouse**.
3. Builds line items: each mapped to an Item by SKU → variant id → title (`_resolve_item_code`). A line with no catalog match becomes a **custom line item** on a shared "Shopify Custom Item" placeholder (`charges.py::build_custom_line_item`) rather than being dropped. Qty uses `current_quantity` when present (post-edit truth).
4. Appends **tax** (`tax.py::_append_tax_lines`), **shipping charge** (`charges.py::append_shipping_charge`), and **order discount** (`charges.py::apply_order_discount`).
5. Sets the **shipping address** (`address.py::sync_order_address`) as the SO's customer/shipping address.
6. Sets `flags.from_shopify_sync` (so doc_events don't echo back), inserts, and submits — unless it's a **draft order** (name starts `#D`), which stays draft.
7. Runs fulfillment → Delivery Note and, if the trigger is met, the Sales Invoice.

### Tax (`tax.py`)
Books each Shopify tax line onto the SO's Sales Taxes and Charges table. `taxes_included=false` (pre-tax prices) → an **Actual** charge added on top using Shopify's exact amount. `taxes_included=true` → an **On Net Total** percentage flagged `included_in_print_rate` so the total isn't inflated. Tax account self-heals (`_resolve_tax_account` → configured `sh_tax_account`, else an existing Tax leaf, else auto-create "Shopify Tax").

### Discounts & shipping (`charges.py`)
- Order-level `total_discounts` → **Additional Discount** on Net Total (per-line discounts already ride in each line's price).
- Shopify shipping line → Sales Taxes and Charges **Actual** row against a self-healed income account.

### Shipping address (`address.py`)
Creates/updates an Alaiy OS **Address** from the order's shipping (fallback billing) address, linked to the customer, set on the SO. Country self-heals to the company's when Shopify's value isn't a known Country record.

---

## Line-item edits (`line_items.py`)

For an `orders/edited` / `orders/updated` on an order not yet shipped:
- `_apply_line_item_diff` reconciles the SO's items against Shopify's current lines (match by variant id, then item code) — adds new, removes deleted, updates qty/rate.
- On a **submitted** SO (items table immutable), it uses Alaiy OS's amend mechanism: cancel + create an amended revision, retrying once on `TimestampMismatchError` (a race with our own outbound echo). A still-**draft** SO is edited in place.
- `_can_modify_order_items` blocks edits once the order is fulfilled/partially fulfilled.

---

## Fulfillment → Delivery Note (`delivery_notes.py`)

- `_sync_fulfillments` — one **Delivery Note per Shopify fulfillment id** (tagged `sh_shopify_fulfillment_id`, so redelivered webhooks and later partial shipments never duplicate). Each Delivery Note is trimmed to exactly the quantities that fulfillment shipped.
- `_create_delivery_note_if_needed` — full-order fallback for the pull path (which has no per-fulfillment breakdown).
- `_force_valid_warehouse` — re-resolves a real leaf warehouse onto every Delivery Note line, ignoring stale group-warehouse values baked into old orders.
- Runs elevated (`_as_administrator`) because the webhook context is Guest.

> Fulfilled-order Delivery Notes need stock. On a site whose Alaiy OS stock doesn't match Shopify's historical fulfillments, enable **Allow Negative Stock** (Stock Settings) or the Delivery Note submit fails with `NegativeStockError` (order still imports; the DN is skipped and logged).

---

## Sales Invoice + payment (`invoice.py`)

When an order qualifies (per `sh_invoice_trigger`: **Paid and Fulfilled** default — COD-correct — or **Paid**), `create_sales_invoice_if_paid`:
- Makes + submits a Sales Invoice from the submitted SO (idempotent — never a second invoice for an already-invoiced SO; non-stock; tax carried over).
- Self-heals accounts: Income Account + cost center on each line (`_fill_item_accounts` / `_resolve_income_account` / `_resolve_cost_center`), and books a full **Payment Entry** so the invoice reads **Paid** (`_mark_invoice_paid` / `_resolve_bank_cash_account`). `_resolve_cost_center` specifically checks `is_group` before using a configured cost center — a group cost center crashes any real transaction ("group cost centers cannot be used in transactions"), confirmed live; falls back through the Company default, then the same leaf-resolving self-heal (`_ensure_cost_center`) product import already uses.

**Reverse:** submitting a Sales Invoice in Alaiy OS for a Shopify order marks that order **Paid** on Shopify — `on_sales_invoice_submit` → `push_order_paid` (`orderMarkAsPaid`). Skipped for invoices we auto-created from an already-paid order (no ping-pong).

---

## Outbound edits (Alaiy OS → Shopify)

`doc_events.py` + `push.py` + `push_line_items.py`, driven by Sales Order doc_events:
- `on_sales_order_submit` → `push_order_create` — a Sales Order created in Alaiy OS (not from Shopify) with Shopify-linked items is created on Shopify (`orderCreate`).
- `on_sales_order_update` / `on_update_after_submit` → `push_order_update` — pushes status/notes; line-item add/remove goes through Shopify's **Order Editing API** (`_apply_shopify_line_item_changes`: begin → set qty 0 / add variant → commit), since `orderUpdate` has no line-item support.
- `on_sales_order_cancel` → `push_order_cancel` (`orderCancel`).
- Item add/remove detection uses a **before-save snapshot** (`snapshot.py`) cached at the `before_request` boundary — Alaiy OS's "Update Items" grid saves twice internally, so a doc.flags snapshot wouldn't survive.

All outbound pushes are skipped when `flags.from_shopify_sync` is set. A shared per-order lock serializes our push against the echoed webhook it triggers.

---

## Notes & status

- `sh_shopify_notes` syncs both directions with Shopify's order `note` field.
- `sh_financial_status` / `sh_fulfillment_status` track Shopify's `displayFinancialStatus` / `displayFulfillmentStatus`, shown as list badges.

---

## Not yet built (order operations)

Refunds/returns (→ Credit Note), restocking, tracking numbers, fulfillment cancel/split reflect-back (Alaiy OS → Shopify), manual customer notifications, and user-editable order **tags** (only an auto status tag is pushed) are not implemented.
