"""Webhook-driven fulfillment cancellation on the connector side (Solist's
own Shopify storefront, not the supplier-store pull side).

Before this file, a real Shopify fulfillment cancellation on this side only
ever reached delivery_status.py's 5-minute poll -- _sync_tracking read
fulfillment.get("display_status")/shipment_status (shipping progress: in
transit, delivered) but never fulfillment.get("status") (the fulfillment's
own lifecycle -- SUCCESS/CANCELLED/ERROR/FAILURE per Shopify's
FulfillmentStatus enum), so the fulfillments/update webhook -- which fires
on a real cancellation the same way it fires for any other change to the
Fulfillment object -- silently updated nothing. Confirmed live: a Delivery
Note stayed submitted, sh_delivery_status stayed unset, for several poll
ticks after Shopify Admin showed the order Unfulfilled.

These tests drive the REAL functions (_sync_tracking,
_cancel_for_cancelled_fulfillment) against an in-memory fake Frappe DB, and
assert on actual document state (docstatus transitions) -- not on the
source text of the functions under test.

Run with:  bench --site <site> run-tests --module \
    alaiy_os_connector_shopify.shopify.tests.test_fulfillment_webhook_cancellation
"""

import unittest
from unittest.mock import MagicMock, patch

import frappe

from alaiy_os_connector_shopify.shopify.order import delivery_notes
from alaiy_os_connector_shopify.shopify.order import delivery_status


class _Doc(dict):
    """A tiny stand-in for a Frappe document: dict-like storage plus the
    handful of doc-API calls under test actually use (.cancel(), .flags,
    attribute access). Mirrors the pattern in
    alaiy_os_thesolist.tests.test_supplier_fulfillment_cancellation."""

    def __init__(self, doctype, name, **fields):
        super().__init__(**fields)
        # Also a real dict entry, not just the attribute below --
        # frappe.get_all's pluck="name" and fields=[...] both read a row's
        # "name" out of the dict body, the same way a real frappe.get_all
        # result row does.
        dict.__setitem__(self, "name", name)
        self.doctype = doctype
        self.name = name
        self.flags = MagicMock()

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        if key in ("doctype", "name", "flags"):
            object.__setattr__(self, key, value)
        else:
            self[key] = value

    def get(self, key, default=None):
        return dict.get(self, key, default)

    def cancel(self):
        self["docstatus"] = 2


class FakeDB:
    instance = None

    def __init__(self):
        self.rows = {}   # doctype -> [dict, ...]
        self.docs = {}   # (doctype, name) -> _Doc
        self.logged_errors = []
        self.set_value_calls = []
        self.locks_acquired = []  # order of GET_LOCK calls, for race-guard tests
        self.locks = set()
        FakeDB.instance = self

    def add(self, doctype, name, **fields):
        doc = _Doc(doctype, name, **fields)
        self.docs[(doctype, name)] = doc
        self.rows.setdefault(doctype, []).append(doc)
        return doc

    def get_all(self, doctype, filters=None, fields=None, pluck=None, **kw):
        rows = self.rows.get(doctype, [])
        out = [r for r in rows if self._matches(r, filters or {})]
        if pluck:
            return [r.get(pluck) for r in out]
        if fields:
            return [
                _Doc(doctype, r["name"], **{f: r.get(f) for f in fields if f != "name"})
                for r in out
            ]
        return out

    def _matches(self, row, filters):
        for key, cond in filters.items():
            val = row.get(key)
            if isinstance(cond, (list, tuple)) and len(cond) == 2 and cond[0] in (
                "in", "not in", "is", "!=", ">=",
            ):
                op, target = cond
                if op == "in" and val not in target:
                    return False
                if op == "not in" and val in target:
                    return False
                if op == "is" and target == "set" and not val:
                    return False
                if op == "!=" and val == target:
                    return False
                if op == ">=" and not (val and val >= target):
                    return False
            else:
                if val != cond:
                    return False
        return True

    def get_doc(self, doctype, name=None):
        if name is None and isinstance(doctype, dict):
            raise NotImplementedError
        doc = self.docs.get((doctype, name))
        if not doc:
            raise Exception(f"{doctype} {name} not found")
        return doc

    def db_get_value(self, doctype, filters, field=None, **kw):
        if isinstance(filters, str):
            doc = self.docs.get((doctype, filters))
            return doc.get(field) if doc else None
        rows = [r for r in self.rows.get(doctype, []) if self._matches(r, filters)]
        if not rows:
            return None
        row = rows[0]
        if isinstance(field, (list, tuple)):
            return _Doc(doctype, row["name"], **{f: row.get(f) for f in field})
        return row.get(field)

    def db_set_value(self, doctype, name, field, value=None, **kw):
        """Mirrors frappe.db.set_value's two call shapes: a single
        (field, value) pair, or a dict of {field: value}."""
        self.set_value_calls.append((doctype, name, field, value))
        doc = self.docs.get((doctype, name))
        if not doc:
            return
        if isinstance(field, dict):
            for k, v in field.items():
                doc[k] = v
        else:
            doc[field] = value

    def db_exists(self, doctype, filters):
        return bool(self.get_all(doctype, filters))

    def db_sql(self, query, params=None):
        if "GET_LOCK" in query:
            name = params[0]
            self.locks_acquired.append(name)
            if name in self.locks:
                return [[0]]
            self.locks.add(name)
            return [[1]]
        if "RELEASE_LOCK" in query:
            self.locks.discard(params[0])
            return [[1]]
        return [[0]]


