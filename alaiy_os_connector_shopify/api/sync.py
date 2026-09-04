import frappe

from alaiy_os_connector_shopify.shopify.product import status as status_map
from alaiy_os_connector_shopify.shopify.sync_guard import load_or_create_log

from alaiy_os_connector_shopify import connections


def _enqueue_sync(sync_type, method, timeout=600, connection=None, **kwargs):
    """
    Queue one sync for one store.

    The connection is resolved here rather than inside the job so that naming a
    store that does not exist fails in the caller's own request, where it can
    be reported, instead of as a background job that quietly never runs. It is
    then passed to the job by name, because a document does not survive being
    serialised onto the queue.
    """
    connection = connections.resolve(connection)

    # Log row created here (not inside the job) so it's visible as "queued"
    # immediately, even if the shared long queue is busy and the job itself
    # doesn't start running for a while.
    log = load_or_create_log(sync_type, "manual", connection=connection)
    frappe.enqueue(
        method,
        queue="long",
        timeout=timeout,
        trigger="manual",
        log_name=log.name,
        connection=connection.name,
        **kwargs,
    )
    return {"queued": True, "log_name": log.name}


@frappe.whitelist()
def trigger_orders_sync(connection=None):
    return _enqueue_sync(
        "orders", "alaiy_os_connector_shopify.shopify.order_sync.run_orders_sync",
        connection=connection)


@frappe.whitelist()
def import_existing_orders(date_from=None, date_to=None, connection=None):
    from alaiy_os_connector_shopify.shopify.order_sync import import_existing_orders as _import
    return _import(date_from=date_from, date_to=date_to, connection=connection)


@frappe.whitelist()
def trigger_inventory_push(connection=None):
    return _enqueue_sync(
        "inventory", "alaiy_os_connector_shopify.shopify.inventory_sync.run_inventory_push",
        connection=connection)


@frappe.whitelist()
def trigger_product_import(statuses=None, connection=None):
    """
    Import products from Shopify. First run (nothing imported yet) wipes
    first as a safety net, then imports everything. Every run after that
    is a real create/update/skip sync -- no wipe -- see
    run_full_product_import's docstring for why.
    """
    return _enqueue_sync(
        "products",
        "alaiy_os_connector_shopify.shopify.product_import.run_full_product_import",
        # Was 1800s (30min) -- provably not enough anymore: each item now
        # also downloads an image, sets tags/SEO/cost/weight, and (for
        # Category) makes an extra taxonomy-search API call, confirmed live
        # to blow the old ceiling partway through a ~3000-item catalog.
        timeout=14400,  # 4 hours
        statuses=statuses,
        connection=connection,
    )


@frappe.whitelist()
def trigger_product_export(statuses=None, connection=None):
    """
    Bulk push every local (not-yet-linked) product to Shopify in one go --
    for manually-created Alaiy OS Items that predate any Shopify connection.
    Enqueued as background job.
    """
    return _enqueue_sync(
        "product_export",
        "alaiy_os_connector_shopify.shopify.product_sync.run_bulk_export_to_shopify",
        timeout=1800,
        statuses=statuses,
        connection=connection,
    )


@frappe.whitelist()
def enable_listings_by_status(statuses=None, connection=None):
    """
    Bulk-enable every currently-disabled Shopify Product Listing whose own
    status matches one of the caller's chosen statuses (any combination --
    not hardcoded to Active). Each enable is a real doc.save(), so
    on_listing_update's push hook fires per listing same as a manual
    checkbox click would -- enqueued because a large matching set is many
    of those in a row.
    """
    return _enqueue_sync(
        "listing_bulk_enable",
        "alaiy_os_connector_shopify.shopify.product.export.run_bulk_enable_listings",
        timeout=1800,
        statuses=statuses,
        connection=connection,
    )


@frappe.whitelist()
def get_sync_status(sync_type=None, connection=None):
    """Recent sync runs. Scoped to one store when the bench has more than one,
    so a seller's dashboard never shows somebody else's last import."""
    filters = {}
    connection_name = connections.resolve_optional_name(connection)
    if connection_name:
        filters["connection"] = connection_name
    if sync_type:
        # "categories" maps to "orders", "items" maps to "inventory", "products" maps to "products"
        type_map = {"categories": "orders", "items": "inventory", "products": "products"}
        filters["sync_type"] = type_map.get(sync_type, sync_type)
    return frappe.get_all(
        "Shopify Sync Log",
        filters=filters,
        fields=[
            "name", "sync_type", "trigger", "status",
            "started_at", "finished_at",
            "items_processed", "items_created", "items_failed",
            "pages_total", "pages_done",
            "error_message",
        ],
        order_by="started_at desc",
        limit=5,
    )


