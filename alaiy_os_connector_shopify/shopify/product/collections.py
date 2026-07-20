"""
Shopify Collections <-> ERPNext sync.

Bidirectional, manual collections:
- Import: cache every Shopify collection as a "Shopify Collection" doc (the
  master list the Item's collections multi-select picks from). Smart/rule-based
  collections are cached read-only (is_smart=1) -- their membership is driven by
  Shopify's own rules, so products can't be added/removed on our side.
- Export (membership): when a product is pushed, reconcile which manual
  collections it belongs to on Shopify against the Item's sh_shopify_collections
  field, using collectionAddProducts / collectionRemoveProducts. Smart
  collections are never touched.
- Export (collection CRUD): a Shopify Collection created/edited/deleted in
  ERPNext is pushed via collectionCreate / collectionUpdate / collectionDelete.
- Webhooks: collections/create|update|delete keep the cache in step with
  changes made on Shopify.
"""

import frappe

# ── GraphQL ──────────────────────────────────────────────────────────────────

_COLLECTIONS_LIST_QUERY = """
query ListCollections($after: String) {
  collections(first: 100, after: $after) {
    edges {
      node {
        id
        legacyResourceId
        title
        handle
        descriptionHtml
        updatedAt
        productsCount {
          count
        }
        ruleSet {
          rules {
            column
          }
        }
        image {
          url
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

_PRODUCT_COLLECTIONS_QUERY = """
query ProductCollections($id: ID!) {
  product(id: $id) {
    collections(first: 100) {
      nodes {
        id
      }
    }
  }
}
"""

_COLLECTION_CREATE_MUTATION = """
mutation CollectionCreate($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection {
      id
      legacyResourceId
      handle
    }
    userErrors {
      field
      message
    }
  }
}
"""

_COLLECTION_UPDATE_MUTATION = """
mutation CollectionUpdate($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection {
      id
      handle
    }
    userErrors {
      field
      message
    }
  }
}
"""

_COLLECTION_DELETE_MUTATION = """
mutation CollectionDelete($input: CollectionDeleteInput!) {
  collectionDelete(input: $input) {
    deletedCollectionId
    userErrors {
      field
      message
    }
  }
}
"""

_COLLECTION_ADD_PRODUCTS_MUTATION = """
mutation CollectionAddProducts($id: ID!, $productIds: [ID!]!) {
  collectionAddProducts(id: $id, productIds: $productIds) {
    userErrors {
      field
      message
    }
  }
}
"""

_COLLECTION_REMOVE_PRODUCTS_MUTATION = """
mutation CollectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
  collectionRemoveProducts(id: $id, productIds: $productIds) {
    userErrors {
      field
      message
    }
  }
}
"""


def _collection_gid(collection_id: str) -> str:
    return f"gid://shopify/Collection/{collection_id}"


# ── Cache sync (Shopify -> local Shopify Collection docs) ─────────────────────

def _upsert_collection_cache(node: dict):
    """
    Create or update one Shopify Collection doc from a GraphQL collection node.
    Keyed on legacyResourceId (sh_collection_id). Sets from_shopify_sync so the
    doc_events push-back hook doesn't echo this straight back to Shopify.
    """
    legacy = str(node.get("legacyResourceId") or "")
    gid = node.get("id") or (_collection_gid(legacy) if legacy else "")
    if not legacy and not gid:
        return None
    is_smart = 1 if (node.get("ruleSet") or {}).get("rules") else 0
    values = {
        "collection_title": node.get("title") or "Untitled",
        "handle": node.get("handle") or "",
        "description": node.get("descriptionHtml") or "",
        "image_url": (node.get("image") or {}).get("url") or "",
        "is_smart": is_smart,
        "product_count": (node.get("productsCount") or {}).get("count") or 0,
        "sh_collection_id": legacy,
        "sh_collection_gid": gid,
        "last_synced": frappe.utils.now_datetime(),
    }

    name = frappe.db.get_value("Shopify Collection", {"sh_collection_id": legacy}, "name") if legacy else None
    if name:
        doc = frappe.get_doc("Shopify Collection", name)
        doc.update(values)
    else:
        doc = frappe.get_doc(dict(doctype="Shopify Collection", **values))
    doc.flags.from_shopify_sync = True
    doc.flags.ignore_permissions = True
    doc.save()
    return doc.name


@frappe.whitelist()
def sync_shopify_collections():
    """
    Fetch every collection on the store and cache it locally as a Shopify
    Collection doc -- the master list the Item collections multi-select picks
    from. Paginated (100/page).
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    total = 0
    try:
        for page_nodes in client.execute_paginated(_COLLECTIONS_LIST_QUERY, {"after": None}, ["collections"]):
            for node in page_nodes:
                _upsert_collection_cache(node)
                total += 1
            frappe.db.commit()
    except Exception:
        frappe.log_error(
            title="Shopify: failed to sync collections",
            message=frappe.get_traceback(),
        )
        return {"status": "failed"}

    frappe.logger().info(f"Shopify collections sync completed: {total} collections")
    return {"status": "ok", "total": total}


