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

Which warehouse to correct is asked of Shopify, not guessed locally: this site
maps 64 warehouses (one per vendor/consignor), and neither the local Bin table
nor Item Default reliably says which one a given item belongs to -- Item
Default is stuck at a placeholder group warehouse for nearly every item, and
most items have no Bin row at all until their first real stock movement. Shopify
already knows, from inventoryLevels on the variant's inventoryItem, exactly
which location(s) track it.

One API call per item, so a large catalogue takes hours in a single process.
slice/slices splits the work across parallel tmux sessions:

    for i in 0 1 2; do
      tmux new -d -s stock$i "cd ~/alaiy_os_bench && bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.pull_stock_from_shopify.run \
        --kwargs \"{'slice_index': $i, 'slices': 3}\" 2>&1 | tee ~/pull_stock$i.log"
    done

Each slice writes its OWN Stock Reconciliation(s) when applied -- one document
cannot be built across processes.

Dry run first:
    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.pull_stock_from_shopify.run

Then, once the dry run's mismatch list looks right, apply for real:
    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.pull_stock_from_shopify.run \
        --kwargs "{'dry_run': False}"
"""

import frappe

from alaiy_os_connector_shopify import connections

_VARIANT_LOCATIONS_QUERY = """
query VariantInventoryLevels($id: ID!) {
  productVariant(id: $id) {
    inventoryItem {
      id
      inventoryLevels(first: 50) {
        nodes {
          location { id }
          quantities(names: ["available"]) { quantity }
        }
        pageInfo { hasNextPage }
      }
    }
  }
}
"""


def _shopify_locations(client, variant_id):
    """[(location_gid, quantity), ...] -- every location Shopify tracks this
    variant's inventory at, not just the one location we happen to guess."""
    variant_gid = f"gid://shopify/ProductVariant/{variant_id}"
    data = client.execute(_VARIANT_LOCATIONS_QUERY, {"id": variant_gid})
    variant = data.get("productVariant") or {}
    levels = (variant.get("inventoryItem") or {}).get("inventoryLevels") or {}
    nodes = levels.get("nodes") or []
    if (levels.get("pageInfo") or {}).get("hasNextPage"):
        print(f"NOTE {variant_id}: tracked at 50+ locations, only the first 50 read", flush=True)
    out = []
    for node in nodes:
        location_gid = (node.get("location") or {}).get("id")
        quantities = node.get("quantities") or []
        qty = quantities[0].get("quantity") if quantities else 0
        if location_gid:
            out.append((location_gid, qty or 0))
    return out


