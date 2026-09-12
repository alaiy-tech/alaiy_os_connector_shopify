"""
The backstop that makes a refund visible when no webhook arrived.

The refund webhook is the fast path and creates the Credit Note. It is not
a guarantee: it can be dropped, fire while the connector is disabled, or
have happened before the order was ever imported. When it does not arrive
the Sales Order keeps reading paid, and the admin Returns page -- which
keys off sh_financial_status, not off our Credit Note, because most refunds
never produce one -- shows nothing at all.

    python -m unittest alaiy_os_connector_shopify.shopify.tests.test_refund_sync
"""

import ast
import pathlib
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_STATUS = _ROOT / "shopify" / "order" / "delivery_status.py"
_HOOKS = _ROOT / "hooks.py"


def _source():
    return _STATUS.read_text(encoding="utf-8")


def _function(name):
    tree = ast.parse(_source())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} not found")


class RefundSync(unittest.TestCase):
    def test_the_sweep_is_scheduled(self):
        """Unscheduled, this catches nothing -- the whole point is the
        webhook that never came."""
        self.assertIn("sync_refund_status", _HOOKS.read_text(encoding="utf-8"))

    def test_it_looks_at_orders_the_other_sweep_ignores(self):
        """sync_order_status only asks about orders still OPEN here, because
        it exists to close them. Refunds land on delivered, Completed orders
        -- exactly the set that sweep skips."""
        body = ast.dump(_function("sync_refund_status"))
        self.assertIn("docstatus", body)
        # It must NOT reuse the open-orders selector.
        self.assertNotIn("_open_shopify_orders", body)

    def test_it_skips_orders_already_known_refunded(self):
        """Re-asking Shopify about a refund already recorded is a wasted
        API call on every run, forever."""
        body = ast.dump(_function("sync_refund_status"))
        self.assertIn("refunded", body)

    def test_it_records_the_refund_but_does_not_invent_a_credit_note(self):
        """handle_refund_webhook needs the refund's line-item breakdown to
        reverse stock and bill correctly. An order-level status carries no
        quantities, so building one from it would guess."""
        fn = _function("_sync_financial_status")
        # Calls, not the docstring -- which legitimately names the documents
        # this must NOT create, and would match a substring search.
        calls = {
            node.func.attr for node in ast.walk(fn)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        for forbidden in ("new_doc", "insert", "submit", "save"):
            self.assertNotIn(forbidden, calls, f"must not {forbidden} anything")

    def test_it_writes_the_field_the_returns_page_reads(self):
        body = ast.dump(_function("_sync_financial_status"))
        self.assertIn("sh_financial_status", body)

    def test_it_writes_the_field_directly_not_through_a_save(self):
        """Saving a submitted Sales Order to change one Shopify-owned status
        risks a TimestampMismatch against whatever else touches that row,
        and no hook needs to fire for it."""
        body = ast.dump(_function("_sync_financial_status"))
        self.assertIn("set_value", body)
        self.assertNotIn("get_doc", body)

    def test_it_does_not_rewrite_an_unchanged_status(self):
        """Every run would otherwise touch every order it checked."""
        self.assertIn(
            "sh_financial_status\") or \"\") == status",
            _source(),
            "must compare before writing",
        )

    def test_the_open_order_sweep_records_it_too(self):
        """The same query already carried displayFinancialStatus and nothing
        read it -- that omission is what let a refunded open order stay
        reading paid."""
        body = ast.dump(_function("sync_order_status"))
        self.assertIn("_sync_financial_status", body)


if __name__ == "__main__":
    unittest.main()
