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

This asks Shopify directly, for the small set of Delivery Notes that could still
change: submitted, carrying a Shopify fulfillment id, and not yet at a terminal
state.
"""

import frappe

# States that will not change again, so there is nothing left to poll for.
# ATTEMPTED_DELIVERY is deliberately NOT terminal -- a second attempt usually
# follows, and the parcel is still in play until it lands.
_TERMINAL = {"DELIVERED", "CANCELED", "CANCELLED"}

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
    """Delivery Notes whose parcel state could still change.

    Cancelled notes are excluded, and so is anything already at a terminal
    state -- re-asking Shopify about a parcel that has already been delivered
    is a call that can never change an answer.
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
    summary = {"ok": True, "checked": len(pending), "updated": 0, "delivered": 0, "failed": 0}
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
            frappe.db.set_value("Delivery Note", dn.name, "sh_delivery_status", status)
            summary["updated"] += 1
            if status == "DELIVERED":
                summary["delivered"] += 1

    frappe.db.commit()
    return summary
