"""
Item validate hook: UOM dedup.

The old Item push machine (on_item_change / on_item_delete /
on_item_price_change / _sync_enabled) lived here -- it was removed when the
Shopify Product Listing became the sole push trigger and enable gate. Item
saves no longer sync to Shopify; see shopify/product/listing_hooks.py and
shopify/product/listing.py. Only the UOM-dedup validate hook remains an
Item-level concern.
"""

import frappe

from alaiy_os_connector_shopify import connections


def resolve_shopify_category_gid(doc, method=None):
    """
    sh_shopify_category is a Link to Shopify Category, named by its human
    path string ("Home & Garden / Linens & Bedding / Towels / ..."), not
    the Shopify taxonomy GID. A raw GID can't go directly into that field
    for a bulk CSV upload -- confirmed live: Frappe's Data Import tool
    pre-validates Link field values against existing doc names BEFORE a
    row ever reaches this validate hook, so the import fails outright
    with "value does not exist" rather than ever giving this function a
    chance to resolve it.

    sh_shopify_category_gid is a plain Data field with no such check --
    CSV uploads map their category_id column there instead, and that
    column can hold three different kinds of value depending on how the
    supplier feed was built: a real GID, a bare leaf category name (e.g.
    "Cat Toys"), or -- since a CSV can be hand-edited -- the exact Shopify
    Category doc name (its full path string) already. Resolve whichever
    one it turns out to be into the real Link field here and clear the
    staging field.
    """
    value = (doc.sh_shopify_category_gid or "").strip()
    if not value:
        return

    if frappe.db.exists("Shopify Category", value):
        # Already the exact doc name (full path) -- no resolution needed.
        resolved = value
    elif value.startswith("gid://shopify/TaxonomyCategory/"):
        resolved = frappe.db.get_value("Shopify Category", {"shopify_category_id": value}, "name")
        if not resolved:
            frappe.throw(f"No Shopify Category found for GID {value}")
    else:
        # Bare leaf name -- match the same way the one-time reparent script
        # does: exact name match only, preferring a real nested node over a
        # standalone no-parent duplicate (partial-import leftover noise),
        # never guessing on a genuine ambiguity.
        matches = frappe.get_all(
            "Shopify Category", filters={"shopify_category_name": value},
            fields=["name", "parent_shopify_category"],
        )
        nested = [m for m in matches if m.parent_shopify_category]
        if len(nested) == 1:
            matches = nested
        if not matches:
            frappe.throw(f"No Shopify Category found named {value!r}")
        if len(matches) > 1:
            frappe.throw(
                f"{value!r} matches multiple Shopify Category nodes -- "
                f"use the exact GID instead: {[m.name for m in matches]}"
            )
        resolved = matches[0].name

    doc.sh_shopify_category = resolved
    doc.sh_shopify_category_gid = None


def ensure_listing_for_new_item(doc, method=None):
    """
    Item after_insert hook: give every new TEMPLATE Item (has_variants=1, or
    a standalone simple product with no variant_of) a Shopify Product
    Listing straight away, disabled by default (ensure_listing's own
    default_enabled=0 -- never auto-pushes). Without this, a merchant-
    created product with no prior Shopify import/push activity could sit
    indefinitely with no Listing at all, silently unable to ever push
    until something else happened to trigger ensure_listing() first (an
    import cycle, or manually opening the Listing list) -- a real gap
    found in a full feature audit of the Listing abstraction.

    A variant Item (doc.variant_of set) never gets its own Listing --
    Listing is 1:1 with the template, per listing.py's own design note.

    Skipped entirely while the connector is disabled. This hook fires on EVERY
    new Item on the site, including items another connector imported, so on a
    tenant that does not sell through Shopify it produced one dead Listing per
    item -- confirmed live: a catalogue import from another connector created
    5,929 of them on a site where Shopify was never configured. Nothing reached
    Shopify (they are created disabled, and there was no store to reach), but
    each one cost an extra document insert during the import.

    Enabling the connector later is covered: backfill_missing_listings() runs on
    the settings save that switches it on, so the gap this hook exists to close
    stays closed.
    """
    if not should_create_listing(doc.variant_of, connections.enabled_value("is_enabled")):
        return
    from alaiy_os_connector_shopify.shopify.product.listing import ensure_listing
    ensure_listing(doc.name, default_enabled=0)


def should_create_listing(variant_of, connector_enabled) -> bool:
    """The after_insert gate, as a function of plain values.

    Split out of the hook so check_listing_gating can exercise the rule
    directly. `connector_enabled` is whatever connections.enabled_value
    returned, so None ("no store switched on") has to read as off.
    """
    return not variant_of and bool(connector_enabled)


