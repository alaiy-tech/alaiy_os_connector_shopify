"""
_trim_return_items caps each return row's quantity to what THIS refund
covers -- a wrong cap here means a partial refund returns/credits more
stock or money than Shopify actually refunded. No DB needed: rows are
plain objects with the two attributes the function touches.
"""

import unittest

from alaiy_os_connector_shopify.shopify.order.returns import _trim_return_items


class _Row:
    def __init__(self, item_code, qty):
        self.item_code = item_code
        self.qty = qty


class _Doc:
    def __init__(self, items):
        self.items = items


class TestTrimReturnItems(unittest.TestCase):
    def test_caps_qty_to_refunded_amount(self):
        doc = _Doc([_Row("SKU-1", -5)])
        self.assertTrue(_trim_return_items(doc, {"SKU-1": 2}))
        self.assertEqual(doc.items[0].qty, -2)

    def test_drops_rows_not_in_the_refund(self):
        doc = _Doc([_Row("SKU-1", -5), _Row("SKU-2", -3)])
        self.assertTrue(_trim_return_items(doc, {"SKU-2": 3}))
        self.assertEqual(len(doc.items), 1)
        self.assertEqual(doc.items[0].item_code, "SKU-2")

    def test_returns_false_when_nothing_matches(self):
        doc = _Doc([_Row("SKU-1", -5)])
        self.assertFalse(_trim_return_items(doc, {"SKU-OTHER": 1}))
        self.assertEqual(doc.items, [])


if __name__ == "__main__":
    unittest.main()
