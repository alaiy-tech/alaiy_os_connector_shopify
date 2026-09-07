# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""The whitelisted surface the agent pack calls. One gate, one delegation, each.

`pack_meta.py` names every handler here by dotted path, and nothing else. That
is the whole reason this module exists rather than the manifest pointing at
`shopify/product/register.py` or `sales.py` directly: core resolves a handler
with `frappe.get_attr` and calls `handler(**input)`, so either layer would work
mechanically, and only this one carries the permission gate. Pointing a tool at
`shopify/graphql_client.py` would run the same code with the gate removed, which
is not a shortcut, it is a hole.

Every function below is therefore deliberately thin. Anything with logic in it
belongs in the module it delegates to, where it can be tested without a
whitelist and reused by the desk.

## Two gates, and why they are different

- `frappe.has_permission(<doctype>, "read", throw=True)` for anything reading
  rows the sync already wrote. The doctype a tool reads is the permission it
  declares in `required_permissions`, so `alaiy_os/engine/permissions.py` checks
  it before the run even starts and the call here is the second line of defence.
- `roles.require_manager()` for anything that spends a live Shopify GraphQL
  call. Those tools declare `required_permissions: []`, because that field is a
  list of `{doctype, ptype}` and cannot express a role -- the cost being guarded
  is Shopify's rate limit, not our data. This call is the only thing between an
  agent run and the store.

## No client at module scope

`ShopifyGraphQLClient.__init__` reads the settings Single and raises on an
unconfigured site. This module is imported during `bench migrate`, when the OS
Agent Tool child controller resolves every handler dotted path -- so a client
built at import time would take migrate down on any site that has installed the
connector but not configured it. Every live handler imports it inside the call.
"""

import frappe

from alaiy_os_connector_shopify import csv_export, links, roles, sales
from alaiy_os_connector_shopify.shopify.product import register

LISTING_DOCTYPE = "Shopify Product Listing"


def _may_read(doctype):
    frappe.has_permission(doctype, "read", throw=True)


# --- the register ------------------------------------------------------------
@frappe.whitelist()
def list_listings(status=None, is_enabled=None, pushed=None, search=None, page_no=1):
    """A page of the Shopify listing register."""
    _may_read(LISTING_DOCTYPE)
    return register.list_listings(
        status=status, is_enabled=is_enabled, pushed=pushed, search=search, page_no=page_no
    )


@frappe.whitelist()
def get_listing(item_code):
    """One listing's effective values -- what a push would actually send."""
    _may_read(LISTING_DOCTYPE)
    return register.listing_details(item_code)


@frappe.whitelist()
def get_listing_gaps(gap=None, limit=None, enabled_only=1):
    """Data-quality gaps across the register. Not Shopify's opinion -- ours."""
    _may_read(LISTING_DOCTYPE)
    return register.listing_gaps(gap=gap, limit=limit, enabled_only=enabled_only)


@frappe.whitelist()
def get_listing_drift(item_code):
    """Has this listing changed since Alaiy OS last pushed it? No Shopify call."""
    _may_read(LISTING_DOCTYPE)
    return register.listing_drift(item_code)


@frappe.whitelist()
def get_catalog_health():
    """Local catalogue state: counts, push coverage, status split, last sync runs.

    Wraps `api/sync.py:get_dashboard_stats` rather than recomputing its counts.
    Two functions answering "how many listings are there" is two functions that
    can disagree, and the desk page and the pack disagreeing about a number both
    of them show is a bug nobody would think to look for.
    """
    _may_read(LISTING_DOCTYPE)
    from alaiy_os_connector_shopify.api import sync

    stats = sync.get_dashboard_stats()
    gaps = register.listing_gaps()
    return {"stats": stats, "gaps": gaps["counts"], "scope": gaps["scope"], "note": gaps["note"]}


@frappe.whitelist()
def get_listing_link(item_code=None, product_id=None):
    """The Shopify admin and storefront URLs for one product. No Shopify call."""
    _may_read("Item")
    return links.listing_link(item_code=item_code, product_id=product_id)


@frappe.whitelist()
def list_collections(search=None, limit=None):
    """The Shopify collections cached locally, with their product counts."""
    _may_read("Shopify Collection")
    from frappe.utils import cint

    filters = {}
    if search:
        filters["collection_title"] = ["like", f"%{search}%"]
    rows = frappe.get_all(
        "Shopify Collection",
        filters=filters,
        fields=[
            "name",
            "collection_title",
            "handle",
            "is_smart",
            "product_count",
            "sh_collection_id",
            "last_synced",
        ],
        order_by="collection_title asc",
        limit_page_length=min(cint(limit) or 50, 200),
    )
    for row in rows:
        row["last_synced"] = str(row["last_synced"]) if row["last_synced"] else None
        row["is_smart"] = bool(row["is_smart"])
    return {
        "total": frappe.db.count("Shopify Collection", filters),
        "returned": len(rows),
        "collections": rows,
        "note": (
            "Cached rows from the last collections sync, not a live read -- "
            "`product_count` is as of `last_synced`."
        ),
    }


