"""
Pure-logic tests for product_sync.py. Run via `bench run-tests` (needs a
site context for frappe.utils.get_system_timezone, same as every other
test in this app) -- not runnable as bare `python -m pytest`.

_to_utc_naive fixed a real crash: comparing Shopify's timezone-aware
updated_at against Alaiy OS's naive last_synced_at raised TypeError on
every single real inbound webhook update.
"""

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from alaiy_os_connector_shopify.shopify.product_sync import _to_utc_naive


class TestToUtcNaive(unittest.TestCase):
    def test_aware_datetime_converts_to_utc_and_drops_tzinfo(self):
        # 2026-01-01 10:00 IST (+05:30) == 2026-01-01 04:30 UTC
        aware = datetime(2026, 1, 1, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
        result = _to_utc_naive(aware)
        self.assertIsNone(result.tzinfo)
        self.assertEqual(result, datetime(2026, 1, 1, 4, 30))

    def test_utc_aware_datetime_is_unchanged_besides_tzinfo(self):
        aware = datetime(2026, 1, 1, 12, 0, tzinfo=ZoneInfo("UTC"))
        result = _to_utc_naive(aware)
        self.assertIsNone(result.tzinfo)
        self.assertEqual(result, datetime(2026, 1, 1, 12, 0))

    def test_naive_and_aware_results_are_directly_comparable(self):
        # The entire point of this function: two datetimes from different
        # sources (one aware, one naive) must compare without raising.
        aware = datetime(2026, 1, 1, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
        naive = _to_utc_naive(datetime(2026, 1, 1, 9, 0, tzinfo=ZoneInfo("UTC")))
        try:
            _to_utc_naive(aware) < naive
        except TypeError:
            self.fail("_to_utc_naive results must be directly comparable")


if __name__ == "__main__":
    unittest.main()
