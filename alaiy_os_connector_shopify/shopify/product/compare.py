# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""What Shopify holds right now, against what a push would send. Reads only.

`register.listing_drift` answers "has local data changed since we last pushed"
for free, out of a stored fingerprint, and cannot say which field. This answers
which field, and costs one live Shopify call. Nothing is written on either side.

## Why this compares a subset, deliberately

The obvious implementation maps Shopify's product node onto the full key set
`canonical._product_canonical` builds and diffs the two dicts. That produces a
permanent, unfixable diff on at least two keys, and a tool that always reports
a difference is worse than no tool:

- **images** -- the canonical holds Alaiy OS file URLs
  (`/files/shirt.png`); Shopify holds its own CDN URLs for re-hosted copies of
  the same pictures. The strings never match and never will. Nothing in either
  representation is a shared identity to match them on, so this is not a
  comparison that can be repaired by normalising harder.
- **category** -- the canonical holds a `Shopify Category` docname; the node
  gives `category.fullName`, a taxonomy path. Comparing them needs the taxonomy
  gid on both sides, and the shared node fragment does not currently request
  `category { id }`. Adding it is the fix, and it is a change to the catalogue
  pull's query as well, so it is not being made inside a read tool.

Both are listed in `not_compared` on every result with the reason, rather than
silently dropped. A caller told "these four fields differ" needs to know the
sentence does not cover the whole product.

## What it does compare

Product-level: title, description, vendor, product type, status, tags and the
two SEO fields -- everything the canonical carries that has a directly
corresponding scalar on the node.

Variant-level, keyed on SKU: price, compare-at price, cost, barcode, HS code
and country of origin. The key works because `_variant_canonical` sets
`sku = variant.item_code` and the push sends that as Shopify's SKU, so the two
sides are keyed on the same string by construction. A SKU on one side only is
reported as an added or missing variant rather than as a field difference.

Money is compared through `fingerprint._money`, so Alaiy OS's `20.0` and
Shopify's `"20.00"` are the same price here for the same reason they are the
same fingerprint.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver
from alaiy_os_connector_shopify.shopify.product import status as status_map
from alaiy_os_connector_shopify.shopify.product.queries import _PRODUCT_BY_ID_QUERY
from alaiy_os_connector_shopify.shopify.product.tags import _item_tags
from alaiy_os_connector_shopify.shopify.sync_engine.fingerprint import _money

LISTING_DOCTYPE = "Shopify Product Listing"
SETTINGS = "Shopify Connector Settings"

#: Fields excluded from the diff, and why. Reported on every result -- see the
#: module docstring.
NOT_COMPARED = {
    "images": (
        "Alaiy OS holds local file URLs and Shopify holds its own CDN URLs for "
        "re-hosted copies, so the two can never be compared as strings."
    ),
    "category": (
        "Alaiy OS holds a Shopify Category record and Shopify reports a taxonomy "
        "path; comparing them needs the taxonomy id, which this query does not ask for."
    ),
    "options": (
        "Variant option structure is compared through the variants themselves, "
        "not as a product-level field."
    ),
}


def _remote_product(product_id):
    """The Shopify product node for a numeric product id, or None if it is gone.

    Imported inside the caller rather than at module scope: constructing a
    client reads the settings Single and raises on an unconfigured site, and
    this module is imported at `bench migrate` time through the pack manifest.
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    body = client.execute(_PRODUCT_BY_ID_QUERY, {"id": f"gid://shopify/Product/{product_id}"})
    return (body.get("data") or {}).get("product")


def _local_side(listing, item, settings):
    """The comparable half of what a push would send."""
    seo = listing_resolver.effective_seo(listing, item)
    return {
        "title": listing_resolver.effective_title(listing, item),
        "description": listing_resolver.effective_description(listing, item),
        "vendor": item.brand or "",
        "product_type": listing_resolver.effective_product_type(listing, item),
        "status": status_map.to_shopify(listing.sh_shopify_status),
        "tags": sorted(_item_tags(item)),
        "seo_title": seo["title"],
        "seo_description": seo["description"],
    }


def _remote_side(node):
    """The same fields, off the Shopify node."""
    seo = node.get("seo") or {}
    return {
        "title": node.get("title") or "",
        "description": node.get("descriptionHtml") or "",
        "vendor": node.get("vendor") or "",
        "product_type": node.get("productType") or "",
        "status": node.get("status") or "",
        "tags": sorted(node.get("tags") or []),
        "seo_title": seo.get("title") or "",
        "seo_description": seo.get("description") or "",
    }


def _local_variants(listing, item, settings):
    """Comparable variant fields, keyed on the SKU the push sends."""
    from alaiy_os_connector_shopify.shopify.product.export import _variants_of
    from alaiy_os_connector_shopify.shopify.product.pricing import (
        _variant_compare_at_price,
        _variant_cost,
    )

    out = {}
    for variant in _variants_of(item):
        code = variant.item_code
        out[code] = {
            "price": _money(listing_resolver.variant_price(listing, code, settings) or 0),
            "compare_at_price": _money(_variant_compare_at_price(code) or 0),
            "cost": _money(_variant_cost(code) or 0),
            "barcode": (variant.barcodes[0].barcode if variant.get("barcodes") else "") or "",
            "harmonized_system_code": variant.get("sh_harmonized_system_code") or "",
            "country_of_origin": variant.get("sh_country_of_origin") or "",
        }
    return out


def _remote_variants(node):
    """The same fields, off the node, keyed on Shopify's SKU."""
    out = {}
    for variant in ((node.get("variants") or {}).get("nodes") or []):
        sku = variant.get("sku") or ""
        if not sku:
            # A variant with no SKU cannot be matched to a local one. Reported
            # as an unmatched remote variant below rather than dropped.
            sku = f"(no sku: {variant.get('legacyResourceId')})"
        inventory_item = variant.get("inventoryItem") or {}
        unit_cost = inventory_item.get("unitCost") or {}
        out[sku] = {
            "price": _money(variant.get("price") or 0),
            "compare_at_price": _money(variant.get("compareAtPrice") or 0),
            "cost": _money(unit_cost.get("amount") or 0),
            "barcode": variant.get("barcode") or "",
            "harmonized_system_code": inventory_item.get("harmonizedSystemCode") or "",
            "country_of_origin": inventory_item.get("countryCodeOfOrigin") or "",
        }
    return out


