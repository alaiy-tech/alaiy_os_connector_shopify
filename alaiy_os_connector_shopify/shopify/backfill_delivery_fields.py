"""
One-off: backfill sh_delivery_method (Sales Order), sh_delivery_status, and
carrier tracking (Delivery Note) for orders that already exist locally but
never got these fields -- either because they predate PR #133, or because
the order-update webhook silently crashed before reaching them (see the
linked-Purchase-Order fix in line_items.py), or because they shipped in the
window before this site's webhooks were correctly registered.

Tracking is written to sh_tracking_number/sh_tracking_company -- the
carrier-agnostic fields, NOT fedex_tracking_number, which is specific to
this connector's own FedEx label-creation flow. Confirmed live: real
shipments here carry USPS and UPS tracking too, not just FedEx.

Read-only against Shopify -- pulls each order's current real data and writes
ONLY the two fields below, on the EXISTING Sales Order / Delivery Note.
Nothing is deleted, cancelled, or recreated; nothing is written back to
Shopify. A field stays blank if Shopify genuinely has nothing to report --
never guessed or defaulted.

Deliberately does NOT create a Delivery Note when one doesn't exist yet
(e.g. an order fulfilled entirely outside this app, like TS27377 via
ShipStation) -- confirmed live that doing so cascades into
alaiy_os_thesolist's own auto-Sales-Invoice-on-DN-submit hook, which can
crash with a real ERPNext over-billing error on an order that was
already fully invoiced through some other path, yet still leaves the
half-completed Sales Invoice persisted as submitted (docstatus=1) with
real GL entries -- caused a genuine duplicate-billing incident that had
to be found and reversed by hand. An order with no local Delivery Note
at all needs a human to create it deliberately, not an automated
backfill.

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


def run(dry_run=True, slice_index=None, slices=None):
    """slice_index/slices splits the work across parallel tmux sessions,
    same convention as migrate_default_warehouse_stock.py:

        for i in 0 1 2 3 4; do
          tmux new -d -s backfill_delivery_$i \
            "bench --site <site> execute alaiy_os_connector_shopify.shopify.backfill_delivery_fields.run \
             --kwargs \"{'dry_run': True, 'slice_index': $i, 'slices': 5}\" 2>&1 | tee ~/backfill_delivery_$i.log"
        done
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.order.utils import _to_gid

    if (slice_index is None) != (slices is None):
        frappe.throw("slice_index and slices must be given together")
    if slices is not None and not 0 <= int(slice_index) < int(slices):
        frappe.throw(f"slice_index must be between 0 and {int(slices) - 1}")

    client = ShopifyGraphQLClient()

    # An order whose sh_delivery_method is already set (e.g. from a prior
    # partial backfill run, or set going forward by PR #133's live pull)
    # was previously excluded here entirely -- but delivery STATUS and
    # TRACKING keep changing/filling in after that while method never does,
    # so a method-only filter permanently blocked ever refreshing them on
    # an order that already has its method. Select on any of the three
    # fields being incomplete: method blank, a linked Delivery Note has no
    # delivery status, or no tracking number.
    sos = frappe.db.sql("""
        SELECT DISTINCT so.name, so.sh_shopify_order_id FROM `tabSales Order` so
        LEFT JOIN `tabDelivery Note Item` dni ON dni.against_sales_order = so.name
        LEFT JOIN `tabDelivery Note` dn ON dn.name = dni.parent
        WHERE so.docstatus = 1
          AND so.sh_shopify_order_id IS NOT NULL AND so.sh_shopify_order_id != ''
          AND (
            (so.sh_delivery_method IS NULL OR so.sh_delivery_method = '')
            OR (dn.name IS NOT NULL AND (dn.sh_delivery_status IS NULL OR dn.sh_delivery_status = ''))
            OR (dn.name IS NOT NULL AND dn.is_return = 0 AND (dn.sh_tracking_number IS NULL OR dn.sh_tracking_number = ''))
          )
        ORDER BY so.creation
    """, as_dict=True)

    if slices:
        sos = [r for n, r in enumerate(sos) if n % int(slices) == int(slice_index)]
        print(f"SLICE {slice_index} of {slices}", flush=True)

    print(f"Found {len(sos)} Sales Orders missing sh_delivery_method, sh_delivery_status, or tracking. dry_run={dry_run}")

    updated_method = 0
    updated_status = 0
    updated_tracking = 0
    no_data_on_shopify = 0
    failed = []
    total = len(sos)

    for i, so in enumerate(sos, start=1):
        if i % 50 == 0 or i == total:
            print(f"  ...{i}/{total} processed (method: {updated_method}, status: {updated_status}, tracking: {updated_tracking}, no-data: {no_data_on_shopify}, failed: {len(failed)})")
        try:
            data = client.execute("""
            query GetOrderDeliveryInfo($id: ID!) {
              order(id: $id) {
                shippingLine { title }
                fulfillments(first: 10) {
                  legacyResourceId
                  displayStatus
                  trackingInfo { number company url }
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

            # Most real Delivery Notes (confirmed live: ~93%) were created via
            # the full-order fallback path and never got tagged with a real
            # sh_shopify_fulfillment_id -- looking up by that id alone missed
            # almost every real DN, which is why this backfill's own status
            # count sat near zero. Fall back to the order's own Delivery
            # Note(s) when the id lookup finds nothing, same as
            # backfill_delivery_note_warehouse.py already does for the
            # identical problem. Only safe when the order has exactly one
            # fulfillment to report -- with more than one, which specific DN
            # a status belongs to can't be known without more work than a
            # backfill should attempt.
            so_dn_names = None
            for f in fulfillments:
                status = (f.get("displayStatus") or "").strip()
                if not status:
                    continue
                fulfillment_id = str(f.get("legacyResourceId") or "")
                dn_name = (
                    frappe.db.get_value("Delivery Note", {"sh_shopify_fulfillment_id": fulfillment_id}, "name")
                    if fulfillment_id else None
                )
                if not dn_name and len(fulfillments) == 1:
                    if so_dn_names is None:
                        so_dn_names = frappe.get_all(
                            "Delivery Note Item", filters={"against_sales_order": so.name},
                            pluck="parent", distinct=True,
                        )
                    if len(so_dn_names) == 1:
                        dn_name = so_dn_names[0]
                if not dn_name:
                    continue
                frappe.db.set_value(
                    "Delivery Note", dn_name, "sh_delivery_status", status.upper(), update_modified=False)
                updated_status += 1

                # Tracking is real per-fulfillment data, same as status --
                # never overwrite a number already recorded (e.g. a real
                # FedEx label already on file), only fill in a genuinely
                # blank one.
                tracking = (f.get("trackingInfo") or [{}])[0]
                number = (tracking.get("number") or "").strip()
                if number and not frappe.db.get_value("Delivery Note", dn_name, "sh_tracking_number"):
                    frappe.db.set_value("Delivery Note", dn_name, {
                        "sh_tracking_number": number,
                        "sh_tracking_company": (tracking.get("company") or "").strip(),
                        "sh_tracking_url": (tracking.get("url") or "").strip(),
                    }, update_modified=False)
                    updated_tracking += 1

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
            f"sh_delivery_status on {updated_status} Delivery Notes, "
            f"tracking on {updated_tracking} Delivery Notes. "
            f"{no_data_on_shopify} orders had no real data on Shopify (left blank). "
            f"Failed: {failed}"
        )
