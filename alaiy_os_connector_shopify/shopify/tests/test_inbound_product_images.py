"""Inbound photo sync must never apply a partial photo list.

A product pushed with five photos sent by URL is processed asynchronously on
Shopify, and products/update deliveries built in that window list only the
photos already finished. Applying one cut the listing to a single photo; the
later delivery listing all five was then dropped as stale, because the check
compared Shopify's updated_at against our own clock at the end of the previous
sync.

    python -m unittest alaiy_os_connector_shopify.shopify.tests.test_inbound_product_images
"""

import datetime
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import frappe

from alaiy_os_connector_shopify.listing import images as _listing_images  # noqa: F401
from alaiy_os_connector_shopify.shopify import graphql_client as _graphql_client  # noqa: F401
from alaiy_os_connector_shopify.shopify.product import export as _export  # noqa: F401
from alaiy_os_connector_shopify.shopify.product import importer, inbound_images, webhooks
from alaiy_os_connector_shopify.shopify.product import listing as _listing  # noqa: F401
from alaiy_os_connector_shopify.shopify.sync_engine import retry_queue as _retry_queue  # noqa: F401
from alaiy_os_connector_shopify.shopify.sync_engine import retry_worker as _retry_worker  # noqa: F401

# Other test modules swap a stub `frappe` into sys.modules and drop every
# connector module (this one included, so setUpModule would be skipped) to
# re-import against it, without putting either back. The code under test
# imports some modules lazily, so each test here runs with the real ones,
# captured before any test ran.
_REAL_MODULES = {
    name: module for name, module in sys.modules.items()
    if name == "frappe" or name.startswith(("frappe.", "alaiy_os_connector_shopify"))
}


