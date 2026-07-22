"""
Alaiy OS -> Shopify product/variant push.

Gated by the template's Shopify Product Listing (is_enabled). Enabling the
Listing pushes the whole product; disabling or trashing it archives the
product on Shopify (kept, hidden from sales channels, order history intact)
and re-enabling unarchives + pushes again. Each variant's inclusion is its
Shopify Listing Variant row (is_enabled): an excluded variant drops from the
next productSet push, which removes it on Shopify.

Always operates at the template level: even when only one variant changed,
the whole current variant set is rebuilt and sent to Shopify via productSet,
since each variant payload carries its own Shopify variant `id` when it has
one -- Shopify updates existing variants and creates new ones from the same
call.

Every push acquires a document lock on the template first. Alaiy OS's own
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

from alaiy_os_connector_shopify.shopify.sync_guard import append_log as _append_export_log

from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
from alaiy_os_connector_shopify.shopify.sync_engine import fingerprint
from alaiy_os_connector_shopify.shopify.sync_engine import entities

from alaiy_os_connector_shopify.shopify.product.queries import _PRODUCT_SET_MUTATION
from alaiy_os_connector_shopify.shopify.product.canonical import _product_canonical, _product_set_input
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver

LOCK_TIMEOUT_SECONDS = 30


def push_item(item_code: str):
    item = frappe.get_doc("Item", item_code)
    # The Shopify Product Listing's is_enabled is the sole live gate now
    # (replaces Item.sync_to_shopify) -- no enabled Listing, nothing pushes.
    if not listing_resolver.is_enabled(item):
        return

    if item.variant_of:
        _push_product(frappe.get_doc("Item", item.variant_of))
    else:
        _push_product(item)


def run_bulk_export_to_shopify(trigger="manual", log_name=None):
    """
    One-off bulk push of every local (not-yet-linked) product to Shopify --
    for manually-created Alaiy OS Items that predate any Shopify connection,
    rather than requiring someone to create + enable a Listing for each one
    by hand. Creates and enables a Listing per candidate (all variant rows
    on), then reuses the same push_item path, called synchronously in a loop.

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
                # Give each candidate an enabled Listing (all variant rows on)
                # and push it -- the Listing is the enable gate now, so a bulk
                # export must create + enable one rather than ticking
                # Item.sync_to_shopify.
                listing = listing_resolver.ensure_listing(item_code)
                if listing:
                    for r in listing.variants:
                        r.is_enabled = 1
                    listing.is_enabled = 1
                    listing.flags.from_shopify_sync = True  # push explicitly below, not via echo
                    listing.save(ignore_permissions=True)
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

    Included variants come from the template's Shopify Listing Variant rows
    (is_enabled) via the resolver -- a variant left out is simply not in the
    rebuilt set productSet sends, which Shopify treats as "remove it."
    """
    if not item.has_variants:
        return [item]
    names = listing_resolver.enabled_variant_names(item.name)
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
    listing = listing_resolver.get_listing(item.name)
    if not listing:
        return  # gate already checked is_enabled, but stay defensive

    variants = _variants_of(item)
    if item.has_variants and not variants:
        # Every variant row disabled but the Listing still enabled -- pushing
        # a full-desired-state productSet with zero variants would be
        # Shopify-invalid (a product always has at least one variant) and
        # destructive even if it weren't. Disabling the LISTING is the "take
        # this product off Shopify" action; disable it and stand down instead
        # of leaving it stuck "uploading".
        frappe.db.set_value("Shopify Product Listing", listing.name, "is_enabled", 0)
        frappe.db.commit()
        frappe.log_error(
            title=f"Shopify push skipped for {item.name}: no variants enabled",
            message="All Listing Variant rows are disabled. Disable the Listing itself to archive the product on Shopify.",
        )
        return

    canonical = _product_canonical(item, variants, settings, listing)
    fp = fingerprint.fingerprint(canonical)

    entity = entities.get_by_erpnext("product", "Item", item.name)
    if entity and entity.erpnext_fingerprint == fp:
        return  # unchanged since our own last push -- avoid spamming the API

    client = ShopifyGraphQLClient()
    product_input = _product_set_input(item, variants, settings, listing, client)

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
        # Self-heal: check if error is due to variant IDs that do not exist on Shopify anymore
        import re
        invalid_variant_ids = []
        for err in errors:
            msg = err.get("message") or ""
            match = re.search(r"Following variant ids do not exist:\s*\[([\d,\s]+)\]", msg)
            if match:
                invalid_ids = [x.strip() for x in match.group(1).split(",") if x.strip()]
                invalid_variant_ids.extend(invalid_ids)

        if invalid_variant_ids:
            frappe.logger().warning(
                f"Shopify push: found stale variant IDs {invalid_variant_ids} in Alaiy OS database. "
                "Clearing them and retrying sync..."
            )
            for v_id in invalid_variant_ids:
                frappe.db.sql("""
                    UPDATE `tabItem`
                    SET sh_shopify_variant_id = NULL
                    WHERE sh_shopify_variant_id = %s
                """, v_id)
            frappe.db.commit()

            # Re-fetch item, rebuild variants list and payload, then retry the sync
            item = frappe.get_doc("Item", item.name)
            variants = _variants_of(item)
            product_input = _product_set_input(item, variants, settings, listing, client)

            data = client.execute(_PRODUCT_SET_MUTATION, {
                "input": product_input,
                "identifier": identifier,
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
    # Item is the single source of truth for the id; the Listing's
    # sh_shopify_product_id is a read-only fetch_from view of it (no separate
    # write here -- avoids a drifting mirror, rule 4). Only stamp last_synced_at.
    frappe.db.set_value("Shopify Product Listing", listing.name,
                        "last_synced_at", frappe.utils.now_datetime())

    # Match by SKU, not response order -- productSet's variants connection
    # isn't documented to preserve submission order, and getting this wrong
    # would silently write one variant's Shopify ID onto a different
    # Alaiy OS item.
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

    # Reconcile manual-collection membership after the product itself is set --
    # membership is product-level, driven by the template Item's collections
    # field. Best-effort: never fails the push it rides on.
    from alaiy_os_connector_shopify.shopify.product.collections import sync_item_collections
    sync_item_collections(item, product_id, client)

    entities.save(
        entity or entities.get_or_new(
            "product", "Item", item.name, product_id),
        external_id=product_id,
        erpnext_doctype="Item",
        erpnext_name=item.name,
        erpnext_fingerprint=fp,
    )
    frappe.db.commit()


def push_changed_items_only():
    """
    Hourly reconciliation: push every template with an enabled Listing.

    Each push fingerprint-guards itself (see _push_product_unlocked), so an
    unchanged item early-returns before any Shopify API call -- no separate
    pre-check needed here. Called by the scheduled job in hooks.py.
    """
    sync_items = frappe.get_all(
        "Shopify Product Listing",
        filters={"is_enabled": 1},
        pluck="item",
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
