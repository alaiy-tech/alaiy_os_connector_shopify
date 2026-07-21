"""
Shopify Category tree helpers -- moved verbatim from product_import.py
and product_sync.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.queries import (
    _TAXONOMY_SEARCH_QUERY, _TAXONOMY_TREE_QUERY, _TAXONOMY_NODES_BY_ID_QUERY,
)

_NODES_PER_CALL = 250  # Shopify's node-by-id bulk lookup cap, same as any other connection page size here.


def _safe_doc_name(path_name: str) -> str:
    """
    Frappe's `name` column is varchar(140) -- a deep real taxonomy path
    ("Apparel & Accessories / Jewelry / ... / <long leaf>") can exceed
    that, confirmed live: 'Data too long for column name'. Truncate with
    a short deterministic hash suffix so it stays unique instead of
    colliding once cut off.
    """
    if len(path_name) <= 140:
        return path_name
    import hashlib
    h = hashlib.sha1(path_name.encode("utf-8")).hexdigest()[:8]
    return path_name[:130] + "-" + h


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
        path_name = _safe_doc_name(" / ".join(parts[:i+1]))

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


def _save_taxonomy_node(node):
    """
    Returns False (never raises) on failure -- confirmed live on a busy
    production site: a real inbound product webhook writing to the same
    Shopify Category table at the same moment caused a MySQL lock-wait
    timeout here, which used to abort the ENTIRE BFS (one contended node
    killed every node after it, including all its unfetched children).
    Retries the transient lock case a few times with backoff before
    giving up on just this one node -- the rest of the tree still
    completes either way.
    """
    shopify_id = node.get("id", "")
    name = node.get("name", "")
    full_name = node.get("fullName") or name
    if not (shopify_id and full_name):
        return False

    import time
    for attempt in range(3):
        try:
            # Re-use our robust nested tree builder to ensure parent-child linking and custom name format
            path_name = ensure_shopify_category(full_name)
            if not path_name:
                return False
            frappe.db.set_value("Shopify Category", path_name, "shopify_category_id", shopify_id)
            return True
        except Exception as exc:
            is_lock_timeout = "Lock wait timeout" in str(exc)
            if is_lock_timeout and attempt < 2:
                frappe.db.rollback()
                time.sleep(1 + attempt)
                continue
            frappe.log_error(
                title=f"Shopify: failed to save taxonomy node '{full_name}'",
                message=frappe.get_traceback(),
            )
            frappe.db.rollback()
            return False
    return False


def fetch_shopify_taxonomy():
    """
    Fetch the full Shopify Standard Product Taxonomy tree and populate
    the Shopify Category doctype. Called on demand or via scheduled job.

    taxonomy.categories() (the query this used before) only ever returns
    the 26 ROOT (level-1) nodes -- confirmed live via introspection, it is
    NOT a flat connection over the whole multi-thousand-node tree despite
    supporting first/after pagination. The real tree is only reachable by
    walking each node's childrenIds recursively (BFS here), batch-fetching
    each next level via Shopify's generic nodes(ids:) bulk lookup (up to
    250 ids per call) instead of one round trip per node.
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    saved = 0
    total = 0
    seen_ids = set()

    try:
        # Level 1 root ids -- the only thing the flat query is actually
        # good for. Everything below is walked via childrenIds instead.
        queue = []
        for page_nodes in client.execute_paginated(_TAXONOMY_TREE_QUERY, {}, ["taxonomy", "categories"]):
            for node in page_nodes:
                node_id = node.get("id")
                if node_id and node_id not in seen_ids:
                    seen_ids.add(node_id)
                    queue.append(node_id)

        # BFS: fetch each level's full node data (name/fullName/childrenIds/
        # isLeaf) in one bulk call per _NODES_PER_CALL ids, save it, queue
        # its children for the next round. One fetch per node, not two.
        while queue:
            next_queue = []
            for i in range(0, len(queue), _NODES_PER_CALL):
                batch = queue[i:i + _NODES_PER_CALL]
                data = client.execute(_TAXONOMY_NODES_BY_ID_QUERY, {"ids": batch})
                nodes = [n for n in (data.get("nodes") or []) if n]
                for node in nodes:
                    total += 1
                    if _save_taxonomy_node(node):
                        saved += 1
                    if not node.get("isLeaf"):
                        for child_id in (node.get("childrenIds") or []):
                            if child_id not in seen_ids:
                                seen_ids.add(child_id)
                                next_queue.append(child_id)
                frappe.db.commit()
            queue = next_queue
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
        f"Shopify taxonomy sync completed: processed {total} categories, saved {saved}"
    )
