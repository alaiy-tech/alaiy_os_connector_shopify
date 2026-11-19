"""The Item indexes are built in the background, one at a time, only when it is safe.

The build must never queue Item queries behind a table lock, must add at most one index per run, must
change nothing when it cannot start, must not repeat a failing build every hour, and must leave nothing
stuck when a run dies. No site: the database is a stand-in that answers the SQL the build issues.
Stdlib unittest.
"""

import importlib
import itertools
import sys
import types
import unittest
from datetime import datetime
from unittest import mock

MODULE = "alaiy_os_connector_shopify.setup.item_indexes"
FIELDS = ("sh_shopify_product_id", "sh_shopify_variant_id", "sh_shopify_inventory_item_id", "sh_shopify_connection")
GIB = 1024**3


class Db:
    """Answers the statements the build issues and records the ones that change something."""

    def __init__(self, indexed=(), present=FIELDS, busy=0, lock=1, flagged=FIELDS, state=None, table=1 * GIB):
        self.db_type = "mariadb"
        self.indexed, self.present, self.busy, self.lock = set(indexed), set(present), busy, lock
        self.flagged, self.table = set(flagged), table
        self.sessions, self.released = [], 0
        self.globals = {"shopify_item_index_state": state} if state is not None else {}
        self.add_index = mock.Mock()
        self.set_value = mock.Mock()
        self.commit = mock.Mock()
        self.rollback = mock.Mock()
        self.saved = []

    def sql(self, query, params=None, as_dict=False):
        q = " ".join(query.split())
        if "get_lock" in q:
            return [[self.lock]]
        if "release_lock" in q:
            self.released += 1
            return [[1]]
        if q.startswith("SHOW INDEX"):
            return [{"Column_name": c, "Seq_in_index": 1} for c in sorted(self.indexed)]
        if "information_schema.processlist" in q:
            return [[self.busy]]
        if "information_schema.tables" in q:
            return [[self.table]]
        if "@@datadir" in q:
            return [["/var/lib/mysql/"]]
        if "@@session.lock_wait_timeout" in q:
            return [[50]]
        if q.startswith("set session lock_wait_timeout"):
            self.sessions.append(params)
            return []
        raise AssertionError(q)

    def has_column(self, doctype, column):
        return column in self.present

    def get_global(self, key):
        return self.globals.get(key)

    def set_global(self, key, value):
        self.globals[key] = value
        self.saved.append(value)


class Base(unittest.TestCase):
    def load(self, db, conf=None, custom_fields=None):
        frappe = types.ModuleType("frappe")
        frappe.db = db
        frappe.conf = dict(conf or {})
        frappe.local = types.SimpleNamespace(site="site1.example")
        frappe.clear_cache = mock.Mock()
        frappe.logger = mock.Mock()
        frappe.enqueue = mock.Mock()
        frappe.log_error = mock.Mock()
        rows = custom_fields if custom_fields is not None else [
            {"name": f"Item-{f}", "fieldname": f, "search_index": 1 if f in db.flagged else 0} for f in FIELDS]
        frappe.get_all = mock.Mock(return_value=rows)
        patcher = mock.patch.dict(sys.modules, {"frappe": frappe})
        patcher.start()
        sys.modules.pop(MODULE, None)
        self.addCleanup(patcher.stop)
        self.addCleanup(sys.modules.pop, MODULE, None)
        return frappe, importlib.import_module(MODULE)

    def build(self, db, **kw):
        frappe, mod = self.load(db, **kw)
        return mod.build_next_item_index(), frappe, mod


