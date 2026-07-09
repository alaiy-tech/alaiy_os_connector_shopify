"""
Lookup/upsert helpers for Shopify Synced Entity -- the table that pairs an
ERPNext document with its Shopify counterpart and holds both sides'
fingerprints for echo detection.
"""

import frappe
from frappe.utils import now_datetime


def get_by_erpnext(entity_type: str, erpnext_doctype: str, erpnext_name: str):
    name = frappe.db.get_value(
        "Shopify Synced Entity",
        {"entity_type": entity_type, "erpnext_doctype": erpnext_doctype, "erpnext_name": erpnext_name},
        "name",
    )
    return frappe.get_doc("Shopify Synced Entity", name) if name else None


def get_by_external_id(entity_type: str, external_id: str):
    name = frappe.db.get_value(
        "Shopify Synced Entity",
        {"entity_type": entity_type, "external_id": external_id},
        "name",
    )
    return frappe.get_doc("Shopify Synced Entity", name) if name else None


def get_or_new(entity_type: str, erpnext_doctype: str = None, erpnext_name: str = None, external_id: str = None):
    """
    Look up an existing pairing by ERPNext document first, falling back to
    Shopify's external ID, or start a fresh (unsaved) one if neither matches.
    """
    entity = None
    if erpnext_doctype and erpnext_name:
        entity = get_by_erpnext(entity_type, erpnext_doctype, erpnext_name)
    if entity is None and external_id:
        entity = get_by_external_id(entity_type, external_id)
    if entity is None:
        entity = frappe.new_doc("Shopify Synced Entity")
        entity.entity_type = entity_type
    return entity


def save(entity, **fields):
    """Set the given fields, stamp last_synced_at, and insert/save."""
    for key, value in fields.items():
        entity.set(key, value)
    entity.last_synced_at = now_datetime()
    if entity.is_new():
        entity.insert(ignore_permissions=True)
    else:
        entity.save(ignore_permissions=True)
    frappe.db.commit()
    return entity