def _diff(local, remote):
    return [
        {"field": key, "local": local[key], "shopify": remote.get(key)}
        for key in local
        if local[key] != remote.get(key)
    ]


def compare_listing(item_code):
    """Field-by-field: Alaiy OS's intended state against Shopify's current one.

    Returns `{item_code, product_id, exists_on_shopify, in_sync, changes,
    variants, not_compared, note}`. `changes` and the variant lists are what
    a push would alter; nothing is submitted.
    """
    if not frappe.db.exists(LISTING_DOCTYPE, item_code):
        frappe.throw(f"No Shopify Product Listing for '{item_code}'.")
    listing = frappe.get_doc(LISTING_DOCTYPE, item_code)
    if not listing.item or not frappe.db.exists("Item", listing.item):
        frappe.throw(f"Listing '{item_code}' points at Item '{listing.item}', which does not exist.")

    item = frappe.get_doc("Item", listing.item)
    product_id = item.sh_shopify_product_id

    if not product_id:
        return {
            "item_code": listing.name,
            "product_id": None,
            "exists_on_shopify": False,
            "in_sync": False,
            "changes": [],
            "variants": {"changed": [], "only_local": [], "only_shopify": []},
            "not_compared": NOT_COMPARED,
            "note": (
                "This product has never been pushed, so Shopify has nothing to compare "
                "against. Everything a push would send would be new."
            ),
        }

    node = _remote_product(product_id)
    if not node:
        return {
            "item_code": listing.name,
            "product_id": product_id,
            "exists_on_shopify": False,
            "in_sync": False,
            "changes": [],
            "variants": {"changed": [], "only_local": [], "only_shopify": []},
            "not_compared": NOT_COMPARED,
            "note": (
                f"Alaiy OS has product id {product_id} on this row, but Shopify returns no "
                "product for it -- it was deleted in the Shopify admin, or the id belongs "
                "to a different store."
            ),
        }

    settings = frappe.get_single(SETTINGS)
    changes = _diff(_local_side(listing, item, settings), _remote_side(node))

    local_variants = _local_variants(listing, item, settings)
    remote_variants = _remote_variants(node)
    changed_variants = []
    for sku, local_fields in local_variants.items():
        if sku not in remote_variants:
            continue
        fields = _diff(local_fields, remote_variants[sku])
        if fields:
            changed_variants.append({"sku": sku, "changes": fields})

    variants = {
        "changed": changed_variants,
        "only_local": sorted(set(local_variants) - set(remote_variants)),
        "only_shopify": sorted(set(remote_variants) - set(local_variants)),
    }
    in_sync = not changes and not any(variants.values())

    return {
        "item_code": listing.name,
        "product_id": product_id,
        "handle": node.get("handle"),
        "exists_on_shopify": True,
        "in_sync": in_sync,
        "changes": changes,
        "variants": variants,
        "not_compared": NOT_COMPARED,
        "note": (
            "Nothing was sent to Shopify. `changes` is what a push would alter, and it "
            "covers only the fields listed as compared -- see `not_compared`."
            if not in_sync
            else "Shopify matches what a push would send, across the compared fields. "
            "See `not_compared` for what this does not cover."
        ),
    }
