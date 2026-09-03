"""Poll Shopify for the delivery state of shipments still in transit.

Shopify's fulfillment carries a displayStatus (IN_TRANSIT, DELIVERED,
ATTEMPTED_DELIVERY, ...) that says where the parcel actually is, distinct from
the order's fulfillment status which only says whether it shipped at all.

That status arrives on a fulfillments/create or fulfillments/update webhook --
but only when Shopify chooses to send one. Marking an order delivered from
Shopify's own admin changes displayStatus without emitting either topic, so the
state simply never reaches us. Confirmed live: a fulfillment reading DELIVERED
on Shopify sat at a blank sh_delivery_status locally, with the topic correctly
subscribed, correctly dispatched, and no error logged anywhere -- there was no
webhook to receive.

The consequence is not cosmetic. A supplier's order only reads "delivered" once
this field says DELIVERED, and only a delivered order becomes invoiceable, so a
delivery Shopify never announced leaves that supplier unable to invoice at all.

Nothing else fills this gap. The full order pull does read displayStatus, but
nothing schedules it, so it only runs when someone triggers an import by hand.

The reverse happens too, and is worse: a merchant can mark a delivered order
unfulfilled, which turns the fulfillment CANCELED -- also silently. The Delivery
Note then still stands here, its stock movement stands, and its supplier remains
invoiceable for goods Shopify now says were never shipped. So a delivered parcel
is still asked about; only a cancelled fulfillment is finished.

A cancellation is acted on, not just reported. Shopify is the source of truth
for whether a fulfillment exists, and there is no unfulfil action anywhere in
the UI -- so a Delivery Note left submitted against a cancelled fulfillment
stayed shipped forever, with its stock movement standing and its supplier still
holding a shipment to invoice for goods that never went out. It is cancelled
instead, which returns the order to pending: the state it is actually in.

The one case still left to a human is a Sales Invoice with a payment against
it. Money arriving for an order Shopify says never shipped is a real books
decision, so that is reported and nothing is unwound.
"""

import frappe

# The only state that will not change again.
#
# DELIVERED is deliberately NOT terminal, which is not obvious: a merchant can
# mark a delivered fulfillment unfulfilled from Shopify's admin, and it becomes
# CANCELED. Confirmed live -- a fulfillment this poll had correctly recorded as
# DELIVERED read CANCELED on Shopify minutes later, with no webhook sent for
# either transition. Treating DELIVERED as final left that Delivery Note
# permanently wrong, still submitted, and its supplier still invoiceable for
# goods Shopify says were never shipped.
#
# ATTEMPTED_DELIVERY is not terminal either: a second attempt usually follows.
_TERMINAL = {"CANCELED", "CANCELLED"}

# Shopify spells it with one L; both are accepted so a spelling change on their
# side cannot silently stop this being recognised as a cancellation.
_CANCELLED = {"CANCELED", "CANCELLED"}

# One Shopify call per batch rather than per Delivery Note.
_BATCH = 50

_FULFILLMENT_STATUS_QUERY = """
query($ids: [ID!]!) {
  nodes(ids: $ids) {
    ... on Fulfillment {
      id
      legacyResourceId
      displayStatus
    }
  }
}
"""


def _pending_delivery_notes(limit=None):
    """Delivery Notes whose Shopify fulfillment could still change state.

    A delivered parcel stays in this set: Shopify lets a merchant mark a
    delivered order unfulfilled, which turns the fulfillment CANCELED, and
    nothing announces it. Only a cancelled fulfillment is genuinely finished.

    Ordered by least-recently-touched so a large backlog spreads across runs
    rather than re-asking about the same rows every hour.
    """
    return frappe.get_all(
        "Delivery Note",
        filters={
            "docstatus": 1,
            "sh_shopify_fulfillment_id": ["is", "set"],
            "sh_delivery_status": ["not in", list(_TERMINAL)],
        },
        fields=["name", "sh_shopify_fulfillment_id", "sh_delivery_status"],
        order_by="modified asc",
        limit=limit,
    )


