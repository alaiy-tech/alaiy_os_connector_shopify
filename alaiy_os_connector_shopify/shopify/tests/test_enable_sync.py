"""Enable Sync is a pure switch, and a never-published product is never created by it.

Switching Enable Sync on for a product that already exists on Shopify records its
current state as in sync and sends nothing; only a later edit pushes. A Listing
with no Shopify id can have sync on, but the sweep (push_item without force) does
not create it on Shopify: publishing is an explicit action.

    python -m unittest alaiy_os_connector_shopify.shopify.tests.test_enable_sync
"""

import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import frappe

from alaiy_os_connector_shopify.shopify.product import export, listing, listing_hooks

# Other test modules swap a stub `frappe` into sys.modules and drop every
# connector module to re-import against it, without putting either back. Each
# test here runs with the real ones, captured before any test ran.
_REAL_MODULES = {
    name: module for name, module in sys.modules.items()
    if name == "frappe" or name.startswith(("frappe.", "alaiy_os_connector_shopify"))
}


def _doc(is_enabled, product_id="123", from_sync=False, was_enabled=0):
    before = None if was_enabled is None else SimpleNamespace(is_enabled=was_enabled)
    return SimpleNamespace(
        is_enabled=is_enabled, sh_shopify_product_id=product_id, item="ITEM-1", name="L-1",
        flags=SimpleNamespace(from_shopify_sync=from_sync),
        get_doc_before_save=lambda: before,
        get=lambda key, default=None: "store",
    )


class TestShouldAdoptOnEnable(unittest.TestCase):
    def test_only_the_off_to_on_save(self):
        self.assertTrue(listing_hooks.should_adopt_on_enable(1, 0))
        self.assertFalse(listing_hooks.should_adopt_on_enable(1, 1))
        self.assertFalse(listing_hooks.should_adopt_on_enable(0, 1))
        self.assertFalse(listing_hooks.should_adopt_on_enable(0, 0))

    def test_first_insert_has_no_before_image(self):
        self.assertFalse(listing_hooks.should_adopt_on_enable(1, None))


class TestNewListingDefault(unittest.TestCase):
    def test_starts_on_unless_told_otherwise(self):
        self.assertTrue(listing.should_enable_new_listing(None))
        self.assertTrue(listing.should_enable_new_listing(1))
        self.assertFalse(listing.should_enable_new_listing(0))


class TestOnListingUpdate(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict(sys.modules, _REAL_MODULES)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.enqueue = MagicMock()
        self.adopt = MagicMock()
        for target, attr, value in (
            (frappe, "enqueue", self.enqueue),
            (listing_hooks, "_adopt_current_state", self.adopt),
            (listing_hooks, "_connector_enabled", MagicMock(return_value=True)),
        ):
            p = patch.object(target, attr, value)
            p.start()
            self.addCleanup(p.stop)

    def test_switching_on_records_state_and_sends_nothing(self):
        listing_hooks.on_listing_update(_doc(1, was_enabled=0))
        self.adopt.assert_called_once()
        self.enqueue.assert_not_called()

    def test_an_edit_while_on_still_pushes(self):
        listing_hooks.on_listing_update(_doc(1, was_enabled=1))
        self.enqueue.assert_called_once()
        self.adopt.assert_not_called()

    def test_never_published_does_nothing(self):
        listing_hooks.on_listing_update(_doc(1, product_id="", was_enabled=0))
        self.enqueue.assert_not_called()
        self.adopt.assert_not_called()

    def test_inbound_provisioning_save_does_nothing(self):
        listing_hooks.on_listing_update(_doc(1, from_sync=True, was_enabled=0))
        self.enqueue.assert_not_called()
        self.adopt.assert_not_called()


class TestPushItemNeverPublished(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict(sys.modules, _REAL_MODULES)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.push = MagicMock()
        self.item = SimpleNamespace(
            name="ITEM-1", variant_of=None, get=lambda key, default=None: None)
        for target, attr, value in (
            (frappe, "get_doc", MagicMock(return_value=self.item)),
            (export.listing_resolver, "is_enabled", MagicMock(return_value=True)),
            (export.status_map, "export_allows", MagicMock(return_value=True)),
            (export, "_push_product", self.push),
        ):
            p = patch.object(target, attr, value)
            p.start()
            self.addCleanup(p.stop)

    def _push(self, product_id, force=False):
        with patch.object(
            export.listing_resolver, "get_listing",
            return_value=SimpleNamespace(sh_shopify_product_id=product_id, sh_shopify_status="Draft",
                                         get=lambda key, default=None: None),
        ):
            export.push_item("ITEM-1", force=force)

    def test_sweep_does_not_create_a_never_published_product(self):
        self._push(product_id="")
        self.push.assert_not_called()

    def test_explicit_publish_still_creates_it(self):
        self._push(product_id="", force=True)
        self.push.assert_called_once()

    def test_a_published_product_pushes(self):
        self._push(product_id="123")
        self.push.assert_called_once()


if __name__ == "__main__":
    unittest.main()
