"""
Canonical/fingerprint form and Shopify productSet payload builders --
moved verbatim from product_sync.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.variants import (
    _variant_canonical, _variant_set_payload,
)
from alaiy_os_connector_shopify.shopify.product.media import _item_images
from alaiy_os_connector_shopify.shopify.product.tags import _item_tags
from alaiy_os_connector_shopify.shopify.product.seo import _seo_values


def _product_canonical(item, variants, settings) -> dict:
    canonical = {"title": item.item_name, "variants": [
        _variant_canonical(v, settings) for v in variants]}
    # Include status so flipping Active<->Draft actually re-pushes (the
    # fingerprint guard skips the push when canonical is unchanged).
    canonical["status"] = "DRAFT" if (item.get("sh_shopify_status") == "Draft") else "ACTIVE"
    if settings.sh_push_description:
        canonical["description"] = item.description or ""
    if settings.sh_push_vendor:
        canonical["vendor"] = item.brand or ""
    if settings.sh_push_product_type:
        canonical["product_type"] = item.get("sh_shopify_product_type") or ""
    if settings.sh_push_images:
        canonical["images"] = _item_images(item, settings)
    canonical["tags"] = sorted(_item_tags(item))
    seo = _seo_values(item)
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


def _product_set_input(item, variants: list, settings, client=None) -> dict:
    """Shared by templates (variants = real children) and simple items
    (variants = [item] itself, standing in as its own only variant). Always
    the full desired state, never a partial patch -- used for both a normal
    push and an archive (see archive_item), so it doesn't matter whether
    productSet treats omitted fields as "leave alone" or "clear"."""
    option_names = []
    for v in variants:
        for a in (v.attributes or []):
            if a.attribute not in option_names:
                option_names.append(a.attribute)
    if not option_names:
        option_names = ["Title"]

    payload = {
        "title": item.item_name,
        # Active vs Draft comes from the template's sh_shopify_status; pushing
        # never leaves ARCHIVED (re-enabling a product unarchives it) --
        # archive_item() overrides this back to ARCHIVED explicitly.
        "status": "DRAFT" if (item.get("sh_shopify_status") == "Draft") else "ACTIVE",
        "productOptions": _product_options_payload(option_names, variants),
        "variants": [
            _variant_set_payload(v, settings, option_names) for v in variants
        ],
    }
    if settings.sh_push_description:
        payload["descriptionHtml"] = item.description or ""
    if settings.sh_push_vendor and item.brand:
        payload["vendor"] = item.brand
    if settings.sh_push_product_type and item.get("sh_shopify_product_type"):
        payload["productType"] = item.sh_shopify_product_type
    if settings.sh_push_images:
        images = _item_images(item, settings)
        if images:
            payload["files"] = [
                {"originalSource": url, "contentType": "IMAGE"} for url in images
            ]
    tags = _item_tags(item)
    if tags:
        payload["tags"] = sorted(tags)
    if item.get("sh_shopify_category"):
        # sh_shopify_category is now a Link to Shopify Category doctype
        category_id = frappe.db.get_value(
            "Shopify Category", item.sh_shopify_category, "shopify_category_id"
        )
        if category_id:
            payload["category"] = category_id
    seo = {k: v for k, v in _seo_values(item).items() if v}
    if seo:
        payload["seo"] = seo
    return payload
