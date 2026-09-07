# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""Registration metadata for alaiy_os's OS Agent Registry -- this connector's pack.

`connector_meta.py` registers the connector: what it is, how to test it, which
sync slots it fills. This registers what an agent may *ask* it, in the same
shape and on the same schedule -- one `OS Agent Registry` row whose `tools` child
rows name this app's whitelisted entry points as dotted-path handlers. The
upsert lives beside the connector one, in setup/install.py, and runs on every
`bench migrate`.

## The handlers are api/agent.py, deliberately

Core resolves a handler with `frappe.get_attr` and calls `handler(**input)`, so
`shopify/product/register.py` would work just as well mechanically.
`api/agent.py` is the right one because the permission gate travels with the
call. Pointing a tool at the module behind it would run the same code with the
gate removed, which is not a shortcut, it is a hole. Nothing in `TOOLS` below
names any other module, and a test asserts it.

## Shopify does not tell you what is wrong with a listing

The sibling Amazon pack has `get_listing_issues`, and it is real: Amazon
adjudicates listings, suppresses them, and publishes an issues feed per SKU that
`spapi/listings.py` writes back after every submission. An `ERROR` there is
usually the reason a listing is not selling.

**Shopify has no equivalent, at all.** It does not review products, does not
suppress them, and reports nothing about their quality. There is no feed to
read, and nothing under `shopify/product/` reads one.

So the two tools that occupy that space here are named for what they actually
are, and neither is called `get_listing_issues`:

- `get_listing_gaps` is *this app's own judgement* -- a product with no image,
  no description, no price. Real and useful, and not Shopify complaining.
- `get_listing_drift` is "local data has changed since we last pushed", read
  out of the fingerprint `product/export.py` already stores to decide whether to
  skip a push. Free, exact, and unable to say which field.

Naming either of them `issues` would be the single most likely way for a model
that has seen the Amazon pack to report Alaiy OS's opinion as Shopify's verdict,
which is a lie with a merchant's afternoon attached to it. `prompts/pack.md`
spends a section on the same point.

## There is no catalog search either

Amazon's `search_catalog` searches a shared global product database that every
seller lists into, keyed by ASIN. Shopify has no cross-store catalog: the only
products that exist are the merchant's own, and `list_listings` already returns
them. A tool called `search_catalog` that quietly meant "search your own
products" would collide with the meaning the same name has one pack over.

`suggest_product_type` is out for a related reason. Shopify's `productType` is a
free-text string with no validation behind it, and its category tree is already
cached locally in `Shopify Category`. If a taxonomy suggester is ever wanted it
belongs to the listing agent, which writes listings; this pack reads them.

## Reads only, except one, and it writes a file

None of the writes in this app is registered. The reasoning is sequencing rather
than taste, and it is the same as the Amazon pack's: `OS Agent Tool` has no
`effect` field, so nothing in the row can tell an orchestrator that a tool
pushes to Shopify; there is no per-tool toggle, so a site cannot switch one off;
and while `productSet` does take an idempotency key, the push path that wraps it
takes an Item lock and a retry queue entry, so a retried tool call is not the
same thing as a retried push. Registering them now would hand an agent a publish
button that no one chose to grant and nothing can take away.

What that costs is small, because `compare_listing` is the whole of the useful
half: it reports exactly what a push would change, and submits nothing.

The sync entry points -- `trigger_product_import`, `trigger_orders_sync`,
`trigger_inventory_push`, `trigger_product_export`, the `refresh_*` family,
`enable_listings_by_status`, `trigger_update_listings` -- are out for a
different reason. They page through an entire catalogue or order window, already
run on the scheduler, and enqueue rather than answer; `trigger_product_import`
carries a four-hour timeout. They are jobs, not tool calls, and one of them
inside a turn would outlast it. `get_orders_sync_status` and
`get_catalog_health` are how the pack answers questions about them instead.

`export_listings_csv` is out despite being a read, because it is not one from
here: it sets `frappe.response.type = "download"` and returns `None`, which
outside an HTTP request hands the executor nothing. Its background twin delivers
by `frappe.publish_realtime` to a browser session an agent run does not have.

