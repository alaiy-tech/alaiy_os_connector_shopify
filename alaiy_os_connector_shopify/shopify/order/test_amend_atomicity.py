"""Self-check: a cancel must not be committed before its replacement exists.

Reconciling line items on a submitted Sales Order is cancel-then-amend: the
original is cancelled and a new amended document takes its place. Committing
between those two steps makes the cancel permanent on its own, so any failure
while building the replacement -- a validation error, a mandatory field, a
killed worker -- leaves the order cancelled with nothing replacing it. The
webhook caller swallows the exception, so it happens with only an Error Log
entry.

Both halves must ride one transaction: Frappe rolls the request back on an
exception, leaving the original submitted and untouched, and Shopify's next
delivery retries the whole exchange from a consistent state.

Asserted structurally rather than by running it -- the real function needs a
site, a Shopify payload and a submitted Sales Order.

    python alaiy_os_connector_shopify/shopify/order/test_amend_atomicity.py
"""

import ast
import pathlib

_SOURCE = pathlib.Path(__file__).with_name("line_items.py")


def _function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} not found")


def _line_of(node, predicate):
    """First line inside `node` whose AST matches `predicate`."""
    for child in ast.walk(node):
        if predicate(child):
            return child.lineno
    return None


def _is_call(node, obj_attr, attr):
    """frappe.db.commit() -> _is_call(n, "db", "commit")"""
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    return (isinstance(f, ast.Attribute) and f.attr == attr
            and isinstance(f.value, ast.Attribute) and f.value.attr == obj_attr)


def _method_call_line(node, receiver, method):
    """Line of `receiver.method()`, e.g. amended.submit()."""
    for child in ast.walk(node):
        if (isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute)
                and child.func.attr == method
                and isinstance(child.func.value, ast.Name)
                and child.func.value.id == receiver):
            return child.lineno
    return None


def demo():
    tree = ast.parse(_SOURCE.read_text(encoding="utf-8"))
    fn = _function(tree, "_sync_order_line_items")

    cancel_line = _method_call_line(fn, "so", "cancel")
    assert cancel_line, "so.cancel() not found -- has this function been restructured?"

    amended_insert = _method_call_line(fn, "amended", "insert")
    amended_submit = _method_call_line(fn, "amended", "submit")
    assert amended_insert and amended_submit, "the amend half is missing"

    commits = [
        c.lineno for c in ast.walk(fn) if _is_call(c, "db", "commit")
    ]

    # The replacement must be built and submitted before any commit that
    # follows the cancel -- otherwise the cancel can stand alone.
    between = [c for c in commits if cancel_line < c < amended_insert]

    # One exception is legitimate: a fully cancelled Shopify order zeroes every
    # line, so there is nothing to amend into and the cancelled original IS the
    # end state. That commit sits inside the `if not amended.items` branch,
    # which returns immediately -- so it is allowed only if it is guarded.
    guarded = set()
    for child in ast.walk(fn):
        if isinstance(child, ast.If):
            for inner in ast.walk(child):
                if _is_call(inner, "db", "commit"):
                    guarded.add(inner.lineno)

    unguarded_between = [c for c in between if c not in guarded]
    assert not unguarded_between, (
        f"frappe.db.commit() at {unguarded_between} runs after so.cancel() "
        f"(line {cancel_line}) and before amended.insert() (line {amended_insert}). "
        f"That makes the cancel permanent on its own; a failure building the "
        f"replacement then leaves the order cancelled with nothing to replace it."
    )

    # And the final commit must come after the replacement is submitted.
    after_submit = [c for c in commits if c > amended_submit]
    assert after_submit, (
        "no frappe.db.commit() after amended.submit() -- the amended order "
        "would never be persisted"
    )

    print("amend atomicity self-check: OK")


if __name__ == "__main__":
    demo()
