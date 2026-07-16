"""
ERPNext -> Shopify product/variant push (Phase 2).

Gated by Item.sync_to_shopify (opt-in). The TEMPLATE's checkbox is the
master switch for the whole product (checking it auto-checks all variants;
unchecking or disabling the Item archives the product on Shopify -- kept,
hidden from sales channels, order history intact -- and re-checking
unarchives + pushes again). Each VARIANT's own checkbox is a per-variant
include flag: unchecking one drops just that variant from the next
productSet push, which removes it on Shopify; new variants added under a
syncing template are auto-checked on insert.

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

from alaiy_os_connector_shopify.shopify.sync_guard import append_log as _append_export_log

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

    template_name = doc.variant_of or doc.name
    template_enabled = bool(
        frappe.db.get_value("Item", template_name, "sync_to_shopify")
    ) and not frappe.db.get_value("Item", template_name, "disabled")
    has_shopify_id = bool(
        frappe.db.get_value("Item", template_name, "sh_shopify_product_id")
    )

    if doc.variant_of:
        # A brand-new variant added under an already-syncing product must
        # flow to Shopify without someone remembering to tick its own
        # checkbox -- otherwise _variants_of's filter would silently leave
        # it out of every future push (this exact regression, confirmed by
        # walking the flow: "add variant in ERPNext -> appears on Shopify"
        # worked before the per-variant filter existed).
        current_sync = doc.get("sync_to_shopify")
        frappe.logger().info(
            f"Shopify variant check: variant={doc.name}, template={template_name}, "
            f"template_enabled={template_enabled}, method={method}, current_sync={current_sync}"
        )
        if method == "after_insert" and template_enabled and not current_sync:
            doc.sync_to_shopify = 1
            frappe.db.set_value("Item", doc.name, "sync_to_shopify", 1)
            frappe.logger().info(f"Shopify auto-checked variant {doc.name}")

        # The template is the master switch: a variant's own checkbox only
        # controls whether THAT variant is included the next time the
        # template pushes (see _variants_of's own sync_to_shopify filter),
        # never whether the product as a whole is syncing. So re-push
        # whenever the template is enabled, regardless of which way this
        # variant's own flag just moved -- unchecking it here is exactly
        # what should make the rebuilt variant set drop it from Shopify.
        if template_enabled:
            frappe.enqueue(
                "alaiy_os_connector_shopify.shopify.product_sync.push_item",
                queue="short",
                timeout=120,
                item_code=template_name,
            )
        return

    # doc is the template itself
    if template_enabled:
        # The template's own checkbox just turned on (not just re-saved
        # while already on) -- auto-check every variant that isn't already
        # explicitly on, so a fresh product syncs all its variants by
        # default instead of requiring each one ticked by hand. Only
        # fires on the actual on-transition so it never re-checks a
        # variant someone deliberately unchecked afterward.
        sync_changed = doc.has_value_changed("sync_to_shopify")
        disabled_changed = doc.has_value_changed("disabled")
        frappe.logger().info(
            f"Shopify auto-check: template={doc.name}, sync_changed={sync_changed}, "
            f"disabled_changed={disabled_changed}, method={method}"
        )
        if sync_changed or disabled_changed:
            variant_names = frappe.get_all(
                "Item",
                filters={"variant_of": doc.name, "sync_to_shopify": 0},
                pluck="name",
            )
            frappe.logger().info(
                f"Shopify auto-check: found {len(variant_names)} unchecked variants to auto-check"
            )
            for variant_name in variant_names:
                frappe.db.set_value("Item", variant_name, "sync_to_shopify", 1)
            if variant_names:
                frappe.db.commit()

        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.push_item",
            queue="short",
            timeout=120,
            item_code=doc.name,
        )
    elif has_shopify_id:
        # Either sync_to_shopify turned off, or the item itself got
        # disabled -- both mean "this product should not be live on
        # Shopify anymore."
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
    Whether this product as a whole should be live on Shopify: the
    template's own sync_to_shopify checkbox AND not disabled. Deliberately
    does NOT stay true forever just because it already has a Shopify ID --
    unchecking (or disabling) is meant to archive it, not be ignored. A
    variant's own checkbox never factors in here -- it only controls
    whether that one variant is included in the rebuilt set once the
    template itself is enabled (see _variants_of, on_item_change).
    """
    if item.get("variant_of"):
        template_name = item.variant_of
        return bool(frappe.db.get_value("Item", template_name, "sync_to_shopify")) \
            and not frappe.db.get_value("Item", template_name, "disabled")
    return bool(item.get("sync_to_shopify")) and not item.get("disabled")


