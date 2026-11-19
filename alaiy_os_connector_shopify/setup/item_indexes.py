"""Builds the Item indexes in the background, one at a time, and never at install.

Item is the big table: a catalogue is millions of rows. Building an index on it scans the whole table and
needs a metadata lock at the start and the end, so doing it inside an install or a migrate is slow and can
hold up every query on Item while it waits. An install therefore adds the columns without the indexes, and
this module adds them afterwards, on its own. Nobody has to run anything.

How it stays out of the way
  - An hourly job, and one run queued after every install and migrate, look for a missing index. The check
    is one SHOW INDEX and queues a build only when an index is missing, so once all four exist it is free.
  - One index per run. Runs cannot overlap: a database lock (not a queue entry) guards them, and that lock
    is released by the database itself if the worker dies, so a crash never leaves it stuck.
  - It does not start while the site is in maintenance mode, while a query older than QUIET_AFTER_SECONDS is
    running on Item, while another statement is waiting on Item's table lock (a migrate, for example), or
    outside the optional window `shopify_item_index_window` (for example "01:00-05:00", server time).
  - It waits for the table lock for lock_wait_seconds at most (default 10, site config
    `shopify_item_index_lock_wait`, kept between 1 and 60), on this connection only. If the lock is not
    free it gives up and changes nothing, so Item queries are never queued behind it for longer than that.
  - It does not start without free disk space (when the database is on this host) for the index and the
    temporary files.
  - A run that fails after doing real work (a lock lost at the end of a long build, a full disk, an online
    DDL log that is too small) is recorded and the next attempt is delayed, 1 hour, then 2, 4 and so on up to
    a day, so a problem that repeats does not re-scan the table every hour. The failure is logged once.
  - The job has a timeout, and Frappe also puts a statement time limit of 1.5 times that on the ALTER, so a
    build cannot run forever. An ALTER is atomic: stopped at any point it leaves the table as it was.
  - A built index is flagged on its Custom Field, because Frappe drops an index its field does not flag on
    the next schema update. If a run is stopped after the index exists but before it is flagged, the next
    run flags it. (A migrate in that gap would drop the index; the build then simply starts again.)
  - Where the database is not MariaDB, it does nothing.

`status()` reports what is built, what is left, and when the next attempt is allowed.
"""

import hashlib
import json
import shutil
import time
from datetime import datetime

import frappe

from alaiy_os_connector_shopify.setup.install import ITEM_INDEXED_FIELDS

LOCK_NAME = "shopify_item_indexes"
STATE_KEY = "shopify_item_index_state"
JOB_TIMEOUT = 14400  # seconds; Frappe limits the statement to 1.5 times this
DEFAULT_LOCK_WAIT = 10
QUIET_AFTER_SECONDS = 30
SLOW_ATTEMPT_SECONDS = 60  # a lock timeout after this long cost real work, so it counts as a failure
BACKOFF_BASE_SECONDS = 3600
BACKOFF_MAX_SECONDS = 86400
MIN_FREE_BYTES = 2 * 1024**3
FREE_FRACTION = 0.10
MYSQL_LOCK_WAIT_TIMEOUT = 1205
LOCAL_HOSTS = (None, "", "localhost", "127.0.0.1", "::1")


# -- pure -----------------------------------------------------------------------------------

def next_missing(indexed_columns, present_columns, fields=ITEM_INDEXED_FIELDS):
    """The first of `fields` that is a column of Item and has no index, or None when none is left.

    A field that is not a column yet (the app is not provisioned) is not missing an index.
    """
    return next((f for f in fields if f in present_columns and f not in indexed_columns), None)


def is_lock_timeout(error):
    """Whether `error` is the database giving up waiting for a table lock."""
    return bool(getattr(error, "args", None)) and error.args[0] == MYSQL_LOCK_WAIT_TIMEOUT


def lock_wait_seconds(configured):
    """The table lock wait: the configured seconds kept between 1 and 60, else the default."""
    try:
        seconds = int(configured)
    except (TypeError, ValueError):
        return DEFAULT_LOCK_WAIT
    return min(60, max(1, seconds))


