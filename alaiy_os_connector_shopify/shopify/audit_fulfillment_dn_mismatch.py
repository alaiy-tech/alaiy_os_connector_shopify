"""
Read-only audit: for every submitted Sales Order linked to a real Shopify
order, compares Shopify's real fulfillment count against the number of
local Delivery Notes -- confirmed live on SAL-ORD-2026-03183 (TS25932):
Shopify shipped 2 separate fulfillments (Omega watch, Hermès watch), each
with its own tracking number, but only 1 local Delivery Note exists,
covering both. That's why backfill_delivery_fields.py's tracking backfill
correctly refused to guess which of the 2 tracking numbers belongs to the
1 local DN.

This never writes anything -- splitting a DN to match Shopify's real
fulfillment count is a real structural change (new documents, stock
ledger entries) and this site has a documented incident where creating a
Delivery Note cascaded into a duplicate Sales Invoice via the
auto-invoice-on-DN-submit hook (see backfill_delivery_fields.py's own
docstring). Scope this first before deciding how -- or whether -- to fix
any of it.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.audit_fulfillment_dn_mismatch.run

Optional: --kwargs '{"limit": 50}' to sample instead of running the full set.
"""

import frappe


def run(limit=None):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.order.utils import _to_gid

    sos = frappe.db.sql("""
        SELECT name, sh_shopify_order_id FROM `tabSales Order`
        WHERE docstatus = 1
          AND sh_shopify_order_id IS NOT NULL AND sh_shopify_order_id != ''
        ORDER BY creation
    """, as_dict=True)
    if limit:
        sos = sos[:limit]

    print(f"Auditing {len(sos)} Sales Orders...", flush=True)

    client = ShopifyGraphQLClient()

    query = """
    query($id: ID!) {
      order(id: $id) {
        fulfillments(first: 10) {
          legacyResourceId
          displayStatus
          trackingInfo { number company }
        }
      }
    }
    """

    mismatched, matched, no_fulfillments, errors = [], 0, 0, []

    for i, so in enumerate(sos, 1):
        if i % 50 == 0 or i == 1 or i == len(sos):
            print(f"[{i}/{len(sos)}] {so.name}...", flush=True)

        dn_names = frappe.get_all(
            "Delivery Note Item", filters={"against_sales_order": so.name},
            pluck="parent", distinct=True,
        )

        try:
            data = client.execute(query, {"id": _to_gid(so.sh_shopify_order_id)})
        except Exception as e:
            errors.append((so.name, str(e)))
            continue

        fulfillments = ((data or {}).get("order") or {}).get("fulfillments") or []
        if not fulfillments:
            no_fulfillments += 1
            continue

        real_count = len(fulfillments)
        local_count = len(dn_names)

        if real_count != local_count:
            distinct_tracking = {
                (f.get("trackingInfo") or [{}])[0].get("number")
                for f in fulfillments
                if (f.get("trackingInfo") or [{}])[0].get("number")
            }
            mismatched.append({
                "so": so.name, "real_fulfillments": real_count, "local_dns": local_count,
                "distinct_tracking_numbers": len(distinct_tracking),
                "dn_names": dn_names,
            })
        else:
            matched += 1

    print(f"\n=== DONE: {len(sos)} orders checked ===")
    print(f"Matched (fulfillment count == local DN count): {matched}")
    print(f"No fulfillments on Shopify yet: {no_fulfillments}")
    print(f"MISMATCHED (real fulfillments != local DNs): {len(mismatched)}")
    for row in mismatched[:30]:
        print(f"  {row['so']}: Shopify has {row['real_fulfillments']} fulfillment(s) "
              f"({row['distinct_tracking_numbers']} distinct tracking#), local has {row['local_dns']} DN(s) {row['dn_names']}")
    if len(mismatched) > 30:
        print(f"  ... and {len(mismatched) - 30} more")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for name, err in errors[:10]:
            print(f"  {name}: {err}")

    return {"checked": len(sos), "matched": matched, "mismatched": len(mismatched), "no_fulfillments": no_fulfillments}
