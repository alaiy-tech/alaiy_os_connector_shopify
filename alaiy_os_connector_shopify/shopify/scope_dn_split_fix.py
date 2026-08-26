"""
Read-only scoping for the 134 orders confirmed by
audit_fulfillment_dn_mismatch.py to have more real Shopify fulfillments
than local Delivery Notes -- before writing any script that actually
splits a Delivery Note, this checks what's already downstream of each
one. This site has a documented history of a real duplicate-billing
incident from careless Delivery Note creation (cascading into the
auto-Sales-Invoice-on-DN-submit hook -- see backfill_delivery_fields.py's
own docstring), so cancelling/recreating a DN that already has a
submitted Sales Invoice against it is exactly the shape of that same
mistake and must never be done blindly.

For each mismatched order, reports:
  - whether a Sales Invoice already exists referencing the DN (if so,
    this order is NOT safe for an automated cancel+recreate split --
    would need a human/accountant to handle the invoice side first)
  - whether the DN has been paid out already (Payment Entry against
    the Sales Invoice)
  - how many real stock ledger entries exist against the DN (repricing/
    resubmitting always has to rebuild these correctly)
  - whether more than one Purchase Order exists for the order (a
    multi-supplier order, which the split needs to route correctly)

Makes no writes. Reads the audit's own live output fresh (same
Shopify calls) rather than trusting a stale log file, since orders can
change state between the audit run and this one.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.scope_dn_split_fix.run
"""

import frappe


def _get_mismatched_orders(limit=None):
    """Re-derives the same mismatched list audit_fulfillment_dn_mismatch.py
    reports, rather than parsing its log text -- the log format isn't
    meant to be machine-read back in."""
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

    mismatched = []
    for i, so in enumerate(sos, 1):
        if i % 100 == 0:
            print(f"  scanning {i}/{len(sos)}...", flush=True)
        dn_names = frappe.get_all(
            "Delivery Note Item", filters={"against_sales_order": so.name},
            pluck="parent", distinct=True,
        )
        try:
            data = client.execute(query, {"id": _to_gid(so.sh_shopify_order_id)})
        except Exception:
            continue
        fulfillments = ((data or {}).get("order") or {}).get("fulfillments") or []
        if not fulfillments:
            continue
        if len(fulfillments) != len(dn_names):
            mismatched.append({"so": so.name, "dn_names": dn_names, "fulfillments": fulfillments})
    return mismatched


def run(limit=None):
    mismatched = _get_mismatched_orders(limit)
    print(f"\nScoping {len(mismatched)} mismatched order(s)...\n", flush=True)

    safe_no_invoice, blocked_has_invoice, blocked_has_payment = [], [], []
    multi_po = []

    for row in mismatched:
        so_name = row["so"]
        dn_names = row["dn_names"]

        sis = frappe.get_all(
            "Sales Invoice Item",
            filters={"sales_order": so_name},
            fields=["parent"], distinct=True,
        )
        si_names = [r.parent for r in sis]
        submitted_sis = frappe.get_all(
            "Sales Invoice", filters={"name": ["in", si_names], "docstatus": 1}, pluck="name",
        ) if si_names else []

        has_payment = False
        if submitted_sis:
            has_payment = bool(frappe.get_all(
                "Payment Entry Reference",
                filters={"reference_name": ["in", submitted_sis], "docstatus": 1},
                limit=1,
            ))

        pos = frappe.get_all("Purchase Order", filters={"os_sales_order": so_name, "docstatus": 1}, pluck="supplier")

        sle_count = frappe.db.count(
            "Stock Ledger Entry", filters={"voucher_type": "Delivery Note", "voucher_no": ["in", dn_names]},
        ) if dn_names else 0

        detail = {
            "so": so_name, "dn_names": dn_names,
            "real_fulfillments": len(row["fulfillments"]),
            "submitted_sales_invoices": submitted_sis,
            "has_payment": has_payment,
            "purchase_order_suppliers": pos,
            "stock_ledger_entries": sle_count,
        }

        if len(set(pos)) > 1:
            multi_po.append(detail)

        if has_payment:
            blocked_has_payment.append(detail)
        elif submitted_sis:
            blocked_has_invoice.append(detail)
        else:
            safe_no_invoice.append(detail)

    print(f"=== SCOPE SUMMARY ({len(mismatched)} mismatched orders) ===")
    print(f"Safe (no Sales Invoice yet -- DN split alone, no invoice conflict): {len(safe_no_invoice)}")
    print(f"Blocked -- has a submitted Sales Invoice, not yet paid: {len(blocked_has_invoice)}")
    print(f"Blocked -- has a submitted Sales Invoice AND a Payment Entry: {len(blocked_has_payment)}")
    print(f"Multi-supplier orders in this set (more than one PO): {len(multi_po)}")

    print(f"\nSafe examples (first 20):")
    for d in safe_no_invoice[:20]:
        print(f"  {d['so']}: {d['real_fulfillments']} fulfillments, {len(d['dn_names'])} local DN(s), "
              f"{d['stock_ledger_entries']} SLE(s), suppliers {d['purchase_order_suppliers']}")

    print(f"\nBlocked-by-invoice examples (first 20):")
    for d in blocked_has_invoice[:20]:
        print(f"  {d['so']}: Sales Invoice(s) {d['submitted_sales_invoices']}")

    print(f"\nBlocked-by-payment examples (first 20):")
    for d in blocked_has_payment[:20]:
        print(f"  {d['so']}: Sales Invoice(s) {d['submitted_sales_invoices']}")

    return {
        "total_mismatched": len(mismatched),
        "safe": len(safe_no_invoice),
        "blocked_invoice": len(blocked_has_invoice),
        "blocked_payment": len(blocked_has_payment),
        "multi_po": len(multi_po),
    }
