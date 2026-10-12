"""_absolute_file_url must return a valid URL for stored paths with spaces or symbols.

`frappe.utils.get_url` needs a site, so `frappe` inside media is replaced with a stand-in.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from alaiy_os_connector_shopify.shopify.product import media

HOST = "https://site.example"


def _fake_frappe():
    return SimpleNamespace(utils=SimpleNamespace(get_url=lambda path: HOST + path))


class TestAbsoluteFileUrl(unittest.TestCase):
    def _url(self, path):
        with patch.object(media, "frappe", _fake_frappe()):
            return media._absolute_file_url(path)

    def test_space_and_parentheses_are_encoded(self):
        self.assertEqual(
            self._url("/files/Photo 1 (2).jpg"), HOST + "/files/Photo%201%20%282%29.jpg"
        )

    def test_hash_in_filename_is_encoded(self):
        self.assertEqual(self._url("/files/a#b.png"), HOST + "/files/a%23b.png")

    def test_already_encoded_path_is_not_double_encoded(self):
        self.assertEqual(self._url("/files/a%20b.jpg"), HOST + "/files/a%20b.jpg")

    def test_query_string_is_preserved(self):
        self.assertEqual(self._url("/files/x.png?v=1"), HOST + "/files/x.png?v=1")

    def test_absolute_url_is_returned_untouched(self):
        cdn = "https://cdn.shopify.com/s/files/1/x.jpg?v=1776192203"
        self.assertEqual(self._url(cdn), cdn)


if __name__ == "__main__":
    unittest.main()
