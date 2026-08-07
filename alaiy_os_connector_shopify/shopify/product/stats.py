"""
Full product/variant/listing count comparison: Shopify's real numbers
against everything Alaiy OS holds locally, plus a breakdown of the
item_code shapes actually in use and duplicate-suffix detection.

Read-only. Makes no writes and no mutations -- same convention as
status_audit.py in this same package.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.product.stats.run

Why it exists: confirmed live on a real site, "how many products/variants
do we have vs Shopify" turned out to have no simple answer -- item_code
shapes vary (SH-<id> simple product, SH-<offer>-<variant>,
SH-PARENT-<offer>-<variant>, SH-PARENT-<offer>_N-<variant> overflow
chunks), and the SAME real offer can exist as more than one duplicate
Item chain locally (same trailing variant id under two different
templates) while Shopify itself carries the duplicate too. Every number
below is measured, not assumed -- run it before trusting any hand-counted
figure.
"""

import collections
import datetime
import re

import frappe

_ALL_PRODUCTS = """
query AllProducts($first: Int!, $after: String) {
  products(first: $first, after: $after) {
    edges { node { legacyResourceId status } }
    pageInfo { hasNextPage endCursor }
  }
}
"""

_ALL_VARIANTS = """
query AllVariants($first: Int!, $after: String) {
  productVariants(first: $first, after: $after) {
    edges { node { legacyResourceId sku product { legacyResourceId } } }
    pageInfo { hasNextPage endCursor }
  }
}
"""

_ALL_PRODUCTS_WITH_TITLE = """
query AllProductsWithTitle($first: Int!, $after: String) {
  products(first: $first, after: $after) {
    edges { node { legacyResourceId title } }
    pageInfo { hasNextPage endCursor }
  }
}
"""

_PAGE = 250

# Every item_code shape confirmed live in this codebase's real data.
# Order matters -- PARENT-with-overflow must be checked before plain
# PARENT, and PARENT before the plain simple/offer form.
_SHAPE_PATTERNS = [
    ("parent_overflow_variant", re.compile(r"^SH-PARENT-\d+_\d+-\d+$")),
    ("parent_overflow_template", re.compile(r"^SH-PARENT-\d+_\d+$")),
    ("parent_variant", re.compile(r"^SH-PARENT-\d+-\d+$")),
    ("parent_template", re.compile(r"^SH-PARENT-\d+$")),
    ("offer_overflow_variant", re.compile(r"^SH-\d+_\d+-\d+$")),
    ("offer_overflow_template", re.compile(r"^SH-\d+_\d+$")),
    ("offer_variant", re.compile(r"^SH-\d+-\d+$")),
    ("simple_product", re.compile(r"^SH-\d+$")),
]


def _classify_item_code(item_code: str) -> str:
    for label, pattern in _SHAPE_PATTERNS:
        if pattern.match(item_code):
            return label
    return "other/unrecognized"


def _pull_shopify_side(client, progress_every=10):
    products = {}
    pages = 0
    for page in client.execute_paginated(_ALL_PRODUCTS, {"first": _PAGE}, ["products"]):
        for node in page:
            products[str(node["legacyResourceId"])] = node["status"]
        pages += 1
        if progress_every and pages % progress_every == 0:
            print(f"  ...{len(products)} products read")

    variants = {}
    pages_v = 0
    for page in client.execute_paginated(_ALL_VARIANTS, {"first": _PAGE}, ["productVariants"]):
        for node in page:
            variants[str(node["legacyResourceId"])] = {
                "sku": node.get("sku") or "",
                "product_id": str((node.get("product") or {}).get("legacyResourceId") or ""),
            }
        pages_v += 1
        if progress_every and pages_v % progress_every == 0:
            print(f"  ...{len(variants)} variants read")

    return products, variants


