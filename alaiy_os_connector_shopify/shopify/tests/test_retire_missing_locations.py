"""_retire_missing_locations: a location Shopify no longer returns stops being
active here.

The location sync only updated locations Shopify still listed, so one that was
deleted or lost its fulfillment service stayed active forever and items kept
pointing at it. These pin the decision (retire, keep, never on an empty
listing), not the database write, so the function is pulled out of
inventory_sync.py and run with stand-ins.
"""

import ast
import os
import types
import unittest

_SOURCE = os.path.join(os.path.dirname(__file__), "..", "inventory_sync.py")


def _load(rows):
    """The function plus the names it saved. rows: [(doc name, sh_location_id)]."""
    with open(_SOURCE, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    fn = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "_retire_missing_locations"
    )
    code = compile(ast.Module(body=[fn], type_ignores=[]), _SOURCE, "exec")

    saved = []

    class _Doc:
        def __init__(self, name):
            self.name = name
            self.flags = types.SimpleNamespace()

        def save(self):
            saved.append((self.name, self.is_active))

    frappe = types.SimpleNamespace(
        get_all=lambda doctype, filters=None, fields=None: [
            types.SimpleNamespace(name=n, sh_location_id=i) for n, i in rows],
        get_doc=lambda doctype, name: _Doc(name),
    )
    ns = {"frappe": frappe, "owned_by": lambda doctype, conn, filters: dict(filters)}
    exec(code, ns)
    return ns["_retire_missing_locations"], saved


class RetireMissingLocations(unittest.TestCase):
    def test_location_missing_from_shopify_is_retired(self):
        fn, saved = _load([("a", "1"), ("b", "2")])
        self.assertEqual(fn("store", {"1"}), 1)
        self.assertEqual(saved, [("b", 0)])

    def test_locations_still_listed_are_kept(self):
        fn, saved = _load([("a", "1"), ("b", "2")])
        self.assertEqual(fn("store", {"1", "2"}), 0)
        self.assertEqual(saved, [])

    def test_empty_listing_retires_nothing(self):
        fn, saved = _load([("a", "1"), ("b", "2")])
        self.assertEqual(fn("store", set()), 0)
        self.assertEqual(saved, [])

    def test_ids_compare_as_text(self):
        fn, saved = _load([("a", 1)])
        self.assertEqual(fn("store", {"1"}), 0)
        self.assertEqual(saved, [])


if __name__ == "__main__":
    unittest.main()
