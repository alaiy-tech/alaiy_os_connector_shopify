"""
One-off: pull Shopify's live inventory quantity for every Shopify-linked
item and apply it locally via Stock Reconciliation (audited correction,
doesn't touch sales/opening-stock history).

Run through bench execute, not as a bare script -- a bare script has to
reimplement everything bench's own wrapper sets up (site config, logging
paths, DB connection), and on this environment that setup diverged from
what frappe.init() alone provides and failed on a log file path.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.pull_stock_from_shopify.run

One API call per item, so a large catalogue takes hours in a single process.
slice/slices splits the work across parallel tmux sessions:

    for i in 0 1 2; do
      tmux new -d -s stock$i "cd ~/alaiy_os_bench && bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.pull_stock_from_shopify.run \
        --kwargs \"{'slice_index': $i, 'slices': 3}\" 2>&1 | tee ~/pull_stock$i.log"
    done

Each slice writes its OWN Stock Reconciliation when applied -- one document
cannot be built across processes -- so a 3-way run produces 3 documents.

Dry run first:
    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.pull_stock_from_shopify.run

Then, once the dry run's mismatch list looks right, apply for real:
    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.pull_stock_from_shopify.run \
        --kwargs "{'dry_run': False}"
"""

import frappe


def run(dry_run=True, slice_index=None, slices=None):
    if isinstance(dry_run, str):
        dry_run = dry_run.strip().lower() not in ("0", "false", "no", "")

    if (slice_index is None) != (slices is None):
        frappe.throw("slice_index and slices must be given together")
    if slices is not None and not 0 <= int(slice_index) < int(slices):
        frappe.throw(f"slice_index must be between 0 and {int(slices) - 1}")

    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.inventory_sync import (
        _resolve_location_pairs, _get_inventory_item_state,
    )

    client = ShopifyGraphQLClient()
    settings = frappe.get_single("Shopify Connector Settings")
    pairs = _resolve_location_pairs(settings, client)
    if not pairs:
        print("No warehouse/location pair resolved -- aborting.", flush=True)
        return {"aborted": "no_location_pair"}
    warehouse, location_id = pairs[0]
    print(f"Pulling live Shopify qty for warehouse={warehouse} location={location_id}", flush=True)

    items = frappe.db.sql("""
        SELECT i.name, v.sh_shopify_variant_id, i.disabled
        FROM `tabItem` i
        JOIN `tabShopify Listing Variant` v ON v.item_variant = i.name
        WHERE v.sh_shopify_variant_id IS NOT NULL AND v.sh_shopify_variant_id != ''
    """, as_dict=True)
    # Slice for parallel runs. Partitioned by position, not by a range, so each
    # session gets an even mix rather than one taking every slow item -- and the
    # partition is deterministic, so a re-run of the same slice covers the same
    # items.
    if slices:
        items = [it for n, it in enumerate(items) if n % int(slices) == int(slice_index)]
        print(f"SLICE {slice_index} of {slices}", flush=True)
    total = len(items)
    print(f"TOTAL {total} items", flush=True)

    corrections = []
    skipped_disabled = []
    for i, item in enumerate(items):
        if item.disabled:
            # ERPNext's Stock Reconciliation rejects the ENTIRE document if
            # any row is a disabled Item -- confirmed live, one disabled
            # item blocked all other real corrections in the same batch.
            # A disabled item can't be sold anyway, so its stock number
            # isn't meaningful to correct; skip it rather than failing
            # everything else over it.
            skipped_disabled.append(item.name)
            continue
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
            frappe.db.commit()  # keep a long-running slice's progress visible/durable

    print(f"DONE scanning. {len(corrections)} items need correction.", flush=True)
    if skipped_disabled:
        print(f"SKIPPED {len(skipped_disabled)} disabled item(s), not corrected: {skipped_disabled}", flush=True)

    if dry_run:
        print("DRY RUN -- nothing applied. Re-run with dry_run=False to apply.", flush=True)
        return {"total": total, "corrections": len(corrections),
                "skipped_disabled": len(skipped_disabled), "dry_run": True}

    if not corrections:
        print("Nothing to correct.", flush=True)
        return {"total": total, "corrections": 0, "dry_run": False}

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
    frappe.db.commit()
    label = f" (slice {slice_index} of {slices})" if slices else ""
    print(f"Applied. Stock Reconciliation: {sr.name}{label}", flush=True)
    return {"total": total, "corrections": len(corrections),
            "reconciliation": sr.name, "dry_run": False}
