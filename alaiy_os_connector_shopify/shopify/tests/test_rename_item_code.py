"""rename_item_code must move everything named after the old code, and undo on failure.

`frappe` inside rename is replaced with a recording stand-in.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from alaiy_os_connector_shopify.shopify.product import rename


class _Thrown(Exception):
    pass


def _fake(existing=(), rename_fails_on=None):
    calls = []
    existing = set(existing)

    def rename_doc(doctype, old, new, **kw):
        if rename_fails_on == doctype:
            raise RuntimeError("boom")
        calls.append(("rename", doctype, old, new))
        existing.discard((doctype, old))
        existing.add((doctype, new))

    def throw(msg):
        raise _Thrown(msg)

    fake = SimpleNamespace(
        _=lambda s: s,
        throw=throw,
        db=SimpleNamespace(
            exists=lambda doctype, name: (doctype, name) in existing,
            sql=lambda q, params: calls.append(("sql", params)),
            commit=lambda: calls.append(("commit",)),
            rollback=lambda: calls.append(("rollback",)),
        ),
        rename_doc=rename_doc,
        get_all=lambda doctype, filters, pluck: ["OLD"] if ("Shopify Product Listing", "OLD") in existing or ("Shopify Enriched Listing", "OLD") in existing else [],
    )
    return fake, calls


class TestRenameItemCode(unittest.TestCase):
    def _run(self, **kw):
        fake, calls = _fake(existing={("Item", "OLD"), ("Shopify Product Listing", "OLD"), ("Shopify Enriched Listing", "OLD")}, **kw)
        with patch.object(rename, "frappe", fake):
            return fake, calls

    def test_renames_item_listings_and_entity_then_commits(self):
        fake, calls = self._run()
        with patch.object(rename, "frappe", fake):
            self.assertEqual(rename.rename_item_code("OLD", " NEW "), "NEW")
        self.assertEqual(calls, [
            ("rename", "Item", "OLD", "NEW"),
            ("rename", "Shopify Product Listing", "OLD", "NEW"),
            ("rename", "Shopify Enriched Listing", "OLD", "NEW"),
            ("sql", ("NEW", "OLD")),
            ("commit",),
        ])

    def test_taken_sku_is_refused_before_anything_changes(self):
        fake, calls = _fake(existing={("Item", "OLD"), ("Item", "NEW")})
        with patch.object(rename, "frappe", fake), self.assertRaises(_Thrown):
            rename.rename_item_code("OLD", "NEW")
        self.assertEqual(calls, [])

    def test_failure_rolls_back_and_raises(self):
        fake, calls = self._run(rename_fails_on="Shopify Product Listing")
        with patch.object(rename, "frappe", fake), self.assertRaises(RuntimeError):
            rename.rename_item_code("OLD", "NEW")
        self.assertIn(("rollback",), calls)
        self.assertNotIn(("commit",), calls)

    def test_same_code_is_a_no_op(self):
        fake, calls = self._run()
        with patch.object(rename, "frappe", fake):
            self.assertEqual(rename.rename_item_code("OLD", "OLD"), "OLD")
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
