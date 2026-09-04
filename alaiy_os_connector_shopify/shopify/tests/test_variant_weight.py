"""Weight fallback: Shopify's shipping weight, else a product metafield.

Some catalogs leave inventoryItem.measurement.weight at 0 and keep the
real gram weight in a metafield, so without this every item imports unweighed
-- and a Delivery Note with no net weight cannot produce a FedEx label.

The parser reads free text a human typed, so the cases that matter most here
are the ones it must REFUSE: a field holding two weights, a range, or a
qualifier must leave weight unset rather than put a guessed number on a label.
"""

import unittest

from alaiy_os_connector_shopify.shopify.product.variants import _weight_from_metafields


def _node(**pairs):
    """A product node carrying the given (namespace, key) metafields."""
    return {"metafields": {"nodes": [
        {"namespace": ns, "key": key, "value": value}
        for (ns, key), value in pairs.items()
    ]}}


TOTAL = ("uploadify_product", "total_weight")
CUSTOM = ("custom", "weight")


class TestWeightFromMetafields(unittest.TestCase):

    def test_numeric_total_weight_is_grams(self):
        self.assertEqual(_weight_from_metafields(_node(**{TOTAL: "10.59"})), (10.59, "Gram"))

    def test_free_text_custom_weight(self):
        self.assertEqual(_weight_from_metafields(_node(**{CUSTOM: "10.59 g"})), (10.59, "Gram"))

    def test_trailing_dot_and_space(self):
        # Seen live: '1.81 g. '
        self.assertEqual(_weight_from_metafields(_node(**{CUSTOM: "1.81 g. "})), (1.81, "Gram"))

    def test_unit_aliases(self):
        for raw, expected in (("40 gr", (40.0, "Gram")), ("11 gm", (11.0, "Gram")),
                              ("2.5 lbs", (2.5, "Pound")), ("1.2 kg", (1.2, "Kg")),
                              ("3 oz", (3.0, "Ounce"))):
            self.assertEqual(_weight_from_metafields(_node(**{CUSTOM: raw})), expected, raw)

    def test_total_weight_preferred_over_custom(self):
        node = _node(**{TOTAL: "6.05", CUSTOM: "6.05 g"})
        self.assertEqual(_weight_from_metafields(node), (6.05, "Gram"))

    def test_falls_back_when_total_weight_blank(self):
        node = _node(**{TOTAL: "", CUSTOM: "4.93 g"})
        self.assertEqual(_weight_from_metafields(node), (4.93, "Gram"))

    def test_refuses_ambiguous_values(self):
        # Every one of these must leave weight unset -- never guessed.
        for raw in ("13.8g, 13g", "5-7 g", "approx 5g", "heavy", "", "0", "0 g"):
            self.assertEqual(_weight_from_metafields(_node(**{CUSTOM: raw})), (None, None), raw)

    def test_no_metafields(self):
        self.assertEqual(_weight_from_metafields({}), (None, None))
        self.assertEqual(_weight_from_metafields(None), (None, None))
