"""
One-off: zero out every Bin row with a negative actual_qty. Negative
on-hand stock is never a real, legitimate state -- confirmed live, 720
such rows exist across several warehouses, predating this session's
work (the pattern -- small negative counts on totally unrelated items
across multiple, otherwise-unconnected warehouses) points to a
historical data issue, not something caused by any script run today.

One Stock Reconciliation per warehouse, correcting every negative item
in it to 0. Read-only against Shopify (none needed -- this only fixes
an internally-impossible state, not a mismatch against live data).

Run via bench execute, dry-run by default:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.fix_negative_bins.run

Apply for real:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.fix_negative_bins.run \
        --kwargs "{'dry_run': False}"
"""

import frappe


def run(dry_run=True):
    if isinstance(dry_run, str):
        dry_run = dry_run.strip().lower() not in ("0", "false", "no", "")

    rows = frappe.db.sql("""
        SELECT item_code, warehouse, actual_qty FROM `tabBin` WHERE actual_qty < 0
    """, as_dict=True)
    print(f"{len(rows)} Bin row(s) with negative quantity. dry_run={dry_run}", flush=True)

    by_warehouse = {}
    for r in rows:
        by_warehouse.setdefault(r.warehouse, []).append(r)

    fixed = 0
    failed = []
    for warehouse, items in by_warehouse.items():
        print(f"{warehouse}: {len(items)} negative item(s)", flush=True)
        if dry_run:
            for r in items:
                print(f"  would zero {r.item_code}: {r.actual_qty} -> 0", flush=True)
            continue

        company = frappe.db.get_value("Warehouse", warehouse, "company") or frappe.defaults.get_global_default("company")
        try:
            sr = frappe.new_doc("Stock Reconciliation")
            sr.company = company
            sr.purpose = "Stock Reconciliation"
            for r in items:
                sr.append("items", {
                    "item_code": r.item_code,
                    "warehouse": warehouse,
                    "qty": 0,
                    "allow_zero_valuation_rate": 1,
                })
            sr.flags.ignore_permissions = True
            sr.insert()
            sr.submit()
            frappe.db.commit()
            fixed += len(items)
            print(f"  Applied: {sr.name}", flush=True)
        except Exception:
            frappe.db.rollback()
            failed.append(warehouse)
            frappe.log_error(
                title=f"fix_negative_bins: failed for warehouse {warehouse}",
                message=frappe.get_traceback(),
            )

    print(f"\n{'Would fix' if dry_run else 'Fixed'} {len(rows) if dry_run else fixed} row(s) across "
          f"{len(by_warehouse)} warehouse(s). Failed warehouses: {failed}", flush=True)
    return {"total_negative": len(rows), "fixed": fixed, "failed_warehouses": failed, "dry_run": dry_run}