def in_window(minutes_now, window):
    """Whether `minutes_now` (minutes since midnight) is inside `window` ("HH:MM-HH:MM", which may wrap
    midnight). No window, or one that cannot be read, means any time."""
    try:
        start, end = (sum(int(p) * m for p, m in zip(part.strip().split(":"), (60, 1))) for part in window.split("-"))
    except (AttributeError, ValueError, TypeError):
        return True
    if start == end:
        return True
    return start <= minutes_now < end if start < end else (minutes_now >= start or minutes_now < end)


def backoff_seconds(failures):
    """How long to wait after `failures` failed attempts in a row: 1 hour, doubling, up to a day."""
    if failures < 1:
        return 0
    return min(BACKOFF_MAX_SECONDS, BACKOFF_BASE_SECONDS * 2 ** (failures - 1))


def enough_room(free_bytes, table_bytes):
    """Whether there is room for the index and its temporary files. Unknown free space is allowed."""
    if free_bytes is None:
        return True
    return free_bytes >= max(MIN_FREE_BYTES, FREE_FRACTION * (table_bytes or 0))


# -- database -------------------------------------------------------------------------------

def is_mariadb():
    return frappe.db.db_type == "mariadb"


def lock_name():
    """The run lock for this site. Database lock names are server-wide, so the site is part of it."""
    return f"{LOCK_NAME}:{hashlib.md5(str(frappe.local.site).encode()).hexdigest()[:16]}"


def indexed_columns():
    """The columns of Item that start an index."""
    rows = frappe.db.sql("SHOW INDEX FROM `tabItem`", as_dict=True)
    return {r["Column_name"] for r in rows if r["Seq_in_index"] == 1}


def present_columns():
    return {f for f in ITEM_INDEXED_FIELDS if frappe.db.has_column("Item", f)}


def item_table_busy():
    """Whether Item is in use in a way a build must not join: a query older than QUIET_AFTER_SECONDS, or a
    statement already waiting on Item's table lock (a migrate or another change), on another connection."""
    running = frappe.db.sql(
        """select count(*) from information_schema.processlist
           where id != connection_id() and info like %s
             and ((command = 'Query' and time > %s) or state like 'Waiting for table metadata lock%%')""",
        ("%tabItem%", QUIET_AFTER_SECONDS))
    return bool(running and running[0][0])


def table_bytes():
    rows = frappe.db.sql(
        """select coalesce(data_length, 0) + coalesce(index_length, 0) from information_schema.tables
           where table_schema = database() and table_name = 'tabItem'""")
    return int(rows[0][0]) if rows and rows[0][0] is not None else 0


def free_bytes():
    """Free space where the database keeps its data, or None when the database is not on this host or the
    path cannot be read."""
    if frappe.conf.get("db_host") not in LOCAL_HOSTS:
        return None
    try:
        return shutil.disk_usage(frappe.db.sql("select @@datadir")[0][0]).free
    except Exception:
        return None


def load_state():
    try:
        return json.loads(frappe.db.get_global(STATE_KEY) or "{}")
    except ValueError:
        return {}


def save_state(state):
    frappe.db.set_global(STATE_KEY, json.dumps(state))
    frappe.db.commit()  # nosemgrep: frapsec-manual-commit -- the state must survive this job


def record_failure(column, message):
    """Remember a failed attempt, delay the next one, and log it once."""
    failures = int(load_state().get("failures", 0)) + 1
    save_state({"failures": failures, "next_try_at": time.time() + backoff_seconds(failures),
                "last": f"{column}: {message}"[:300]})
    frappe.log_error(title="Shopify connector: Item index build failed", message=f"{column}: {message}")


