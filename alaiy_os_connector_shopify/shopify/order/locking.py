"""
Per-order MySQL advisory lock -- moved verbatim from order_sync.py,
unchanged.
"""

import frappe


def _acquire_order_lock(order_id: str, timeout: int = 30) -> bool:
    """
    MySQL-native advisory lock shared by BOTH _upsert_order and
    _update_order for the same Shopify order_id -- enforced by the DB
    server itself, so it holds across separate worker processes
    regardless of how redis-cache is configured. A single shared lock
    name per order_id serializes our own outbound push (which can itself
    trigger Shopify to send back an echoed orders/updated webhook) against
    the inbound webhook handler for that very echo: observed live, the
    inbound handler loaded the Sales Order before an in-flight local save
    (removing an item) had committed, computed a stale diff against it,
    and then failed with TimestampMismatchError trying to cancel/amend a
    document that had changed underneath it by the time it got there.
    """
    return bool(frappe.db.sql("SELECT GET_LOCK(%s, %s)", (f"shopify_order_{order_id}", timeout))[0][0])


def _release_order_lock(order_id: str):
    frappe.db.sql("SELECT RELEASE_LOCK(%s)", (f"shopify_order_{order_id}",))
