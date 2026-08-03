"""
Compare every product's real status on Shopify against what Alaiy OS holds.

Read-only. Makes no writes and no mutations -- it answers "do our statuses match
the store" before anything is changed on the strength of that answer.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.product.status_audit.run

Why it exists: the import maps only ACTIVE and DRAFT
(product/importer.py::_apply_product_meta). ARCHIVED matches neither branch, so
the field is never written and a new Item keeps its default -- "Active". An
archived product therefore reads Active locally. Worse than a wrong label: the
canonical builder sends ACTIVE for anything not marked Draft, so a later push can
un-archive a product the merchant deliberately archived. This report measures how
far that has already spread.
"""

import collections

import frappe

_ALL_PRODUCT_STATUS = """
query AllProductStatus($first: Int!, $after: String) {
  products(first: $first, after: $after) {
    edges { node { legacyResourceId status } }
    pageInfo { hasNextPage endCursor }
  }
}
"""

# Shopify's status -> the value sh_shopify_status would hold if it could.
# "Archived" is deliberately included even though the Select does not offer it --
# that absence is part of what this audit reports.
_LOCAL_OF = {"ACTIVE": "Active", "DRAFT": "Draft", "ARCHIVED": "Archived"}

_PAGE = 250


def _live_statuses(client, progress_every=10):
    """{legacyResourceId: status} for every product in the store."""
    live = {}
    pages = 0
    for page in client.execute_paginated(_ALL_PRODUCT_STATUS, {"first": _PAGE}, ["products"]):
        for node in page:
            live[str(node["legacyResourceId"])] = node["status"]
        pages += 1
        if progress_every and pages % progress_every == 0:
            print(f"  ...{len(live)} products read")
    return live, pages


def run(show=5):
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    live, pages = _live_statuses(ShopifyGraphQLClient())
    print(f"\nSHOPIFY -- {len(live)} product(s) over {pages} page(s)")
    for status, count in collections.Counter(live.values()).most_common():
        print(f"  {status:<10} {count}")

    rows = frappe.db.sql("""
        select it.name, it.sh_shopify_product_id as pid,
               it.sh_shopify_status as item_status, it.disabled,
               l.is_enabled, l.sh_shopify_status as listing_status
          from `tabItem` it
          left join `tabShopify Product Listing` l on l.item = it.name
         where it.variant_of is null
    """, as_dict=True)
    linked = [r for r in rows if r.pid]

    print(f"\nLOCAL -- {len(rows)} template(s), {len(linked)} with a Shopify product id")
    for status, count in collections.Counter(
            r.item_status or "<blank>" for r in linked).most_common():
        print(f"  Item.sh_shopify_status     {status:<12} {count}")
    for status, count in collections.Counter(
            r.listing_status or "<no listing>" for r in linked).most_common():
        print(f"  Listing.sh_shopify_status  {status:<12} {count}")
    print(f"  Item.disabled = 1          {sum(1 for r in linked if r.disabled)}")
    print(f"  Listing.is_enabled = 1     {sum(1 for r in linked if r.is_enabled)}")

    agree = collections.Counter()
    mismatch = collections.Counter()
    examples = collections.defaultdict(list)
    # A mismatch where the Listing is still enabled is the dangerous subset: the
    # next push sends ACTIVE and un-archives the product on Shopify.
    at_risk = 0

    for row in linked:
        remote = live.get(str(row.pid))
        if remote is None:
            continue
        want = _LOCAL_OF.get(remote, remote)
        got = row.item_status or "<blank>"
        if want == got:
            agree[remote] += 1
            continue
        key = f"{remote} on Shopify -> {got} locally"
        mismatch[key] += 1
        if remote == "ARCHIVED" and row.is_enabled:
            at_risk += 1
        if len(examples[key]) < int(show):
            examples[key].append(
                f"{row.name} (listing_enabled={row.is_enabled}, item_disabled={row.disabled})")

    print("\nCOMPARISON")
    for status, count in agree.most_common():
        print(f"  agree     {status:<10} {count}")
    if not mismatch:
        print("  no mismatches")
    for key, count in mismatch.most_common():
        print(f"\n  MISMATCH  {count:<6} {key}")
        for example in examples[key]:
            print(f"              {example}")

    local_ids = {str(r.pid) for r in linked}
    only_local = [r.name for r in linked if str(r.pid) not in live]
    only_remote = set(live) - local_ids

    print("\nEDGES")
    print(f"  product id set locally but not found on Shopify: {len(only_local)}")
    for name in only_local[:int(show)]:
        print(f"    {name}")
    print(f"  on Shopify with no local Item: {len(only_remote)}")

    if at_risk:
        print(f"\n  {at_risk} archived product(s) still have an ENABLED Listing -- "
              f"a push would set them back to ACTIVE on Shopify.")

    return {
        "shopify_total": len(live),
        "shopify_by_status": dict(collections.Counter(live.values())),
        "local_templates": len(rows),
        "local_linked": len(linked),
        "agree": sum(agree.values()),
        "mismatch": sum(mismatch.values()),
        "mismatch_detail": dict(mismatch),
        "archived_with_enabled_listing": at_risk,
        "only_local": len(only_local),
        "only_remote": len(only_remote),
    }
