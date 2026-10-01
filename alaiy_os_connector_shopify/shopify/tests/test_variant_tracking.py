"""
Stock Alaiy OS holds is tracked on Shopify, and a new supplier product starts
at its supplier's location.

A variant created through productSet without `inventoryItem.tracked` is left
untracked, and Shopify then ignores every quantity pushed to it and sells the
product as always available. Nothing else ever turns tracking on, so the push
has to ask for it -- but only for stock Alaiy OS actually holds: a gift card or
digital product has no Bin and keeps whatever setting Shopify has.

variants.py is loaded with its neighbours stubbed, so this runs without a bench.
"""

import importlib.util
import pathlib
import sys
import types
import unittest

MODULE = pathlib.Path(__file__).resolve().parents[1] / "product" / "variants.py"


class Variant(dict):
    __getattr__ = dict.get


def _load(has_bin=True, cost=None, bin_qty=None, gid="gid://shopify/Location/9"):
    frappe = types.ModuleType("frappe")

    def get_value(doctype, filters=None, fieldname=None, *a, **k):
        if doctype == "Shopify Location":
            return gid
        if doctype == "Bin":
            return bin_qty
        return None

    frappe.db = types.SimpleNamespace(
        exists=lambda doctype, filters=None: has_bin and doctype == "Bin",
        get_value=get_value,
    )
    utils = types.ModuleType("frappe.utils")
    utils.flt = lambda v, *a: float(v or 0)
    frappe.utils = utils

    pricing = types.ModuleType("alaiy_os_connector_shopify.shopify.product.pricing")
    pricing._variant_price = pricing._variant_compare_at_price = pricing._set_item_cost = lambda *a, **k: None
    pricing._variant_cost = lambda code: cost
    masters = types.ModuleType("alaiy_os_connector_shopify.shopify.product.masters")
    masters._ensure_uom = lambda *a, **k: None
    media = types.ModuleType("alaiy_os_connector_shopify.shopify.product.media")
    media._absolute_file_url = lambda url: url
    listing = types.ModuleType("alaiy_os_connector_shopify.shopify.product.listing")
    product = types.ModuleType("alaiy_os_connector_shopify.shopify.product")
    product.listing = listing

    stubs = {
        "frappe": frappe, "frappe.utils": utils,
        "alaiy_os_connector_shopify": types.ModuleType("alaiy_os_connector_shopify"),
        "alaiy_os_connector_shopify.shopify": types.ModuleType("alaiy_os_connector_shopify.shopify"),
        "alaiy_os_connector_shopify.shopify.product": product,
        "alaiy_os_connector_shopify.shopify.product.pricing": pricing,
        "alaiy_os_connector_shopify.shopify.product.masters": masters,
        "alaiy_os_connector_shopify.shopify.product.listing": listing,
        "alaiy_os_connector_shopify.shopify.product.media": media,
    }
    saved = {k: sys.modules.get(k) for k in stubs}
    sys.modules.update(stubs)
    try:
        spec = importlib.util.spec_from_file_location("variants_under_test", MODULE)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        for k, v in saved.items():
            sys.modules.pop(k, None) if v is None else sys.modules.__setitem__(k, v)
    return mod


class VariantTrackingTests(unittest.TestCase):
    def test_stock_we_hold_is_tracked(self):
        payload = _load(has_bin=True)._variant_inventory_item_payload(Variant(item_code="IT-1"))
        self.assertTrue(payload["tracked"])

    def test_an_item_with_no_bin_keeps_shopifys_setting(self):
        payload = _load(has_bin=False)._variant_inventory_item_payload(Variant(item_code="GIFT-1"))
        self.assertNotIn("tracked", payload)

    def test_a_variant_at_a_supplier_location_is_tracked_even_with_no_stock_yet(self):
        payload = _load(has_bin=False)._variant_inventory_item_payload(
            Variant(item_code="IT-1", shopify_location="kaj8bk954r"))
        self.assertTrue(payload["tracked"])

    def test_cost_and_tracking_travel_together(self):
        payload = _load(has_bin=True, cost=12.5)._variant_inventory_item_payload(Variant(item_code="IT-1"))
        self.assertEqual(payload, {"tracked": True, "cost": "12.50"})


class Settings:
    def __init__(self, rows):
        self.rows = rows

    def get(self, key):
        return self.rows if key == "sh_location_map" else []


MAP = [types.SimpleNamespace(shopify_location="kaj8bk954r", warehouse="OAK GEM - TS")]


class InitialQuantityTests(unittest.TestCase):
    def quantities(self, variant, bin_qty=None, rows=MAP):
        mod = _load(bin_qty=bin_qty)
        return mod._variant_initial_inventory_quantities(variant, Settings(rows))

    def test_no_stock_record_starts_at_zero_at_the_supplier_location(self):
        # Without this the product is created with no stock anywhere and Shopify
        # puts it at its default location.
        out = self.quantities(Variant(item_code="IT-1", shopify_location="kaj8bk954r"), bin_qty=None)
        self.assertEqual(out, [{"locationId": "gid://shopify/Location/9", "name": "available", "quantity": 0}])

    def test_recorded_stock_is_sent_as_is(self):
        out = self.quantities(Variant(item_code="IT-1", shopify_location="kaj8bk954r"), bin_qty=3.0)
        self.assertEqual(out[0]["quantity"], 3)

    def test_a_variant_with_no_location_sends_nothing(self):
        self.assertEqual(self.quantities(Variant(item_code="IT-1"), bin_qty=3.0), [])

    def test_a_location_with_no_mapped_warehouse_sends_nothing(self):
        self.assertEqual(
            self.quantities(Variant(item_code="IT-1", shopify_location="elsewhere"), bin_qty=3.0), [])


if __name__ == "__main__":
    unittest.main()