class _TestCase(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict(sys.modules, _REAL_MODULES)
        patcher.start()
        self.addCleanup(patcher.stop)

CDN = "https://cdn.shopify.com/s/files/1/0000/0000/files/"


def _media(*statuses):
    return [
        {
            "mediaContentType": "IMAGE",
            "status": status,
            # A photo that is not ready yet has no image to preview.
            "preview": {"image": {"url": f"{CDN}p{i}.png"} if status == "READY" else None},
        }
        for i, status in enumerate(statuses)
    ]


def _fetch(media, product_present=True):
    client = MagicMock()
    client.execute.return_value = {
        "product": {"featuredMedia": None, "media": {"nodes": media}} if product_present else None
    }
    with patch.object(inbound_images.connections, "require_enabled", return_value=MagicMock()), \
            patch("alaiy_os_connector_shopify.shopify.graphql_client.ShopifyGraphQLClient",
                  return_value=client), \
            patch.object(inbound_images, "frappe", SimpleNamespace(logger=MagicMock())):
        return inbound_images.fetch_product_images("42")


class TestFetchProductImages(_TestCase):
    def test_all_ready_is_settled(self):
        urls, settled = _fetch(_media("READY", "READY"))
        self.assertTrue(settled)
        self.assertEqual(urls, [f"{CDN}p0.png", f"{CDN}p1.png"])

    def test_a_photo_still_processing_is_not_settled(self):
        # The incident: one photo finished, four still being fetched.
        urls, settled = _fetch(_media("READY", "PROCESSING", "UPLOADED", "PROCESSING", "PROCESSING"))
        self.assertFalse(settled)
        self.assertEqual(urls, [f"{CDN}p0.png"])

    def test_a_failed_photo_does_not_hold_the_rest_back(self):
        urls, settled = _fetch(_media("READY", "FAILED"))
        self.assertTrue(settled)
        self.assertEqual(urls, [f"{CDN}p0.png"])

    def test_a_product_gone_from_shopify_is_none(self):
        self.assertIsNone(_fetch([], product_present=False))


def _fake_frappe(**overrides):
    fake = SimpleNamespace(
        utils=frappe.utils,
        DocumentLockedError=frappe.DocumentLockedError,
        db=SimpleNamespace(exists=MagicMock(return_value=True), commit=MagicMock()),
        get_doc=MagicMock(),
        logger=MagicMock(),
        log_error=MagicMock(),
        get_traceback=MagicMock(return_value="traceback"),
    )
    for key, value in overrides.items():
        setattr(fake, key, value)
    return fake


class TestSettledShopifyImages(_TestCase):
    def _run(self, fetched=None, raises=None):
        fetch = MagicMock(return_value=fetched, side_effect=raises)
        schedule = MagicMock()
        entity = SimpleNamespace(name="ENT-1")
        with patch.object(webhooks, "frappe", _fake_frappe()), \
                patch.object(inbound_images, "fetch_product_images", fetch), \
                patch.object(inbound_images, "schedule_recheck", schedule), \
                patch.object(webhooks.entities, "get_by_external_id", return_value=entity):
            return webhooks._settled_shopify_images("42"), schedule

    def test_settled_photos_are_returned(self):
        images, schedule = self._run(fetched=(["a", "b"], True))
        self.assertEqual(images, ["a", "b"])
        schedule.assert_not_called()

    def test_partial_photos_are_withheld_and_rechecked(self):
        images, schedule = self._run(fetched=(["a"], False))
        self.assertIsNone(images)
        schedule.assert_called_once_with("42", "ENT-1", None)

    def test_shopify_unreachable_leaves_photos_alone_and_rechecks(self):
        images, schedule = self._run(raises=RuntimeError("timeout"))
        self.assertIsNone(images)
        schedule.assert_called_once()

    def test_a_product_gone_from_shopify_is_not_rechecked(self):
        images, schedule = self._run(fetched=None)
        self.assertIsNone(images)
        schedule.assert_not_called()


class TestPartialPhotosNeverReachTheListing(_TestCase):
    def test_the_update_path_reads_photos_through_the_gate_not_the_payload(self):
        import inspect

        source = inspect.getsource(webhooks._update_item_from_shopify)
        self.assertIn("_settled_shopify_images(", source)
        self.assertNotIn('img.get("src") for img in (product.get("images")', source)


class TestApplyInboundImages(_TestCase):
    def _listing(self, urls):
        listing = MagicMock()
        listing.name = "ITEM-1"
        listing.images = [SimpleNamespace(image=u) for u in urls]
        return listing

    def test_a_changed_set_rewrites_the_listing(self):
        listing = self._listing(["a"])
        with patch("alaiy_os_connector_shopify.listing.images.follow_rehosted_urls"):
            dirty = webhooks._apply_inbound_images(MagicMock(), listing, ["a", "b"], None)
        self.assertTrue(dirty)
        listing.set.assert_called_once_with("images", [])
        self.assertEqual(listing.append.call_count, 2)

    def test_the_same_set_leaves_the_listing_alone(self):
        listing = self._listing(["a", "b"])
        with patch("alaiy_os_connector_shopify.listing.images.follow_rehosted_urls"):
            dirty = webhooks._apply_inbound_images(MagicMock(), listing, ["b", "a"], None)
        self.assertFalse(dirty)
        listing.set.assert_not_called()


class TestUpdateOrdering(_TestCase):
    """The staleness check runs on Shopify's clock, on both sides."""

    def _deliver(self, updated_at, shopify_updated_at, last_synced_at=None):
        entity = SimpleNamespace(
            name="ENT-1", erpnext_name="ITEM-1",
            shopify_updated_at=shopify_updated_at, last_synced_at=last_synced_at,
        )
        entity.get = lambda key, default=None: getattr(entity, key, default)
        item = MagicMock()
        item.name = "ITEM-1"
        fake = _fake_frappe(get_doc=MagicMock(return_value=item))
        with patch.object(webhooks, "frappe", fake), \
                patch.object(webhooks.entities, "get_by_external_id", return_value=entity), \
                patch.object(webhooks.connections, "require_enabled", return_value=MagicMock()), \
                patch.object(webhooks, "_update_item_from_shopify") as update, \
                patch.object(webhooks, "_refresh_push_fingerprint") as refresh:
            webhooks._handle_product_update("42", {"id": 42, "updated_at": updated_at})
        return update, refresh

    def test_the_incident_delivery_is_applied(self):
        # Shopify's last delivery said 15:21:32Z. The previous sync finished
        # at 15:21:33 by our clock, which the old check compared against and
        # so dropped this delivery. On Shopify's clock it is the newest state.
        update, refresh = self._deliver(
            "2026-10-01T15:21:32Z",
            shopify_updated_at=datetime.datetime(2026, 10, 1, 15, 21, 28),
            last_synced_at=datetime.datetime(2026, 10, 1, 20, 51, 33),
        )
        update.assert_called_once()
        self.assertEqual(
            refresh.call_args.kwargs["shopify_updated_at"],
            datetime.datetime(2026, 10, 1, 15, 21, 32),
        )

    def test_a_delivery_older_than_the_newest_applied_state_is_skipped(self):
        update, refresh = self._deliver(
            "2026-10-01T15:21:20Z",
            shopify_updated_at=datetime.datetime(2026, 10, 1, 15, 21, 25),
        )
        update.assert_not_called()
        refresh.assert_not_called()

    def test_a_delivery_in_the_same_second_is_applied(self):
        # updated_at has one-second resolution, and Shopify sends several
        # deliveries within one second. Equal is not older.
        update, _ = self._deliver(
            "2026-10-01T15:21:25Z",
            shopify_updated_at=datetime.datetime(2026, 10, 1, 15, 21, 25),
        )
        update.assert_called_once()

    def test_offset_timestamps_compare_in_utc(self):
        # REST webhooks carry the shop's offset; the watermark is UTC.
        update, _ = self._deliver(
            "2026-10-01T11:21:20-04:00",
            shopify_updated_at=datetime.datetime(2026, 10, 1, 15, 21, 25),
        )
        update.assert_not_called()

    def test_no_watermark_yet_applies(self):
        update, _ = self._deliver("2026-10-01T15:21:32Z", shopify_updated_at=None)
        update.assert_called_once()


class TestRecheckProductImages(_TestCase):
    def _recheck(self, fetched):
        entity = SimpleNamespace(name="ENT-1", erpnext_name="ITEM-1")
        item = MagicMock()
        item.name = "ITEM-1"
        listing = MagicMock()
        fake = _fake_frappe(get_doc=MagicMock(return_value=item))
        with patch.object(webhooks, "frappe", fake), \
                patch.object(webhooks.entities, "get_by_external_id", return_value=entity), \
                patch.object(webhooks.connections, "require_enabled", return_value=MagicMock()), \
                patch.object(inbound_images, "fetch_product_images", return_value=fetched), \
                patch.object(webhooks, "get_listing", return_value=listing), \
                patch.object(webhooks, "_apply_inbound_images", return_value=True) as apply, \
                patch.object(webhooks, "_save_listing_with_retry") as save, \
                patch.object(webhooks, "_refresh_push_fingerprint") as refresh:
            webhooks.recheck_product_images("42")
        return item, apply, save, refresh

    def test_still_processing_raises_so_the_queue_retries(self):
        with self.assertRaises(inbound_images.PhotosStillProcessing):
            self._recheck((["a"], False))

    def test_settled_photos_are_applied_under_the_item_lock(self):
        item, apply, save, refresh = self._recheck((["a", "b"], True))
        apply.assert_called_once()
        self.assertEqual(apply.call_args.args[2], ["a", "b"])
        save.assert_called_once()
        refresh.assert_called_once()
        item.lock.assert_called_once()
        item.unlock.assert_called_once()


class TestScheduleRecheck(_TestCase):
    def _schedule(self, already_queued):
        fake = SimpleNamespace(db=SimpleNamespace(exists=MagicMock(return_value=already_queued)))
        with patch.object(inbound_images, "frappe", fake), \
                patch("alaiy_os_connector_shopify.shopify.sync_engine.retry_queue.enqueue") as enqueue:
            inbound_images.schedule_recheck("42", "ENT-1", "default")
        return enqueue

    def test_queues_one_recheck(self):
        enqueue = self._schedule(already_queued=False)
        enqueue.assert_called_once_with(
            "inbound", "product", {"product_id": "42", "connection": "default"},
            synced_entity="ENT-1",
        )

    def test_a_burst_of_webhooks_queues_only_one(self):
        self._schedule(already_queued=True).assert_not_called()

    def test_the_retry_worker_knows_how_to_run_it(self):
        from alaiy_os_connector_shopify.shopify.sync_engine import retry_worker

        self.assertIn(inbound_images.RECHECK_KEY, retry_worker._HANDLERS)


class TestImportPathWaitsForPhotos(_TestCase):
    """A re-import or pull reads the same partial list while photos process."""

    def _node(self, *statuses):
        return {"featuredMedia": None, "media": {"nodes": _media(*statuses)}}

    def test_media_settled(self):
        self.assertTrue(inbound_images.media_settled(self._node("READY", "FAILED")))
        self.assertFalse(inbound_images.media_settled(self._node("READY", "PROCESSING")))
        self.assertFalse(inbound_images.media_settled(self._node("UPLOADED")))

    def test_a_node_without_status_reads_as_settled(self):
        # A webhook payload reshaped into a node carries no media status.
        node = {"media": {"nodes": [{"mediaContentType": "IMAGE", "preview": None}]}}
        self.assertTrue(inbound_images.media_settled(node))

    def test_partial_photos_are_withheld_from_the_listing_and_rechecked(self):
        entity = SimpleNamespace(name="ENT-1", external_id="42")
        with patch.object(inbound_images, "schedule_recheck") as schedule:
            images = importer._settled_listing_images(self._node("READY", "PROCESSING"), entity)
        self.assertIsNone(images)
        schedule.assert_called_once_with("42", "ENT-1", None)

    def test_settled_photos_reach_the_listing(self):
        entity = SimpleNamespace(name="ENT-1", external_id="42")
        with patch.object(inbound_images, "schedule_recheck") as schedule:
            images = importer._settled_listing_images(self._node("READY", "READY"), entity)
        self.assertEqual(images, [f"{CDN}p0.png", f"{CDN}p1.png"])
        schedule.assert_not_called()

    def test_every_listing_photo_write_in_the_importer_is_gated(self):
        import inspect

        source = inspect.getsource(importer)
        self.assertEqual(source.count("apply_inbound_from_shopify("), 3)
        calls = source.split("apply_inbound_from_shopify(")[1:]
        for call in calls:
            args = call.split(")")[0]
            self.assertNotIn("images=images", args)
            self.assertNotIn("images=product_image_urls", args)

    def test_the_import_query_reads_media_status(self):
        from alaiy_os_connector_shopify.shopify.product import queries

        media = queries._PRODUCT_NODE_FIELDS.split("media(first")[1].split("variants(")[0]
        self.assertIn("status", media)


if __name__ == "__main__":
    unittest.main()
