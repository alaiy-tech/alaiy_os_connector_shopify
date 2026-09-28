"""
Pure-logic tests for _build_full_import_query -- no DB/Shopify connection
needed. Locks in the unquoted-date fix: quoting the date value made
Shopify silently ignore the range clause and return unfiltered history.
"""

import unittest

from alaiy_os_connector_shopify.shopify.order.pull import _build_full_import_query


class TestBuildFullImportQuery(unittest.TestCase):
    def test_no_dates_is_status_any_only(self):
        self.assertEqual(_build_full_import_query(), "status:any")

    def test_date_values_are_not_quoted(self):
        # Shopify's search syntax parses >=/<= against a bare ISO date --
        # a quoted value fails to parse and the clause is dropped silently.
        q = _build_full_import_query(date_from="2026-01-01", date_to="2026-09-28")
        self.assertNotIn("'", q)
        self.assertIn("created_at:>=2026-01-01", q)
        self.assertIn("created_at:<=2026-09-28", q)

    def test_date_from_only(self):
        q = _build_full_import_query(date_from="2026-01-01")
        self.assertEqual(q, "status:any AND created_at:>=2026-01-01")

    def test_date_to_only(self):
        q = _build_full_import_query(date_to="2026-09-28")
        self.assertEqual(q, "status:any AND created_at:<=2026-09-28")


if __name__ == "__main__":
    unittest.main()
