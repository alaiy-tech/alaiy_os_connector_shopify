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
    real per-supplier warehouse. Falls back to the single generic
    sh_default_warehouse when there's no location_id, no mapping for it,
    or the caller didn't pass one at all (the full-order-fallback path
    has no per-fulfillment location to work with).
    """
    settings = frappe.get_single("Shopify Connector Settings")
    warehouse = _resolve_warehouse_for_location(location_id, settings) or _resolve_default_warehouse(settings)
    for item in dn.items:
        item.warehouse = warehouse
    dn.set_warehouse = warehouse
