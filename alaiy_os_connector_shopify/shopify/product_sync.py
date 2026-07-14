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

from zoneinfo import ZoneInfo

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
from alaiy_os_connector_shopify.shopify.sync_engine import fingerprint
from alaiy_os_connector_shopify.shopify.sync_engine import entities

LOCK_TIMEOUT_SECONDS = 30


def _to_utc_naive(dt):
    """
    Normalize a datetime to naive UTC so two datetimes from different
    sources can be compared safely. Shopify's updated_at parses to a
    timezone-AWARE datetime (it carries a UTC offset); Frappe's own
    Datetime fields (e.g. Shopify Synced Entity.last_synced_at) are
    always naive, implicitly in the site's system timezone. Comparing
    aware to naive directly raises TypeError.
    """
    if dt.tzinfo is not None:
        return dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    system_tz = ZoneInfo(frappe.utils.get_system_timezone())
    return dt.replace(tzinfo=system_tz).astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

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
    if doc.flags.from_shopify_sync:
        # This save originated from an inbound webhook update (see
        # _update_item_from_shopify) -- pushing it back to Shopify would
        # create an infinite create/update ping-pong between the two sides.
        return

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


def on_item_delete(doc, method=None):
    """
    Deleting a variant in ERPNext should remove it from Shopify too,
    rather than silently diverging. push_item always rebuilds the FULL
    variant list from the template's current children before calling
    productSet, which Shopify treats as the complete desired state -- so
    simply re-pushing the template right after this variant is gone
    naturally drops it from Shopify as well, with no separate delete
    mutation needed.

    Scoped to variant deletions only. Deleting the template itself (the
    whole product) is a bigger, more destructive call -- not handled
    here.
    """
    if not doc.variant_of:
        return
    if not doc.get("sh_shopify_variant_id"):
        return  # Never synced to Shopify -- nothing to remove there
    template_name = doc.variant_of
    if not frappe.db.get_value("Item", template_name, "sync_to_shopify"):
        return  # Outbound push disabled for this product -- leave Shopify alone

    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product_sync.push_item",
        queue="short",
        timeout=120,
        item_code=template_name,
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


# ── Bidirectional Sync: Only push CHANGED items ──────────────────────────────

def push_changed_items_only(item_code: str = None):
    """
    Push only items that have CHANGED since last sync (fingerprint detection).
    Prevents unnecessary API calls when item hasn't actually changed.

    Called by:
      - on_item_change() doc_event (single item)
      - Scheduled job every hour (all items)
    """
    if item_code:
        # Single item from doc_event
        item = frappe.get_doc("Item", item_code)
        if not _sync_enabled(item):
            return
        template_name = item.variant_of or item.name
        item = frappe.get_doc("Item", template_name)
        if _has_changed_since_last_sync(item):
            push_item(item_code)
        else:
            frappe.logger().debug(f"Item {item_code} unchanged, skipping push")
    else:
        # Hourly reconciliation - all items that have "sync_to_shopify" checked
        pushed = 0
        unchanged = 0
        sync_items = frappe.get_all(
            "Item",
            filters={"sync_to_shopify": 1, "variant_of": ""},
            pluck="name"
        )
        for code in sync_items:
            item = frappe.get_doc("Item", code)
            try:
                if _has_changed_since_last_sync(item):
                    push_item(code)
                    pushed += 1
                else:
                    unchanged += 1
            except Exception as exc:
                frappe.log_error(
                    title=f"Shopify: sync push failed for {code}",
                    message=str(exc)
                )
        frappe.logger().info(f"Sync push: {pushed} changed, {unchanged} unchanged")


def _has_changed_since_last_sync(item) -> bool:
    """
    Check if Item has changed since last push via fingerprint comparison.

    Returns True if:
      - Item has no Synced Entity (never pushed)
      - Item fingerprint differs from stored fingerprint (actually changed)
      - Item was just created
    """
    entity = entities.get_by_erpnext("product", "Item", item.name)

    if not entity:
        return True  # Never pushed - consider changed

    if item.has_variants:
        variant_names = frappe.get_all(
            "Item", filters={"variant_of": item.name}, pluck="name")
        variants = [frappe.get_doc("Item", v) for v in variant_names]
    else:
        variants = [item]

    settings = frappe.get_single("Shopify Connector Settings")
    canonical = _product_canonical(item, variants, settings)
    current_fp = fingerprint.fingerprint(canonical)

    if not entity.erpnext_fingerprint:
        return True  # No stored fingerprint - consider changed

    return entity.erpnext_fingerprint != current_fp


# ── Inbound Sync: Handle Shopify product changes via webhooks ─────────────────

