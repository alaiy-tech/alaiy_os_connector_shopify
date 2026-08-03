"""
Delete Alaiy OS Sales Orders that were imported from Shopify, without touching
the live Shopify orders. Nothing here calls the Shopify API at all -- this is a
local cleanup, and the store is left exactly as it is.

Dry run by default. Pass dry_run=0 to actually delete.

  # what would be deleted, changes nothing
  bench --site <site> execute \
      alaiy_os_connector_shopify.api.clear_orders.run

  # a date range, still a dry run
  bench --site <site> execute \
      alaiy_os_connector_shopify.api.clear_orders.run \
      --kwargs "{'since': '2026-07-01', 'until': '2026-07-31'}"

  # delete for real
  bench --site <site> execute \
      alaiy_os_connector_shopify.api.clear_orders.run \
      --kwargs "{'dry_run': 0}"

Cascade, child first: Delivery Note -> Purchase Order -> Sales Invoice ->
Payment Entry -> Sales Order.

Docstatus is force-flipped with raw db.set_value and the doc force-deleted,
rather than going through cancel(). A proper cancel() proved impossible partway
through a real run: once a linked doc had been cancelled by an earlier partial
pass, ERPNext's own stock-ledger and reserved-qty checks refused the next one.
No on_trash hook exists for any of these doctypes (checked against hooks.py).

frappe.flags.in_test makes delete_doc run its delete_dynamic_links cleanup
inline instead of enqueuing a background job per delete, which would otherwise
flood the queue on a large batch.

Deadlock-safe: each order is retried, with periodic commits, because one giant
transaction across thousands of orders collides with any concurrent writer
touching the same tables.

Re-importing afterwards works: order import dedups on the Sales Order's own
sh_shopify_order_id, so once the orders are gone a fresh pull recreates them.
Orders do not register Shopify Synced Entity rows, so there is no fingerprint
cache left behind to make the re-pull think they are already synced.
"""

import time

import frappe

_MAX_ATTEMPTS = 3


def _force_clear(doctype, name):
    if frappe.db.get_value(doctype, name, "docstatus") == 1:
        frappe.db.set_value(doctype, name, "docstatus", 2)
    frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)


def _linked_docs(so_name):
    """{doctype: [names]} for everything that has to go before the Sales Order."""
    linked = {}
    linked["Delivery Note"] = frappe.get_all(
        "Delivery Note Item", filters={"against_sales_order": so_name},
        pluck="parent", distinct=True)
    linked["Purchase Order"] = frappe.get_all(
        "Purchase Order Item", filters={"sales_order": so_name},
        pluck="parent", distinct=True)
    invoices = frappe.get_all(
        "Sales Invoice Item", filters={"sales_order": so_name},
        pluck="parent", distinct=True)
    linked["Sales Invoice"] = invoices
    payments = []
    for si_name in invoices:
        payments += frappe.get_all(
            "Payment Entry Reference",
            filters={"reference_doctype": "Sales Invoice", "reference_name": si_name},
            pluck="parent", distinct=True)
    linked["Payment Entry"] = sorted(set(payments))
    return linked


def _clear_one(so_name):
    linked = _linked_docs(so_name)
    for dn_name in linked["Delivery Note"]:
        _force_clear("Delivery Note", dn_name)
    for po_name in linked["Purchase Order"]:
        _force_clear("Purchase Order", po_name)
    for pe_name in linked["Payment Entry"]:
        _force_clear("Payment Entry", pe_name)
    for si_name in linked["Sales Invoice"]:
        _force_clear("Sales Invoice", si_name)
    if frappe.db.exists("Sales Order", so_name):
        _force_clear("Sales Order", so_name)


def _orders_to_clear(since=None, until=None, limit=None):
    filters = {"sh_shopify_order_id": ["is", "set"]}
    if since and until:
        filters["transaction_date"] = ["between", [since, until]]
    elif since:
        filters["transaction_date"] = [">=", since]
    elif until:
        filters["transaction_date"] = ["<=", until]
    return frappe.get_all(
        "Sales Order", filters=filters, pluck="name",
        order_by="transaction_date asc", limit_page_length=int(limit) if limit else 0)


def run(dry_run=True, since=None, until=None, limit=None, show=10):
    """Delete Shopify-imported Sales Orders and everything hanging off them.

    dry_run -- default True. Reports what would go and deletes nothing.
    since / until -- transaction_date bounds, 'YYYY-MM-DD'. Omit both for every
                     Shopify order on the site.
    limit -- stop after this many orders, useful for a first real run.
    """
    if isinstance(dry_run, str):
        dry_run = dry_run.strip().lower() not in ("0", "false", "no", "")

    so_names = _orders_to_clear(since, until, limit)
    scope = f"{since or 'the beginning'} to {until or 'now'}"
    print(f"[clear_orders] {len(so_names)} Shopify Sales Order(s) in scope ({scope})"
          f"{' -- DRY RUN, nothing will be deleted' if dry_run else ''}")
    if not so_names:
        return {"in_scope": 0, "deleted": 0, "dry_run": bool(dry_run)}

    if dry_run:
        totals = {"Delivery Note": 0, "Purchase Order": 0,
                  "Sales Invoice": 0, "Payment Entry": 0}
        for index, so_name in enumerate(so_names, 1):
            linked = _linked_docs(so_name)
            for doctype, names in linked.items():
                totals[doctype] += len(names)
            if index <= int(show):
                detail = ", ".join(f"{len(names)} {doctype}"
                                   for doctype, names in linked.items() if names) or "no linked docs"
                print(f"  {so_name}: {detail}")
        if len(so_names) > int(show):
            print(f"  ... and {len(so_names) - int(show)} more")
        print("\nWOULD DELETE")
        print(f"  Sales Order    : {len(so_names)}")
        for doctype, count in totals.items():
            print(f"  {doctype:<15}: {count}")
        print("\nNothing was deleted. Re-run with --kwargs \"{'dry_run': 0}\" to apply.")
        return dict(totals, in_scope=len(so_names), deleted=0, dry_run=True)

    frappe.flags.in_test = True
    done = failed = 0
    try:
        for so_name in so_names:
            for attempt in range(_MAX_ATTEMPTS):
                try:
                    _clear_one(so_name)
                    done += 1
                    break
                except frappe.QueryDeadlockError:
                    frappe.db.rollback()
                    time.sleep(1)
            else:
                failed += 1
                print(f"  [clear_orders] gave up on {so_name} after "
                      f"{_MAX_ATTEMPTS} deadlocks")
            if (done + failed) % 50 == 0:
                frappe.db.commit()
                print(f"[clear_orders] progress: {done + failed}/{len(so_names)}")
    finally:
        frappe.flags.in_test = False
        frappe.db.commit()

    remaining = frappe.db.count("Sales Order", {"sh_shopify_order_id": ["is", "set"]})
    print(f"[clear_orders] deleted {done}, failed {failed}; "
          f"{remaining} Shopify Sales Order(s) left on the site")
    return {"in_scope": len(so_names), "deleted": done, "failed": failed,
            "remaining": remaining, "dry_run": False}