# ── Canonical form + fingerprint ─────────────────────────────────────────────

def _price_rate(item_code: str, price_list: str, buying: bool = False) -> float:
    filters = {"item_code": item_code, "price_list": price_list}
    if buying:
        filters["buying"] = 1
    return flt(frappe.db.get_value("Item Price", filters, "price_list_rate") or 0)


def _variant_price(item_code: str, settings) -> float:
    return _price_rate(item_code, settings.sh_selling_price_list or "Standard Selling")


def _variant_compare_at_price(item_code: str) -> float:
    from alaiy_os_connector_shopify.shopify.product_import import _COMPARE_AT_PRICE_LIST
    return _price_rate(item_code, _COMPARE_AT_PRICE_LIST)


def _variant_cost(item_code: str) -> float:
    from alaiy_os_connector_shopify.shopify.product_import import _COST_PRICE_LIST
    return _price_rate(item_code, _COST_PRICE_LIST, buying=True)


def _variant_inventory_item_payload(variant) -> dict:
    """inventoryItem sub-input for ProductVariantSetInput -- cost and
    weight live here, not flat on the variant."""
    from alaiy_os_connector_shopify.shopify.product_import import _UOM_TO_WEIGHT_UNIT
    payload = {}
    cost = _variant_cost(variant.item_code)
    if cost > 0:
        payload["cost"] = f"{cost:.2f}"
    if variant.get("weight_per_unit") and variant.get("weight_uom"):
        weight_unit = _UOM_TO_WEIGHT_UNIT.get(variant.weight_uom)
        if weight_unit:
            payload["measurement"] = {
                "weight": {"value": flt(variant.weight_per_unit), "unit": weight_unit}
            }
    return payload


def _absolute_file_url(url: str) -> str:
    """
    ERPNext's own file fields (Item.image, Website Slideshow's image rows)
    store root-relative paths like "/files/xyz.jpg" -- fine for our own
    UI, but Shopify's productSet rejected every single one live with
    "File URL is invalid" since originalSource needs a real, publicly
    reachable absolute URL, not a path relative to nothing as far as
    Shopify's servers are concerned.
    """
    if url.startswith("/"):
        return frappe.utils.get_url(url)
    return url


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
    return [_absolute_file_url(u) for u in urls]


def _variant_canonical(variant, settings) -> dict:
    return {
        "sku": variant.item_code,
        "title": variant.item_name,
        "price": _variant_price(variant.item_code, settings),
        "compare_at_price": _variant_compare_at_price(variant.item_code),
        "cost": _variant_cost(variant.item_code),
        "weight_per_unit": flt(variant.get("weight_per_unit") or 0),
        "weight_uom": variant.get("weight_uom") or "",
        "attributes": [
            {"attribute": a.attribute, "value": a.attribute_value}
            for a in (variant.attributes or [])
        ],
        "barcode": variant.barcodes[0].barcode if variant.get("barcodes") else "",
    }


def _seo_values(item) -> dict:
    """
    Shopify's own admin shows the product title/description as the SEO
    title/description whenever no explicit override is set -- mirror that
    default instead of pushing nothing when our fields are blank. The
    description default is Item.description, which is HTML (imported from
    body_html) -- an SEO meta description must be plain text, and Shopify
    caps it at 320 chars in its own admin.

    Shared by _product_set_input (what gets pushed) and _product_canonical
    (what gets fingerprinted) -- if these two ever computed defaults
    differently, every push would see a phantom "change" and re-push
    forever, or worse, never notice a real one.
    """
    title = (item.get("sh_seo_title") or item.item_name or "").strip()
    description = item.get("sh_seo_description") or frappe.utils.strip_html_tags(item.description or "")
    description = (description or "").strip()[:320]
    return {"title": title, "description": description}


