"""
Durable retry queue for sync operations that failed transiently (rate
limits, network blips, momentary lock contention). Backed by the Shopify
Retry Queue Entry doctype so failures survive a worker restart, unlike an
in-memory retry loop.
"""

import json

import frappe
from frappe.utils import now_datetime, add_to_date

DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_BASE_DELAY_SECONDS = 60


def enqueue(direction: str, entity_type: str, payload: dict, synced_entity: str = None):
    """Insert a `pending` entry, ready to be picked up immediately."""
    entry = frappe.new_doc("Shopify Retry Queue Entry")
    entry.direction = direction
    entry.entity_type = entity_type
    entry.payload = json.dumps(payload)
    entry.synced_entity = synced_entity
    entry.status = "pending"
    entry.insert(ignore_permissions=True)
    frappe.db.commit()
    return entry


def record_failure(entry, error: str, max_attempts: int = DEFAULT_MAX_ATTEMPTS,
                    base_delay_seconds: int = DEFAULT_BASE_DELAY_SECONDS):
    """
    Increment the attempt count and either schedule the next attempt with
    exponential backoff, or move to dead_letter once max_attempts is hit.
    """
    entry.attempt_count = (entry.attempt_count or 0) + 1
    entry.last_error = str(error)[:500]

    if entry.attempt_count >= max_attempts:
        entry.status = "dead_letter"
        entry.next_attempt_at = None
    else:
        entry.status = "pending"
        delay = base_delay_seconds * (2 ** (entry.attempt_count - 1))
        entry.next_attempt_at = add_to_date(now_datetime(), seconds=delay)

    entry.save(ignore_permissions=True)
    frappe.db.commit()
    return entry


def record_success(entry):
    entry.status = "completed"
    entry.next_attempt_at = None
    entry.save(ignore_permissions=True)
    frappe.db.commit()
    return entry


def get_due_entries(limit: int = 50):
    """Pending entries whose next_attempt_at has arrived (or was never set)."""
    now = now_datetime()
    rows = frappe.get_all(
        "Shopify Retry Queue Entry",
        filters={"status": "pending"},
        fields=["name", "next_attempt_at"],
        limit_page_length=limit,
    )
    return [r.name for r in rows if not r.next_attempt_at or r.next_attempt_at <= now]
