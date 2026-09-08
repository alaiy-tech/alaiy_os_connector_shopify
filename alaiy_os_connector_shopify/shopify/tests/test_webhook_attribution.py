"""
A webhook's store reaches the handlers that act on it.

The receiver resolves the store from X-Shopify-Shop-Domain and verifies the
HMAC against that store's secret alone. That answer used to stop there:
_dispatch took only the topic and the payload, so the handlers looked records
up by Shopify id with no store attached.

For refunds that was a money bug. A Shopify order id is only unique inside one
shop, so a refund for one seller's order 1001 could resolve another seller's
Sales Order -- and the refund path posts a Credit Note and a Payment Entry
against whatever it finds.

These pin the wiring: every enqueue carries the store, and every handler
accepts it.
"""

import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _tree(relative):
    return ast.parse((ROOT / relative).read_text(encoding="utf-8"))


class TestDispatchCarriesTheStore(unittest.TestCase):
    def test_the_receiver_passes_the_resolved_connection_to_dispatch(self):
        tree = _tree("api/webhooks.py")
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_dispatch"]
        self.assertTrue(calls, "_dispatch is never called")
        for call in calls:
            self.assertGreaterEqual(
                len(call.args), 3,
                "_dispatch must be given the connection, not just topic and payload")

    def test_every_enqueued_webhook_job_is_given_the_store(self):
        tree = _tree("api/webhooks.py")
        enqueues = [n for n in ast.walk(tree)
                    if isinstance(n, ast.Call)
                    and getattr(n.func, "attr", "") == "enqueue"]
        self.assertTrue(enqueues)
        for call in enqueues:
            passed = {k.arg for k in call.keywords}
            method = call.args[0].value if call.args else "?"
            self.assertIn("connection", passed,
                          f"{method} is enqueued without its store")


class TestHandlersAcceptTheStore(unittest.TestCase):
    HANDLERS = {
        "shopify/order/webhook.py": ["handle_order_webhook",
                                     "handle_fulfillment_webhook"],
        "shopify/order/returns.py": ["handle_refund_webhook"],
        "shopify/product/webhooks.py": ["handle_product_webhook"],
        "shopify/product/collections.py": ["handle_collection_webhook"],
        "shopify/inventory_sync.py": ["handle_inventory_level_webhook"],
    }

    def test_each_handler_takes_a_connection(self):
        for relative, names in self.HANDLERS.items():
            tree = _tree(relative)
            found = {n.name: n for n in ast.walk(tree)
                     if isinstance(n, ast.FunctionDef)}
            for name in names:
                self.assertIn(name, found, f"{name} missing from {relative}")
                params = [a.arg for a in found[name].args.args]
                self.assertIn("connection", params,
                              f"{name} cannot be told which store it is for")


class TestMoneyPathsResolveWithinTheStore(unittest.TestCase):
    def test_the_refund_path_scopes_its_sales_order_lookup(self):
        # The defect this whole change exists for. Unscoped, this resolves
        # another seller's Sales Order and credits their books.
        tree = _tree("shopify/order/returns.py")
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_process_refund")
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                 and getattr(n.func, "id", "") == "get_active_sales_order"]
        self.assertTrue(calls, "the refund path no longer resolves a Sales Order")
        for call in calls:
            self.assertEqual(
                len(call.args), 2,
                "get_active_sales_order must be scoped to the refund's store")

    def test_cancel_update_and_tracking_scope_theirs_too(self):
        for relative, fname in (
            ("shopify/order/webhook.py", "_cancel_order"),
            ("shopify/order/update.py", "_update_order_unlocked"),
            ("shopify/order/delivery_notes.py", "_sync_tracking"),
        ):
            tree = _tree(relative)
            fn = next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == fname)
            for call in [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                         and getattr(n.func, "id", "") == "get_active_sales_order"]:
                self.assertEqual(len(call.args), 2,
                                 f"{fname} resolves an order without its store")


if __name__ == "__main__":
    unittest.main()
