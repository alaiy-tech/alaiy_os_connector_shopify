import frappe
from frappe.utils import now_datetime, add_to_date

STALE_ACTIVE_THRESHOLD_MINUTES = 120


def has_active_sync(sync_type: str, exclude_name: str = None) -> bool:
    """
    True if another sync of this type is genuinely still queued/running. A
    queued/running log older than the stale threshold is treated as orphaned
    -- e.g. its worker was killed mid-run by a deploy/restart -- and is
    marked failed so it stops permanently blocking future runs.

    Uses a MySQL named lock to serialize the check-then-mark-stale logic
    across concurrent callers (e.g. a scheduled tick and a manual button
    click landing at the same moment) -- without it, two callers could both
    read "no active rows" before either flips a row to running, letting two
    pushes run at once.
    """
    lock_name = f"shopify_sync_guard_{sync_type}"
    got_lock = frappe.db.sql("SELECT GET_LOCK(%s, 5)", (lock_name,))[0][0]
    if not got_lock:
        # Another caller is mid-check right now -- treat as active rather
        # than risk a double-run.
        return True
    try:
        cutoff = add_to_date(now_datetime(), minutes=-STALE_ACTIVE_THRESHOLD_MINUTES)
        active_rows = frappe.get_all(
            "Shopify Sync Log",
            filters={"sync_type": sync_type, "status": ["in", ["queued", "running"]]},
            fields=["name", "started_at"],
        )
        active = False
        for row in active_rows:
            if row.name == exclude_name:
                continue
            if row.started_at and row.started_at < cutoff:
                frappe.db.set_value("Shopify Sync Log", row.name, {
                    "status": "failed",
                    "finished_at": now_datetime(),
                    "error_message": "Marked failed: orphaned queued/running log (worker likely restarted mid-run).",
                })
            else:
                active = True
        if active_rows:
            frappe.db.commit()
        return active
    finally:
        frappe.db.sql("SELECT RELEASE_LOCK(%s)", (lock_name,))


def load_or_create_log(sync_type: str, trigger: str, log_name: str = None):
    """
    Reuse the Sync Log row created at enqueue time (so it's visible as
    "queued" even before the job starts), or create one on the spot for
    callers that don't pre-create it (e.g. direct bench execute).
    """
    if log_name and frappe.db.exists("Shopify Sync Log", log_name):
        return frappe.get_doc("Shopify Sync Log", log_name)
    log = frappe.new_doc("Shopify Sync Log")
    log.sync_type = sync_type
    log.trigger = trigger
    log.status = "queued"
    log.started_at = now_datetime()
    log.insert(ignore_permissions=True)
    frappe.db.commit()
    return log


def append_log(log, message: str):
    """Append a line to log.log_messages without saving."""
    existing = log.log_messages or ""
    log.log_messages = (existing + "\n" + message).strip()


def is_cancel_requested(log_name: str) -> bool:
    """
    Cheap poll for a running job's own loop to check whether the Stop
    button in the Shopify dashboard was clicked. A plain column read, not
    the killable-job mechanism -- a long export/import loop cooperatively
    checks this every N items and stops itself cleanly (partial progress
    already flushed to the log stays), rather than the job being killed
    from outside mid-write.
    """
    return bool(frappe.db.get_value("Shopify Sync Log", log_name, "cancel_requested"))


@frappe.whitelist()
def request_cancel(log_name: str):
    """Flip cancel_requested on a running/queued Sync Log -- the job itself
    checks this and stops cleanly on its next poll, see is_cancel_requested.
    No effect on a log that's already finished (success/failed/skipped/
    cancelled), so a stale UI click after the job ended is harmless."""
    status = frappe.db.get_value("Shopify Sync Log", log_name, "status")
    if status not in ("queued", "running"):
        return {"cancelled": False, "reason": f"Job already {status}"}
    frappe.db.set_value("Shopify Sync Log", log_name, "cancel_requested", 1)
    frappe.db.commit()
    return {"cancelled": True}


def close_log(log, status, processed=0, created=0, failed=0, error=""):
    log.status = status
    log.finished_at = now_datetime()
    log.items_processed = processed
    log.items_created = created
    log.items_failed = failed
    if error:
        log.error_message = (error or "")[:500]
    log.save(ignore_permissions=True)
    frappe.db.commit()
