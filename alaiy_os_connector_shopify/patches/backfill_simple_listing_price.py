"""
One-time backfill: for simple/no-variant Listings whose listing_price is
blank, copy in the real resolved Item Price so the Desk form shows an
actual number instead of relying purely on the blank-inherits-from-Item
fallback (a Currency field displays blank as 0.00, easy to mistake for
"price not set" even when push-time resolution is correct).

Idempotent: only touches rows that are actually blank; safe to re-run.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.pricing import _variant_price


def execute():
    settings = frappe.get_single("Shopify Connector Settings")
    rows = frappe.db.sql("""
        SELECT l.name, l.item
        FROM `tabShopify Product Listing` l
        JOIN `tabItem` i ON i.name = l.item
        WHERE i.has_variants = 0
          AND (l.listing_price IS NULL OR l.listing_price = 0)
    """, as_dict=True)

    updated = 0
    for r in rows:
        price = _variant_price(r.item, settings)
        if price is not None and price > 0:
            frappe.db.set_value("Shopify Product Listing", r.name, "listing_price", price)
            updated += 1

    if updated:
        frappe.db.commit()
    frappe.logger().info(f"Simple listing price backfill: {updated}/{len(rows)} row(s) updated")
