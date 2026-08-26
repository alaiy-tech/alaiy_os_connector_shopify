"""
Real per-location product counts for every ACTIVE item, built from
actual Shopify inventory level data -- not the productsCount(query:
"inventory_location_id:...") filter, which was confirmed live to be
broken (every supplier got back the same suspiciously round number --
10000/20000 -- regardless of their real product count, meaning the
filter is silently ignored and Shopify returns a store-wide/capped
total instead).

Same real, proven query shape as pull_stock_from_shopify.py (this
app's own stock-reconciliation script): for each item, ask Shopify
which locations track its variant's inventory and at what quantity.
"Belongs to" a location means real stock there (quantity > 0) -- same
lesson learned earlier this session on the Item Supplier corruption
fix: a location merely being tracked at zero stock is not real
ownership, Shopify's own inventory-tracking-at-every-location default
makes almost every item look owned by dozens of locations if "tracked
at all" were the bar.

Scoped to ACTIVE items only (Item.disabled = 0), not the full catalog
-- one Shopify API call per active item, so this is still a real-scale
scan; use slice_index/slices to split it across parallel tmux sessions.

Read-only. Makes no writes.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.scan_live_location_product_counts.run

slice_index/slices splits the per-item Shopify calls across parallel
tmux sessions, same convention as this app's other large scans:

    for i in 0 1 2 3; do
      tmux new -d -s livecounts$i "cd ~/alaiy_os_bench && bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.scan_live_location_product_counts.run \
        --kwargs \"{'slice_index': $i, 'slices': 4}\" 2>&1 | tee ~/live_counts$i.log"
    done

Once every slice has finished, combine into one Excel workbook:

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.combine_live_location_product_counts.run
"""

import frappe

_VARIANT_LOCATIONS_QUERY = """
query VariantInventoryLevels($id: ID!) {
  productVariant(id: $id) {
    inventoryItem {
      inventoryLevels(first: 50) {
        nodes {
          location { id name }
          quantities(names: ["available"]) { quantity }
        }
        pageInfo { hasNextPage }
      }
    }
  }
}
"""


def _real_stock_locations(client, variant_id):
    """[(location_gid, location_name, quantity), ...] for real stock
    only (quantity > 0) -- same "any tracked location" vs "real owner"
    distinction confirmed necessary on the Item Supplier corruption fix
    earlier this session."""
    variant_gid = f"gid://shopify/ProductVariant/{variant_id}"
    data = client.execute(_VARIANT_LOCATIONS_QUERY, {"id": variant_gid})
    variant = (data or {}).get("productVariant") or {}
    levels = (variant.get("inventoryItem") or {}).get("inventoryLevels") or {}
    nodes = levels.get("nodes") or []
    out = []
    for node in nodes:
        location = node.get("location") or {}
        quantities = node.get("quantities") or []
        qty = quantities[0].get("quantity") if quantities else 0
        if location.get("id") and (qty or 0) > 0:
            out.append((location["id"], location.get("name") or "", qty))
    return out


def run(slice_index=None, slices=None):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    if (slice_index is None) != (slices is None):
        frappe.throw("slice_index and slices must be given together")

    # sh_shopify_status is Shopify's own real ACTIVE/DRAFT/ARCHIVED status
    # (synced from Shopify, distinct from Item.disabled which is a LOCAL
    # archive flag -- disabled=0 also includes drafts, unpublished, and
    # anything else that was never explicitly disabled here, which is why
    # filtering on it alone massively overcounted "active" against what
    # Shopify itself reports). Confirmed live elsewhere in this app this
    # field can go stale, but it's still the right first-pass narrowing
    # filter here -- the per-item Shopify call below reads the real,
    # current status anyway, so a stale local flag only risks checking a
    # few extra/missing items, not reporting a wrong final count.
    items = frappe.get_all(
        "Item",
        filters={"disabled": 0, "sh_shopify_status": "active", "sh_shopify_variant_id": ["!=", ""]},
        fields=["item_code", "sh_shopify_variant_id"],
        order_by="item_code",
    )
    if slices:
        items = [it for i, it in enumerate(items) if i % int(slices) == int(slice_index)]
        print(f"SLICE {slice_index}/{slices}: {len(items)} active item(s)", flush=True)
    else:
        print(f"Checking {len(items)} active item(s)...", flush=True)

    client = ShopifyGraphQLClient()

    location_counts = {}  # location_gid -> {"name": str, "product_count": int}
    no_real_stock, errors = [], []

    for i, item in enumerate(items, 1):
        if i % 100 == 0 or i == len(items):
            print(f"  ...{i}/{len(items)} checked", flush=True)
        try:
            real_locations = _real_stock_locations(client, item.sh_shopify_variant_id)
        except Exception as e:
            errors.append((item.item_code, str(e)))
            continue

        if not real_locations:
            no_real_stock.append(item.item_code)
            continue

        for gid, name, qty in real_locations:
            entry = location_counts.setdefault(gid, {"name": name, "product_count": 0})
            entry["product_count"] += 1

    print(f"\n=== DONE: {len(items)} active item(s) checked ===")
    print(f"No real stock at any Shopify location: {len(no_real_stock)}")
    print(f"Locations with at least one real-stock product: {len(location_counts)}\n")
    for gid, entry in sorted(location_counts.items(), key=lambda kv: -kv[1]["product_count"]):
        print(f"  {entry['name']} ({gid}): {entry['product_count']} product(s)")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for code, err in errors[:15]:
            print(f"  {code}: {err}")

    suffix = f"_slice{slice_index}" if slice_index is not None else ""
    import csv
    filename = f"live_location_product_counts{suffix}.csv"
    path = frappe.utils.get_site_path(f"private/files/{filename}")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["location_gid", "location_name", "product_count"])
        for gid, entry in location_counts.items():
            writer.writerow([gid, entry["name"], entry["product_count"]])
    print(f"\nWrote {len(location_counts)} location row(s) to {path}")

    return {"items_checked": len(items), "locations_found": len(location_counts), "no_real_stock": len(no_real_stock)}