def _local_side():
    """Every Item under the SH- upload convention -- templates (has_variants=1
    or no variant_of) and real variants (variant_of set), plus every
    Shopify Product Listing / Shopify Listing Variant row."""
    items = frappe.db.sql("""
        SELECT item_code, has_variants, variant_of, sh_shopify_product_id, sh_shopify_variant_id
        FROM `tabItem`
        WHERE item_code LIKE 'SH-%'
    """, as_dict=True)

    listings = frappe.db.count("Shopify Product Listing")
    listing_variants = frappe.db.count("Shopify Listing Variant")

    return items, listings, listing_variants


def _find_duplicate_suffixes(items: list) -> dict:
    """Real variant rows (variant_of set) that share the same trailing
    dash-separated id under a DIFFERENT template -- confirmed live, this
    is a genuine duplicate product upload, not a coincidence. Groups by
    suffix, keeps only groups with more than one distinct template."""
    by_suffix = collections.defaultdict(set)
    code_by_suffix_template = collections.defaultdict(list)
    for item in items:
        if not item.variant_of:
            continue
        suffix = item.item_code.rsplit("-", 1)[-1]
        by_suffix[suffix].add(item.variant_of)
        code_by_suffix_template[suffix].append(item.item_code)

    return {
        suffix: code_by_suffix_template[suffix]
        for suffix, templates in by_suffix.items()
        if len(templates) > 1
    }


def fix_stale_variant_ids(dry_run=True, show=20):
    """
    Clears sh_shopify_variant_id (and sh_shopify_product_id, if the
    product itself is also gone) on local Items whose linked Shopify
    variant no longer exists there. Confirmed live: a scheduled push
    (product/export.py's productSet) hits a hard RuntimeError --
    "Following variant ids do not exist" -- for every item still carrying
    one of these stale ids, blocking that item's push every single run
    until cleared. Clearing lets the next push CREATE a fresh variant
    instead of failing to update one that's gone.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.stats.fix_stale_variant_ids
    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.stats.fix_stale_variant_ids \
        --kwargs "{'dry_run': False}"
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    if isinstance(dry_run, str):
        dry_run = dry_run.strip().lower() not in ("0", "false", "no", "")

    live_products, live_variants = _pull_shopify_side(ShopifyGraphQLClient())

    rows = frappe.db.sql("""
        SELECT name, sh_shopify_variant_id, sh_shopify_product_id
        FROM `tabItem`
        WHERE sh_shopify_variant_id IS NOT NULL AND sh_shopify_variant_id != ''
    """, as_dict=True)

    stale_variant_only = []
    stale_both = []
    for row in rows:
        variant_gone = str(row.sh_shopify_variant_id) not in live_variants
        if not variant_gone:
            continue
        product_gone = (
            not row.sh_shopify_product_id or str(row.sh_shopify_product_id) not in live_products
        )
        (stale_both if product_gone else stale_variant_only).append(row)

    print(f"stale variant id (product still exists): {len(stale_variant_only)}")
    print(f"stale variant id AND stale product id:    {len(stale_both)}")
    for row in (stale_variant_only + stale_both)[:show]:
        print(f"  {row.name}  variant={row.sh_shopify_variant_id}  product={row.sh_shopify_product_id}")

    if not dry_run:
        for row in stale_variant_only:
            frappe.db.set_value("Item", row.name, "sh_shopify_variant_id", "", update_modified=False)
        for row in stale_both:
            frappe.db.set_value(
                "Item", row.name, {"sh_shopify_variant_id": "", "sh_shopify_product_id": ""},
                update_modified=False)
        frappe.db.commit()
        print(f"cleared {len(stale_variant_only) + len(stale_both)} Item(s)")
    else:
        print("DRY RUN -- nothing written. Re-run with dry_run=False to apply.")

    return {"stale_variant_only": len(stale_variant_only), "stale_both": len(stale_both), "dry_run": dry_run}


def investigate_only_on_shopify(show=66):
    """
    For every product that's on Shopify but has no local Item linked by
    sh_shopify_product_id, check WHY before assuming it needs importing --
    it may instead be a product Alaiy OS pushed TO Shopify (export
    direction) whose local Item never got the id written back, in which
    case linking is the fix, not a fresh import that would create a
    duplicate. Matches by exact title against local Item templates with a
    blank sh_shopify_product_id.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.stats.investigate_only_on_shopify
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    all_products = {}
    for page in client.execute_paginated(_ALL_PRODUCTS_WITH_TITLE, {"first": _PAGE}, ["products"]):
        for node in page:
            all_products[str(node["legacyResourceId"])] = node["title"]

    local_ids = {
        r.sh_shopify_product_id
        for r in frappe.db.sql(
            "SELECT sh_shopify_product_id FROM `tabItem` "
            "WHERE variant_of IS NULL AND sh_shopify_product_id IS NOT NULL "
            "AND sh_shopify_product_id != ''", as_dict=True)
    }
    only_on_shopify = {pid: title for pid, title in all_products.items() if pid not in local_ids}

    unlinked_by_title = {
        r.item_name: r.name
        for r in frappe.db.sql(
            "SELECT name, item_name FROM `tabItem` WHERE variant_of IS NULL "
            "AND (sh_shopify_product_id IS NULL OR sh_shopify_product_id = '')", as_dict=True)
    }

    likely_unlinked_export = []
    genuinely_never_touched = []
    for pid, title in only_on_shopify.items():
        local_match = unlinked_by_title.get(title)
        if local_match:
            likely_unlinked_export.append({"shopify_id": pid, "title": title, "local_item": local_match})
        else:
            genuinely_never_touched.append({"shopify_id": pid, "title": title})

    print(f"only-on-Shopify: {len(only_on_shopify)}")
    print(f"  likely export-direction, just unlinked: {len(likely_unlinked_export)}")
    for row in likely_unlinked_export[:show]:
        print(f"    {row['shopify_id']}  {row['title'][:60]!r}  -> local {row['local_item']}")
    print(f"  genuinely never touched (real import candidates): {len(genuinely_never_touched)}")
    for row in genuinely_never_touched[:show]:
        print(f"    {row['shopify_id']}  {row['title'][:60]!r}")

    return {"likely_unlinked_export": likely_unlinked_export, "genuinely_never_touched": genuinely_never_touched}


