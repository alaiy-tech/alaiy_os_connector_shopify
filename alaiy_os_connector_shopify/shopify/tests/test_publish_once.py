"""Publishing a product must create at most one Shopify product.

Each queued push of a never-published product used to create its own copy on Shopify:
repeated Publish clicks, and the backlog of them that ran together once workers were
back, produced four copies of one product.

Two guards, tested here with a stand-in for `frappe` (no site, no Shopify):
  * publish_now queues one push per product, so a repeat while one is queued is dropped;
  * _push_product starts a fresh database snapshot once it holds the product lock, so a
    push that waited for the lock sees the id the push ahead of it saved.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from alaiy_os_connector_shopify.shopify.product import export


class Locked(Exception):
    pass


def _fake_frappe(calls):
    db = SimpleNamespace(
        commit=lambda: calls.append("commit"),
        set_value=lambda *a, **k: None,
    )
    return SimpleNamespace(
        has_permission=lambda *a, **k: True,
        enqueue=lambda method, **kwargs: calls.append(("enqueue", kwargs)),
        db=db,
        DocumentLockedError=Locked,
        _=lambda s: s,
    )


class TestPublishQueuesOnce(unittest.TestCase):
    def test_a_repeat_while_one_is_queued_is_dropped(self):
        calls = []
        listing = SimpleNamespace(name="P1", sh_shopify_product_id=None)
        with patch.object(export, "frappe", _fake_frappe(calls)), patch(
            "alaiy_os_connector_shopify.shopify.product.listing.ensure_listing", return_value=listing
        ):
            export.publish_now("P1")
        kwargs = next(c[1] for c in calls if isinstance(c, tuple) and c[0] == "enqueue")
        self.assertTrue(kwargs["deduplicate"])
        self.assertEqual(kwargs["job_id"], "shopify_publish::P1")
        self.assertTrue(kwargs["force"])

    def test_each_product_has_its_own_job_id(self):
        calls = []
        listing = SimpleNamespace(name="x", sh_shopify_product_id=None)
        with patch.object(export, "frappe", _fake_frappe(calls)), patch(
            "alaiy_os_connector_shopify.shopify.product.listing.ensure_listing", return_value=listing
        ):
            export.publish_now("A")
            export.publish_now("B")
        ids = [c[1]["job_id"] for c in calls if isinstance(c, tuple)]
        self.assertEqual(len(set(ids)), 2)


class TestPushStartsFromFreshData(unittest.TestCase):
    def _push(self, lock_error=None):
        calls = []
        item = SimpleNamespace(
            name="P1",
            lock=lambda timeout=None: (_ for _ in ()).throw(lock_error) if lock_error else None,
            unlock=lambda: calls.append("unlock"),
        )
        with patch.object(export, "frappe", _fake_frappe(calls)), patch.object(
            export, "_push_product_unlocked", lambda i: calls.append("push")
        ):
            export._push_product(item)
        return calls

    def test_a_fresh_snapshot_is_taken_before_the_push_reads_anything(self):
        self.assertEqual(self._push(), ["commit", "push", "unlock"])

    def test_a_push_that_loses_the_lock_does_nothing(self):
        self.assertEqual(self._push(lock_error=Locked()), [])


if __name__ == "__main__":
    unittest.main()