def _product_canonical(item, variants, settings) -> dict:
    canonical = {"title": item.item_name, "variants": [
        _variant_canonical(v, settings) for v in variants]}
    if settings.sh_push_description:
        canonical["description"] = item.description or ""
    if settings.sh_push_vendor:
        canonical["vendor"] = item.brand or ""
    if settings.sh_push_product_type:
        canonical["product_type"] = item.get("sh_shopify_product_type") or ""
    if settings.sh_push_images:
        canonical["images"] = _item_images(item, settings)
    canonical["tags"] = item.get("sh_shopify_tags") or ""
    seo = _seo_values(item)
    canonical["seo_title"] = seo["title"]
    canonical["seo_description"] = seo["description"]
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
    if variant.get("barcodes"):
        payload["barcode"] = variant.barcodes[0].barcode
    compare_at = _variant_compare_at_price(variant.item_code)
    if compare_at > 0:
        payload["compareAtPrice"] = f"{compare_at:.2f}"
    inventory_item = _variant_inventory_item_payload(variant)
    if inventory_item:
        payload["inventoryItem"] = inventory_item
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


_TAXONOMY_SEARCH_QUERY = """
query SearchTaxonomy($search: String!) {
  taxonomy {
    categories(search: $search, first: 5) {
      edges {
        node {
          id
          name
        }
      }
    }
  }
}
"""

# Per-process cache -- the taxonomy tree doesn't change mid-run, and this
# search can otherwise fire on every single push of every item sharing the
# same category string.
_category_id_cache = {}


def _resolve_category_id(client, category_name: str):
    """
    Shopify's Category field takes a taxonomy ID, not a plain name --
    resolves our stored category name against Shopify's Standard Product
    Taxonomy search. Picks an exact case-insensitive name match if one
    comes back; otherwise the first (most relevant) search result.
    Returns None (silently, logged) if nothing matches -- an unresolvable
    category must never block the rest of the product push.
    """
    if category_name in _category_id_cache:
        return _category_id_cache[category_name]

    result = None
    try:
        data = client.execute(_TAXONOMY_SEARCH_QUERY, {"search": category_name})
        edges = ((data.get("taxonomy") or {}).get("categories") or {}).get("edges") or []
        nodes = [e["node"] for e in edges if e.get("node")]
        exact = next((n for n in nodes if n.get("name", "").lower() == category_name.lower()), None)
        chosen = exact or (nodes[0] if nodes else None)
        result = chosen.get("id") if chosen else None
    except Exception:
        frappe.log_error(
            title=f"Shopify: failed to resolve category '{category_name}'",
            message=frappe.get_traceback(),
        )

    _category_id_cache[category_name] = result
    return result


# ── Taxonomy Tree Fetch ──────────────────────────────────────────────────────

_TAXONOMY_TREE_QUERY = """
query GetTaxonomyTree {
  taxonomy {
    categories(first: 250) {
      edges {
        node {
          id
          name
          level
        }
      }
    }
  }
}
"""


