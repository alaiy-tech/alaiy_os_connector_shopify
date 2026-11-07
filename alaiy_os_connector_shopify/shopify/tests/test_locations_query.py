"""The location sync asks Shopify for app-managed (fulfillment service)
locations too. Shopify omits them unless includeLegacy is set, and their stock
then shows up on every pull as a location the site has no record of.

Run with:  bench --site <site> run-tests --module \
    alaiy_os_connector_shopify.shopify.tests.test_locations_query
"""

import unittest

from alaiy_os_connector_shopify.shopify.inventory_sync import _LOCATIONS_QUERY


class TestLocationsQuery(unittest.TestCase):
    def test_app_managed_locations_are_requested(self):
        self.assertIn("includeLegacy: true", _LOCATIONS_QUERY)
