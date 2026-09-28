"""A seeded photo row is not an enhanced one.

api._ensure_enriched_listing seeds every photo as a row holding the photo
itself (url == source_url), so an untouched photo publishes as the original.
already_enhanced used to count any row with a url, so "select all, enrich"
answered "already retouched — nothing spent" for photos never retouched and
handed the originals back as the retouch (live 2026-09-29, Z058-03286R).

`frappe.db` is a thread-local proxy that raises "object is not bound" outside
a real request/job context, so the whole `frappe` name inside
image_generation is replaced with a stand-in -- see test_image_stage_apply_lock.

Run with:  bench --site <site> run-tests --module \
    alaiy_os_connector_shopify.shopify.tests.test_already_enhanced_seeded
"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from alaiy_os_connector_shopify.listing import image_generation


def _row(source_url, url):
    return SimpleNamespace(source_url=source_url, url=url)


def _fake_frappe(rows, exists=True):
    return SimpleNamespace(
        db=SimpleNamespace(exists=MagicMock(return_value=exists)),
        get_all=MagicMock(return_value=rows),
    )


class TestAlreadyEnhanced(unittest.TestCase):
    def _run(self, rows, exists=True):
        with patch.object(image_generation, "frappe", _fake_frappe(rows, exists)):
            return image_generation.already_enhanced("ITEM")

    def test_seeded_original_is_not_enhanced(self):
        self.assertEqual(self._run([_row("/files/a.jpg", "/files/a.jpg")]), {})

    def test_retouched_photo_is_enhanced(self):
        rows = [_row("/files/a.jpg", "/files/listing-enhanced-1.png")]
        self.assertEqual(
            self._run(rows), {"/files/a.jpg": "/files/listing-enhanced-1.png"}
        )

    def test_mixed_listing_only_reports_the_retouched_ones(self):
        rows = [
            _row("/files/1.jpg", "/files/1.jpg"),
            _row("/files/2.jpg", "/files/2.jpg"),
            _row("/files/3.jpg", "/files/3.jpg"),
            _row("/files/4.jpg", "/files/listing-enhanced-4.png"),
        ]
        self.assertEqual(
            self._run(rows), {"/files/4.jpg": "/files/listing-enhanced-4.png"}
        )

    def test_pending_or_failed_row_is_not_enhanced(self):
        self.assertEqual(self._run([_row("/files/a.jpg", None)]), {})

    def test_no_enriched_listing(self):
        self.assertEqual(self._run([], exists=False), {})


if __name__ == "__main__":
    unittest.main()
