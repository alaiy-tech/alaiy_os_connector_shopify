# Alaiy OS Connector — Shopify: Orders Module Tech Spec

Status: Draft v2
App: `alaiy_os_connector_shopify` (+ one cross-app edit in `alaiy_os` core — see §2.3)
Owner: Sarthak
Last updated: 2026-07-12

Changelog v1 → v2: single-store confirmed, Payment Entry created directly (no Sales Invoice), full order-edit/amendment design added, Shopify Fulfillment Queue dropped entirely, GraphQL client now *replaces* the REST client (not alongside — affects product/inventory sync too), sidebar approach changed from runtime injection to a direct edit of `alaiy_os` core's sidebar config, logging expanded with a new low-level API Call Log doctype.

Awaiting: you mentioned attaching Shopify's official docs URL — nothing came through in the last message. Anywhere this spec says "verify against official docs," treat that as still open until you send the link; I'll fold in specifics once I have it.

---

## 1. Audit Findings (verified against current code) — unchanged from v1

### 1.1 API version is hardcoded-but-editable, must become a true constant

`shopify/client.py` currently does:

```python
api_version = (settings.sh_api_version or "2024-01").strip()
self.base_url = f"{shop_url}/admin/api/{api_version}"
```

`sh_api_version` is a required `Data` field on **Shopify Connector Settings** (default `"2024-01"`), fully editable by any System Manager. Wrong on two counts: it's merchant-facing when it shouldn't be, and it's pinned to a stale default.

**Fix:** remove `sh_api_version` from `shopify_connector_settings.json` (field + `field_order`); hardcode a module constant instead. Since the REST client is being fully replaced (§3.1), this constant now lives on the new GraphQL client:
```python
SHOPIFY_API_VERSION = "2026-07"
```
Add a patch (§10.6) to drop the column from any site that already set it.

### 1.2 `api/oauth.py` is dead code — confirmed, remove it

`exchange_code_for_token` in `api/oauth.py` is never referenced by any `.js`, hook, or page. The connector's real (only) auth flow is the client_credentials grant in `shopify/auth.py`. `oauth.py` implements the unrelated authorization-code grant, with no UI to trigger it.

**Fix:** delete `alaiy_os_connector_shopify/api/oauth.py` entirely.

### 1.3 HMAC verification is fail-open, not fail-closed — confirmed

`api/webhooks.py::handle_webhook` is `@frappe.whitelist(allow_guest=True)` — a public, unauthenticated endpoint by design. If `sh_webhook_secret` is blank, the entire HMAC-check block is skipped with no fallback: any POST with a plausible `X-Shopify-Topic` header gets dispatched as if it were a genuine Shopify webhook.

**Fix (fail closed):**
```python
webhook_secret = settings.get_password("sh_webhook_secret", raise_exception=False)
if not webhook_secret:
    frappe.log_error(title="Shopify webhook rejected: no secret configured")
    frappe.response.status_code = 401
    return {"ok": False, "reason": "webhook secret not configured"}

computed = hmac.new(webhook_secret.encode("utf-8"), raw_body, hashlib.sha256).digest()
expected = base64.b64encode(computed).decode("utf-8")
if not hmac_header or not hmac.compare_digest(expected, hmac_header):
    frappe.response.status_code = 401
    return {"ok": False, "reason": "HMAC validation failed"}
```
Make `sh_webhook_secret` `reqd: 1`; block webhook registration if it isn't set.

---

## 2. UI / Integration: `/desk/shopify` page

Settings page stays as-is (credentials, defaults, sync intervals). New: a dedicated Frappe **Page** at `/desk/shopify` for connector operations — manual triggers, historical sync controls, future order/inventory tooling.

### 2.1 Page doctype

`alaiy_os_connector_shopify/alaiy_os_connector_shopify/page/shopify/shopify.json`:
```json
{
  "doctype": "Page",
  "module": "Alaiy OS Connector Shopify",
  "name": "shopify",
  "page_name": "shopify",
  "standard": "Yes",
  "title": "Shopify",
  "roles": []
}
```

### 2.2 Page JS — boilerplate only for now

