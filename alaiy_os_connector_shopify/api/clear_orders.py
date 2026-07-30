"""
One-off: safely wipe ALL Alaiy OS Sales Orders imported from Shopify,
without touching the live Shopify orders.

Cascade (child first): Delivery Note -> Purchase Order -> Sales Invoice ->
Payment Entry -> Sales Order. Docstatus is force-flipped via raw db.set_value
and the doc force-deleted directly, instead of going through the normal
cancel() business logic -- ERPNext's own stock-ledger/reserved-qty checks
made a proper cancel() impossible partway through a real run once a linked
doc was already cancelled by an earlier partial pass. No on_trash hook
exists for any of these doctypes (confirmed via hooks.py), and
frappe.flags.in_test forces delete_doc's own delete_dynamic_links cleanup to
run inline instead of enqueuing a background job per delete (avoids flooding
the queue on a large batch). Deadlock-safe: wrapped per-order in a retry
loop with periodic commits, since a single giant transaction across
thousands of orders collides with any concurrent writer touching the same
tables.

Run via bench execute:

  bench --site <site> execute alaiy_os_commerce.upload_scripts.clear_orders.run
"""

import time

import frappe


def _force_clear(doctype, name):
    if frappe.db.get_value(doctype, name, "docstatus") == 1:
        frappe.db.set_value(doctype, name, "docstatus", 2)
    frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)


def _clear_one(so_name):
    dn_rows = frappe.get_all(
        "Delivery Note Item", filters={"against_sales_order": so_name}, pluck="parent", distinct=True)
    for dn_name in dn_rows:
        _force_clear("Delivery Note", dn_name)

    po_rows = frappe.get_all(
        "Purchase Order Item", filters={"sales_order": so_name}, pluck="parent", distinct=True)
    for po_name in po_rows:
        _force_clear("Purchase Order", po_name)

    si_rows = frappe.get_all(
        "Sales Invoice Item", filters={"sales_order": so_name}, pluck="parent", distinct=True)
    for si_name in si_rows:
        pe_rows = frappe.get_all(
            "Payment Entry Reference",
            filters={"reference_doctype": "Sales Invoice", "reference_name": si_name},
            pluck="parent", distinct=True)
        for pe_name in pe_rows:
            _force_clear("Payment Entry", pe_name)
        _force_clear("Sales Invoice", si_name)

    if frappe.db.exists("Sales Order", so_name):
        _force_clear("Sales Order", so_name)


def run():
    so_names = frappe.get_all(
        "Sales Order", filters={"sh_shopify_order_id": ["is", "set"]}, pluck="name")
    print(f"[clear_orders] to clear: {len(so_names)}")

    frappe.in_test = True
    done = 0
    try:
        for so_name in so_names:
            for attempt in range(3):
                try:
                    _clear_one(so_name)
                    break
                except frappe.QueryDeadlockError:
                    frappe.db.rollback()
                    time.sleep(1)
            done += 1
            if done % 50 == 0:
                frappe.db.commit()
                print(f"[clear_orders] progress: {done}/{len(so_names)}")
    finally:
        frappe.in_test = False

    frappe.db.commit()
    remaining = frappe.db.count("Sales Order", {"sh_shopify_order_id": ["is", "set"]})
    print(f"[clear_orders] done, remaining sales orders with shopify id: {remaining}")
