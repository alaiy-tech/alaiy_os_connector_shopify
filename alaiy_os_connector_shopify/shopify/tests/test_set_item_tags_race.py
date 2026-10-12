"""_set_item_tags must survive concurrent jobs creating the same new Shopify Tag.

`frappe` inside tags is replaced with a stand-in that keeps the real DuplicateEntryError.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import frappe

from alaiy_os_connector_shopify.shopify.product import tags


def _fake_frappe(insert_side_effect=None):
    doc = MagicMock()
    doc.insert.side_effect = insert_side_effect
    return SimpleNamespace(
        DuplicateEntryError=frappe.DuplicateEntryError,
        db=SimpleNamespace(exists=MagicMock(return_value=False)),
        get_doc=MagicMock(return_value=doc),
        logger=MagicMock(),
    )


class TestSetItemTagsRace(unittest.TestCase):
    def test_duplicate_on_insert_still_links_the_tag(self):
        item = MagicMock()
        with patch.object(tags, "frappe", _fake_frappe(frappe.DuplicateEntryError)):
            tags._set_item_tags(item, ["9.28.26"])

        item.set.assert_called_once_with("sh_shopify_tags", [{"shopify_tag": "9.28.26"}])

    def test_other_insert_failure_still_raises(self):
        with patch.object(tags, "frappe", _fake_frappe(RuntimeError("boom"))):
            with self.assertRaises(RuntimeError):
                tags._set_item_tags(MagicMock(), ["9.28.26"])


if __name__ == "__main__":
    unittest.main()