class TestPure(Base):
    def setUp(self):
        _f, self.mod = self.load(Db())

    def test_the_first_unindexed_present_field_is_next(self):
        self.assertEqual(self.mod.next_missing({"sh_shopify_product_id"}, set(FIELDS)), "sh_shopify_variant_id")

    def test_a_field_that_is_not_a_column_yet_is_not_missing_an_index(self):
        self.assertIsNone(self.mod.next_missing(set(), set()))

    def test_nothing_is_next_when_all_four_exist(self):
        self.assertIsNone(self.mod.next_missing(set(FIELDS), set(FIELDS)))

    def test_only_a_lock_wait_timeout_counts_as_the_lock_being_busy(self):
        self.assertTrue(self.mod.is_lock_timeout(Exception(1205, "Lock wait timeout exceeded")))
        self.assertFalse(self.mod.is_lock_timeout(Exception(1054, "Unknown column")))
        self.assertFalse(self.mod.is_lock_timeout(Exception()))

    def test_the_lock_wait_is_kept_between_1_and_60_and_defaults_when_unreadable(self):
        for given, want in ((None, 10), ("abc", 10), (0, 1), (500, 60), ("20", 20), (7, 7)):
            self.assertEqual(self.mod.lock_wait_seconds(given), want, given)

    def test_the_window_may_wrap_midnight_and_an_unreadable_one_means_any_time(self):
        w = self.mod.in_window
        self.assertTrue(w(720, None) and w(720, "") and w(720, "nonsense") and w(720, "01:00-01:00"))
        self.assertTrue(w(120, "01:00-05:00"))
        self.assertFalse(w(360, "01:00-05:00") or w(300, "01:00-05:00"))
        self.assertTrue(w(1380, "22:00-06:00") and w(120, "22:00-06:00"))
        self.assertFalse(w(720, "22:00-06:00"))

    def test_the_wait_after_a_failure_doubles_up_to_a_day(self):
        b = self.mod.backoff_seconds
        self.assertEqual([b(0), b(1), b(2), b(3)], [0, 3600, 7200, 14400])
        self.assertEqual((b(10), b(40)), (86400, 86400))

    def test_room_is_a_floor_or_a_tenth_of_the_table_and_unknown_space_is_allowed(self):
        room = self.mod.enough_room
        self.assertTrue(room(None, 10**12))
        self.assertFalse(room(1 * GIB, 0))
        self.assertTrue(room(2 * GIB, 0))
        self.assertFalse(room(9 * GIB, 100 * GIB))
        self.assertTrue(room(10 * GIB, 100 * GIB))


class TestBuild(Base):
    def test_it_adds_one_index_flags_its_field_and_restores_the_lock_wait(self):
        db = Db(indexed={"sh_shopify_product_id"}, flagged={"sh_shopify_product_id"})
        result, _frappe, _mod = self.build(db)
        self.assertEqual(result, "built sh_shopify_variant_id")
        db.add_index.assert_called_once_with("Item", ["sh_shopify_variant_id"], index_name="sh_shopify_variant_id")
        db.set_value.assert_any_call("Custom Field", "Item-sh_shopify_variant_id", "search_index", 1, update_modified=False)
        self.assertEqual(db.sessions, [10, 50])
        self.assertEqual(db.released, 1)
        self.assertEqual(db.saved[-1], "{}")  # a success clears the failure state

    def test_it_does_nothing_once_all_four_exist(self):
        db = Db(indexed=set(FIELDS))
        self.assertEqual(self.build(db)[0], "done")
        db.add_index.assert_not_called()
        self.assertEqual(db.released, 1)

    def test_an_index_that_exists_but_was_never_flagged_is_flagged_even_with_nothing_to_build(self):
        db = Db(indexed=set(FIELDS), flagged=set())
        self.assertEqual(self.build(db)[0], "done")
        self.assertEqual(db.set_value.call_count, 4)

    def test_it_does_not_start_while_a_long_query_or_a_waiting_statement_holds_the_table(self):
        db = Db(busy=1)
        self.assertEqual(self.build(db)[0], "busy")
        db.add_index.assert_not_called()
        self.assertEqual(db.sessions, [])

    def test_it_does_not_start_in_maintenance_mode_and_does_not_even_take_the_lock(self):
        db = Db()
        db.sql = mock.Mock(side_effect=AssertionError("no query expected"))
        self.assertEqual(self.build(db, conf={"maintenance_mode": 1})[0], "maintenance mode")

    def test_it_does_nothing_when_another_run_holds_the_lock(self):
        db = Db(lock=0)
        self.assertEqual(self.build(db)[0], "running")
        db.add_index.assert_not_called()
        self.assertEqual(db.released, 0)

    def test_it_does_nothing_where_the_database_is_not_mariadb(self):
        db = Db()
        db.db_type = "postgres"
        db.sql = mock.Mock(side_effect=AssertionError("no query expected"))
        self.assertEqual(self.build(db)[0], "skipped: not MariaDB")

    def test_it_waits_out_a_recorded_failure(self):
        db = Db(state='{"failures": 1, "next_try_at": 9999999999}')
        self.assertEqual(self.build(db)[0], "backing off after a failure")
        db.add_index.assert_not_called()

    def test_it_stays_inside_the_configured_window(self):
        frappe, mod = self.load(Db(), conf={"shopify_item_index_window": "01:00-05:00"})
        with mock.patch.object(mod, "datetime") as clock:
            clock.now.return_value = datetime(2026, 11, 19, 12, 0)
            self.assertEqual(mod.build_next_item_index(), "outside the window")
        frappe.db.add_index.assert_not_called()

    def test_it_does_not_start_without_free_disk_space_and_records_it_once(self):
        db = Db()
        frappe, mod = self.load(db)
        with mock.patch.object(mod.shutil, "disk_usage", return_value=types.SimpleNamespace(free=1 * GIB)):
            self.assertEqual(mod.build_next_item_index(), "not enough free disk space")
        db.add_index.assert_not_called()
        frappe.log_error.assert_called_once()
        self.assertEqual(mod.status()["failures"], 1)

    def test_free_space_is_not_checked_when_the_database_is_on_another_host(self):
        db = Db()
        frappe, mod = self.load(db, conf={"db_host": "db.internal"})
        self.assertIsNone(mod.free_bytes())

    def test_a_table_lock_that_is_not_free_changes_nothing_and_restores_the_wait(self):
        db = Db()
        db.add_index.side_effect = Exception(1205, "Lock wait timeout exceeded")
        result, frappe, _mod = self.build(db)
        self.assertEqual(result, "waiting for the table lock")
        db.set_value.assert_not_called()
        frappe.log_error.assert_not_called()
        self.assertEqual(db.sessions, [10, 50])
        self.assertEqual(db.released, 1)
        db.rollback.assert_called()

    def test_a_lock_lost_after_a_long_build_counts_as_a_failure_and_is_delayed(self):
        db = Db()
        db.add_index.side_effect = Exception(1205, "Lock wait timeout exceeded")
        frappe, mod = self.load(db)
        with mock.patch.object(mod.time, "monotonic", side_effect=itertools.chain([0], itertools.repeat(600))):
            result = mod.build_next_item_index()
        self.assertTrue(result.startswith("failed:"))
        frappe.log_error.assert_called_once()
        status = mod.status()
        self.assertEqual(status["failures"], 1)
        self.assertGreater(status["next_try_at"], 0)

    def test_any_other_error_is_recorded_not_raised_and_leaves_nothing_stuck(self):
        db = Db()
        db.add_index.side_effect = Exception(1114, "The table is full")
        result, frappe, _mod = self.build(db)
        self.assertTrue(result.startswith("failed:"))
        frappe.log_error.assert_called_once()
        self.assertEqual(db.released, 1)
        self.assertEqual(db.sessions, [10, 50])
        db.set_value.assert_not_called()

    def test_a_second_failure_waits_twice_as_long(self):
        db = Db(state='{"failures": 1, "next_try_at": 0}')
        db.add_index.side_effect = Exception(1114, "The table is full")
        frappe, mod = self.load(db)
        mod.build_next_item_index()
        self.assertEqual(mod.status()["failures"], 2)

    def test_the_lock_wait_follows_the_site_config(self):
        db = Db()
        self.build(db, conf={"shopify_item_index_lock_wait": 3})
        self.assertEqual(db.sessions, [3, 50])


