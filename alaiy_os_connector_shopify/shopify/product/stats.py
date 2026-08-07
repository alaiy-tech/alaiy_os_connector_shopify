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
