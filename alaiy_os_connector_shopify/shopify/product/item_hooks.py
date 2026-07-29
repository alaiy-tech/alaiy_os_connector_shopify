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
    """
    if doc.variant_of:
        return
    from alaiy_os_connector_shopify.shopify.product.listing import ensure_listing
    ensure_listing(doc.name, default_enabled=0)


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
