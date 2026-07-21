"""
One-off: pull Shopify's live inventory quantity for every Shopify-linked
item and apply it locally via Stock Reconciliation (audited correction,
doesn't touch sales/opening-stock history).

Run backgrounded (recommended -- ~1000+ items, one API call each):
    nohup ./env/bin/python -u apps/alaiy_os_connector_shopify/scripts/pull_stock_from_shopify.py <site_name> --dry-run > ~/pull_stock.log 2>&1 &
    tail -f ~/pull_stock.log

Then, once the dry run's mismatch list looks right, apply for real:
    nohup ./env/bin/python -u apps/alaiy_os_connector_shopify/scripts/pull_stock_from_shopify.py <site_name> --apply > ~/pull_stock_apply.log 2>&1 &
    tail -f ~/pull_stock_apply.log
"""
import sys

import frappe


def main(site, dry_run=True):
    frappe.init(site=site)
    frappe.connect()

    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.inventory_sync import (
        _resolve_location_pairs, _get_inventory_item_state,
    )

    client = ShopifyGraphQLClient()
    settings = frappe.get_single("Shopify Connector Settings")
    pairs = _resolve_location_pairs(settings, client)
    if not pairs:
        print("No warehouse/location pair resolved -- aborting.", flush=True)
        return
    warehouse, location_id = pairs[0]
    print(f"Pulling live Shopify qty for warehouse={warehouse} location={location_id}", flush=True)

    items = frappe.get_all(
        "Item",
        filters=[["sh_shopify_variant_id", "is", "set"]],
        fields=["name", "sh_shopify_variant_id"],
    )
    total = len(items)
    print(f"TOTAL {total} items", flush=True)

    corrections = []
    for i, item in enumerate(items):
        local_qty = frappe.db.get_value(
            "Bin", {"item_code": item.name, "warehouse": warehouse}, "actual_qty") or 0
        try:
            _, shopify_qty = _get_inventory_item_state(
                client, item.sh_shopify_variant_id, location_id)
        except Exception as exc:
            print(f"ERROR {item.name}: {exc}", flush=True)
            continue
        shopify_qty = int(shopify_qty or 0)
        if shopify_qty < 0:
            # Shopify itself can report negative available qty (oversold --
            # an order went through while "continue selling when out of
            # stock" was on for that variant). Alaiy OS doesn't allow
            # negative stock by default; clamp to 0 rather than fail the
            # whole reconciliation over one variant.
            print(f"NOTE {item.name}: Shopify qty is negative ({shopify_qty}), clamping to 0", flush=True)
            shopify_qty = 0
        if int(local_qty) != shopify_qty:
            corrections.append({"item_code": item.name, "qty": shopify_qty, "was": int(local_qty)})
            print(f"MISMATCH {item.name}: {int(local_qty)} -> {shopify_qty}", flush=True)

        if (i + 1) % 100 == 0:
            print(f"progress {i+1}/{total} -- {len(corrections)} mismatches so far", flush=True)

    print(f"DONE scanning. {len(corrections)} items need correction.", flush=True)

    if dry_run:
        print("DRY RUN -- nothing applied. Re-run with --apply to actually correct.", flush=True)
        return

    if not corrections:
        print("Nothing to correct.", flush=True)
        return

    company = frappe.db.get_value("Warehouse", warehouse, "company")
    sr = frappe.new_doc("Stock Reconciliation")
    sr.company = company
    sr.purpose = "Stock Reconciliation"
    for c in corrections:
        sr.append("items", {
            "item_code": c["item_code"],
            "warehouse": warehouse,
            "qty": c["qty"],
            # Confirmed live: without this, submit fails partway through
            # (past the docstatus flip, before the actual stock ledger/GL
            # entries are created) with "Valuation Rate required" for any
            # item that's never had a cost basis recorded -- same reasoning
            # as opening stock's own allow_zero_valuation_rate=1.
            "allow_zero_valuation_rate": 1,
        })
    sr.flags.ignore_permissions = True
    sr.insert()
    sr.submit()
    print(f"Applied. Stock Reconciliation: {sr.name}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pull_stock_from_shopify.py <site_name> [--dry-run|--apply]", flush=True)
        sys.exit(1)
    site = sys.argv[1]
    dry_run = "--apply" not in sys.argv
    main(site, dry_run=dry_run)
