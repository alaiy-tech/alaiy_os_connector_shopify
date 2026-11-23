"""A credit note must not link a cancelled Sales Order, and a long product
title must be fitted to the 140-character field on the webhook path.

Pulled out of the source and run with stand-ins -- the decision is pinned, not
a database write.
"""

import ast
import os
import types
import unittest

_BASE = os.path.join(os.path.dirname(__file__), "..")


def _fn(path, name):
    full = os.path.join(_BASE, path)
    with open(full, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return compile(ast.Module(body=[node], type_ignores=[]), full, "exec")


class _Row(dict):
    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value


def _unlink(rows, docstatus_by_so):
    ns = {"frappe": types.SimpleNamespace(db=types.SimpleNamespace(
        get_value=lambda doctype, name, field: docstatus_by_so.get(name)))}
    exec(_fn("order/returns.py", "_unlink_cancelled_sales_orders"), ns)
    doc = types.SimpleNamespace(items=rows)
    ns["_unlink_cancelled_sales_orders"](doc)
    return rows


class UnlinkCancelledSalesOrders(unittest.TestCase):
    def test_cancelled_order_link_is_cleared(self):
        rows = _unlink([_Row(sales_order="SO-1", so_detail="d1")], {"SO-1": 2})
        self.assertIsNone(rows[0].sales_order)
        self.assertIsNone(rows[0].so_detail)

    def test_live_order_link_is_kept(self):
        rows = _unlink([_Row(sales_order="SO-1", so_detail="d1")], {"SO-1": 1})
        self.assertEqual((rows[0].sales_order, rows[0].so_detail), ("SO-1", "d1"))

    def test_row_without_an_order_is_untouched(self):
        rows = _unlink([_Row(sales_order=None, so_detail=None)], {})
        self.assertIsNone(rows[0].sales_order)

    def test_only_the_cancelled_row_changes(self):
        rows = _unlink(
            [_Row(sales_order="SO-1", so_detail="d1"), _Row(sales_order="SO-2", so_detail="d2")],
            {"SO-1": 2, "SO-2": 1})
        self.assertIsNone(rows[0].sales_order)
        self.assertEqual(rows[1].sales_order, "SO-2")


class FitItemName(unittest.TestCase):
    def test_long_title_is_cut_to_the_field_limit(self):
        ns = {}
        with open(os.path.join(_BASE, "product", "utils.py"), encoding="utf-8") as handle:
            tree = ast.parse(handle.read())
        keep = [n for n in tree.body
                if (isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "_ITEM_NAME_MAX_LENGTH" for t in n.targets))
                or (isinstance(n, ast.FunctionDef) and n.name == "_fit_item_name")]
        exec(compile(ast.Module(body=keep, type_ignores=[]), "utils", "exec"), ns)
        self.assertEqual(len(ns["_fit_item_name"]("x" * 300)), 140)
        self.assertEqual(ns["_fit_item_name"]("short"), "short")
        self.assertEqual(ns["_fit_item_name"](None), "")


if __name__ == "__main__":
    unittest.main()