`export_csv` is the exception. What it writes is a private File owned by the
run's user, out of rows the model is already holding -- no Shopify call, nothing
in the register touched, nothing another person's screen would show differently.
It is declared on File create so a site can withhold it by withholding that
permission, which is the toggle the push tools do not have.

## One store, so no connection and no marketplace

`Shopify Connector Settings` is a Single. There is one store, one set of
credentials, and nothing to select -- so unlike the Amazon pack there is no
`connection` parameter to omit and no ambiguity to refuse. The day this
connector serves two stores the answer is two registry rows and two packs, not a
parameter, for the same reason it is there.
"""

import json
from pathlib import Path

_APP = "alaiy_os_connector_shopify"
_APP_DIR = Path(__file__).resolve().parent

# The OS Agent Registry primary key, and what OS Agent Run records per run.
# Distinct from `listing`, the channel-agnostic listing agent's own id.
PACK_ID = "shopify"
PACK_NAME = "Shopify"
PACK_ICON = "shopping-bag"

# The OS Connector Registry id, stamped on every tool row. `engine/factory.py`
# refuses to build a runnable when this connector's row is disabled, which is
# how a site turns the whole pack off without touching the pack.
CONNECTOR_ID = "shopify"

DESCRIPTION = (
    "Answers questions about this store's Shopify listings and its Shopify sales. "
    "Reads the local listing register, reports what a push would send and what has "
    "changed since the last one, and aggregates the Sales Orders the order sync "
    "wrote. Can compare one product against Shopify live. Changes nothing: it "
    "cannot push, publish, archive or start a sync."
)

MODEL = "claude-sonnet-5"
MAX_TURNS = 16

# Handlers are api/agent.py and nothing else -- see the module docstring.
_API = f"{_APP}.api.agent"

# Shared schema fragments, so the same vocabulary cannot be spelled two ways
# across two tools.
_LISTING_STATUSES = ["Active", "Draft", "Archived"]
_GAPS = ["no_image", "no_description", "no_price", "no_product_type", "never_pushed"]
_GRANULARITIES = ["day", "week", "month", "total"]
_FINANCIAL_STATUSES = [
    "pending",
    "authorized",
    "partially_paid",
    "paid",
    "partially_refunded",
    "refunded",
    "voided",
    "expired",
]
_FULFILLMENT_STATUSES = [
    "unfulfilled",
    "partially_fulfilled",
    "fulfilled",
    "restocked",
    "scheduled",
    "on_hold",
]

_PAID_ONLY = (
    "The order sync only fetches orders Shopify reports as paid, so unpaid and "
    "pending orders are missing from this regardless of the dates asked for. Call "
    "get_orders_sync_status before trusting a small or zero figure."
)

_GROSS = (
    "Gross, not a payout: Shopify's fees are not deducted and refunds are counted "
    "separately rather than netted out. Never call any figure here earnings or a payout."
)


def _period_schema(granularity_default):
    """The date pair every sales read takes, described the same way each time."""
    return {
        "date_from": {
            "type": "string",
            "description": "Start of the period, inclusive, as YYYY-MM-DD. Required.",
        },
        "date_to": {
            "type": "string",
            "description": (
                "End of the period, inclusive, as YYYY-MM-DD. Defaults to today, so "
                "'since March' needs only date_from."
            ),
        },
        "granularity": {
            "type": "string",
            "enum": _GRANULARITIES,
            "description": (
                f"Bucket size for the series. Defaults to {granularity_default}. Use "
                "'total' for one figure over the whole period. A period too long for "
                "the granularity is refused naming a coarser one rather than truncated."
            ),
        },
    }


_FINANCIAL_STATUS_PARAM = {
    "type": "string",
    "enum": _FINANCIAL_STATUSES,
    "description": (
        "Optional. Filter to one Shopify financial status. Note the sync itself only "
        "fetches paid orders, so the other values will usually match nothing."
    ),
}

_FULFILLMENT_STATUS_PARAM = {
    "type": "string",
    "enum": _FULFILLMENT_STATUSES,
    "description": "Optional. Filter to one Shopify fulfillment status.",
}


TOOLS = [
    # --- the register --------------------------------------------------------
    {
        "tool_id": "list_listings",
        "description": (
            "List this store's Shopify listings -- the local register the sync fills -- "
            "returning {total, page_no, page_size, has_more, listings}. Each row carries "
            "{item_code, item_name, is_enabled, status, product_id, handle, pushed, "
            "listing_price, product_type, has_variants, enabled_variants, last_synced_at}.\n\n"
            "This is the tool to start from: it is the only one here that answers without "
            "being handed a product, and every other listing tool needs an item_code.\n\n"
            "`item_code` is the identifier throughout this pack -- it is both the Item's "
            "code and the listing row's name. `product_id` is Shopify's own numeric id and "
            "exists only once the product has actually been pushed; `pushed` is false and "
            "`product_id` is null for a listing that never has been.\n\n"
            "Rows are as fresh as each one's `last_synced_at` and no fresher. A `total` of "
            "0 with no filters means nothing has ever synced -- call get_catalog_health "
            "rather than reporting an empty catalogue."
        ),
        "handler": f"{_API}.list_listings",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": _LISTING_STATUSES,
                    "description": (
                        "Optional. The product's intended state on Shopify. This is the "
                        "listing vocabulary and has nothing to do with the order status "
                        "filters on the sales tools."
                    ),
                },
                "is_enabled": {
                    "type": "integer",
                    "enum": [0, 1],
                    "description": (
                        "Optional. 1 for listings the connector will push, 0 for ones it "
                        "will not. A disabled listing is one nobody intends to sell here."
                    ),
                },
                "pushed": {
                    "type": "integer",
                    "enum": [0, 1],
                    "description": (
                        "Optional. 1 for products Shopify has given an id, 0 for ones the "
                        "export has never reached."
                    ),
                },
                "search": {
                    "type": "string",
                    "description": "Optional. Substring match on item code, title or Shopify product id.",
                },
                "page_no": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "1-based page number. Defaults to 1, 20 rows a page.",
                },
            },
        },
        "required_permissions": [{"doctype": "Shopify Product Listing", "ptype": "read"}],
    },
    {
        "tool_id": "get_listing",
        "description": (
            "One listing's EFFECTIVE values -- what a push would actually send, after every "
            "override and fallback is resolved -- plus its variants, images, metafields and "
            "push state.\n\n"
            "Effective matters here. A blank override field on the listing does not mean "
            "'nothing will be sent'; it means 'inherited from the Item'. This returns the "
            "resolved value, so a title reported here is the title Shopify would receive.\n\n"
            "This says nothing about what Shopify currently holds. For that, "
            "get_listing_drift (free, says whether anything changed) or compare_listing "
            "(live, says which fields)."
        ),
        "handler": f"{_API}.get_listing",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "item_code": {
                    "type": "string",
                    "description": "The item code, which is also the listing row's name. Required.",
                }
            },
            "required": ["item_code"],
        },
        "required_permissions": [{"doctype": "Shopify Product Listing", "ptype": "read"}],
    },
    {
        "tool_id": "get_listing_gaps",
        "description": (
            "Data-quality gaps across the register: products a push would send with no "
            "image, no description, no price, no product type, or that have never been "
            "pushed at all. With no `gap` it returns the count of each; with one it also "
            "returns a sample of the products in it.\n\n"
            "IMPORTANT: these are Alaiy OS's own judgements, not Shopify's. Shopify does "
            "not review listings, does not suppress them, and reports no issues of any "
            "kind. There is nothing here that Shopify has complained about, and describing "
            "it that way to a merchant would be wrong. Say 'these are missing data' rather "
            "than 'Shopify flagged these'.\n\n"
            "Counts cover enabled listings by default, because a disabled listing is one "
            "nobody intends to push and its gaps are not problems. `no_image` is a floor: "
            "an Item pointing at an empty slideshow counts as having images."
        ),
        "handler": f"{_API}.get_listing_gaps",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "gap": {
                    "type": "string",
                    "enum": _GAPS,
                    "description": "Optional. Which gap to sample products for. Omit for counts only.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Sample size when `gap` is given. Defaults to 50, capped at 200.",
                },
                "enabled_only": {
                    "type": "integer",
                    "enum": [0, 1],
                    "description": "Defaults to 1. Set 0 to count disabled listings too.",
                },
            },
        },
        "required_permissions": [{"doctype": "Shopify Product Listing", "ptype": "read"}],
    },
    {
        "tool_id": "get_listing_drift",
        "description": (
            "Has this product's local data changed since Alaiy OS last pushed it? Costs no "
            "Shopify call.\n\n"
            "Exact about the question it answers: it recomputes the same fingerprint the "
            "push itself uses to decide whether to skip, and compares it to the same stored "
            "value -- so a `changed_since_push` of true means the next push would send "
            "something different.\n\n"
            "It CANNOT say which field changed; only the hash is stored. Use compare_listing "
            "for that, which costs a live call. It also compares Alaiy OS against its own "
            "record of the push, NOT against Shopify -- an edit made directly in the Shopify "
            "admin does not show up here, and compare_listing is the only tool that catches "
            "one."
        ),
        "handler": f"{_API}.get_listing_drift",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "item_code": {"type": "string", "description": "The item code. Required."}
            },
            "required": ["item_code"],
        },
        "required_permissions": [{"doctype": "Shopify Product Listing", "ptype": "read"}],
    },
    {
        "tool_id": "get_catalog_health",
        "description": (
            "One call for the state of the catalogue: how many items and listings exist, "
            "how many have been pushed, the Active/Draft/Archived split, how many orders "
            "have synced, the last run of each sync type, and the data-quality gap counts.\n\n"
            "All local, no Shopify call. This is the tool for 'is everything working' and "
            "for explaining a surprising zero from any other tool. Compare its "
            "`listings_total` against get_store_counts to see whether Alaiy OS and Shopify "
            "actually agree about how big the catalogue is -- a large gap is a real and "
            "previously observed failure, not a rounding difference."
        ),
        "handler": f"{_API}.get_catalog_health",
        "parameters_schema": {"type": "object", "properties": {}},
        "required_permissions": [{"doctype": "Shopify Product Listing", "ptype": "read"}],
    },
    {
        "tool_id": "get_listing_link",
        "description": (
            "The Shopify admin URL and the storefront URL for one product, formatted from "
            "ids already held locally. No Shopify call.\n\n"
            "Here because this pack's most useful answers end in something it cannot do -- a "
            "listing it cannot fix, a diff it cannot push -- and the Shopify admin is where "
            "a person goes to do them.\n\n"
            "A missing URL comes back null with a `note` saying why, never as a guessed "
            "address: a product that has never been pushed has no admin page, and one "
            "Shopify has not assigned a handle has no storefront page. The storefront URL is "
            "the myshopify.com one, which redirects if the store has a custom domain."
        ),
        "handler": f"{_API}.get_listing_link",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "item_code": {
                    "type": "string",
                    "description": "The item code. Gives both links. Preferred.",
                },
                "product_id": {
                    "type": "string",
                    "description": (
                        "Shopify's numeric product id, for a caller that already holds one. "
                        "Gives the admin link only -- the storefront handle lives on the Item."
                    ),
                },
            },
        },
        "required_permissions": [{"doctype": "Item", "ptype": "read"}],
    },
    {
        "tool_id": "list_collections",
        "description": (
            "The Shopify collections cached locally, with each one's handle, whether it is "
            "smart (rule-based) or manual, and its product count.\n\n"
            "Cached rows from the last collections sync, not a live read -- `product_count` "
            "is as of `last_synced`. Use get_collection_products for what is actually in one "
            "right now."
        ),
        "handler": f"{_API}.list_collections",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "search": {"type": "string", "description": "Optional. Substring match on the title."},
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Defaults to 50, capped at 200.",
                },
            },
        },
        "required_permissions": [{"doctype": "Shopify Collection", "ptype": "read"}],
    },
    # --- live Shopify reads --------------------------------------------------
    {
        "tool_id": "compare_listing",
        "description": (
            "What Shopify holds for this product RIGHT NOW, field by field against what a "
            "push would send. One live Shopify call. Submits nothing.\n\n"
            "The only tool here that can catch an edit made directly in the Shopify admin. "
            "Returns `changes` (product fields that differ), `variants.changed` (per SKU), "
            "and `variants.only_local` / `variants.only_shopify`.\n\n"
            "READ `not_compared` BEFORE SAYING A PRODUCT MATCHES. Images and category are "
            "deliberately excluded and always will be: Alaiy OS holds local file URLs where "
            "Shopify holds its own CDN copies, and the two category representations need a "
            "taxonomy id this query does not fetch. 'In sync' means 'in sync across the "
            "compared fields', and an answer should say so.\n\n"
            "Prefer get_listing_drift when the question is only whether anything changed "
            "locally -- it is free and this is not."
        ),
        "handler": f"{_API}.compare_listing",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "item_code": {"type": "string", "description": "The item code. Required."}
            },
            "required": ["item_code"],
        },
        "required_permissions": [],
    },
    {
        "tool_id": "get_store_counts",
        "description": (
            "How many products and orders Shopify itself reports. Two live calls.\n\n"
            "The check against the local figures: a large gap between this and "
            "get_catalog_health's counts means Alaiy OS's register and the store have "
            "diverged, which has happened before and is worth reporting plainly.\n\n"
            "Counts only -- Shopify has no endpoint that returns an authoritative revenue "
            "figure, so there is no Shopify-side number to check the sales tools against. "
            "Variants are not counted here either; doing it accurately means paging the "
            "whole catalogue, which is a sync job."
        ),
        "handler": f"{_API}.get_store_counts",
        "parameters_schema": {"type": "object", "properties": {}},
        "required_permissions": [],
    },
    {
        "tool_id": "get_collection_products",
        "description": (
            "The products actually inside one Shopify collection, read live from Shopify. "
            "Takes the local Shopify Collection record's name, which list_collections "
            "returns as `name`. Each product comes back with its title, image, price, SKU "
            "and the local item_code it maps to, where one exists."
        ),
        "handler": f"{_API}.get_collection_products",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "collection_name": {
                    "type": "string",
                    "description": "The Shopify Collection record name, from list_collections. Required.",
                }
            },
            "required": ["collection_name"],
        },
        "required_permissions": [],
    },
    # --- sales ---------------------------------------------------------------
    {
        "tool_id": "get_sales_summary",
        "description": (
            "Revenue, units, orders and average order value over a period, bucketed by day, "
            "week, month or total. The headline sales read.\n\n"
            "`product_sales` is items only, no tax -- the figure to quote. `order_total` "
            "adds whatever tax and shipping rows the sync wrote. "
            + _GROSS
            + "\n\n`totals.refunds` counts the credit notes that landed in the period; they "
            "are NOT subtracted from the figures. `totals.orders_at_fallback_rate` counts "
            "orders whose currency conversion looks wrong, so a non-zero value is a reason "
            "to caveat the total.\n\n"
            "Buckets with no orders are absent, not zero -- a missing bucket is an empty "
            "one. Always read `coverage.note` and pass on what it says. " + _PAID_ONLY
        ),
        "handler": f"{_API}.get_sales_summary",
        "parameters_schema": {
            "type": "object",
            "properties": {
                **_period_schema("day"),
                "financial_status": _FINANCIAL_STATUS_PARAM,
                "fulfillment_status": _FULFILLMENT_STATUS_PARAM,
            },
            "required": ["date_from"],
        },
        "required_permissions": [{"doctype": "Sales Order", "ptype": "read"}],
    },
    {
        "tool_id": "get_top_selling_products",
        "description": (
            "The best-selling products over a period, ranked by revenue or by units.\n\n"
            "`group_by` defaults to `item`, which is how merchants think -- the t-shirt, not "
            "the medium blue one. Use `variant` when the size or colour mix is the question; "
            "revenue actually lands on variant lines, so the variant view is the finer one.\n\n"
            "`totals.unattributed_product_sales` is revenue on lines whose grouping key was "
            "never stamped, which the ranking excludes. If it is large the ranking is "
            "covering less than it looks. " + _GROSS + " " + _PAID_ONLY
        ),
        "handler": f"{_API}.get_top_selling_products",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "date_from": {
                    "type": "string",
                    "description": "Start of the period, inclusive, as YYYY-MM-DD. Required.",
                },
                "date_to": {
                    "type": "string",
                    "description": "End of the period, inclusive. Defaults to today.",
                },
                "by": {
                    "type": "string",
                    "enum": ["revenue", "units"],
                    "description": "Rank by revenue (default) or by units sold.",
                },
                "group_by": {
                    "type": "string",
                    "enum": ["item", "variant"],
                    "description": "Group by product (default) or by Shopify variant.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "How many rows. Defaults to 10, capped at 50.",
                },
                "financial_status": _FINANCIAL_STATUS_PARAM,
                "fulfillment_status": _FULFILLMENT_STATUS_PARAM,
            },
            "required": ["date_from"],
        },
        "required_permissions": [{"doctype": "Sales Order", "ptype": "read"}],
    },
    {
        "tool_id": "get_product_sales",
        "description": (
            "How one product or one variant sold over a period, bucketed. Pass exactly one "
            "of item_code or variant_id.\n\n"
            "Per-line revenue, so there is no order_total here -- the tax rows are per order "
            "and cannot be attributed to a line. " + _GROSS + " " + _PAID_ONLY
        ),
        "handler": f"{_API}.get_product_sales",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "item_code": {
                    "type": "string",
                    "description": "The item code. Pass this or variant_id, not both.",
                },
                "variant_id": {
                    "type": "string",
                    "description": "A Shopify variant id. Pass this or item_code, not both.",
                },
                **_period_schema("month"),
            },
            "required": ["date_from"],
        },
        "required_permissions": [{"doctype": "Sales Order", "ptype": "read"}],
    },
    {
        "tool_id": "compare_sales_periods",
        "description": (
            "One period's totals against another's, with the absolute and percentage "
            "changes already computed.\n\n"
            "Its own tool rather than two summary calls because the arithmetic is the part "
            "that goes wrong. Do not work a percentage change out yourself from two "
            "get_sales_summary calls -- use this.\n\n"
            "A `percent` of null means the baseline was zero, and growth from nothing has no "
            "percentage. Report the absolute figure there; do not call it 100%. "
            + _GROSS
            + " "
            + _PAID_ONLY
        ),
        "handler": f"{_API}.compare_sales_periods",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "date_from": {"type": "string", "description": "Start of the current period. Required."},
                "date_to": {"type": "string", "description": "End of the current period. Required."},
                "compare_to": {
                    "type": "string",
                    "enum": ["previous_period", "previous_year"],
                    "description": (
                        "Which baseline. `previous_period` (default) is the same number of "
                        "days immediately before; `previous_year` is the same dates 365 days "
                        "back. Ignored if baseline_from is given."
                    ),
                },
                "baseline_from": {
                    "type": "string",
                    "description": "Optional. An explicit baseline start, instead of compare_to.",
                },
                "baseline_to": {"type": "string", "description": "Optional. An explicit baseline end."},
                "financial_status": _FINANCIAL_STATUS_PARAM,
                "fulfillment_status": _FULFILLMENT_STATUS_PARAM,
            },
            "required": ["date_from", "date_to"],
        },
        "required_permissions": [{"doctype": "Sales Order", "ptype": "read"}],
    },
    {
        "tool_id": "list_shopify_orders",
        "description": (
            "A page of the individual Shopify orders behind the sales figures, returning "
            "{total, page_no, page_size, has_more, orders}.\n\n"
            "Quote `shopify_order_name` -- the `#1015` a merchant says out loud. The Sales "
            "Order name is an Alaiy OS id and means nothing to them.\n\n"
            "Unlike every other sales tool this one does NOT filter to what counts as sold, "
            "because it takes the status parameters and hiding a cancelled order would make "
            "them a lie. Each row carries `counts_as_sold` instead. DO NOT add the rows up "
            "and present the result as revenue -- the totals tools answer a deliberately "
            "different question, and this page includes orders they exclude. " + _PAID_ONLY
        ),
        "handler": f"{_API}.list_shopify_orders",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "date_from": {"type": "string", "description": "Start of the period. Required."},
                "date_to": {"type": "string", "description": "End of the period. Defaults to today."},
                "financial_status": _FINANCIAL_STATUS_PARAM,
                "fulfillment_status": _FULFILLMENT_STATUS_PARAM,
                "item_code": {
                    "type": "string",
                    "description": "Optional. Only orders containing this product.",
                },
                "page_no": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "1-based page number. Defaults to 1, 20 rows a page.",
                },
            },
            "required": ["date_from"],
        },
        "required_permissions": [{"doctype": "Sales Order", "ptype": "read"}],
    },
    {
        "tool_id": "get_orders_sync_status",
        "description": (
            "Is the order sync working, and how far back does its data actually reach? "
            "Returns the last run's status and the coverage window "
            "(`first_order_date`, `last_order_date`, `synced_orders`).\n\n"
            "CALL THIS BEFORE TRUSTING ANY SMALL OR ZERO SALES FIGURE. Without it every "
            "total lies by omission: a store whose sync only reaches back to March answers "
            "'sales in January' with a confident zero, and nothing in the zero distinguishes "
            "'you sold nothing' from 'we have no data'. " + _PAID_ONLY
        ),
        "handler": f"{_API}.get_orders_sync_status",
        "parameters_schema": {"type": "object", "properties": {}},
        "required_permissions": [{"doctype": "Sales Order", "ptype": "read"}],
    },
    # --- the one write -------------------------------------------------------
    {
        "tool_id": "export_csv",
        "description": (
            "Write rows you are already holding to a CSV file and get back its URL. Use it "
            "when someone asks for a spreadsheet, a list to work through, or data to send "
            "on -- prose cannot satisfy that and pasting commas into the reply is worse.\n\n"
            "Pass the JSON result of an earlier tool call straight through as `rows_json`: "
            "a wrapper like {total, listings: [...]} is unwrapped to its rows "
            "automatically, and a single record stays one row.\n\n"
            "Writes a private file. Reads and changes nothing on Shopify. A payload that "
            "cannot be read comes back as {saved: false, error: ...} rather than failing the "
            "turn, so fix the call and try again."
        ),
        "handler": f"{_API}.export_csv",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "rows_json": {
                    "type": "string",
                    "description": (
                        "The rows to export, as a JSON string: either an array of objects or "
                        "an object wrapping one. Required."
                    ),
                },
                "filename": {
                    "type": "string",
                    "description": "Names the file, without the extension. Defaults to 'export'.",
                },
                "columns": {
                    "type": "string",
                    "description": (
                        "Optional. Comma-separated column names, to fix the order or to "
                        "export a subset. Defaults to every field, first-seen order."
                    ),
                },
            },
            "required": ["rows_json"],
        },
        "required_permissions": [{"doctype": "File", "ptype": "create"}],
    },
]


def read_text(relpath):
    """Read a file relative to this app's package directory."""
    return (_APP_DIR / relpath).read_text(encoding="utf-8")


def build_pack_meta():
    """The OS Agent Registry row this connector registers."""
    return {
        "agent_id": PACK_ID,
        "agent_name": PACK_NAME,
        "description": DESCRIPTION,
        "icon": PACK_ICON,
        "model": MODEL,
        "max_turns": MAX_TURNS,
        "system_prompt": read_text("prompts/pack.md"),
        "output_format": "Text",
        "tools": TOOLS,
    }


def as_registry_tool(tool):
    """One manifest tool as its OS Agent Tool child row, with the JSON as text."""
    return {
        "tool_id": tool["tool_id"],
        "description": tool["description"],
        "handler": tool["handler"],
        "connector": CONNECTOR_ID,
        "parameters_schema": json.dumps(tool["parameters_schema"], indent=1),
        "required_permissions": (
            json.dumps(tool["required_permissions"], indent=1)
            if tool["required_permissions"]
            else None
        ),
    }
