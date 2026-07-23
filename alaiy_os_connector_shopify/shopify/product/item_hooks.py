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
