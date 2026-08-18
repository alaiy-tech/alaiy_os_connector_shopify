"""
fulfillmentCreate requires every fulfillment order named in one call to be
assigned to the same Shopify location -- a Delivery Note whose items span
locations must become one call per location. _bucket_by_location is the
function that enforces that split; get it wrong and a multi-location push
either mixes locations in one call (Shopify rejects it) or merges buckets
that should stay separate.
"""

import unittest

from alaiy_os_connector_shopify.shopify.order.fulfillment_push import _bucket_by_location


class TestBucketByLocation(unittest.TestCase):
    def test_single_location_stays_one_bucket(self):
        fulfillment_input_per_order = {
            "fo1": [{"id": "li1", "quantity": 2}],
            "fo2": [{"id": "li2", "quantity": 1}],
        }
        location_by_fulfillment_order = {"fo1": "loc-A", "fo2": "loc-A"}
        buckets = _bucket_by_location(fulfillment_input_per_order, location_by_fulfillment_order)
        self.assertEqual(len(buckets), 1)
        self.assertEqual(set(buckets["loc-A"].keys()), {"fo1", "fo2"})

    def test_two_locations_split_into_two_buckets(self):
        fulfillment_input_per_order = {
            "fo1": [{"id": "li1", "quantity": 2}],
            "fo2": [{"id": "li2", "quantity": 1}],
        }
        location_by_fulfillment_order = {"fo1": "loc-A", "fo2": "loc-B"}
        buckets = _bucket_by_location(fulfillment_input_per_order, location_by_fulfillment_order)
        self.assertEqual(len(buckets), 2)
        self.assertEqual(buckets["loc-A"], {"fo1": [{"id": "li1", "quantity": 2}]})
        self.assertEqual(buckets["loc-B"], {"fo2": [{"id": "li2", "quantity": 1}]})

    def test_missing_location_gets_its_own_bucket_not_merged(self):
        fulfillment_input_per_order = {
            "fo1": [{"id": "li1", "quantity": 2}],
            "fo2": [{"id": "li2", "quantity": 1}],
        }
        location_by_fulfillment_order = {"fo1": "loc-A", "fo2": None}
        buckets = _bucket_by_location(fulfillment_input_per_order, location_by_fulfillment_order)
        self.assertEqual(len(buckets), 2)
        self.assertIn("loc-A", buckets)
        self.assertIn(None, buckets)


if __name__ == "__main__":
    unittest.main()