def _cancel_for_cancelled_fulfillment(dn_name, status):
    """Cancel the Delivery Note behind a fulfillment Shopify has cancelled.

    Shopify is the source of truth for whether a fulfillment exists. Once it
    says CANCELED, keeping the Delivery Note submitted here means the order
    reads as shipped in a portal, its stock movement stands, and its supplier
    still has a shipment to invoice against -- for goods Shopify says never
    went out. There is no unfulfil action anywhere in the UI, so nothing could
    correct that by hand either; the order was stuck shipped forever.

    Cancelling returns the order to pending, which is the state it is actually
    in: nobody has shipped it and it needs fulfilling again.

    A submitted Sales Invoice against the Delivery Note blocks its cancel, so
    that is cancelled first -- but only when nothing has been paid against it.
    A paid invoice is a real books situation (money arrived for an order
    Shopify now says never shipped) and is reported for a human rather than
    unwound automatically.

    from_shopify_sync suppresses on_delivery_note_cancel's push-back: Shopify
    cancelled this fulfillment, so sending it a second cancellation for the
    same one is both wrong and noisy.

    Returns None -- neither done nor needing a human -- when the whole order
    was cancelled rather than just its fulfillment. See below.
    """
    # A cancelled Sales Order is a different situation entirely, and ERPNext
    # will not allow this cancel at all: DeliveryNote.on_cancel runs
    # update_reserved_qty, which throws InvalidStatusError ("Sales Order ... is
    # cancelled or closed") because there is no live order left to adjust a
    # reservation against.
    #
    # Nothing here should fight that. "Return the order to pending" is
    # meaningless for an order nobody can ship, and forcing a stock reversal
    # against a dead order is how a ledger ends up wrong. The Delivery Note
    # stays as the historical record that goods did go out before the order was
    # cancelled -- which is usually exactly what happened.
    #
    # Measured live: 5 of 7 cancelled fulfillments were this case, not an
    # unfulfil. Without this they retried and failed every scheduler tick,
    # burying real failures in the Error Log.
    so_names = frappe.get_all(
        "Delivery Note Item",
        filters={"parent": dn_name, "against_sales_order": ["is", "set"]},
        pluck="against_sales_order",
        distinct=True,
    )
    cancelled_orders = frappe.get_all(
        "Sales Order",
        filters={"name": ["in", list(set(so_names))], "docstatus": 2},
        pluck="name",
    ) if so_names else []
    if cancelled_orders:
        frappe.logger().info(
            f"Shopify reported fulfillment {status} for {dn_name}, but its order "
            f"{', '.join(cancelled_orders)} is already cancelled -- leaving the "
            f"Delivery Note as the record that the goods shipped."
        )
        return None

    invoices = frappe.get_all(
        "Sales Invoice Item",
        filters={"delivery_note": dn_name, "docstatus": 1},
        pluck="parent",
        distinct=True,
    )
    for si_name in set(invoices):
        paid = frappe.get_all(
            "Payment Entry Reference",
            filters={"reference_doctype": "Sales Invoice",
                     "reference_name": si_name, "docstatus": 1},
            limit=1,
        )
        if paid:
            frappe.log_error(
                title=f"Shopify cancelled a fulfillment that is already paid -- {dn_name}",
                message=(
                    f"Shopify now reports this fulfillment as {status}, but "
                    f"{si_name} has a payment against it, so neither it nor the "
                    f"Delivery Note can be reversed automatically.\n\n"
                    f"Money has arrived for an order Shopify says never shipped. "
                    f"Decide what should happen to the payment and the invoice, "
                    f"then cancel them by hand -- the Delivery Note is still "
                    f"submitted until that is done."
                ),
            )
            return False
        si = frappe.get_doc("Sales Invoice", si_name)
        si.flags.from_shopify_sync = True
        si.flags.ignore_permissions = True
        si.cancel()

    dn = frappe.get_doc("Delivery Note", dn_name)
    dn.flags.from_shopify_sync = True
    dn.flags.ignore_permissions = True
    dn.cancel()
    frappe.logger().info(
        f"Shopify reported fulfillment {status} for {dn_name}: cancelled it "
        f"(and {len(set(invoices))} invoice(s)), order returns to pending."
    )
    return True


