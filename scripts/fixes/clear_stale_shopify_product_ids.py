"""
One-off: Item.sh_shopify_product_id can go stale after a store swap --
the previous store's product ids stay stamped locally even though they
don't exist in the currently-connected store, which silently hides those
items from the export candidate query (it only looks at blank ids).

Confirmed live: local DB had 893 non-variant items with sh_shopify_product_id
set, but Shopify's own productsCount returned only 298 -- the gap is stale ids.

Fetches every real product id from the connected store, then clears
sh_shopify_product_id (and the matching variant ids) on any local item
whose id isn't in that live set, so export picks them up again as fresh
candidates.

Run backgrounded, dry-run first:
    nohup ./env/bin/python -u apps/alaiy_os_connector_shopify/scripts/fixes/clear_stale_shopify_product_ids.py <site_name> --dry-run > ~/clear_stale.log 2>&1 &
    tail -f ~/clear_stale.log

Then apply:
    nohup ./env/bin/python -u apps/alaiy_os_connector_shopify/scripts/fixes/clear_stale_shopify_product_ids.py <site_name> --apply > ~/clear_stale_apply.log 2>&1 &
"""
import os
import sys

import frappe


def main(site, dry_run=True):
    sites_path = os.path.join(os.getcwd(), "sites")
    frappe.init(site=site, sites_path=sites_path)
    frappe.connect()

    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()

    live_ids = set()
    query = """
    query($cursor: String) {
      products(first: 250, after: $cursor) {
        edges { node { legacyResourceId } }
        pageInfo { hasNextPage endCursor }
      }
    }
    """
    cursor = None
    while True:
        data = client.execute(query, {"cursor": cursor})
        conn = data["products"]
        for edge in conn["edges"]:
            live_ids.add(str(edge["node"]["legacyResourceId"]))
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]

    print(f"Live products in connected store: {len(live_ids)}", flush=True)

    local_items = frappe.db.sql("""
        SELECT name, sh_shopify_product_id FROM `tabItem`
        WHERE (variant_of IS NULL OR variant_of = '')
        AND sh_shopify_product_id IS NOT NULL AND sh_shopify_product_id != ''
    """, as_dict=True)

    stale = [row for row in local_items if row.sh_shopify_product_id not in live_ids]
    print(f"Local items marked synced: {len(local_items)}, stale (not in live store): {len(stale)}", flush=True)

    if dry_run:
        for row in stale[:50]:
            print(f"  STALE: {row.name} -> {row.sh_shopify_product_id}", flush=True)
        if len(stale) > 50:
            print(f"  ... and {len(stale) - 50} more", flush=True)
        print("Dry run only -- pass --apply to clear these.", flush=True)
        return

    for row in stale:
        frappe.db.set_value("Item", row.name, "sh_shopify_product_id", "")
        frappe.db.sql("""
            UPDATE `tabShopify Listing Variant` slv
            JOIN `tabItem` i ON i.name = slv.item_variant
            SET slv.sh_shopify_variant_id = ''
            WHERE i.variant_of = %s OR i.name = %s
        """, (row.name, row.name))
    frappe.db.commit()
    print(f"Cleared {len(stale)} stale product ids.", flush=True)


if __name__ == "__main__":
    site = sys.argv[1]
    dry_run = "--apply" not in sys.argv
    main(site, dry_run=dry_run)