# ── Item membership field (mirror of tags) ────────────────────────────────────

def _set_item_collections(item, collection_titles: list):
    """
    Set sh_shopify_collections (Table MultiSelect of Item Shopify Collection
    rows) from a list of collection titles. Only titles that already exist as
    Shopify Collection docs are linked -- unlike tags we do NOT auto-create the
    master here, since a collection is a real Shopify object with an id, created
    via the Sync Collections action or the collections/create webhook.
    """
    rows = []
    for title in collection_titles:
        name = frappe.db.get_value("Shopify Collection", {"collection_title": title}, "name")
        if name:
            rows.append({"shopify_collection": name})
    item.set("sh_shopify_collections", rows)


def _item_collection_names(item) -> list:
    """Linked Shopify Collection doc names on this Item's multi-select."""
    return [row.shopify_collection for row in (item.get("sh_shopify_collections") or []) if row.shopify_collection]


def copy_template_collections_to_variant(doc, method=None):
    """
    sh_shopify_collections is a Table MultiSelect (child-table data), so it
    can't inherit via fetch_from like scalar fields -- copy the template's rows
    onto the variant explicitly, same as copy_template_tags_to_variant.
    """
    if not doc.variant_of:
        return
    rows = frappe.get_all(
        "Item Shopify Collection",
        filters={"parent": doc.variant_of},
        fields=["shopify_collection"],
        order_by="idx",
    )
    doc.set("sh_shopify_collections", [{"shopify_collection": r.shopify_collection} for r in rows])


# ── Membership export (ERPNext -> Shopify) ────────────────────────────────────

def sync_item_collections(item, product_id, client):
    """
    Reconcile a product's manual-collection membership on Shopify against the
    Item's sh_shopify_collections field. Adds to newly-selected collections and
    removes from de-selected ones -- but only for MANUAL collections we manage
    (never smart ones, whose membership is rule-driven and would error).

    product_id is the legacy Shopify product id; client is a live
    ShopifyGraphQLClient. Best-effort: logs and moves on rather than failing
    the whole product push if a membership call errors.
    """
    if not product_id:
        return
    product_gid = f"gid://shopify/Product/{product_id}"

    # desired manual-collection gids from the Item's field
    desired = {}
    for name in _item_collection_names(item):
        row = frappe.db.get_value(
            "Shopify Collection", name, ["sh_collection_gid", "is_smart"], as_dict=True)
        if row and row.sh_collection_gid and not row.is_smart:
            desired[row.sh_collection_gid] = True

    # current collection gids on Shopify, narrowed to ones we know AND manual
    known_manual = set(
        frappe.get_all(
            "Shopify Collection",
            filters={"is_smart": 0, "sh_collection_gid": ["is", "set"]},
            pluck="sh_collection_gid",
        )
    )
    try:
        data = client.execute(_PRODUCT_COLLECTIONS_QUERY, {"id": product_gid})
        current = {
            n.get("id")
            for n in ((data.get("product") or {}).get("collections") or {}).get("nodes", [])
            if n.get("id") in known_manual
        }
    except Exception:
        frappe.log_error(
            title=f"Shopify: could not read collections for product {product_id}",
            message=frappe.get_traceback(),
        )
        return

    to_add = set(desired) - current
    to_remove = current - set(desired)

    for gid in to_add:
        _collection_membership_call(client, _COLLECTION_ADD_PRODUCTS_MUTATION, gid, product_gid, "add", item.name)
    for gid in to_remove:
        _collection_membership_call(client, _COLLECTION_REMOVE_PRODUCTS_MUTATION, gid, product_gid, "remove", item.name)