def _install_fake_frappe():
    db = FakeDB()
    patches = [
        patch.object(frappe, "get_all", side_effect=db.get_all),
        patch.object(frappe, "get_doc", side_effect=db.get_doc),
        patch.object(frappe.db, "get_value", side_effect=db.db_get_value),
        patch.object(frappe.db, "set_value", side_effect=db.db_set_value),
        patch.object(frappe.db, "exists", side_effect=db.db_exists),
        patch.object(frappe.db, "sql", side_effect=db.db_sql),
        patch.object(frappe.db, "commit", lambda: None),
        patch.object(frappe.db, "rollback", lambda: None),
        patch.object(frappe, "log_error", side_effect=lambda title="", message="": db.logged_errors.append(title)),
        patch.object(frappe, "logger", return_value=MagicMock()),
    ]
    return db, patches


class _BaseWebhookCancellationTest(unittest.TestCase):
    def setUp(self):
        self.db, self.patches = _install_fake_frappe()
        for p in self.patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in self.patches])
        # owned_by(doctype, connection, filters) just merges a connection
        # filter in real code; for these single-connection tests it can be
        # a straight pass-through so FakeDB._matches sees plain filters.
        self._owned_by_patch = patch(
            "alaiy_os_connector_shopify.shopify.order.delivery_notes.owned_by",
            side_effect=lambda doctype, connection, filters=None: filters or {},
        )
        self._owned_by_patch.start()
        self.addCleanup(self._owned_by_patch.stop)

    def _make_dn(self, dn_name="DN-0001", fulfillment_id="111", so_name="SO-0001",
                 docstatus=1, delivery_status=None):
        self.db.add("Sales Order", so_name, docstatus=1, status="To Bill")
        dn = self.db.add(
            "Delivery Note", dn_name, docstatus=docstatus,
            sh_shopify_fulfillment_id=str(fulfillment_id),
            sh_delivery_status=delivery_status,
        )
        self.db.rows.setdefault("Delivery Note Item", []).append(
            _Doc("Delivery Note Item", f"{dn_name}-item-1",
                 parent=dn_name, against_sales_order=so_name)
        )
        return dn


class TestWebhookCancelsExistingDeliveryNote(_BaseWebhookCancellationTest):
    """CASE B: a fulfillment already recorded as a submitted Delivery Note
    is now reported CANCELLED by fulfillments/update."""

    def test_status_cancelled_cancels_the_delivery_note(self):
        dn = self._make_dn(dn_name="DN-0001", fulfillment_id="222")
        fulfillment = {"id": "222", "status": "cancelled"}

        delivery_notes._sync_tracking(fulfillment, connection="default")

        self.assertEqual(dn.docstatus, 2)

    def test_status_success_does_not_cancel(self):
        """Preserve existing behaviour: a non-cancelled status still just
        updates tracking, never touches docstatus."""
        dn = self._make_dn(dn_name="DN-0002", fulfillment_id="223")
        fulfillment = {
            "id": "223", "status": "success",
            "tracking_number": "TRACK-A", "tracking_company": "FedEx",
        }

        delivery_notes._sync_tracking(fulfillment, connection="default")

        self.assertEqual(dn.docstatus, 1)
        self.assertEqual(dn.sh_tracking_number, "TRACK-A")

    def test_both_spellings_of_cancelled_are_recognised(self):
        """Shopify spells it CANCELED (one L) in some payload shapes; both
        must be recognised the same way delivery_status.py's own _CANCELLED
        set already does."""
        dn = self._make_dn(dn_name="DN-0003", fulfillment_id="224")
        fulfillment = {"id": "224", "status": "CANCELED"}

        delivery_notes._sync_tracking(fulfillment, connection="default")

        self.assertEqual(dn.docstatus, 2)


