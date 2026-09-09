"""
Lookup/upsert helpers for Shopify Synced Entity -- the table that pairs an
Alaiy OS document with its Shopify counterpart and holds both sides'
fingerprints for echo detection.

An external id is Shopify's, so it is only unique inside one shop: two sellers
both have a product 12345. Keyed on the id alone, the pairing table maps both
of their products to a single row, and the fingerprint on it -- the thing that
decides whether something changed and needs syncing -- then answers for
whichever store wrote last. The practical effect is one seller's update being
silently skipped as "unchanged" because the other seller's copy matches.

So every lookup takes the store. It stays optional and None searches every
store, which is the behaviour a caller that has not been given a connection
still needs.
"""

import frappe
from frappe.utils import now_datetime

from alaiy_os_connector_shopify.shopify.scoping import owned_by

DOCTYPE = "Shopify Synced Entity"


def get_by_erpnext(entity_type: str, erpnext_doctype: str, erpnext_name: str,
                   connection=None):
    name = frappe.db.get_value(
        DOCTYPE,
        owned_by(DOCTYPE, connection, {
            "entity_type": entity_type,
            "erpnext_doctype": erpnext_doctype,
            "erpnext_name": erpnext_name,
        }),
        "name",
    )
    return frappe.get_doc(DOCTYPE, name) if name else None


def get_by_external_id(entity_type: str, external_id: str, connection=None):
    name = frappe.db.get_value(
        DOCTYPE,
        owned_by(DOCTYPE, connection,
                 {"entity_type": entity_type, "external_id": external_id}),
        "name",
    )
    return frappe.get_doc(DOCTYPE, name) if name else None


def get_or_new(entity_type: str, erpnext_doctype: str = None, erpnext_name: str = None,
               external_id: str = None, connection=None):
    """
    Look up an existing pairing by Alaiy OS document first, falling back to
    Shopify's external ID, or start a fresh (unsaved) one if neither matches.

    A new row records the store, so the next lookup can find it by the pair
    rather than by the id alone.
    """
    entity = None
    if erpnext_doctype and erpnext_name:
        entity = get_by_erpnext(entity_type, erpnext_doctype, erpnext_name, connection)
    if entity is None and external_id:
        entity = get_by_external_id(entity_type, external_id, connection)
    if entity is None:
        entity = frappe.new_doc(DOCTYPE)
        entity.entity_type = entity_type
        if connection is not None:
            entity.connection = getattr(connection, "name", connection)
    return entity


def save(entity, **fields):
    """Set the given fields, stamp last_synced_at, and insert/save."""
    for key, value in fields.items():
        entity.set(key, value)
    entity.last_synced_at = now_datetime()
    if entity.is_new():
        entity.insert(ignore_permissions=True)
    else:
        try:
            entity.save(ignore_permissions=True)
        except frappe.TimestampMismatchError:
            # Concurrency fallback: update the database directly, bypassing checks
            fields["last_synced_at"] = now_datetime()
            frappe.db.set_value(entity.doctype, entity.name, fields, update_modified=True)
            # Reload to keep the in-memory object updated and matching DB
            entity = frappe.get_doc(entity.doctype, entity.name)
    frappe.db.commit()
    return entity
