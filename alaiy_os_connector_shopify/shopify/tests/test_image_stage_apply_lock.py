"""_apply_locked serializes photo jobs writing the same product's enriched
listing, so a paid-for render always has somewhere to land.

Confirmed live on 2026-09-28, item 13A419-5001: three per-photo jobs for the
same product landed close enough together that one job's already-rendered
image never made it onto any row it could be found by again. The fix locks
the listing's database row around each load-modify-save.

The first version of that fix used Document.lock(), and every photo job then
failed on its own save: Document.save() refuses to run while a lock file
exists for the document, whoever holds it (live 2026-09-28/29, reported as
"Timed out waiting for another photo job..."). These tests pin the row lock
in its place and check the document's own lock is never touched.

`frappe.db` is a thread-local proxy that raises "object is not bound" the
moment anything (even mock.patch's own introspection) touches it outside a
real request/job context, so these tests replace the whole `frappe` name
inside image_stage with a lightweight stand-in instead of patching
`frappe.db` in place -- see _fake_frappe. The real exception classes are
kept on it so `except frappe.QueryTimeoutError` inside the module under
test still matches what these tests raise.

Run with:  bench --site <site> run-tests --module \
    alaiy_os_connector_shopify.shopify.tests.test_image_stage_apply_lock
"""

import unittest
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, call, patch

import frappe

from alaiy_os_connector_shopify.listing import image_stage


def _fake_frappe(row_exists=True):
    events = MagicMock()
    fake = SimpleNamespace(
        QueryTimeoutError=frappe.QueryTimeoutError,
        TimestampMismatchError=frappe.TimestampMismatchError,
        DoesNotExistError=frappe.DoesNotExistError,
        get_doc=events.get_doc,
        db=SimpleNamespace(
            exists=MagicMock(return_value=True),
            sql=events.sql,
            commit=events.commit,
            rollback=events.rollback,
        ),
        log_error=MagicMock(),
    )
    fake.db.sql.return_value = [("ITEM",)] if row_exists else []
    return fake, events


class TestApplyLocked(unittest.TestCase):
    def test_commits_render_before_applying(self):
        fake, events = _fake_frappe()
        with patch.object(image_stage, "frappe", fake), \
             patch.object(image_stage, "_apply", return_value=2) as apply_mock:
            events.attach_mock(apply_mock, "apply")
            result = image_stage._apply_locked("ITEM", [{"source_url": "x"}])

        self.assertEqual(result, 2)
        self.assertEqual(
            events.mock_calls[:2],
            [call.commit(), call.apply("ITEM", [{"source_url": "x"}])],
        )

    def test_lock_wait_timeout_rolls_back_and_retries(self):
        fake, _ = _fake_frappe()
        with patch.object(image_stage, "frappe", fake), \
             patch.object(image_stage, "_apply",
                          side_effect=[frappe.QueryTimeoutError, 1]) as apply_mock:
            result = image_stage._apply_locked("ITEM", [])

        self.assertEqual(result, 1)
        self.assertEqual(apply_mock.call_count, 2)
        fake.db.rollback.assert_called_once()
        fake.log_error.assert_not_called()

    def test_every_attempt_timing_out_logs_once_and_raises(self):
        fake, _ = _fake_frappe()
        with patch.object(image_stage, "frappe", fake), \
             patch.object(image_stage, "_apply",
                          side_effect=frappe.QueryTimeoutError) as apply_mock:
            with self.assertRaises(frappe.QueryTimeoutError):
                image_stage._apply_locked("ITEM", [])

        self.assertEqual(apply_mock.call_count, image_stage._APPLY_LOCK_ATTEMPTS)
        fake.log_error.assert_called_once()

    def test_listing_gone_returns_none(self):
        fake, _ = _fake_frappe()
        with patch.object(image_stage, "frappe", fake), \
             patch.object(image_stage, "_apply", return_value=None):
            self.assertIsNone(image_stage._apply_locked("ITEM", []))


class TestApplyOnceRowLock(unittest.TestCase):
    def test_row_locked_before_loading_and_document_lock_never_used(self):
        fake, events = _fake_frappe()
        doc = MagicMock(images=[])
        events.get_doc.return_value = doc
        with patch.object(image_stage, "frappe", fake):
            produced = image_stage._apply_once("ITEM", [{"url": "u", "source_url": "s"}])

        self.assertEqual(produced, 1)
        names = [c[0] for c in events.mock_calls]
        self.assertLess(names.index("sql"), names.index("get_doc"))
        self.assertIn("for update", events.sql.call_args[0][0])
        doc.save.assert_called_once()
        # Document.lock() makes the holder's own save() raise DocumentLockedError.
        doc.lock.assert_not_called()

    def test_missing_row_returns_none_without_loading(self):
        fake, events = _fake_frappe(row_exists=False)
        with patch.object(image_stage, "frappe", fake):
            self.assertIsNone(image_stage._apply_once("ITEM", [{"url": "u"}]))
        events.get_doc.assert_not_called()


class TestRunStepLockHandling(unittest.TestCase):
    """run_step must never crash on a lock timeout -- a crash skips
    _nudge_batches and can leave a bulk batch waiting forever (see
    _nudge_batches's own docstring)."""

    def test_lock_timeout_reports_failed_and_still_nudges_batches(self):
        fake, _ = _fake_frappe()
        with patch.object(image_stage, "frappe", fake), \
             patch.object(image_stage, "_set_state") as set_state, \
             patch.object(image_stage, "_publish") as publish, \
             patch.object(image_stage, "_nudge_batches") as nudge, \
             patch.object(image_stage, "_render", return_value={"images": [{"url": "x"}], "image_tokens": 0}), \
             patch.object(image_stage, "_apply_locked", side_effect=frappe.QueryTimeoutError):
            image_stage.run_step("ITEM", image_stage.GENERATE, {})

        set_state.assert_called_with("ITEM", "Failed", ANY)
        publish.assert_called_once_with("ITEM", "Failed")
        nudge.assert_called_once_with("ITEM")

    def test_listing_deleted_mid_render_logs_and_nudges_without_crashing(self):
        fake, _ = _fake_frappe()
        with patch.object(image_stage, "frappe", fake), \
             patch.object(image_stage, "_set_state") as set_state, \
             patch.object(image_stage, "_publish") as publish, \
             patch.object(image_stage, "_nudge_batches") as nudge, \
             patch.object(image_stage, "_render", return_value={"images": [{"url": "x"}], "image_tokens": 0}), \
             patch.object(image_stage, "_apply_locked", return_value=None):
            image_stage.run_step("ITEM", image_stage.GENERATE, {})

        fake.log_error.assert_called_once()
        publish.assert_not_called()
        nudge.assert_called_once_with("ITEM")


if __name__ == "__main__":
    unittest.main()
