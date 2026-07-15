"""
Periodic safety net for products: webhooks are the primary sync path and
normally fire instantly, but a webhook delivery CAN silently fail (network
blip, HMAC edge case, Shopify's own retry budget exhausted) with no visible
symptom -- confirmed this session for orders (a wrong webhook secret meant
real edits never arrived, invisibly, for days). Products have no periodic
recheck at all today, unlike inventory. Re-diffing the entire catalog on a
timer would be expensive and pointless (~1500+ products, most unchanged);
instead this only asks Shopify for products it says changed within a
recent window, which is cheap and catches the same class of missed update.
"""

import frappe
from frappe.utils import add_to_date, now_datetime, get_datetime

from alaiy_os_connector_shopify.shopify.sync_guard import (
    has_active_sync, load_or_create_log, append_log as _append_log, close_log as _close_log,
)
from alaiy_os_connector_shopify.shopify.sync_engine import entities
from alaiy_os_connector_shopify.shopify.product_sync import _to_utc_naive

_RECENT_PRODUCTS_QUERY = """
query RecentProducts($after: String) {
  products(first: 50, after: $after, sortKey: UPDATED_AT, reverse: true) {
    edges {
      node {
        legacyResourceId
        updatedAt
        title
        bodyHtml
        vendor
        productType
        tags
        category { name }
        status
        images(first: 10) { nodes { src } }
        variants(first: 100) {
          nodes {
            legacyResourceId
            sku
            price
            compareAtPrice
            inventoryItem {
              measurement { weight { value unit } }
            }
          }
        }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""


def _graphql_node_to_rest_shape(node: dict) -> dict:
    """
    Reshapes a GraphQL product node (this query's own shape) into the same
    REST-style dict _handle_product_update/_update_item_from_shopify already
    consume -- reuses that one already-tested update path instead of a
    second parallel implementation for reconciliation.
    """
    from alaiy_os_connector_shopify.shopify.product_import import _WEIGHT_UNIT_TO_UOM

    category = node.get("category") or {}
    variants = []
    for v in (node.get("variants") or {}).get("nodes", []):
        weight = ((v.get("inventoryItem") or {}).get("measurement") or {}).get("weight") or {}
        variant = {
            "variant_id": v.get("legacyResourceId"),
            "sku": v.get("sku"),
            "price": v.get("price"),
            "compare_at_price": v.get("compareAtPrice"),
        }
        if weight.get("value"):
            variant["weight"] = weight["value"]
            variant["weight_unit"] = _WEIGHT_UNIT_TO_UOM.get(weight.get("unit"), "").lower()
        variants.append(variant)

    return {
        "id": node.get("legacyResourceId"),
        "updated_at": node.get("updatedAt"),
        "title": node.get("title", ""),
        "body_html": node.get("bodyHtml", ""),
        "vendor": node.get("vendor", ""),
        "product_type": node.get("productType", ""),
        "tags": node.get("tags") and ", ".join(node["tags"]) or "",
        "category": {"name": category.get("name")} if category.get("name") else None,
        "status": (node.get("status") or "").lower(),
        "images": [{"src": img.get("src")} for img in (node.get("images") or {}).get("nodes", []) if img.get("src")],
        "variants": variants,
    }


def run_recent_reconciliation(trigger="scheduled", window_minutes=90, log_name=None):
    """
    Pulls products Shopify reports as updated within the last window_minutes
    (paged newest-first, stopping at the first product older than the
    window -- cheap, not a full-catalog scan) and re-applies any whose
    Shopify updated_at is newer than what we last recorded, exactly as if
    their webhook had actually arrived. A product with no Synced Entity at
    all (a missed products/create) is imported fresh via the same one-time
    import path a manual import already uses.
    """
    log = load_or_create_log("products_reconcile", trigger, log_name)
    if has_active_sync("products_reconcile", exclude_name=log.name):
        _close_log(log, "skipped", error="Skipped: another reconciliation is already running.")
        return log.name

    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    try:
        from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
        from alaiy_os_connector_shopify.shopify.product_sync import _handle_product_update
        from alaiy_os_connector_shopify.shopify.product_import import _import_product

        client = ShopifyGraphQLClient()
        cutoff = add_to_date(now_datetime(), minutes=-window_minutes)

        processed = updated = created = failed = 0
        after = None
        stop = False
        while not stop:
            data = client.execute(_RECENT_PRODUCTS_QUERY, {"after": after})
            products = (data.get("products") or {})
            edges = products.get("edges") or []
            for edge in edges:
                node = edge.get("node") or {}
                product_id = str(node.get("legacyResourceId", ""))
                shopify_updated = node.get("updatedAt")
                if not product_id or not shopify_updated:
                    continue
                if _to_utc_naive(get_datetime(shopify_updated)) < _to_utc_naive(cutoff):
                    stop = True
                    break

                processed += 1
                try:
                    entity = entities.get_by_external_id("product", product_id)
                    if not entity:
                        was_created, _reason = _import_product(node)
                        if was_created:
                            created += 1
                        continue

                    if entity.last_synced_at and _to_utc_naive(get_datetime(shopify_updated)) <= _to_utc_naive(get_datetime(entity.last_synced_at)):
                        continue  # already up to date -- nothing was missed

                    _handle_product_update(product_id, _graphql_node_to_rest_shape(node))
                    updated += 1
                except Exception:
                    failed += 1
                    frappe.log_error(
                        title=f"Shopify: product reconciliation failed for {product_id}",
                        message=frappe.get_traceback(),
                    )

            page_info = products.get("pageInfo") or {}
            if stop or not page_info.get("hasNextPage"):
                break
            after = page_info.get("endCursor")

        _append_log(log, f"{updated} updated, {created} created (missed), {failed} failed, {processed} checked.")
        _close_log(log, "success", processed=processed, created=updated + created, failed=failed)
    except Exception:
        _close_log(log, "failed", error=frappe.get_traceback())
        raise

    return log.name
