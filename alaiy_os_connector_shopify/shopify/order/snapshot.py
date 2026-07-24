"""
Before-save item snapshotting for change detection -- moved verbatim from
order_push.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver


def _items_before_cache_key(so_name: str) -> str:
    return f"shopify_items_before::{so_name}"


def snapshot_before_update_child_qty_rate():
    """
    before_request hook: for Alaiy OS's "Update Items" quick-edit grid
    specifically (erpnext.controllers.accounts_controller.update_child_qty_rate),
    snapshot the Sales Order's current items into cache BEFORE that
    whitelisted method runs at all.

    Confirmed live that on_sales_order_validate's capture doesn't reliably
    fire for this endpoint -- an item ADDITION never produced a validate
    snapshot at all (items removal did, inconsistently), so relying on
    validate() for this specific call is a dead end. Capturing here
    instead, at the request boundary, guarantees the true pre-edit state
    regardless of how many internal saves/reloads update_child_qty_rate
    performs afterward.
    """
    if frappe.form_dict.get("cmd") != "erpnext.controllers.accounts_controller.update_child_qty_rate":
        return
    if frappe.form_dict.get("parent_doctype") != "Sales Order":
        return
    so_name = frappe.form_dict.get("parent_doctype_name")
    if not so_name:
        return
    cache_key = _items_before_cache_key(so_name)
    if frappe.cache().get_value(cache_key) is not None:
        return
    snapshot = frappe.get_all(
        "Sales Order Item",
        filters={"parent": so_name},
        fields=["item_code", "qty", "rate", "sh_shopify_variant_id"],
    )
    frappe.cache().set_value(cache_key, snapshot, expires_in_sec=1800)
    # Plain logger, not frappe.log_error -- this is a routine trace, not a
    # failure. Confirmed live: leaving debug traces on log_error made
    # Error Log indistinguishable from real crashes for anyone checking it.
    frappe.logger().debug(f"Shopify: pre-request snapshot for {so_name}: {snapshot!r}")


def on_sales_order_validate(doc, method=None):
    """
    Snapshots the DB's current items (before this save's changes land) into
    cache, for _detect_items_changed/_detect_removed_variant_ids to diff
    against later in on_update/on_update_after_submit.

    Persisted in cache keyed by doc.name -- NOT on doc.flags. Alaiy OS's
    "Update Items" quick-edit grid (update_child_qty_rate) saves an
    already-submitted Sales Order TWICE internally: once to apply the item
    changes, then again on a freshly RELOADED doc object to recalculate
    totals/taxes. doc.flags is pure in-memory state on one Python object,
    so it's gone by the second save -- confirmed live: on_update_after_submit
    saw before_snapshot=None and items_changed=False every single time,
    because whatever validate() had captured never survived to the save
    whose on_update_after_submit we actually catch.

    Guarded so the SECOND save in that sequence doesn't overwrite the true
    original with the already-changed intermediate state: only the first
    validate() call in a given edit sequence writes the cache key.
    """
    if doc.is_new():
        return
    cache_key = _items_before_cache_key(doc.name)
    if frappe.cache().get_value(cache_key) is not None:
        return
    snapshot = frappe.get_all(
        "Sales Order Item",
        filters={"parent": doc.name},
        fields=["item_code", "qty", "rate", "sh_shopify_variant_id"],
    )
    frappe.cache().set_value(cache_key, snapshot, expires_in_sec=1800)
    # Plain logger, not frappe.log_error -- see snapshot_before_update_child_qty_rate's
    # matching comment.
    frappe.logger().debug(f"Shopify: validate snapshot for {doc.name}: {snapshot!r}")


def _detect_items_changed(doc) -> bool:
    """
    Check if Sales Order's items have been added, removed, or modified.
    Returns True if any items field changed, False if only status/metadata changed.
    """
    before_rows = frappe.cache().get_value(_items_before_cache_key(doc.name))
    if before_rows is None:
        # No snapshot means "we don't actually know if items changed", NOT
        # "confirmed nothing changed" -- returning False here would silently
        # skip reflecting a real item edit to Shopify (same bug shape as
        # the missing-Bin-as-zero inventory incident). Assume changed and
        # log it so a genuinely expired/evicted snapshot is visible instead
        # of a silent no-op.
        frappe.log_error(
            title=f"Shopify: no before-snapshot for {doc.name}, assuming items changed",
            message="Snapshot cache key missing/expired -- cannot diff, erring toward reflecting the edit.",
        )
        return True

    original_items = {
        (row["item_code"], row["qty"], row["rate"]) for row in before_rows
    }
    current_items = {
        (item.item_code, item.qty, item.rate) for item in (doc.items or [])
    }
    return original_items != current_items


def _detect_removed_variant_ids(doc) -> list:
    """
    Shopify variant IDs for line item ROWS present before this save but
    missing after -- i.e. genuinely removed rows, not a qty/rate edit on a
    surviving row. This is what actually gets matched against Shopify's
    order line items for removal; item_code/qty/rate alone can't tell us
    WHICH item to remove on the Shopify side.
    """
    before_rows = frappe.cache().get_value(_items_before_cache_key(doc.name))
    if not before_rows:
        # Can't know WHICH rows were removed without the before-state --
        # nothing safe to fabricate here, but flag it so a real removal
        # that silently fails to reflect to Shopify is at least visible.
        frappe.log_error(
            title=f"Shopify: no before-snapshot for {doc.name}, cannot detect removed items",
            message="Snapshot cache key missing/expired -- any item removal in this save will NOT be reflected to Shopify.",
        )
        return []
    before_keys = {
        (row["item_code"], row["sh_shopify_variant_id"]) for row in before_rows
    }
    after_keys = {
        (item.item_code, item.get("sh_shopify_variant_id")) for item in (doc.items or [])
    }
    removed = before_keys - after_keys
    return [variant_id for (_, variant_id) in removed if variant_id]


def _detect_added_items(doc) -> list:
    """
    Line item ROWS present after this save but missing before -- genuinely
    new rows, not a qty/rate edit on a surviving row. Falls back to the
    Item master's own sh_shopify_variant_id when the new row itself
    doesn't have one set -- a row a user just added by hand through the
    grid won't have it (unlike rows our own inbound sync creates), but
    the linked Item record already carries it if this SKU was ever synced
    from Shopify. An Item with no Shopify link at all is simply skipped,
    since there's nothing to push it as.
    """
    before_rows = frappe.cache().get_value(_items_before_cache_key(doc.name))
    if before_rows is None:
        # Same reasoning as _detect_removed_variant_ids: can't fabricate
        # which rows are genuinely new without the before-state, but flag
        # it so a real addition that silently fails to reflect is visible.
        frappe.log_error(
            title=f"Shopify: no before-snapshot for {doc.name}, cannot detect added items",
            message="Snapshot cache key missing/expired -- any item addition in this save will NOT be reflected to Shopify.",
        )
        return []
    before_keys = {
        (row["item_code"], row["sh_shopify_variant_id"]) for row in before_rows
    }
    added = []
    for item in (doc.items or []):
        variant_id = item.get("sh_shopify_variant_id")
        if (item.item_code, variant_id) in before_keys:
            continue
        if not variant_id:
            # Listing Variant's copy first, Item as fallback.
            variant_id = listing_resolver.variant_id_of_item(item.item_code)
        if not variant_id:
            continue
        added.append({"variant_id": variant_id, "qty": item.qty})
    return added