def handle_product_webhook(topic: str, payload: dict):
    """
    Handle product events from Shopify webhooks.
    Topics: products/create, products/update, products/delete

    Only updates if Shopify version is newer (timestamp-based conflict resolution).
    Shopify timestamp wins on conflicts (inbound takes precedence).
    """
    if not payload:
        return

    # Shopify's REST webhook body IS the resource itself (no wrapper key) --
    # unlike our own GraphQL responses, which nest a product under a field
    # name. payload.get("product") would always be None and silently no-op.
    product = payload
    product_id = str(product.get("id", ""))

    if not product_id:
        frappe.logger().warning("Product webhook: no product ID")
        return

    try:
        if topic == "products/delete":
            _handle_product_delete(product_id, product)
        elif topic == "products/create":
            _handle_product_create(product_id, product)
        elif topic == "products/update":
            _handle_product_update(product_id, product)
    except Exception as exc:
        frappe.log_error(
            title=f"Shopify: product webhook {topic} failed",
            message=f"Product ID: {product_id}\nError: {str(exc)}"
        )


def _webhook_product_to_graphql_node(product: dict) -> dict:
    """
    Adapt a REST-shaped webhook product payload (id, body_html, product_type,
    variants: [...], images: [...]) into the GraphQL node shape that
    product_import._import_product() expects (legacyResourceId, bodyHtml,
    productType, variants.nodes, images.nodes) -- so webhook-triggered
    creates reuse the same, already-tested import logic instead of a second
    parallel implementation.

    Also carries option data across: REST gives the product's option names
    positionally (options: [{name, position}, ...]) and each variant only
    the values (option1/option2/option3, same position order) -- these are
    remapped into the same options/selectedOptions shape the GraphQL import
    query uses, so a webhook-created product ends up with the same Size/
    Color attributes a one-time import would give it, instead of silently
    falling back to a synthetic "Title" attribute.
    """
    variants = product.get("variants") or []
    images = product.get("images") or []
    options = product.get("options") or []
    # Shopify positions are 1-indexed; option1/2/3 map to position 1/2/3.
    option_names_by_position = {
        opt.get("position"): opt.get("name") for opt in options if opt.get("name")
    }

    def _variant_selected_options(v: dict) -> list:
        selected = []
        for position in (1, 2, 3):
            name = option_names_by_position.get(position)
            value = v.get(f"option{position}")
            if name and value:
                selected.append({"name": name, "value": value})
        return selected

    return {
        "legacyResourceId": str(product.get("id", "")),
        "title": product.get("title", ""),
        "bodyHtml": product.get("body_html", ""),
        "vendor": product.get("vendor", ""),
        "productType": product.get("product_type", ""),
        "options": [{"name": opt.get("name")} for opt in options if opt.get("name")],
        "images": {
            "nodes": [{"src": img.get("src")} for img in images if img.get("src")]
        },
        "variants": {
            "nodes": [
                {
                    "legacyResourceId": str(v.get("id", "")),
                    "sku": v.get("sku"),
                    "title": v.get("title"),
                    "price": v.get("price"),
                    "selectedOptions": _variant_selected_options(v),
                    # Reshaped to match the GraphQL inventoryItem.inventoryLevels
                    # shape product_import._variant_available_qty() reads, so a
                    # webhook-created product gets its opening stock set the
                    # same way a one-time import does.
                    "inventoryItem": {
                        "inventoryLevels": {
                            "nodes": [
                                {"quantities": [{"quantity": v.get("inventory_quantity")}]}
                            ]
                        } if v.get("inventory_quantity") is not None else {"nodes": []}
                    },
                }
                for v in variants
            ]
        },
    }


def _handle_product_create(product_id: str, product: dict):
    """New product on Shopify - create ERPNext Item."""
    entity = entities.get_by_external_id("product", product_id)

    if entity:
        # Already linked - treat as update
        return _handle_product_update(product_id, product)

    # New product - import it (reuses the one-time-import logic, translated
    # from the webhook's REST shape into the GraphQL node shape it expects).
    from alaiy_os_connector_shopify.shopify.product_import import _import_product
    node = _webhook_product_to_graphql_node(product)
    _import_product(node)
    frappe.logger().info(f"Created Item from Shopify product {product_id}")


