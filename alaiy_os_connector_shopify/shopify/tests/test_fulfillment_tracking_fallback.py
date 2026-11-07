"""_sync_tracking's fallback when no Delivery Note carries the fulfillment id.

An order shipped by two suppliers has two Shopify fulfillments. The fallback
used to take the order's first Delivery Note and stamp the second
fulfillment's id and tracking over it. That detached the first note from its
own fulfillment, and since _sync_fulfillments skips an id already present on
a note, the second shipment never got a Delivery Note of its own.

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


class TestTrackingFallbackAcrossFulfillments(_BaseWebhookCancellationTest):
    def _add_dn(self, name, fulfillment_id, so_name="SO-0001", docstatus=1):
        dn = self.db.add(
            "Delivery Note", name, docstatus=docstatus,
            sh_shopify_fulfillment_id=fulfillment_id,
        )
        self.db.rows.setdefault("Delivery Note Item", []).append(
            _Doc("Delivery Note Item", f"{name}-item-1",
                 parent=name, against_sales_order=so_name)
        )
        return dn

    def _sync(self, fulfillment):
        with patch(_GET_ACTIVE_SO, return_value="SO-0001"):
            delivery_notes._sync_tracking(fulfillment, connection="default")

    def test_note_tagged_with_another_fulfillment_is_left_alone(self):
        first = self._add_dn("DN-A", "111")

        self._sync({
            "id": "222", "order_id": "777", "status": "success",
            "tracking_number": "TRACK-B", "tracking_company": "FedEx",
        })

        self.assertEqual(first.sh_shopify_fulfillment_id, "111")
        self.assertIsNone(first.sh_tracking_number)
        self.assertEqual(self.db.set_value_calls, [])

    def test_single_untagged_note_still_gets_the_id_and_tracking(self):
        note = self._add_dn("DN-A", None)

        self._sync({
            "id": "222", "order_id": "777", "status": "success",
            "tracking_number": "TRACK-B", "tracking_company": "FedEx",
        })

        self.assertEqual(note.sh_shopify_fulfillment_id, "222")
        self.assertEqual(note.sh_tracking_number, "TRACK-B")

    def test_two_untagged_notes_are_ambiguous_and_left_alone(self):
        a = self._add_dn("DN-A", None)
        b = self._add_dn("DN-B", None)

        self._sync({"id": "222", "order_id": "777", "status": "success",
                    "tracking_number": "TRACK-B"})

        self.assertIsNone(a.sh_shopify_fulfillment_id)
        self.assertIsNone(b.sh_shopify_fulfillment_id)

    def test_cancelled_untagged_note_is_not_a_candidate(self):
        cancelled = self._add_dn("DN-A", None, docstatus=2)

        self._sync({"id": "222", "order_id": "777", "status": "success",
                    "tracking_number": "TRACK-B"})

        self.assertIsNone(cancelled.sh_shopify_fulfillment_id)
