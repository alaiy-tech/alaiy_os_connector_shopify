"""
#60: order line-item -> Item resolution must agree whether the variant id
lives on the Listing Variant row or (pre-migration) only on the Item --
a wrong answer here means an order gets matched to the wrong SKU. No DB
needed: frappe.db.get_value is mocked to simulate both states.
"""

import unittest
from unittest.mock import patch

from alaiy_os_connector_shopify.shopify.product.listing import item_by_variant_id
from alaiy_os_connector_shopify.shopify.order.utils import _resolve_item_code


class TestItemByVariantId(unittest.TestCase):
    def test_prefers_listing_variant_row(self):
        with patch("frappe.db.get_value") as get_value:
            get_value.return_value = "SKU-FROM-LISTING"
            self.assertEqual(item_by_variant_id("123"), "SKU-FROM-LISTING")
            # Only the Listing Variant lookup should fire -- Item fallback
            # is skipped once the Listing Variant already answered.
            get_value.assert_called_once_with(
                "Shopify Listing Variant", {"sh_shopify_variant_id": "123"}, "item_variant"
            )

    def test_falls_back_to_item_when_no_listing_variant_row(self):
        with patch("frappe.db.get_value") as get_value:
            get_value.side_effect = [None, "SKU-FROM-ITEM"]
            self.assertEqual(item_by_variant_id("123"), "SKU-FROM-ITEM")
            self.assertEqual(get_value.call_count, 2)
            self.assertEqual(get_value.call_args_list[1].args[0], "Item")

    def test_blank_variant_id_short_circuits(self):
        self.assertIsNone(item_by_variant_id(""))
        self.assertIsNone(item_by_variant_id(None))


class TestResolveItemCode(unittest.TestCase):
    def test_sku_match_wins_before_any_variant_id_lookup(self):
        with patch("frappe.db.exists", return_value=True), \
             patch("frappe.db.get_value") as get_value:
            code = _resolve_item_code({"sku": "SKU-1", "variant_id": "999"})
            self.assertEqual(code, "SKU-1")
            get_value.assert_not_called()

    def test_variant_id_resolves_via_listing_first(self):
        with patch("frappe.db.exists", return_value=False), \
             patch("frappe.db.get_value", return_value="SKU-FROM-LISTING") as get_value:
            code = _resolve_item_code({"sku": "", "variant_id": "123"})
            self.assertEqual(code, "SKU-FROM-LISTING")
            get_value.assert_called_once_with(
                "Shopify Listing Variant", {"sh_shopify_variant_id": "123"}, "item_variant"
            )

    def test_variant_id_falls_back_to_item_and_agrees_with_pre_60_behavior(self):
        # Pre-#60, this same line item resolved straight off Item -- the
        # fallback path must still return the exact same SKU.
        with patch("frappe.db.exists", return_value=False), \
             patch("frappe.db.get_value", side_effect=[None, "SKU-FROM-ITEM"]):
            code = _resolve_item_code({"sku": "", "variant_id": "123"})
            self.assertEqual(code, "SKU-FROM-ITEM")

    def test_falls_back_to_title_when_no_sku_or_variant_match(self):
        with patch("frappe.db.exists") as exists, \
             patch("frappe.db.get_value", return_value=None):
            exists.side_effect = lambda doctype, name: name == "Some Title"
            code = _resolve_item_code({"sku": "", "variant_id": "", "title": "Some Title"})
            self.assertEqual(code, "Some Title")

    def test_returns_none_when_nothing_matches(self):
        with patch("frappe.db.exists", return_value=False), \
             patch("frappe.db.get_value", return_value=None):
            self.assertIsNone(_resolve_item_code({"sku": "x", "variant_id": "1", "title": "y"}))


if __name__ == "__main__":
    unittest.main()
