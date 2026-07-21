# Setup & Configuration

This connector is a standalone Frappe app that plugs into `alaiy_os`'s `OS Connector Registry`. It ships **disabled** and does nothing until an admin fills in credentials and checks **Enable Shopify** — that first enable is what provisions custom fields and registers webhooks.

---

## 1. Prerequisites

- A Frappe bench with `alaiy_os` installed (`required_apps = ["alaiy_os", "erpnext"]` in `hooks.py` — bench refuses to install without it).
- A Shopify store with a **custom app** created in the Shopify admin (Settings → Apps and sales channels → Develop apps), with Admin API access. The connector talks to the Shopify **Admin GraphQL API**, version `2026-07` (`shopify/graphql_client.py`, `SHOPIFY_API_VERSION`).

---

## 2. Shopify custom app credentials

From the Shopify custom app you need three secrets, entered into Shopify Connector Settings:

| Shopify admin value | Settings field |
|---|---|
| Client ID (API key) | `sh_client_id` |
| Client secret (API secret key) | `sh_client_secret` |
| Webhook signing secret | `sh_webhook_secret` |
| Store domain (`yourshop.myshopify.com`) | `sh_shop_url` |

The connector uses the **client-credentials grant** (`shopify/auth.py::get_client_credentials_token`) to mint an access token from the Client ID/Secret — you do not paste an access token by hand. The token and its expiry are stored (`sh_access_token`, `sh_token_refreshed_at`, `sh_token_expires_at`) and refreshed automatically (see [Architecture](architecture.md)).

---

## 3. Shopify Connector Settings — every field

`Shopify Connector Settings` is a **Single** DocType (one row site-wide). Fields, grouped by section:

### API Connection

| Field | Type | Purpose |
|---|---|---|
| `is_enabled` | Check | Master switch. 0→1 transition provisions custom fields + registers webhooks; 1→0 unregisters them. |
| `sh_shop_url` | Data (reqd) | Store domain. |
| `sh_client_id` | Data (reqd) | Custom-app Client ID. |
| `sh_client_secret` | Password (reqd) | Custom-app secret. |
| `sh_access_token` | Password (hidden) | Auto-minted; never hand-edited. |
| `sh_token_refreshed_at` | Datetime (RO) | When the token was last minted. |
| `sh_token_expires_at` | Datetime (RO) | Token expiry reported by Shopify. |
| `sh_webhook_secret` | Password (reqd) | Validates the `X-Shopify-Hmac-Sha256` header on inbound webhooks. |

### Alaiy OS Defaults

| Field | Type | Purpose |
|---|---|---|
| `sh_company` | Link Company (reqd) | Company for imported orders/items. |
| `sh_default_warehouse` | Link Warehouse (reqd) | Stock warehouse; validated to be a non-Group (leaf) warehouse. |
| `sh_customer_group` | Link Customer Group (reqd) | Group for auto-created customers. |
| `sh_default_territory` | Link Territory | Territory for auto-created customers; self-heals if blank. |
| `sh_selling_price_list` | Link Price List (reqd) | Price list product prices are read from / written to. |
| `sh_cost_center` | Link Cost Center (reqd) | Cost center on orders/invoices. |
| `sh_tax_account` | Link Account | Account order tax lines are booked against. **Blank → auto-resolved / created** ("Shopify Tax" under Duties and Taxes). |
| `sh_auto_sales_invoice` | Check (default 1) | Auto-create + submit a Sales Invoice when an order qualifies; submitting it also marks the Shopify order paid. |
| `sh_invoice_trigger` | Select (default "Paid and Fulfilled") | When to invoice: `Paid and Fulfilled` (COD-correct) or `Paid`. |

### Inventory Locations

| Field | Type | Purpose |
|---|---|---|
| `sh_location_map` | Table (Shopify Location Map) | Maps Alaiy OS Warehouse → Shopify Location for multi-location stock. Empty = single-location (Default Warehouse → primary location). See [Inventory](inventory.md). |

### Sync Settings

| Field | Type | Purpose |
|---|---|---|
| `sh_order_status_filter` | Select (default "Any") | Which orders the routine pull fetches: Open / Any / Closed / Cancelled. |
| `sh_inventory_sync_interval` | Select (default "30 min") | How often stock is pushed: Disabled / 5 / 15 / 30 / 60 min. |
| `sh_token_refresh_interval` | Select (default "12 hours") | Proactive token-refresh cadence: Disabled / 6h / 12h / 24h. |

