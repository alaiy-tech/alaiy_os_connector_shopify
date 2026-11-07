"""_sync_tracking's fallback when no Delivery Note carries the fulfillment id.

An order shipped by two suppliers has two Shopify fulfillments. The fallback
used to take the order's first Delivery Note and stamp the second
fulfillment's id and tracking over it. That detached the first note from its
own fulfillment, and since _sync_fulfillments skips an id already present on
a note, the second shipment never got a Delivery Note of its own.

The fallback now attaches only to the one untagged note that carries every
item the fulfillment ships.

Run with:  bench --site <site> run-tests --module \
    alaiy_os_connector_shopify.shopify.tests.test_fulfillment_tracking_fallback
"""

from unittest.mock import patch

from alaiy_os_connector_shopify.shopify.order import delivery_notes
from alaiy_os_connector_shopify.shopify.tests.test_fulfillment_webhook_cancellation import (
    _BaseWebhookCancellationTest,
    _Doc,
)

_GET_ACTIVE_SO = (
    "alaiy_os_connector_shopify.shopify.order.upsert.get_active_sales_order"
)


def _fulfillment(fid, *skus, **extra):
    data = {
        "id": fid, "order_id": "777", "status": "success",
        "tracking_number": "TRACK-" + fid,
        "line_items": [{"sku": sku, "title": sku} for sku in skus],
    }
    data.update(extra)
    return data


class TestTrackingFallbackAcrossFulfillments(_BaseWebhookCancellationTest):
    def setUp(self):
        super().setUp()
        # An item's code is its sku in these tests.
        patcher = patch.object(
            delivery_notes, "_resolve_item_code",
            side_effect=lambda li, connection=None: li.get("sku"),
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def _add_dn(self, name, fulfillment_id, *item_codes, so_name="SO-0001", docstatus=1):
        dn = self.db.add(
            "Delivery Note", name, docstatus=docstatus,
            sh_shopify_fulfillment_id=fulfillment_id,
        )
        for index, code in enumerate(item_codes):
            self.db.rows.setdefault("Delivery Note Item", []).append(
                _Doc("Delivery Note Item", f"{name}-item-{index}",
                     parent=name, against_sales_order=so_name, item_code=code)
            )
        return dn

    def _sync(self, fulfillment):
        with patch(_GET_ACTIVE_SO, return_value="SO-0001"):
            delivery_notes._sync_tracking(fulfillment, connection="default")

    def test_note_tagged_with_another_fulfillment_is_left_alone(self):
        first = self._add_dn("DN-A", "111", "A1")

        self._sync(_fulfillment("222", "B1"))

        self.assertEqual(first.sh_shopify_fulfillment_id, "111")
        self.assertIsNone(first.sh_tracking_number)
        self.assertEqual(self.db.set_value_calls, [])

    def test_untagged_note_holding_the_fulfillments_items_gets_the_id(self):
        note = self._add_dn("DN-A", None, "A1", "A2")

        self._sync(_fulfillment("222", "A1", "A2"))

        self.assertEqual(note.sh_shopify_fulfillment_id, "222")
        self.assertEqual(note.sh_tracking_number, "TRACK-222")

    def test_two_suppliers_each_fulfillment_reaches_only_its_own_note(self):
        a = self._add_dn("DN-A", None, "A1", "A2")
        b = self._add_dn("DN-B", None, "B1")

        self._sync(_fulfillment("222", "B1"))

        self.assertEqual(b.sh_shopify_fulfillment_id, "222")
        self.assertIsNone(a.sh_shopify_fulfillment_id)

        self._sync(_fulfillment("333", "A1", "A2"))

        self.assertEqual(a.sh_shopify_fulfillment_id, "333")
        self.assertEqual(b.sh_shopify_fulfillment_id, "222")

    def test_untagged_note_for_other_items_is_not_used(self):
        other = self._add_dn("DN-A", None, "A1")

        self._sync(_fulfillment("222", "B1"))

        self.assertIsNone(other.sh_shopify_fulfillment_id)

    def test_two_untagged_notes_holding_the_same_items_are_ambiguous(self):
        a = self._add_dn("DN-A", None, "A1")
        b = self._add_dn("DN-B", None, "A1")

        self._sync(_fulfillment("222", "A1"))

        self.assertIsNone(a.sh_shopify_fulfillment_id)
        self.assertIsNone(b.sh_shopify_fulfillment_id)

    def test_a_line_that_cannot_be_resolved_attaches_nothing(self):
        note = self._add_dn("DN-A", None, "A1")
        fulfillment = _fulfillment("222", "A1")
        fulfillment["line_items"].append({"sku": None, "title": None})
        self.db.add("Sales Order", "SO-0001", docstatus=1)

        self._sync(fulfillment)

        self.assertIsNone(note.sh_shopify_fulfillment_id)

    def test_cancelled_untagged_note_is_not_a_candidate(self):
        cancelled = self._add_dn("DN-A", None, "A1", docstatus=2)

        self._sync(_fulfillment("222", "A1"))

        self.assertIsNone(cancelled.sh_shopify_fulfillment_id)