def run(dry_run=True, slice_index=None, slices=None):
    if isinstance(dry_run, str):
        dry_run = dry_run.strip().lower() not in ("0", "false", "no", "")

    if (slice_index is None) != (slices is None):
        frappe.throw("slice_index and slices must be given together")
    if slices is not None and not 0 <= int(slice_index) < int(slices):
        frappe.throw(f"slice_index must be between 0 and {int(slices) - 1}")

    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.inventory_sync import _resolve_location_pairs

    client = ShopifyGraphQLClient(connections.require_enabled())
    settings = connections.require_enabled()
    pairs = _resolve_location_pairs(settings, client)
    if not pairs:
        print("No warehouse/location pair resolved -- aborting.", flush=True)
        return {"aborted": "no_location_pair"}
    print(f"{len(pairs)} warehouse/location pair(s) mapped", flush=True)
    warehouse_of_location = {location_gid: warehouse for warehouse, location_gid in pairs}

    # Scoped to Active templates -- run status_audit.fix_statuses first so
    # sh_shopify_status actually reflects Shopify (it doesn't until that's
    # run: an import predating the Archived mapping left archived products
    # reading Active). A draft/archived product's stock isn't sellable
    # inventory the storefront needs corrected right now.
    items = frappe.db.sql("""
        SELECT i.name, v.sh_shopify_variant_id, i.disabled
        FROM `tabItem` i
        JOIN `tabShopify Listing Variant` v ON v.item_variant = i.name
        JOIN `tabItem` tmpl ON tmpl.name = coalesce(i.variant_of, i.name)
        WHERE v.sh_shopify_variant_id IS NOT NULL AND v.sh_shopify_variant_id != ''
          AND tmpl.sh_shopify_status = 'Active'
    """, as_dict=True)
    # Slice for parallel runs. Partitioned by position, not by a range, so each
    # session gets an even mix rather than one taking every slow item -- and the
    # partition is deterministic, so a re-run of the same slice covers the same
    # items.
    if slices:
        items = [it for n, it in enumerate(items) if n % int(slices) == int(slice_index)]
        print(f"SLICE {slice_index} of {slices}", flush=True)
    total = len(items)
    print(f"TOTAL {total} item(s)", flush=True)

    corrections = []
    skipped_disabled = []
    skipped_no_mapped_location = []
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
        try:
            locations = _shopify_locations(client, item.sh_shopify_variant_id)
        except Exception as exc:
            print(f"ERROR {item.name}: {exc}", flush=True)
            continue

        matched = [(warehouse_of_location[loc], qty)
                   for loc, qty in locations if loc in warehouse_of_location]
        if not matched:
            skipped_no_mapped_location.append(item.name)
            continue

        for warehouse, shopify_qty in matched:
            shopify_qty = int(shopify_qty or 0)
            if shopify_qty < 0:
                # Shopify itself can report negative available qty (oversold --
                # an order went through while "continue selling when out of
                # stock" was on for that variant). Alaiy OS doesn't allow
                # negative stock by default; clamp to 0 rather than fail the
                # whole reconciliation over one variant.
                print(f"NOTE {item.name}/{warehouse}: Shopify qty is negative ({shopify_qty}), clamping to 0", flush=True)
                shopify_qty = 0
            local_qty = int(frappe.db.get_value(
                "Bin", {"item_code": item.name, "warehouse": warehouse}, "actual_qty") or 0)
            if local_qty != shopify_qty:
                corrections.append({"item_code": item.name, "warehouse": warehouse,
                                     "qty": shopify_qty, "was": local_qty})
                print(f"MISMATCH {item.name}/{warehouse}: {local_qty} -> {shopify_qty}", flush=True)

        if (i + 1) % 100 == 0:
            print(f"progress {i+1}/{total} -- {len(corrections)} mismatches so far", flush=True)
            frappe.db.commit()  # keep a long-running slice's progress visible/durable

    print(f"DONE scanning. {len(corrections)} row(s) need correction.", flush=True)
    if skipped_disabled:
        print(f"SKIPPED {len(skipped_disabled)} disabled item(s), not corrected: {skipped_disabled}", flush=True)
    if skipped_no_mapped_location:
        print(f"SKIPPED {len(skipped_no_mapped_location)} item(s) -- Shopify tracks them at no "
              f"location we have mapped to a warehouse: {skipped_no_mapped_location[:20]}", flush=True)

    if dry_run:
        print("DRY RUN -- nothing applied. Re-run with dry_run=False to apply.", flush=True)
        return {"total": total, "corrections": len(corrections),
                "skipped_disabled": len(skipped_disabled),
                "skipped_no_mapped_location": len(skipped_no_mapped_location), "dry_run": True}

    if not corrections:
        print("Nothing to correct.", flush=True)
        return {"total": total, "corrections": 0, "dry_run": False}

    # One Stock Reconciliation per warehouse -- a single document can hold rows
    # for multiple warehouses, but company is resolved per-warehouse and this
    # keeps a bad row in one warehouse from blocking another's correction.
    by_warehouse = {}
    for c in corrections:
        by_warehouse.setdefault(c["warehouse"], []).append(c)

    reconciliations = []
    for warehouse, rows in by_warehouse.items():
        company = frappe.db.get_value("Warehouse", warehouse, "company")
        sr = frappe.new_doc("Stock Reconciliation")
        sr.company = company
        sr.purpose = "Stock Reconciliation"
        for c in rows:
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
        reconciliations.append(sr.name)
        print(f"Applied {warehouse}: {sr.name}", flush=True)

    label = f" (slice {slice_index} of {slices})" if slices else ""
    print(f"Applied.{label} {len(reconciliations)} reconciliation(s): {reconciliations}", flush=True)
    return {"total": total, "corrections": len(corrections),
            "reconciliations": reconciliations, "dry_run": False}
