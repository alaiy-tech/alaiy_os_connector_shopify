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


def _force_valid_warehouse(dn):
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
    """
    settings = frappe.get_single("Shopify Connector Settings")
    warehouse = _resolve_default_warehouse(settings)
    for item in dn.items:
        item.warehouse = warehouse
    dn.set_warehouse = warehouse
