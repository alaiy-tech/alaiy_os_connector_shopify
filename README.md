# Alaiy OS Connector — Shopify

A [Frappe](https://frappeframework.com) app that bidirectionally syncs **Alaiy OS** with a **Shopify** store — products, orders, inventory, customers, collections, tags, categories, and sales channels — over the Shopify **Admin GraphQL API** (version `2026-07`).

It is built on the Alaiy OS connector pattern: a self-contained Frappe app that registers itself into `alaiy_os`'s **`OS Connector Registry`** on every `bench migrate`, owns its own settings (a Single DocType with credentials + mapping defaults), its own sync logic, and its own log history. Core `alaiy_os` never contains Shopify-specific code — it only calls this app's methods through dotted paths stored in the registry.

## What it does

| Domain | Direction | Summary |
|---|---|---|
| **Products** | Shopify ⇄ Alaiy OS | Full import + push; variants, pricing (price/compare-at/cost), images, SEO, product type, Active/Draft status, archive-on-disable, item-group hierarchy. |
| **Collections** | Shopify ⇄ Alaiy OS | Manual collection cache + CRUD push, product membership sync, product grid + count on the form. |
| **Tags** | Shopify ⇄ Alaiy OS | Cached tag list, Table-MultiSelect on Item, bidirectional sync, template→variant inheritance. |
| **Categories** | Shopify → Alaiy OS | Standard Product Taxonomy tree cached as a doctype; category push on export via taxonomy search. |
| **Sales Channels** | Shopify ⇄ Alaiy OS | Publications shown per collection; click-to-publish / unpublish control. |
| **Orders** | Shopify ⇄ Alaiy OS | Order pull + webhooks → Sales Order; line-item add/remove/amend, tax, discounts, shipping charge, shipping address, custom line items, fulfillment → Delivery Note, auto Sales Invoice + payment, cancel, notes, status badges. |
| **Inventory** | Alaiy OS → Shopify | Stock-level push, single or multi-location (warehouse → Shopify location map). |
| **Customers** | Shopify → Alaiy OS | Customer + Territory + Address creation/matching from order data. |
| **Sync engine** | — | GraphQL client (token, pagination, throttle), fingerprint dedup, per-record locks, retry queue, sync logs, HMAC webhooks, scheduler. |

All writes to Shopify are guarded by a **content fingerprint** so an unchanged record never re-hits the API, and by **per-record locks** so concurrent saves never double-create. Inbound saves are flagged `from_shopify_sync` so they never echo straight back to Shopify.

## Installation

Requires a Frappe/Alaiy OS bench with `alaiy_os` already installed (`required_apps = ["alaiy_os", "erpnext"]`).

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app alaiy_os_connector_shopify $URL_OF_THIS_REPO --branch main
bench install-app alaiy_os_connector_shopify
bench --site <site> migrate
bench build --app alaiy_os_connector_shopify
```

## Quick start

1. Open **Shopify Connector Settings**, fill in the Shop URL + custom-app Client ID / Secret / Webhook Secret, and the Alaiy OS defaults (Company, Warehouse, Price List, Customer Group, Cost Center).
2. Check **Enable Shopify** — this provisions custom fields and registers webhooks.
3. Use the **Shopify** dashboard page (`/app/shopify`) to run the initial syncs: Sync Categories, Sync Tags, Sync Collections, Sync Locations, Import Products, Import Orders.

Full field-by-field configuration is in [docs/setup.md](docs/setup.md).

## Documentation

Detailed, per-domain documentation lives in [`docs/`](docs/):

- **[Setup & Configuration](docs/setup.md)** — Shopify custom app, every settings field, enabling, webhook registration, Test Connection, sync intervals, the dashboard page.
- **[Products](docs/products.md)** — import, export, variants, pricing, media, SEO, product type, status, item-group hierarchy, product webhooks.
- **[Collections](docs/collections.md)** — collection cache, CRUD push, membership sync, form product grid.
- **[Tags](docs/tags.md)** — tag cache, Item multi-select, bidirectional sync, variant inheritance.
- **[Categories](docs/categories.md)** — Standard Product Taxonomy tree, category assignment + push.
- **[Sales Channels](docs/sales-channels.md)** — Publications display + publish/unpublish control.
- **[Orders](docs/orders.md)** — order pull/import, webhooks, line items, tax, discounts, shipping, addresses, custom items, fulfillment → Delivery Note, Sales Invoice + payment, cancellation, notes.
- **[Customers](docs/customers.md)** — customer/territory/address creation and matching.
- **[Inventory](docs/inventory.md)** — stock push, single vs multi-location, location map.
- **[Architecture & Sync Engine](docs/architecture.md)** — GraphQL client, auth/token, pagination, throttling, fingerprint dedup, per-record locks, retry queue, sync logs, scheduler, webhook HMAC.

## License

AGPL-3.0
