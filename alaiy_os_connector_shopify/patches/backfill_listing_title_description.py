"""
One-time backfill: fill listing_title / listing_description on any existing
Shopify Product Listing that has them blank, from the matching Item.

Gap: ensure_listing() used to leave these blank on creation (relying on the
resolver's Item fallback at push time), so a Listing created before that
changed looks empty on the form even though it already has real content.

Idempotent: only touches rows that are actually blank; safe to re-run.
"""

import frappe


def execute():
    rows = frappe.db.sql("""
        SELECT l.name, i.item_name, i.description
        FROM `tabShopify Product Listing` l
        JOIN `tabItem` i ON i.name = l.item
        WHERE (l.listing_title IS NULL OR l.listing_title = '')
           OR (l.listing_description IS NULL OR l.listing_description = '')
    """, as_dict=True)

    for r in rows:
        values = {}
        if r.item_name:
            values["listing_title"] = r.item_name
        if r.description:
            values["listing_description"] = r.description
        if values:
            frappe.db.set_value("Shopify Product Listing", r.name, values)

    if rows:
        frappe.db.commit()
    frappe.logger().info(f"Listing title/description backfill: {len(rows)} row(s) checked")
