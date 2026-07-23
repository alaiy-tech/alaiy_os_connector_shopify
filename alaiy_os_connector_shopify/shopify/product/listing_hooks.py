"""
Shopify Product Listing doc_events + the two slim Item hooks that keep
desk-side variant add/delete flowing to Shopify now that Item saves no
longer push on their own.

The Listing is the trigger and the sole enable gate (replacing the old
Item.sync_to_shopify-driven item_hooks.on_item_change): saving an enabled
Listing pushes its product; disabling it archives; trashing it unlinks.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver


# ── Shopify Product Listing doc_events ───────────────────────────────────────

def on_listing_update(doc, method=None):
    """
    A Listing (or any of its variant/image child rows -- they save with the
    parent) changed: push the product if enabled, archive it if just
    disabled. Mirrors the old on_item_change enable/disable machine, keyed
    off the Listing instead of Item.sync_to_shopify.
    """
    if doc.flags.from_shopify_sync:
        # Provisioning insert (backfill / inbound import) -- data mirrored
        # from an existing Item, pushing it back would be a pointless echo.
        return
    if doc.is_enabled:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.push_item",
            queue="short", timeout=120, item_code=doc.item,
        )
    elif doc.sh_shopify_product_id:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.archive_item",
            queue="short", timeout=60, item_code=doc.item,
        )


def on_listing_trash(doc, method=None):
    """Deleting the Listing takes the product off Shopify (archive: hidden,
    order history intact), same terminal state as unchecking then removing."""
    if doc.sh_shopify_product_id:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.archive_item",
            queue="short", timeout=60, item_code=doc.item,
        )


# ── Slim Item hooks (data upkeep only -- never push directly) ────────────────

def sync_new_variant_to_listing(doc, method=None):
    """
    Item after_insert. A brand-new variant added in the desk under a template
    that already has a Listing must appear on Shopify without someone opening
    the Listing -- append an enabled Listing Variant row and save, which fires
    on_listing_update -> push. No-op for templates (a fresh product goes live
    by creating/enabling its Listing) and for inbound imports (they own their
    own Listing rows via ensure_listing).
    """
    if doc.flags.from_shopify_sync or not doc.variant_of:
        return
    listing = listing_resolver.get_listing(doc.variant_of)
    if not listing:
        return
    if any(r.item_variant == doc.name for r in listing.variants):
        return
    listing.append("variants", {"item_variant": doc.name, "is_enabled": 1})
    listing.save(ignore_permissions=True)


def remove_variant_from_listing(doc, method=None):
    """
    Item on_trash. Deleting a variant in the desk drops it from Shopify:
    remove its Listing Variant row and save, which re-pushes the rebuilt
    variant set (productSet is full-desired-state, so the dropped variant
    disappears on Shopify). Scoped to variants; deleting a whole product is
    done by trashing its Listing.
    """
    if doc.flags.from_shopify_sync or not doc.variant_of:
        return
    listing = listing_resolver.get_listing(doc.variant_of)
    if not listing:
        return
    rows = [r for r in listing.variants if r.item_variant != doc.name]
    if len(rows) == len(listing.variants):
        return  # variant wasn't listed -- nothing to do
    listing.set("variants", rows)
    listing.save(ignore_permissions=True)
