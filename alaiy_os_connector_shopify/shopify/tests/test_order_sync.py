"""
Pure-logic tests for order_sync.py -- no DB/Shopify connection needed.

_line_item_qty is the single highest-bug-history function in this
connector: reading "quantity" instead of "current_quantity" made every
Shopify Order Edit removal silently invisible for the entire life of the
feature until caught live. This locks that fix in place.
"""

import unittest

from alaiy_os_connector_shopify.shopify.order_sync import _line_item_qty


class TestLineItemQty(unittest.TestCase):
    def test_uses_current_quantity_when_present(self):
        # Shopify keeps "quantity" at the pre-edit value forever -- only
        # current_quantity reflects a removal via Order Editing.
        li = {"quantity": 1, "current_quantity": 0}
        self.assertEqual(_line_item_qty(li), 0)

    def test_current_quantity_wins_even_when_nonzero_and_different(self):
        li = {"quantity": 3, "current_quantity": 1}
        self.assertEqual(_line_item_qty(li), 1)

    def test_falls_back_to_quantity_when_current_quantity_absent(self):
        # The GraphQL pull query has no current_quantity field at all --
        # only real Shopify webhook payloads carry it.
        li = {"quantity": 2}
        self.assertEqual(_line_item_qty(li), 2)

    def test_defaults_to_one_when_both_absent(self):
        self.assertEqual(_line_item_qty({}), 1)

    def test_zero_current_quantity_is_not_treated_as_absent(self):
        # A falsy-but-present 0 must still be read as a real removal, not
        # fall through to the "quantity" default.
        li = {"quantity": 1, "current_quantity": 0}
        self.assertEqual(_line_item_qty(li), 0)


if __name__ == "__main__":
    unittest.main()