def sync_delivery_status(limit=None):
    """Refresh sh_delivery_status from Shopify. Safe to run on a schedule.

    Returns a summary rather than raising: this runs unattended, and a
    Shopify-side failure must not take down whatever else the scheduler is
    doing in the same tick.
    """
    settings = frappe.get_cached_doc("Shopify Connector Settings")
    if not settings.is_enabled:
        return {"ok": False, "reason": "connector disabled"}

    pending = _pending_delivery_notes(limit)
    summary = {"ok": True, "checked": len(pending), "updated": 0, "delivered": 0,
               "cancelled": 0, "reverted": 0, "order_cancelled": 0,
               "needs_human": 0, "failed": 0}
    if not pending:
        return summary

    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    client = ShopifyGraphQLClient()

    by_legacy_id = {str(dn.sh_shopify_fulfillment_id): dn for dn in pending}
    ids = list(by_legacy_id)

    for start in range(0, len(ids), _BATCH):
        chunk = ids[start:start + _BATCH]
        # _to_gid in order.utils builds an Order gid specifically, so the
        # Fulfillment one is built here rather than widening a shared helper.
        gids = [f"gid://shopify/Fulfillment/{fid}" for fid in chunk]
        try:
            data = client.execute(_FULFILLMENT_STATUS_QUERY, {"ids": gids})
        except Exception:
            summary["failed"] += len(chunk)
            frappe.log_error(
                title="Shopify: delivery status poll failed for a batch",
                message=f"Fulfillment ids: {chunk}\n\n{frappe.get_traceback()}",
            )
            continue

        for node in data.get("nodes") or []:
            if not node:
                # A fulfillment Shopify no longer returns -- deleted, or the
                # id belongs to another store. Nothing to write.
                continue
            dn = by_legacy_id.get(str(node.get("legacyResourceId") or ""))
            status = (node.get("displayStatus") or "").upper()
            if not dn or not status or status == (dn.sh_delivery_status or "").upper():
                continue
            if status in _CANCELLED:
                summary["cancelled"] += 1
                # The status is written only AFTER the cancel succeeds.
                # CANCELED is in _TERMINAL, so writing it first would drop
                # this Delivery Note out of _pending_delivery_notes forever --
                # and a cancel that failed (a paid invoice refusing it, a
                # linked Purchase Invoice, a locked Stock Ledger) would leave
                # the DN submitted and never be retried. That is the exact
                # stuck-forever state this whole path exists to end.
                try:
                    outcome = _cancel_for_cancelled_fulfillment(dn.name, status)
                    if outcome is None:
                        # The whole order was cancelled, not just its
                        # fulfillment. There is nothing to do and nothing a
                        # human can act on, so mark it terminal: this must not
                        # come back on every tick.
                        frappe.db.set_value(
                            "Delivery Note", dn.name, "sh_delivery_status", status,
                            update_modified=False,
                        )
                        summary["updated"] += 1
                        summary["order_cancelled"] += 1
                        frappe.db.commit()
                    elif outcome:
                        frappe.db.set_value(
                            "Delivery Note", dn.name, "sh_delivery_status", status,
                            update_modified=False,
                        )
                        summary["updated"] += 1
                        summary["reverted"] += 1
                        frappe.db.commit()
                    else:
                        # Reported for a human and deliberately NOT marked
                        # terminal, so the next tick asks again -- once the
                        # payment is dealt with it resolves on its own.
                        summary["needs_human"] += 1
                        frappe.db.rollback()
                except Exception:
                    # Must not stop the rest of the batch: every other parcel
                    # in this run still needs its real status. Status stays
                    # unwritten so this is retried next tick.
                    summary["failed"] += 1
                    frappe.db.rollback()
                    frappe.log_error(
                        title=f"Shopify: could not cancel {dn.name} after its fulfillment was cancelled",
                        message=frappe.get_traceback(),
                    )
                continue

            frappe.db.set_value("Delivery Note", dn.name, "sh_delivery_status", status)
            summary["updated"] += 1
            if status == "DELIVERED":
                summary["delivered"] += 1

    frappe.db.commit()
    return summary


# ── Order status reconcile ────────────────────────────────────────────────────
#
# Same reasoning as the delivery poll above, one level up: an order's own state
# on Shopify does not reliably reach us either, and for orders the failure is
# worse than a stale field.
#
# The orders/* webhooks are not a guarantee:
#   - A cancel can lose a write race. A concurrent orders/updated for the same
#     order saves it mid-cancel and so.cancel() raises TimestampMismatchError.
#     Retrying helps, but a retry that loses again leaves nothing behind.
#   - handle_order_webhook catches every exception, logs it and answers 200, so
#     Shopify counts the delivery as successful and never redelivers. A failed
#     cancel is therefore permanent, not deferred.
#   - A webhook can simply not arrive.
#
# Confirmed live on an order (a Sales Order): cancelled on Shopify at
# 15:52Z, the webhook fired hours later, lost the race twice 30ms apart, and
# the Sales Order stayed Completed against an order Shopify had cancelled.
# Nothing anywhere would ever have corrected it.
#
# So order state is reconciled rather than trusted. Asking turns a lost race
# from permanent corruption into a delay of one scheduler tick.
#
# One-directional: this only applies to Alaiy OS what Shopify already says,
# and never pushes a state back out.

