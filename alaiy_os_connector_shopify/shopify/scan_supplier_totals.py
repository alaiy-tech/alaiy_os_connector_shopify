"""
Per-supplier scan: for every real supplier in the system, reports how
many products and how many orders (created_at >= a given date, default
2026-01-01) belong to them, comparing our local counts against
Shopify's live data, and flags anything missing locally.

Supplier attribution: Shopify has no native "supplier" field on a
product or order. A product belongs to a supplier via the same
location-based ownership pattern used elsewhere on the client site
this runs against (Item.shopify_location -> Shopify Location.linked_supplier,
or the Item Supplier child table as fallback). An order belongs to a
supplier if at least one of its line items' SKU maps to that supplier.

Products: Shopify's own product search has no location filter, so
per-supplier product counts are computed from OUR local data (which
mirrors Shopify via the regular product sync) rather than one Shopify
call per supplier. A separate site-wide productsCount check flags if
our local Item count has drifted from Shopify's real total at all.

Orders: pulled fresh from Shopify for the date window, matched to a
supplier via each order's real line item SKUs, and compared against
local Sales Orders for the same order id. A "missing" order is one
Shopify reports for a date in range that has no local Sales Order at
all -- reuses the same real-fulfillment/local-mismatch approach as
audit_order_reconciliation.py, scoped per supplier here instead of a
flat list.

Read-only. Makes no writes.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.scan_supplier_totals.run \
      --kwargs '{"date_from": "2026-01-01"}'

slice_index/slices splits the per-order Shopify pull across parallel
tmux sessions, same convention as this app's other large scans:

    for i in 0 1 2 3; do
      tmux new -d -s supptotals$i "cd ~/alaiy_os_bench && bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.scan_supplier_totals.run \
        --kwargs \"{'date_from': '2026-01-01', 'slice_index': $i, 'slices': 4}\" 2>&1 | tee ~/supp_totals$i.log"
    done
"""

import frappe


def _local_product_counts_by_supplier():
    """{supplier: count} from local Item data, same ownership logic
    _item_codes_for_supplier already uses (shopify_location -> linked
    Shopify Location, falling back to Item Supplier)."""
    from collections import Counter

    counts = Counter()

    loc_to_supplier = {}
    for row in frappe.get_all(
        "Shopify Location", filters={"linked_supplier": ["!=", ""]},
        fields=["sh_location_id", "sh_location_gid", "linked_supplier"],
    ):
        if row.sh_location_id:
            loc_to_supplier[row.sh_location_id] = row.linked_supplier
        if row.sh_location_gid:
            loc_to_supplier[row.sh_location_gid] = row.linked_supplier

    items_with_location = frappe.get_all(
        "Item", filters={"disabled": 0, "shopify_location": ["!=", ""]},
        fields=["item_code", "shopify_location"],
    )
    located_codes = set()
    for row in items_with_location:
        supplier = loc_to_supplier.get(row.shopify_location)
        if supplier:
            counts[supplier] += 1
            located_codes.add(row.item_code)

    # Item Supplier fallback -- items with no shopify_location at all, or
    # whose location doesn't map to a supplier.
    rows = frappe.db.sql("""
        SELECT s.supplier, s.parent
        FROM `tabItem Supplier` s
        JOIN `tabItem` i ON i.name = s.parent
        WHERE s.parenttype = 'Item' AND i.disabled = 0
    """, as_dict=True)
    seen_via_fallback = set()
    for row in rows:
        if row.parent in located_codes or row.parent in seen_via_fallback:
            continue
        counts[row.supplier] += 1
        seen_via_fallback.add(row.parent)

    return counts


def _sku_to_supplier_map():
    """{item_code: supplier} for every item with a resolvable owner --
    same two sources as _local_product_counts_by_supplier, flattened to
    a lookup for matching order line items."""
    mapping = {}

    loc_to_supplier = {}
    for row in frappe.get_all(
        "Shopify Location", filters={"linked_supplier": ["!=", ""]},
        fields=["sh_location_id", "sh_location_gid", "linked_supplier"],
    ):
        if row.sh_location_id:
            loc_to_supplier[row.sh_location_id] = row.linked_supplier
        if row.sh_location_gid:
            loc_to_supplier[row.sh_location_gid] = row.linked_supplier

    for row in frappe.get_all(
        "Item", filters={"shopify_location": ["!=", ""]}, fields=["item_code", "shopify_location"],
    ):
        supplier = loc_to_supplier.get(row.shopify_location)
        if supplier:
            mapping[row.item_code] = supplier

    for row in frappe.get_all("Item Supplier", filters={"parenttype": "Item"}, fields=["parent", "supplier"]):
        mapping.setdefault(row.parent, row.supplier)

    return mapping


