"""A price-only push must not reach Shopify for a product with Enable Sync off.

Any write to Shopify makes it send products/update back with the whole
product, and the inbound handler applies Shopify's title, description and
photos over the Listing. A price edit on a product still being edited locally
(Enable Sync off, so nothing else had been pushed) brought Shopify's older
copy back over the unpushed edits.

    python -m unittest alaiy_os_connector_shopify.shopify.tests.test_variant_price_push
"""

import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import frappe

from alaiy_os_connector_shopify.shopify.product import export

# Other test modules swap a stub `frappe` into sys.modules and drop every
# connector module to re-import against it, without putting either back. Each
# test here runs with the real ones, captured before any test ran.
_REAL_MODULES = {
    name: module for name, module in sys.modules.items()
    if name == "frappe" or name.startswith(("frappe.", "alaiy_os_connector_shopify"))
}


def _listing(is_enabled):
    return SimpleNamespace(is_enabled=is_enabled, sh_shopify_product_id="111")


class TestVariantPricePush(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict(sys.modules, _REAL_MODULES)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.client = MagicMock()
        self.client.execute.return_value = {"productVariantsBulkUpdate": {"userErrors": [], "productVariants": []}}
        for target, kwargs in (
            (frappe, {"db": MagicMock(**{"get_value.return_value": SimpleNamespace(variant_of=None, name="ITEM-1")})}),
            (export.listing_resolver, {"variant_shopify_id": MagicMock(return_value="222")}),
            (export.connections, {"require_enabled": MagicMock()}),
            (export, {"ShopifyGraphQLClient": MagicMock(return_value=self.client)}),
        ):
            p = patch.multiple(target, **kwargs)
            p.start()
            self.addCleanup(p.stop)

    def _push(self, is_enabled):
        with patch.object(export.listing_resolver, "get_listing", return_value=_listing(is_enabled)):
            return export.update_variant_prices({"ITEM-1": 2755.0})

    def test_sync_off_is_skipped_and_never_sent(self):
        result = self._push(is_enabled=0)

        self.assertEqual(result, {"updated": [], "failed": {}, "skipped": ["ITEM-1"]})
        self.client.execute.assert_not_called()

    def test_sync_on_is_sent(self):
        result = self._push(is_enabled=1)

        self.assertEqual(result, {"updated": ["ITEM-1"], "failed": {}, "skipped": []})
        self.client.execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
