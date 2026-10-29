"""
A store connected through a self-serve flow: a connection that is never the
bench's single enabled store and was made without the desk form's settings.

- The full order import names its store on the log, which is where the pull
  reads it; without it the pull asked for the single enabled store and failed.
- A shopper's Customer goes in a group ERPNext accepts when the connection has
  none configured, not the "All Customer Groups" root.
- The webhook address can be set in site_config, for a site Shopify reaches
  through another public host.
"""

import unittest
from unittest.mock import MagicMock, patch

from alaiy_os_connector_shopify.shopify import webhooks
from alaiy_os_connector_shopify.shopify.order import customer, pull


class TestFullImportNamesItsStore(unittest.TestCase):
    def test_the_connection_goes_on_the_log(self):
        with (
            patch.object(pull, "load_or_create_log", return_value="LOG") as load,
            patch.object(pull, "_run_orders_pull", return_value="LOG") as run,
        ):
            pull.run_full_import(connection="store-a")
        load.assert_called_once_with("orders", "manual", None, connection="store-a")
        run.assert_called_once_with("LOG", "status:any", skip_existing=True)


class TestDefaultCustomerGroup(unittest.TestCase):
    def frappe(self, configured="", individual=True, leaf="Commercial"):
        fake = MagicMock()
        fake.db.get_single_value.return_value = configured
        fake.db.exists.return_value = individual
        fake.db.get_value.return_value = leaf
        return patch.object(customer, "frappe", fake)

    def test_the_sites_default_comes_first(self):
        with self.frappe(configured="Retail"):
            self.assertEqual(customer._default_customer_group(), "Retail")

    def test_then_individual(self):
        with self.frappe():
            self.assertEqual(customer._default_customer_group(), "Individual")

    def test_then_any_group_that_is_not_a_group(self):
        with self.frappe(individual=False):
            self.assertEqual(customer._default_customer_group(), "Commercial")


class TestWebhookAddress(unittest.TestCase):
    def frappe(self, configured=None):
        fake = MagicMock()
        fake.conf.get.return_value = configured
        fake.utils.get_url.return_value = "https://site.example.com/"
        return patch.object(webhooks, "frappe", fake)

    def test_the_sites_own_url_by_default(self):
        with self.frappe():
            self.assertEqual(webhooks.get_webhook_address(), f"https://site.example.com{webhooks.WEBHOOK_PATH}")

    def test_site_config_sets_it(self):
        with self.frappe(configured=" https://tunnel.example.com/hook "):
            self.assertEqual(webhooks.get_webhook_address(), "https://tunnel.example.com/hook")


if __name__ == "__main__":
    unittest.main()
