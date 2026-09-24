"""
One-time backfill: fill listing_title / listing_description / listing_price
on any existing Shopify Product Listing that has them blank, from the
matching Item (title/description) or Item Price (price, simple products only).

Gap: ensure_listing() used to leave these blank on creation (relying on the
resolver's Item fallback at push time), so a Listing created before that
changed looks empty on the form even though it already has real content.

Idempotent: only touches rows that are actually blank; safe to re-run.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.pricing import _variant_price

from alaiy_os_connector_shopify import connections


def execute():
    rows = frappe.db.sql("""
        SELECT l.name, l.item, i.item_name, i.description, i.has_variants,
               l.listing_price
        FROM `tabShopify Product Listing` l
        JOIN `tabItem` i ON i.name = l.item
        WHERE (l.listing_title IS NULL OR l.listing_title = '')
           OR (l.listing_description IS NULL OR l.listing_description = '')
           OR (i.has_variants = 0 AND (l.listing_price IS NULL OR l.listing_price = 0))
    """, as_dict=True)

    # A backfill must not fail a migrate on a site that has no Shopify store,
    # so this asks rather than requires. `settings` is only read for its
    # price list / defaults below; with no store there is nothing to backfill.
    settings = connections.enabled_connection()
    if not settings:
        return
    for r in rows:
        values = {}
        if r.item_name:
            values["listing_title"] = r.item_name
        if r.description:
            values["listing_description"] = r.description
        if not r.has_variants and not r.listing_price:
            price = _variant_price(r.item, settings)
            if price is not None:
                values["listing_price"] = price
        if values:
            frappe.db.set_value("Shopify Product Listing", r.name, values)

    if rows:
        frappe.db.commit()
    frappe.logger().info(f"Listing title/description/price backfill: {len(rows)} row(s) checked")
