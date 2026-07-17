"""
Shopify Category tree helpers -- moved verbatim from product_import.py
and product_sync.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.queries import (
    _TAXONOMY_SEARCH_QUERY, _TAXONOMY_TREE_QUERY,
)


def ensure_shopify_category(full_name: str) -> str:
    """
    Ensure the nested parent-child Shopify Category tree exists for a full name path
    (e.g., 'Apparel & Accessories / Clothing / Activewear / Sweatshirts').
    Returns the leaf node document name.
    """
    # Replace '>' with '/' to comply with Frappe's naming restrictions against special characters '<' and '>'
    full_name_clean = full_name.replace(">", "/")
    parts = [p.strip() for p in full_name_clean.split("/") if p.strip()]
    if not parts:
        return None

    parent = None
    for i, part in enumerate(parts):
        # Unique node name is the path itself to prevent collision (e.g. Sweatshirts)
        path_name = " / ".join(parts[:i+1])

        if not frappe.db.exists("Shopify Category", path_name):
            doc = frappe.new_doc("Shopify Category")
            doc.shopify_category_name = part
            doc.name = path_name
            if parent:
                doc.parent_shopify_category = parent
            doc.insert(ignore_permissions=True, set_name=path_name)
            parent = doc.name
        else:
            parent = path_name

    return parent


# Per-process cache -- the taxonomy tree doesn't change mid-run, and this
# search can otherwise fire on every single push of every item sharing the
# same category string.
_category_id_cache = {}


def _resolve_category_id(client, category_name: str):
    """
    Shopify's Category field takes a taxonomy ID, not a plain name --
    resolves our stored category name against Shopify's Standard Product
    Taxonomy search. Picks an exact case-insensitive name match if one
    comes back; otherwise the first (most relevant) search result.
    Returns None (silently, logged) if nothing matches -- an unresolvable
    category must never block the rest of the product push.
    """
    if category_name in _category_id_cache:
        return _category_id_cache[category_name]

    result = None
    try:
        data = client.execute(_TAXONOMY_SEARCH_QUERY, {"search": category_name})
        edges = ((data.get("taxonomy") or {}).get("categories") or {}).get("edges") or []
        nodes = [e["node"] for e in edges if e.get("node")]
        exact = next((n for n in nodes if n.get("name", "").lower() == category_name.lower()), None)
        chosen = exact or (nodes[0] if nodes else None)
        result = chosen.get("id") if chosen else None
    except Exception:
        frappe.log_error(
            title=f"Shopify: failed to resolve category '{category_name}'",
            message=frappe.get_traceback(),
        )

    _category_id_cache[category_name] = result
    return result


def fetch_shopify_taxonomy():
    """
    Fetch the full Shopify Standard Product Taxonomy tree and populate
    the Shopify Category doctype. Called on demand or via scheduled job.

    Paginated -- Shopify's full taxonomy has several thousand categories,
    far past the single page of 250 a single client.execute() call used
    to silently stop at (confirmed: no pageInfo/after handling at all
    before this fix, so only the first 250 nodes were ever imported).
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    created = 0
    total = 0
    try:
        for page_nodes in client.execute_paginated(_TAXONOMY_TREE_QUERY, {}, ["taxonomy", "categories"]):
            total += len(page_nodes)
            for node in page_nodes:
                shopify_id = node.get("id", "")
                name = node.get("name", "")
                full_name = node.get("fullName") or name
                if shopify_id and full_name:
                    # Re-use our robust nested tree builder to ensure parent-child linking and custom name format
                    path_name = ensure_shopify_category(full_name)
                    if path_name:
                        frappe.db.set_value("Shopify Category", path_name, "shopify_category_id", shopify_id)
                        created += 1
            frappe.db.commit()
    except Exception:
        frappe.log_error(
            title="Shopify: failed to fetch taxonomy tree",
            message=frappe.get_traceback(),
        )
        return

    if not total:
        frappe.logger().warning("Shopify taxonomy returned no categories")
        return

    frappe.logger().info(
        f"Shopify taxonomy sync completed: processed {total} categories"
    )