class TestEnqueue(Base):
    def test_nothing_is_queued_when_no_index_is_missing(self):
        frappe, mod = self.load(Db(indexed=set(FIELDS)))
        mod.enqueue_build()
        frappe.enqueue.assert_not_called()

    def test_a_missing_index_queues_a_build_on_the_long_queue_with_a_timeout(self):
        frappe, mod = self.load(Db())
        mod.enqueue_build()
        frappe.enqueue.assert_called_once()
        kwargs = frappe.enqueue.call_args.kwargs
        self.assertEqual((kwargs["queue"], kwargs["timeout"]), ("long", mod.JOB_TIMEOUT))
        self.assertNotIn("job_id", kwargs)  # a crashed run must not block the next one
        self.assertFalse(kwargs["enqueue_after_commit"])

    def test_an_install_or_migrate_queues_the_build_only_after_its_own_commit(self):
        frappe, mod = self.load(Db())
        mod.enqueue_build(after_commit=True)
        self.assertTrue(frappe.enqueue.call_args.kwargs["enqueue_after_commit"])

    def test_nothing_is_queued_in_maintenance_mode_or_off_mariadb(self):
        frappe, mod = self.load(Db(), conf={"maintenance_mode": 1})
        mod.enqueue_build()
        frappe.enqueue.assert_not_called()
        db = Db()
        db.db_type = "postgres"
        frappe, mod = self.load(db)
        mod.enqueue_build()
        frappe.enqueue.assert_not_called()

    def test_queueing_also_flags_an_index_that_was_built_but_not_flagged(self):
        db = Db(indexed={"sh_shopify_product_id"}, flagged=set())
        frappe, mod = self.load(db)
        mod.enqueue_build()
        db.set_value.assert_called_once_with("Custom Field", "Item-sh_shopify_product_id", "search_index", 1, update_modified=False)

    def test_status_lists_what_is_built_what_is_left_and_the_last_failure(self):
        frappe, mod = self.load(Db(indexed={"sh_shopify_product_id"}, state='{"failures": 2, "next_try_at": 5, "last": "x: full"}'))
        self.assertEqual(mod.status(), {"built": ["sh_shopify_product_id"],
            "missing": ["sh_shopify_variant_id", "sh_shopify_inventory_item_id", "sh_shopify_connection"],
            "failures": 2, "next_try_at": 5, "last_failure": "x: full"})


if __name__ == "__main__":
    unittest.main()
