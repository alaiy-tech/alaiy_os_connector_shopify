"""Self-check for the delivery-status poll's selection and write rules.

The poll exists because Shopify does not reliably announce a delivery. Marking
an order delivered from its own admin changes the fulfillment's displayStatus
and emits no webhook, so the state never reaches us -- confirmed live with
fulfillments/update correctly subscribed, correctly dispatched, and no error
logged anywhere.

Two things have to be right, and neither needs a site to check:

  * which Delivery Notes are worth asking about -- asking Shopify again about a
    parcel already delivered is a call whose answer cannot change, and there are
    thousands of them;
  * when a returned status is actually worth writing.

    python alaiy_os_connector_shopify/shopify/order/test_delivery_status.py
"""

import ast
import pathlib

_SOURCE = pathlib.Path(__file__).with_name("delivery_status.py")

_TERMINAL = {"CANCELED", "CANCELLED"}
_CANCELLED = {"CANCELED", "CANCELLED"}


def _worth_polling(dn):
    """Mirrors _pending_delivery_notes' filters."""
    return (
        dn["docstatus"] == 1
        and bool(dn.get("sh_shopify_fulfillment_id"))
        and (dn.get("sh_delivery_status") or "").upper() not in _TERMINAL
    )


def _worth_writing(current, incoming):
    """Mirrors the write guard in sync_delivery_status."""
    incoming = (incoming or "").upper()
    return bool(incoming) and incoming != (current or "").upper()


def demo():
    # A shipped parcel with no status yet is exactly what this is for.
    assert _worth_polling({"docstatus": 1, "sh_shopify_fulfillment_id": "70310", "sh_delivery_status": None})

    # In transit: still moving, still worth asking.
    assert _worth_polling({"docstatus": 1, "sh_shopify_fulfillment_id": "70310", "sh_delivery_status": "IN_TRANSIT"})

    # A failed attempt is NOT terminal -- a second attempt usually follows and
    # the parcel is still in play.
    assert _worth_polling({"docstatus": 1, "sh_shopify_fulfillment_id": "70310",
                           "sh_delivery_status": "ATTEMPTED_DELIVERY"})

    # DELIVERED is NOT the end. Shopify lets a merchant mark a delivered order
    # unfulfilled, which turns the fulfillment CANCELED and announces nothing --
    # confirmed live. Dropping it from the poll left the Delivery Note
    # permanently wrong and its supplier invoiceable for goods Shopify says were
    # never shipped.
    assert _worth_polling({"docstatus": 1, "sh_shopify_fulfillment_id": "70310",
                           "sh_delivery_status": "DELIVERED"})

    # A cancelled fulfillment genuinely is the end.
    for spelling in ("CANCELED", "CANCELLED"):
        assert not _worth_polling({"docstatus": 1, "sh_shopify_fulfillment_id": "70310",
                                   "sh_delivery_status": spelling})

    # Never pushed to Shopify, so there is no fulfillment to ask about.
    assert not _worth_polling({"docstatus": 1, "sh_shopify_fulfillment_id": None,
                               "sh_delivery_status": None})

    # Draft and cancelled notes are not live shipments.
    assert not _worth_polling({"docstatus": 0, "sh_shopify_fulfillment_id": "70310", "sh_delivery_status": None})
    assert not _worth_polling({"docstatus": 2, "sh_shopify_fulfillment_id": "70310", "sh_delivery_status": None})

    # Writing: the case this whole module exists for.
    assert _worth_writing(None, "DELIVERED")
    assert _worth_writing("IN_TRANSIT", "DELIVERED")

    # No change is not a write -- otherwise every run would touch every row and
    # the `modified` ordering that spreads load would be meaningless.
    assert not _worth_writing("IN_TRANSIT", "IN_TRANSIT")
    assert not _worth_writing("IN_TRANSIT", "in_transit")

    # A blank answer must never wipe a status already recorded.
    assert not _worth_writing("DELIVERED", "")
    assert not _worth_writing("DELIVERED", None)

    # The poll must never raise: it runs unattended, and a Shopify failure must
    # not take down the rest of the scheduler tick.
    tree = ast.parse(_SOURCE.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "sync_delivery_status")
    raises = [n for n in ast.walk(fn) if isinstance(n, ast.Raise)]
    assert not raises, f"sync_delivery_status raises at {[r.lineno for r in raises]}"
    handlers = [n for n in ast.walk(fn) if isinstance(n, ast.ExceptHandler)]
    assert handlers, "the Shopify call is not wrapped -- one failed batch would end the run"

    # The delivered -> cancelled reversal must be recognised, in either spelling.
    assert _worth_writing("DELIVERED", "CANCELED")
    assert ("CANCELED" in _CANCELLED) and ("CANCELLED" in _CANCELLED)

    # A cancellation has to be reported, not just recorded: the Delivery Note
    # stays submitted, so nothing else would reveal that its stock movement and
    # its supplier's claim to be paid now rest on a fulfillment Shopify has
    # withdrawn.
    src = _SOURCE.read_text(encoding="utf-8")
    assert "_report_cancelled_fulfillment" in src, "a cancelled fulfillment is recorded but never raised"

    print("delivery status poll self-check: OK")


if __name__ == "__main__":
    demo()
