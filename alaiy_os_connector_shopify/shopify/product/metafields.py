"""
Shopify product metafields: full fetch on import (every namespace, every
page), stored on the Shopify Product Listing's own child table, pushed
back in full on export via metafieldsSet.

Metafields are marketplace-specific product data (same rule as everything
else moved in #60) -- they live on the Listing, never on the Item.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.queries import (
    _PRODUCT_METAFIELDS_PAGE_QUERY, _METAFIELDS_SET_MUTATION,
)


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
