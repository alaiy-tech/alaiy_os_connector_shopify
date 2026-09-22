"""
_update_order's handling of an order Shopify has cancelled.

An order cancelled on Shopify AFTER we imported it used to stay open here
forever. The dedicated orders/cancelled path is the only one that ever
cancelled anything, and it does nothing when the cancel predates the Sales
Order -- an order re-imported later (a catalogue reimport, say) never sees
that webhook. Every later orders/updated then read only financial_status and
fulfillment_status, so the cancel was invisible: the order stayed "To Deliver
and Bill", unfulfilled, and aged past its SLA on the dashboard against an
order Shopify shows as Cancelled and Refunded.

These pin the guard only -- that a cancelled payload cancels and stops, and
that a live one is untouched. The cascade through a linked invoice lives in
_cancel_sales_order and needs a real bench.
"""

import sys
import types
import unittest


def _load(docstatus=1, so_name="SAL-ORD-0001"):
    """_update_order with frappe stubbed, plus a record of what it did."""
    calls = {"cancelled": [], "line_items": [], "set_values": []}

    frappe = types.ModuleType("frappe")

    class _DB:
        def get_value(self, doctype, name, field):
            return docstatus

        def set_value(self, doctype, name, field, value):
            calls["set_values"].append((field, value))

        def commit(self):
            pass

    frappe.db = _DB()
    frappe.log_error = lambda **kw: None
    frappe.logger = lambda: types.SimpleNamespace(info=lambda *a, **k: None)
    sys.modules["frappe"] = frappe


    def _stub(path, **attrs):
        mod = types.ModuleType(path)
        for key, value in attrs.items():
            setattr(mod, key, value)
        sys.modules[path] = mod
        return mod

    base = "alaiy_os_connector_shopify.shopify.order."
    _stub(base + "locking",
          _acquire_order_lock=lambda *a, **k: True,
          _release_order_lock=lambda *a, **k: None)
    _stub(base + "upsert",
          get_active_sales_order=lambda oid: so_name,
          _upsert_order_unlocked=lambda *a, **k: None)
    _stub(base + "line_items",
          _sync_order_line_items=lambda n, o: calls["line_items"].append(n))
    _stub(base + "delivery_notes",
          _create_delivery_note_if_needed=lambda *a, **k: None,
          _sync_fulfillments=lambda *a, **k: None,
          _sync_tracking=lambda *a, **k: None)
    _stub(base + "webhook",
          _cancel_sales_order=lambda n: calls["cancelled"].append(n))
    _stub(base + "invoice",
          create_sales_invoice_if_paid=lambda *a, **k: None)
    _stub(base + "push",
          parse_tags=lambda t: [],
          strip_status_tag=lambda t: [])

    for name in list(sys.modules):
        if name.endswith(".order.update"):
            del sys.modules[name]
    # _update_order is only the per-order lock wrapper; the logic under
    # test lives in the unlocked half, which is also what the lock path
    # calls straight through to.
    from alaiy_os_connector_shopify.shopify.order.update import _update_order_unlocked
    return _update_order_unlocked, calls


LIVE = {"financial_status": "paid", "fulfillment_status": ""}
# Refunded in full with the line items removed, never formally cancelled:
# cancelled_at is null, and the order is finished all the same.
REFUNDED = {"financial_status": "refunded", "fulfillment_status": ""}
PARTIAL = {"financial_status": "partially_refunded", "fulfillment_status": "",
           "line_items": [{"quantity": 1, "current_quantity": 1},
                          {"quantity": 2, "current_quantity": 0}]}
# TS26012's real shape: refunded line by line until nothing was left, so the
# order-level status still says "partially" while every line sits at zero.
ALL_LINES_REMOVED = {"financial_status": "partially_refunded", "fulfillment_status": "",
                     "line_items": [{"quantity": 1, "current_quantity": 0}]}
CANCELLED = {"financial_status": "refunded", "fulfillment_status": "",
             "cancelled_at": "2026-01-03T19:15:00-05:00"}