class TestWebhookCancellationTakesTheOrderLock(_BaseWebhookCancellationTest):
    """Confirmed live on a real order (TS27771): fulfillments/update
    (cancelling a Delivery Note) and a near-simultaneous orders/updated can
    both be in flight within a couple of seconds of each other --
    _update_order's own fallback (_create_delivery_note_if_needed) read "no
    Delivery Note exists yet" in the gap between this function's read and
    its cancel, and created a SECOND Delivery Note for the same order,
    leaving the order reading shipped forever even though the real one was
    correctly cancelled. _sync_tracking's cancellation branch must take the
    same shared per-order lock _update_order already does, so the two
    webhook paths can never race on the same order."""

    def test_cancellation_acquires_and_releases_the_shared_order_lock(self):
        self._make_dn(dn_name="DN-0009", fulfillment_id="900")
        fulfillment = {"id": "900", "status": "cancelled", "order_id": "777"}

        delivery_notes._sync_tracking(fulfillment, connection="default")

        # locking.py's _lock_name: "shopify_order_<connection>_<order_id>"
        # when a connection is given -- same name _update_order would use
        # for the SAME order, so the two paths genuinely serialise.
        self.assertEqual(self.db.locks_acquired, ["shopify_order_default_777"])
        # Released afterward -- must not stay held past this one call.
        self.assertNotIn("shopify_order_default_777", self.db.locks)

    def test_lock_is_released_even_if_the_cancel_raises(self):
        """The lock must not leak if _cancel_for_cancelled_fulfillment
        itself blows up -- a real Frappe error, not the expected paid-
        invoice/dead-order outcomes, which is what the try/except in
        _sync_tracking's cancellation branch exists to guarantee."""
        # No Sales Order fixture at all -- frappe.get_doc will raise inside
        # _cancel_for_cancelled_fulfillment when it tries to load the
        # Delivery Note's linked order state.
        self.db.add(
            "Delivery Note", "DN-0010", docstatus=1,
            sh_shopify_fulfillment_id="901",
        )
        # No Delivery Note Item row at all -- so_names comes back empty and
        # _cancel_for_cancelled_fulfillment's own guards short-circuit
        # cleanly rather than raising; simulate a real failure instead by
        # making frappe.get_doc blow up for this specific Delivery Note.
        original_get_doc = self.db.get_doc

        def _blow_up(doctype, name=None):
            if doctype == "Delivery Note" and name == "DN-0010":
                raise RuntimeError("simulated Frappe failure")
            return original_get_doc(doctype, name)

        with patch.object(frappe, "get_doc", side_effect=_blow_up):
            fulfillment = {"id": "901", "status": "cancelled", "order_id": "778"}
            # Must not propagate -- the webhook handler's own try/except
            # (one layer up, in webhook.py) is the real safety net, but
            # _sync_tracking's finally must release the lock regardless.
            delivery_notes._sync_tracking(fulfillment, connection="default")

        self.assertNotIn("shopify_order_default_778", self.db.locks)
        self.assertEqual(len(self.db.logged_errors), 1)


class TestWebhookCancellationIsIdempotent(_BaseWebhookCancellationTest):
    """A redelivered fulfillments/update webhook, or the webhook racing the
    poll, must never double-cancel or raise."""

    def test_duplicate_cancel_webhook_is_a_safe_noop(self):
        dn = self._make_dn(dn_name="DN-0004", fulfillment_id="333")
        fulfillment = {"id": "333", "status": "cancelled"}

        delivery_notes._sync_tracking(fulfillment, connection="default")
        self.assertEqual(dn.docstatus, 2)

        # Redelivered -- must not raise, must not double-cancel.
        delivery_notes._sync_tracking(fulfillment, connection="default")
        self.assertEqual(dn.docstatus, 2)

    def test_shared_cancel_helper_is_idempotent_directly(self):
        """_cancel_for_cancelled_fulfillment itself must tolerate being
        called on an already-cancelled Delivery Note -- this is what makes
        the webhook path and the poll safe to race each other, since both
        funnel through this one function."""
        dn = self._make_dn(dn_name="DN-0005", fulfillment_id="444", docstatus=2)

        result = delivery_status._cancel_for_cancelled_fulfillment("DN-0005", "CANCELLED")

        self.assertTrue(result)
        self.assertEqual(dn.docstatus, 2)


class TestCaseANeverRecorded(_BaseWebhookCancellationTest):
    """A fulfillment cancelled before this side ever saw it must not create
    anything -- delivery_notes._sync_tracking's existing no-op-if-no-DN
    behaviour, confirmed still correct with the new status check ahead of
    it."""

    def test_no_delivery_note_and_no_order_match_does_nothing(self):
        fulfillment = {"id": "555", "status": "cancelled", "order_id": "999"}

        # No Sales Order, no Delivery Note exist anywhere -- must return
        # cleanly without raising or creating anything.
        delivery_notes._sync_tracking(fulfillment, connection="default")

        self.assertEqual(self.db.rows.get("Delivery Note", []), [])


