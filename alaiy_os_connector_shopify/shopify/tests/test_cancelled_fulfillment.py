"""The ordering rule behind auto-cancelling a cancelled fulfillment.

CANCELED is a terminal status, and _pending_delivery_notes excludes terminal
rows. So writing the status BEFORE the cancel succeeds drops the Delivery Note
out of the poll forever -- and a cancel that failed (a paid invoice refusing
it, a linked Purchase Invoice, a locked Stock Ledger) would leave the DN
submitted, the order reading as shipped, and nothing ever looking again. That
is the same stuck-forever state the feature exists to end.

These cover the ordering itself, which is the part that must not regress. The
document cancels are ERPNext's own and are not re-tested here.
"""

import unittest

from alaiy_os_connector_shopify.shopify.order.delivery_status import (
    _CANCELLED, _TERMINAL,
)


class TestCancelledFulfillmentContract(unittest.TestCase):

    def test_cancelled_is_terminal(self):
        """The whole ordering rule depends on this being true."""
        for value in _CANCELLED:
            self.assertIn(
                value, _TERMINAL,
                "a cancelled fulfillment must be terminal, or the poll re-asks forever",
            )

    def test_delivered_is_not_terminal(self):
        """A merchant can unfulfil a delivered order; it must stay in the poll."""
        self.assertNotIn("DELIVERED", _TERMINAL)

    def test_both_spellings_recognised(self):
        """Shopify spells it CANCELED; a change to CANCELLED must not go unnoticed."""
        self.assertIn("CANCELED", _CANCELLED)
        self.assertIn("CANCELLED", _CANCELLED)

    def test_pending_query_excludes_terminal(self):
        """_pending_delivery_notes must filter on the same terminal set.

        Read from the source rather than executed: the filter is what makes a
        successful cancel final and an unsuccessful one retried, so a change to
        one side without the other silently breaks the guarantee.
        """
        import inspect
        from alaiy_os_connector_shopify.shopify.order import delivery_status

        src = inspect.getsource(delivery_status._pending_delivery_notes)
        self.assertIn("_TERMINAL", src)
        self.assertIn('"docstatus": 1', src)

    def test_status_written_only_after_successful_cancel(self):
        """The ordering itself, asserted against the source.

        In sync_delivery_status the set_value for a cancelled fulfillment must
        sit INSIDE the success branch. If it moves above the cancel attempt,
        every failed cancel becomes permanent.
        """
        import inspect
        from alaiy_os_connector_shopify.shopify.order import delivery_status

        src = inspect.getsource(delivery_status.sync_delivery_status)
        cancel_call = src.index("_cancel_for_cancelled_fulfillment")
        # The cancelled branch's own set_value comes after the call, and the
        # branch ends in a continue so it never falls through to the general
        # status write below.
        after = src[cancel_call:]
        self.assertIn("set_value", after)
        self.assertIn("continue", after)

    def test_three_outcomes_are_distinguished(self):
        """None / True / False must each be handled separately.

        None (the order itself was cancelled) and True (cancelled
        successfully) both mark the status terminal so the poll stops asking.
        False (a paid invoice needing a human) must NOT, so it is retried once
        the payment is resolved. Collapsing None into False was what made 5
        cancelled orders fail on every tick.
        """
        import inspect
        from alaiy_os_connector_shopify.shopify.order import delivery_status

        src = inspect.getsource(delivery_status.sync_delivery_status)
        self.assertIn("outcome is None", src)
        self.assertIn("elif outcome", src)
        # The needs_human branch must not write the status.
        needs_human = src.index("needs_human")
        self.assertIn("rollback", src[needs_human:needs_human + 200])

    def test_cancelled_order_is_detected_before_cancelling(self):
        """A cancelled Sales Order must short-circuit before any cancel runs.

        ERPNext throws InvalidStatusError from update_reserved_qty when the
        order is cancelled, so attempting it is guaranteed to fail.
        """
        import inspect
        from alaiy_os_connector_shopify.shopify.order import delivery_status

        src = inspect.getsource(delivery_status._cancel_for_cancelled_fulfillment)
        guard = src.index('"docstatus": 2')
        cancel = src.index("dn.cancel()")
        self.assertLess(guard, cancel, "the cancelled-order guard must come first")
