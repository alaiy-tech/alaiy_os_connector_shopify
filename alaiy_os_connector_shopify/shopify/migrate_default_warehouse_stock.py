"""
One-off: for EVERY item with a Bin row in ANY warehouse (not just the
shared default warehouses product import falls back to -- see
stock.py), check its REAL live Shopify location(s) and confirm the Bin
it's sitting in is actually one of them. Move it to the real warehouse
if it isn't.

"Move" means: set the real warehouse's quantity to Shopify's live
number via Stock Reconciliation, and zero the wrong warehouse's row for
that same item -- so each item ends up recorded in exactly one place,
not duplicated across a stale leftover and its real warehouse.

Read-only against Shopify (one live GraphQL call per item, via
pull_stock_from_shopify._shopify_locations). Writes only Stock
Reconciliation documents locally, nothing pushed back to Shopify,
nothing deleted.

Run via bench execute, dry-run by default:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.migrate_default_warehouse_stock.run

Apply for real:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.migrate_default_warehouse_stock.run \
        --kwargs "{'dry_run': False}"

slice_index/slices splits the work across parallel tmux sessions, same
convention as pull_stock_from_shopify.py:

    for i in 0 1 2; do
      tmux new -d -s migrate$i "cd ~/alaiy_os_bench && bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.migrate_default_warehouse_stock.run \
        --kwargs \"{'slice_index': $i, 'slices': 3}\" 2>&1 | tee ~/migrate_stock$i.log"
    done
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
    from alaiy_os_connector_shopify.shopify.pull_stock_from_shopify import _shopify_locations
    from alaiy_os_connector_shopify.shopify.inventory_sync import _resolve_location_pairs

    client = ShopifyGraphQLClient()
    settings = frappe.get_single("Shopify Connector Settings")
    pairs = _resolve_location_pairs(settings, client)
    if not pairs:
        print("No warehouse/location pair resolved -- aborting.", flush=True)
        return {"aborted": "no_location_pair"}
    warehouse_of_location = {location_gid: warehouse for warehouse, location_gid in pairs}
    print(f"{len(warehouse_of_location)} warehouse/location pair(s) mapped", flush=True)

    # Every real Item with any Bin row at all, wherever it currently sits --
    # not scoped to any particular warehouse. A row is only meaningful to
    # check if the item is actually Shopify-linked (has a real variant id
    # to look up against Shopify's live API) and not disabled (can't be
    # sold, no point correcting it).
    rows = frappe.db.sql("""
        SELECT b.item_code, b.warehouse AS current_warehouse, b.actual_qty AS current_qty,
               i.sh_shopify_variant_id, i.disabled
        FROM `tabBin` b
        JOIN `tabItem` i ON i.item_code = b.item_code
        WHERE i.sh_shopify_variant_id IS NOT NULL AND i.sh_shopify_variant_id != ''
    """, as_dict=True)

    if slices:
        rows = [r for n, r in enumerate(rows) if n % int(slices) == int(slice_index)]
        print(f"SLICE {slice_index} of {slices}", flush=True)
    total = len(rows)
    print(f"TOTAL {total} (item, warehouse) Bin row(s) to check against live Shopify", flush=True)

    moved = []
    correct = []
    skipped_disabled = []
    skipped_no_mapped_location = []

    for i, row in enumerate(rows, start=1):
        if i % 100 == 0 or i == total:
            print(f"...{i}/{total} processed ({len(moved)} to fix, {len(correct)} already correct, "
                  f"{len(skipped_no_mapped_location)} no mapped location)", flush=True)

        if row.disabled:
            skipped_disabled.append(row.item_code)
            continue

        try:
            locations = _shopify_locations(client, row.sh_shopify_variant_id)
        except Exception as exc:
            print(f"ERROR {row.item_code}: {exc}", flush=True)
            continue

        # Every real warehouse this item's LIVE Shopify data resolves to
        # right now, with its real quantity -- an item can legitimately be
        # correct in more than one warehouse if Shopify tracks it at more
        # than one location.
        matched = {warehouse_of_location[loc]: int(qty or 0)
                   for loc, qty in locations if loc in warehouse_of_location}

        if not matched:
            # Shopify has no mapped location at all for this item -- can't
            # tell where it belongs, so its current warehouse is neither
            # confirmed correct nor confirmed wrong. Leave it alone.
            skipped_no_mapped_location.append(row.item_code)
            continue

        if row.current_warehouse in matched and int(row.current_qty or 0) == matched[row.current_warehouse]:
            correct.append(row.item_code)
            continue

        if row.current_warehouse in matched:
            # Right warehouse, wrong quantity -- a real drift, not a
            # misplacement. Correct the number in place, nothing to move.
            print(f"  {row.item_code}: already in the right warehouse {row.current_warehouse}, "
                  f"qty {row.current_qty} -> {matched[row.current_warehouse]}", flush=True)
            moved.append(row.item_code)
            if not dry_run:
                _apply_correction(row.item_code, row.current_warehouse, matched[row.current_warehouse])
            continue

        # Wrong warehouse entirely -- pick the first real match as the
        # destination (an item split across multiple real locations picks
        # its first one here; the others get their own correct Bin rows
        # on their own pass through this same loop, since every Bin row
        # is checked independently).
        real_warehouse, real_qty = next(iter(matched.items()))
        print(f"  {row.item_code}: {row.current_warehouse}={row.current_qty} -> 0, "
              f"belongs in {real_warehouse} -> {real_qty}", flush=True)
        moved.append(row.item_code)
        if not dry_run:
            _apply_move(row.item_code, row.current_warehouse, real_warehouse, real_qty)

    print(
        f"\n{'Would fix' if dry_run else 'Fixed'} {len(moved)} (item, warehouse) row(s). "
        f"Already correct: {len(correct)}. "
        f"No mapped real location (left untouched): {len(skipped_no_mapped_location)}. "
        f"Disabled, skipped: {len(skipped_disabled)}.",
        flush=True,
    )
    return {
        "total": total, "moved": len(moved), "already_correct": len(correct),
        "no_mapped_location": len(skipped_no_mapped_location), "disabled": len(skipped_disabled),
        "dry_run": dry_run,
    }


def _apply_correction(item_code, warehouse, real_qty):
    """Right warehouse, wrong quantity -- a plain single-row correction."""
    company = frappe.db.get_value("Warehouse", warehouse, "company") or frappe.defaults.get_global_default("company")
    try:
        sr = frappe.new_doc("Stock Reconciliation")
        sr.company = company
        sr.purpose = "Stock Reconciliation"
        sr.append("items", {
            "item_code": item_code,
            "warehouse": warehouse,
            "qty": real_qty,
            "allow_zero_valuation_rate": 1,
        })
        sr.flags.ignore_permissions = True
        sr.insert()
        sr.submit()
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        frappe.log_error(
            title=f"migrate_default_warehouse_stock: correction failed for {item_code}",
            message=frappe.get_traceback(),
        )


def _apply_move(item_code, wrong_warehouse, real_warehouse, real_qty):
    """One Stock Reconciliation, two rows: the real warehouse corrected to
    Shopify's live quantity, the wrong warehouse zeroed -- same document,
    so both sides of the move land atomically together."""
    company = frappe.db.get_value("Warehouse", real_warehouse, "company") or frappe.defaults.get_global_default("company")
    try:
        sr = frappe.new_doc("Stock Reconciliation")
        sr.company = company
        sr.purpose = "Stock Reconciliation"
        sr.append("items", {
            "item_code": item_code,
            "warehouse": real_warehouse,
            "qty": real_qty,
            "allow_zero_valuation_rate": 1,
        })
        sr.append("items", {
            "item_code": item_code,
            "warehouse": wrong_warehouse,
            "qty": 0,
            "allow_zero_valuation_rate": 1,
        })
        sr.flags.ignore_permissions = True
        sr.insert()
        sr.submit()
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        frappe.log_error(
            title=f"migrate_default_warehouse_stock: failed for {item_code}",
            message=frappe.get_traceback(),
        )
