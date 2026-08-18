"""
One-off: correct conversion_rate=1.0 on USD Sales Orders (+ their Delivery
Notes and Sales Invoices) that were wrongly stamped with a real exchange
rate on a same-currency (USD order, USD company) order. Traced live on
Solist: ~1,481 orders created 2026-07-31..2026-08-03 carry a conversion_rate
around 89-95 instead of 1.0 -- ERPNext's own currency.py already guards
`if from_currency == to_currency: return 1.0` and Company.default_currency
was never actually changed (checked Version history), so the exact cause
of that window is unclear, but the bug is not present in the code as it
stands today (recent orders correctly show 1.0).

Verified this is purely cosmetic bookkeeping (base_* mirror fields) -- the
actual prices/amounts already match Shopify's live data exactly, confirmed
on SAL-ORD-2026-04416. Fixing conversion_rate does NOT retroactively
recalculate base_grand_total/base_net_total/etc on these already-submitted
documents (a plain frappe.db.set_value doesn't re-run validate()), so this
intentionally touches ONLY conversion_rate -- the one field
validate_return_against actually checks -- not any base_* field, leaving
whatever accounting has already used those numbers untouched.

Run via bench execute, matching this app's own pull_stock_from_shopify.py
convention:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.fix_conversion_rates.run

Dry run is the default -- prints what would change, writes nothing.
Apply for real:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.fix_conversion_rates.run \
        --kwargs "{'dry_run': False}"
"""

import frappe


def run(dry_run=True):
    affected_sos = frappe.db.sql("""
        SELECT name, conversion_rate FROM `tabSales Order`
        WHERE currency = 'USD' AND conversion_rate != 1.0 AND docstatus = 1
        ORDER BY creation
    """, as_dict=True)

    print(f"Found {len(affected_sos)} affected Sales Orders. dry_run={dry_run}")

    fixed = 0
    skipped = []
    for row in affected_sos:
        so_name = row.name
        try:
            dns = frappe.db.sql("""
                SELECT DISTINCT parent FROM `tabDelivery Note Item`
                WHERE against_sales_order = %s
            """, so_name, pluck=True)
            sis = frappe.db.sql("""
                SELECT DISTINCT sii.parent FROM `tabSales Invoice Item` sii
                JOIN `tabSales Invoice` si ON si.name = sii.parent
                WHERE sii.sales_order = %s AND si.docstatus = 1
            """, so_name, pluck=True)

            if dry_run:
                print(f"  would fix: {so_name} (DNs: {dns}, SIs: {sis})")
                continue

            frappe.db.set_value("Sales Order", so_name, "conversion_rate", 1.0, update_modified=False)
            for dn in dns:
                frappe.db.set_value("Delivery Note", dn, "conversion_rate", 1.0, update_modified=False)
            for si in sis:
                frappe.db.set_value("Sales Invoice", si, "conversion_rate", 1.0, update_modified=False)
            frappe.db.commit()
            fixed += 1
            if fixed % 100 == 0:
                print(f"  ...{fixed} done")
        except Exception:
            frappe.db.rollback()
            skipped.append(so_name)
            frappe.log_error(
                title=f"fix_conversion_rates: failed for {so_name}",
                message=frappe.get_traceback(),
            )

    if not dry_run:
        print(f"Fixed {fixed} of {len(affected_sos)}. Skipped (see Error Log): {skipped}")
