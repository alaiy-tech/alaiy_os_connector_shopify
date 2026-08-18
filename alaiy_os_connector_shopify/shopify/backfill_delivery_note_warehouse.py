"""
One-off: correct the warehouse on existing Delivery Notes that were created
before PR #139 (fulfillment location -> real per-supplier warehouse via
sh_location_map). Confirmed live: 100% of checked fulfillment-linked
Delivery Notes had landed on the one shared sh_default_warehouse instead of
their real supplier warehouse, since order/DN creation never consulted the
mapping table before that fix.

Read-only against Shopify for the lookup (one call per Delivery Note, via
its own fulfillment's real Shopify location); writes only the warehouse
field on the Delivery Note Item rows and the DN's own set_warehouse -- no
new documents, no cancel/amend, nothing pushed back to Shopify. A
Delivery Note whose fulfillment's location has no real mapping entry, or
whose Shopify fulfillment can't be found, is skipped and left untouched.

Run via bench execute, matching this app's own pull_stock_from_shopify.py/
fix_conversion_rates.py/backfill_delivery_fields.py convention:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.backfill_delivery_note_warehouse.run

Dry run is the default -- prints what would change, writes nothing.
Apply for real:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.backfill_delivery_note_warehouse.run \
        --kwargs "{'dry_run': False}"
"""

import frappe


def run(dry_run=True):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    settings = frappe.get_single("Shopify Connector Settings")
    location_map = {row.shopify_location: row.warehouse for row in (settings.get("sh_location_map") or [])}

    dns = frappe.db.sql("""
        SELECT name, sh_shopify_fulfillment_id FROM `tabDelivery Note`
        WHERE docstatus = 1 AND sh_shopify_fulfillment_id IS NOT NULL
          AND sh_shopify_fulfillment_id != '' AND is_return = 0
        ORDER BY creation
    """, as_dict=True)

    print(f"Found {len(dns)} fulfillment-linked Delivery Notes. dry_run={dry_run}")

    fixed = 0
    already_correct = 0
    no_mapping = 0
    failed = []
    total = len(dns)

    for i, dn in enumerate(dns, start=1):
        if i % 50 == 0 or i == total:
            print(f"  ...{i}/{total} processed (fixed: {fixed}, already correct: {already_correct}, no mapping: {no_mapping}, failed: {len(failed)})")
        try:
            data = client.execute("""
            query GetFulfillmentLocation($id: ID!) {
              fulfillment(id: $id) { location { id } }
            }
            """, {"id": f"gid://shopify/Fulfillment/{dn.sh_shopify_fulfillment_id}"})
            fulfillment = (data or {}).get("fulfillment") or {}
            location_gid = (fulfillment.get("location") or {}).get("id")
            if not location_gid:
                no_mapping += 1
                continue

            loc_name = frappe.db.get_value("Shopify Location", {"sh_location_gid": location_gid}, "name")
            expected_warehouse = location_map.get(loc_name) if loc_name else None
            if not expected_warehouse:
                no_mapping += 1
                continue

            actual_warehouse = frappe.db.get_value("Delivery Note Item", {"parent": dn.name}, "warehouse")
            if actual_warehouse == expected_warehouse:
                already_correct += 1
                continue

            if dry_run:
                print(f"  would fix {dn.name}: '{actual_warehouse}' -> '{expected_warehouse}'")
                continue

            item_names = frappe.get_all("Delivery Note Item", filters={"parent": dn.name}, pluck="name")
            for item_name in item_names:
                frappe.db.set_value("Delivery Note Item", item_name, "warehouse", expected_warehouse, update_modified=False)
            frappe.db.set_value("Delivery Note", dn.name, "set_warehouse", expected_warehouse, update_modified=False)
            frappe.db.commit()
            fixed += 1
        except Exception:
            failed.append(dn.name)
            frappe.log_error(
                title=f"backfill_delivery_note_warehouse: failed for {dn.name}",
                message=frappe.get_traceback(),
            )

    if not dry_run:
        print(
            f"Fixed {fixed} Delivery Notes. Already correct: {already_correct}. "
            f"No mapping/skip: {no_mapping}. Failed: {failed}"
        )