class TestReFulfillmentAfterCancellation(_BaseWebhookCancellationTest):
    """Fulfillment A cancelled, then Shopify's own new Fulfillment B (a
    different id -- Shopify never reuses a cancelled fulfillment's id, see
    fulfillmentCancel's documented behaviour) must land on a NEW Delivery
    Note, never revive A."""

    def test_new_fulfillment_id_is_untouched_by_the_old_cancellation(self):
        dn_a = self._make_dn(dn_name="DN-A", fulfillment_id="666")
        fulfillment_a = {"id": "666", "status": "cancelled"}
        delivery_notes._sync_tracking(fulfillment_a, connection="default")
        self.assertEqual(dn_a.docstatus, 2)

        # A brand new fulfillment, unrelated id, already recorded as its own
        # Delivery Note (as a real webhook-driven create would have done
        # via _create_delivery_note_if_needed -- out of scope for this
        # file, so the DN is seeded directly here).
        dn_b = self._make_dn(dn_name="DN-B", fulfillment_id="667", so_name="SO-0001")
        fulfillment_b = {
            "id": "667", "status": "success", "tracking_number": "TRACK-B",
        }
        delivery_notes._sync_tracking(fulfillment_b, connection="default")

        self.assertEqual(dn_b.docstatus, 1)
        self.assertEqual(dn_b.sh_tracking_number, "TRACK-B")
        # A stays cancelled and historical -- never revived, never reused.
        self.assertEqual(dn_a.docstatus, 2)


class TestPaidInvoiceSafety(_BaseWebhookCancellationTest):
    """The paid-invoice guard in _cancel_for_cancelled_fulfillment
    must apply through the webhook path exactly as it already does through
    the poll -- one shared function, one safety rule."""

    def test_unpaid_invoice_is_cancelled_with_the_dn(self):
        dn = self._make_dn(dn_name="DN-0007", fulfillment_id="888")
        si = self.db.add("Sales Invoice", "SINV-0001", docstatus=1)
        self.db.rows.setdefault("Sales Invoice Item", []).append(
            _Doc("Sales Invoice Item", "SINV-0001-item-1",
                 parent="SINV-0001", delivery_note="DN-0007", docstatus=1)
        )
        fulfillment = {"id": "888", "status": "cancelled"}

        delivery_notes._sync_tracking(fulfillment, connection="default")

        self.assertEqual(dn.docstatus, 2)
        self.assertEqual(si.docstatus, 2)

    def test_paid_invoice_blocks_the_cancel_and_logs(self):
        dn = self._make_dn(dn_name="DN-0008", fulfillment_id="889")
        si = self.db.add("Sales Invoice", "SINV-0002", docstatus=1)
        self.db.rows.setdefault("Sales Invoice Item", []).append(
            _Doc("Sales Invoice Item", "SINV-0002-item-1",
                 parent="SINV-0002", delivery_note="DN-0008", docstatus=1)
        )
        self.db.add("Payment Entry Reference", "PER-0001",
                     reference_doctype="Sales Invoice", reference_name="SINV-0002",
                     docstatus=1)
        fulfillment = {"id": "889", "status": "cancelled"}

        delivery_notes._sync_tracking(fulfillment, connection="default")

        # Nothing touched -- still submitted, and reported for a human.
        self.assertEqual(dn.docstatus, 1)
        self.assertEqual(si.docstatus, 1)
        self.assertEqual(len(self.db.logged_errors), 1)


class TestWholeOrderCancellationGuard(_BaseWebhookCancellationTest):
    """A cancelled fulfillment must never be confused with the whole Sales
    Order being cancelled -- the existing dead-order guard in
    _cancel_for_cancelled_fulfillment must still apply when reached via
    the webhook path, not just the poll."""

    def test_dn_left_alone_when_its_order_is_already_cancelled(self):
        dn = self._make_dn(dn_name="DN-0006", fulfillment_id="777")
        # The Sales Order this DN belongs to was separately cancelled.
        so = self.db.docs[("Sales Order", "SO-0001")]
        so["docstatus"] = 2
        fulfillment = {"id": "777", "status": "cancelled"}

        delivery_notes._sync_tracking(fulfillment, connection="default")

        # Left standing as the historical record -- not force-cancelled
        # against a dead order.
        self.assertEqual(dn.docstatus, 1)


if __name__ == "__main__":
    unittest.main()
