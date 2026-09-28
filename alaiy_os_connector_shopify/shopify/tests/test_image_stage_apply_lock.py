"""_apply_locked serializes photo jobs writing the same product's enriched
listing, so a paid-for render always has somewhere to land.

Confirmed live on 2026-09-28, item 13A419-5001: three per-photo jobs for the
same product landed close enough together that one job's already-rendered
image never made it onto any row it could be found by again. _apply's own
retry-on-conflict only protected the document's save, not what happened
around it. _apply_locked takes a document lock around the load-modify-save
step so only one photo job for a given product can be mid-save at a time,
while the slow render itself still runs fully in parallel across workers.

`frappe.db` is a thread-local proxy that raises "object is not bound" the
moment anything (even mock.patch's own introspection) touches it outside a
real request/job context, so these tests replace the whole `frappe` name
inside image_stage with a lightweight stand-in instead of patching
`frappe.db` in place -- see _fake_frappe. The real exception classes are
kept on it so `except frappe.DocumentLockedError` inside the module under
test still matches what these tests raise.

Run with:  bench --site <site> run-tests --module \
    alaiy_os_connector_shopify.shopify.tests.test_image_stage_apply_lock
"""

import unittest
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, patch

import frappe

from alaiy_os_connector_shopify.listing import image_stage


def _fake_frappe(exists=True):
    fake = SimpleNamespace(
        DocumentLockedError=frappe.DocumentLockedError,
        DoesNotExistError=frappe.DoesNotExistError,
        get_doc=MagicMock(),
        db=SimpleNamespace(exists=MagicMock(return_value=exists)),
        log_error=MagicMock(),
    )
    return fake


class TestApplyLocked(unittest.TestCase):
    def test_missing_doc_returns_none_without_locking(self):
        fake = _fake_frappe()
        fake.get_doc.side_effect = frappe.DoesNotExistError
        with patch.object(image_stage, "frappe", fake):
            result = image_stage._apply_locked("ITEM", [])
        self.assertIsNone(result)

    def test_lock_acquired_and_released_around_apply(self):
        doc = MagicMock()
        fake = _fake_frappe(exists=True)
        fake.get_doc.return_value = doc
        with patch.object(image_stage, "frappe", fake), \
             patch.object(image_stage, "_apply", return_value=2) as apply_mock:
            result = image_stage._apply_locked("ITEM", [{"source_url": "x"}])

        self.assertEqual(result, 2)
        doc.lock.assert_called_once_with(timeout=image_stage._APPLY_LOCK_TIMEOUT_SECONDS)
        doc.unlock.assert_called_once()
        apply_mock.assert_called_once_with("ITEM", [{"source_url": "x"}])

    def test_listing_deleted_between_lock_and_write_returns_none_and_still_unlocks(self):
        doc = MagicMock()
        fake = _fake_frappe(exists=False)
        fake.get_doc.return_value = doc
        with patch.object(image_stage, "frappe", fake), \
             patch.object(image_stage, "_apply") as apply_mock:
            result = image_stage._apply_locked("ITEM", [])

        self.assertIsNone(result)
        doc.unlock.assert_called_once()
        apply_mock.assert_not_called()

    def test_lock_timeout_logs_and_raises_without_unlocking(self):
        doc = MagicMock()
        doc.lock.side_effect = frappe.DocumentLockedError
        fake = _fake_frappe()
        fake.get_doc.return_value = doc
        with patch.object(image_stage, "frappe", fake):
            with self.assertRaises(frappe.DocumentLockedError):
                image_stage._apply_locked("ITEM", [])

        fake.log_error.assert_called_once()
        # Never acquired, so there is nothing to release -- unlocking an
        # unheld lock would release a DIFFERENT job's still-active one.
        doc.unlock.assert_not_called()

    def test_apply_exception_still_unlocks(self):
        doc = MagicMock()
        fake = _fake_frappe(exists=True)
        fake.get_doc.return_value = doc
        with patch.object(image_stage, "frappe", fake), \
             patch.object(image_stage, "_apply", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                image_stage._apply_locked("ITEM", [])

        doc.unlock.assert_called_once()


class TestRunStepLockHandling(unittest.TestCase):
    """run_step must never crash on a lock timeout -- a crash skips
    _nudge_batches and can leave a bulk batch waiting forever (see
    _nudge_batches's own docstring)."""

    def test_lock_timeout_reports_failed_and_still_nudges_batches(self):
        fake = _fake_frappe(exists=True)
        with patch.object(image_stage, "frappe", fake), \
             patch.object(image_stage, "_set_state") as set_state, \
             patch.object(image_stage, "_publish") as publish, \
             patch.object(image_stage, "_nudge_batches") as nudge, \
             patch.object(image_stage, "_render", return_value={"images": [{"url": "x"}], "image_tokens": 0}), \
             patch.object(image_stage, "_apply_locked", side_effect=frappe.DocumentLockedError):
            image_stage.run_step("ITEM", image_stage.GENERATE, {})

        set_state.assert_called_with("ITEM", "Failed", ANY)
        publish.assert_called_once_with("ITEM", "Failed")
        nudge.assert_called_once_with("ITEM")

    def test_listing_deleted_mid_render_logs_and_nudges_without_crashing(self):
        fake = _fake_frappe(exists=True)
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
