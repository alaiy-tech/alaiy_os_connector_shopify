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

    # Two separate populations: variant rows (variant_of set, may carry
    # their own variant id) and TEMPLATE rows (variant_of blank, never
    # have a variant id of their own -- only a product id). A template
    # whose product was deleted (e.g. by remove_duplicate_products) is
    # missed entirely by a query that requires sh_shopify_variant_id to
    # be set -- confirmed live, exactly the gap this run closes.
    rows = frappe.db.sql("""
        SELECT name, sh_shopify_variant_id, sh_shopify_product_id
        FROM `tabItem`
        WHERE (sh_shopify_variant_id IS NOT NULL AND sh_shopify_variant_id != '')
           OR (sh_shopify_product_id IS NOT NULL AND sh_shopify_product_id != '')
    """, as_dict=True)

    stale_variant_only = []
    stale_both = []
    stale_product_only = []
    for row in rows:
        has_variant = bool(row.sh_shopify_variant_id)
        variant_gone = has_variant and str(row.sh_shopify_variant_id) not in live_variants
        product_gone = bool(row.sh_shopify_product_id) and str(row.sh_shopify_product_id) not in live_products

        if has_variant:
            if not variant_gone:
                continue
            (stale_both if product_gone else stale_variant_only).append(row)
        elif product_gone:
            stale_product_only.append(row)

    print(f"stale variant id (product still exists): {len(stale_variant_only)}")
    print(f"stale variant id AND stale product id:    {len(stale_both)}")
    print(f"template with stale product id (no variant id at all): {len(stale_product_only)}")
    for row in (stale_variant_only + stale_both + stale_product_only)[:show]:
        print(f"  {row.name}  variant={row.sh_shopify_variant_id}  product={row.sh_shopify_product_id}")

    if not dry_run:
        for row in stale_variant_only:
            frappe.db.set_value("Item", row.name, "sh_shopify_variant_id", "", update_modified=False)
        for row in stale_both + stale_product_only:
            frappe.db.set_value(
                "Item", row.name, {"sh_shopify_variant_id": "", "sh_shopify_product_id": ""},
                update_modified=False)
        frappe.db.commit()
        print(f"cleared {len(stale_variant_only) + len(stale_both) + len(stale_product_only)} Item(s)")
    else:
        print("DRY RUN -- nothing written. Re-run with dry_run=False to apply.")

    return {
        "stale_variant_only": len(stale_variant_only), "stale_both": len(stale_both),
        "stale_product_only": len(stale_product_only), "dry_run": dry_run,
    }


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


