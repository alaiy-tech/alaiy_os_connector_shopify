"""
One-off: correct the warehouse on existing Delivery Notes that were created
before PR #139 (fulfillment location -> real per-supplier warehouse via
sh_location_map). Confirmed live: 100% of checked fulfillment-linked
Delivery Notes had landed on the one shared sh_default_warehouse instead of
their real supplier warehouse, since order/DN creation never consulted the
mapping table before that fix.

Covers two cases:
  1. Delivery Notes tagged with a real sh_shopify_fulfillment_id -- look up
     that exact fulfillment's location directly.
  2. Delivery Notes with NO fulfillment id (confirmed live: the much larger
     group, ~1,357 of ~1,458 total -- created via the full-order-fallback
     path, _create_delivery_note_if_needed, which never tags one specific
     fulfillment event) -- traced via the linked Sales Order's own Shopify
     order id, then that order's fulfillments. If the order has exactly one
     distinct location across its fulfillments, that's used; if it has more
     than one (a genuinely multi-location order), this is skipped rather
     than guessed, since there's no way to know which DN row belongs to
     which location without more work than a one-off backfill should do.

Read-only against Shopify for every lookup; writes only the warehouse
field on the Delivery Note Item rows and the DN's own set_warehouse -- no
new documents, no cancel/amend, nothing pushed back to Shopify.

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


def _resolve_expected_warehouse_via_fulfillment(client, fulfillment_id, location_map):
    data = client.execute("""
    query GetFulfillmentLocation($id: ID!) {
      fulfillment(id: $id) { location { id } }
    }
    """, {"id": f"gid://shopify/Fulfillment/{fulfillment_id}"})
    fulfillment = (data or {}).get("fulfillment") or {}
    location_gid = (fulfillment.get("location") or {}).get("id")
    if not location_gid:
        return None
    loc_name = frappe.db.get_value("Shopify Location", {"sh_location_gid": location_gid}, "name")
    return location_map.get(loc_name) if loc_name else None


def _resolve_expected_warehouse_via_order(client, shopify_order_id, location_map):
    """Returns (warehouse_or_None, multi_location_bool)."""
    from alaiy_os_connector_shopify.shopify.order.utils import _to_gid

    data = client.execute("""
    query GetOrderFulfillmentLocations($id: ID!) {
      order(id: $id) {
        fulfillments(first: 20) { location { id } }
      }
    }
    """, {"id": _to_gid(shopify_order_id)})
    fulfillments = ((data or {}).get("order") or {}).get("fulfillments") or []
    location_gids = {f["location"]["id"] for f in fulfillments if f.get("location")}
    if not location_gids:
        return None, False
    if len(location_gids) > 1:
        return None, True
    location_gid = next(iter(location_gids))
    loc_name = frappe.db.get_value("Shopify Location", {"sh_location_gid": location_gid}, "name")
    return (location_map.get(loc_name) if loc_name else None), False


def run(dry_run=True):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    settings = frappe.get_single("Shopify Connector Settings")
    location_map = {row.shopify_location: row.warehouse for row in (settings.get("sh_location_map") or [])}

    dns = frappe.db.sql("""
        SELECT dn.name, dn.sh_shopify_fulfillment_id,
               (SELECT dni.against_sales_order FROM `tabDelivery Note Item` dni
                WHERE dni.parent = dn.name LIMIT 1) as against_sales_order
        FROM `tabDelivery Note` dn
        WHERE dn.docstatus = 1 AND dn.is_return = 0
        ORDER BY dn.creation
    """, as_dict=True)

    print(f"Found {len(dns)} Delivery Notes total. dry_run={dry_run}")

    fixed = 0
    already_correct = 0
    no_mapping = 0
    multi_location_skipped = 0
    failed = []
    total = len(dns)

    for i, dn in enumerate(dns, start=1):
        if i % 50 == 0 or i == total:
            print(
                f"  ...{i}/{total} processed (fixed: {fixed}, already correct: {already_correct}, "
                f"no mapping: {no_mapping}, multi-location skipped: {multi_location_skipped}, failed: {len(failed)})"
            )
        try:
            expected_warehouse = None
            if dn.sh_shopify_fulfillment_id:
                expected_warehouse = _resolve_expected_warehouse_via_fulfillment(
                    client, dn.sh_shopify_fulfillment_id, location_map)
            elif dn.against_sales_order:
                shopify_order_id = frappe.db.get_value("Sales Order", dn.against_sales_order, "sh_shopify_order_id")
                if not shopify_order_id:
                    no_mapping += 1
                    continue
                expected_warehouse, is_multi = _resolve_expected_warehouse_via_order(
                    client, shopify_order_id, location_map)
                if is_multi:
                    multi_location_skipped += 1
                    continue
            else:
                no_mapping += 1
                continue

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
            f"No mapping/skip: {no_mapping}. Multi-location skipped: {multi_location_skipped}. Failed: {failed}"
        )
