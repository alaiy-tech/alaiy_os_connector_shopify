"""
Fixes the 134 orders confirmed by audit_fulfillment_dn_mismatch.py:
Shopify shipped these in 2+ real boxes, but only 1 local Delivery Note
exists, so only one box's tracking number ever had anywhere to go.

Creating a second real Delivery Note for the missing box doesn't work
here -- confirmed live (SAL-ORD-2026-04721): ERPNext's own
make_delivery_note() only offers whatever quantity is still
UNDELIVERED against the Sales Order, and since the old single-DN
already recorded the item as fully delivered, there's nothing left to
put on a second DN. Building around that (force-inserting rows
ERPNext itself says are already delivered) would corrupt the stock
ledger, which is exactly the kind of document surgery this site has a
documented duplicate-billing incident from doing carelessly before.

So this never creates or touches a second document. It writes onto the
ONE existing Delivery Note only:
  - sh_tracking_number / sh_tracking_company / sh_tracking_url: every
    distinct real tracking number from every real fulfillment, joined
    with ", " -- never overwrites a tracking number already recorded,
    only appends what's missing.
  - sh_delivery_status: the LEAST advanced status among all real
    fulfillments (e.g. IN_TRANSIT wins over DELIVERED) -- an order
    isn't fully delivered until every box has arrived, so this never
    overstates progress.

Read-only against Shopify. Never creates, cancels, or amends any
document. Dry run by default.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.backfill_multi_shipment_tracking.run

Apply for real:
  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.backfill_multi_shipment_tracking.run \
      --kwargs "{'dry_run': False}"
"""

import frappe

# Shopify's real fulfillment status values, ordered least to most complete --
# used to pick the honest overall status when an order has more than one
# real shipment in different states.
_STATUS_RANK = [
    "PENDING", "OPEN", "IN_PROGRESS", "SUBMITTED", "SCHEDULED",
    "CONFIRMED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "ATTEMPTED_DELIVERY",
    "DELIVERED", "CANCELED", "FAILURE",
]


def _least_advanced(statuses):
    ranked = [s for s in statuses if s in _STATUS_RANK]
    if not ranked:
        return statuses[0] if statuses else ""
    return min(ranked, key=_STATUS_RANK.index)


def run(dry_run=True, order_names=None):
    if isinstance(dry_run, str):
        dry_run = dry_run.lower() not in ("false", "0", "")
    if isinstance(order_names, str):
        import json as _json
        order_names = _json.loads(order_names)

    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.order.utils import _to_gid

    filters = {"docstatus": 1, "sh_shopify_order_id": ["!=", ""]}
    if order_names:
        filters["name"] = ["in", order_names]
    sos = frappe.get_all(
        "Sales Order", filters=filters, fields=["name", "sh_shopify_order_id"], order_by="creation",
    )
    print(f"{'DRY RUN: ' if dry_run else ''}Checking {len(sos)} order(s)...", flush=True)

    client = ShopifyGraphQLClient()
    query = """
    query($id: ID!) {
      order(id: $id) {
        fulfillments(first: 10) {
          displayStatus
          trackingInfo { number company url }
        }
      }
    }
    """

    updated, unchanged, no_dn, errors = [], 0, [], []

    for i, so in enumerate(sos, 1):
        if i % 100 == 0 or i == len(sos):
            print(f"  ...{i}/{len(sos)} checked", flush=True)

        dn_names = frappe.get_all(
            "Delivery Note Item", filters={"against_sales_order": so.name},
            pluck="parent", distinct=True,
        )
        if len(dn_names) != 1:
            continue  # only fixing the collapsed-to-exactly-one-DN case here
        dn_name = dn_names[0]

        try:
            data = client.execute(query, {"id": _to_gid(so.sh_shopify_order_id)})
        except Exception as e:
            errors.append((so.name, str(e)))
            continue

        fulfillments = ((data or {}).get("order") or {}).get("fulfillments") or []
        if len(fulfillments) <= 1:
            continue  # not a multi-shipment order -- nothing to merge

        numbers, companies, urls, statuses = [], [], [], []
        for f in fulfillments:
            status = (f.get("displayStatus") or "").strip()
            if status:
                statuses.append(status.upper())
            for t in (f.get("trackingInfo") or []):
                number = (t.get("number") or "").strip()
                if number and number not in numbers:
                    numbers.append(number)
                    companies.append((t.get("company") or "").strip())
                    urls.append((t.get("url") or "").strip())

        existing = frappe.db.get_value(
            "Delivery Note", dn_name, ["sh_tracking_number", "sh_delivery_status"], as_dict=True,
        )
        existing_numbers = [n.strip() for n in (existing.sh_tracking_number or "").split(",") if n.strip()]
        new_numbers = [n for n in numbers if n not in existing_numbers]

        overall_status = _least_advanced(statuses) if statuses else ""
        status_changed = bool(overall_status) and overall_status != (existing.sh_delivery_status or "")

        if not new_numbers and not status_changed:
            unchanged += 1
            continue

        merged_numbers = existing_numbers + new_numbers
        detail = {
            "so": so.name, "dn": dn_name,
            "tracking_before": existing.sh_tracking_number, "tracking_after": ", ".join(merged_numbers),
            "status_before": existing.sh_delivery_status, "status_after": overall_status or existing.sh_delivery_status,
        }

        if dry_run:
            updated.append(detail)
            continue

        try:
            values = {}
            if new_numbers:
                values["sh_tracking_number"] = ", ".join(merged_numbers)
                values["sh_tracking_company"] = ", ".join(dict.fromkeys(c for c in companies if c))
                values["sh_tracking_url"] = ", ".join(dict.fromkeys(u for u in urls if u))
            if status_changed:
                values["sh_delivery_status"] = overall_status
            frappe.db.set_value("Delivery Note", dn_name, values, update_modified=False)
            frappe.db.commit()
            updated.append(detail)
        except Exception as e:
            errors.append((so.name, str(e)))

    print(f"\n=== {'DRY RUN' if dry_run else 'APPLIED'} ===")
    print(f"{'Would update' if dry_run else 'Updated'}: {len(updated)} Delivery Note(s)")
    for row in updated[:30]:
        print(f"  {row}")
    if len(updated) > 30:
        print(f"  ... and {len(updated) - 30} more")

    print(f"\nAlready correct, no change needed: {unchanged}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for name, err in errors[:15]:
            print(f"  {name}: {err}")

    if dry_run:
        print("\nDry run only -- nothing written. Re-run with dry_run=false to apply.")

    return {"updated": len(updated), "unchanged": unchanged, "errors": len(errors)}