> Product push fields (description, vendor, product type, images) always sync — there is no toggle for them. Earlier versions gated each behind a "Product Push Fields" setting; that section was removed since these should always be kept in sync.

---

## 4. Enabling — what the first enable does

Checking **Enable Shopify** (0→1) runs, via the settings controller's `validate`/`on_update`:

1. `setup/install.py::setup_custom_fields()` — provisions all custom fields on Item, Sales Order, Sales Order Item, Customer, Delivery Note, Sales Invoice (also re-run idempotently on every `bench migrate`).
2. Webhook registration (`shopify/webhooks.py::ensure_webhooks_registered`).
3. Mirrors the enabled flag onto the `OS Connector Registry` row so the workspace card reflects it.

`sync_connector_registry()` (on every `after_migrate`) upserts this connector's `connector_meta` into the registry and re-runs `alaiy_os`'s workspace/sidebar provisioning.

---

## 5. Custom fields provisioned

`setup/install.py::setup_custom_fields()` adds:

- **Item** — `sh_shopify_product_id`, `sh_shopify_variant_id`, `sync_to_shopify`, `sh_shopify_status`, `sh_shopify_tags`, `sh_shopify_category`, `sh_shopify_product_type`, `sh_seo_title`, `sh_seo_description`, `sh_shopify_collections`.
- **Sales Order** — `sh_shopify_order_id`, `sh_shopify_order_name`, `sh_financial_status`, `sh_fulfillment_status`, `sh_shopify_notes`.
- **Sales Order Item** — `sh_shopify_variant_id`.
- **Customer** — `sh_shopify_customer_id`.
- **Delivery Note** — `sh_shopify_fulfillment_id`.

Field-level detail is in each domain doc.

---

## 6. Webhooks

On enable (and self-healed every minute by the scheduler if any are missing), the connector registers these topics pointing at `/api/method/alaiy_os_connector_shopify.api.webhooks.handle_webhook`:

```
orders/create   orders/updated   orders/cancelled   orders/fulfilled
orders/paid     orders/delete    orders/edited
products/create products/update  products/delete
collections/create collections/update collections/delete
```

`handle_webhook` is `allow_guest=True` and **fails closed**: it rejects any request whose HMAC doesn't match either the app Client Secret or the Notifications-page webhook secret. Valid payloads are routed by `_dispatch()` onto the `short` queue. Detail in [Architecture](architecture.md).

---

## 7. Test Connection

The settings form's **Test Connection** button calls `alaiy_os.api.connectors.test_connector`, which wraps this app's `api/test_connection.py::test_connection()` — it validates the Shop URL + credentials, mints a test token, and updates the registry's `connection_status` / `last_tested_at` (flipping the connector card to "Connected").

---

## 8. The Shopify dashboard page

`/app/shopify` (`page/shopify/shopify.js`) is the operations console. Buttons:

| Button | Calls | Action |
|---|---|---|
| Import Orders from Shopify | `api.sync.import_existing_orders` | Modal: all orders or a date range. |
| Sync Inventory | `api.sync.trigger_inventory_push` | Push stock levels now. |
| Import Products from Shopify | `api.sync.trigger_product_import` | First run: wipes prior Shopify-linked items then imports fresh. Every run after: creates new products, updates changed ones, skips unchanged ones -- no wipe. See [Products](products.md). |
| Export Products to Shopify | `api.sync.trigger_product_export` | Push local (unlinked) products. |
| Sync Categories | `api.sync.refresh_shopify_taxonomy` | Refresh the taxonomy tree. |
| Sync Tags | `api.sync.refresh_shopify_tags` | Refresh the tag cache. |
| Sync Collections | `api.sync.refresh_shopify_collections` | Refresh the collection cache. |
| Sync Locations | `api.sync.refresh_shopify_locations` | Refresh the location cache. |

The page also renders the connector status card and the last 5 sync logs (`get_sync_status`), polling while a sync runs.

> **Cache syncs (Categories / Tags / Collections / Locations)** are occasional — run once after setup and again only when you add new ones on Shopify. Categories auto-refresh daily via the scheduler; the others are manual (or scheduled if you wire them).