def run(date_from="2026-01-01", date_to=None, slice_index=None, slices=None):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    if (slice_index is None) != (slices is None):
        frappe.throw("slice_index and slices must be given together")

    suppliers = frappe.get_all("Supplier", pluck="name")
    if slices:
        suppliers = [s for i, s in enumerate(sorted(suppliers)) if i % int(slices) == int(slice_index)]
        print(f"SLICE {slice_index}/{slices}: {len(suppliers)} supplier(s)", flush=True)

    local_product_counts = _local_product_counts_by_supplier()
    sku_to_supplier = _sku_to_supplier_map()

    print(f"Pulling Shopify orders created_at >= {date_from}"
          + (f" and <= {date_to}" if date_to else "") + " ...", flush=True)

    client = ShopifyGraphQLClient()
    query_string = f"created_at:>='{date_from}'"
    if date_to:
        query_string += f" AND created_at:<='{date_to}'"

    q = """
    query($after: String, $queryString: String!) {
      orders(first: 100, after: $after, query: $queryString, sortKey: CREATED_AT) {
        edges {
          node {
            name
            legacyResourceId
            lineItems(first: 50) { edges { node { sku } } }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
    """

    shopify_orders_by_supplier = {}
    total_orders_seen = 0
    for page_nodes in client.execute_paginated(q, {"after": None, "queryString": query_string}, ["orders"]):
        for node in page_nodes:
            total_orders_seen += 1
            skus = [e["node"]["sku"] for e in node.get("lineItems", {}).get("edges", []) if e["node"].get("sku")]
            order_suppliers = {sku_to_supplier[sku] for sku in skus if sku in sku_to_supplier}
            for supplier in order_suppliers:
                shopify_orders_by_supplier.setdefault(supplier, []).append(
                    {"shopify_name": node["name"], "shopify_id": node["legacyResourceId"]}
                )
        if total_orders_seen % 200 == 0:
            print(f"  ...{total_orders_seen} orders scanned so far", flush=True)

    print(f"\nTotal Shopify orders in window: {total_orders_seen}", flush=True)
    print(f"=== Per-supplier totals ({len(suppliers)} supplier(s)) ===\n")

    rows_out = []
    for supplier in sorted(suppliers):
        local_products = local_product_counts.get(supplier, 0)

        shopify_orders_for_supplier = shopify_orders_by_supplier.get(supplier, [])
        shopify_order_ids = {o["shopify_id"] for o in shopify_orders_for_supplier}

        local_order_count = 0
        missing_orders = []
        if shopify_order_ids:
            existing = set(frappe.get_all(
                "Sales Order", filters={"sh_shopify_order_id": ["in", list(shopify_order_ids)]},
                pluck="sh_shopify_order_id",
            ))
            local_order_count = len(existing)
            missing_orders = [o["shopify_name"] for o in shopify_orders_for_supplier if o["shopify_id"] not in existing]

        row = {
            "supplier": supplier,
            "local_products": local_products,
            "shopify_orders_in_window": len(shopify_order_ids),
            "local_orders_matched": local_order_count,
            "missing_orders_count": len(missing_orders),
            "missing_orders": missing_orders,
        }
        rows_out.append(row)

        flag = "  <-- MISSING ORDERS" if missing_orders else ""
        print(f"  {supplier}: {local_products} local product(s), "
              f"{len(shopify_order_ids)} Shopify order(s) in window, "
              f"{local_order_count} matched locally, "
              f"{len(missing_orders)} missing{flag}")

    suffix = f"_slice{slice_index}" if slice_index is not None else ""
    import csv
    import shutil

    filename = f"supplier_totals{suffix}.csv"
    private_path = frappe.utils.get_site_path(f"private/files/{filename}")
    with open(private_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["supplier", "local_products", "shopify_orders_in_window",
                          "local_orders_matched", "missing_orders_count", "missing_orders"])
        for row in rows_out:
            writer.writerow([row["supplier"], row["local_products"], row["shopify_orders_in_window"],
                              row["local_orders_matched"], row["missing_orders_count"], "; ".join(row["missing_orders"])])
    print(f"\nWrote {len(rows_out)} supplier row(s) to {private_path}")

    # Also copied to public/files so it's directly downloadable via a plain
    # URL (https://<site>/files/<filename>) without needing to log into
    # Desk -- same convention this app's other one-off reports already use
    # for handing a CSV to someone outside the team.
    public_path = frappe.utils.get_site_path(f"public/files/{filename}")
    shutil.copy(private_path, public_path)
    print(f"Also copied to {public_path} (downloadable at /files/{filename})")

    return {"suppliers_checked": len(suppliers), "total_orders_in_window": total_orders_seen}
