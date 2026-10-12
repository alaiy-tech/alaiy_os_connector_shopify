"""_save_listing_with_retry must recover once from run_webhooks' None cache and re-raise anything else.

`frappe` inside webhooks is replaced with a stand-in that keeps the real TimestampMismatchError.
"""

import contextlib
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import frappe

from alaiy_os_connector_shopify.shopify.product import webhooks

NONE_CACHE = AttributeError("'NoneType' object has no attribute 'get'")


def _fake_frappe(fresh):
    return SimpleNamespace(
        TimestampMismatchError=frappe.TimestampMismatchError,
        db=SimpleNamespace(rollback=MagicMock()),
        client_cache=SimpleNamespace(delete_value=MagicMock()),
        get_doc=MagicMock(return_value=fresh),
    )


def _listing(save_side_effect=None):
    listing = MagicMock()
    listing.name = "ITEM"
    listing.as_dict.return_value = {"name": "ITEM", "title": "New title"}
    listing.save.side_effect = save_side_effect
    return listing


class TestSaveListingWebhookCache(unittest.TestCase):
    def _run(self, listing, fresh):
        fake = _fake_frappe(fresh)
        with patch.object(webhooks, "frappe", fake), patch.object(
            webhooks, "_as_administrator", contextlib.nullcontext
        ):
            webhooks._save_listing_with_retry(listing)
        return fake

    def test_none_cache_drops_key_and_saves_a_reloaded_copy(self):
        fresh = _listing()
        fake = self._run(_listing(NONE_CACHE), fresh)

        fake.client_cache.delete_value.assert_called_once_with("webhooks")
        fresh.set.assert_any_call("title", "New title")
        fresh.save.assert_called_once_with(ignore_version=True)

    def test_other_attribute_error_still_raises(self):
        fake = _fake_frappe(_listing())
        with patch.object(webhooks, "frappe", fake), patch.object(
            webhooks, "_as_administrator", contextlib.nullcontext
        ):
            with self.assertRaises(AttributeError):
                webhooks._save_listing_with_retry(_listing(AttributeError("no such field")))

        fake.client_cache.delete_value.assert_not_called()

    def test_failure_that_survives_the_retry_raises(self):
        fake = _fake_frappe(_listing(NONE_CACHE))
        with patch.object(webhooks, "frappe", fake), patch.object(
            webhooks, "_as_administrator", contextlib.nullcontext
        ):
            with self.assertRaises(AttributeError):
                webhooks._save_listing_with_retry(_listing(NONE_CACHE))

        fake.client_cache.delete_value.assert_called_once_with("webhooks")


if __name__ == "__main__":
    unittest.main()
