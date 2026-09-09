"""
owned_by narrows a lookup to one store, and never invents one.

The helper is three lines, but the thing it must not do is the whole point:
if it ever resolved a connection on its own, a caller that forgot to thread
one would keep returning plausible rows from whichever store wrote first, and
nothing would look broken.
"""

import sys
import types
import unittest


def _load():
    sys.modules.setdefault("frappe", types.ModuleType("frappe"))
    for mod in list(sys.modules):
        if mod.startswith("alaiy_os_connector_shopify"):
            del sys.modules[mod]
    from alaiy_os_connector_shopify.shopify import scoping
    return scoping


class TestFieldPerDoctype(unittest.TestCase):
    def test_erpnext_doctypes_use_the_custom_field(self):
        s = _load()
        for doctype in ("Item", "Sales Order", "Customer",
                        "Delivery Note", "Sales Invoice", "Sales Order Item"):
            self.assertEqual(s.connection_field(doctype), "sh_shopify_connection")

    def test_connector_doctypes_use_the_plain_field(self):
        s = _load()
        for doctype in ("Shopify Location", "Shopify Collection", "Shopify Tag",
                        "Shopify Product Listing", "Shopify Synced Entity"):
            self.assertEqual(s.connection_field(doctype), "connection")


class TestNarrowing(unittest.TestCase):
    def test_the_connection_is_added_to_the_filters(self):
        s = _load()
        got = s.owned_by("Item", "seller-a", {"sh_shopify_variant_id": "77"})
        self.assertEqual(got, {"sh_shopify_variant_id": "77",
                               "sh_shopify_connection": "seller-a"})

    def test_a_document_works_as_well_as_a_name(self):
        s = _load()
        connection = types.SimpleNamespace(name="seller-b")
        got = s.owned_by("Shopify Location", connection, {"sh_location_id": "1"})
        self.assertEqual(got["connection"], "seller-b")

    def test_the_callers_dict_is_not_mutated(self):
        # Several call sites build their filters once and reuse them.
        s = _load()
        original = {"sh_shopify_order_id": "1001"}
        s.owned_by("Sales Order", "seller-a", original)
        self.assertEqual(original, {"sh_shopify_order_id": "1001"})

    def test_no_filters_is_still_scoped(self):
        s = _load()
        self.assertEqual(s.owned_by("Shopify Tag", "seller-a"),
                         {"connection": "seller-a"})


class TestItNeverInventsAConnection(unittest.TestCase):
    def test_none_leaves_the_filters_alone(self):
        # An unconverted caller must keep working unchanged. Falling back to
        # "the default store" here would turn every one of them into a silent
        # cross-store read that still returns plausible rows.
        s = _load()
        got = s.owned_by("Item", None, {"sh_shopify_product_id": "12345"})
        self.assertEqual(got, {"sh_shopify_product_id": "12345"})

    def test_none_adds_no_connection_key_at_all(self):
        s = _load()
        self.assertNotIn("sh_shopify_connection", s.owned_by("Item", None, {}))
        self.assertNotIn("connection", s.owned_by("Shopify Tag", None, {}))


if __name__ == "__main__":
    unittest.main()
