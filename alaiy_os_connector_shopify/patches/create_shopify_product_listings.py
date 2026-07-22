"""
One-time backfill: create a Shopify Product Listing (+ image/variant child
rows) for every Item already linked to Shopify, so the Listing-driven export
pipeline has a record to read the moment it goes live -- without this, every
already-live Shopify product would silently stop syncing on upgrade.

Idempotent: a template that already has a Listing is skipped, so a partial
run is safe to re-run. Only touches Items with a Shopify product id -- never
creates Listings for products that were never on Shopify. Creation logic
lives in shopify.product.listing.ensure_listing (shared with the inbound
importer) so there is exactly one definition of "build a Listing from an Item".
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.listing import ensure_listing


def execute():
    templates = frappe.get_all(
        "Item",
        filters={
            "variant_of": ["in", ["", None]],
            "sh_shopify_product_id": ["not in", ["", None]],
        },
        pluck="name",
    )

    migrated = skipped = 0
    for name in templates:
        if frappe.db.exists("Shopify Product Listing", name):
            skipped += 1
            continue
        try:
            ensure_listing(name)
            migrated += 1
        except Exception:
            frappe.log_error(
                title=f"Listing backfill failed for {name}",
                message=frappe.get_traceback(),
            )

    frappe.db.commit()
    frappe.logger().info(
        f"Shopify Product Listing backfill: {migrated} created, {skipped} already existed"
    )
