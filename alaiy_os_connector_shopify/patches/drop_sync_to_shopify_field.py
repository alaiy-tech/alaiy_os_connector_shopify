"""
Remove the legacy Item.sync_to_shopify custom field. Its role (the Shopify
enable gate) is fully taken over by Shopify Product Listing.is_enabled, and
no code reads it after the listings cutover. create_shopify_product_listings
copies its value into each Listing first (ordered before this in
patches.txt), so nothing is lost.

Only sync_to_shopify is dropped here -- sh_shopify_product_id /
sh_shopify_variant_id stay on Item this phase (still the lookup source for
order matching, inventory, and importer idempotency).
"""

import frappe


def execute():
    if frappe.db.exists("Custom Field", "Item-sync_to_shopify"):
        frappe.delete_doc("Custom Field", "Item-sync_to_shopify", ignore_permissions=True)

    # delete_doc on the Custom Field drops the column via a schema change, but
    # be explicit/idempotent in case the field was already removed by hand.
    if "sync_to_shopify" in frappe.db.get_table_columns("Item"):
        frappe.db.sql_ddl("ALTER TABLE `tabItem` DROP COLUMN `sync_to_shopify`")

    frappe.db.commit()
