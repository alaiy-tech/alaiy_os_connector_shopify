"""The `listing_title` hook: a client's rule applied to the agent's title.

Run with:  bench --site <site> run-tests --module \
    alaiy_os_connector_shopify.shopify.tests.test_listing_title_hook
"""

import unittest
from unittest.mock import patch

from alaiy_os_connector_shopify.listing import title as title_hook


def _suffix(item_code, title):
    return f"{title} {item_code}"


def _broken(item_code, title):
    raise ValueError("boom")


def _blank(item_code, title):
    return ""


_PROVIDERS = {"suffix": _suffix, "broken": _broken, "blank": _blank}


class Apply(unittest.TestCase):
    def _apply(self, providers, title="A Title"):
        with patch.object(title_hook.frappe, "get_hooks", return_value=providers), \
                patch.object(title_hook.frappe, "get_attr", side_effect=_PROVIDERS.get), \
                patch.object(title_hook.frappe, "log_error") as log_error:
            return title_hook.apply("X1", title), log_error

    def test_no_provider_leaves_the_title_alone(self):
        result, _ = self._apply([])
        self.assertEqual(result, "A Title")

    def test_a_provider_rewrites_the_title(self):
        result, _ = self._apply(["suffix"])
        self.assertEqual(result, "A Title X1")

    def test_providers_chain_in_hook_order(self):
        result, _ = self._apply(["suffix", "suffix"])
        self.assertEqual(result, "A Title X1 X1")

    def test_a_failing_provider_is_logged_and_skipped(self):
        result, log_error = self._apply(["broken", "suffix"])
        self.assertEqual(result, "A Title X1")
        log_error.assert_called_once()

    def test_a_blank_result_does_not_erase_the_title(self):
        result, _ = self._apply(["blank"])
        self.assertEqual(result, "A Title")


if __name__ == "__main__":
    unittest.main()
