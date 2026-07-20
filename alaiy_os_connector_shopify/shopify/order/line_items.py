"""
Sales Order line-item reconciliation against Shopify's current state --
moved verbatim from order_sync.py, unchanged.
"""

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.order.utils import _line_item_qty, _resolve_item_code


def _apply_line_item_diff(doc, order: dict, warehouse: str) -> bool:
    """
    Reconciles doc.items (a Sales Order's child table) against Shopify's
    current line items. Returns True if anything actually changed, so the
    caller can decide whether a save/amend is even needed.
    """
    current_items_by_variant = {item.get("sh_shopify_variant_id"): item for item in doc.items if item.get("sh_shopify_variant_id")}
    current_items_by_code = {item.item_code: item for item in doc.items if not item.get("sh_shopify_variant_id")}
    new_items_from_shopify = {}

    # Parse Shopify's line items
    for li in order.get("line_items", []):
        item_code = _resolve_item_code(li)
        if not item_code:
            continue
        variant_id = str(li.get("variant_id", ""))
        if not variant_id:
            continue

        qty = _line_item_qty(li)
        if qty <= 0:
            continue  # removed via Order Editing -- handled below via removed_variants

        new_items_from_shopify[variant_id] = {
            "item_code": item_code,
            "qty": qty,
            "rate": flt(li.get("price", 0)),
            "warehouse": warehouse,
        }

    # Detect changes: match by variant_id first, then by item_code (fallback for old items)
    added_variants = set()
    common_variants = set()
    for variant_id, new_item_data in new_items_from_shopify.items():
        if variant_id in current_items_by_variant:
            common_variants.add(variant_id)
        elif new_item_data["item_code"] in current_items_by_code:
            # Fallback: old item without variant_id, match by item_code
            # Promote it to variant-keyed for consistent removal/update logic
            old_item = current_items_by_code.pop(new_item_data["item_code"])
            current_items_by_variant[variant_id] = old_item
            common_variants.add(variant_id)
        else:
            added_variants.add(variant_id)

    # Items in current_items_by_code that weren't matched = removed from Shopify
    removed_variants = set(current_items_by_variant.keys()) - set(new_items_from_shopify.keys())

    changed = bool(added_variants or removed_variants)

    # Remove items that were deleted in Shopify
    for variant_id in removed_variants:
        doc.items.remove(current_items_by_variant[variant_id])

    # Add new items from Shopify
    for variant_id in added_variants:
        new_item_data = new_items_from_shopify[variant_id]
        item_code = new_item_data["item_code"]
        item_name = frappe.db.get_value("Item", item_code, "item_name") or item_code
        uom = frappe.db.get_value("Item", item_code, "stock_uom") or "Nos"
        doc.append("items", {
            "item_code": item_code,
            "item_name": item_name,
            "uom": uom,
            "conversion_factor": 1,
            "qty": new_item_data["qty"],
            "rate": new_item_data["rate"],
            "warehouse": new_item_data["warehouse"],
            "delivery_date": frappe.utils.getdate(frappe.utils.today()),
        })

    # Update quantities on existing items and backfill variant_id if missing
    for variant_id in common_variants:
        current_row = current_items_by_variant[variant_id]
        new_qty = new_items_from_shopify[variant_id]["qty"]
        new_rate = new_items_from_shopify[variant_id]["rate"]

        if current_row.qty != new_qty or current_row.rate != new_rate:
            current_row.qty = new_qty
            current_row.rate = new_rate
            changed = True

        # Backfill variant_id for old items (created before variant_id field existed)
        if not current_row.get("sh_shopify_variant_id"):
            current_row.sh_shopify_variant_id = variant_id

    return changed


def _sync_order_line_items(so_name: str, order: dict):
    """
    Reconciles line items between Shopify order and Alaiy OS Sales Order.

    A submitted Sales Order can't have its Items table structurally changed
    in place -- Alaiy OS enforces this (UpdateAfterSubmitError), confirmed
    live: removing a line via Shopify's Order Editing hit this the moment
    a real submitted order was edited. The correct handling for "a
    submitted document needs to change" is Alaiy OS's own amend mechanism
    (cancel, then create a new revision carrying amended_from) rather than
    silently dropping the change or bypassing the doctype's own guard.
    A still-Draft order (not yet auto-submitted -- see _upsert_order's
    draft-order handling) can just be edited and saved directly.
    """
    from alaiy_os_connector_shopify.shopify.order.warehouse import _resolve_default_warehouse

    so = frappe.get_doc("Sales Order", so_name)
    if so.docstatus not in (0, 1):
        return

    settings = frappe.get_single("Shopify Connector Settings")
    warehouse = _resolve_default_warehouse(settings)

    if so.docstatus == 0:
        if _apply_line_item_diff(so, order, warehouse):
            so.flags.ignore_permissions = True
            so.flags.from_shopify_sync = True
            so.save()
            frappe.db.commit()
        return

    # docstatus == 1: dry-run the diff on a throwaway copy first -- cancel +
    # amend is a real, visible action (new doc name, original marked
    # Cancelled), not worth doing unless something actually changed.
    #
    # Retries once on TimestampMismatchError: our own outbound push (e.g.
    # removing an item locally) can itself cause Shopify to echo back this
    # very webhook. Even with _update_order's per-order lock, there's a
    # narrow window where `so` was loaded a moment before that local save
    # committed -- so re-fetch fresh and recompute the diff rather than
    # failing outright (confirmed live: this raced and crashed before the
    # retry was added). Same self-healing idiom already used elsewhere in
    # this codebase for TimestampMismatchError.
    for attempt in range(2):
        probe = frappe.copy_doc(so)
        if not _apply_line_item_diff(probe, order, warehouse):
            return

        so.flags.ignore_permissions = True
        so.flags.from_shopify_sync = True
        try:
            so.cancel()
            break
        except frappe.TimestampMismatchError:
            if attempt == 1:
                raise
            so = frappe.get_doc("Sales Order", so_name)
    frappe.db.commit()

    amended = frappe.copy_doc(so)
    amended.amended_from = so.name
    _apply_line_item_diff(amended, order, warehouse)
    amended.flags.ignore_permissions = True
    amended.flags.from_shopify_sync = True
    amended.insert()
    amended.submit()
    frappe.db.commit()
