"""
Warehouse resolution helpers -- moved verbatim from order_sync.py,
unchanged.
"""

import frappe


def _resolve_default_warehouse(settings):
    """
    Belt-and-suspenders alongside ShopifyConnectorSettings._validate_default_warehouse:
    that check stops a NEW misconfiguration at save time, but doesn't retroactively
    fix a site that set this before the validation existed (confirmed live --
    a real site had it pointed at the auto-seeded root Group Warehouse, which
    silently killed every auto-created Delivery Note with "Group node warehouse
    is not allowed to select for transactions"). If the configured warehouse
    turns out to be a Group, fall back to the first real leaf warehouse under
    the connector's configured Company instead of hard-failing order import.
    """
    configured = settings.sh_default_warehouse
    if configured and not frappe.db.get_value("Warehouse", configured, "is_group"):
        return configured

    if configured:
        frappe.log_error(
            title="Shopify: Default Warehouse is a Group Warehouse, falling back",
            message=f"Configured: {configured}. Set a leaf warehouse in Shopify Connector Settings to silence this.",
        )

    fallback = frappe.db.get_value(
        "Warehouse", {"is_group": 0, "company": settings.sh_company}, "name")
    if not fallback:
        fallback = frappe.db.get_value("Warehouse", {"is_group": 0}, "name")
    if not fallback:
        frappe.throw(
            "No usable (non-Group) Warehouse exists for this company. "
            "Create one, then set it as 'Default Warehouse' on Shopify Connector Settings."
        )
    return fallback


def _resolve_warehouse_for_location(location_id, settings):
    """
    Look up the real per-supplier warehouse for a Shopify location id
    (the fulfillment's own location_id, REST-shaped -- a plain legacy
    numeric id, matching Shopify Location.sh_location_id), via
    Shopify Connector Settings.sh_location_map.

    Confirmed live: this map (Warehouse to Location Map, 70+ real rows,
    one per supplier) was populated and correct, but nothing in order/
    Delivery Note creation ever consulted it -- only inventory_sync.py's
    stock push did. Every order regardless of which supplier/location it
    actually came from was landing on the one generic
    sh_default_warehouse, silently wrong for FedEx shipping labels (the
    shipper address needs to be the SUPPLIER's real warehouse, not a
    shared fallback).

    Returns None if location_id is missing or has no mapping -- caller
    falls back to _resolve_default_warehouse, same as before this existed.
    """
    if not location_id:
        return None
    location_name = frappe.db.get_value("Shopify Location", {"sh_location_id": str(location_id)}, "name")
    if not location_name:
        return None
    for row in settings.get("sh_location_map") or []:
        if row.shopify_location == location_name:
            return row.warehouse
    return None


def _resolve_warehouse_for_item(item_code, settings, default_warehouse):
    """
    Real per-line-item warehouse for a Sales Order line, resolved from the
    ITEM's own Item.shopify_location -- not the order-level default.

    Confirmed live: _upsert_order_unlocked stamped every Sales Order Item
    with the same single _resolve_default_warehouse(settings) result,
    regardless of which real supplier actually owns that line. An order
    with line items from 2+ different suppliers had every line recorded
    against one shared warehouse -- order_routing.py's routing decision
    still resolves the real supplier correctly (it reads Item.shopify_
    location itself, independently), but the Sales Order Item's own stored
    warehouse field was silently wrong from the moment of import, for
    anyone/anything that reads that field directly rather than going
    through routing.

    Same resolution chain as the rest of this session's fixes: Item.
    shopify_location -> Shopify Location docname -> Shopify Connector
    Settings.sh_location_map -> real Warehouse. Falls back to the passed-in
    default_warehouse when the item has no resolved location yet (a real,
    expected gap for anything not yet imported through the fixed write
    path, or an item this connector doesn't own at all).
    """
    if not frappe.get_meta("Item").get_field("shopify_location"):
        return default_warehouse

    location_name = frappe.db.get_value("Item", item_code, "shopify_location")
    if not location_name:
        return default_warehouse

    for row in settings.get("sh_location_map") or []:
        if row.shopify_location == location_name:
            return row.warehouse

    return default_warehouse


def _force_valid_warehouse(dn, location_id=None):
    """
    make_delivery_note() copies each item's warehouse straight from the
    Sales Order's own already-stored Item rows -- which is exactly the
    problem for any order created before the Group Warehouse validation/
    self-heal existed (confirmed live: several real orders had a Group
    Warehouse permanently baked into their Item rows, since a submitted
    Sales Order's items can never be edited/amended just to fix this).
    Never trust that stored value for an actual stock transaction --
    always re-resolve and force a real leaf warehouse here, at the one
    point that actually matters (the document that moves stock), so this
    class of stale data can never break delivery creation again, for any
    order regardless of when it was created.

    location_id (the fulfillment's own Shopify location, when the caller
    has one) takes priority: resolves through sh_location_map to the
    real per-supplier warehouse, and applies to every row -- Shopify
    itself is saying this whole shipment left that one location.

    With no usable location_id, each row resolves its OWN warehouse from
    its item's Item.shopify_location instead of all sharing one fallback.
    A Delivery Note is the document that actually MOVES stock, so an
    order containing items from two different suppliers would otherwise
    draw every line out of the single default warehouse -- including the
    lines whose stock physically sits in a supplier's warehouse and was
    never in the default one at all. That both misstates the ledger and
    drives the default warehouse negative (the internally-impossible
    state scripts/fixes/fix_negative_bins.py exists to clean up).

    dn.set_warehouse stays the single order-level default: it's only the
    header default ERPNext applies to rows that don't set their own, and
    every row here sets one explicitly.
    """
    settings = frappe.get_single("Shopify Connector Settings")
    default_warehouse = _resolve_default_warehouse(settings)
    location_warehouse = _resolve_warehouse_for_location(location_id, settings)
    for item in dn.items:
        item.warehouse = location_warehouse or _resolve_warehouse_for_item(
            item.item_code, settings, default_warehouse)
    dn.set_warehouse = location_warehouse or default_warehouse