`shopify.js`:
```js
frappe.pages["shopify"].on_page_load = function (wrapper) {
  frappe.ui.make_app_page({
    parent: wrapper,
    title: "Shopify",
    single_column: true,
  });
  const body = $(wrapper).find(".layout-main-section");
  body.html(`
    <div class="shopify-ops-page">
      <p class="text-muted">Shopify connector operations. Manual triggers and historical sync controls land here.</p>
      <div class="shopify-sync-old-orders"></div>
    </div>
  `);
  render_sync_old_orders_section(body.find(".shopify-sync-old-orders"));
};

function render_sync_old_orders_section(container) {
  // Boilerplate only in this pass -- wired up fully in §8.
  container.html(`
    <div class="checkbox">
      <label><input type="checkbox" id="sh-sync-old-toggle"> Sync Old Shopify Orders</label>
    </div>
    <div id="sh-sync-old-fields" style="display:none;">
      <div class="form-group">
        <label>Since</label>
        <input type="date" id="sh-sync-since" class="form-control">
      </div>
      <div class="form-group">
        <label>Until</label>
        <input type="date" id="sh-sync-until" class="form-control">
      </div>
      <div class="form-group">
        <label>Sync Interval</label>
        <select id="sh-sync-interval" class="form-control">
          <option value="5">5 mins</option>
          <option value="15">15 mins</option>
          <option value="30">30 mins</option>
          <option value="60">1 hour</option>
          <option value="120">2 hours</option>
          <option value="180">3 hours</option>
        </select>
      </div>
    </div>
  `);
  container.find("#sh-sync-old-toggle").on("change", function () {
    container.find("#sh-sync-old-fields").toggle(this.checked);
  });
}
```

### 2.3 Sidebar: direct core config edit, not runtime injection

**Correction from v1:** the "OS" `Workspace Sidebar` is not something the connector should inject into at runtime after the fact. Its actual source of truth is a hardcoded constant inside the `alaiy_os` core app itself: `WORKSPACE_SIDEBAR_ITEMS` in `alaiy_os/constants/workspace.py`, consumed by `create_or_update_workspace_sidebar()` in `alaiy_os/setup/install.py`. Per your instruction, the Shopify button gets added there directly.

**This means this piece of work is a change to the `alaiy_os` core repo, not the `alaiy_os_connector_shopify` repo.** Flagging explicitly because it's a real architectural tradeoff worth being aware of: every connector that wants a sidebar button under this approach requires a core-app PR, rather than being self-contained in the connector's own install script (the way `alaiy_os_connector_competitor_sites` currently does it, via its own `_inject_sidebar()`). That's a precedent divergence — worth a one-line note to whoever reviews the `alaiy_os` PR so it's a deliberate choice, not an inconsistency someone "fixes" later by reverting to injection.

Two files need the matching edit, per the existing comment in `workspace.py` ("mirrors ALAIY_SIDEBAR_CONFIG in `public/constants/workspace_config.js` — keep both in sync"):

**`alaiy_os/constants/workspace.py`** — add to `WORKSPACE_SIDEBAR_ITEMS` (after an existing section, e.g. right before or after "Sales"):
```python
    # ── Connectors ─────────────────────────────────────────────────────────────
    {"type": "Section Break", "label": "Connectors",
        "icon": "plug",             "child": 0, "indent": 1},
    {"type": "Link", "link_type": "Page", "link_to": "shopify",
     "label": "Shopify",            "child": 1, "icon": "shopping-bag"},
```
(If a "Connectors" section break already exists or gets added by another connector later, reuse it rather than creating a duplicate section — check before adding.)

**`alaiy_os/public/constants/workspace_config.js`** — add a matching entry to `ALAIY_SIDEBAR_CONFIG`, using `type: "page"` (not `"link"`) so it's correctly excluded from the DocType-overlay-preview mechanism this file drives (`ALAIY_LABEL_TO_DOCTYPE` / `ALAIY_SKIP_LABELS` — a Page has no `doctype` to preview against, so it must land in the "skip overlay, just navigate" bucket alongside section headers and Workspace links):
```js
  { label: "Connectors", type: "section", icon: "plug" },
  { label: "Shopify", type: "page", icon: "shopping-bag" },
```

Both edits are additive and idempotent (list literals in source, not DB rows) — no patch/migration needed, they just ship with the next `alaiy_os` release the connector depends on.