def validate_item_uoms(doc, method=None):
    """
    Validation hook on Item before saving to automatically deduplicate
    the UOM conversion factors for both template and variant Items.
    This prevents standard Alaiy OS validation errors from blocking
    Desk UI saves and webhook runs.
    """
    # 1. Clean up the document's own in-memory UOMs list first
    seen_uoms = set()
    deduped = []
    has_duplicates = False
    for row in doc.get("uoms") or []:
        if row.uom in seen_uoms:
            has_duplicates = True
            continue
        seen_uoms.add(row.uom)
        deduped.append(row)

    if has_duplicates:
        doc.set("uoms", deduped)

    # 2. Database level cleanup for the current Item and all variants
    all_item_names = [doc.name]
    if doc.has_variants:
        all_item_names += frappe.get_all("Item", filters={"variant_of": doc.name}, pluck="name")
    elif doc.variant_of:
        # If it's a variant, also clean the template and other sibling variants
        all_item_names.append(doc.variant_of)
        all_item_names += frappe.get_all("Item", filters={"variant_of": doc.variant_of}, pluck="name")
        all_item_names = list(set(all_item_names))

    for name in all_item_names:
        duplicates = frappe.db.sql("""
            SELECT uom, MIN(name) as keep_name
            FROM `tabUOM Conversion Detail`
            WHERE parent = %s
            GROUP BY uom
            HAVING COUNT(*) > 1
        """, name, as_dict=True)

        for dup in duplicates:
            frappe.db.sql("""
                DELETE FROM `tabUOM Conversion Detail`
                WHERE parent = %s AND uom = %s AND name != %s
            """, (name, dup.uom, dup.keep_name))


def backfill_missing_listings(batch=None):
    """Create a disabled Listing for every template Item that has none.

    ensure_listing_for_new_item only fires while the connector is enabled, so a
    site that imports its catalogue first and connects Shopify afterwards would
    otherwise have thousands of Items with no Listing and no way to push them.
    This runs on the settings save that enables the connector, and can be called
    by hand at any time -- it is idempotent, an Item that already has a Listing
    is left untouched.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.item_hooks.backfill_missing_listings
    """
    from alaiy_os_connector_shopify.shopify.product.listing import ensure_listing

    # "is set" rather than ["not in", ["", None]] -- SQL `NOT IN (…, NULL)` is
    # never true, so that filter silently matches zero rows.
    templates = frappe.get_all(
        "Item", filters={"variant_of": ["in", ["", None]]},
        pluck="name", limit_page_length=int(batch) if batch else 0)

    created = skipped = failed = 0
    for name in templates:
        if frappe.db.exists("Shopify Product Listing", name):
            skipped += 1
            continue
        try:
            ensure_listing(name, default_enabled=0)
            created += 1
        except Exception:
            failed += 1
            frappe.log_error(
                title=f"Shopify: listing backfill failed for {name}",
                message=frappe.get_traceback(),
            )
        if created and created % 200 == 0:
            frappe.db.commit()

    frappe.db.commit()
    print(f"[listings] created {created}, already present {skipped}, failed {failed}")
    return {"created": created, "skipped": skipped, "failed": failed}


def backfill_listings_on_enable(doc, method=None):
    """Shopify Connection on_update: backfill Listings when switched on.

    Only acts on the save that flips is_enabled from off to on -- comparing
    against the pre-save value, so re-saving an already-enabled settings doc does
    not walk the whole Item table again.
    """
    if not doc.is_enabled:
        # Cheap short-circuit: a save that is not switching anything on does not
        # need its before-image loaded.
        return
    before = doc.get_doc_before_save()
    if not should_backfill_on_enable(doc.is_enabled, before.is_enabled if before else None):
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product.item_hooks.backfill_missing_listings",
        queue="long", timeout=3600,
    )


def should_backfill_on_enable(is_enabled, was_enabled) -> bool:
    """Backfill only on the off -> on transition.

    `was_enabled` is None when the settings doc has no before-image at all --
    its first-ever save -- which is a transition into enabled.
    """
    return bool(is_enabled) and not was_enabled


def check_listing_gating():
    """Self-check for the enable gating. No DB, no API, nothing patched.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.item_hooks.check_listing_gating
    """
    # A variant never gets a Listing, connector on or off -- Listing is 1:1 with
    # the template.
    assert should_create_listing("TEMPLATE", 1) is False
    assert should_create_listing("TEMPLATE", 0) is False

    # Connector off: a template gets nothing. This is the whole fix -- a
    # catalogue import on a non-Shopify tenant must not leave a Listing per item
    # behind. No enabled store at all reads back as None, and means off too.
    assert should_create_listing(None, 0) is False
    assert should_create_listing(None, None) is False
    assert should_create_listing("", 0) is False

    # Connector on: a template gets its Listing (created disabled by the caller).
    assert should_create_listing(None, 1) is True
    assert should_create_listing("", 1) is True

    # Switching the connector on backfills, but only on the transition, so
    # re-saving an already-enabled settings doc does not walk the Item table.
    assert should_backfill_on_enable(0, 0) is False
    assert should_backfill_on_enable(0, 1) is False
    assert should_backfill_on_enable(1, 1) is False
    assert should_backfill_on_enable(1, 0) is True
    # First-ever save of the settings doc has no before-image.
    assert should_backfill_on_enable(1, None) is True

    print("listing gating self-check passed")