def _collection_membership_call(client, mutation, collection_gid, product_gid, verb, item_name):
    try:
        data = client.execute(mutation, {"id": collection_gid, "productIds": [product_gid]})
        key = "collectionAddProducts" if verb == "add" else "collectionRemoveProducts"
        errors = (data.get(key) or {}).get("userErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: collection {verb} failed for {item_name}",
                message=f"{collection_gid}: {errors}",
            )
    except Exception:
        frappe.log_error(
            title=f"Shopify: collection {verb} errored for {item_name}",
            message=frappe.get_traceback(),
        )


# ── Collection CRUD push (ERPNext -> Shopify) ─────────────────────────────────

def _collection_input(doc):
    payload = {"title": doc.collection_title}
    if doc.description:
        payload["descriptionHtml"] = doc.description
    if doc.image_url:
        payload["image"] = {"src": doc.image_url}
    return payload


def on_shopify_collection_update(doc, method=None):
    """
    doc_event on Shopify Collection: create it on Shopify if it originated here
    (no gid yet), else push the edit. Skipped for smart collections (rule-based,
    not manually creatable this way) and for saves that came FROM Shopify.
    """
    if doc.flags.from_shopify_sync:
        return
    if doc.is_smart:
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product_sync.push_collection",
        queue="short",
        timeout=60,
        collection_name=doc.name,
    )


def on_shopify_collection_trash(doc, method=None):
    if doc.flags.from_shopify_sync:
        return
    if not doc.sh_collection_gid:
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product_sync.delete_collection",
        queue="short",
        timeout=60,
        collection_gid=doc.sh_collection_gid,
    )


def push_collection(collection_name: str):
    """Create (no gid) or update a collection on Shopify from its local doc."""
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    doc = frappe.get_doc("Shopify Collection", collection_name)
    client = ShopifyGraphQLClient()
    payload = _collection_input(doc)

    try:
        if doc.sh_collection_gid:
            payload["id"] = doc.sh_collection_gid
            data = client.execute(_COLLECTION_UPDATE_MUTATION, {"input": payload})
            result = data.get("collectionUpdate") or {}
        else:
            data = client.execute(_COLLECTION_CREATE_MUTATION, {"input": payload})
            result = data.get("collectionCreate") or {}
        errors = result.get("userErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: collection push failed for {collection_name}",
                message=str(errors),
            )
            return
        col = result.get("collection") or {}
        if col.get("id") and not doc.sh_collection_gid:
            frappe.db.set_value("Shopify Collection", collection_name, {
                "sh_collection_gid": col.get("id"),
                "sh_collection_id": str(col.get("legacyResourceId") or ""),
                "handle": col.get("handle") or "",
            })
            frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: collection push errored for {collection_name}",
            message=frappe.get_traceback(),
        )


def delete_collection(collection_gid: str):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    try:
        data = client.execute(_COLLECTION_DELETE_MUTATION, {"input": {"id": collection_gid}})
        errors = (data.get("collectionDelete") or {}).get("userErrors") or []
        if errors:
            frappe.log_error(
                title="Shopify: collection delete failed",
                message=f"{collection_gid}: {errors}",
            )
    except Exception:
        frappe.log_error(
            title="Shopify: collection delete errored",
            message=frappe.get_traceback(),
        )


# ── Webhook handler (Shopify -> ERPNext) ──────────────────────────────────────

def handle_collection_webhook(topic, payload):
    """
    collections/create|update -> upsert the cache doc; collections/delete ->
    remove it. Webhook payload is REST-shaped (id, title, handle, body_html,
    image, and for smart collections a non-null rules/disjunctive block).
    """
    try:
        legacy = str(payload.get("id") or "")
        if not legacy:
            return

        if topic == "collections/delete":
            name = frappe.db.get_value("Shopify Collection", {"sh_collection_id": legacy}, "name")
            if name:
                doc = frappe.get_doc("Shopify Collection", name)
                doc.flags.from_shopify_sync = True
                doc.flags.ignore_permissions = True
                doc.delete()
                frappe.db.commit()
            return

        # create / update -- reshape REST payload into the node shape the cache
        # upsert already consumes.
        node = {
            "legacyResourceId": legacy,
            "id": _collection_gid(legacy),
            "title": payload.get("title"),
            "handle": payload.get("handle"),
            "descriptionHtml": payload.get("body_html"),
            "image": {"url": (payload.get("image") or {}).get("src")} if payload.get("image") else None,
            "ruleSet": {"rules": payload.get("rules")} if payload.get("rules") else None,
        }
        _upsert_collection_cache(node)
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Shopify: collection webhook {topic} failed",
            message=frappe.get_traceback(),
        )
