"""Whitelisted endpoints for the Shopify connector.

`@frappe.whitelist()` only requires a session: every endpoint in this package is
reachable by any logged-in user on the site, whatever their role. The doctypes
behind them -- Shopify Connection, Shopify Sync Log -- grant read and write to
System Manager alone, but none of the calls these endpoints make consult that:
`frappe.get_all`, `frappe.db.*` and `frappe.get_cached_doc` all bypass doctype
permissions. The check has to be made here, in the endpoint, or it is not made
at all.
"""

import frappe

CONNECTION = "Shopify Connection"


def require_access(connection_name: str | None = None, ptype: str = "read") -> None:
    """Refuse a caller who may not act on this store.

    Checked against the Shopify Connection document rather than a hardcoded
    role, so it follows the doctype's own permissions and any User Permission a
    bench uses to keep one seller out of another seller's connection -- which is
    what a caller-supplied `connection=` name otherwise leaves wide open on a
    bench holding many stores.

    `connection_name` is None for a bench-wide call, or one the connector could
    not resolve to a store; the doctype-level permission still has to hold.
    """
    frappe.has_permission(CONNECTION, ptype, doc=connection_name, throw=True)


def require_access_to_record(doctype: str, name: str, ptype: str = "read") -> str | None:
    """
    Refuse a caller who may not act on the store a record belongs to.

    Several endpoints are addressed by a record rather than by a store: a
    Delivery Note to push, a Collection to publish, a Listing to read defaults
    off. The store is not in the request at all -- it is on the row -- so the
    check has to load it first and authorise against that.

    Without this, naming somebody else's record is enough. The endpoints in
    question call Shopify with the owning store's own credentials, so an
    unauthorised call does not fail at the boundary: it succeeds, against the
    wrong merchant's shop.

    Returns the store's name so the caller can scope its own work to it, or
    None for a record with no store yet -- an unmigrated row, or one created by
    hand. None still goes through the doctype-level check.
    """
    from alaiy_os_connector_shopify.shopify.scoping import connection_field

    connection_name = None
    if name and frappe.db.exists(doctype, name):
        connection_name = frappe.db.get_value(doctype, name, connection_field(doctype))

    require_access(connection_name, ptype)
    return connection_name
