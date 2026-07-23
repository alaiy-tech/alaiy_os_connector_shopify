"""
Scheduled/manual order pull and historical import -- moved verbatim from
order_sync.py, unchanged.
"""

import frappe
from frappe.utils import now_datetime

from alaiy_os_connector_shopify.shopify.sync_guard import (
    has_active_sync, load_or_create_log, append_log as _append_log,
)
from alaiy_os_connector_shopify.shopify.order.queries import _ORDERS_COUNT_QUERY, _ORDERS_QUERY
from alaiy_os_connector_shopify.shopify.order.utils import _order_node_to_rest_shape
from alaiy_os_connector_shopify.shopify.order.upsert import _upsert_order


def run_orders_sync(trigger="manual", log_name=None):
    log = load_or_create_log("orders", trigger, log_name)
    settings = frappe.get_single("Shopify Connector Settings")
    # NOTE: "status:<open|closed|cancelled|any>" mirrors the old REST
    # `status` param's values 1:1 but wasn't independently verified
    # against Shopify's order search-syntax docs -- if a live pull
    # unexpectedly returns zero orders, check this filter string first.
    # The Select field's options are capitalized labels (Open/Any/...)
    # for display -- Shopify's search syntax expects lowercase tokens.
    status_filter = (settings.sh_order_status_filter or "open").lower()
    query_string = f"financial_status:paid AND status:{status_filter}"
    return _run_orders_pull(log, query_string)


def _run_orders_pull(log, query_string, skip_existing=False):
    """
    Shared pull loop for both the routine sync (run_orders_sync, filtered)
    and the full historical import (run_full_import, status:any). Owns the
    running/skipped/success/failed log transitions. skip_existing does a
    cheap exists-check before upsert -- only the historical import needs it,
    and only it emits the "imported N / already existed" summary line.
    """
    if has_active_sync("orders", exclude_name=log.name):
        log.status = "skipped"
        log.finished_at = now_datetime()
        log.error_message = "Skipped: another orders sync is already running."
        log.save(ignore_permissions=True)
        frappe.db.commit()
        return log.name

    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    try:
        from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
        client = ShopifyGraphQLClient()
        variables = {"after": None, "queryString": query_string}

        processed = created = failed = skipped_existing = pages = 0
        for page_nodes in client.execute_paginated(_ORDERS_QUERY, variables, ["orders"]):
            pages += 1
            for node in page_nodes:
                order = _order_node_to_rest_shape(node)
                processed += 1
                if skip_existing:
                    order_id = str(order.get("id", ""))
                    if order_id and frappe.db.exists("Sales Order", {"sh_shopify_order_id": order_id}):
                        skipped_existing += 1
                        continue
                try:
                    if _upsert_order(order):
                        created += 1
                except Exception as exc:
                    failed += 1
                    _append_log(log, f"ERROR order={order.get('name')}: {exc}")
                    frappe.log_error(
                        title=f"Shopify: order {order.get('name')} failed",
                        message=frappe.get_traceback(),
                    )

            # Flush real progress after every page, not just at the very end --
            # a long historical import (hundreds of orders) otherwise shows
            # 0/0/0 in the Sync Log the entire time it's running, giving no
            # way to tell "actively working" from "stuck". Same fix already
            # applied to the product importer and inventory push.
            log.items_processed = processed
            log.items_created = created
            log.items_failed = failed
            log.pages_done = pages
            log.save(ignore_permissions=True)
            frappe.db.commit()

        log.status = "success"
        log.items_processed = processed
        log.items_created = created
        log.items_failed = failed
        log.pages_done = pages
        log.finished_at = now_datetime()
        if skip_existing:
            if processed and created == 0 and failed == 0:
                _append_log(log, "All orders are already synced from Shopify.")
            else:
                _append_log(
                    log, f"Imported {created} new order(s); {skipped_existing} already existed.")
        log.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        log.status = "failed"
        log.error_message = frappe.get_traceback()[:500]
        log.finished_at = now_datetime()
        log.save(ignore_permissions=True)
        frappe.db.commit()
        raise

    return log.name


# ── Historical / full import ────────────────────────────────────────────────────

def get_shopify_orders_count() -> int:
    """Cheap count-only query, used to decide up front whether a full
    import has anything left to do, without paging through every order."""
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    client = ShopifyGraphQLClient()
    data = client.execute(_ORDERS_COUNT_QUERY)
    return int((data.get("ordersCount") or {}).get("count") or 0)


def import_existing_orders(date_from=None, date_to=None):
    """
    Entry point for the "Import Orders from Shopify" button. With no date
    range, it's the full-historical import: a fast pre-check against
    Shopify's own order count vs. how many we've already linked skips
    enqueuing a no-op pull when they already match. A date range instead
    scopes the pull to orders created in that window, so the shortcut
    doesn't apply -- Shopify's total count isn't windowed the same way.
    Either way this queues in the background, since a first-time import of
    a real store's history can be thousands of orders and must never run
    inline on the request that clicked the button.
    """
    if has_active_sync("orders"):
        return {"status": "already_running", "message": "An orders sync is already in progress."}

    if not date_from and not date_to:
        shopify_total = get_shopify_orders_count()
        already_synced = frappe.db.count(
            "Sales Order", {"sh_shopify_order_id": ["is", "set"]})

        if shopify_total and already_synced >= shopify_total:
            return {
                "status": "already_synced",
                "message": "All orders are already synced from Shopify.",
            }
        remaining_message = f"Importing {max(shopify_total - already_synced, 0)} remaining order(s) from Shopify."
    else:
        remaining_message = "Importing orders from Shopify for the selected date range."

    log = load_or_create_log("orders", "manual")
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_sync.run_full_import",
        queue="long",
        timeout=3600,
        log_name=log.name,
        date_from=date_from,
        date_to=date_to,
    )
    return {
        "status": "queued",
        "message": remaining_message,
    }


def run_full_import(log_name=None, date_from=None, date_to=None):
    """
    Pulls every order regardless of status/financial_status (unlike
    run_orders_sync, which respects the configured filter for routine
    syncs) -- this is specifically the one-time/occasional "get everything
    historical" action. Still fully idempotent via the same
    sh_shopify_order_id exists-check _upsert_order already does, so
    re-running it after a partial run only creates what's still missing.

    date_from/date_to (YYYY-MM-DD) optionally scope the pull to orders
    created in that window instead of the full history.
    """
    log = load_or_create_log("orders", "manual", log_name)
    query_string = "status:any"
    if date_from:
        query_string += f" AND created_at:>='{date_from}'"
    if date_to:
        query_string += f" AND created_at:<='{date_to}'"
    return _run_orders_pull(log, query_string, skip_existing=True)