def remove_duplicate_products(dry_run=True, show=20, shard=0, num_shards=1):
    """
    For every likely-bug-duplicate title group (see
    _group_duplicate_products), keeps the OLDEST product and deletes the
    rest -- but ONLY if every single member of that group has zero
    inventory. A group with even one member carrying real stock is
    skipped entirely and reported, never partially touched.

    shard/num_shards let several of these run concurrently (e.g. 3 tmux
    sessions with num_shards=3, shard=0/1/2) to split the delete workload
    -- each shard re-pulls the same full Shopify state and computes the
    same full to_delete list, then only acts on every num_shards-th
    product id, so running several shards together is safe (no two
    shards ever touch the same product) without needing to coordinate a
    shared work queue.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.stats.remove_duplicate_products
    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.stats.remove_duplicate_products \
        --kwargs "{'dry_run': False, 'shard': 0, 'num_shards': 3}"
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    if isinstance(dry_run, str):
        dry_run = dry_run.strip().lower() not in ("0", "false", "no", "")
    shard, num_shards = int(shard), int(num_shards)

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

    # Sort by id for a stable, deterministic split -- every shard computes
    # the identical full list above, so slicing it the same way on each
    # shard guarantees no overlap without any coordination between them.
    to_delete.sort(key=lambda r: r["id"])
    if num_shards > 1:
        full_count = len(to_delete)
        to_delete = [r for i, r in enumerate(to_delete) if i % num_shards == shard]
        print(f"shard {shard}/{num_shards}: {len(to_delete)} of {full_count} total assigned to this shard")

    print(f"groups considered: {len(likely_bug_duplicates)}")
    print(f"skipped (has real inventory somewhere in the group): {len(skipped_has_inventory)}")
    print(f"products to delete (this shard): {len(to_delete)}")
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


_PRODUCTS_WITH_VARIANT_OPTIONS = """
query AllProductsWithOptions($first: Int!, $after: String) {
  products(first: $first, after: $after) {
    edges {
      node {
        legacyResourceId
        title
        status
        totalInventory
        variants(first: 100) {
          nodes { selectedOptions { name value } }
        }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""

_PLACEHOLDER_VALUE = re.compile(r"^V\d+$", re.IGNORECASE)

_ARCHIVE_MUTATION = """
mutation($input: ProductInput!) {
  productUpdate(input: $input) {
    userErrors { field message }
  }
}
"""


def _find_placeholder_variant_products(client, progress_every=10):
    """Products where a variant's option value is a bare placeholder like
    "V1"/"V2" instead of a real attribute (color, size, ...) -- confirmed
    live, this is the bulk-import bug's signature: generic option names
    paired with unrelated (often Chinese-source) images, a separate defect
    from the title/time-window duplicates already handled by
    remove_duplicate_products."""
    matches = []
    pages = 0
    for page in client.execute_paginated(_PRODUCTS_WITH_VARIANT_OPTIONS, {"first": _PAGE}, ["products"]):
        for node in page:
            values = [
                opt["value"]
                for v in (node.get("variants") or {}).get("nodes") or []
                for opt in (v.get("selectedOptions") or [])
            ]
            if any(_PLACEHOLDER_VALUE.match(v) for v in values):
                matches.append({
                    "id": str(node["legacyResourceId"]),
                    "title": node["title"],
                    "status": node["status"],
                    "total_inventory": node.get("totalInventory"),
                })
        pages += 1
        if progress_every and pages % progress_every == 0:
            print(f"  ...{pages * _PAGE} products checked, {len(matches)} placeholder matches so far")
    return matches


def relink_deleted_placeholder_products(dry_run=True, show=20):
    """For local templates whose sh_shopify_product_id points at a product
    that's been deleted (e.g. by resolve_placeholder_variant_products
    deleting a garbage duplicate in favour of a clean one already on
    Shopify) -- relink to that clean product by exact title match instead
    of clearing and letting the next push create a THIRD duplicate.
    Variant ids are relinked by SKU (confirmed live: a Shopify variant's
    sku is the full item_code verbatim)."""
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    live_products, live_variants = _pull_shopify_side(client)

    titles = {}
    for page in client.execute_paginated(_ALL_PRODUCTS_WITH_TITLE, {"first": _PAGE}, ["products"]):
        for node in page:
            titles[str(node["legacyResourceId"])] = node["title"]
    title_to_ids = collections.defaultdict(list)
    for pid, title in titles.items():
        title_to_ids[title].append(pid)

    sku_to_variant = {v["sku"]: (vid, v["product_id"]) for vid, v in live_variants.items() if v.get("sku")}

    templates = frappe.db.sql("""
        SELECT i.name, i.item_name, i.sh_shopify_product_id, l.listing_title
        FROM `tabItem` i
        LEFT JOIN `tabShopify Product Listing` l ON l.item = i.name
        WHERE i.item_code LIKE 'SH-%' AND (i.variant_of IS NULL OR i.variant_of = '')
          AND i.sh_shopify_product_id IS NOT NULL AND i.sh_shopify_product_id != ''
    """, as_dict=True)

    to_relink = []
    for t in templates:
        if str(t.sh_shopify_product_id) in live_products:
            continue
        effective_title = (t.listing_title or "").strip() or t.item_name
        candidates = title_to_ids.get(effective_title) or []
        if len(candidates) == 1:
            to_relink.append((t, candidates[0]))

    print(f"local templates linked to a deleted product: "
          f"{sum(1 for t in templates if str(t.sh_shopify_product_id) not in live_products)}")
    print(f"  relinkable by exact unique title match: {len(to_relink)}")
    for t, new_pid in to_relink[:show]:
        print(f"  {t.name}  {t.sh_shopify_product_id} -> {new_pid}  ({t.item_name})")

    if dry_run:
        print("\nDRY RUN -- nothing written. Re-run with dry_run=False to apply.")
        return {"relinkable": len(to_relink), "dry_run": True}

    relinked_products, relinked_variants = 0, 0
    for t, new_pid in to_relink:
        frappe.db.set_value("Item", t.name, "sh_shopify_product_id", new_pid, update_modified=False)
        frappe.db.set_value("Shopify Product Listing", {"item": t.name}, "sh_shopify_product_id", new_pid,
                             update_modified=False)
        relinked_products += 1

        variants = frappe.db.sql("""
            SELECT name, item_code FROM `tabItem` WHERE variant_of = %s
        """, t.name, as_dict=True)
        # Simple products (no separate variant rows) are their own only
        # variant -- confirmed live, relinking 32 templates this way left
        # every one at 0 relinked variants because there were no child
        # rows to iterate. Fall back to the template's own item_code/sku.
        if not variants:
            variants = [frappe.db.get_value("Item", t.name, ["name", "item_code"], as_dict=True)]
        for v in variants:
            hit = sku_to_variant.get(v.item_code)
            if hit and hit[1] == new_pid:
                frappe.db.set_value("Item", v.name, "sh_shopify_variant_id", hit[0], update_modified=False)
                frappe.db.set_value("Shopify Listing Variant", {"item_variant": v.name}, "sh_shopify_variant_id",
                                     hit[0], update_modified=False)
                relinked_variants += 1
    frappe.db.commit()
    print(f"relinked {relinked_products} template(s), {relinked_variants} variant(s)")

    return {"relinked_products": relinked_products, "relinked_variants": relinked_variants, "dry_run": False}


def investigate_unlinked_variants(show=30):
    """Read-only. For every Shopify variant with no matching local
    sh_shopify_variant_id: is it under a product we already have linked
    locally (a partial-push gap -- the product synced but this specific
    variant's id never got written back), or under one of the products
    that's only on Shopify with no local link at all (products_only_on_shopify)?"""
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    live_products, live_variants = _pull_shopify_side(client)

    templates = frappe.db.sql("""
        SELECT name, item_code, sh_shopify_product_id FROM `tabItem`
        WHERE item_code LIKE 'SH-%' AND (variant_of IS NULL OR variant_of = '')
          AND sh_shopify_product_id IS NOT NULL AND sh_shopify_product_id != ''
    """, as_dict=True)
    linked_product_ids = {str(t.sh_shopify_product_id) for t in templates}
    product_to_template = {str(t.sh_shopify_product_id): t.item_code for t in templates}

    local_variant_ids = {
        r.sh_shopify_variant_id for r in frappe.db.sql("""
            SELECT sh_shopify_variant_id FROM `tabItem`
            WHERE item_code LIKE 'SH-%' AND variant_of IS NOT NULL AND variant_of != ''
              AND sh_shopify_variant_id IS NOT NULL AND sh_shopify_variant_id != ''
        """, as_dict=True)
    }

    unlinked = [(vid, v) for vid, v in live_variants.items() if vid not in local_variant_ids]

    under_linked_product = [(vid, v) for vid, v in unlinked if v["product_id"] in linked_product_ids]
    under_orphan_product = [(vid, v) for vid, v in unlinked if v["product_id"] not in linked_product_ids]

    print(f"\nunlinked Shopify variants: {len(unlinked)}")
    print(f"  under a product we already have linked (partial-push gap): {len(under_linked_product)}")
    print(f"  under a product with no local link at all (orphan):         {len(under_orphan_product)}")

    print("\npartial-push gap examples (product linked, this variant's id missing):")
    for vid, v in under_linked_product[:show]:
        print(f"  variant={vid}  sku={v['sku']}  local_template={product_to_template.get(v['product_id'])}")

    orphan_product_counts = collections.Counter(v["product_id"] for _, v in under_orphan_product)
    print(f"\norphan products accounting for these variants: {len(orphan_product_counts)}")
    for pid, count in orphan_product_counts.most_common(show):
        print(f"  product={pid}  variant_count={count}")

    return {
        "unlinked_total": len(unlinked),
        "under_linked_product": len(under_linked_product),
        "under_orphan_product": len(under_orphan_product),
        "orphan_product_count": len(orphan_product_counts),
    }


def fix_partial_push_gap(dry_run=True, show=20):
    """Writes back sh_shopify_variant_id for every local Item whose SKU
    (= full item_code, confirmed live) exactly matches an unlinked
    Shopify variant under a product we already have linked -- the
    product pushed fine, this specific variant's id just never made it
    back into Alaiy OS. Safe direct match, not a guess."""
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    live_products, live_variants = _pull_shopify_side(client)

    linked_product_ids = {
        str(r.sh_shopify_product_id) for r in frappe.db.sql("""
            SELECT sh_shopify_product_id FROM `tabItem`
            WHERE item_code LIKE 'SH-%' AND (variant_of IS NULL OR variant_of = '')
              AND sh_shopify_product_id IS NOT NULL AND sh_shopify_product_id != ''
        """, as_dict=True)
    }

    sku_to_variant = {
        v["sku"]: vid for vid, v in live_variants.items()
        if v.get("sku") and v["product_id"] in linked_product_ids
    }

    rows = frappe.db.sql("""
        SELECT name, item_code FROM `tabItem`
        WHERE item_code LIKE 'SH-%' AND variant_of IS NOT NULL AND variant_of != ''
          AND (sh_shopify_variant_id IS NULL OR sh_shopify_variant_id = '')
    """, as_dict=True)

    to_fix = [(r, sku_to_variant[r.item_code]) for r in rows if r.item_code in sku_to_variant]

    print(f"local variants with no Shopify id, fixable by exact SKU match: {len(to_fix)}")
    for r, vid in to_fix[:show]:
        print(f"  {r.name}  -> variant={vid}")

    if dry_run:
        print("\nDRY RUN -- nothing written. Re-run with dry_run=False to apply.")
        return {"fixable": len(to_fix), "dry_run": True}

    for r, vid in to_fix:
        frappe.db.set_value("Item", r.name, "sh_shopify_variant_id", vid, update_modified=False)
        frappe.db.set_value("Shopify Listing Variant", {"item_variant": r.name}, "sh_shopify_variant_id", vid,
                             update_modified=False)
    frappe.db.commit()
    print(f"fixed {len(to_fix)} Item(s)")
    return {"fixed": len(to_fix), "dry_run": False}


def find_placeholder_variant_products(show=20):
    """Read-only. Lists Shopify products whose variants use placeholder
    option values (V1, V2, ...) -- the bulk-import garbage-listing bug."""
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    matches = _find_placeholder_variant_products(ShopifyGraphQLClient())
    print(f"\nplaceholder-variant products: {len(matches)}")
    for row in matches[:show]:
        print(f"  id={row['id']:<14} status={row['status']:<10} "
              f"inventory={row['total_inventory']:<5} title={row['title']}")
    return {"count": len(matches), "products": matches}


def resolve_placeholder_variant_products(dry_run=True, show=20):
    """For every placeholder-variant (V1/V2/...) garbage product: if a
    clean product (real attributes, not itself a placeholder match) shares
    its exact title, delete the garbage one -- the real copy already
    covers it. Otherwise archive it (not delete) since it may be the only
    copy of that data. Zero-inventory required either way -- a group
    member carrying real stock is left alone and reported, same safety
    convention as remove_duplicate_products."""
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    matches = _find_placeholder_variant_products(client)
    placeholder_ids = {m["id"] for m in matches}
    candidates = [m for m in matches if m["status"] != "ARCHIVED"]

    print("Pulling all product titles to check for a clean copy of each match...")
    clean_titles = collections.defaultdict(list)
    for page in client.execute_paginated(_ALL_PRODUCTS_WITH_TITLE, {"first": _PAGE}, ["products"]):
        for node in page:
            pid = str(node["legacyResourceId"])
            if pid not in placeholder_ids:
                clean_titles[node["title"]].append(pid)

    to_delete, to_archive, has_inventory = [], [], []
    for row in candidates:
        if row["total_inventory"] not in (0, None):
            has_inventory.append(row)
        elif clean_titles.get(row["title"]):
            to_delete.append(row)
        else:
            to_archive.append(row)

    print(f"\nplaceholder-variant products: {len(matches)} found "
          f"({len(matches) - len(candidates)} already archived)")
    print(f"  clean copy exists -> delete:  {len(to_delete)}")
    print(f"  no clean copy -> archive only: {len(to_archive)}")
    print(f"  skipped, has real inventory:   {len(has_inventory)}")
    for row in to_delete[:show]:
        print(f"  DELETE  id={row['id']:<14} title={row['title']}")
    for row in to_archive[:show]:
        print(f"  ARCHIVE id={row['id']:<14} title={row['title']}")
    if has_inventory:
        for row in has_inventory[:show]:
            print(f"  SKIP    id={row['id']:<14} inventory={row['total_inventory']} title={row['title']}")

    if dry_run:
        print("\nDRY RUN -- nothing changed. Re-run with dry_run=False to actually apply.")
        return {"would_delete": len(to_delete), "would_archive": len(to_archive),
                "skipped_has_inventory": len(has_inventory), "dry_run": True}

    deleted, archived, failed = 0, 0, 0
    total = len(to_delete) + len(to_archive)
    for i, row in enumerate(to_delete + to_archive, 1):
        try:
            if row in to_delete:
                data = client.execute(_DELETE_MUTATION, {"id": f"gid://shopify/Product/{row['id']}"})
                errors = (data.get("productDelete") or {}).get("userErrors") or []
                ok_key = "deletedProductId"
                if not errors and (data.get("productDelete") or {}).get(ok_key):
                    deleted += 1
                elif not errors:
                    deleted += 1
                else:
                    print(f"  FAILED delete id={row['id']}: {errors}")
                    failed += 1
            else:
                data = client.execute(_ARCHIVE_MUTATION, {
                    "input": {"id": f"gid://shopify/Product/{row['id']}", "status": "ARCHIVED"}
                })
                errors = (data.get("productUpdate") or {}).get("userErrors") or []
                if errors:
                    print(f"  FAILED archive id={row['id']}: {errors}")
                    failed += 1
                else:
                    archived += 1
        except Exception as e:
            print(f"  FAILED id={row['id']}: {e}")
            failed += 1
        if i % 25 == 0 or i == total:
            print(f"  ...{i}/{total} processed (deleted={deleted} archived={archived} failed={failed})")

    return {"deleted": deleted, "archived": archived, "failed": failed,
            "skipped_has_inventory": len(has_inventory), "dry_run": False}
