"""
One-time backfill: fill listing_category / listing_product_type on any
existing Shopify Product Listing that has them blank, from the matching
Item's sh_shopify_category / sh_shopify_product_type.

Gap: these two Listing fields are new (added alongside the existing
listing_title/description/price override pattern) -- ensure_listing() leaves
them blank on creation, relying on the resolver's Item fallback at push time,
so every Listing that existed before this change looks empty on the form
even once its Item's category/product_type get set.

Idempotent: only touches rows that are actually blank; safe to re-run.
"""

import frappe


def execute():
    rows = frappe.db.sql("""
        SELECT l.name, i.sh_shopify_category, i.sh_shopify_product_type
        FROM `tabShopify Product Listing` l
        JOIN `tabItem` i ON i.name = l.item
        WHERE (l.listing_category IS NULL OR l.listing_category = '')
           OR (l.listing_product_type IS NULL OR l.listing_product_type = '')
    """, as_dict=True)

    updated = 0
    for r in rows:
        values = {}
        if r.sh_shopify_category:
            values["listing_category"] = r.sh_shopify_category
        if r.sh_shopify_product_type:
            values["listing_product_type"] = r.sh_shopify_product_type
        if values:
            frappe.db.set_value("Shopify Product Listing", r.name, values)
            updated += 1

    if rows:
        frappe.db.commit()
    frappe.logger().info(f"Listing category/product_type backfill: {updated}/{len(rows)} row(s) updated")
