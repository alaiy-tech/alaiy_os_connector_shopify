"""_ensure_enriched_listing must survive several callers seeding the SAME
product's Shopify Enriched Listing at once.

Confirmed live on 2026-09-29: selecting every photo on a product with no
enriched listing yet, and enriching them together, fires one
enrich_listing_image request per photo, in parallel. Every one of them
reaches _ensure_enriched_listing's exists-check seeing "not there" before
any of them commits an insert -- Shopify Enriched Listing is autonamed
`field:item_code`, so every loser collides on the same primary key and the
browser saw a 409 Conflict on all but one photo.

`frappe.db` is a thread-local proxy that raises "object is not bound" the
moment anything (even mock.patch's own introspection) touches it outside a
real request/job context, so these tests replace the whole `frappe` name
inside listing_api with a lightweight stand-in instead -- see _fake_frappe.
The real DuplicateEntryError is kept on it so `except
frappe.DuplicateEntryError` inside the module under test still matches what
these tests raise.

Run with:  bench --site <site> run-tests --module \
    alaiy_os_connector_shopify.shopify.tests.test_ensure_enriched_listing_race
"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import frappe

from alaiy_os_connector_shopify.listing import api as listing_api
from alaiy_os_connector_shopify.listing import handlers


def _fake_frappe(exists=False, new_doc=None):
    return SimpleNamespace(
        DuplicateEntryError=frappe.DuplicateEntryError,
        db=SimpleNamespace(exists=MagicMock(return_value=exists)),
        new_doc=MagicMock(return_value=new_doc or MagicMock()),
    )


def _empty_seed_patches():
    """Every source _ensure_enriched_listing copies from the listing onto the
    new draft, stubbed to empty so the append loops have something iterable
    to walk without needing a real Shopify Product Listing document."""
    return [
        patch.object(handlers, "published_attributes", return_value={}),
        patch.object(handlers, "listing_image_urls", return_value=[]),
        patch.object(handlers, "variant_image_map", return_value={}),
    ]


class TestEnsureEnrichedListingConcurrentCreate(unittest.TestCase):
    def test_already_exists_returns_without_creating(self):
        fake = _fake_frappe(exists=True)
        with patch.object(listing_api, "frappe", fake):
            listing_api._ensure_enriched_listing("ITEM", MagicMock())

        fake.new_doc.assert_not_called()

    def test_duplicate_entry_on_insert_is_swallowed(self):
        """The concurrent-loser path: another request already won the race
        and inserted this same item_code first."""
        doc = MagicMock()
        doc.insert.side_effect = frappe.DuplicateEntryError
        fake = _fake_frappe(exists=False, new_doc=doc)
        patches = _empty_seed_patches()
        with patch.object(listing_api, "frappe", fake), patches[0], patches[1], patches[2]:
            # Must not raise.
            listing_api._ensure_enriched_listing("ITEM", MagicMock())

        doc.insert.assert_called_once_with(ignore_permissions=True)

    def test_successful_insert_is_unaffected(self):
        doc = MagicMock()
        fake = _fake_frappe(exists=False, new_doc=doc)
        patches = _empty_seed_patches()
        with patch.object(listing_api, "frappe", fake), patches[0], patches[1], patches[2]:
            listing_api._ensure_enriched_listing("ITEM", MagicMock())

        doc.insert.assert_called_once_with(ignore_permissions=True)

    def test_a_different_insert_failure_still_raises(self):
        """Only the exact race this exists for is swallowed -- any other
        insert failure (a real validation error, a DB outage) must still
        surface, not be silently eaten alongside it."""
        doc = MagicMock()
        doc.insert.side_effect = RuntimeError("boom")
        fake = _fake_frappe(exists=False, new_doc=doc)
        patches = _empty_seed_patches()
        with patch.object(listing_api, "frappe", fake), patches[0], patches[1], patches[2]:
            with self.assertRaises(RuntimeError):
                listing_api._ensure_enriched_listing("ITEM", MagicMock())


if __name__ == "__main__":
    unittest.main()