The Settings doctype's own link (via `OS Connector Registry` → Connectors section in the *Settings* workspace sidebar, a separate mechanism in `_build_connector_sidebar_items()`) is untouched by this — this only adds the new `/desk/shopify` Page link to the main **"OS"** sidebar.

---

## 3. Orders Module — Design Principle

**ERPNext Sales Order remains the single authoritative business document.** `Shopify Order` is the external-channel representation and sync record; `Shopify Order Event`, `Shopify Order Sync Log`, and `Shopify API Call Log` (§7) exist purely for integration reliability, auditing, and retries.

```
Shopify Store (single store)
      │
      ▼
Shopify Order ──────────────► Sales Order ──► Payment Entry (direct, no Sales Invoice)
      │                            ├── Customer
      │                            └── Address (shipping / billing)
      ▼
Shopify Order Event ──► Webhook Processor
      │
      ▼
Shopify Order Sync Log ──► Retry / Audit
      │
      ▼
Shopify API Call Log ──► every raw GraphQL request/response, order-scoped or not
```

Not creating as doctypes: Shopify Order Items, Shopify Shipping Lines, Shopify Discounts, Shopify Taxes, Shopify Transactions, **or Shopify Fulfillment Queue** (see §3.3). These map onto native ERPNext structures (Sales Order Item, Sales Taxes and Charges, Additional Discount / Pricing Rule, Payment Entry, Delivery Note).

### 3.1 API surface: GraphQL client fully replaces the REST client

**Correction from v1:** this is not "GraphQL alongside REST" — the REST `ShopifyClient` in `shopify/client.py` is retired entirely and replaced by a `ShopifyGraphQLClient` that every module uses, including the ones outside this Orders spec's original scope:

| Current REST caller | File | Endpoints used | Must move to GraphQL |
|---|---|---|---|
| `order_sync.py` | orders | `orders.json` | `orders` connection query + `Order` mutations |
| `product_sync.py` | products | `products.json` (POST/PUT), `products/{id}.json` (PUT) | `productCreate` / `productUpdate` |
| `inventory_sync.py` | inventory | `inventory_levels/set.json`, `locations.json`, `variants/{id}.json` | `inventorySetQuantities` (or current equivalent), `locations` query, `productVariant` query |
| `webhooks.py` | webhook management | `POST /webhooks.json`, `GET/DELETE webhooks/{id}.json` | `webhookSubscriptionCreate` / `webhookSubscriptions` query / `webhookSubscriptionDelete` |
| `test_connection.py` | shop check | `shop.json` | `shop` query |

This is a bigger blast radius than "just Orders" — flagging it clearly so it's tracked as its own workstream even though it's delivered as one client swap. **Every module needs a regression pass after the swap**, not just Orders: product push, inventory push, and webhook registration all change their wire format even though their business logic shouldn't.

