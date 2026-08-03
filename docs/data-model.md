# Data Model

What this connector creates of its own, and what it writes into DocTypes that already exist in Frappe, ERPNext and `alaiy_os`.

---

## DocTypes this connector creates — 15

All under module `Alaiy OS Connector Shopify`. Five are child tables.

| # | DocType | Child table | Fields | Naming |
|---|---|---|---|---|
| 1 | `Shopify Connector Settings` | | 25 | Single |
| 2 | `Shopify Product Listing` | | 13 | `field:item` |
| 3 | `Shopify Listing Variant` | yes | 5 | — |
| 4 | `Shopify Listing Image` | yes | 4 | — |
| 5 | `Shopify Product Metafield` | yes | 4 | — |
| 6 | `Shopify Synced Entity` | | 8 | `hash` |
| 7 | `Shopify Sync Log` | | 13 | `SH-SYNC-.YYYY.-.MM.-.DD.-.######` |
| 8 | `Shopify Retry Queue Entry` | | 8 | `hash` |
| 9 | `Shopify Category` | | 6 | tree (`is_tree`, nested set) |
| 10 | `Shopify Collection` | | 13 | `hash` |
| 11 | `Shopify Tag` | | 1 | `field:tag_name` |
| 12 | `Shopify Location` | | 5 | `hash` |
| 13 | `Shopify Location Map` | yes | 2 | — |
| 14 | `Item Shopify Tag` | yes | 1 | — |
| 15 | `Item Shopify Collection` | yes | 1 | — |

What each holds:

- **1** — shop URL, credentials, access token, sync intervals, and every default the connector resolves against (company, warehouse, price list, customer group, territory, cost center).
- **2–5** — the listing layer. One `Shopify Product Listing` per template Item, carrying `is_enabled`, `sh_shopify_status`, `sh_shopify_product_id`, `last_synced_at`, and per-channel overrides for title, description, price, category and product type, so Shopify presentation can differ from the Item. Variants, images and metafields hang off it as child tables. An Item save no longer pushes; the Listing is the push trigger and the enable gate.
- **6** — the identity map: Alaiy OS doc ↔ Shopify external id, plus the last fingerprint each way. An outbound push whose fingerprint is unchanged is skipped with no API call. `entity_type` is product / variant / price / inventory / order / customer.
- **7** — one row per sync run: type, trigger, status, timings, counters, page progress, `cancel_requested`, error, full log text.
- **8** — failed sync units awaiting retry: direction, attempt count, `next_attempt_at`, payload, last error. Terminal state `dead_letter`.
- **9–13** — caches of Shopify-side data, so a user picks from a list instead of typing a value the store may not have. `Shopify Category` is Shopify's Standard Product Taxonomy as a nested set (`lft` / `rgt` / `parent_shopify_category`). `Shopify Location Map` pairs a Shopify location with an Alaiy OS Warehouse.
- **14–15** — back the two Table MultiSelect fields on Item.

---

## Custom fields added to existing DocTypes — 20 across 5 DocTypes

Created by `setup/install.py::setup_custom_fields`, run on every migrate with `update=True` so property changes re-sync onto existing fields. All prefixed `sh_`.

### Item — 12

| Fieldname | Type | Written by | Notes |
|---|---|---|---|
| `sh_shopify_product_id` | Data | connector | Read-only, indexed, `fetch_from` variant_of. |
| `sh_shopify_variant_id` | Data | connector | Read-only, indexed, per variant. |
| `sh_shopify_status` | Select Active/Draft | both directions | Template-owned; variants inherit and are locked. |
| `sh_shopify_tags` | Table MultiSelect | both directions | From the cached tag list, no free typing. |
| `sh_shopify_category` | Link → Shopify Category | both directions | Template-owned. |
| `sh_shopify_category_gid` | Data | user, on import | Staging field, cleared after resolution. |
| `sh_shopify_product_type` | Data | both directions | Kept separate from Item Group. |
| `sh_country_of_origin` | Link → Country | user | Pushed as `inventoryItem.countryCodeOfOrigin`. |
| `sh_harmonized_system_code` | Data | user | Pushed as `inventoryItem.harmonizedSystemCode`. |
| `sh_seo_title` | Data | both directions | Falls back to Item Name. |
| `sh_seo_description` | Small Text | both directions | Falls back to Description. |
| `sh_shopify_collections` | Table MultiSelect | both directions | From the cached collection list. |

Two details that bite:

- `sh_shopify_category_gid` exists only because Frappe's Data Import validates Link values against existing doc names *before* a row reaches the validate hook — so a raw taxonomy GID in `sh_shopify_category` fails the import outright. This plain Data field has no such check; the hook resolves the GID and clears the field.
- A Table MultiSelect cannot use `fetch_from` (child-table data, not a scalar), so tag and collection inheritance to variants runs through Item's validate hook rather than the field definition. The scalar fields do use `fetch_from` plus `read_only_depends_on: eval:doc.variant_of`.

### Sales Order — 5

