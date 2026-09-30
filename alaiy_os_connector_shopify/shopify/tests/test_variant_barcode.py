"""A variant's pushed barcode: barcode list first, else the barcode imported from Shopify."""

import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock


class _Variant(dict):
    """Stand-in for an Item doc: .get() plus attribute access."""


def _load():
    sys.modules.setdefault("frappe", MagicMock())
    sys.modules.setdefault("frappe.utils", MagicMock())
    from alaiy_os_connector_shopify.shopify.product import variants

    return variants._variant_barcode


class TestVariantBarcode(unittest.TestCase):
    def setUp(self):
        self.barcode = _load()

    def test_barcode_list_wins(self):
        v = _Variant(barcodes=[SimpleNamespace(barcode="LIST1")], sh_barcode="SH1")
        self.assertEqual(self.barcode(v), "LIST1")

    def test_falls_back_to_imported_barcode(self):
        self.assertEqual(self.barcode(_Variant(barcodes=[], sh_barcode="SH1")), "SH1")

    def test_blank_list_row_falls_back(self):
        v = _Variant(barcodes=[SimpleNamespace(barcode="")], sh_barcode="SH1")
        self.assertEqual(self.barcode(v), "SH1")

    def test_none_when_neither_set(self):
        self.assertEqual(self.barcode(_Variant()), "")


if __name__ == "__main__":
    unittest.main()
