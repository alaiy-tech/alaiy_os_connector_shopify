"""
Per-connection settings CRUD for the Next.js UI.

The platform's generic connector-settings API (alaiy_os.api.connectors) reads
and writes through frappe.get_single(settings_doctype) -- built for one
settings row per connector. Shopify Connection is a real multi-row DocType
(one bench can hold several stores), so that generic API cannot address a
single named connection; this module is the connection-aware equivalent,
mirroring its field-rendering and Password-masking logic exactly so the
frontend's existing ConnectorConfig-shaped response handling still applies.
"""

import frappe

from alaiy_os_connector_shopify.api import require_access, CONNECTION
from alaiy_os_connector_shopify import connections

RENDERABLE = {"Data", "Password", "Int", "Float", "Link", "Select", "Check", "Text", "Small Text", "Table"}


@frappe.whitelist()
def list_stores():
    """Every Shopify Connection this user may read, for the settings list page.
    Unlike api.sync.list_connections (enabled-only, for the sync picker), this
    includes disabled/not-yet-configured connections too -- the settings list
    is where a seller sets one up in the first place."""
    rows = []
    for name in connections.names():
        if not frappe.has_permission(CONNECTION, "read", doc=name):
            continue
        doc = frappe.get_cached_doc(CONNECTION, name)
        rows.append({
            "name": name,
            "label": doc.get("label") or name,
            "shop_url": doc.get("sh_shop_url") or "",
            "is_enabled": doc.get("is_enabled"),
            "last_status": doc.get("last_status"),
        })
    return rows


@frappe.whitelist()
def get_store_config(connection: str):
    """Field metadata + current values for one Shopify Connection, same shape
    as alaiy_os.api.connectors.get_connector_config."""
    require_access(connection, "read")
    meta = frappe.get_meta(CONNECTION)
    fields = []
    for f in meta.fields:
        if f.fieldtype not in RENDERABLE:
            continue
        fields.append({
            "fieldname": f.fieldname,
            "label": f.label,
            "fieldtype": f.fieldtype,
            "options": f.options,
            "reqd": f.reqd,
            "description": f.description,
        })

    doc = frappe.get_doc(CONNECTION, connection)
    values = {}
    for f in fields:
        if f["fieldtype"] == "Password":
            raw = doc.get(f["fieldname"])
            values[f["fieldname"]] = {"_type": "password", "_set": bool(raw)}
        else:
            values[f["fieldname"]] = doc.get(f["fieldname"])

    return {"fields": fields, "values": values}


@frappe.whitelist()
def save_store_config(connection: str, values):
    """Save one Shopify Connection's fields, then run its own connection test."""
    import json

    if isinstance(values, str):
        values = json.loads(values)

    require_access(connection, "write")
    doc = frappe.get_doc(CONNECTION, connection)
    meta = frappe.get_meta(CONNECTION)

    for fieldname, value in values.items():
        field_meta = meta.get_field(fieldname)
        if not field_meta:
            continue
        if field_meta.fieldtype == "Password":
            if value and str(value).strip():
                doc.set(fieldname, value)
        else:
            doc.set(fieldname, value)

    doc.save()
    frappe.db.commit()

    from alaiy_os_connector_shopify.api.test_connection import test_connection
    result = test_connection(connection=connection)
    return result


@frappe.whitelist()
def create_store(connection_id: str, label: str = None):
    """Make a new (disabled, unconfigured) Shopify Connection for the seller
    to fill in on the detail page. Requires create permission on the doctype
    itself -- there's no existing row yet to check doc-level access against."""
    frappe.has_permission(CONNECTION, "create", throw=True)
    if frappe.db.exists(CONNECTION, connection_id):
        frappe.throw(f"A connection named '{connection_id}' already exists.")
    doc = connections.create(connection_id, label=label)
    return {"name": doc.name}