class CancelledOrderSync(unittest.TestCase):
    def test_a_cancelled_order_is_cancelled_locally(self):
        update, calls = _load()
        update(CANCELLED, "5001")
        self.assertEqual(calls["cancelled"], ["SAL-ORD-0001"])

    def test_a_cancelled_order_does_not_reach_the_line_item_diff(self):
        """The diff amends a live order. Running it on a cancelled one is
        both wrong and what raised LinkExistsError against a linked PO."""
        update, calls = _load()
        update(CANCELLED, "5001")
        self.assertEqual(calls["line_items"], [])

    def test_the_status_fields_are_still_written_before_cancelling(self):
        """sh_financial_status is what the dashboards read to explain WHY an
        order closed, so the cancel must not skip recording it."""
        update, calls = _load()
        update(CANCELLED, "5001")
        self.assertIn(("sh_financial_status", "refunded"), calls["set_values"])

    def test_an_already_cancelled_order_is_not_cancelled_twice(self):
        update, calls = _load(docstatus=2)
        update(CANCELLED, "5001")
        self.assertEqual(calls["cancelled"], [])

    def test_a_fully_refunded_order_is_cancelled_even_with_no_cancelled_at(self):
        """Shopify shows Refunded / "Fulfillment not required" / Archived and
        no Canceled badge. Nothing left to ship, so it must not keep ageing
        against its SLA."""
        update, calls = _load()
        update(REFUNDED, "5001")
        self.assertEqual(calls["cancelled"], ["SAL-ORD-0001"])

    def test_a_partial_refund_leaves_the_order_alone(self):
        """Part of the money back, the rest still to fulfil -- a live order."""
        update, calls = _load()
        update(PARTIAL, "5001")
        self.assertEqual(calls["cancelled"], [])
        self.assertEqual(calls["line_items"], ["SAL-ORD-0001"])

    def test_an_order_with_every_line_removed_is_cancelled(self):
        """Refunded line by line: financial_status never reaches "refunded",
        but currentQuantity 0 everywhere means nothing is left to ship."""
        update, calls = _load()
        update(ALL_LINES_REMOVED, "5001")
        self.assertEqual(calls["cancelled"], ["SAL-ORD-0001"])

    def test_a_partial_refund_with_a_line_still_live_is_left_alone(self):
        """One line refunded, one still to ship -- a real live order. This is
        the case that must never be swept up by the rule above."""
        update, calls = _load()
        update(PARTIAL, "5001")
        self.assertEqual(calls["cancelled"], [])

    def test_a_live_order_is_untouched(self):
        update, calls = _load()
        update(LIVE, "5001")
        self.assertEqual(calls["cancelled"], [])
        self.assertEqual(calls["line_items"], ["SAL-ORD-0001"])


class FinishedOnShopify(unittest.TestCase):
    """The scheduled poll's own view of "this order is over"."""

    def _fn(self):
        import importlib
        _load()  # installs the frappe stub the module imports at top level
        mod = importlib.import_module(
            "alaiy_os_connector_shopify.shopify.order.delivery_status")
        return mod._finished_on_shopify

    def test_a_cancelled_order_is_finished(self):
        self.assertTrue(self._fn()({"cancelledAt": "2026-01-03T19:15:00-05:00"}))

    def test_a_fully_refunded_order_is_finished(self):
        self.assertTrue(self._fn()({"cancelledAt": None,
                                    "displayFinancialStatus": "REFUNDED"}))

    def test_a_partially_refunded_order_is_not(self):
        self.assertFalse(self._fn()({"cancelledAt": None,
                                     "displayFinancialStatus": "PARTIALLY_REFUNDED"}))

    def test_a_paid_order_is_not(self):
        self.assertFalse(self._fn()({"cancelledAt": None,
                                     "displayFinancialStatus": "PAID"}))

    def test_every_line_at_zero_is_finished(self):
        self.assertTrue(self._fn()({
            "cancelledAt": None, "displayFinancialStatus": "PARTIALLY_REFUNDED",
            "lineItems": {"nodes": [{"quantity": 1, "currentQuantity": 0}]}}))

    def test_one_line_still_live_is_not(self):
        self.assertFalse(self._fn()({
            "cancelledAt": None, "displayFinancialStatus": "PARTIALLY_REFUNDED",
            "lineItems": {"nodes": [{"quantity": 1, "currentQuantity": 1},
                                    {"quantity": 2, "currentQuantity": 0}]}}))

    def test_no_line_items_in_the_payload_is_not_treated_as_empty(self):
        """A missing list means the read told us nothing -- cancelling on
        that is worse than missing one order."""
        self.assertFalse(self._fn()({
            "cancelledAt": None, "displayFinancialStatus": "PAID",
            "lineItems": {"nodes": []}}))


if __name__ == "__main__":
    unittest.main()