Practical shape:
- New `shopify/graphql_client.py` (replaces `shopify/client.py`) — POSTs to `{shop_url}/admin/api/{SHOPIFY_API_VERSION}/graphql.json`, reuses the existing client-credentials token refresh from `shopify/auth.py` unchanged (auth mechanism doesn't change, only the query/mutation transport does).
- Every existing call site (`product_sync.py`, `inventory_sync.py`, `webhooks.py`, `test_connection.py`, `order_sync.py`) gets its REST call rewritten as the equivalent GraphQL query/mutation.
- Order identity moves from numeric REST id to GraphQL GID (`gid://shopify/Order/12345`) as canonical — see §3.2.
- Exact GraphQL field/mutation names (`displayFinancialStatus`, `inventorySetQuantities` vs. older `inventoryAdjustQuantities`, order-edit mutation names, etc.) must be verified against Shopify's live 2026-07 GraphQL schema reference during implementation — **this is exactly where your official-docs link will matter most**, particularly for the Order Edit mutations in §5.

### 3.2 Dedup / idempotency rule — unchanged from v1

**Shopify Order GID (`gid://shopify/Order/<id>`) is the single source of truth for identity**, everywhere:
- `Shopify Order.shopify_order_gid` — unique index.
- Every webhook handler and every pull-sync path looks up by GID first; convert legacy numeric ids to GID form (`gid://shopify/Order/{id}`) before lookup if a payload only has the numeric id.
- Upsert, never insert-blindly — one upsert function used by webhooks, scheduled historical sync, and manual "Sync Orders" button alike. No separate code paths that could diverge and double-create.

### 3.3 Shopify Fulfillment Queue — dropped, not deferred

**Correction from v1:** this doctype is out of scope, full stop — not "Phase 2." Confirmed via grep that no code in the connector references it (`fulfillment_queue`, `Fulfillment Queue` — zero hits outside this spec document itself), so there's nothing to remove from the codebase. It's simply not part of this design anymore. If synchronous-fulfillment-push turns out to be insufficient later, that's a fresh design conversation, not a resurrection of this doctype.

---

## 4. New DocTypes

### 4.1 Shopify Order

The canonical record of the Shopify order. **Not** the Sales Order — this is connector metadata + a pointer to the Sales Order.

| Section | Field | Type | Notes |
|---|---|---|---|
| Identity | `shopify_order_id` | Data | numeric REST-style id, kept for reference/search |
| | `shopify_order_gid` | Data | `gid://shopify/Order/...` — **unique index**, canonical identity |
| | `order_name` | Data | e.g. `#1001` |
| | `order_number` | Int | |
| | `store` | Data | **single-store connector today** — just the store name/label, not a Link to any Store doctype. Filled once from settings at import time. |
| | `channel` | Data | Shopify sales channel name |
| | `status` | Select | open / closed / cancelled |
| | `financial_status` | Select | Shopify's `displayFinancialStatus` values |
| | `fulfillment_status` | Select | Shopify's `displayFulfillmentStatus` values |
| | `cancelled_at` | Datetime | |
| | `closed_at` | Datetime | |
| | `archived` | Check | also set true on `orders/delete` (§7) |
| Customer | `shopify_customer_id` | Data | |
| | `erp_customer` | Link (Customer) | |
| | `email` | Data | |
| | `phone` | Data | |
| Pricing | `currency` | Data | |
| | `presentment_currency` | Data | |
| | `total` | Currency | |
| | `subtotal` | Currency | |
| | `discount_total` | Currency | |
| | `shipping_total` | Currency | |
| | `tax_total` | Currency | |
| | `duties_total` | Currency | |
| | `total_outstanding` | Currency | |
| Sync | `erp_sales_order` | Link (Sales Order) | always points at the *current* Sales Order — updated to the amended doc's name after an amendment (§5) |
| | `sync_status` | Select | pending / synced / failed / skipped |
| | `imported_at` | Datetime | |
| | `last_synced_at` | Datetime | |
| | `last_webhook_at` | Datetime | |
| Edit tracking | `sh_last_edit_reason` | Small Text | internal-only note from Shopify's "Reason for edit" field (§5.4) — never customer-visible |
| | `sh_last_edited_at` | Datetime | |
| Raw | `json_payload` | Long Text / Code (JSON) | optional, full GraphQL response |
| | `webhook_payload` | Long Text / Code (JSON) | optional, last webhook body |

Autoname: `hash`.

### 4.2 Shopify Order Event

Every webhook received, unconditionally, written **before** dispatch/processing.

| Field | Type | Notes |
|---|---|---|
| `store` | Data | matches `Shopify Order.store` |
| `shopify_order` | Link (Shopify Order) | nullable — may arrive before the Shopify Order row exists |
| `webhook_topic` | Select | orders/create, orders/updated, orders/delete, orders/edited, orders/fulfilled, orders/paid, orders/cancelled, orders/partially_fulfilled |
| `received_at` | Datetime | |
| `processed_at` | Datetime | |
| `status` | Select | received / processing / processed / failed |
| `retry_count` | Int | |
| `error` | Small Text | |
| `payload_json` | Long Text / Code | raw body, stored regardless of downstream outcome |

### 4.3 Shopify Order Sync Log

Every sync attempt, per order.

| Field | Type | Notes |
|---|---|---|
| `shopify_order` | Link (Shopify Order) | |
| `direction` | Select | Shopify → ERP / ERP → Shopify |
| `operation` | Select | import / update / cancel / amend / payment_entry_create / delete |
| `status` | Select | started / finished / error |
| `started_at` / `finished_at` | Datetime | |
| `error` | Small Text | |
| `response` | Long Text | |

`operation` gained `amend` (order-edit → Sales Order amendment, §5) and `payment_entry_create` (§6) compared to v1, so every non-trivial action on an order is individually traceable here, not just create/update/cancel.

### 4.4 Shopify API Call Log (new in v2)

Low-level, doctype-agnostic log of every raw GraphQL request/response the connector makes — not just order-related. This exists because the client swap (§3.1) touches product, inventory, and webhook-management traffic too, and because you asked for logging of "each and every thing," which the order-scoped `Shopify Order Event` / `Shopify Order Sync Log` don't cover on their own (they only exist for orders).

| Field | Type | Notes |
|---|---|---|
| `operation_name` | Data | GraphQL operation/mutation name, e.g. `orderEditCommit` |
| `request_variables` | Long Text / Code (JSON) | redact `sh_client_secret`/token if ever accidentally included |
| `status_code` | Int | HTTP status |
| `duration_ms` | Int | |
| `graphql_errors` | Long Text | Shopify's own `errors[]` array if present, even on HTTP 200 (GraphQL can return 200 with an errors payload) |
| `response_snippet` | Long Text | truncated response body, enough to debug without storing arbitrarily large payloads |
| `triggered_by_doctype` | Data | e.g. `Shopify Order Sync Log`, nullable |
| `triggered_by_name` | Data | link-by-name to the row above, nullable (dynamic link, not a hard Link field, since this logger is shared across modules) |
| `created_at` | Datetime | |

Every call the new `ShopifyGraphQLClient` makes writes one row here, success or failure — this becomes the connector-wide "did we actually talk to Shopify and what happened" ledger, independent of which higher-level module initiated it.

---

## 5. Order Edits — Amendment Handling

Shopify's order-edit surface covers four things per your notes, and each maps to a specific ERPNext handling decision:

### 5.1 Products — add existing, add custom item, remove, adjust quantity

ERPNext Sales Orders are immutable once submitted (docstatus 1) for line-item changes. **Any structural line-item change from Shopify triggers ERPNext's standard Amendment flow**, not an in-place edit:
1. Fetch the full current order state via GraphQL (the `orders/edited` webhook payload itself may only carry a delta — confirm exact shape against official docs once shared; don't assume the webhook body alone is sufficient to rebuild full state).
2. Cancel the existing Sales Order (`so.cancel()`).
3. Create a new Sales Order via Frappe's amendment mechanism (`frappe.copy_doc` + `amended_from` set to the cancelled doc's name — standard Frappe pattern, same naming series with `-1`, `-2` suffixes), reflecting the new full line-item set (existing product added, custom item added as a non-stock/service Item or a designated "Custom Item" placeholder Item — needs one implementation decision: does a Shopify custom line item need a real Item master record created on the fly, or a single shared placeholder Item used for all custom items with the description carrying the specifics? Recommend the latter to avoid Item-master sprawl, but flagging as a call for the engineer/you to confirm during build).
4. Update `Shopify Order.erp_sales_order` to point at the new amended Sales Order name.
5. Log the amendment as its own `Shopify Order Sync Log` row (`operation = amend`).

**Restock on removal:** Shopify's edit payload indicates whether a removed line item was restocked (and to which location) or the merchant deselected restock. ERPNext-side, Sales Order itself carries no stock impact (stock only moves via Delivery Note / Stock Entry) — so:
- If no Delivery Note yet exists against the order, there's nothing to reconcile; the new amended Sales Order simply reflects fewer items, full stop.
- If a Delivery Note *already* exists for an item now being removed by a Shopify edit (order was partially fulfilled, then edited), that's a genuine edge case needing a Stock Entry (return) to reflect the restock in ERPNext — **flagging this as an open implementation question, not solving it here**, since it depends on warehouse/return policy specifics. Log it clearly (`Shopify Order Sync Log` with an explicit warning) rather than silently dropping it if it occurs.

### 5.2 Shipping fees

Non-structural relative to line items, but still a Sales Order Taxes and Charges row — also requires the amendment path if the Sales Order is already submitted (can't edit a submitted child table row either). Bundled into the same amendment transaction as line-item changes when both change together (which the `orders/edited` webhook will typically represent as a single combined event).

### 5.3 Discounts

Same treatment — manual per-item or order-level discounts become Sales Order Item `discount_amount`/`discount_percentage` or an order-level Additional Discount, rebuilt into the amended Sales Order alongside the line-item and shipping changes in the same amendment pass. Not a separate operation from §5.1/5.2 — one amendment per `orders/edited` event, covering whatever combination of products/shipping/discounts changed in that edit.

### 5.4 Reason for edit

Shopify's internal "reason for edit" note (never customer-visible) is stored as:
- `Shopify Order.sh_last_edit_reason` (overwritten each edit — latest reason)
- Also added as a Frappe **Comment** on the new amended Sales Order (`frappe.get_doc({"doctype": "Comment", ...})` or `doc.add_comment("Info", ...)`), so the reason survives per-amendment in the Sales Order's own timeline, not just the latest value on Shopify Order.

### 5.5 Non-structural updates don't trigger amendment

To be clear about the boundary: `orders/updated` events that only touch financial/fulfillment status, tags, or notes — with no line-item/shipping/discount change — update the Sales Order's custom fields and `Shopify Order` fields **in place**, no cancel/amend. Amendment is reserved specifically for genuine structural edits (`orders/edited`, or an `orders/updated` that turns out to include a structural diff — diff against the last-known snapshot in `Shopify Order.json_payload` to tell the difference).

---

## 6. Payment Entry — created directly, no Sales Invoice

**Correction from v1:** on `orders/paid` (financial_status becomes paid), the connector creates a **Payment Entry directly against the Sales Order**, bypassing Sales Invoice entirely. This means:
- The Sales Invoice custom fields proposed in v1 (`sh_shopify_payment_status`, `sh_shopify_transaction_id`, `sh_shopify_payment_gateway`) move to **Payment Entry** instead:

| Field | Type | Notes |
|---|---|---|
| `sh_shopify_payment_status` | Data | |
| `sh_shopify_transaction_id` | Data | Shopify transaction GID, dedup key for this Payment Entry (don't create a second Payment Entry for a transaction already recorded) |
| `sh_shopify_payment_gateway` | Data | |

- Dedup rule mirrors §3.2: look up `Payment Entry` by `sh_shopify_transaction_id` before creating a new one, so a duplicate `orders/paid` webhook (Shopify does redeliver) never double-records payment.
- Standard Payment Entry fields (`party_type = Customer`, `party`, `paid_amount`, `reference_no`/`reference_date` against the Sales Order) populate from the order's customer/total — exact reconciliation account/mode of payment mapping is a implementation detail to confirm against your Company's chart of accounts, not something this spec hardcodes.
- Logged via `Shopify Order Sync Log` with `operation = payment_entry_create`.

---

## 7. Webhooks

Topics (registered via GraphQL `webhookSubscriptionCreate`, replacing the REST 4-topic list):

```
orders/create
orders/updated                 (Shopify's real topic key — not "orders/update")
orders/delete
orders/edited
orders/fulfilled
orders/paid
orders/cancelled
orders/partially_fulfilled      (your list had "orders/partially_fullfilled" — typo, one "l" in the real topic)
```

| Topic | Action |
|---|---|
| `orders/create` | Create Shopify Order + Sales Order (+ Customer/Address if missing) |
| `orders/updated` | In-place update if non-structural (§5.5); amendment if the diff is structural |
| `orders/edited` | Always goes through the amendment path (§5) |
| `orders/cancelled` | Cancel the linked Sales Order |
| `orders/delete` | Cancel the Sales Order if submitted, mark `Shopify Order.archived = 1`; nothing hard-deleted in ERPNext |
| `orders/fulfilled` | Set fulfillment_status = fulfilled on Shopify Order + Sales Order custom field; Delivery Note linkage |
| `orders/partially_fulfilled` | Same, partial status |
| `orders/paid` | Set financial_status = paid; create Payment Entry (§6) |

Every one of the 8 handlers:
1. Writes a `Shopify Order Event` row first, unconditionally.
2. Runs its action through the shared GID-based upsert/amendment logic.
3. Writes a `Shopify Order Sync Log` row for the resulting operation.
4. Every underlying GraphQL call made along the way writes a `Shopify API Call