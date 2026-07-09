"""
ERPNext -> Shopify product/variant push (Phase 2).

Gated by Item.sync_to_shopify (opt-in) -- variants inherit their template's
flag. Unlike the reference connector, an already-linked item does NOT keep
syncing forever regardless of the flag: unchecking it archives the product
on Shopify (kept, hidden from sales channels, order history intact), and
re-checking it unarchives + pushes again.

Always operates at the template level: even when only one variant changed,
the whole current variant set is rebuilt and PUT to Shopify, since each
variant payload carries its own Shopify variant `id` when it has one --
Shopify updates existing variants and creates new ones from the same call.

Every push acquires a document lock on the template first. ERPNext's own
Item controller resaves every sibling variant whenever a template is saved
(unless the caller sets dont_update_variants, which our own doc_events
can't control since the trigger is the user's/Cloudstore's save, not ours) --
so a single checkbox click can fire up to 1 + (variant count) on_update
events in quick succession, each independently enqueuing a push for the
SAME template. Without the lock, several of those race to see "no Shopify
product ID yet" before any of them writes one back, and each creates its
own duplicate product.
"""

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.client import ShopifyClient
from alaiy_os_connector_shopify.shopify.sync_engine import fingerprint
from alaiy_os_connector_shopify.shopify.sync_engine import entities

LOCK_TIMEOUT_SECONDS = 30


# ── Doc event entry points ──────────────────────────────────────────────────
# Never call Shopify inline inside a save transaction -- enqueue and return.

def on_item_change(doc, method=None):
    enabled = _sync_enabled(doc)
    template_name = doc.variant_of or doc.name
    has_shopify_id = bool(
        frappe.db.get_value("Item", template_name, "sh_shopify_product_id")
    )

    if enabled:
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.push_item",
            queue="short",
            timeout=120,
            item_code=doc.name,
        )
    elif has_shopify_id and not doc.variant_of:
        # Flag just turned off on the template itself (variants don't carry
        # their own archive state -- only the template/product does).
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.archive_item",
            queue="short",
            timeout=60,
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
        "alaiy_os_connector_shopify.shopify.product_sync.push_item",
        queue="short",
        timeout=120,
        item_code=doc.item_code,
    )


# ── Sync-enable gate ─────────────────────────────────────────────────────────

def _sync_enabled(item) -> bool:
    """
    Whether this item's checkbox (or its template's, for a variant) is
    currently ON. Deliberately does NOT stay true forever just because it
    already has a Shopify ID -- unchecking is meant to archive it, not be
    ignored. See on_item_change for what happens when this is False but the
    item was previously linked.
    """
    if item.get("variant_of"):
        return bool(frappe.db.get_value("Item", item.variant_of, "sync_to_shopify"))
    return bool(item.get("sync_to_shopify"))


# ── Canonical form + fingerprint ─────────────────────────────────────────────

def _variant_price(item_code: str, settings) -> float:
    price_list = settings.sh_selling_price_list or "Standard Selling"
    rate = frappe.db.get_value(
        "Item Price", {"item_code": item_code,
                       "price_list": price_list}, "price_list_rate"
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
    canonical = {"title": item.item_name, "variants": [
        _variant_canonical(v, settings) for v in variants]}
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
    attrs = {a.attribute: a.attribute_value for a in (
        variant.attributes or [])}
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
        # Pushing implies "this should be live" -- unarchives on every push
        # rather than needing a separate un-archive step when re-enabled.
        "status": "active",
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
    try:
        item.lock(timeout=LOCK_TIMEOUT_SECONDS)
    except frappe.DocumentLockedError:
        # Another push for this same template is already in flight (or just
        # finished writing back its Shopify ID) -- let it own this update.
        return

    try:
        _push_product_unlocked(item)
    finally:
        item.unlock()


def _push_product_unlocked(item):
    # Re-fetch: another push may have just written a product_id while we
    # were waiting for the lock, and we must build the payload from that,
    # not from what `item` looked like before we acquired it.
    item = frappe.get_doc("Item", item.name)
    settings = frappe.get_single("Shopify Connector Settings")

    if item.has_variants:
        variant_names = frappe.get_all(
            "Item", filters={"variant_of": item.name}, pluck="name")
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
        resp = client.put(
            f"products/{item.sh_shopify_product_id}.json", {"product": payload})
    else:
        resp = client.post("products.json", {"product": payload})

    product = resp.get("product", {})
    product_id = str(product.get("id", ""))
    if not product_id:
        return

    if item.sh_shopify_product_id != product_id:
        frappe.db.set_value("Item", item.name,
                            "sh_shopify_product_id", product_id)

    returned_variants = product.get("variants", [])
    for variant, returned in zip(variants, returned_variants):
        variant_id = str(returned.get("id", ""))
        if variant_id and variant.get("sh_shopify_variant_id") != variant_id:
            frappe.db.set_value("Item", variant.name,
                                "sh_shopify_variant_id", variant_id)

    entities.save(
        entity or entities.get_or_new(
            "product", "Item", item.name, product_id),
        external_id=product_id,
        erpnext_doctype="Item",
        erpnext_name=item.name,
        erpnext_fingerprint=fp,
    )
    frappe.db.commit()


# ── Archive (disable) ────────────────────────────────────────────────────────

def archive_item(item_code: str):
    """Called when sync_to_shopify is unchecked on an item that's already
    linked -- archives the Shopify product (hidden from sales channels,
    order history intact) rather than deleting it or silently ignoring the
    checkbox."""
    item = frappe.get_doc("Item", item_code)
    if item.variant_of or not item.get("sh_shopify_product_id"):
        return
    if item.get("sync_to_shopify"):
        return  # re-checked before this job ran -- don't archive what should stay active

    try:
        item.lock(timeout=LOCK_TIMEOUT_SECONDS)
    except frappe.DocumentLockedError:
        return

    try:
        client = ShopifyClient()
        client.put(f"products/{item.sh_shopify_product_id}.json",
                   {"product": {"status": "archived"}})
    finally:
        item.unlock()