`sh_shopify_order_id` (indexed, the import dedup key), `sh_shopify_order_name` (read-only), `sh_financial_status` and `sh_fulfillment_status` (read-only, in list view), `sh_shopify_notes` (both directions, `allow_on_submit` — these orders submit immediately, so without it the field would be read-only in practice always).

### Sales Order Item — 1

`sh_shopify_variant_id` (indexed) — matches line items when an order modification arrives from Shopify.

### Customer — 1

`sh_shopify_customer_id` (indexed) — the primary match key, tried before any name or email comparison.

### Delivery Note — 1

`sh_shopify_fulfillment_id` (read-only, indexed) — one Delivery Note per Shopify fulfillment; this is what stops a repeated webhook creating a duplicate.

Historical fields are cleaned up by `_remove_deprecated_item_fields` (Frappe refuses a fieldtype change on an existing field, so the Custom Field is deleted and recreated) and by two patches: `drop_legacy_item_shopify_ids`, `drop_sync_to_shopify_field`.

---

## Data written into pre-existing DocTypes — 22

### From product import

| DocType | Fields the connector sets | Source file |
|---|---|---|
| `Item` | `item_code`, `item_name`, `description`, `item_group`, `brand`, `stock_uom` (`Nos`), `is_stock_item`, `include_item_in_selling`, `include_item_in_buying`, and all 12 `sh_` fields | `shopify/product/importer.py` |
| `Item Group` | `item_group_name`, parent — created on demand, including intermediate parents | `shopify/product/masters.py` |
| `Item Attribute` | `attribute_name` and its value rows — created on demand from Shopify option names | `shopify/product/masters.py` |
| `Item Variant Attribute` | child rows on variant Items | `shopify/product/importer.py` |
| `Brand` | `brand` — from Shopify's `vendor` | `shopify/product/masters.py` |
| `UOM` | `uom_name` — only when a Shopify unit has no local equivalent | `shopify/product/masters.py` |
| `Item Price` | `item_code`, `price_list`, `price_list_rate`, `selling` | `shopify/product/pricing.py` |
| `Price List` | `price_list_name`, `currency`, `selling` — only if the configured list is missing | `shopify/product/pricing.py` |
| `Website Slideshow` | `slideshow_name` and image rows — one per product with multiple images | `shopify/product/media.py` |
| `File` | product images downloaded and stored via `save_file`, public | `shopify/product/media.py` |
| `Stock Entry` | opening stock as `Material Receipt`: `item_code`, `qty`, `t_warehouse`, `cost_center` | `shopify/product/stock.py` |
| `Stock Entry Type` | only if `Material Receipt` is missing | `shopify/product/stock.py` |

Shopify gives a **selling** price, not a cost basis, so that opening-stock receipt has no true valuation rate — see the comment in `stock.py` for how submit is allowed anyway.

### From order import

| DocType | Fields the connector sets | Source file |
|---|---|---|
| `Sales Order` | `customer`, `company`, `currency`, `conversion_rate`, `transaction_date`, `delivery_date`, `selling_price_list`, `set_warehouse`, `cost_center`, `customer_address`, `shipping_address_name`, and the 5 `sh_` fields | `shopify/order/upsert.py` |
| `Customer` | `customer_name`, `customer_group`, `territory`, `sh_shopify_customer_id` | `shopify/order/customer.py` |
| `Territory` | `All Territories` root — only if the site has none | `shopify/order/customer.py` |
| `Address` | `address_title`, `address_type` (Shipping), `address_line1`, `address_line2`, `city`, `state`, `pincode`, `country`, linked to the Customer | `shopify/order/address.py` |
| `Address Template` | one per country — only if missing; ERPNext cannot render an address without it | `shopify/order/address.py` |
| `Sales Invoice` | built by ERPNext's own `make_sales_invoice` from the Sales Order, then submitted, once Shopify reports the order paid. `posting_date` is set explicitly — the helper defaults to today, which breaks `due_date` validation on a back-dated order | `shopify/order/invoice.py` |
| `Payment Entry` | full payment against that invoice via `get_payment_entry`, so it reads Paid — Shopify already collected the money. Same posting-date correction | `shopify/order/invoice.py` |
| `Delivery Note` | built by `make_delivery_note` on a fulfillment event, one per Shopify fulfillment | `shopify/order/delivery_notes.py` |
| `Account` | four, on demand: `Debtors <CURRENCY>` (Receivable), `Round Off`, `Shopify Sales` (Income), `Shopify Tax` (Tax) — each with `account_name`, `parent_account`, `account_type` | `order/currency.py`, `order/invoice.py`, `order/tax.py` |
| `Cost Center` | on demand, when the configured one is absent | `shopify/product/masters.py` |

Invoice, payment and delivery creation are all best-effort: a failure is logged and does not abort the order import, so a failed invoice never costs you the order.

### Read, never written

| DocType | Read for |
|---|---|
| `Bin` | `actual_qty` for the inventory push, and `modified` to find what changed. Stock is only ever moved through a Stock Entry. |
| `Warehouse` | resolved from settings and the location map |
| `Company` | default currency and country |
| `Country` | ISO code for country of origin, and Address Template naming |
