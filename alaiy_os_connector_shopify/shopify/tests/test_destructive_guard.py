"""
The bulk deletes refuse to cross a store boundary.

`_wipe_all_items` and `clear_orders` both select by "the Shopify id is set",
which on a bench with two sellers means both sellers' rows. Neither can be
narrowed yet -- the rows carry nothing saying which store they came from --
so the guard refuses instead.

These pin the refusal itself: one store runs, several stores refuse, and the
explicit acknowledgement gets through. A frappe stub stands in for the DB so
the decision can be exercised without a site.
"""

import sys
import types
import unittest


def _install_frappe_stub():
    frappe = types.ModuleType("frappe")

    class ValidationError(Exception):
        pass

    def throw(msg, exc=None, **kwargs):
        raise (exc or ValidationError)(msg)

    frappe.ValidationError = ValidationError
    frappe.throw = throw
    frappe._ = lambda s: s
    frappe.db = types.SimpleNamespace(exists=lambda *a, **k: True)
    frappe.get_all = lambda *a, **k: []
    sys.modules["frappe"] = frappe
    return frappe


def _load(store_names):
    """Reload the guard against a bench holding exactly these connections."""
    _install_frappe_stub()
    for mod in list(sys.modules):
        if mod.startswith("alaiy_os_connector_shopify"):
            del sys.modules[mod]
    from alaiy_os_connector_shopify.shopify import destructive
    destructive.connections = types.SimpleNamespace(
        names=lambda: list(store_names))
    return destructive


class TestSingleStoreStillRuns(unittest.TestCase):
    def test_one_connection_is_allowed(self):
        # Every existing single-store bench. The guard must be invisible
        # there -- it is not a behaviour change for them.
        d = _load(["default"])
        d.assert_safe("Import Products")  # must not raise

    def test_no_connection_is_allowed(self):
        # A bench mid-install has no connection row yet. Nothing to cross.
        d = _load([])
        d.assert_safe("Import Products")


class TestMultiStoreRefuses(unittest.TestCase):
    def test_two_connections_refuse(self):
        d = _load(["seller-a", "seller-b"])
        with self.assertRaises(d.CrossStoreDeletion):
            d.assert_safe("Import Products")

    def test_the_refusal_names_the_operation_and_the_stores(self):
        # Whoever hits this is at a bench console; the message is the only
        # thing telling them which command stopped and what it would have hit.
        d = _load(["seller-a", "seller-b"])
        with self.assertRaises(d.CrossStoreDeletion) as caught:
            d.assert_safe("clear_orders")
        message = str(caught.exception)
        self.assertIn("clear_orders", message)
        self.assertIn("seller-a", message)
        self.assertIn("seller-b", message)

    def test_explicit_acknowledgement_gets_through(self):
        # The operator who genuinely means "every store on this bench".
        d = _load(["seller-a", "seller-b"])
        d.assert_safe("clear_orders", ack_multi_store=True)


if __name__ == "__main__":
    unittest.main()
