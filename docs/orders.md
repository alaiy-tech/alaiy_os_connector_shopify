# Orders

Shopify orders sync into Alaiy OS as **Sales Orders**, with fulfillment → Delivery Note, payment → Sales Invoice + Payment Entry, and a set of outbound edits pushed back to Shopify. Code lives in the `shopify/order/` package; `order_sync.py` and `order_push.py` are compatibility shims re-exporting it.

The Sales Order is the single authoritative business document — Shopify has no separate "invoice" object, so the Sales Invoice is derived from the order's paid state.

---

## Custom fields

**Sales Order:** `sh_shopify_order_id` (indexed), `sh_shopify_order_name`, `sh_financial_status`, `sh_fulfillment_status`, `sh_shopify_notes` (bidirectional notes, allow-on-submit).
**Sales Order Item:** `sh_shopify_variant_id` — a per-line snapshot captured straight from Shopify's line-item payload at pull/webhook time, used for line-item reconciliation. Distinct from the Item/Listing catalog id fields below: this one lives on the order line itself and isn't part of the Listing id-ownership model.
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
3. Builds line items: each mapped to an Item by SKU → variant id → title (`_resolve_item_code`; the variant-id lookup resolves via the Shopify Listing Variant row first, Item as fallback). A line with no catalog match becomes a **custom line item** on a shared "Shopify Custom Item" placeholder (`charges.py::build_custom_line_item`) rather than being dropped. `_merge_duplicate_item_rows` collapses multiple lines that land on the same item_code (e.g. two unmatched lines both falling on the shared placeholder) into one row before insert — qty summed, rate recomputed so the total stays exact — since Alaiy OS rejects the same item_code appearing twice on one order. Qty uses `current_quantity` when present (post-edit truth).
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
- `_sync_tracking` — carries `sh_tracking_number` / `sh_tracking_company` / `sh_tracking_url` from the `fulfillments/create`/`fulfillments/update` webhook payload onto the matching Delivery Note.
- `_force_valid_warehouse` — re-resolves a real leaf warehouse onto every Delivery Note line, ignoring stale group-warehouse values baked into old orders.
- `_fill_expense_accounts` — self-heals a valid Expense Account on any line missing one.
- Runs elevated (`_as_administrator`) because the webhook context is Guest. Both creation paths set `flags.from_shopify_sync` so the outbound push below never tries to re-push a fulfillment Shopify already told us about.

> Fulfilled-order Delivery Notes need stock. On a site whose Alaiy OS stock doesn't match Shopify's historical fulfillments, enable **Allow Negative Stock** (Stock Settings) or the Delivery Note submit fails with `NegativeStockError` (order still imports; the DN is skipped and logged).

---

## Delivery Note → Fulfillment, outbound (`fulfillment_push.py`)

Gated by `Shopify Connector Settings.sh_fulfillment_sync_direction` — **"Shopify → Alaiy OS (default)"** leaves this section's behavior fully inert; existing installs see no change. Switching to **"Alaiy OS → Shopify (two-way)"** activates it for sites where the warehouse ships out of Alaiy OS itself (e.g. scanning items on a Delivery Note against a Sales Order).

- `on_delivery_note_submit` — submitting a Delivery Note (not one mirrored in from Shopify, and not already linked) enqueues `push_delivery_note_fulfillment_job`, which matches the DN's items to the Shopify order's still-open `fulfillmentOrder` line items (by variant id, SKU as fallback) and calls `fulfillmentCreate` with exactly those quantities — a partial shipment only fulfills what it actually shipped, not everything Shopify has left open. The resulting Shopify fulfillment id is written back onto `sh_shopify_fulfillment_id`, the same field the inbound path checks — so the `orders/fulfilled` webhook this triggers on Shopify's side is recognized as already-accounted-for and never creates a duplicate Delivery Note.
- Reuses the existing `sh_tracking_number` / `sh_tracking_company` fields (previously inbound-only, written by `_sync_tracking`) as an input in two-way mode: set before or after submit, carried into the `fulfillmentCreate` call if set before submit.
- `on_delivery_note_update_after_submit` — editing `sh_tracking_number`/`sh_tracking_company` on a Delivery Note that already has a linked fulfillment pushes `fulfillmentTrackingInfoUpdate`.
- `on_delivery_note_cancel` — cancelling a Delivery Note that this app pushed out (never one mirrored in) cancels the matching Shopify fulfillment via `fulfillmentCancel`. Independent of the current setting value — a fulfillment already pushed stays cancellable even if the setting is later switched back to inbound-only.
- `push_fulfillment_for_delivery_note` — a separate whitelisted entry point, independent of the setting, for carrier connectors (e.g. FedEx's `create_shipment_for_delivery_note`) to call explicitly once they have a real tracking number. An explicit call like this is the caller opting in directly, not the generic submit hook.

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

## Refunds/returns (`returns.py`)

Shopify has no separate "return" resource — a refund is the return record.
`refunds/create` → `handle_refund_webhook` → `_process_refund`:
1. Idempotency gate: skips entirely if either a Delivery Note **or** a Sales Invoice already carries this `sh_shopify_refund_id`. Both are checked because a no-restock refund creates no Delivery Note at all, so checking only that would let a redelivered webhook duplicate the Credit Note.
2. Resolves the Sales Order via `get_active_sales_order`; skips if not found/not submitted.
3. Maps each `refund_line_items[].line_item` to an item code (`_resolve_item_code`, same SKU → variant id → title chain as inbound order creation; `variant_id` is legitimately null on some lines, which the fallback chain handles). An unmatchable line is logged, not silently dropped.
4. Splits the refunded quantities into **two** maps by `restock_type`:
   - every line counts toward the **credit** quantity (money always comes back),
   - only `return` / `legacy_restock` lines count toward the **restock** quantity. `no_restock` (damaged, written off) and `cancel` (never shipped, so it never left stock) must not create a positive stock movement — otherwise the connector invents inventory that doesn't physically exist.
5. **Sales Return**: `make_return_doc("Delivery Note", ...)`, trimmed to the restock quantities (`_trim_return_items`), tagged `sh_shopify_refund_id`. Lands in **Return Warehouse** (`sh_return_warehouse`) if configured, else Default Warehouse — the connector doesn't decide what happens to the item after that; a downstream quality check or supplier-portal routing owns that decision.
6. **Credit Note**: `make_return_doc("Sales Invoice", ...)`, trimmed to the credit quantities, same tag. `update_stock=0` — stock already moved via the Sales Return.
7. If Shopify's refund `transactions` carry a **successful** `kind: "refund"` amount, books a refund Payment Entry against the Credit Note (mirrors `invoice.py`'s `_mark_invoice_paid`, reversed direction). If nothing has settled yet, the Credit Note still stands but is deliberately left **unpaid** — see below.

