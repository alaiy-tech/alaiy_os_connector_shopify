"""
Shopify Tags helpers -- moved verbatim from product_import.py and
product_sync.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.queries import _PRODUCT_TAGS_QUERY


def _normalize_tags(tags) -> list:
    """
    Shopify's tags arrive in two different shapes depending on the code
    path: GraphQL gives a list of individual tag strings, while the REST
    webhook payload gives one comma-joined string wrapped in a list
    upstream (see product_sync.py's webhook reshape). Splitting every
    element on "," handles both uniformly, since splitting an
    already-individual GraphQL tag on "," is a no-op.
    """
    if not tags:
        return []
    if isinstance(tags, str):
        tags = [tags]
    result = []
    for t in tags:
        result.extend(p.strip() for p in (t or "").split(",") if p.strip())
    return result


def _set_item_tags(item, tag_names: list):
    """
    Sets sh_shopify_tags (a Table MultiSelect of Item Shopify Tag rows)
    from a plain list of tag name strings, self-healing any "Shopify Tag"
    master record that doesn't exist yet locally -- a product pulled in
    with a tag never seen before (i.e. before the next "Sync Shopify
    Tags" run catches up) shouldn't fail or silently drop it.
    """
    for tag_name in tag_names:
        if not frappe.db.exists("Shopify Tag", tag_name):
            frappe.get_doc({"doctype": "Shopify Tag", "tag_name": tag_name}).insert(
                ignore_permissions=True)
    item.set("sh_shopify_tags", [{"shopify_tag": t} for t in tag_names])


def _item_tags(item) -> list:
    """sh_shopify_tags is a Table MultiSelect (Item Shopify Tag rows) --
    this is the one place both the outbound push and the fingerprint/
    canonical comparison should read the plain tag-name list from."""
    return [row.shopify_tag for row in (item.get("sh_shopify_tags") or []) if row.shopify_tag]


def copy_template_tags_to_variant(doc, method=None):
    """
    sh_shopify_tags is a Table MultiSelect (Item Shopify Tag rows), unlike
    the plain scalar fields elsewhere on this Item (sh_shopify_category,
    sh_shopify_product_type) that inherit from the template via
    fetch_from -- Frappe's fetch_from only copies simple field values, not
    child-table data, so a variant's tags have to be copied in explicitly
    here instead. read_only_depends_on already keeps the grid non-editable
    on a variant in the UI; this keeps its actual data in sync with
    whatever the template's tags currently are.
    """
    if not doc.variant_of:
        return
    template_tags = frappe.get_all(
        "Item Shopify Tag",
        filters={"parent": doc.variant_of},
        fields=["shopify_tag"],
        order_by="idx",
    )
    doc.set("sh_shopify_tags", [{"shopify_tag": row.shopify_tag} for row in template_tags])


@frappe.whitelist()
def sync_shopify_tags():
    """
    Fetch every tag ever used across the store's products and cache it
    locally as a Shopify Tag record -- the master list the Item Shopify
    Tag multi-select field picks from, so users choose from real Shopify
    tags instead of free-typing new ones. Paginated (250/page) since a
    real store can easily have thousands of distinct tags, well past
    Shopify's per-page connection limit.
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    created = 0
    total = 0
    try:
        for page_nodes in client.execute_paginated(_PRODUCT_TAGS_QUERY, {}, ["productTags"]):
            for tag_name in page_nodes:
                if not tag_name:
                    continue
                total += 1
                if not frappe.db.exists("Shopify Tag", tag_name):
                    frappe.get_doc({"doctype": "Shopify Tag", "tag_name": tag_name}).insert(
                        ignore_permissions=True)
                    created += 1
            frappe.db.commit()
    except Exception:
        frappe.log_error(
            title="Shopify: failed to sync product tags",
            message=frappe.get_traceback(),
        )
        return {"status": "failed"}

    frappe.logger().info(
        f"Shopify tags sync completed: {total} tags seen, {created} new"
    )
    return {"status": "ok", "total": total, "created": created}
