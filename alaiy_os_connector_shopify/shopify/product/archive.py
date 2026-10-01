"""
Product archive-on-Shopify -- moved verbatim from product_sync.py,
unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
from alaiy_os_connector_shopify.shopify.product.queries import _PRODUCT_UPDATE_MUTATION
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver
from alaiy_os_connector_shopify.shopify.product import status as status_map

from alaiy_os_connector_shopify import connections

LOCK_TIMEOUT_SECONDS = 30


def archive_item(item_code: str):
    """Called when the Listing is disabled/trashed -- or the Item disabled --
    on a template that's already linked. Archives the Shopify product
    (hidden from sales channels, order history intact) by setting its status
    to ARCHIVED via the productUpdate mutation."""
    item = frappe.get_doc("Item", item_code)
    if item.variant_of:
        return
    # Prefer the Listing's copy of the id (dual-written on every push),
    # fall back to Item's -- Item stays the ultimate owner until every read
    # site has moved, but reads now go through the Listing first.
    listing = listing_resolver.get_listing(item.name)
    product_id = (listing.sh_shopify_product_id if listing else None) or item.get("sh_shopify_product_id")
    if not product_id:
        return
    if listing_resolver.is_enabled(item):
        # Re-enabled before this job ran -- don't archive what should stay active.
        return

    try:
        item.lock(timeout=LOCK_TIMEOUT_SECONDS)
    except frappe.DocumentLockedError:
        return

    try:
        item = frappe.get_doc("Item", item.name)
        conn = item.get("sh_shopify_connection")
        client = ShopifyGraphQLClient(connections.resolve(conn) if conn else connections.require_enabled())

        data = client.execute(_PRODUCT_UPDATE_MUTATION, {
            "input": {
                "id": f"gid://shopify/Product/{product_id}",
                "status": "ARCHIVED",
            }
        })
        errors = (data.get("productUpdate") or {}).get("userErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: archive failed for {item.name}",
                message=str(errors),
            )
        else:
            # canonical.py's own push payload reads sh_shopify_status as the
            # Active/Draft input and assumes ("pushing never leaves ARCHIVED
            # -- archive_item() overrides this back to ARCHIVED explicitly")
            # that this write already happens here. It never did -- the
            # Listing's copy sat frozen at whatever it was seeded to when
            # first created, forever, since nothing else in the connector
            # ever writes it again.
            if listing and listing.sh_shopify_status != "Archived":
                listing.db_set("sh_shopify_status", "Archived", update_modified=False)
                # nosemgrep: committed independently of the fingerprint-clear
                # block below, which has its own separate commit and can be
                # skipped entirely (no entity found) or fail on its own --
                # the fact that Shopify really did archive this product must
                # be durable on its own, not bundled with a second, unrelated
                # write that might not run at all.
                frappe.db.commit()
            # Same write, on the Item. This function never touched it before --
            # confirmed live, 230 Item/Listing sh_shopify_status mismatches
            # across the catalogue, this path being one real cause. Most
            # reads (admin aggregates, reports, low-stock scoping) still key
            # off Item.sh_shopify_status; leaving it stale there mislabels a
            # genuinely-archived product as Active in every one of them.
            if item.get("sh_shopify_status") != "Archived":
                frappe.db.set_value("Item", item.name, "sh_shopify_status", "Archived", update_modified=False)
                frappe.db.commit()

            # Clear fingerprint on successful archive so a subsequent push_item
            # (when re-enabled or unarchived) detects the status change and pushes.
            from alaiy_os_connector_shopify.shopify.sync_engine import entities
            entity = entities.get_by_erpnext("product", "Item", item.name, connection=conn)
            if entity:
                entity.erpnext_fingerprint = None
                entity.save(ignore_permissions=True)
                frappe.db.commit()
    finally:
        item.unlock()


def set_product_status(item_code: str, status: str):
    """Set a product's status on Shopify (Active, Draft or Archived), whether or
    not continuous sync is on.

    Status only: it sends productUpdate with the status and nothing else, so it
    cannot overwrite any other field with this app's copy. The local Listing and
    Item copies are written only after Shopify accepts the change, and the
    push fingerprint is cleared so the next push sees the new status.

    A product that has never been pushed has no Shopify status to change; the
    Listing's status is recorded instead and used when it is first published.
    Returns {"ok": True, "pushed": bool}, or {"ok": False, "reason": str}.
    """
    if status not in status_map.LOCAL_VALUES:
        return {"ok": False, "reason": f"Status must be one of {', '.join(status_map.LOCAL_VALUES)}."}

    item = frappe.get_doc("Item", item_code)
    template = frappe.get_doc("Item", item.variant_of) if item.variant_of else item
    listing = listing_resolver.get_listing(template.name)
    if not listing:
        return {"ok": False, "reason": "This item has no Shopify Product Listing yet."}

    product_id = listing.sh_shopify_product_id or template.get("sh_shopify_product_id")
    pushed = False
    if product_id:
        conn = template.get("sh_shopify_connection")
        client = ShopifyGraphQLClient(connections.resolve(conn) if conn else connections.require_enabled())
        data = client.execute(_PRODUCT_UPDATE_MUTATION, {
            "input": {
                "id": f"gid://shopify/Product/{product_id}",
                "status": status_map.TO_SHOPIFY[status],
            }
        })
        errors = (data.get("productUpdate") or {}).get("userErrors") or []
        if errors:
            return {"ok": False, "reason": "; ".join(e.get("message", "") for e in errors)}
        pushed = True

    # Written after Shopify has accepted the change, and left to the request's
    # own commit: this runs inside an admin request, which commits on success.
    if listing.sh_shopify_status != status:
        listing.db_set("sh_shopify_status", status, update_modified=False)
    if template.get("sh_shopify_status") != status:
        frappe.db.set_value("Item", template.name, "sh_shopify_status", status, update_modified=False)

    if pushed:
        from alaiy_os_connector_shopify.shopify.sync_engine import entities
        entity = entities.get_by_erpnext("product", "Item", template.name, connection=template.get("sh_shopify_connection"))
        if entity:
            entity.db_set("erpnext_fingerprint", None, update_modified=False)
    return {"ok": True, "pushed": pushed}