def fetch_shopify_taxonomy():
    """
    Fetch the full Shopify Standard Product Taxonomy tree and populate
    the Shopify Category doctype. Called on demand or via scheduled job.
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient()
    try:
        data = client.execute(_TAXONOMY_TREE_QUERY)
    except Exception:
        frappe.log_error(
            title="Shopify: failed to fetch taxonomy tree",
            message=frappe.get_traceback(),
        )
        return

    categories = ((data.get("taxonomy") or {}).get("categories") or {}).get("edges") or []
    if not categories:
        frappe.logger().warning("Shopify taxonomy returned no categories")
        return

    # Build a map of shopify_id -> category info
    cat_map = {}
    for edge in categories:
        node = edge.get("node") or {}
        shopify_id = node.get("id", "")
        name = node.get("name", "")
        level = node.get("level", 0)
        if shopify_id and name:
            cat_map[shopify_id] = {"name": name, "level": level}

    # Get existing categories to avoid duplicates
    existing = {
        d.shopify_category_id: d.name
        for d in frappe.get_all(
            "Shopify Category",
            fields=["name", "shopify_category_id"],
        )
    }

    created = updated = 0
    for shopify_id, info in cat_map.items():
        if shopify_id in existing:
            # Update name if changed
            doc = frappe.get_doc("Shopify Category", existing[shopify_id])
            if doc.shopify_category_name != info["name"]:
                doc.shopify_category_name = info["name"]
                doc.save(ignore_permissions=True)
                updated += 1
        else:
            # Create new category
            doc = frappe.new_doc("Shopify Category")
            doc.shopify_category_name = info["name"]
            doc.shopify_category_id = shopify_id
            doc.insert(ignore_permissions=True)
            created += 1

    frappe.db.commit()
    frappe.logger().info(
        f"Shopify taxonomy sync: {created} created, {updated} updated, "
        f"{len(cat_map)} total categories"
    )


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
    if settings.sh_push_product_type and item.get("sh_shopify_product_type"):
        payload["productType"] = item.sh_shopify_product_type
    if settings.sh_push_images:
        images = _item_images(item, settings)
        if images:
            payload["files"] = [
                {"originalSource": url, "contentType": "IMAGE"} for url in images
            ]
    if item.get("sh_shopify_tags"):
        payload["tags"] = [t.strip() for t in item.sh_shopify_tags.split(",") if t.strip()]
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


# ── Push entry point ─────────────────────────────────────────────────────────

def push_item(item_code: str):
    item = frappe.get_doc("Item", item_code)
    if not _sync_enabled(item):
        return

    if item.variant_of:
        _push_product(frappe.get_doc("Item", item.variant_of))
    else:
        _push_product(item)


def run_bulk_export_to_shopify(trigger="manual", log_name=None):
    """
    One-off bulk push of every local (not-yet-linked) product to Shopify --
    for manually-created ERPNext Items that predate any Shopify connection,
    rather than requiring someone to open each one and tick the checkbox
    individually. Opts each candidate Item into sync_to_shopify as it's
    pushed (so future edits keep flowing outbound the normal way) and
    reuses the exact same push_item path Item's own doc_events already use,
    just called synchronously in a loop instead of one enqueue per save.

    Scoped to templates and simple items only (skips variants -- pushing a
    template already pushes its full current variant set in one call).
    """
    from alaiy_os_connector_shopify.shopify.sync_guard import load_or_create_log, has_active_sync

    log = load_or_create_log("product_export", trigger, log_name)

    if has_active_sync("product_export", exclude_name=log.name):
        log.status = "skipped"
        log.finished_at = frappe.utils.now_datetime()
        log.error_message = "Skipped: another product export is already running."
        log.save(ignore_permissions=True)
        frappe.db.commit()
        return log.name

    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    try:
        candidates = frappe.get_all(
            "Item",
            filters={
                "sh_shopify_product_id": ["in", ["", None]],
                "variant_of": ["in", ["", None]],
                "disabled": 0,
            },
            pluck="name",
        )

        processed = created = failed = 0

        for item_code in candidates:
            processed += 1
            try:
                if not frappe.db.get_value("Item", item_code, "sync_to_shopify"):
                    frappe.db.set_value("Item", item_code, "sync_to_shopify", 1)
                # Variants carry their own per-variant include flag (see
                # _variants_of) -- without opting them in too, a bulk
                # export of a template would push an empty variant set.
                frappe.db.set_value(
                    "Item", {"variant_of": item_code, "sync_to_shopify": 0},
                    "sync_to_shopify", 1,
                )
                push_item(item_code)
                # A real Shopify id landing on this Item is the only
                # reliable signal the push actually created something --
                # push_item silently no-ops on an unchanged/already-synced
                # item, so "no exception" alone doesn't mean "created".
                if frappe.db.get_value("Item", item_code, "sh_shopify_product_id"):
                    created += 1
                else:
                    failed += 1
                    _append_export_log(log, f"ERROR item={item_code}: push completed but no Shopify ID was written back")
            except Exception as exc:
                failed += 1
                _append_export_log(log, f"ERROR item={item_code}: {str(exc)[:200]}")
                frappe.log_error(
                    title=f"Shopify export: item {item_code} push failed",
                    message=frappe.get_traceback(),
                )

        log.status = "success"
        log.items_processed = processed
        log.items_created = created
        log.items_failed = failed
        log.finished_at = frappe.utils.now_datetime()
        summary = f"Exported {created} products to Shopify"
        if failed:
            summary += f"; {failed} failed"
        _append_export_log(log, summary)
        log.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception:
        log.status = "failed"
        log.error_message = frappe.get_traceback()[:500]
        log.finished_at = frappe.utils.now_datetime()
        log.save(ignore_permissions=True)
        frappe.db.commit()
        raise

    return log.name


def _variants_of(item):
    """
    Real variant docs for a template, or [item] itself for a simple item.

    Filters to variants with their own sync_to_shopify checked -- a
    variant's checkbox is the per-variant "include this one" switch (see
    on_item_change), so an unchecked variant is simply left out of the
    rebuilt set productSet sends, which Shopify treats as "remove it."
    """
    if not item.has_variants:
        return [item]
    names = frappe.get_all(
        "Item",
        filters={"variant_of": item.name, "sync_to_shopify": 1},
        pluck="name",
    )
    return [frappe.get_doc("Item", v) for v in names]


def _all_variants_of(item):
    """Every variant regardless of its own checkbox -- for archive_item,
    which must never restructure the product's variant set as a side
    effect of hiding it (productSet is full-desired-state; archiving with
    a filtered list would also DELETE the excluded variants on Shopify)."""
    if not item.has_variants:
        return [item]
    names = frappe.get_all("Item", filters={"variant_of": item.name}, pluck="name")
    return [frappe.get_doc("Item", v) for v in names]


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

    variants = _variants_of(item)
    if item.has_variants and not variants:
        # Every single variant unchecked but the template still on --
        # pushing a full-desired-state productSet with zero variants would
        # be Shopify-invalid (a product always has at least one variant)
        # and destructive even if it weren't. Unchecking the TEMPLATE is
        # the "take this product off Shopify" action; log and stand down.
        frappe.log_error(
            title=f"Shopify push skipped for {item.name}: no variants enabled",
            message="All variants have Sync to Shopify unchecked. Uncheck it on the template itself to archive the product on Shopify.",
        )
        return

    canonical = _product_canonical(item, variants, settings)
    fp = fingerprint.fingerprint(canonical)

    entity = entities.get_by_erpnext("product", "Item", item.name)
    if entity and entity.erpnext_fingerprint == fp:
        return  # unchanged since our own last push -- avoid spamming the API

    client = ShopifyGraphQLClient()
    product_input = _product_set_input(item, variants, settings, client)

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

def push_changed_items_only():
    """
    Hourly reconciliation: push every template flagged sync_to_shopify.

    Each push fingerprint-guards itself (see _push_product_unlocked), so an
    unchanged item early-returns before any Shopify API call -- no separate
    pre-check needed here. Called by the scheduled job in hooks.py.
    """
    sync_items = frappe.get_all(
        "Item",
        filters={"sync_to_shopify": 1, "variant_of": ""},
        pluck="name",
    )
    pushed = failed = 0
    for code in sync_items:
        try:
            push_item(code)
            pushed += 1
        except Exception:
            failed += 1
            frappe.log_error(
                title=f"Shopify: sync push failed for {code}",
                message=frappe.get_traceback(),
            )
    frappe.logger().info(f"Sync push reconciliation: {pushed} processed, {failed} failed")


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
    # list so _apply_product_meta's isinstance(tags, list) branch joins it
    # right back into the same string, keeping one code path for both.
    tags_raw = product.get("tags")
    category = product.get("category") or {}

    return {
        "legacyResourceId": str(product.get("id", "")),
        "title": product.get("title", ""),
        "bodyHtml": product.get("body_html", ""),
        "vendor": product.get("vendor", ""),
        "productType": product.get("product_type", ""),
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
    variants = _variants_of(item)
    canonical = _product_canonical(item, variants, settings)
    entities.save(entity, erpnext_fingerprint=fingerprint.fingerprint(canonical))

    frappe.logger().info(f"Updated Item {item.name} from Shopify product {product_id}")


def _update_item_from_shopify(item, product: dict):
    """
    Update ERPNext Item from Shopify product (inbound sync).

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

    from alaiy_os_connector_shopify.shopify.product_import import _apply_product_meta
    tags = product.get("tags")
    category = product.get("category") or {}
    _apply_product_meta(item, {
        "tags": [tags] if tags else [],
        "category": {"name": category.get("name") or category.get("full_name")} if category.get("name") or category.get("full_name") else None,
    })

    # Status: active/draft/archived
    if product.get("status"):
        item.disabled = 1 if product["status"] in ("archived", "draft") else 0

    # Self-heal a duplicated UOM row in the conversion factor table --
    # confirmed live: ERPNext's own Item.validate() appends a default UOM
    # row if it doesn't see one yet, and two near-simultaneous saves of the
    # same freshly-created template (e.g. import creating it, then an
    # immediate products/update webhook for the same product) can each
    # independently decide "no row yet" and both append one, leaving a
    # genuine duplicate that then blocks every future save with
    # "Unit of Measure ... entered more than once" forever until cleared.
    seen_uoms = set()
    deduped = []
    for row in item.uoms:
        if row.uom in seen_uoms:
            continue
        seen_uoms.add(row.uom)
        deduped.append(row)
    item.uoms = deduped

    # Save item. item.flags.ignore_permissions only covers this save --
    # ERPNext's Item.on_update() cascades into update_variants(), which
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
    if settings.sh_push_images:
        images = [img.get("src") for img in (product.get("images") or []) if img.get("src")]
        if images:
            from alaiy_os_connector_shopify.shopify.product_import import (
                _set_item_image, _set_item_slideshow
            )
            _set_item_image(item.name, images[0])
            if len(images) > 1:
                _set_item_slideshow(item.name, images, settings)

    # Update price + compare-at price per variant. Was previously never
    # touched on inbound update at all (see this function's old docstring) --
    # the webhook payload already carries both per variant, same as a
    # one-time import, so there's no reason a price edit made on Shopify
    # shouldn't flow back the same way title/description/tags do.
    from alaiy_os_connector_shopify.shopify.product_import import (
        _set_item_price, _set_item_compare_at_price, _ensure_uom, _REST_WEIGHT_UNIT_TO_UOM,
    )
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
    """Product deleted on Shopify - unlink ERPNext Item (preserve local data)."""
    entity = entities.get_by_external_id("product", product_id)

    if not entity:
        return

    if frappe.db.exists("Item", entity.erpnext_name):
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

    frappe.logger().info(f"Unlinked Item {entity.erpnext_name} (product {product_id} deleted)")


