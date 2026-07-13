import contextlib

import frappe
from frappe.utils import flt, now_datetime

from alaiy_os_connector_shopify.shopify.sync_guard import has_active_sync, load_or_create_log


@contextlib.contextmanager
def _as_administrator():
    """
    handle_webhook is allow_guest=True, so frappe.session.user is "Guest"
    for the whole request AND the background job it enqueues (RQ workers
    inherit the enqueuing request's user). make_delivery_note()'s internal
    get_mapped_doc() checks create-permission on the mapped doc BEFORE we
    ever get a chance to set ignore_permissions on it -- Guest fails that
    check outright, unlike a plain doc.insert() where our own
    flags.ignore_permissions actually takes effect. Elevate just for this
    one call, then restore -- RQ workers reuse the same process across
    multiple jobs, so leaving this elevated would leak into unrelated ones.
    """
    original_user = frappe.session.user
    frappe.set_user("Administrator")
    try:
        yield
    finally:
        frappe.set_user(original_user)

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
    warehouse = _resolve_default_warehouse(settings)

    line_items = []
    for li in order.get("line_items", []):
        item_code = _resolve_item_code(li)
        if not item_code:
            continue
        line_items.append({
            "item_code": item_code,
            "qty": flt(li.get("quantity", 1)),
            "rate": flt(li.get("price", 0)),
            "warehouse": warehouse,
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
    so.set_warehouse = warehouse
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

    if order.get("fulfillments"):
        _sync_fulfillments(so.name, order.get("fulfillments"))
    elif so.sh_fulfillment_status == "fulfilled":
        # GraphQL pull path has no per-fulfillment breakdown to work with
        # (see _create_delivery_note_if_needed's note) -- full-order fallback.
        _create_delivery_note_if_needed(so.name)
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

    _sync_fulfillments(so_name, order.get("fulfillments") or [])
    return False


def _create_delivery_note_if_needed(so_name):
    """
    Full-order fallback for the one path that has no per-fulfillment
    breakdown to work with: an order pulled/imported that's already
    fulfilled on Shopify (historical import, or orders/create arriving
    after the order was already completed there) -- the GraphQL orders
    query used for pulls doesn't currently fetch the fulfillments
    connection, only the REST-shaped webhook payload does. Delivers the
    full order in one go; idempotent via the same against_sales_order
    check _sync_fulfillments's per-fulfillment-id check doesn't cover here.
    """
    if frappe.db.exists("Delivery Note Item", {"against_sales_order": so_name}):
        return

    so = frappe.get_doc("Sales Order", so_name)
    if so.docstatus != 1:
        return

    try:
        from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
        with _as_administrator():
            dn = make_delivery_note(so_name)
            _force_valid_warehouse(dn)
            dn.flags.ignore_permissions = True
            dn.insert()
            dn.submit()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: auto Delivery Note failed for {so_name}",
            message=frappe.get_traceback(),
        )


def _force_valid_warehouse(dn):
    """
    make_delivery_note() copies each item's warehouse straight from the
    Sales Order's own already-stored Item rows -- which is exactly the
    problem for any order created before the Group Warehouse validation/
    self-heal existed (confirmed live: several real orders had a Group
    Warehouse permanently baked into their Item rows, since a submitted
    Sales Order's items can never be edited/amended just to fix this).
    Never trust that stored value for an actual stock transaction --
    always re-resolve and force a real leaf warehouse here, at the one
    point that actually matters (the document that moves stock), so this
    class of stale data can never break delivery creation again, for any
    order regardless of when it was created.
    """
    settings = frappe.get_single("Shopify Connector Settings")
    warehouse = _resolve_default_warehouse(settings)
    for item in dn.items:
        item.warehouse = warehouse
    dn.set_warehouse = warehouse


def _sync_fulfillments(so_name, fulfillments):
    """
    Each Shopify Fulfillment object (in the webhook's REST-shaped payload,
    not just the order-level fulfillment_status label) carries exactly
    which line items/quantities were shipped in that specific event -- this
    is what makes PARTIAL fulfillment trackable at all, not just the binary
    fulfilled/unfulfilled case. One Delivery Note per Shopify Fulfillment
    id, tagged with sh_shopify_fulfillment_id so a redelivered webhook for
    the same fulfillment event never creates a duplicate Delivery Note, and
    a second, later partial shipment creates its own separate one.
    """
    if not fulfillments:
        return

    so = frappe.get_doc("Sales Order", so_name)
    if so.docstatus != 1:
        return

    for fulfillment in fulfillments:
        fulfillment_id = str(fulfillment.get("id") or "")
        if not fulfillment_id:
            continue
        if frappe.db.exists("Delivery Note", {"sh_shopify_fulfillment_id": fulfillment_id}):
            continue
        _create_delivery_note_for_fulfillment(
            so, fulfillment_id, fulfillment.get("line_items") or [])


def _create_delivery_note_for_fulfillment(so, fulfillment_id, fulfillment_line_items):
    qty_by_item = {}
    for li in fulfillment_line_items:
        item_code = _resolve_item_code({
            "sku": li.get("sku"),
            "variant_id": li.get("variant_id"),
            "title": li.get("title") or li.get("name"),
        })
        if not item_code:
            continue
        qty_by_item[item_code] = qty_by_item.get(item_code, 0) + flt(li.get("quantity", 0))

    if not qty_by_item:
        frappe.log_error(
            title=f"Shopify: fulfillment {fulfillment_id} had no mappable items",
            message=f"Sales Order: {so.name}, line_items: {fulfillment_line_items}",
        )
        return

    try:
        from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
        with _as_administrator():
            dn = make_delivery_note(so.name)
            _force_valid_warehouse(dn)

            # make_delivery_note maps the full remaining quantity per item
            # by default -- trim each row down to only what THIS
            # fulfillment event covers, dropping rows it didn't touch.
            kept_items = []
            for dn_item in dn.items:
                fulfilled_qty = qty_by_item.get(dn_item.item_code, 0)
                if fulfilled_qty <= 0:
                    continue
                dn_item.qty = min(dn_item.qty, fulfilled_qty)
                kept_items.append(dn_item)
            dn.items = kept_items
            if not dn.items:
                return

            dn.sh_shopify_fulfillment_id = fulfillment_id
            dn.flags.ignore_permissions = True
            dn.insert()
            dn.submit()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: auto Delivery Note failed for fulfillment {fulfillment_id}",
            message=f"Sales Order: {so.name}\n{frappe.get_traceback()}",
        )


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
    c.territory = _resolve_default_territory(settings)
    if shopify_id:
        c.sh_shopify_customer_id = shopify_id
    c.flags.ignore_permissions = True
    c.insert()
    frappe.db.commit()
    return c.name


