"""
ERPNext -> Shopify product/variant push (Phase 2).

Gated by Item.sync_to_shopify (opt-in) -- variants inherit their template's
flag. Unlike the reference connector, an already-linked item does NOT keep
syncing forever regardless of the flag: unchecking it archives the product
on Shopify (kept, hidden from sales channels, order history intact), and
re-checking it unarchives + pushes again.

Always operates at the template level: even when only one variant changed,
the whole current variant set is rebuilt and sent to Shopify via productSet,
since each variant payload carries its own Shopify variant `id` when it has
one -- Shopify updates existing variants and creates new ones from the same
call.

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

from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
from alaiy_os_connector_shopify.shopify.sync_engine import fingerprint
from alaiy_os_connector_shopify.shopify.sync_engine import entities

LOCK_TIMEOUT_SECONDS = 30

_PRODUCT_SET_MUTATION = """
mutation PushProduct($input: ProductSetInput!, $identifier: ProductSetIdentifiers, $synchronous: Boolean!) {
  productSet(input: $input, identifier: $identifier, synchronous: $synchronous) {
    product {
      id
      legacyResourceId
      variants(first: 100) {
        nodes {
          id
          legacyResourceId
          sku
        }
      }
    }
    userErrors {
      field
      message
    }
  }
}
"""


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


# ── Shopify payload builders (productSet input shape) ───────────────────────

def _variant_set_payload(variant, settings, option_names: list) -> dict:
    attrs = {a.attribute: a.attribute_value for a in (variant.attributes or [])}
    payload = {
        "sku": variant.item_code,
        "price": f"{_variant_price(variant.item_code, settings):.2f}",
        "optionValues": [
            {"optionName": name, "name": attrs.get(name) or "Default"}
            for name in option_names
        ],
    }
    if variant.get("sh_shopify_variant_id"):
        payload["id"] = f"gid://shopify/ProductVariant/{variant.sh_shopify_variant_id}"
    return payload


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


def _product_set_input(item, variants: list, settings) -> dict:
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
        # Pushing implies "this should be live" -- unarchives on every push
        # rather than needing a separate un-archive step when re-enabled.
        # archive_item() overrides this back to ARCHIVED explicitly.
        "status": "ACTIVE",
        "productOptions": _product_options_payload(option_names, variants),
        "variants": [
            _variant_set_payload(v, settings, option_names) for v in variants
        ],
    }
    if settings.sh_push_description:
        payload["descriptionHtml"] = item.description or ""
    if settings.sh_push_vendor and item.brand:
        payload["vendor"] = item.brand
    if settings.sh_push_product_type and item.item_group:
        payload["productType"] = item.item_group
    if settings.sh_push_images:
        images = _item_images(item, settings)
        if images:
            payload["files"] = [
                {"originalSource": url, "contentType": "IMAGE"} for url in images
            ]
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

    client = ShopifyGraphQLClient()
    product_input = _product_set_input(item, variants, settings)

    identifier = None
    if item.get("sh_shopify_product_id"):
        identifier = {
            "id": f"gid://shopify/Product/{item.sh_shopify_product_id}"}

    data = client.execute(_PRODUCT_SET_MUTATION, {
        "input": product_input,
        "identifier": identifier,
        # Product/variant counts here are small (single to low tens) --
        # synchronous keeps write-back a single round trip. Revisit if a
        # template's variant count ever grows enough to risk timeouts.
        "synchronous": True,
    })
    result = data.get("productSet") or {}
    errors = result.get("userErrors") or []
    if errors:
        raise RuntimeError(f"Shopify productSet userErrors: {errors}")

    product = result.get("product") or {}
    product_id = product.get("legacyResourceId")
    if not product_id:
        return

    if item.sh_shopify_product_id != product_id:
        frappe.db.set_value("Item", item.name,
                            "sh_shopify_product_id", product_id)

    # Match by SKU, not response order -- productSet's variants connection
    # isn't documented to preserve submission order, and getting this wrong
    # would silently write one variant's Shopify ID onto a different
    # ERPNext item.
    returned_by_sku = {
        v.get("sku"): v.get("legacyResourceId")
        for v in (product.get("variants") or {}).get("nodes", [])
        if v.get("sku")
    }
    for variant in variants:
        variant_id = returned_by_sku.get(variant.item_code)
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
    checkbox. Resends the full product_set_input (not just {status}) since
    it's unconfirmed whether productSet treats a missing field as "leave
    alone" or "clear" -- sending the complete state is correct either way."""
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
        item = frappe.get_doc("Item", item.name)
        settings = frappe.get_single("Shopify Connector Settings")

        if item.has_variants:
            variant_names = frappe.get_all(
                "Item", filters={"variant_of": item.name}, pluck="name")
            variants = [frappe.get_doc("Item", v) for v in variant_names]
        else:
            variants = [item]

        product_input = _product_set_input(item, variants, settings)
        product_input["status"] = "ARCHIVED"

        client = ShopifyGraphQLClient()
        data = client.execute(_PRODUCT_SET_MUTATION, {
            "input": product_input,
            "identifier": {"id": f"gid://shopify/Product/{item.sh_shopify_product_id}"},
            "synchronous": True,
        })
        errors = (data.get("productSet") or {}).get("userErrors") or []
        if errors:
            frappe.log_error(
                title=f"Shopify: archive failed for {item.name}",
                message=str(errors),
            )
    finally:
        item.unlock()
