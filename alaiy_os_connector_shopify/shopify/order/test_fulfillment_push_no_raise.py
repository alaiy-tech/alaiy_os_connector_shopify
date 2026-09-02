"""Self-check: a failed fulfillment push must never raise.

By the time push_delivery_note_fulfillment runs, the goods have physically
shipped, a carrier label exists and the Delivery Note is submitted. Anything
raised from there unwinds the whole request in Frappe, so a Shopify-side
mismatch took the Sales Order, its Purchase Orders and the Delivery Note with
it -- confirmed live: a customer refunded an order minutes before the supplier
fulfilled it, which closed Shopify's fulfillment orders, nothing matched, and
the push threw. FedEx had already issued tracking 794858949598 and the parcel
was in the carrier's network; the order existed nowhere in ERPNext afterwards,
and the only trace was an Error Log nobody was watching.

This asserts the shape of the module rather than running it: the real function
needs a site, a Shopify client and a submitted Delivery Note.

    python alaiy_os_connector_shopify/shopify/order/test_fulfillment_push_no_raise.py
"""

import ast
import pathlib

_SOURCE = pathlib.Path(__file__).with_name("fulfillment_push.py")

# Guards that run BEFORE anything has shipped -- these are correct as throws,
# because nothing has been dispatched yet and the caller should stop.
_PRE_SHIPMENT_GUARDS = 3


def _function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} not found")


def _throws_in(node):
    """Line numbers of every frappe.throw call inside a function."""
    out = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if (isinstance(func, ast.Attribute) and func.attr == "throw"
                and isinstance(func.value, ast.Name) and func.value.id == "frappe"):
            out.append(child.lineno)
    return out


def demo():
    tree = ast.parse(_SOURCE.read_text(encoding="utf-8"))
    fn = _function(tree, "push_delivery_note_fulfillment")

    throws = _throws_in(fn)

    # The only remaining throws must be the pre-shipment guards at the top of
    # the function: already linked, no Sales Order, no Shopify order. Each one
    # fires before any Shopify call and before anything is written.
    assert len(throws) == _PRE_SHIPMENT_GUARDS, (
        f"expected {_PRE_SHIPMENT_GUARDS} pre-shipment guards, found {len(throws)} "
        f"frappe.throw calls at lines {throws}. A throw after the goods have "
        f"shipped destroys the order it was shipping."
    )

    # They must all sit above the point where the Shopify client is built --
    # everything after that is post-dispatch territory.
    client_line = next(
        (n.lineno for n in ast.walk(fn)
         if isinstance(n, ast.Assign)
         and any(isinstance(t, ast.Name) and t.id == "client" for t in n.targets)),
        None,
    )
    assert client_line, "could not locate the Shopify client assignment"
    assert all(t < client_line for t in throws), (
        f"a frappe.throw at {[t for t in throws if t > client_line]} runs after the "
        f"Shopify client is built, which is after the shipment exists"
    )

    # And the failure paths must return a result rather than raising.
    returns = [
        n for n in ast.walk(fn)
        if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict)
    ]
    assert returns, "no dict-returning failure path found -- a push that cannot " \
                    "match must report, not raise"

    print("fulfillment push no-raise self-check: OK")


if __name__ == "__main__":
    demo()
