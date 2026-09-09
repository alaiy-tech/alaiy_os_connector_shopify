"""
One-off backlog cleanup: retry the local mark-as-paid Payment Entry for
every submitted Sales Invoice created from an already-paid Shopify order
that's still showing Unpaid.

This is a ONE-TIME sweep for invoices created BEFORE _mark_invoice_paid got
its own automatic retry-once (see invoice.py) -- that fix now handles this
at import time going forward, so this script should only ever need running
once against the existing backlog, not on a recurring schedule.

Only touches invoices linked to a Sales Order with a Shopify order id
(sh_shopify_order_id set) -- leaves manually-created/non-Shopify invoices
alone.

Run via bench execute:
    bench --site <site> execute alaiy_os_connector_shopify.api.retry_unpaid_invoices.run --kwargs "{'dry_run': True}"
    bench --site <site> execute alaiy_os_connector_shopify.api.retry_unpaid_invoices.run --kwargs "{'dry_run': False}"
"""
import frappe

from alaiy_os_connector_shopify import connections


def run(dry_run=True):
    from alaiy_os_connector_shopify.shopify.order.invoice import _mark_invoice_paid

    rows = frappe.db.sql("""
        select si.name
        from `tabSales Invoice` si
        join `tabSales Invoice Item` sii on sii.parent = si.name
        join `tabSales Order` so on so.name = sii.sales_order
        where si.docstatus = 1
          and si.status != 'Paid'
          and so.sh_shopify_order_id is not null and so.sh_shopify_order_id != ''
          -- Only re-attempt orders Shopify STILL says are paid right now, not
          -- just at invoice-creation time -- a refund/partial-refund after
          -- invoicing must stay Unpaid, this script must never force that.
          and so.sh_financial_status = 'paid'
        group by si.name
    """, as_dict=True)

    print(f"[retry_unpaid_invoices] {len(rows)} unpaid Shopify-linked invoices found")
    if dry_run:
        print("[retry_unpaid_invoices] DRY RUN -- nothing changed. Re-run with dry_run=False to apply.")
        return

    settings = connections.require_enabled()
    fixed = failed = 0
    for i, row in enumerate(rows):
        si = frappe.get_doc("Sales Invoice", row.name)
        try:
            _mark_invoice_paid(si, settings)
            if frappe.db.get_value("Sales Invoice", row.name, "status") == "Paid":
                fixed += 1
            else:
                failed += 1
        except Exception as exc:
            failed += 1
            print(f"  FAILED {row.name}: {exc}")
        if (i + 1) % 50 == 0:
            frappe.db.commit()
            print(f"  progress: {i + 1}/{len(rows)}")

    frappe.db.commit()
    print(f"[retry_unpaid_invoices] done: fixed={fixed} still_failed={failed}")