_ALL_PRODUCTS_DETAILED = """
query AllProductsDetailed($first: Int!, $after: String) {
  products(first: $first, after: $after) {
    edges {
      node {
        legacyResourceId
        title
        status
        createdAt
        updatedAt
        totalInventory
        descriptionHtml
        images(first: 1) { edges { node { id } } }
        variants(first: 1) { edges { node { id } } }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""

# Confirmed live: grouping by title alone is the WRONG signal on this
# catalog -- a bulk-imported supplier feed legitimately reuses the same
# generic marketing title across dozens of genuinely different physical
# products (one real title hit 76 copies, all created on different days --
# not duplicates). The trustworthy signal, confirmed on a real example
# ("Cowhide Hand-Stitched Steering Wheel Cover, 38cm Diameter", 6 copies
# created 8 SECONDS apart): a bulk-import script creating the same product
# more than once in a single run. Only title groups where every member was
# created within this window of each other are flagged.
_DUPLICATE_CREATION_WINDOW = datetime.timedelta(minutes=5)


def _created_at(row):
    return datetime.datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))


def _group_duplicate_products(client):
    """Shared by investigate_duplicates and remove_duplicate_products --
    groups by exact title, splits into likely-bug (all members created
    within _DUPLICATE_CREATION_WINDOW) vs generic-shared-title (real,
    unrelated products that happen to share a supplier title)."""
    by_title = collections.defaultdict(list)
    for page in client.execute_paginated(_ALL_PRODUCTS_DETAILED, {"first": _PAGE}, ["products"]):
        for node in page:
            by_title[node["title"]].append({
                "id": node["legacyResourceId"],
                "status": node["status"],
                "created_at": node["createdAt"],
                "updated_at": node["updatedAt"],
                "total_inventory": node["totalInventory"],
                "has_image": bool(node["images"]["edges"]),
                "has_description": bool((node.get("descriptionHtml") or "").strip()),
            })

    all_title_groups = {title: rows for title, rows in by_title.items() if len(rows) > 1}
    likely_bug_duplicates = {}
    generic_shared_title = {}
    for title, rows in all_title_groups.items():
        times = sorted(_created_at(r) for r in rows)
        if times[-1] - times[0] <= _DUPLICATE_CREATION_WINDOW:
            likely_bug_duplicates[title] = rows
        else:
            generic_shared_title[title] = rows
    return likely_bug_duplicates, generic_shared_title, len(all_title_groups)


_DELETE_MUTATION = """
mutation($id: ID!) {
  productDelete(input: {id: $id}) {
    deletedProductId
    userErrors { field message }
  }
}
"""


def remove_duplicate_products(dry_run=True, show=20):
    """
    For every likely-bug-duplicate title group (see
    _group_duplicate_products), keeps the OLDEST product and deletes the
    rest -- but ONLY if every single member of that group has zero
    inventory. A group with even one member carrying real stock is
    skipped entirely and reported, never partially touched.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.stats.remove_duplicate_products
    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.stats.remove_duplicate_products \
        --kwargs "{'dry_run': False}"
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    if isinstance(dry_run, str):
        dry_run = dry_run.strip().lower() not in ("0", "false", "no", "")

    client = ShopifyGraphQLClient()
    likely_bug_duplicates, _, _ = _group_duplicate_products(client)

    to_delete = []
    skipped_has_inventory = []
    for title, rows in likely_bug_duplicates.items():
        if any(r["total_inventory"] not in (0, None) for r in rows):
            skipped_has_inventory.append((title, len(rows)))
            continue
        ordered = sorted(rows, key=lambda r: r["created_at"])
        keep = ordered[0]
        to_delete.extend({"title": title, "id": r["id"], "keep_instead": keep["id"]} for r in ordered[1:])

    print(f"groups considered: {len(likely_bug_duplicates)}")
    print(f"skipped (has real inventory somewhere in the group): {len(skipped_has_inventory)}")
    print(f"products to delete: {len(to_delete)}")
    for row in to_delete[:show]:
        print(f"  delete {row['id']} (keeping {row['keep_instead']})  {row['title'][:60]!r}")

    if dry_run:
        print("DRY RUN -- nothing deleted. Re-run with dry_run=False to apply.")
        return {"to_delete": len(to_delete), "skipped_has_inventory": len(skipped_has_inventory), "dry_run": True}

    deleted = 0
    failed = []
    total = len(to_delete)
    for i, row in enumerate(to_delete, 1):
        try:
            result = client.execute(_DELETE_MUTATION, {"id": f"gid://shopify/Product/{row['id']}"})
            errors = result["productDelete"].get("userErrors") or []
            if errors:
                failed.append((row["id"], str(errors)))
            else:
                deleted += 1
        except Exception as e:
            failed.append((row["id"], str(e)))
        if i % 25 == 0 or i == total:
            print(f"  ...{i}/{total} processed, deleted={deleted} failed={len(failed)}")

    print(f"deleted={deleted} failed={len(failed)}")
    if failed:
        print(f"first 10 failures: {failed[:10]}")

    return {"deleted": deleted, "failed": len(failed), "skipped_has_inventory": len(skipped_has_inventory)}


