# Architecture & Sync Engine

The plumbing shared across every domain: how the connector authenticates, talks GraphQL, avoids redundant/duplicate writes, retries failures, logs, and receives webhooks.

---

## Connector pattern

A standalone Frappe app registered into `alaiy_os`'s `OS Connector Registry` on every `after_migrate` (`setup/install.py::sync_connector_registry`, from `connector_meta.py`). Core calls this app's methods via dotted paths in the registry; it holds no Shopify-specific code. Settings live in the `Shopify Connector Settings` Single DocType; sync history in `Shopify Sync Log`.

---

## Auth & GraphQL client

`shopify/auth.py`:
- `get_client_credentials_token(shop_url, client_id, client_secret)` — mints an access token via the **client-credentials grant**.
- `refresh_and_store_access_token()` — mints a fresh token and persists `sh_access_token` / `sh_token_refreshed_at` / `sh_token_expires_at`.

`shopify/graphql_client.py` — `ShopifyGraphQLClient`:
- POSTs to `{shop_url}/admin/api/{SHOPIFY_API_VERSION}/graphql.json` (`SHOPIFY_API_VERSION = "2026-07"`), timeout `(10, 60)`.
- `execute()` — runs a query/mutation, auto-refreshes the token on 401, and retries once on a `THROTTLED` error after waiting the throttle window (`_is_throttled` / `_throttle_wait_seconds`).
- `execute_paginated(query, variables, connection_path)` — cursor-pagination generator yielding each page's `edges[].node`, following `pageInfo.hasNextPage` / `endCursor`.
- `new_idempotency_key()` — UUID for the `@idempotent` directive on inventory mutations.

Token refresh is also proactive: `sync_jobs._maybe_refresh_token` refreshes on the `sh_token_refresh_interval` cadence.

---

## Change detection & identity

`shopify/sync_engine/`:
- **`fingerprint.py`** — `fingerprint(canonical)` = SHA-256 of a normalized canonical dict (money/timestamps/booleans normalized). Every outbound push builds a canonical, compares its fingerprint to the last successful one, and **skips the API call when unchanged**.
- **`entities.py`** — `Shopify Synced Entity` mapping (Alaiy OS doc ↔ Shopify external id + last fingerprint). `get_by_erpnext` / `get_by_external_id` / `get_or_new` / `save`.
- Per-record **locks**: products lock the template document; orders use a MySQL `GET_LOCK` advisory lock shared between the create and update paths — preventing duplicate products/orders under the event cascades Frappe fires on save.
- **`from_shopify_sync` flag** — set on every inbound save so outbound doc_events don't echo it back (no ping-pong).

---

## Retry queue

`shopify/sync_engine/retry_queue.py` + `Shopify Retry Queue Entry`:
- `enqueue(direction, entity_type, payload, ...)` — records a failed push/pull.
- `record_failure` (increments `attempt_count`, stores `error`), `record_success`, `get_due_entries(limit=50)`.

---

## Sync logging

`shopify/sync_guard.py` + `Shopify Sync Log` (autoname `SH-SYNC-.YYYY.-.MM.-.DD.-.######`):
- `has_active_sync(sync_type)` — prevents concurrent runs of the same type.
- `load_or_create_log` — creates the log row at enqueue time (so the UI shows "queued" instantly).
- `append_log` / `close_log` — progress lines + final status/counts.
- `sync_type` values: `orders`, `inventory`, `products`, `product_export`, `collections`, `locations`, `webhook`. Statuses: queued → running → success / failed / skipped.

---

## Scheduler

`hooks.py` `scheduler_events`:
- **cron `* * * * *`** → `sync_jobs.check_and_enqueue` — every minute: ensures webhooks are registered (`_maybe_ensure_webhooks`), refreshes the token if due (`_maybe_refresh_token`), and enqueues an inventory push if the interval elapsed and none is running (`_maybe_enqueue_inventory`), with a 30-minute staleness guard so a crashed job can't block the schedule forever.
- **hourly** → `product_sync.push_changed_items_only`.
- **daily** → `product_sync.fetch_shopify_taxonomy`.

---

## Webhooks

`api/webhooks.py::handle_webhook` (`allow_guest=True`):
- **Fails closed** — rejects (401) any request whose `X-Shopify-Hmac-Sha256` matches neither the app Client Secret nor the Notifications-page webhook secret. Both are accepted because `orders/edited` is only delivered via the legacy Notifications mechanism (its own secret), while GraphQL-registered topics are signed with the Client Secret.
- Valid payloads → `_dispatch(topic, payload)` enqueues the right handler on the `short` queue: order topics → `handle_order_webhook`, product topics → `handle_product_webhook`, collection topics → `handle_collection_webhook`.

`shopify/webhooks.py`:
- `WEBHOOK_TOPICS` — the registered topic list.
- `ensure_webhooks_registered()` — reads existing subscriptions, creates only the missing ones (self-healing; called on enable and every minute by the scheduler).
- `unregister_webhooks()` — removes this site's subscriptions on disable.
- `_topic_to_graphql_enum` — `orders/create` → `ORDERS_CREATE`, etc.

---

## API endpoints (`api/`)

| Method | Purpose |
|---|---|
| `sync.trigger_orders_sync` | Enqueue routine order pull. |
| `sync.import_existing_orders` | Import all / date-range orders. |
| `sync.trigger_inventory_push` | Push stock now. |
| `sync.trigger_product_import` | Product import/sync: create new, update changed, skip unchanged (4h). Wipes only on first run. |
| `sync.trigger_product_export` | Bulk export local products (30m). |
| `sync.get_sync_status` | Last 5 logs (feeds the dashboard + connector card). |
| `sync.refresh_shopify_taxonomy` / `_tags` / `_collections` / `_locations` | Refresh each cache. |
| `test_connection.test_connection` | Validate credentials, mint a test token. |
| `webhooks.handle_webhook` | Guest webhook endpoint (HMAC-validated). |

Whitelisted trigger endpoints create a Sync Log row then enqueue on the `long` queue — nothing sync-heavy runs inside a web request.

---

## Currency

Product prices follow the configured `sh_selling_price_list`; currency is inherited from that price list. The synthetic compare-at / cost price lists inherit the same currency, falling back to `INR` only if the base list has no currency set (`product/pricing.py`).
