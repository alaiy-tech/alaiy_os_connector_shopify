"""
One-time backfill: copy each variant Item's own image into its Shopify
Listing Variant row's variant_image, for any row that's currently blank.

Gap: variant_image is a new field (added alongside HS code/country of
origin/variant-level export support) -- ensure_listing() never populated
it on creation, so every existing Listing Variant row is blank even
though its Item already has a real per-variant image set.

Idempotent: only touches rows that are actually blank; safe to re-run.
"""

import frappe


def execute():
    rows = frappe.db.sql("""
        SELECT lv.name, i.image
        FROM `tabShopify Listing Variant` lv
        JOIN `tabItem` i ON i.name = lv.item_variant
        WHERE (lv.variant_image IS NULL OR lv.variant_image = '')
          AND i.image IS NOT NULL AND i.image != ''
    """, as_dict=True)

    for r in rows:
        frappe.db.set_value("Shopify Listing Variant", r.name, "variant_image", r.image)

    if rows:
        frappe.db.commit()
    frappe.logger().info(f"Listing variant image backfill: {len(rows)} row(s) updated")
