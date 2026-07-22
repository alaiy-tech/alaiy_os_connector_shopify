"""
Pure-logic tests for the Listing resolver's fallback rules -- the core of the
whole feature: a blank Listing field must inherit the Item's value, a filled
one must override. Run via `bench run-tests` (needs a site context, same as
the other tests in this app).

The DB-touching resolvers (is_enabled, enabled_variant_names, effective_price
when blank) are covered by integration behavior on a real site; here we pin
the fallback branching that decides "override vs inherit", which is exactly
where a regression would silently push the wrong title/description.
"""

import unittest
from types import SimpleNamespace

from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver


class TestEffectiveContent(unittest.TestCase):
    def _item(self):
        return SimpleNamespace(item_code="SKU1", item_name="Item Name", description="Item desc")

    def test_title_prefers_listing_override(self):
        listing = SimpleNamespace(listing_title="Custom Title")
        self.assertEqual(listing_resolver.effective_title(listing, self._item()), "Custom Title")

    def test_title_falls_back_to_item_when_blank(self):
        for blank in ("", "   ", None):
            listing = SimpleNamespace(listing_title=blank)
            self.assertEqual(listing_resolver.effective_title(listing, self._item()), "Item Name")

    def test_description_prefers_listing_override(self):
        listing = SimpleNamespace(listing_description="Custom desc")
        self.assertEqual(
            listing_resolver.effective_description(listing, self._item()), "Custom desc"
        )

    def test_description_falls_back_to_item_when_blank(self):
        listing = SimpleNamespace(listing_description=None)
        self.assertEqual(
            listing_resolver.effective_description(listing, self._item()), "Item desc"
        )


if __name__ == "__main__":
    unittest.main()
