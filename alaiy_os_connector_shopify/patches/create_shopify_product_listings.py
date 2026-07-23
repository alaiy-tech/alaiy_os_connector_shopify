"""
One-time backfill: create a Shopify Product Listing (+ image/variant child
rows) for every Item already linked to Shopify, so the Listing-driven export
pipeline has a record to read the moment it goes live -- without this, every
already-live Shopify product would silently stop syncing on upgrade.

This is the ONLY reader of the legacy Item.sync_to_shopify field: it copies
that value into each Listing's is_enabled (and per-variant is_enabled) to
preserve exactly which products/variants were syncing before. It MUST run
before drop_sync_to_shopify_field (ordered in patches.txt) -- after that
patch the column is gone.

Idempotent: a template that already has a Listing is skipped, so a partial
run is safe to re-run. Only touches Items with a Shopify product id.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.listing import ensure_listing


def execute():
    # NOTE: use "is set", NOT ["not in", ["", None]] -- SQL `NOT IN (…, NULL)`
    # is never true, so that filter silently matches ZERO rows.
    templates = frappe.get_all(
        "Item",
        filters={
            "variant_of": ["in", ["", None]],
            "sh_shopify_product_id": ["is", "set"],
        },
        pluck="name",
    )

    migrated = skipped = 0
    for name in templates:
        if frappe.db.exists("Shopify Product Listing", name):
            skipped += 1
            continue
        try:
            _backfill_one(name)
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


def _backfill_one(template_name):
    # If sync_to_shopify is already gone (e.g. a re-run after the drop patch),
    # a linked product is live on Shopify, so default it enabled.
    has_flag = "sync_to_shopify" in frappe.db.get_table_columns("Item")
    template_synced = frappe.db.get_value("Item", template_name, "sync_to_shopify") if has_flag else 1
    listing = ensure_listing(template_name, default_enabled=1 if template_synced else 0)
    if not listing or not has_flag:
        return
    # Preserve each variant's old per-variant sync flag onto its Listing row.
    changed = False
    for row in listing.variants:
        old = frappe.db.get_value("Item", row.item_variant, "sync_to_shopify")
        want = 1 if old else 0
        if row.is_enabled != want:
            row.is_enabled = want
            changed = True
    if changed:
        listing.flags.from_shopify_sync = True
        listing.save(ignore_permissions=True)
