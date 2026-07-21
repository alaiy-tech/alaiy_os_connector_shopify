"""
One-off: pull Shopify's live inventory quantity for every Shopify-linked
item and apply it locally via Stock Reconciliation (audited correction,
doesn't touch sales/opening-stock history).

Run inside `bench --site <site> console`:
    exec(open("pull_stock_from_shopify.py").read())
"""
import frappe
from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
from alaiy_os_connector_shopify.shopify.inventory_sync import (
    _resolve_location_pairs, _get_inventory_item_state,
)


def pull_stock_from_shopify(dry_run=True):
    client = ShopifyGraphQLClient()
    settings = frappe.get_single("Shopify Connector Settings")
    pairs = _resolve_location_pairs(settings, client)
    if not pairs:
        print("No warehouse/location pair resolved -- aborting.")
        return
    warehouse, location_id = pairs[0]
    print(f"Pulling live Shopify qty for warehouse={warehouse} location={location_id}")

    items = frappe.get_all(
        "Item",
        filters=[["sh_shopify_variant_id", "is", "set"]],
        fields=["name", "sh_shopify_variant_id"],
    )
    print(f"TOTAL {len(items)} items")

    company = frappe.db.get_value("Warehouse", warehouse, "company")
    corrections = []
    for i, item in enumerate(items):
        local_qty = frappe.db.get_value(
            "Bin", {"item_code": item.name, "warehouse": warehouse}, "actual_qty") or 0
        try:
            _, shopify_qty = _get_inventory_item_state(
                client, item.sh_shopify_variant_id, location_id)
        except Exception as exc:
            print(f"ERROR {item.name}: {exc}")
            continue
        shopify_qty = int(shopify_qty or 0)
        if int(local_qty) != shopify_qty:
            corrections.append({"item_code": item.name, "qty": shopify_qty, "was": int(local_qty)})
        if (i + 1) % 200 == 0:
            print(f"progress {i+1}/{len(items)} -- {len(corrections)} mismatches so far")

    print(f"DONE scanning. {len(corrections)} items need correction.")
    for c in corrections[:20]:
        print(f"  {c['item_code']}: {c['was']} -> {c['qty']}")
    if len(corrections) > 20:
        print(f"  ... and {len(corrections) - 20} more")

    if dry_run:
        print("\nDRY RUN -- nothing applied. Call with dry_run=False to actually correct.")
        return corrections

    if not corrections:
        print("Nothing to correct.")
        return corrections

    sr = frappe.new_doc("Stock Reconciliation")
    sr.company = company
    sr.purpose = "Stock Reconciliation"
    for c in corrections:
        sr.append("items", {"item_code": c["item_code"], "warehouse": warehouse, "qty": c["qty"]})
    sr.flags.ignore_permissions = True
    sr.insert()
    sr.submit()
    print(f"Applied. Stock Reconciliation: {sr.name}")
    return corrections