def flag_built_indexes(indexed):
    """Flag the Custom Field of every index that exists, so Frappe keeps it through schema updates."""
    rows = frappe.get_all(
        "Custom Field", filters={"dt": "Item", "fieldname": ["in", list(ITEM_INDEXED_FIELDS)]},
        fields=["name", "fieldname", "search_index"])
    changed = False
    for row in rows:
        if row.get("fieldname") in indexed and not row.get("search_index"):
            frappe.db.set_value("Custom Field", row["name"], "search_index", 1, update_modified=False)
            changed = True
    if changed:
        frappe.db.commit()  # nosemgrep: frapsec-manual-commit -- one flag is its own unit of work
        frappe.clear_cache(doctype="Item")


def status():
    """What is built, what is left and when the next attempt is allowed."""
    indexed, present, state = indexed_columns(), present_columns(), load_state()
    return {
        "built": [f for f in ITEM_INDEXED_FIELDS if f in indexed],
        "missing": [f for f in ITEM_INDEXED_FIELDS if f in present and f not in indexed],
        "failures": int(state.get("failures", 0)),
        "next_try_at": state.get("next_try_at"),
        "last_failure": state.get("last"),
    }


def enqueue_build(after_commit=False):
    """Queue a build while an index is missing. Cheap when nothing is: one SHOW INDEX and no job.

    Runs hourly from the scheduler and once after every install and migrate. The install and migrate pass
    after_commit=True so the job starts only once the install's own changes are committed.
    """
    if not is_mariadb():
        return
    indexed = indexed_columns()
    flag_built_indexes(indexed)
    if next_missing(indexed, present_columns()) is None or frappe.conf.get("maintenance_mode"):
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.setup.item_indexes.build_next_item_index", queue="long", timeout=JOB_TIMEOUT,
        enqueue_after_commit=after_commit)


def _quietly(run):
    """Run cleanup that must not hide the error that is already being handled."""
    try:
        run()
    except Exception:
        pass


def build_next_item_index():
    """Build at most one missing Item index, when it is safe to. Returns what happened.

    Safe to call at any time and as often as wanted: a run that cannot start, cannot take the table lock,
    finds the table busy or finds nothing to do changes nothing.
    """
    if not is_mariadb():
        return "skipped: not MariaDB"
    if frappe.conf.get("maintenance_mode"):
        return "maintenance mode"
    if not frappe.db.sql("select get_lock(%s, 0)", lock_name())[0][0]:
        return "running"  # another run holds it; the database frees the lock if that run dies
    try:
        indexed = indexed_columns()
        flag_built_indexes(indexed)
        column = next_missing(indexed, present_columns())
        if column is None:
            if load_state():
                save_state({})
            return "done"

        state = load_state()
        if float(state.get("next_try_at") or 0) > time.time():
            return "backing off after a failure"
        now = datetime.now()
        if not in_window(now.hour * 60 + now.minute, frappe.conf.get("shopify_item_index_window")):
            return "outside the window"
        if item_table_busy():
            return "busy"
        if not enough_room(free_bytes(), table_bytes()):
            record_failure(column, "not enough free disk space for the index")
            return "not enough free disk space"

        previous = frappe.db.sql("select @@session.lock_wait_timeout")[0][0]
        frappe.db.sql("set session lock_wait_timeout = %s", lock_wait_seconds(frappe.conf.get("shopify_item_index_lock_wait")))
        started = time.monotonic()
        try:
            # The index is named after its column, as Frappe names the ones it builds itself.
            frappe.db.add_index("Item", [column], index_name=column)
        except Exception as error:
            _quietly(frappe.db.rollback)
            if is_lock_timeout(error) and time.monotonic() - started < SLOW_ATTEMPT_SECONDS:
                return "waiting for the table lock"  # nothing was lost; the next run tries again
            record_failure(column, str(error))
            return f"failed: {error}"
        finally:
            _quietly(lambda: frappe.db.sql("set session lock_wait_timeout = %s", previous))

        flag_built_indexes(indexed | {column})
        save_state({})
        frappe.logger("shopify").info(f"Item index built on {column}")
        return f"built {column}"
    finally:
        _quietly(lambda: frappe.db.sql("select release_lock(%s)", lock_name()))
