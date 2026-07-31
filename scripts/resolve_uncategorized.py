"""
Read-only: for every distinct Item.sh_shopify_category value that has no
resolved shopify_category_id (confirmed live on commerce.os.alaiy.com --
~11,000+ item rows across labels like "Dog Supplies", "Dog Toys", "Cat Toy",
"Pet collar", "Bubble Envelope" showing uncategorized on Shopify despite
being set locally), search Shopify's own Standard Product Taxonomy for the
best canonical match and write a CSV proposal for manual review.

Root cause: canonical.py's push only sets payload["category"] when
frappe.db.get_value("Shopify Category", category, "shopify_category_id")
resolves to something -- silently drops it otherwise, no error logged.
These raw/short labels (as opposed to full taxonomy paths like
"Home & Garden / Decor / Slipcovers") were never run through the taxonomy
search at all, so no Shopify Category record with a real id exists for them.

Same safety shape as suggest_category_mapping.py: propose only, changes
NOTHING. A separate apply step (after manual review of the CSV) creates/
updates the Shopify Category record so canonical.py's existing lookup
starts resolving automatically -- no push-code change needed.

Requires the Shopify Category cache to be populated first (dashboard ->
Sync Categories, or fetch_shopify_taxonomy()).

Run:
    bench --site <site> console
    exec(open("/home/ubuntu/alaiy_os_bench/apps/alaiy_os_connector_shopify/scripts/resolve_uncategorized.py").read(), globals())
    suggest_category_fixes()
"""
import csv

import frappe


def _unmapped_categories():
    """
    Every distinct Item.sh_shopify_category currently in use that has no
    Shopify Category record with a real shopify_category_id -- either the
    record doesn't exist at all, or it exists with a blank id.
    """
    rows = frappe.db.sql("""
        SELECT i.sh_shopify_category AS category, count(*) AS item_count
        FROM `tabItem` i
        LEFT JOIN `tabShopify Category` sc ON sc.name = i.sh_shopify_category
        WHERE i.sh_shopify_category IS NOT NULL AND i.sh_shopify_category != ''
          AND (sc.shopify_category_id IS NULL OR sc.shopify_category_id = '')
        GROUP BY i.sh_shopify_category
        ORDER BY item_count DESC
    """, as_dict=True)
    return rows


def suggest_category_fixes():
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.product.queries import _TAXONOMY_SEARCH_QUERY

    unmapped = _unmapped_categories()
    total = len(unmapped)
    print(f"TOTAL {total} distinct unmapped sh_shopify_category values "
          f"({sum(r.item_count for r in unmapped)} items affected)", flush=True)

    client = ShopifyGraphQLClient()
    out_rows = []
    for i, row in enumerate(unmapped):
        name = row.category
        try:
            data = client.execute(_TAXONOMY_SEARCH_QUERY, {"search": name})
            edges = ((data.get("taxonomy") or {}).get("categories") or {}).get("edges") or []
            candidates = [e["node"] for e in edges if e.get("node")]
        except Exception as exc:
            print(f"ERROR searching '{name}': {exc}", flush=True)
            candidates = []

        if not candidates:
            out_rows.append({
                "loose_category": name,
                "item_count": row.item_count,
                "suggested_category_path": "",
                "suggested_category_id": "",
                "confidence": "NO_MATCH",
                "alt_1": "", "alt_2": "",
            })
            print(f"{name} ({row.item_count} items): NO MATCH", flush=True)
            continue

        exact = next((c for c in candidates if c.get("name", "").lower() == name.lower()), None)
        chosen = exact or candidates[0]
        chosen_id = chosen.get("id")
        chosen_path = frappe.db.get_value("Shopify Category", {"shopify_category_id": chosen_id}, "name") or chosen.get("name", "")
        alts = [c.get("name", "") for c in candidates if c is not chosen][:2]

        out_rows.append({
            "loose_category": name,
            "item_count": row.item_count,
            "suggested_category_path": chosen_path,
            "suggested_category_id": chosen_id,
            "confidence": "EXACT" if exact else "BEST_GUESS",
            "alt_1": alts[0] if len(alts) > 0 else "",
            "alt_2": alts[1] if len(alts) > 1 else "",
        })
        print(f"{name} ({row.item_count} items) -> {chosen_path} "
              f"({'EXACT' if exact else 'guess'})", flush=True)

        if (i + 1) % 20 == 0:
            print(f"progress {i+1}/{total}", flush=True)

    site_path = frappe.get_site_path("private", "files")
    out_path = f"{site_path}/uncategorized_mapping_proposal.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "loose_category", "item_count", "suggested_category_path",
            "suggested_category_id", "confidence", "alt_1", "alt_2",
        ])
        writer.writeheader()
        writer.writerows(out_rows)

    exact_count = sum(1 for r in out_rows if r["confidence"] == "EXACT")
    guess_count = sum(1 for r in out_rows if r["confidence"] == "BEST_GUESS")
    none_count = sum(1 for r in out_rows if r["confidence"] == "NO_MATCH")
    print(f"\nDONE. {exact_count} exact, {guess_count} best-guess, {none_count} no match.", flush=True)
    print(f"Wrote {len(out_rows)} rows to {out_path}", flush=True)
    return out_rows
