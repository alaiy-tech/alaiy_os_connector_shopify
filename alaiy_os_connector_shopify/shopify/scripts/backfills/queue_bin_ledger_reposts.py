"""
One-off: find every Bin row that disagrees with its own Stock Ledger Entry
total, and queue a Repost Item Valuation for each one that isn't already
queued/completed/failed -- ERPNext's own built-in mechanism for recomputing
Bin (and valuation) from real ledger history.

Root cause of the mismatch: the Shopify inventory webhook used to write
Bin.actual_qty directly (see inventory_sync.py's apply_pulled_stock docstring
for the full story). That bug is fixed; this is the one-time backlog cleanup
for the ~12,000 rows it already corrupted.

Safe to re-run: skips any (item_code, warehouse) pair that already has a
Repost Item Valuation row, so an interrupted run just picks up where it left
off.

posting_date is deliberately set to 2020-01-01 so these sort ahead of the
real, more-recent entries ERPNext queues on its own -- these ARE the
priority, they're the actual bug we're fixing.

Run detached, since this queues thousands of documents and each is a real
insert+submit:

    tmux new -d -s repost_queue "cd ~/alaiy_os_bench && bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.scripts.backfills.queue_bin_ledger_reposts.run 2>&1 | tee ~/repost_queue.log"

Then check progress any time, from anywhere, without needing this session:

    tail -f ~/repost_queue.log
"""

import frappe


def run(batch_commit=200):
    mismatches = frappe.db.sql("""
        SELECT item_code, warehouse FROM (
            SELECT b.item_code, b.warehouse,
                   b.actual_qty - COALESCE(SUM(sle.actual_qty), 0) AS diff
            FROM `tabBin` b
            LEFT JOIN `tabStock Ledger Entry` sle
              ON sle.item_code = b.item_code AND sle.warehouse = b.warehouse
             AND sle.is_cancelled = 0
            GROUP BY b.item_code, b.warehouse
        ) x
        WHERE ABS(diff) > 0.001
    """, as_dict=True)
    print(f"{len(mismatches)} item/warehouse pairs mismatched", flush=True)

    already = {
        (r.item_code, r.warehouse)
        for r in frappe.get_all("Repost Item Valuation", fields=["item_code", "warehouse"])
    }
    remaining = [m for m in mismatches if (m.item_code, m.warehouse) not in already]
    print(f"{len(remaining)} left to queue (skipping {len(mismatches) - len(remaining)} already queued/processed)", flush=True)

    queued = 0
    for i, m in enumerate(remaining):
        riv = frappe.get_doc({
            "doctype": "Repost Item Valuation",
            "item_code": m.item_code,
            "warehouse": m.warehouse,
            "based_on": "Item and Warehouse",
            "posting_date": "2020-01-01",
            "posting_time": "00:00:00",
        })
        riv.insert(ignore_permissions=True)
        riv.submit()
        queued += 1
        if (i + 1) % batch_commit == 0:
            frappe.db.commit()
            print(f"progress {i + 1}/{len(remaining)}", flush=True)

    frappe.db.commit()
    print(f"DONE. Queued {queued} more Repost Item Valuation document(s).", flush=True)
    return {"mismatched": len(mismatches), "queued": queued}
