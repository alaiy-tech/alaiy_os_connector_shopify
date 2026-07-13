import frappe
from frappe.utils import flt, now_datetime

from alaiy_os_connector_shopify.shopify.sync_guard import has_active_sync, load_or_create_log

_ORDERS_COUNT_QUERY = """
query { ordersCount { count } }
"""

_ORDERS_QUERY = """
query PullOrders($after: String, $queryString: String!) {
  orders(first: 50, after: $after, query: $queryString, sortKey: CREATED_AT) {
    edges {
      node {
        legacyResourceId
        name
        displayFinancialStatus
        displayFulfillmentStatus
        customer {
          legacyResourceId
          firstName
          lastName
          email
        }
        lineItems(first: 100) {
          nodes {
            sku
            title
            quantity
            variant {
              legacyResourceId
            }
            originalUnitPriceSet {
              shopMoney {
                amount
              }
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""


def _order_node_to_rest_shape(node: dict) -> dict:
    """
    Reshape a GraphQL order node into the same REST-style dict that
    _upsert_order/_cancel_order/_resolve_item_code already consume.
    Webhook payloads are still REST-shaped JSON regardless of the GraphQL
    mutation used to register the subscription (Shopify sends the classic
    resource representation to webhook endpoints either way) -- keeping one
    shared internal shape means the webhook and pull code paths below don't
    need to diverge.
    """
    customer = node.get("customer") or {}
    line_items = []
    for li in (node.get("lineItems") or {}).get("nodes", []):
        variant = li.get("variant") or {}
        money = (li.get("originalUnitPriceSet") or {}).get("shopMoney") or {}
        line_items.append({
            "sku": li.get("sku"),
            "title": li.get("title"),
            "quantity": li.get("quantity"),
            "variant_id": variant.get("legacyResourceId"),
            "price": money.get("amount"),
        })
    return {
        "id": node.get("legacyResourceId"),
        "name": node.get("name"),
        "customer": {
            "id": customer.get("legacyResourceId"),
            "first_name": customer.get("firstName"),
            "last_name": customer.get("lastName"),
            "email": customer.get("email"),
        } if customer.get("legacyResourceId") else {},
        "line_items": line_items,
        "financial_status": (node.get("displayFinancialStatus") or "").lower(),
        "fulfillment_status": (node.get("displayFulfillmentStatus") or "").lower(),
    }


# ── Webhook handler ────────────────────────────────────────────────────────────

def handle_order_webhook(topic, payload):
    """
    Routes by topic. orders/create is the only one that should ever insert a
    new Sales Order from scratch -- updated/fulfilled apply in place (or fall
    back to creating it, in case Shopify's delivery order put an update
    before the create), and cancelled/delete both just cancel, never
    hard-delete, per ERPNext's own docstatus model.
    """
    if topic in ("orders/cancelled", "orders/delete"):
        _cancel_order(payload)
    elif topic == "orders/create":
        _upsert_order(payload)
    else:
        # orders/updated, orders/fulfilled
        _update_order(payload)


# ── Scheduled / manual pull ────────────────────────────────────────────────────

def run_orders_sync(trigger="manual", log_name=None):
    log = load_or_create_log("orders", trigger, log_name)
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
        settings = frappe.get_single("Shopify Connector Settings")

        # NOTE: "status:<open|closed|cancelled|any>" mirrors the old REST
        # `status` param's values 1:1 but wasn't independently verified
        # against Shopify's order search-syntax docs -- if a live pull
        # unexpectedly returns zero orders, check this filter string first.
        # The Select field's options are capitalized labels (Open/Any/...)
        # for display -- Shopify's search syntax expects lowercase tokens.
        status_filter = (settings.sh_order_status_filter or "open").lower()
        query_string = f"financial_status:paid AND status:{status_filter}"
        variables = {"after": None, "queryString": query_string}

        processed = created = failed = pages = 0
        for page_nodes in client.execute_paginated(_ORDERS_QUERY, variables, ["orders"]):
            pages += 1
            for node in page_nodes:
                order = _order_node_to_rest_shape(node)
                processed += 1
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

        log.status = "success"
        log.items_processed = processed
        log.items_created = created
        log.items_failed = failed
        log.pages_done = pages
        log.finished_at = now_datetime()
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


def import_existing_orders():
    """
    Entry point for the "Import Existing Orders" button. Fast pre-check
    against Shopify's own order count vs. how many we've already linked --
    if they match, there is nothing to import and we say so immediately
    instead of enqueuing a no-op pull. Otherwise queues the full historical
    pull (every status, not just the configured filter) in the background,
    since a first-time import of a real store's history can be thousands of
    orders and must never run inline on the request that clicked the button.
    """
    if has_active_sync("orders"):
        return {"status": "already_running", "message": "An orders sync is already in progress."}

    shopify_total = get_shopify_orders_count()
    already_synced = frappe.db.count(
        "Sales Order", {"sh_shopify_order_id": ["is", "set"]})

    if shopify_total and already_synced >= shopify_total:
        return {
            "status": "already_synced",
            "message": "All orders are already synced from Shopify.",
        }

    log = load_or_create_log("orders", "manual")
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.order_sync.run_full_import",
        queue="long",
        timeout=3600,
        log_name=log.name,
    )
    return {
        "status": "queued",
        "message": f"Importing {max(shopify_total - already_synced, 0)} remaining order(s) from Shopify.",
    }


def run_full_import(log_name=None):
    """
    Pulls every order regardless of status/financial_status (unlike
    run_orders_sync, which respects the configured filter for routine
    syncs) -- this is specifically the one-time/occasional "get everything
    historical" action. Still fully idempotent via the same
    sh_shopify_order_id exists-check _upsert_order already does, so
    re-running it after a partial run only creates what's still missing.
    """
    log = load_or_create_log("orders", "manual", log_name)
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
        variables = {"after": None, "queryString": "status:any"}

        processed = created = failed = skipped_existing = pages = 0
        for page_nodes in client.execute_paginated(_ORDERS_QUERY, variables, ["orders"]):
            pages += 1
            for node in page_nodes:
                order = _order_node_to_rest_shape(node)
                processed += 1
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

        log.status = "success"
        log.items_processed = processed
        log.items_created = created
        log.items_failed = failed
        log.pages_done = pages
        log.finished_at = now_datetime()
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


# ── Internal helpers ───────────────────────────────────────────────────────────

def _upsert_order(order):
    """Returns True if a new Sales Order was created, False if skipped."""
    order_id = str(order.get("id", ""))
    if not order_id:
        return False
    if frappe.db.exists("Sales Order", {"sh_shopify_order_id": order_id}):
        return False  # already processed

    settings = frappe.get_single("Shopify Connector Settings")
    customer_name = _get_or_create_customer(
        order.get("customer") or {}, settings)

    line_items = []
    for li in order.get("line_items", []):
        item_code = _resolve_item_code(li)
        if not item_code:
            continue
        line_items.append({
            "item_code": item_code,
            "qty": flt(li.get("quantity", 1)),
            "rate": flt(li.get("price", 0)),
            "delivery_date": frappe.utils.today(),
        })

    if not line_items:
        frappe.log_error(
            title=f"Shopify order {order.get('name')}: no mappable items",
            message=str(order.get("line_items")),
        )
        return False

    so = frappe.new_doc("Sales Order")
    so.customer = customer_name
    so.company = settings.sh_company or frappe.defaults.get_global_default(
        "company")
    so.transaction_date = frappe.utils.today()
    so.delivery_date = frappe.utils.today()
    so.selling_price_list = settings.sh_selling_price_list or "Standard Selling"
    so.set_warehouse = settings.sh_default_warehouse
    if settings.sh_cost_center:
        so.cost_center = settings.sh_cost_center
    so.sh_shopify_order_id = order_id
    so.sh_shopify_order_name = order.get("name", "")
    so.sh_financial_status = order.get("financial_status", "")
    so.sh_fulfillment_status = order.get("fulfillment_status", "")
    for li in line_items:
        so.append("items", li)

    # Set BEFORE insert/submit -- Sales Order's on_update/on_submit doc_events
    # check this flag to skip pushing back to Shopify, since this save
    # originated FROM Shopify (webhook or pull) and pushing it back would
    # just be echoing the same data Shopify already has.
    so.flags.from_shopify_sync = True
    so.flags.ignore_permissions = True
    so.insert()
    so.submit()
    frappe.db.commit()
    return True


def _update_order(order):
    """
    Applies an orders/updated or orders/fulfilled webhook to an existing
    Sales Order in place. Only touches status-tracking fields, never line
    items -- a submitted Sales Order can't have its items changed without
    ERPNext's amendment flow, and auto-amending on every status ping would
    be far more disruptive than it's worth. If the order's line items
    genuinely changed on Shopify, that needs a human to review and amend;
    this at least keeps financial/fulfillment status current automatically.
    Falls back to a full create if we've never seen this order (e.g.
    Shopify redelivered orders/updated before orders/create ever arrived).
    """
    order_id = str(order.get("id", ""))
    if not order_id:
        return False

    so_name = frappe.db.get_value(
        "Sales Order", {"sh_shopify_order_id": order_id}, "name")
    if not so_name:
        return _upsert_order(order)

    updates = {}
    financial_status = order.get("financial_status") or ""
    fulfillment_status = order.get("fulfillment_status") or ""
    if financial_status:
        updates["sh_financial_status"] = financial_status
    if fulfillment_status:
        updates["sh_fulfillment_status"] = fulfillment_status

    if updates:
        for field, value in updates.items():
            frappe.db.set_value("Sales Order", so_name, field, value)
        frappe.db.commit()
    return False


def _cancel_order(order):
    order_id = str(order.get("id", ""))
    so_name = frappe.db.get_value(
        "Sales Order", {"sh_shopify_order_id": order_id}, "name")
    if so_name:
        so = frappe.get_doc("Sales Order", so_name)
        if so.docstatus == 1:
            # See _upsert_order's note on from_shopify_sync -- this cancel
            # came FROM Shopify, so the on_cancel push-back hook must not
            # try to cancel the same order on Shopify again.
            so.flags.from_shopify_sync = True
            so.cancel()
            frappe.db.commit()


def _get_or_create_customer(customer_data, settings):
    shopify_id = str(customer_data.get("id", ""))
    if shopify_id:
        existing = frappe.db.get_value(
            "Customer", {"sh_shopify_customer_id": shopify_id}, "name"
        )
        if existing:
            return existing

    first = customer_data.get("first_name", "")
    last = customer_data.get("last_name", "")
    full_name = f"{first} {last}".strip() or customer_data.get(
        "email", "") or f"Shopify {shopify_id}"

    if frappe.db.exists("Customer", full_name):
        return full_name

    c = frappe.new_doc("Customer")
    c.customer_name = full_name
    c.customer_type = "Individual"
    c.customer_group = settings.sh_customer_group or "All Customer Groups"
    c.territory = "All Territories"
    if shopify_id:
        c.sh_shopify_customer_id = shopify_id
    c.flags.ignore_permissions = True
    c.insert()
    frappe.db.commit()
    return c.name


def _resolve_item_code(line_item):
    sku = (line_item.get("sku") or "").strip()
    if sku and frappe.db.exists("Item", sku):
        return sku

    variant_id = str(line_item.get("variant_id") or "")
    if variant_id:
        by_variant = frappe.db.get_value(
            "Item", {"sh_shopify_variant_id": variant_id}, "name"
        )
        if by_variant:
            return by_variant

    title = (line_item.get("title") or "").strip()
    if title and frappe.db.exists("Item", title):
        return title

    return None


# ── Sync log helpers ───────────────────────────────────────────────────────────

def _append_log(log, message: str):
    """Append a line to log.log_messages without saving."""
    existing = log.log_messages or ""
    log.log_messages = (existing + "\n" + message).strip()
