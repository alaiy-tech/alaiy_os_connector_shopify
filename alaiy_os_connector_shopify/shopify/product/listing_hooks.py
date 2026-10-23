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

from alaiy_os_connector_shopify import connections


def _connector_enabled(doc=None):
    """Is THIS Listing's store switched on for the connector.

    Confirmed live: disabling Shopify Connector Settings.is_enabled did NOT
    stop on_listing_trash/on_listing_update from still enqueuing a real
    push/archive against the live store, since neither function read this
    field at all. A bulk local deletion (e.g. wiping the catalogue for a
    clean re-import) with the connector "disabled" would otherwise still
    archive the real Shopify catalogue underneath it. Checked once, used at
    the top of every function in this module that can enqueue outbound
    work.

    Reads the store off the Listing itself, not off "the" enabled store --
    that stopped naming a single answer once a bench can enable more than
    one. `doc=None` falls back to the single-enabled-store check, matching
    this connector's pre-multi-store behaviour exactly.

    A Listing created before that field existed carries no store, and the
    fallback has to answer for it. `enabled_connection` cannot on a bench with
    several enabled, where it returns None and this gate reads that as
    "switched off" -- every pre-backfill Listing then stops pushing without
    saying so. The Listing's own Item is asked first, since an Item that has
    been through an import or a push carries the store the Listing is missing;
    only when that is blank too is there genuinely nothing to go on, and then
    nothing is pushed rather than pushed at a guessed store."""
    if doc is None:
        return connections.enabled_connection() is not None
    if doc.get("connection"):
        return True
    if doc.get("item") and frappe.db.get_value("Item", doc.item, "sh_shopify_connection"):
        return True
    return connections.enabled_connection() is not None


# ── Shopify Product Listing doc_events ───────────────────────────────────────

def on_listing_update(doc, method=None):
    """
    A Listing (or any of its variant/image child rows -- they save with the
    parent) changed: push the product if enabled. is_enabled ("Enable Sync")
    only gates whether local edits keep auto-pushing to Shopify -- it is not
    a status control. Turning it off just stops syncing; it must never
    archive the live Shopify product on its own. Archived/Active/Draft is
    controlled solely by the Listing's own sh_shopify_status field (pushed
    via publish_now / push_item's productSet, or the archive/unarchive
    actions that explicitly set it) -- never as a side effect of this toggle.

    Turning is_enabled on does NOT push. For a Listing that already has a real
    sh_shopify_product_id it records the current local state as already in sync
    (see _adopt_current_state) and sends nothing, so enabling is a pure switch
    and only later edits push. A Listing that was never published has no product
    id, so enabling it cannot create a Shopify product either: its first push
    goes through an explicit publish call (product_sync.push_item with
    force=True).
    """
    if doc.flags.from_shopify_sync:
        # Provisioning insert (backfill / inbound import) -- data mirrored
        # from an existing Item, pushing it back would be a pointless echo.
        return
    if not _connector_enabled(doc):
        return
    if doc.is_enabled and doc.sh_shopify_product_id:
        before = doc.get_doc_before_save()
        if should_adopt_on_enable(doc.is_enabled, before.is_enabled if before else None):
            _adopt_current_state(doc)
            return
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.push_item",
            queue="short", timeout=120, item_code=doc.item,
            enqueue_after_commit=True,
        )


def should_adopt_on_enable(is_enabled, was_enabled) -> bool:
    """True only for the save that switches Enable Sync from off to on.

    `was_enabled` is None when the Listing has no before-image (a first insert),
    which keeps the existing behaviour: a brand-new Listing is not an enable of
    something that already exists on Shopify.
    """
    return bool(is_enabled) and was_enabled is not None and not was_enabled


def _adopt_current_state(doc):
    """Switching Enable Sync on records the product as already in sync; nothing
    is sent.

    While sync was off the importer kept no push fingerprint (see
    webhooks._refresh_push_fingerprint), so the first push after enabling would
    be a full productSet of everything the Listing holds -- titles, descriptions,
    images, tags, variants, metafields -- over whatever is live on Shopify,
    including enriched content that was never published. Storing the fingerprint
    of the current local state makes that push, and the hourly sweep, see "no
    change" until someone actually edits the product. The edit that follows
    pushes as usual.

    If the state cannot be recorded, Enable Sync is put back off and the error is
    raised: leaving it on with no fingerprint is exactly the full push this
    exists to avoid.
    """
    from alaiy_os_connector_shopify.shopify.sync_engine import entities, fingerprint
    from alaiy_os_connector_shopify.shopify.product.canonical import _product_canonical
    from alaiy_os_connector_shopify.shopify.product.export import _variants_of

    try:
        item = frappe.get_doc("Item", doc.item)
        conn = item.get("sh_shopify_connection") or doc.get("connection")
        settings = connections.resolve(conn) if conn else connections.require_enabled()
        canonical = _product_canonical(item, _variants_of(item), settings, doc)
        entity = entities.get_or_new(
            "product", "Item", item.name, doc.sh_shopify_product_id, connection=settings)
        entities.save(
            entity,
            external_id=doc.sh_shopify_product_id,
            erpnext_doctype="Item",
            erpnext_name=item.name,
            erpnext_fingerprint=fingerprint.fingerprint(canonical),
        )
    except Exception:
        frappe.db.set_value("Shopify Product Listing", doc.name, "is_enabled", 0)
        raise


def check_adopt_on_enable():
    """Self-check for the enable transition. No DB, no API.

    bench --site <site> execute         alaiy_os_connector_shopify.shopify.product.listing_hooks.check_adopt_on_enable
    """
    assert should_adopt_on_enable(1, 0) is True
    assert should_adopt_on_enable(1, 1) is False
    assert should_adopt_on_enable(0, 0) is False
    assert should_adopt_on_enable(0, 1) is False
    # No before-image: a first insert, never an enable of an existing product.
    assert should_adopt_on_enable(1, None) is False
    print("adopt-on-enable self-check passed")


def on_listing_trash(doc, method=None):
    """Deleting the Listing just unlinks it locally -- it must never archive
    the live Shopify product as a side effect. Archiving is an explicit
    status action (sh_shopify_status), not something a local delete should
    trigger on its own."""
    return


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