### Three separate Shopify state machines

This module is driven by the **refund**, not by Shopify's Return object. Shopify models three things independently, and only the middle one is handled here:

| | What it is | Handled? |
|---|---|---|
| Return lifecycle | `returns/request`, `returns/approve`, `returns/decline`, `returns/cancel`, `returns/update`, `returns/process`, `returns/close`, `returns/reopen` — the physical goods: requested, approved, received. GraphQL Admin API only. | **No** |
| Refund | `refunds/create` — the financial reversal, carrying refunded line items + restock instructions. | Yes |
| Money settlement | each refund's `OrderTransaction` status: `pending` / `processing` / `success` / `failure`. | Partly — see below |

**Consequence:** a return that is requested, approved, and physically received but **not yet refunded** produces nothing in Alaiy OS. For a merchant who inspects goods before refunding, the warehouse sees the box arrive with no corresponding record until the refund is issued on Shopify. Closing that gap means subscribing to `returns/process` (and probably `returns/approve`), which needs a decision about what an approved-but-unrefunded return should create — a draft Sales Return? a flag on the order? — so it's deliberately not wired up by default.

**Money settlement:** `refunds/create` fires *independent of money movement* — a Refund existing does not mean the customer has been paid. Only `status: "success"` refund transactions are counted. When none have settled, the Credit Note is created (the sale really is reversed) but no Payment Entry is booked, and the situation is logged with every transaction's kind/status. Shopify does **not** re-fire `refunds/create` when a pending transaction later succeeds, so nothing revisits this automatically — the invoice sitting visibly unpaid in Accounts Receivable is the intended signal, rather than it silently looking settled.

**On double-restocking:** Shopify adjusts its own inventory for `return`/`cancel` lines (that's what `refund_line_items[].location_id` is for). That is *not* a reason to skip our Sales Return — it's the same physical unit counted independently in two systems. Alaiy OS is the stock source of truth and the scheduled inventory push (`inventory_sync.py`) overwrites Shopify's number with ours, so our count must include the returned unit or the next push would wrongly tell Shopify the return never happened.

**Source document selection.** Both `make_return_doc` calls pick a document that actually carries one of the refunded items (`_source_delivery_note` / `_source_sales_invoice`), most recent first — never just the order's first Delivery Note or Invoice. A partially shipped or per-shipment invoiced order has several, and returning against the wrong one maps lines the refund never touched, which the trim then drops — a silently empty return. The invoice lookup also skips existing return invoices.

**Quantity trimming** treats the refunded quantities as a budget drawn down across rows, not a per-row cap. Two rows can share an `item_code` (the same SKU on two order lines, or two unmatched Shopify lines both resolving to the shared "Shopify Custom Item" placeholder), and capping each independently against the same total would return double. `make_return_doc` has already netted off earlier returns, so a refund for more than what's left lands short rather than going negative.

**Refund total vs Credit Note total.** The Payment Entry settles the Credit Note's own outstanding amount, not Shopify's refund figure. Shopify's refund can legitimately include refunded shipping, duties, or a manual adjustment — none of which are line items on the trimmed Credit Note — and forcing that larger total onto the invoice is an ERPNext over-allocation error. Any difference is logged for a human to book separately rather than guessed at.

No Delivery Note yet (nothing shipped) → no Sales Return. No Sales Invoice yet (not invoiced) → no Credit Note. Either can happen independently; a refund on an unshipped/unpaid order just returns the reserved qty via the Sales Order itself.

## Not yet built (order operations)

Restocking-to-a-specific-warehouse (returns land in whatever warehouse the original Delivery Note used — the sellable/damaged split, flow.txt's Return Warehouse → Rejected Goods step, is a deliberate non-goal since that decision belongs to whoever inspects the goods), fulfillment **split** reflect-back (a single Shopify fulfillment order split across multiple Delivery Notes maps back to more than one `sh_shopify_fulfillment_id`, only the first is currently linked/trackable), manual customer notifications, and user-editable order **tags** (only an auto status tag is pushed) are not implemented. Tracking number sync and fulfillment cancel (both directions) are covered above.
