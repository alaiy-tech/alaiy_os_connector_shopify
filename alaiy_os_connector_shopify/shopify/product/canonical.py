"""
Canonical/fingerprint form and Shopify productSet payload builders --
moved verbatim from product_sync.py, unchanged.
"""

import json

import frappe

from alaiy_os_connector_shopify.shopify.product.variants import (
    _variant_canonical, _variant_set_payload,
)
from alaiy_os_connector_shopify.shopify.product.tags import _item_tags
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver
from alaiy_os_connector_shopify.shopify.product import status as status_map


def _product_canonical(item, variants, settings, listing) -> dict:
    # Effective (post-fallback) values -- MUST fingerprint what actually gets
    # pushed, not the raw Listing fields, so an inherited Item-level change a
    # blank Listing field is currently showing still re-pushes (see #58).
    canonical = {
        "title": listing_resolver.effective_title(listing, item),
        "variants": [_variant_canonical(v, settings, listing) for v in variants],
    }
    # Status now lives on the Listing; keep flipping Active<->Draft re-pushing.
    canonical["status"] = status_map.to_shopify(listing.sh_shopify_status)
    canonical["description"] = listing_resolver.effective_description(listing, item)
    canonical["vendor"] = item.brand or ""
    canonical["product_type"] = listing_resolver.effective_product_type(listing, item)
    canonical["category"] = listing_resolver.effective_category(listing, item) or ""
    canonical["images"] = listing_resolver.effective_images(listing, item, settings)
    canonical["tags"] = sorted(_item_tags(item))
    seo = listing_resolver.effective_seo(listing, item)
    canonical["seo_title"] = seo["title"]
    canonical["seo_description"] = seo["description"]
    return canonical


def _product_options_payload(option_names: list, variants: list) -> list:
    """One entry per option, `values` deduplicated across all variants in
    first-seen order -- e.g. Size: [Small, Large], not one row per variant."""
    options = []
    for name in option_names:
        seen = []
        for v in variants:
            attrs = {a.attribute: a.attribute_value for a in (v.attributes or [])}
            value = attrs.get(name) or "Default"
            if value not in seen:
                seen.append(value)
        options.append({"name": name, "values": [{"name": v} for v in seen]})
    return options


_PRIORITY_OPTION_NAMES = ["size", "color", "colour", "style"]


def _split_options_over_limit(option_names: list) -> tuple:
    """
    Shopify hard-caps productOptions at 3 -- confirmed live, real products
    rejected outright with "Can only specify a maximum of 3 options".
    Team decision: keep Size/Color/Style as the real Shopify options when
    present, push anything beyond that into a metafield instead of failing
    the whole product. Returns (kept, overflow).
    """
    if len(option_names) <= 3:
        return option_names, []
    priority = [n for n in option_names if n.lower() in _PRIORITY_OPTION_NAMES]
    rest = [n for n in option_names if n not in priority]
    kept = (priority + rest)[:3]
    overflow = [n for n in option_names if n not in kept]
    return kept, overflow


def _product_set_input(item, variants: list, settings, listing, client=None) -> dict:
    """Shared by templates (variants = real children) and simple items
    (variants = [item] itself, standing in as its own only variant). Always
    the full desired state, never a partial patch -- used for both a normal
    push and an archive (see archive_item), so it doesn't matter whether
    productSet treats omitted fields as "leave alone" or "clear"."""
    all_option_names = []
    for v in variants:
        for a in (v.attributes or []):
            if a.attribute not in all_option_names:
                all_option_names.append(a.attribute)
    if not all_option_names:
        all_option_names = ["Title"]
    option_names, overflow_names = _split_options_over_limit(all_option_names)

    payload = {
        "title": listing_resolver.effective_title(listing, item),
        # Active vs Draft comes from the Listing's sh_shopify_status; pushing
        # never leaves ARCHIVED (re-enabling a product unarchives it) --
        # archive_item() overrides this back to ARCHIVED explicitly.
        "status": status_map.to_shopify(listing.sh_shopify_status),
        "productOptions": _product_options_payload(option_names, variants),
        "variants": [
            _variant_set_payload(v, settings, option_names, listing) for v in variants
        ],
    }
    metafields = []
    if overflow_names:
        # Attributes beyond Shopify's 3-option cap don't disappear -- kept
        # as a per-variant metafield instead of failing the whole push.
        # Team decision (30-07-2026): Size/Color/Style stay real options,
        # anything past that goes here.
        overflow_by_sku = {}
        for v in variants:
            attrs = {a.attribute: a.attribute_value for a in (v.attributes or [])}
            extra = {name: attrs[name] for name in overflow_names if name in attrs}
            if extra:
                overflow_by_sku[v.item_code] = extra
        if overflow_by_sku:
            metafields.append({
                "namespace": "custom",
                "key": "extra_variant_attributes",
                "type": "json",
                "value": json.dumps(overflow_by_sku),
            })

    # length/width/height have no dedicated Shopify product/variant field
    # (only weight has one, via inventoryItem.measurement) -- confirmed
    # live via schema introspection. Pushed as a per-variant metafield,
    # same shape as the overflow-attributes one above, so this data isn't
    # silently stuck in Alaiy OS with no way to reach Shopify at all.
    dims_by_sku = {}
    for v in variants:
        dims = {k: v.get(k) for k in ("length", "width", "height") if v.get(k)}
        if dims:
            dims_by_sku[v.item_code] = dims
    if dims_by_sku:
        metafields.append({
            "namespace": "custom",
            "key": "dimensions",
            "type": "json",
            "value": json.dumps(dims_by_sku),
        })

    if metafields:
        payload["metafields"] = metafields

    payload["descriptionHtml"] = listing_resolver.effective_description(listing, item)
    if item.brand:
        payload["vendor"] = item.brand
    product_type = listing_resolver.effective_product_type(listing, item)
    if product_type:
        payload["productType"] = product_type
    images = listing_resolver.effective_images(listing, item, settings)
    # Shopify's productSet resolves each variant's "file" input by matching
    # its originalSource against this top-level files list -- a variant
    # image not also listed here fails with "File original source missing
    # from the product files input" even though the URL itself is valid.
    variant_images = [
        listing_resolver.effective_variant_image(listing, v.item_code) for v in variants
    ]
    all_images = list(dict.fromkeys(images + [u for u in variant_images if u]))
    if len(all_images) > 250:
        # Shopify's own hard cap on productSet's files array -- confirmed
        # live ("input array size of 385 is greater than the maximum
        # allowed of 250"). Keep product-level images first, then as many
        # variant images as fit; variants past the cut simply push without
        # their own distinct image rather than failing the whole product.
        frappe.logger().warning(
            f"Shopify: {item.name} has {len(all_images)} distinct images, "
            "trimming to 250 (productSet files array limit)."
        )
        all_images = all_images[:250]
    if all_images:
        payload["files"] = [
            {"originalSource": url, "contentType": "IMAGE"} for url in all_images
        ]
        allowed = set(all_images)
        for v_payload in payload["variants"]:
            f = v_payload.get("file")
            if f and f.get("originalSource") not in allowed:
                del v_payload["file"]
    tags = _item_tags(item)
    if tags:
        payload["tags"] = sorted(tags)
    category = listing_resolver.effective_category(listing, item)
    if category:
        # sh_shopify_category / listing_category is a Link to Shopify Category doctype
        category_id = frappe.db.get_value("Shopify Category", category, "shopify_category_id")
        if category_id:
            payload["category"] = category_id
    seo = {k: v for k, v in listing_resolver.effective_seo(listing, item).items() if v}
    if seo:
        payload["seo"] = seo
    return payload
