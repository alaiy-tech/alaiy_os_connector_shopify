"""
Order locks are per store, and always released under the name they took.

The lock serialises a real race -- our own outbound push against the echoed
orders/updated webhook Shopify sends back for it -- so it has to keep working
exactly as it did. What changes is only the name: a Shopify order id is unique
inside one shop, so two sellers' unrelated order 1001s used to wait on each
other.

The failure mode to guard against is not "no lock" but "two names": if acquire
and release disagree, the lock is never released and every later order in that
store waits the full timeout.
"""

import sys
import types
import unittest


def _load():
    frappe = types.ModuleType("frappe")
    frappe.db = types.SimpleNamespace(sql=lambda *a, **k: [[1]])
    sys.modules["frappe"] = frappe
    for mod in list(sys.modules):
        if mod.startswith("alaiy_os_connector_shopify"):
            del sys.modules[mod]
    from alaiy_os_connector_shopify.shopify.order import locking
    return locking


class TestNamesAreStoreScoped(unittest.TestCase):
    def test_two_stores_do_not_share_a_lock(self):
        lock = _load()
        self.assertNotEqual(lock._lock_name("1001", "seller-a"),
                            lock._lock_name("1001", "seller-b"))

    def test_the_same_order_in_the_same_store_is_one_lock(self):
        # The whole point: this pair must still serialise.
        lock = _load()
        self.assertEqual(lock._lock_name("1001", "seller-a"),
                         lock._lock_name("1001", "seller-a"))

    def test_a_document_and_its_name_agree(self):
        # Callers pass either. If these differed, acquire and release could
        # take different names and the lock would leak.
        lock = _load()
        self.assertEqual(lock._lock_name("1001", types.SimpleNamespace(name="seller-a")),
                         lock._lock_name("1001", "seller-a"))

    def test_no_connection_keeps_the_old_name(self):
        lock = _load()
        self.assertEqual(lock._lock_name("1001"), "shopify_order_1001")


class TestMySQLNameLimit(unittest.TestCase):
    def test_a_long_store_id_is_hashed_not_truncated(self):
        # MySQL truncates a lock name past 64 characters, and two names that
        # truncate to the same thing are silently the SAME lock -- which would
        # reintroduce cross-store blocking exactly where it is least expected.
        lock = _load()
        name = lock._lock_name("1001", "x" * 80)
        self.assertLessEqual(len(name), 64)

    def test_two_long_store_ids_still_differ(self):
        lock = _load()
        self.assertNotEqual(lock._lock_name("1001", "x" * 80),
                            lock._lock_name("1001", "y" * 80))


class TestAcquireAndReleaseAgree(unittest.TestCase):
    def test_release_uses_the_name_acquire_took(self):
        lock = _load()
        taken = []
        lock.frappe.db.sql = lambda q, args: (taken.append(args[0]), [[1]])[1]
        lock._acquire_order_lock("1001", connection="seller-a")
        lock._release_order_lock("1001", "seller-a")
        self.assertEqual(len(taken), 2)
        self.assertEqual(taken[0], taken[1], "lock would never be released")


if __name__ == "__main__":
    unittest.main()
