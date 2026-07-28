"""
Remove the legacy Item.sh_shopify_product_id / Item.sh_shopify_variant_id
custom fields, closing #61.

Every read site has resolved the Listing/Listing Variant copy first for
weeks (see shopify.product.listing's id-ownership helpers), falling back
to these Item fields only for a row that hadn't been dual-written to yet.
backfill_listing_ids and backfill_simple_item_variant_rows close that gap
for every existing row, so nothing is lost by dropping Item's copy now.

NOT wired into patches.txt on purpose -- this drops columns, a one-way
schema change. Run it by hand, per site, only after confirming zero
Listings/Listing Variant rows have a blank id where the matching Item has
one:

    SELECT l.name FROM `tabShopify Product Listing` l
    JOIN `tabItem` i ON i.name = l.item
    WHERE l.sh_shopify_product_id != i.sh_shopify_product_id;

    SELECT v.name FROM `tabShopify Listing Variant` v
    JOIN `tabItem` i ON i.name = v.item_variant
    WHERE i.sh_shopify_variant_id IS NOT NULL AND i.sh_shopify_variant_id != ''
      AND (v.sh_shopify_variant_id IS NULL OR v.sh_shopify_variant_id != i.sh_shopify_variant_id);

Both must return zero rows on a site before running:
    bench --site <site> execute alaiy_os_connector_shopify.patches.drop_legacy_item_shopify_ids.execute
"""

import json

import frappe


def execute():
    for fieldname in ("sh_shopify_product_id", "sh_shopify_variant_id"):
        key = f"Item-{fieldname}"
        if frappe.db.exists("Custom Field", key):
            frappe.delete_doc("Custom Field", key, ignore_permissions=True)
        if fieldname in frappe.db.get_table_columns("Item"):
            frappe.db.sql_ddl(f"ALTER TABLE `tabItem` DROP COLUMN `{fieldname}`")

    _scrub_list_view_refs()
    frappe.db.commit()


def _scrub_list_view_refs():
    """Same cleanup drop_sync_to_shopify_field did: strip the dropped fields
    from Item's List View Settings and clear per-user saved Item-list state
    that might reference them, or the list view errors on load."""
    if frappe.db.exists("List View Settings", "Item"):
        s = frappe.get_doc("List View Settings", "Item")
        dropped = {"sh_shopify_product_id", "sh_shopify_variant_id"}
        fields = [f for f in json.loads(s.fields or "[]") if f.get("fieldname") not in dropped]
        s.fields = json.dumps(fields)
        s.save(ignore_permissions=True)
    frappe.db.delete("__UserSettings", {"doctype": "Item"})