# --- live Shopify reads ------------------------------------------------------
@frappe.whitelist()
def compare_listing(item_code):
    """What Shopify holds right now vs. what a push would send. Submits nothing."""
    roles.require_manager()
    from alaiy_os_connector_shopify.shopify.product import compare

    return compare.compare_listing(item_code)


@frappe.whitelist()
def get_store_counts():
    """Shopify's own product and order counts, live.

    Deliberately not `api/sync.py:get_shopify_side_stats`, which answers the
    same question for the desk page and additionally walks the entire catalogue
    100 products at a time to count variants accurately -- its own comment
    records a store where that meant 16,550 variants over 166 round trips. That
    is a job, not a tool call, and it would outlast the turn it was made in.
    Two counts, two calls.
    """
    roles.require_manager()
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    products = client.execute("query { productsCount { count } }")
    orders = client.execute("query { ordersCount { count } }")
    return {
        "shopify_products": (products.get("productsCount") or {}).get("count"),
        "shopify_orders": (orders.get("ordersCount") or {}).get("count"),
        "note": (
            "Variants are not counted here. Counting them accurately means paging the "
            "whole catalogue, which is a sync job rather than a tool call -- the desk "
            "page's Shopify-side stats do it."
        ),
    }


@frappe.whitelist()
def get_collection_products(collection_name):
    """The products inside one Shopify collection, read live from Shopify."""
    roles.require_manager()
    from alaiy_os_connector_shopify.shopify.product import collections

    products = collections.get_collection_products(collection_name)
    return {
        "collection": collection_name,
        "returned": len(products),
        "products": products,
    }


# --- sales -------------------------------------------------------------------
@frappe.whitelist()
def get_sales_summary(
    date_from, date_to=None, granularity="day", financial_status=None, fulfillment_status=None
):
    """Revenue, units, orders and average order value over a period, bucketed."""
    _may_read("Sales Order")
    return sales.sales_summary(
        date_from,
        date_to=date_to,
        granularity=granularity,
        financial_status=financial_status,
        fulfillment_status=fulfillment_status,
    )


@frappe.whitelist()
def get_top_selling_products(
    date_from,
    date_to=None,
    by="revenue",
    group_by="item",
    limit=None,
    financial_status=None,
    fulfillment_status=None,
):
    """The best-selling items or variants over a period, ranked."""
    _may_read("Sales Order")
    return sales.top_selling_products(
        date_from,
        date_to=date_to,
        by=by,
        group_by=group_by,
        limit=limit,
        financial_status=financial_status,
        fulfillment_status=fulfillment_status,
    )


@frappe.whitelist()
def get_product_sales(item_code=None, variant_id=None, date_from=None, date_to=None, granularity="month"):
    """How one item or variant sold over a period, bucketed."""
    _may_read("Sales Order")
    return sales.product_sales(
        item_code=item_code,
        variant_id=variant_id,
        date_from=date_from,
        date_to=date_to,
        granularity=granularity,
    )


@frappe.whitelist()
def compare_sales_periods(
    date_from,
    date_to,
    compare_to="previous_period",
    baseline_from=None,
    baseline_to=None,
    financial_status=None,
    fulfillment_status=None,
):
    """One period's totals against another's, with the deltas already computed."""
    _may_read("Sales Order")
    return sales.compare_sales_periods(
        date_from,
        date_to,
        compare_to=compare_to,
        baseline_from=baseline_from,
        baseline_to=baseline_to,
        financial_status=financial_status,
        fulfillment_status=fulfillment_status,
    )


@frappe.whitelist()
def list_shopify_orders(
    date_from,
    date_to=None,
    financial_status=None,
    fulfillment_status=None,
    item_code=None,
    page_no=1,
):
    """A page of the Shopify orders behind the sales figures."""
    _may_read("Sales Order")
    return sales.list_shopify_orders(
        date_from,
        date_to=date_to,
        financial_status=financial_status,
        fulfillment_status=fulfillment_status,
        item_code=item_code,
        page_no=page_no,
    )


@frappe.whitelist()
def get_orders_sync_status():
    """Is the order sync working, and how far back does its data reach?"""
    _may_read("Sales Order")
    return sales.orders_sync_status()


# --- the one write -----------------------------------------------------------
@frappe.whitelist()
def export_csv(rows_json, filename="export", columns=""):
    """Write rows the caller already holds to a private CSV File, and return its URL."""
    frappe.has_permission("File", "create", throw=True)
    return csv_export.export_csv(rows_json, filename=filename, columns=columns)