def _resolve_default_territory(settings):
    """
    "All Territories" is ERPNext's usual seeded root, but nothing guarantees
    it exists under that exact name on every site (renamed, demo data never
    loaded, or a from-scratch site with zero Territory rows at all --
    confirmed live on a real site). Order import must never hard-fail over
    a missing master record the merchant didn't know they needed, so this
    self-heals: configured setting, then the conventional name if present,
    then any existing Territory, then create a root one as a last resort.
    """
    if settings.sh_default_territory:
        return settings.sh_default_territory
    if frappe.db.exists("Territory", "All Territories"):
        return "All Territories"
    fallback = frappe.db.get_value("Territory", {}, "name")
    if fallback:
        return fallback
    return _create_root_territory()


def _create_root_territory():
    territory = frappe.new_doc("Territory")
    territory.territory_name = "All Territories"
    territory.is_group = 1
    territory.flags.ignore_permissions = True
    territory.insert()
    frappe.db.commit()
    return territory.name


def _resolve_default_warehouse(settings):
    """
    Belt-and-suspenders alongside ShopifyConnectorSettings._validate_default_warehouse:
    that check stops a NEW misconfiguration at save time, but doesn't retroactively
    fix a site that set this before the validation existed (confirmed live --
    a real site had it pointed at the auto-seeded root Group Warehouse, which
    silently killed every auto-created Delivery Note with "Group node warehouse
    is not allowed to select for transactions"). If the configured warehouse
    turns out to be a Group, fall back to the first real leaf warehouse under
    the connector's configured Company instead of hard-failing order import.
    """
    configured = settings.sh_default_warehouse
    if configured and not frappe.db.get_value("Warehouse", configured, "is_group"):
        return configured

    if configured:
        frappe.log_error(
            title="Shopify: Default Warehouse is a Group Warehouse, falling back",
            message=f"Configured: {configured}. Set a leaf warehouse in Shopify Connector Settings to silence this.",
        )

    fallback = frappe.db.get_value(
        "Warehouse", {"is_group": 0, "company": settings.sh_company}, "name")
    if not fallback:
        fallback = frappe.db.get_value("Warehouse", {"is_group": 0}, "name")
    if not fallback:
        frappe.throw(
            "No usable (non-Group) Warehouse exists for this company. "
            "Create one, then set it as 'Default Warehouse' on Shopify Connector Settings."
        )
    return fallback


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
