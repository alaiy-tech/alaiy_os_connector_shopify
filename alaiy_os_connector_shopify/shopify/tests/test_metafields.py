"""
Pure-logic tests for metafields.py's build_metafields_input. Run via
`bench run-tests` -- not runnable as bare `python -m pytest` (see
test_product_sync.py for why).

A blank-value row used to be sent through as "" rather than dropped.
Shopify's metafieldsSet rejects a blank value with "Value can't be
blank.", and since one call carries a whole batch of up to 25 rows, that
single bad row failed every other row in its batch -- confirmed live: 27
otherwise-valid metafields on a real product silently stopped updating
because 2 rows in the same batch had gone blank upstream.
"""

import unittest
from types import SimpleNamespace

from alaiy_os_connector_shopify.shopify.product.metafields import build_metafields_input


def _row(namespace="custom", key="material", type="single_line_text_field", value="18K Rose Gold"):
    return SimpleNamespace(namespace=namespace, key=key, type=type, value=value)


class TestBuildMetafieldsInput(unittest.TestCase):
    def test_blank_value_row_is_dropped(self):
        listing = SimpleNamespace(metafields=[
            _row(key="material", value="18K Rose Gold"),
            _row(key="color", value=""),
        ])
        rows = build_metafields_input(listing, "gid://shopify/Product/1")
        self.assertEqual([r["key"] for r in rows], ["material"])

    def test_none_value_row_is_dropped(self):
        listing = SimpleNamespace(metafields=[_row(key="color", value=None)])
        rows = build_metafields_input(listing, "gid://shopify/Product/1")
        self.assertEqual(rows, [])

    def test_one_blank_row_does_not_drop_the_others(self):
        listing = SimpleNamespace(metafields=[
            _row(key="material", value="18K Rose Gold"),
            _row(key="color", value=""),
            _row(key="movement", value="Automatic"),
        ])
        rows = build_metafields_input(listing, "gid://shopify/Product/1")
        self.assertEqual([r["key"] for r in rows], ["material", "movement"])

    def test_row_missing_namespace_or_key_is_still_dropped(self):
        listing = SimpleNamespace(metafields=[
            _row(namespace="", key="material", value="18K Rose Gold"),
            _row(namespace="custom", key="", value="18K Rose Gold"),
        ])
        rows = build_metafields_input(listing, "gid://shopify/Product/1")
        self.assertEqual(rows, [])

    def test_valid_row_carries_owner_id_and_type(self):
        listing = SimpleNamespace(metafields=[_row()])
        rows = build_metafields_input(listing, "gid://shopify/Product/1")
        self.assertEqual(rows, [{
            "ownerId": "gid://shopify/Product/1",
            "namespace": "custom",
            "key": "material",
            "type": "single_line_text_field",
            "value": "18K Rose Gold",
        }])


if __name__ == "__main__":
    unittest.main()
