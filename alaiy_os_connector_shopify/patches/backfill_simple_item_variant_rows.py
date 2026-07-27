"""
One-time backfill: give every simple (non-variant) product's Listing a
self-referencing Shopify Listing Variant row (item_variant = the item
itself), the same shape a template's child variants already get.

Gap: a simple product still has exactly one variant on Shopify's side --
our Listing schema just never gave that variant a row of its own, so its
Shopify variant id had no home except Item.sh_shopify_variant_id. Existing
Listings created before shopify.product.listing._template_variant_items
started covering this case are missing that row.

Idempotent: only touches Listings that don't already have a matching row.
"""

import frappe


def execute():
    rows = frappe.db.sql("""
        SELECT l.name AS listing, i.sh_shopify_variant_id
        FROM `tabShopify Product Listing` l
        JOIN `tabItem` i ON i.name = l.item
        WHERE i.has_variants = 0
          AND NOT EXISTS (
              SELECT 1 FROM `tabShopify Listing Variant` v
              WHERE v.parent = l.name AND v.item_variant = l.item
          )
    """, as_dict=True)

    for r in rows:
        listing = frappe.get_doc("Shopify Product Listing", r.listing)
        listing.append("variants", {
            "item_variant": r.listing, "is_enabled": 1,
            "sh_shopify_variant_id": r.sh_shopify_variant_id or None,
        })
        listing.flags.from_shopify_sync = True
        listing.save(ignore_permissions=True)

    if rows:
        frappe.db.commit()
    frappe.logger().info(f"Simple-item variant row backfill: {len(rows)} listing(s) fixed")