@frappe.whitelist()
def get_dashboard_stats():
    """
    Stat cards for the Shopify desk page -- plain counts, no Shopify API
    calls, so this stays fast even with the catalog at 20k+ items.
    """
    items_total = frappe.db.count("Item")
    templates_total = frappe.db.count("Item", {"variant_of": ["in", ["", None]]})
    templates_pushed = frappe.db.count("Item", {
        "variant_of": ["in", ["", None]], "sh_shopify_product_id": ["is", "set"]})
    templates_pending = frappe.db.count("Item", {
        "variant_of": ["in", ["", None]], "sh_shopify_product_id": ["in", ["", None]], "disabled": 0})

    # Variants aren't always separate Item docs -- some sites never use
    # ERPNext's real Item.variant_of at all and track every variant purely
    # as a Shopify Listing Variant child row instead (confirmed live:
    # variant_of count was 0 despite 3300+ real variants existing). The
    # Listing Variant row is the actual source of truth for "how many
    # variants we're tracking", regardless of which pattern a given site
    # uses underneath.
    variants_total = frappe.db.count("Shopify Listing Variant")
    variants_pushed = frappe.db.count("Shopify Listing Variant", {"sh_shopify_variant_id": ["is", "set"]})

    listings_total = frappe.db.count("Shopify Product Listing")
    listings_enabled = frappe.db.count("Shopify Product Listing", {"is_enabled": 1})

    # Blank reads as Active -- same rule status.to_shopify/export_allows use for
    # an unset field, so these three always add up to templates_total.
    templates_active = frappe.db.count("Item", {
        "variant_of": ["in", ["", None]], "sh_shopify_status": ["in", ["", None, status_map.DEFAULT_LOCAL]]})
    templates_draft = frappe.db.count("Item", {
        "variant_of": ["in", ["", None]], "sh_shopify_status": "Draft"})
    templates_archived = frappe.db.count("Item", {
        "variant_of": ["in", ["", None]], "sh_shopify_status": "Archived"})

    # Push and pull both stamp the same sh_shopify_order_id field -- nothing
    # in the schema distinguishes which direction created the link, so this
    # is "synced with Shopify" overall, not split by direction.
    orders_synced = frappe.db.count("Sales Order", {"sh_shopify_order_id": ["is", "set"]})

    last_runs = frappe.get_all(
        "Shopify Sync Log",
        fields=["sync_type", "status", "started_at"],
        order_by="started_at desc",
        limit=50,
    )
    latest_by_type = {}
    for row in last_runs:
        latest_by_type.setdefault(row.sync_type, row)

    return {
        "items_total": items_total,
        "templates_total": templates_total,
        "templates_pushed": templates_pushed,
        "templates_pending": templates_pending,
        "variants_total": variants_total,
        "variants_pushed": variants_pushed,
        "listings_total": listings_total,
        "listings_enabled": listings_enabled,
        "templates_active": templates_active,
        "templates_draft": templates_draft,
        "templates_archived": templates_archived,
        "orders_synced": orders_synced,
        "last_runs": latest_by_type,
    }


@frappe.whitelist()
def get_shopify_side_stats(connection=None):
    """
    Real counts from Shopify itself -- separate call from
    get_dashboard_stats since this hits the live API (slower, and pointless
    to block the fast local-DB numbers on). Lets the desk page show both
    sides side by side instead of only ever trusting our own DB, which is
    exactly what caused the "298 vs 23k" confusion investigated 29-07 --
    stale local ids made our own counts look right when the store itself
    didn't match.
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient(connection)
    products = client.execute("query { productsCount { count } }")
    orders = client.execute("query { ordersCount { count } }")

    # productVariantsCount caps/estimates at 10,000 for larger stores --
    # confirmed live: reported 10,000 while a full walk found 16,550 real
    # variants. Sum each product's own variantsCount instead (cheap
    # per-product aggregate, no need to list every variant id) -- accurate
    # regardless of total size.
    variant_total = 0
    cursor = None
    query = """
    query($cursor: String) {
      products(first: 100, after: $cursor) {
        edges { node { variantsCount { count } } }
        pageInfo { hasNextPage endCursor }
      }
    }
    """
    while True:
        data = client.execute(query, {"cursor": cursor})
        conn = data["products"]
        for edge in conn["edges"]:
            variant_total += (edge["node"].get("variantsCount") or {}).get("count") or 0
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]

    return {
        "shopify_products": (products.get("productsCount") or {}).get("count"),
        "shopify_orders": (orders.get("ordersCount") or {}).get("count"),
        "shopify_variants": variant_total,
    }


@frappe.whitelist()
def refresh_shopify_taxonomy(connection=None):
    """
    Manually trigger a refresh of Shopify's Standard Product Taxonomy tree.
    Fetches the full taxonomy from Shopify GraphQL and populates/updates
    the Shopify Category doctype (tree structure).
    """
    return _enqueue_sync(
        "taxonomy",
        "alaiy_os_connector_shopify.shopify.product_sync.fetch_shopify_taxonomy",
        # Shopify's full Standard Product Taxonomy is tens of thousands of
        # nodes, walked in batches of 250 with a real GraphQL round trip
        # each -- 300s was nowhere near enough and confirmed live to abort
        # mid-node, leaving a transaction to roll back. An hour is generous
        # headroom; the walk itself is idempotent/resumable via re-run.
        timeout=3600,
        connection=connection,
    )


@frappe.whitelist()
def refresh_shopify_tags(connection=None):
    """
    Manually trigger a refresh of the cached Shopify Tag list -- every
    tag ever used across the store's products, paginated in from
    productTags. Populates the Shopify Tag doctype the tags multi-select
    field picks from.
    """
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product_sync.sync_shopify_tags",
        queue="long",
        timeout=300,
    )
    return {"queued": True}


@frappe.whitelist()
def refresh_shopify_collections(connection=None):
    """
    Manually trigger a refresh of the cached Shopify Collection list -- every
    collection on the store, paginated in. Populates the Shopify Collection
    doctype the collections multi-select field picks from. Logged (sync_type
    "collections") so it shows in the dashboard like every other sync.
    """
    return _enqueue_sync(
        "collections",
        "alaiy_os_connector_shopify.shopify.product_sync.sync_shopify_collections",
        connection=connection,
    )


@frappe.whitelist()
def refresh_shopify_locations(connection=None):
    """
    Manually refresh the cached Shopify Location list -- what the
    warehouse-to-location map picks from for multi-location inventory sync.
    """
    return _enqueue_sync(
        "locations",
        "alaiy_os_connector_shopify.shopify.inventory_sync.sync_shopify_locations",
        connection=connection,
    )