# Newer than this and a webhook still has a fair chance of arriving on its own;
# older and the order is cold. Keeps each run bounded on years of history.
_ORDER_LOOKBACK_DAYS = 30

_ORDER_STATUS_QUERY = """
query($ids: [ID!]!) {
  nodes(ids: $ids) {
    ... on Order {
      id
      legacyResourceId
      cancelledAt
      cancelReason
      displayFinancialStatus
      displayFulfillmentStatus
    }
  }
}
"""


def _open_shopify_orders(limit=None):
    """Submitted Sales Orders from Shopify whose state could still change here.

    docstatus 1 only: a draft was never submitted and a 2 is already cancelled,
    so neither needs asking about. Least-recently-touched first so a large
    backlog spreads across runs instead of re-asking about the same rows.
    """
    return frappe.get_all(
        "Sales Order",
        filters={
            "docstatus": 1,
            "sh_shopify_order_id": ["is", "set"],
            "transaction_date": [
                ">=", frappe.utils.add_days(frappe.utils.nowdate(), -_ORDER_LOOKBACK_DAYS)
            ],
        },
        fields=["name", "sh_shopify_order_id"],
        order_by="modified asc",
        limit=limit,
    )


def sync_order_status(limit=None):
    """Apply Shopify's own order state to Sales Orders. Safe on a schedule.

    Today this cancels what Shopify has cancelled -- the one divergence that
    silently corrupts state rather than just delaying it. The financial and
    fulfillment statuses are fetched alongside so adding a check for either is
    a branch here rather than another Shopify round-trip.

    Returns a summary rather than raising: runs unattended, and a Shopify-side
    failure must not take down the rest of the scheduler tick.
    """
    settings = frappe.get_cached_doc("Shopify Connector Settings")
    if not settings.is_enabled:
        return {"ok": False, "reason": "connector disabled"}

    open_orders = _open_shopify_orders(limit)
    summary = {"ok": True, "checked": len(open_orders), "cancelled": 0, "failed": 0}
    if not open_orders:
        return summary

    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.order.webhook import _cancel_sales_order

    client = ShopifyGraphQLClient()
    by_legacy_id = {str(o.sh_shopify_order_id): o.name for o in open_orders}
    ids = list(by_legacy_id)

    for start in range(0, len(ids), _BATCH):
        chunk = ids[start:start + _BATCH]
        gids = [f"gid://shopify/Order/{oid}" for oid in chunk]
        try:
            data = client.execute(_ORDER_STATUS_QUERY, {"ids": gids})
        except Exception:
            summary["failed"] += len(chunk)
            frappe.log_error(
                title="Shopify: order status poll failed for a batch",
                message=f"Order ids: {chunk}\n\n{frappe.get_traceback()}",
            )
            continue

        for node in data.get("nodes") or []:
            if not node or not node.get("cancelledAt"):
                continue
            so_name = by_legacy_id.get(str(node.get("legacyResourceId") or ""))
            if not so_name:
                continue
            # Re-read rather than trusting the list: a webhook may have
            # cancelled it since, and cancelling twice throws.
            if frappe.db.get_value("Sales Order", so_name, "docstatus") != 1:
                continue
            try:
                _cancel_sales_order(so_name)
                summary["cancelled"] += 1
                frappe.logger().info(
                    f"Shopify order reconcile: cancelled {so_name} "
                    f"(Shopify cancelledAt {node['cancelledAt']}, "
                    f"reason {node.get('cancelReason')})"
                )
            except Exception:
                # _cancel_sales_order already logs what it can explain (a
                # linked invoice that cannot be cancelled, a lost race).
                # Anything here is unexpected and must not stop the remaining
                # orders in this run from being corrected.
                summary["failed"] += 1
                frappe.db.rollback()
                frappe.log_error(
                    title=f"Shopify: order reconcile failed for {so_name}",
                    message=frappe.get_traceback(),
                )

    return summary
