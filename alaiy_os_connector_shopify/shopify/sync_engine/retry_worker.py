"""
Drain the retry queue, and tell somebody when a sync gives up.

retry_queue.py has always described a durable, backing-off retry with a
dead-letter end state -- it just had no caller on either side. Nothing
enqueued to it and nothing drained it, so every transient failure was a
single log line and the queue stayed permanently empty. This is the missing
half: the scheduler runs `drain` every five minutes, and the handlers below
say what "retry this" actually means per entity type.

Alerting is here rather than in retry_queue because the two answer different
questions. record_failure knows an attempt failed; only this module knows
the attempt was the LAST one, which is the only moment worth interrupting a
person for. A notification per attempt would train everyone to ignore them.
"""

import json

import frappe
from frappe.utils import now_datetime

from alaiy_os_connector_shopify.shopify.sync_engine import retry_queue

#: How many entries one tick will work through. The queue is drained by the
#: scheduler every five minutes, so a backlog clears over several ticks
#: rather than one run holding a worker for as long as it takes.
BATCH = 25

#: Who hears about a sync that has given up. System Manager rather than a
#: named address: a person leaves, an address goes stale, and the alert then
#: fails silently -- which is the same as having no alert at all.
ALERT_ROLE = "System Manager"


def drain(limit: int = BATCH):
    """Run every retry that is due. Safe on a schedule, never raises.

    Returns a summary rather than raising, for the same reason the other
    scheduled jobs here do: this runs unattended and one poisoned entry must
    not take down the rest of the tick.
    """
    summary = {"ok": True, "attempted": 0, "succeeded": 0, "failed": 0, "dead_lettered": 0}

    for name in retry_queue.get_due_entries(limit):
        entry = frappe.get_doc("Shopify Retry Queue Entry", name)
        # Re-check under the fresh read: another worker may have taken it
        # between get_due_entries and here, and running an outbound push
        # twice is a duplicate fulfillment or a double cancel on Shopify.
        if entry.status != "pending":
            continue

        entry.status = "in_progress"
        entry.save(ignore_permissions=True)
        frappe.db.commit()
        summary["attempted"] += 1

        try:
            _run(entry)
        except Exception as exc:
            frappe.db.rollback()
            retry_queue.record_failure(entry, frappe.get_traceback())
            summary["failed"] += 1
            # record_failure decides whether this was the last attempt. Only
            # then is anyone told -- a message per attempt for something the
            # queue is about to retry anyway is noise, and noise is what
            # makes a real alert get skimmed past.
            if entry.status == "dead_letter":
                summary["dead_lettered"] += 1
                notify_dead_letter(entry, exc)
        else:
            retry_queue.record_success(entry)
            summary["succeeded"] += 1

    return summary


def _run(entry):
    """Perform one queued operation, or refuse to guess at it.

    An unknown entity_type raises rather than silently succeeding. A queue
    that quietly marks work done because it did not recognise it is worse
    than one that fails loudly: the row disappears and the operation never
    happened.
    """
    payload = json.loads(entry.payload or "{}")
    handler = _HANDLERS.get((entry.direction, entry.entity_type))
    if not handler:
        raise ValueError(
            f"No retry handler for {entry.direction}/{entry.entity_type}. "
            "Add one to _HANDLERS rather than letting this entry pass as done."
        )
    handler(payload)


def _retry_order_cancel(payload):
    from alaiy_os_connector_shopify.shopify.order.push import push_order_cancel

    push_order_cancel(
        payload["order_id"], payload["sales_order"],
        reason=payload.get("reason", "OTHER"),
        refund=payload.get("refund", False),
        notify_customer=payload.get("notify_customer", False),
    )


def _retry_fulfillment_push(payload):
    from alaiy_os_connector_shopify.shopify.order.fulfillment_push import (
        push_delivery_note_fulfillment,
    )

    push_delivery_note_fulfillment(
        payload["delivery_note"],
        tracking_number=payload.get("tracking_number"),
        carrier=payload.get("carrier"),
        tracking_url=payload.get("tracking_url"),
    )


#: (direction, entity_type) -> what retrying it means. Keyed on both because
#: an inbound order and an outbound one are different operations entirely.
_HANDLERS = {
    ("outbound", "order"): _retry_order_cancel,
    ("outbound", "inventory"): _retry_fulfillment_push,
}


def notify_dead_letter(entry, error=None):
    """Tell an admin that a sync has stopped retrying.

    A Notification Log entry rather than an email: it needs no outgoing mail
    account (this site has none configured), it cannot bounce, and it appears
    in the desk where the person who can act on it already works. Email can
    be layered on later without changing this call site.

    Never raises. A failure to send an alert must not fail the drain that
    was reporting the original problem -- that turns one broken sync into a
    broken queue.
    """
    try:
        recipients = frappe.get_all(
            "Has Role", filters={"role": ALERT_ROLE, "parenttype": "User"},
            pluck="parent",
        )
        enabled = set(frappe.get_all(
            "User", filters={"name": ["in", recipients], "enabled": 1}, pluck="name"
        )) if recipients else set()
        # Never the system users: an alert addressed to Administrator or
        # Guest is an alert nobody receives.
        enabled -= {"Administrator", "Guest"}
        if not enabled:
            frappe.log_error(
                title="Shopify: nobody to alert about a dead-lettered sync",
                message=(
                    f"{entry.direction}/{entry.entity_type} entry {entry.name} gave up after "
                    f"{entry.attempt_count} attempts, and no enabled {ALERT_ROLE} exists to "
                    "tell. Grant the role to someone who watches this site."
                ),
            )
            return

        detail = str(error or entry.last_error or "")[:500]
        for user in enabled:
            note = frappe.new_doc("Notification Log")
            note.subject = f"Shopify sync gave up: {entry.entity_type} ({entry.direction})"
            note.for_user = user
            note.type = "Alert"
            note.document_type = "Shopify Retry Queue Entry"
            note.document_name = entry.name
            note.email_content = (
                f"A {entry.direction} {entry.entity_type} sync failed "
                f"{entry.attempt_count} times and has stopped retrying.<br><br>"
                f"<b>Last error:</b> {frappe.utils.escape_html(detail)}<br><br>"
                "Open the Shopify Retry Queue Entry to see the payload, fix the cause, "
                "then set its status back to pending to try again."
            )
            note.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        frappe.log_error(
            title="Shopify: could not send a dead-letter alert",
            message=frappe.get_traceback(),
        )


@frappe.whitelist()
def retry_now(entry_name: str):
    """Put a dead-lettered entry back in the queue, from the desk.

    The counterpart to the alert: being told a sync gave up is only useful if
    there is a way to try it again once the cause is fixed. Resets the
    attempt count, so a re-queued entry gets a full set of attempts rather
    than dying on the first one.
    """
    if "System Manager" not in frappe.get_roles():
        frappe.throw(
            frappe._("Only a System Manager can requeue a failed sync."),
            frappe.PermissionError,
        )

    entry = frappe.get_doc("Shopify Retry Queue Entry", entry_name)
    if entry.status not in ("dead_letter", "pending"):
        frappe.throw(
            frappe._("Entry {0} is {1}, so there is nothing to requeue.").format(
                entry_name, entry.status
            )
        )

    entry.status = "pending"
    entry.attempt_count = 0
    entry.next_attempt_at = now_datetime()
    entry.save(ignore_permissions=True)
    frappe.db.commit()
    return {"ok": True, "requeued": entry_name}
