"""
Inbound Sync: Handle Shopify product changes via webhooks -- moved
verbatim from product_sync.py, unchanged.
"""

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.sync_engine import fingerprint
from alaiy_os_connector_shopify.shopify.sync_engine import entities

from alaiy_os_connector_shopify.shopify.product.canonical import _product_canonical
from alaiy_os_connector_shopify.shopify.product.export import _variants_of
from alaiy_os_connector_shopify.shopify.product.utils import _to_utc_naive


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
    except Exception:
        # str(exc) alone was landing blank for some exception types,
        # losing all diagnostic info -- full traceback always has
        # something to go on.
        frappe.log_error(
            title=f"Shopify: product webhook {topic} failed",
            message=f"Product ID: {product_id}\n{frappe.get_traceback()}"
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

    # Shopify's REST tags field is already a single comma-separated string
    # (unlike GraphQL's [String!]! list) -- pass it through as a one-item
    # list; _normalize_tags splits it back into individual tags the same
    # way it splits GraphQL's list, keeping one code path for both.
    tags_raw = product.get("tags")
    category = product.get("category") or {}

    return {
        "legacyResourceId": str(product.get("id", "")),
        "title": product.get("title", ""),
        "bodyHtml": product.get("body_html", ""),
        "vendor": product.get("vendor", ""),
        "productType": product.get("product_type", ""),
        "status": product.get("status", ""),
        "tags": [tags_raw] if tags_raw else [],
        "category": {"name": category.get("name") or category.get("full_name")} if category.get("name") or category.get("full_name") else None,
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
                    "compareAtPrice": v.get("compare_at_price"),
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
    """New product on Shopify - create Alaiy OS Item."""
    entity = entities.get_by_external_id("product", product_id)

    if entity:
        # Already linked - treat as update
        return _handle_product_update(product_id, product)

    # New product - import it (reuses the one-time-import logic, translated
    # from the webhook's REST shape into the GraphQL node shape it expects).
    from alaiy_os_connector_shopify.shopify.product.importer import _import_product
    node = _webhook_product_to_graphql_node(product)
    _import_product(node)
    frappe.logger().info(f"Created Item from Shopify product {product_id}")


def _handle_product_update(product_id: str, product: dict):
    """Product updated on Shopify - update Alaiy OS Item if Shopify is newer."""
    entity = entities.get_by_external_id("product", product_id)

    if not entity:
        return  # Product not linked to Alaiy OS

    if not frappe.db.exists("Item", entity.erpnext_name):
        # Self-heal: the item was deleted locally. Delete the stale synced entity
        # so it can be recreated/re-imported cleanly.
        frappe.delete_doc("Shopify Synced Entity", entity.name, ignore_permissions=True)
        frappe.db.commit()
        return

    item = frappe.get_doc("Item", entity.erpnext_name)

    # Get Shopify product timestamp
    shopify_updated = product.get("updated_at")
    if not shopify_updated:
        return

    # Shopify wins if newer than our last sync. Both sides must be
    # normalized to the same UTC-naive form before comparing -- Shopify's
    # timestamp string carries a UTC offset (parses to a timezone-AWARE
    # datetime) while entity.last_synced_at is a naive Alaiy OS-local
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
    from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver
    listing = listing_resolver.get_listing(item.name)
    # Only re-fingerprint when a Listing exists (i.e. this product is
    # outbound-managed) -- the canonical must match what an outbound push
    # would build, which now reads the Listing. No Listing => outbound never
    # pushes this product anyway, so there's nothing to guard against.
    if listing:
        variants = _variants_of(item)
        canonical = _product_canonical(item, variants, settings, listing)
        entities.save(entity, erpnext_fingerprint=fingerprint.fingerprint(canonical))

    frappe.logger().info(f"Updated Item {item.name} from Shopify product {product_id}")


def _update_item_from_shopify(item, product: dict):
    """
    Update Alaiy OS Item from Shopify product (inbound sync).

    Fields updated: title, description, vendor, product_type, status, images,
    tags, category (read-only, see _apply_product_meta), variant price,
    compare-at price, weight

    Fields NOT updated live via webhook (import/pull only): SEO title/
    description, unit cost, country of origin, harmonized system code --
    Shopify's REST webhook payload doesn't carry these the same way the
    GraphQL-based one-time import/pull does. Also NOT updated: stock
    levels (separate feature), variant structure (add/remove variants).
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
        # sh_shopify_product_type, not item_group -- Item Group is a real
        # Link field with its own master data and validation, and mixing
        # it with Shopify's free-text product_type meant an inbound update
        # could fail validation outright if the exact string didn't already
        # exist as an Item Group. The dedicated field also keeps Item Group
        # reorganizable locally without it ever touching Shopify or vice
        # versa (see the field's own description).
        item.sh_shopify_product_type = product["product_type"]

    from alaiy_os_connector_shopify.shopify.product.importer import _apply_product_meta
    tags = product.get("tags")
    category = product.get("category") or {}
    _apply_product_meta(item, {
        "tags": [tags] if tags else [],
        "category": {"name": category.get("name") or category.get("full_name")} if category.get("name") or category.get("full_name") else None,
        "status": product.get("status") or "",
    })

    # Status: active/draft/archived. Draft is a real visibility state now (kept
    # on sh_shopify_status by _apply_product_meta), NOT a disable -- only an
    # ARCHIVED product disables the Item.
    if product.get("status") == "archived":
        item.disabled = 1
    elif product.get("status") in ("active", "draft"):
        item.disabled = 0

    from alaiy_os_connector_shopify.shopify.product.masters import _dedupe_item_uoms
    _dedupe_item_uoms(item)

    # Save item. item.flags.ignore_permissions only covers this save --
    # Alaiy OS's Item.on_update() cascades into update_variants(), which
    # fetches fresh sibling variant Item docs and calls variant.save() on
    # each of THOSE, none of which inherit our flag. This webhook runs as
    # Guest (allow_guest=True endpoint), so that cascaded save hits a real
    # frappe.PermissionError -- confirmed live. Same fix order_sync.py
    # already uses for its own Guest-context saves: elevate for the call.
    item.flags.from_shopify_sync = True
    item.flags.ignore_permissions = True
    from alaiy_os_connector_shopify.shopify.order_sync import _as_administrator
    with _as_administrator():
        item.save()
    frappe.db.commit()

    # Update images
    images = [img.get("src") for img in (product.get("images") or []) if img.get("src")]
    if images:
        from alaiy_os_connector_shopify.shopify.product.media import (
            _set_item_image, _set_item_slideshow
        )
        _set_item_image(item.name, images[0])
        if len(images) > 1:
            _set_item_slideshow(item.name, images, settings)

    # Disable Listing Variant rows for variants no longer present on Shopify,
    # and clear their stale Item-level ids. The Listing's rows are the
    # outbound include set now (not Item.sync_to_shopify), so this is what
    # actually drops them from future pushes.
    if item.has_variants and "variants" in product:
        incoming_skus = {
            (v.get("sku") or "").strip()
            for v in (product.get("variants") or [])
            if (v.get("sku") or "").strip()
        }
        from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver
        listing = listing_resolver.get_listing(item.name)
        changed = False
        for row in (listing.variants if listing else []):
            if row.is_enabled and row.item_variant not in incoming_skus:
                row.is_enabled = 0
                frappe.db.set_value("Item", row.item_variant, "sh_shopify_variant_id", None)
                frappe.db.set_value("Item", row.item_variant, "sh_shopify_product_id", None)
                changed = True
        if changed:
            listing.flags.from_shopify_sync = True  # inbound reconcile, don't echo a push
            listing.save(ignore_permissions=True)

    # Update price + compare-at price per variant. Was previously never
    # touched on inbound update at all (see this function's old docstring) --
    # the webhook payload already carries both per variant, same as a
    # one-time import, so there's no reason a price edit made on Shopify
    # shouldn't flow back the same way title/description/tags do.
    from alaiy_os_connector_shopify.shopify.product.pricing import (
        _set_item_price, _set_item_compare_at_price,
    )
    from alaiy_os_connector_shopify.shopify.product.masters import _ensure_uom
    from alaiy_os_connector_shopify.shopify.product.variants import _REST_WEIGHT_UNIT_TO_UOM
    for variant in (product.get("variants") or []):
        sku = (variant.get("sku") or "").strip()
        if not sku or not frappe.db.exists("Item", sku):
            continue
        price = flt(variant.get("price") or 0)
        if price > 0:
            _set_item_price(sku, price, settings)
        compare_at_price = flt(variant.get("compare_at_price") or variant.get("compareAtPrice") or 0)
        if compare_at_price > 0:
            _set_item_compare_at_price(sku, compare_at_price, settings)

        # Weight: REST payload's flat weight/weight_unit -- cost, country
        # of origin, and HS code aren't reliably present here, so those
        # stay import-only (see this function's docstring).
        weight_value = flt(variant.get("weight") or 0)
        weight_unit = _REST_WEIGHT_UNIT_TO_UOM.get((variant.get("weight_unit") or "").lower())
        if weight_value > 0 and weight_unit:
            frappe.db.set_value("Item", sku, {
                "weight_per_unit": weight_value,
                "weight_uom": _ensure_uom(weight_unit),
            })

    # Log variant inventory data (for inventory_sync to use later)
    variants = product.get("variants") or []
    if variants:
        frappe.logger().debug(
            f"Product {item.name}: {len(variants)} variants with inventory_quantity, "
            f"compare_at_price, and inventory_policy data available for inventory_sync"
        )


def _handle_product_delete(product_id: str, product: dict):
    """Product deleted on Shopify - unlink Alaiy OS Item (preserve local data)."""
    entity = entities.get_by_external_id("product", product_id)

    if not entity:
        return

    if frappe.db.exists("Item", entity.erpnext_name):
        item = frappe.get_doc("Item", entity.erpnext_name)

        # Unlink: remove Shopify IDs but keep Item in Alaiy OS
        frappe.db.set_value("Item", item.name, "sh_shopify_product_id", None)

        # Disable the Listing too, or the hourly outbound reconciliation would
        # re-push (and recreate on Shopify) a product just deleted there. The
        # id itself lives on the Item (cleared above); the Listing's id field
        # is a fetch_from view, so only is_enabled needs writing here.
        if frappe.db.exists("Shopify Product Listing", item.name):
            frappe.db.set_value("Shopify Product Listing", item.name, "is_enabled", 0)

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

    frappe.logger().info(f"Unlinked Item {entity.erpnext_name} (product {product_id} deleted)")
