"""
One-off: backfill sh_delivery_method (Sales Order) and sh_delivery_status
(Delivery Note) for orders that already exist locally but never got these
fields -- either because they predate PR #133, or because the order-update
webhook silently crashed before reaching them (see the linked-Purchase-Order
fix in line_items.py).

Read-only against Shopify -- pulls each order's current real data and writes
ONLY the two fields below, on the EXISTING Sales Order / Delivery Note.
Nothing is deleted, cancelled, or recreated; nothing is written back to
Shopify. A field stays blank if Shopify genuinely has nothing to report --
never guessed or defaulted.

Run via bench execute, matching this app's own pull_stock_from_shopify.py /
fix_conversion_rates.py convention:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.backfill_delivery_fields.run

Dry run is the default -- prints what would change, writes nothing.
Apply for real:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.backfill_delivery_fields.run \
        --kwargs "{'dry_run': False}"
"""

import frappe

from alaiy_os_connector_shopify import connections


def run(dry_run=True):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.order.utils import _to_gid

    client = ShopifyGraphQLClient(connections.require_enabled())

    sos = frappe.db.sql("""
        SELECT name, sh_shopify_order_id FROM `tabSales Order`
        WHERE docstatus = 1
          AND sh_shopify_order_id IS NOT NULL AND sh_shopify_order_id != ''
          AND (sh_delivery_method IS NULL OR sh_delivery_method = '')
        ORDER BY creation
    """, as_dict=True)

    print(f"Found {len(sos)} Sales Orders missing sh_delivery_method. dry_run={dry_run}")

    updated_method = 0
    updated_status = 0
    no_data_on_shopify = 0
    failed = []
    total = len(sos)

    for i, so in enumerate(sos, start=1):
        if i % 50 == 0 or i == total:
            print(f"  ...{i}/{total} processed (method: {updated_method}, status: {updated_status}, no-data: {no_data_on_shopify}, failed: {len(failed)})")
        try:
            data = client.execute("""
            query GetOrderDeliveryInfo($id: ID!) {
              order(id: $id) {
                shippingLine { title }
                fulfillments(first: 10) {
                  legacyResourceId
                  displayStatus
                }
              }
            }
            """, {"id": _to_gid(so.sh_shopify_order_id)})

            order_node = (data or {}).get("order") or {}
            method = ((order_node.get("shippingLine") or {}).get("title") or "").strip()
            fulfillments = order_node.get("fulfillments") or []

            if not method and not fulfillments:
                no_data_on_shopify += 1
                continue

            if dry_run:
                print(f"  would update {so.name}: method={method!r}, fulfillments={fulfillments!r}")
                continue

            if method:
                frappe.db.set_value("Sales Order", so.name, "sh_delivery_method", method, update_modified=False)
                updated_method += 1

            for f in fulfillments:
                status = (f.get("displayStatus") or "").strip()
                if not status:
                    continue
                fulfillment_id = str(f.get("legacyResourceId") or "")
                if not fulfillment_id:
                    continue
                dn_name = frappe.db.get_value(
                    "Delivery Note", {"sh_shopify_fulfillment_id": fulfillment_id}, "name")
                if not dn_name:
                    continue
                frappe.db.set_value(
                    "Delivery Note", dn_name, "sh_delivery_status", status.upper(), update_modified=False)
                updated_status += 1

            frappe.db.commit()
        except Exception:
            failed.append(so.name)
            frappe.log_error(
                title=f"backfill_delivery_fields: failed for {so.name}",
                message=frappe.get_traceback(),
            )

    if not dry_run:
        print(
            f"Updated sh_delivery_method on {updated_method} Sales Orders, "
            f"sh_delivery_status on {updated_status} Delivery Notes. "
            f"{no_data_on_shopify} orders had no real data on Shopify (left blank). "
            f"Failed: {failed}"
        )
