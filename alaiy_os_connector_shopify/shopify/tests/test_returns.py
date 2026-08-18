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

    def test_same_item_on_two_rows_shares_one_budget(self):
        """Two rows with the same item_code must not each get the full
        refunded qty -- that would return twice what Shopify refunded.
        Happens for real: the same SKU on two order lines, or two unmatched
        Shopify lines both resolving to the shared placeholder Item."""
        doc = _Doc([_Row("SKU-1", -5), _Row("SKU-1", -5)])
        self.assertTrue(_trim_return_items(doc, {"SKU-1": 3}))
        self.assertEqual(sum(abs(r.qty) for r in doc.items), 3)

    def test_budget_exhausted_drops_later_rows_entirely(self):
        doc = _Doc([_Row("SKU-1", -2), _Row("SKU-1", -2)])
        self.assertTrue(_trim_return_items(doc, {"SKU-1": 2}))
        self.assertEqual(len(doc.items), 1)
        self.assertEqual(doc.items[0].qty, -2)

    def test_refund_larger_than_returnable_lands_short(self):
        """make_return_doc already nets off earlier returns, so a refund for
        more than what's left returns only what's actually available rather
        than going negative."""
        doc = _Doc([_Row("SKU-1", -1)])
        self.assertTrue(_trim_return_items(doc, {"SKU-1": 4}))
        self.assertEqual(doc.items[0].qty, -1)


if __name__ == "__main__":
    unittest.main()
