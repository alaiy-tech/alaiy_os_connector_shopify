"""A new Delivery Note takes its store from its Sales Order.

Run with:  bench --site <site> run-tests --module \
    alaiy_os_connector_shopify.shopify.tests.test_delivery_note_connection
"""

from alaiy_os_connector_shopify.shopify.order import delivery_notes
from alaiy_os_connector_shopify.shopify.tests.test_fulfillment_webhook_cancellation import (
    _BaseWebhookCancellationTest,
    _Doc,
)


class TestDeliveryNoteConnection(_BaseWebhookCancellationTest):
    def _dn(self, so_name="SO-0001", connection=None):
        dn = _Doc("Delivery Note", "DN-NEW", sh_shopify_connection=connection)
        dn["items"] = [_Doc("Delivery Note Item", "row-1", against_sales_order=so_name)]
        return dn

    def test_blank_connection_is_filled_from_the_sales_order(self):
        self.db.add("Sales Order", "SO-0001", sh_shopify_connection="default")
        dn = self._dn()

        delivery_notes.set_connection_from_sales_order(dn)

        self.assertEqual(dn.sh_shopify_connection, "default")

    def test_existing_connection_is_kept(self):
        self.db.add("Sales Order", "SO-0001", sh_shopify_connection="default")
        dn = self._dn(connection="other")

        delivery_notes.set_connection_from_sales_order(dn)

        self.assertEqual(dn.sh_shopify_connection, "other")

    def test_order_with_no_store_leaves_it_blank(self):
        self.db.add("Sales Order", "SO-0001", sh_shopify_connection=None)
        dn = self._dn()

        delivery_notes.set_connection_from_sales_order(dn)

        self.assertIsNone(dn.sh_shopify_connection)

    def test_note_with_no_sales_order_is_left_alone(self):
        dn = self._dn(so_name=None)

        delivery_notes.set_connection_from_sales_order(dn)

        self.assertIsNone(dn.sh_shopify_connection)
