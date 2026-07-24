"""
#60: one-time backfill for Shopify Product Listing / Shopify Listing Variant
rows whose id fields are blank even though the matching Item already has one.

Gap: sync_listing_variants only APPENDS a row for a variant that isn't
listed yet -- it never backfills an id onto a row that already exists with
a blank sh_shopify_variant_id. Any Listing (or Listing Variant row) created
before the #60 dual-write went live can carry stale blanks. Since every
read site now checks the Listing first and only falls back to Item when
blank, a blank-but-existing Listing id is silently WRONG (looks final, but
isn't) rather than falling through -- this backfill closes that gap before
Item's copy is ever dropped (step 8).

Idempotent: only touches rows that are actually blank; safe to re-run.
"""

import frappe


def execute():
    _backfill_templates()
    _backfill_variants()


def _backfill_templates():
    rows = frappe.db.sql("""
        SELECT i.name, i.sh_shopify_product_id
        FROM `tabItem` i
        JOIN `tabShopify Product Listing` l ON l.name = i.name
        WHERE i.sh_shopify_product_id IS NOT NULL AND i.sh_shopify_product_id != ''
          AND (l.sh_shopify_product_id IS NULL OR l.sh_shopify_product_id = '')
    """, as_dict=True)
    for r in rows:
        frappe.db.set_value("Shopify Product Listing", r.name, "sh_shopify_product_id", r.sh_shopify_product_id)
    if rows:
        frappe.db.commit()
    frappe.logger().info(f"Listing id backfill: {len(rows)} template(s) fixed")


def _backfill_variants():
    # Existing Listing Variant row with a blank id -- fill it from the Item.
    rows = frappe.db.sql("""
        SELECT lv.name AS row_name, i.sh_shopify_variant_id
        FROM `tabShopify Listing Variant` lv
        JOIN `tabItem` i ON i.name = lv.item_variant
        WHERE i.sh_shopify_variant_id IS NOT NULL AND i.sh_shopify_variant_id != ''
          AND (lv.sh_shopify_variant_id IS NULL OR lv.sh_shopify_variant_id = '')
    """, as_dict=True)
    for r in rows:
        frappe.db.set_value("Shopify Listing Variant", r.row_name, "sh_shopify_variant_id", r.sh_shopify_variant_id)

    # Item variant with an id but no Listing Variant row at all -- create one,
    # same shape sync_listing_variants uses for a freshly-seen variant.
    missing = frappe.db.sql("""
        SELECT i.name, i.variant_of, i.sh_shopify_variant_id
        FROM `tabItem` i
        LEFT JOIN `tabShopify Listing Variant` lv
            ON lv.parent = i.variant_of AND lv.item_variant = i.name
        WHERE i.sh_shopify_variant_id IS NOT NULL AND i.sh_shopify_variant_id != ''
          AND i.variant_of IS NOT NULL AND i.variant_of != ''
          AND lv.name IS NULL
          AND EXISTS (SELECT 1 FROM `tabShopify Product Listing` p WHERE p.name = i.variant_of)
    """, as_dict=True)
    created = 0
    for m in missing:
        listing = frappe.get_doc("Shopify Product Listing", m.variant_of)
        listing.append("variants", {
            "item_variant": m.name, "is_enabled": 1,
            "sh_shopify_variant_id": m.sh_shopify_variant_id,
        })
        listing.flags.from_shopify_sync = True
        listing.save(ignore_permissions=True)
        created += 1

    if rows or created:
        frappe.db.commit()
    frappe.logger().info(
        f"Listing id backfill: {len(rows)} variant row(s) fixed, {created} row(s) created"
    )
