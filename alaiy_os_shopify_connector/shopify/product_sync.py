"""
ERPNext -> Shopify product/variant push (Phase 2).

Gated by Item.sync_to_shopify (opt-in) -- variants inherit their template's
flag, and anything already linked (has a stored Shopify ID) keeps syncing
regardless of the flag, matching the reference connector's own rule.

Always operates at the template level: even when only one variant changed,
the whole current variant set is rebuilt and PUT to Shopify, since each
variant payload carries its own Shopify variant `id` when it has one --
Shopify updates existing variants and creates new ones from the same call.
"""

import frappe
from frappe.utils import flt

from alaiy_os_shopify_connector.shopify.client import ShopifyClient
from alaiy_os_shopify_connector.shopify.sync_engine import fingerprint
from alaiy_os_shopify_connector.shopify.sync_engine import entities


# ── Doc event entry points ──────────────────────────────────────────────────
# Never call Shopify inline inside a save transaction -- enqueue and return.

def on_item_change(doc, method=None):
    if not _sync_enabled(doc):
        return
    frappe.enqueue(
        "alaiy_os_shopify_connector.shopify.product_sync.push_item",
        queue="short",
        timeout=120,
        item_code=doc.name,
    )


def on_item_price_change(doc, method=None):
    settings = frappe.get_single("Shopify Connector Settings")
    if doc.price_list != (settings.sh_selling_price_list or "Standard Selling"):
        return
    if not frappe.db.exists("Item", doc.item_code):
        return
    item = frappe.get_doc("Item", doc.item_code)
    if not _sync_enabled(item):
        return
    frappe.enqueue(
        "alaiy_os_shopify_connector.shopify.product_sync.push_item",
        queue="short",
        timeout=120,
        item_code=doc.item_code,
    )


# ── Sync-enable gate ─────────────────────────────────────────────────────────

def _sync_enabled(item) -> bool:
    if item.get("sh_shopify_product_id") or item.get("sh_shopify_variant_id"):
        return True  # already linked -- keep it in sync regardless of the flag
    if item.get("variant_of"):
        template = frappe.db.get_value(
            "Item", item.variant_of, ["sync_to_shopify", "sh_shopify_product_id"], as_dict=True
        )
        return bool(template and (template.sync_to_shopify or template.sh_shopify_product_id))
    return bool(item.get("sync_to_shopify"))


# ── Canonical form + fingerprint ─────────────────────────────────────────────

def _variant_price(item_code: str, settings) -> float:
    price_list = settings.sh_selling_price_list or "Standard Selling"
    rate = frappe.db.get_value(
        "Item Price", {"item_code": item_code, "price_list": price_list}, "price_list_rate"
    )
    return flt(rate or 0)


def _item_images(item, settings) -> list:
    if not settings.sh_push_images:
        return []
    urls = []
    if item.image:
        urls.append(item.image)
    if item.get("slideshow") and frappe.db.exists("Website Slideshow", item.slideshow):
        slideshow = frappe.get_doc("Website Slideshow", item.slideshow)
        for row in slideshow.slideshow_items:
            if row.image and row.image not in urls:
                urls.append(row.image)
    return urls


def _variant_canonical(variant, settings) -> dict:
    return {
        "sku": variant.item_code,
        "title": variant.item_name,
        "price": _variant_price(variant.item_code, settings),
        "attributes": [
            {"attribute": a.attribute, "value": a.attribute_value}
            for a in (variant.attributes or [])
        ],
    }


def _product_canonical(item, variants, settings) -> dict:
    canonical = {"title": item.item_name, "variants": [_variant_canonical(v, settings) for v in variants]}
    if settings.sh_push_description:
        canonical["description"] = item.description or ""
    if settings.sh_push_vendor:
        canonical["vendor"] = item.brand or ""
    if settings.sh_push_product_type:
        canonical["product_type"] = item.item_group or ""
    if settings.sh_push_images:
        canonical["images"] = _item_images(item, settings)
    return canonical


# ── Shopify payload builders ─────────────────────────────────────────────────

def _variant_payload(variant, settings, option_names: list) -> dict:
    attrs = {a.attribute: a.attribute_value for a in (variant.attributes or [])}
    payload = {
        "sku": variant.item_code,
        "price": f"{_variant_price(variant.item_code, settings):.2f}",
    }
    for idx, name in enumerate(option_names, start=1):
        payload[f"option{idx}"] = attrs.get(name) or "Default"
    if variant.get("sh_shopify_variant_id"):
        payload["id"] = int(variant.sh_shopify_variant_id)
    return payload


def _product_payload(item, variants: list, settings) -> dict:
    """Shared by templates (variants = real children) and simple items
    (variants = [item] itself, standing in as its own only variant)."""
    option_names = []
    for v in variants:
        for a in (v.attributes or []):
            if a.attribute not in option_names:
                option_names.append(a.attribute)
    if not option_names:
        option_names = ["Title"]

    payload = {
        "title": item.item_name,
        "options": [{"name": name} for name in option_names],
        "variants": [_variant_payload(v, settings, option_names) for v in variants],
    }
    if settings.sh_push_description:
        payload["body_html"] = item.description or ""
    if settings.sh_push_vendor and item.brand:
        payload["vendor"] = item.brand
    if settings.sh_push_product_type and item.item_group:
        payload["product_type"] = item.item_group
    if settings.sh_push_images:
        images = _item_images(item, settings)
        if images:
            payload["images"] = [{"src": url} for url in images]
    return payload


# ── Push entry point ─────────────────────────────────────────────────────────

def push_item(item_code: str):
    item = frappe.get_doc("Item", item_code)
    if not _sync_enabled(item):
        return

    if item.variant_of:
        _push_product(frappe.get_doc("Item", item.variant_of))
    else:
        _push_product(item)


def _push_product(item):
    """item is either a template (has_variants=1, pushes its real children)
    or a simple item (pushes itself as its own single variant)."""
    settings = frappe.get_single("Shopify Connector Settings")

    if item.has_variants:
        variant_names = frappe.get_all("Item", filters={"variant_of": item.name}, pluck="name")
        variants = [frappe.get_doc("Item", v) for v in variant_names]
    else:
        variants = [item]

    canonical = _product_canonical(item, variants, settings)
    fp = fingerprint.fingerprint(canonical)

    entity = entities.get_by_erpnext("product", "Item", item.name)
    if entity and entity.erpnext_fingerprint == fp:
        return  # unchanged since our own last push -- avoid spamming the API

    client = ShopifyClient()
    payload = _product_payload(item, variants, settings)

    if item.get("sh_shopify_product_id"):
        resp = client.put(f"products/{item.sh_shopify_product_id}.json", {"product": payload})
    else:
        resp = client.post("products.json", {"product": payload})

    product = resp.get("product", {})
    product_id = str(product.get("id", ""))
    if not product_id:
        return

    if item.sh_shopify_product_id != product_id:
        frappe.db.set_value("Item", item.name, "sh_shopify_product_id", product_id)

    returned_variants = product.get("variants", [])
    for variant, returned in zip(variants, returned_variants):
        variant_id = str(returned.get("id", ""))
        if variant_id and variant.get("sh_shopify_variant_id") != variant_id:
            frappe.db.set_value("Item", variant.name, "sh_shopify_variant_id", variant_id)

    entities.save(
        entity or entities.get_or_new("product", "Item", item.name, product_id),
        external_id=product_id,
        erpnext_doctype="Item",
        erpnext_name=item.name,
        erpnext_fingerprint=fp,
    )
