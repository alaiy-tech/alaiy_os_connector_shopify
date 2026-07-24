"""
Shopify product metafields: full fetch on import (every namespace, every
page), stored on the Shopify Product Listing's own child table, pushed
back in full on export via metafieldsSet.

Metafields are marketplace-specific product data, so they live on the
Listing, never on the Item.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.queries import (
    _PRODUCT_METAFIELDS_PAGE_QUERY, _METAFIELDS_SET_MUTATION,
)


def fetch_all_metafields_for_product(product_gid: str, client) -> list:
    """Every metafield for a product, fetched fresh (no bulk-query inline
    data available) -- for standalone backfill/refresh, not the import path."""
    nodes = []
    after = None
    has_next = True
    while has_next:
        data = client.execute(_PRODUCT_METAFIELDS_PAGE_QUERY, {"id": product_gid, "after": after})
        page = (data.get("product") or {}).get("metafields") or {}
        nodes.extend(page.get("nodes") or [])
        page_info = page.get("pageInfo") or {}
        has_next = page_info.get("hasNextPage")
        after = page_info.get("endCursor")
    return nodes


def all_metafields_of(product_node: dict, client, product_gid: str = None) -> list:
    """
    Every metafield for a product node from _PRODUCTS_QUERY, following
    pagination past the inline first-250 page if the product genuinely has
    more (rare, but "whatever is there" means don't silently cap it).
    """
    mf = product_node.get("metafields") or {}
    nodes = list(mf.get("nodes") or [])
    page_info = mf.get("pageInfo") or {}

    gid = product_gid or product_node.get("id")
    while page_info.get("hasNextPage") and gid:
        data = client.execute(_PRODUCT_METAFIELDS_PAGE_QUERY, {
            "id": gid, "after": page_info.get("endCursor"),
        })
        page = ((data.get("product") or {}).get("metafields") or {})
        nodes.extend(page.get("nodes") or [])
        page_info = page.get("pageInfo") or {}

    return nodes


def sync_listing_metafields(listing, metafield_nodes: list):
    """
    Replace the Listing's metafields child table with the current Shopify
    state -- full replace, not merge, since Shopify is the source of truth
    for what metafields currently exist (a deleted-on-Shopify metafield
    should disappear here too, not linger as a stale row).
    """
    if metafield_nodes is None:
        return
    listing.set("metafields", [])
    for node in metafield_nodes:
        if not node.get("namespace") or not node.get("key"):
            continue
        listing.append("metafields", {
            "namespace": node["namespace"],
            "key": node["key"],
            "type": node.get("type") or "",
            "value": node.get("value") or "",
        })


def build_metafields_input(listing, product_gid: str) -> list:
    """metafieldsSet input rows for every row on the Listing's own table --
    full push, same "whatever is there" completeness as the import side."""
    return [
        {
            "ownerId": product_gid,
            "namespace": row.namespace,
            "key": row.key,
            "type": row.type or "single_line_text_field",
            "value": row.value or "",
        }
        for row in (listing.metafields or [])
        if row.namespace and row.key
    ]


def push_listing_metafields(listing, product_gid: str, client):
    """Best-effort: logs and returns rather than failing the whole product
    push over a metafield issue."""
    rows = build_metafields_input(listing, product_gid)
    if not rows:
        return
    try:
        data = client.execute(_METAFIELDS_SET_MUTATION, {"metafields": rows})
        errors = (data.get("metafieldsSet") or {}).get("userErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: metafieldsSet userErrors for {listing.item}",
                message=str(errors),
            )
    except Exception:
        frappe.log_error(
            title=f"Shopify: failed to push metafields for {listing.item}",
            message=frappe.get_traceback(),
        )


@frappe.whitelist()
def backfill_all_product_metafields():
    """
    One-time-run tool: fetch metafields for every product already linked to
    a Shopify Product Listing, without re-running the full product import
    (which would re-diff every Item's content for no reason -- this only
    needs the metafields, nothing else on the product has changed). Not
    wired into patches.txt -- unlike a pure-DB patch, this makes one live
    Shopify API call per product, which could run long and would otherwise
    block a routine bench migrate. Run manually via bench execute instead.
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    listings = frappe.get_all(
        "Shopify Product Listing",
        filters={"sh_shopify_product_id": ["is", "set"]},
        fields=["name", "sh_shopify_product_id"],
    )
    if not listings:
        return {"done": 0, "failed": 0}

    client = ShopifyGraphQLClient()
    done = failed = 0
    for row in listings:
        try:
            listing = frappe.get_doc("Shopify Product Listing", row.name)
            product_gid = f"gid://shopify/Product/{row.sh_shopify_product_id}"
            nodes = fetch_all_metafields_for_product(product_gid, client)
            sync_listing_metafields(listing, nodes)
            listing.flags.from_shopify_sync = True
            listing.flags.ignore_permissions = True
            listing.save()
            done += 1
        except Exception:
            failed += 1
            frappe.log_error(
                title=f"Shopify: metafields backfill failed for {row.name}",
                message=frappe.get_traceback(),
            )
        if done % 50 == 0:
            frappe.db.commit()

    frappe.db.commit()
    result = {"done": done, "failed": failed}
    frappe.logger().info(f"Product metafields backfill: {result}")
    return result
