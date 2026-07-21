"""
Read-only: for every distinct "messy" Item Group currently in use (a flat,
root-level group that came from Shopify's free-text productType fallback,
not a real taxonomy path -- e.g. "Backpack", "Backpacks", "Necklace"),
search Shopify's own Standard Product Taxonomy for the best canonical
match and write a CSV proposal for manual review. Changes NOTHING --
this is the "figure out the mapping" step, not the "apply it" step.

Requires the Shopify Category cache to be populated first (dashboard ->
Sync Categories, or fetch_shopify_taxonomy()) -- this script reads that
cache to get each match's full breadcrumb path, not just its bare name.

Run:
    bench --site <site> console
    exec(open("/home/ubuntu/alaiy_os_bench/apps/alaiy_os_connector_shopify/scripts/suggest_category_mapping.py").read(), globals())
    suggest_mappings()
"""
import csv

import frappe


def _loose_group_names():
    """
    Every currently-used Item Group name that is a direct child of "All
    Item Groups" AND matches some Item's own sh_shopify_product_type --
    the fingerprint of "this group came from the productType fallback,
    not a real taxonomy path".
    """
    rows = frappe.db.sql("""
        SELECT DISTINCT i.item_group
        FROM `tabItem` i
        WHERE i.sh_shopify_product_id IS NOT NULL AND i.sh_shopify_product_id != ''
          AND i.variant_of IS NULL
          AND i.item_group = i.sh_shopify_product_type
          AND i.item_group IS NOT NULL AND i.item_group != ''
    """, as_dict=True)
    return sorted(set(r.item_group for r in rows))


def suggest_mappings():
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.product.queries import _TAXONOMY_SEARCH_QUERY

    loose_names = _loose_group_names()
    total = len(loose_names)
    print(f"TOTAL {total} distinct loose (productType-fallback) Item Groups to map", flush=True)

    client = ShopifyGraphQLClient()
    rows = []
    for i, name in enumerate(loose_names):
        try:
            data = client.execute(_TAXONOMY_SEARCH_QUERY, {"search": name})
            edges = ((data.get("taxonomy") or {}).get("categories") or {}).get("edges") or []
            candidates = [e["node"] for e in edges if e.get("node")]
        except Exception as exc:
            print(f"ERROR searching '{name}': {exc}", flush=True)
            candidates = []

        if not candidates:
            rows.append({
                "loose_group": name,
                "item_count": frappe.db.count("Item", {"item_group": name}),
                "suggested_category_path": "",
                "suggested_category_id": "",
                "confidence": "NO_MATCH",
                "alt_1": "", "alt_2": "",
            })
            print(f"{name}: NO MATCH", flush=True)
            continue

        exact = next((c for c in candidates if c.get("name", "").lower() == name.lower()), None)
        chosen = exact or candidates[0]
        chosen_id = chosen.get("id")
        # Look up the cached full breadcrumb path for this id (populated by
        # fetch_shopify_taxonomy / Sync Categories) rather than just the
        # bare leaf name the search result gives us.
        chosen_path = frappe.db.get_value("Shopify Category", {"shopify_category_id": chosen_id}, "name") or chosen.get("name", "")
        alts = [c.get("name", "") for c in candidates if c is not chosen][:2]

        rows.append({
            "loose_group": name,
            "item_count": frappe.db.count("Item", {"item_group": name}),
            "suggested_category_path": chosen_path,
            "suggested_category_id": chosen_id,
            "confidence": "EXACT" if exact else "BEST_GUESS",
            "alt_1": alts[0] if len(alts) > 0 else "",
            "alt_2": alts[1] if len(alts) > 1 else "",
        })
        print(f"{name} -> {chosen_path} ({'EXACT' if exact else 'guess'})", flush=True)

        if (i + 1) % 20 == 0:
            print(f"progress {i+1}/{total}", flush=True)

    site_path = frappe.get_site_path("private", "files")
    out_path = f"{site_path}/category_mapping_proposal.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "loose_group", "item_count", "suggested_category_path",
            "suggested_category_id", "confidence", "alt_1", "alt_2",
        ])
        writer.writeheader()
        writer.writerows(rows)

    exact_count = sum(1 for r in rows if r["confidence"] == "EXACT")
    guess_count = sum(1 for r in rows if r["confidence"] == "BEST_GUESS")
    none_count = sum(1 for r in rows if r["confidence"] == "NO_MATCH")
    print(f"\nDONE. {exact_count} exact, {guess_count} best-guess, {none_count} no match.", flush=True)
    print(f"Wrote {len(rows)} rows to {out_path}", flush=True)
    return rows