def _handle_product_update(product_id: str, product: dict):
    """Product updated on Shopify - update ERPNext Item if Shopify is newer."""
    entity = entities.get_by_external_id("product", product_id)

    if not entity:
        return  # Product not linked to ERPNext

    item = frappe.get_doc("Item", entity.erpnext_name)

    # Get Shopify product timestamp
    shopify_updated = product.get("updated_at")
    if not shopify_updated:
        return

    # Shopify wins if newer than our last sync. Both sides must be
    # normalized to the same UTC-naive form before comparing -- Shopify's
    # timestamp string carries a UTC offset (parses to a timezone-AWARE
    # datetime) while entity.last_synced_at is a naive ERPNext-local
    # datetime; comparing aware to naive directly raises TypeError, which
    # was silently swallowed by this function's own caller and made every
    # single real webhook update fail with no visible symptom beyond
    # "the update just didn't happen."
    last_synced = entity.last_synced_at
    if last_synced and _to_utc_naive(frappe.utils.get_datetime(shopify_updated)) < _to_utc_naive(frappe.utils.get_datetime(last_synced)):
        frappe.logger().debug(
            f"Product {product_id} older than local, skipping update"
        )
        return

    _update_item_from_shopify(item, product)

    # Recompute and store the fingerprint for the post-update state so the
    # hourly outbound reconciliation (push_changed_items_only) doesn't see
    # this inbound-driven change as "different from last push" and push it
    # straight back to Shopify.
    item = frappe.get_doc("Item", item.name)
    settings = frappe.get_single("Shopify Connector Settings")
    if item.has_variants:
        variant_names = frappe.get_all("Item", filters={"variant_of": item.name}, pluck="name")
        variants = [frappe.get_doc("Item", v) for v in variant_names]
    else:
        variants = [item]
    canonical = _product_canonical(item, variants, settings)
    entities.save(entity, erpnext_fingerprint=fingerprint.fingerprint(canonical))

    frappe.logger().info(f"Updated Item {item.name} from Shopify product {product_id}")


def _update_item_from_shopify(item, product: dict):
    """
    Update ERPNext Item from Shopify product (inbound sync).

    Fields updated: title, description, vendor, product_type, status, images

    Fields NOT updated: pricing (separate inventory_sync), stock levels (separate feature), variant structure
    """
    settings = frappe.get_single("Shopify Connector Settings")

    # Basic fields
    if product.get("title"):
        item.item_name = product["title"]
    if product.get("body_html"):
        item.description = product["body_html"]
    if product.get("vendor"):
        item.brand = product["vendor"]
    if product.get("product_type"):
        item.item_group = product["product_type"]

    # Status: active/draft/archived
    if product.get("status"):
        item.disabled = 1 if product["status"] in ("archived", "draft") else 0

    # Save item
    item.flags.from_shopify_sync = True
    item.flags.ignore_permissions = True
    item.save()
    frappe.db.commit()

    # Update images
    if settings.sh_push_images:
        images = [img.get("src") for img in (product.get("images") or []) if img.get("src")]
        if images:
            from alaiy_os_connector_shopify.shopify.product_import import (
                _set_item_image, _set_item_slideshow
            )
            _set_item_image(item.name, images[0])
            if len(images) > 1:
                _set_item_slideshow(item.name, images, settings)

    # Log variant inventory data (for inventory_sync to use later)
    variants = product.get("variants") or []
    if variants:
        frappe.logger().debug(
            f"Product {item.name}: {len(variants)} variants with inventory_quantity, "
            f"compare_at_price, and inventory_policy data available for inventory_sync"
        )


def _handle_product_delete(product_id: str, product: dict):
    """Product deleted on Shopify - unlink ERPNext Item (preserve local data)."""
    entity = entities.get_by_external_id("product", product_id)

    if not entity:
        return

    item = frappe.get_doc("Item", entity.erpnext_name)

    # Unlink: remove Shopify IDs but keep Item in ERPNext
    frappe.db.set_value("Item", item.name, "sh_shopify_product_id", None)
    frappe.db.set_value("Item", item.name, "sync_to_shopify", 0)

    # A template's variants each carry their own copy of sh_shopify_product_id
    # (set at import time) -- leaving those in place after the template
    # itself is unlinked means _wipe_unlinked_products() (which only deletes
    # Items with NO Shopify id) would never clean them up, and a SKU Shopify
    # later reuses for a genuinely new product would collide with this dead
    # variant on the next import.
    if item.has_variants:
        variant_names = frappe.get_all("Item", filters={"variant_of": item.name}, pluck="name")
        for variant_name in variant_names:
            frappe.db.set_value("Item", variant_name, "sh_shopify_product_id", None)
            frappe.db.set_value("Item", variant_name, "sh_shopify_variant_id", None)

    entity.external_id = None
    entity.save(ignore_permissions=True)
    frappe.db.commit()

    frappe.logger().info(f"Unlinked Item {item.name} (product {product_id} deleted)")


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