# ── Archive (disable) ────────────────────────────────────────────────────────

def archive_item(item_code: str):
    """Called when sync_to_shopify is unchecked -- or the Item disabled --
    on a template that's already linked. Archives the Shopify product
    (hidden from sales channels, order history intact) rather than
    deleting it or silently ignoring the checkbox. Resends the full
    product_set_input (not just {status}) since it's unconfirmed whether
    productSet treats a missing field as "leave alone" or "clear" --
    sending the complete state is correct either way."""
    item = frappe.get_doc("Item", item_code)
    if item.variant_of or not item.get("sh_shopify_product_id"):
        return
    if _sync_enabled(item):
        # Re-enabled before this job ran -- don't archive what should stay
        # active. Checks the full gate (checkbox AND not disabled), not
        # just the checkbox: a disabled item with sync still ticked must
        # NOT early-return here, or disabling would never archive at all.
        return

    try:
        item.lock(timeout=LOCK_TIMEOUT_SECONDS)
    except frappe.DocumentLockedError:
        return

    try:
        item = frappe.get_doc("Item", item.name)
        settings = frappe.get_single("Shopify Connector Settings")

        # Full variant set, deliberately unfiltered: productSet is
        # full-desired-state, so archiving with only the checked variants
        # would also DELETE the unchecked ones from Shopify as a side
        # effect of hiding the product.
        variants = _all_variants_of(item)

        client = ShopifyGraphQLClient()
        product_input = _product_set_input(item, variants, settings, client)
        product_input["status"] = "ARCHIVED"

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
