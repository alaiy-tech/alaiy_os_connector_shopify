"""
Pure-logic tests for product_import.py -- no DB needed.
"""

import unittest
from types import SimpleNamespace

from alaiy_os_connector_shopify.shopify.product_import import (
    _apply_product_meta,
    _WEIGHT_UNIT_TO_UOM,
    _UOM_TO_WEIGHT_UNIT,
    _REST_WEIGHT_UNIT_TO_UOM,
)


class TestWeightUnitMaps(unittest.TestCase):
    def test_graphql_and_uom_maps_are_exact_inverses(self):
        # Push (ERPNext UOM -> Shopify enum) must round-trip back to the
        # same UOM the import path would have set, or weight silently
        # drifts every time a variant syncs in both directions.
        for enum_value, uom in _WEIGHT_UNIT_TO_UOM.items():
            self.assertEqual(_UOM_TO_WEIGHT_UNIT[uom], enum_value)

    def test_rest_map_covers_the_same_uoms_as_the_graphql_map(self):
        # Two independent mappings exist on purpose (REST's webhook
        # weight_unit strings, e.g. "kg", differ from GraphQL's enum,
        # e.g. "KILOGRAMS") -- confirmed live, conflating them silently
        # mismatches units. Both must still resolve to the same UOM set.
        self.assertEqual(
            set(_REST_WEIGHT_UNIT_TO_UOM.values()),
            set(_WEIGHT_UNIT_TO_UOM.values()),
        )


class TestApplyProductMeta(unittest.TestCase):
    def test_tags_list_is_joined_into_comma_string(self):
        item = SimpleNamespace()
        _apply_product_meta(item, {"tags": ["Adult", "Red", "FW25"]})
        self.assertEqual(item.sh_shopify_tags, "Adult, Red, FW25")

    def test_tags_already_a_string_is_passed_through(self):
        # REST webhook payloads carry tags as one comma-separated string
        # already, wrapped in a one-item list by the webhook adapter --
        # must not get re-joined into "Adult, Red, FW25" -> ["Adult, Red, FW25"]
        # style double-nesting.
        item = SimpleNamespace()
        _apply_product_meta(item, {"tags": "Adult, Red, FW25"})
        self.assertEqual(item.sh_shopify_tags, "Adult, Red, FW25")

    def test_empty_tags_leaves_field_untouched(self):
        item = SimpleNamespace()
        _apply_product_meta(item, {"tags": []})
        self.assertFalse(hasattr(item, "sh_shopify_tags"))

    def test_category_name_is_set(self):
        item = SimpleNamespace()
        _apply_product_meta(item, {"category": {"name": "Ankle Boots"}})
        self.assertEqual(item.sh_shopify_category, "Ankle Boots")

    def test_missing_category_leaves_field_untouched(self):
        item = SimpleNamespace()
        _apply_product_meta(item, {"category": None})
        self.assertFalse(hasattr(item, "sh_shopify_category"))

    def test_seo_title_and_description_are_set(self):
        item = SimpleNamespace()
        _apply_product_meta(item, {"seo": {"title": "T", "description": "D"}})
        self.assertEqual(item.sh_seo_title, "T")
        self.assertEqual(item.sh_seo_description, "D")


if __name__ == "__main__":
    unittest.main()
