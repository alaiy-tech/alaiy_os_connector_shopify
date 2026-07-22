"""
Read-only audit: for every Shopify-linked product (template or simple
item), report its Item Group, its Shopify Category (if any), and its
Shopify Product Type. Flags:
  - NO_CATEGORY: Shopify never gave this product a Standard Taxonomy
    category at all (node.category was empty at import time) -- nothing
    to build a tree from for this one without another signal.
  - PRODUCT_TYPE_AS_ROOT: the Item Group currently equals the raw
    productType string sitting flat under "All Item Groups" instead of
    a real nested taxonomy path -- this is the actual bug pattern.
  - OK: Item Group looks like it came from a real taxonomy path (has a
    parent other than "All Item Groups", or matches a known Shopify
    Category name).

Writes a CSV to the site's private/files for full review.

Run:
    bench --site <site> console
    exec(open("/home/ubuntu/alaiy_os_bench/apps/alaiy_os_connector_shopify/scripts/audit_item_groups.py").read(), globals())
    run_audit()
"""
import csv

import frappe


def run_audit():
    items = frappe.get_all(
        "Item",
        filters=[["sh_shopify_product_id", "is", "set"], ["variant_of", "is", "not set"]],
        fields=["name", "item_name", "item_group", "sh_shopify_category", "sh_shopify_product_type"],
    )
    total = len(items)
    print(f"TOTAL {total} products to audit", flush=True)

    # Item Groups that are direct children of the root -- a real taxonomy
    # path's TOP level is a real Shopify top-level category name (e.g.
    # "Apparel & Accessories", "Jewelry"), but a flat productType fallback
    # also lands directly under root. Can't tell these apart by parent
    # alone, so the real signal is: does item_group's name literally match
    # this item's own product_type string, AND is it a root-level (no real
    # children pattern) group. Approximate via: item_group == product_type
    # (case-insensitive) as the strong signal for the bug.
    no_category = []
    product_type_as_group = []
    ok = []

    for i, item in enumerate(items):
        cat = (item.sh_shopify_category or "").strip()
        ptype = (item.sh_shopify_product_type or "").strip()
        group = (item.item_group or "").strip()

        row = {
            "item_code": item.name,
            "item_name": item.item_name,
            "item_group": group,
            "shopify_category": cat,
            "product_type": ptype,
        }

        if not cat:
            no_category.append(row)
        if ptype and group.lower() == ptype.lower():
            product_type_as_group.append(row)
        if cat and group.lower() != ptype.lower():
            ok.append(row)

        if (i + 1) % 1000 == 0:
            print(f"progress {i+1}/{total}", flush=True)

    print(f"DONE. no_category={len(no_category)} product_type_as_group={len(product_type_as_group)} ok={len(ok)}", flush=True)

    site_path = frappe.get_site_path("private", "files")
    for name, rows in [
        ("audit_no_category.csv", no_category),
        ("audit_product_type_as_group.csv", product_type_as_group),
    ]:
        path = f"{site_path}/{name}"
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["item_code", "item_name", "item_group", "shopify_category", "product_type"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {path}", flush=True)

    # Also dump distinct Item Group names currently in use by Shopify-linked
    # products, vs distinct product_type strings -- shows the overlap/mess
    # directly.
    distinct_groups = sorted(set(r["item_group"] for r in items if r.get("item_group")))
    distinct_types = sorted(set((item.sh_shopify_product_type or "").strip() for item in items if item.sh_shopify_product_type))
    print(f"\nDistinct Item Groups in use: {len(distinct_groups)}", flush=True)
    print(f"Distinct Product Types in use: {len(distinct_types)}", flush=True)
    overlap = set(g.lower() for g in distinct_groups) & set(t.lower() for t in distinct_types)
    print(f"Overlap (same string used as both): {len(overlap)}", flush=True)

    return {
        "no_category": no_category,
        "product_type_as_group": product_type_as_group,
        "ok": ok,
    }