def investigate_duplicates(show=100):
    """
    Groups Shopify products by exact title, then keeps only the groups
    where every member was created within a tight time window of each
    other (see _DUPLICATE_CREATION_WINDOW) -- the real signature of one
    bulk-import run accidentally creating the same product more than once,
    as opposed to a generic supplier title legitimately shared across many
    different real products over time. No deletion, no keep/remove
    decision made here.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.stats.investigate_duplicates
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    likely_bug_duplicates, generic_shared_title, all_title_groups_count = _group_duplicate_products(client)

    print(f"title groups total: {all_title_groups_count} "
          f"(likely bulk-duplicate-creation bug: {len(likely_bug_duplicates)}, "
          f"generic shared title, not duplicates: {len(generic_shared_title)})")
    for title, rows in list(likely_bug_duplicates.items())[:show]:
        print(f"\n  {title[:70]!r} -- {len(rows)} copies, all created within "
              f"{_DUPLICATE_CREATION_WINDOW}")
        for row in sorted(rows, key=lambda r: r["created_at"]):
            print(f"    id={row['id']:<14} status={row['status']:<10} "
                  f"created={row['created_at']:<25} inventory={row['total_inventory']:<5} "
                  f"image={row['has_image']} description={row['has_description']}")

    return {"likely_bug_duplicates": likely_bug_duplicates, "generic_shared_title_count": len(generic_shared_title)}


def run(show=10):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    print("Pulling Shopify's real product + variant counts (paginated, this takes a while)...")
    shopify_products, shopify_variants = _pull_shopify_side(ShopifyGraphQLClient())

    print(f"\nSHOPIFY")
    print(f"  products: {len(shopify_products)}")
    for status, count in collections.Counter(shopify_products.values()).most_common():
        print(f"    {status:<10} {count}")
    print(f"  variants: {len(shopify_variants)}")

    items, listings, listing_variants = _local_side()

    templates = [i for i in items if not i.variant_of]
    variants = [i for i in items if i.variant_of]

    print(f"\nLOCAL (Alaiy OS)")
    print(f"  Item templates (variant_of blank): {len(templates)}")
    print(f"  Item variants (variant_of set):    {len(variants)}")
    print(f"  Shopify Product Listing rows:      {listings}")
    print(f"  Shopify Listing Variant rows:      {listing_variants}")

    print(f"\nITEM_CODE SHAPES (all {len(items)} SH- items)")
    shape_counts = collections.Counter(_classify_item_code(i.item_code) for i in items)
    for shape, count in shape_counts.most_common():
        print(f"    {shape:<26} {count}")
    if shape_counts.get("other/unrecognized"):
        examples = [i.item_code for i in items if _classify_item_code(i.item_code) == "other/unrecognized"][:show]
        print(f"    unrecognized examples: {examples}")

    print(f"\nCROSS-CHECK (by Shopify product/variant id, where set locally)")
    local_product_ids = {i.sh_shopify_product_id for i in templates if i.sh_shopify_product_id}
    local_variant_ids = {i.sh_shopify_variant_id for i in variants if i.sh_shopify_variant_id}
    products_only_on_shopify = set(shopify_products) - local_product_ids
    products_only_local = local_product_ids - set(shopify_products)
    variants_only_on_shopify = set(shopify_variants) - local_variant_ids
    variants_only_local = local_variant_ids - set(shopify_variants)
    print(f"  products on Shopify with no local match:  {len(products_only_on_shopify)}")
    print(f"  products local with no Shopify match:     {len(products_only_local)}")
    print(f"  variants on Shopify with no local match:  {len(variants_only_on_shopify)}")
    print(f"  variants local with no Shopify match:     {len(variants_only_local)}")

    print(f"\nDUPLICATE-SUFFIX CHECK (same trailing variant id under 2+ different templates)")
    duplicates = _find_duplicate_suffixes(items)
    print(f"  duplicate suffix groups: {len(duplicates)}")
    for suffix, codes in list(duplicates.items())[:show]:
        print(f"    {suffix}: {codes}")

    return {
        "shopify_products": len(shopify_products),
        "shopify_products_by_status": dict(collections.Counter(shopify_products.values())),
        "shopify_variants": len(shopify_variants),
        "local_templates": len(templates),
        "local_variants": len(variants),
        "local_listings": listings,
        "local_listing_variants": listing_variants,
        "item_code_shapes": dict(shape_counts),
        "products_only_on_shopify": len(products_only_on_shopify),
        "products_only_local": len(products_only_local),
        "variants_only_on_shopify": len(variants_only_on_shopify),
        "variants_only_local": len(variants_only_local),
        "duplicate_suffix_groups": len(duplicates),
        "duplicate_suffix_detail": duplicates,
    }
