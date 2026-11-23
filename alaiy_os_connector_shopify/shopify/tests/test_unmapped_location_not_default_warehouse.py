"""Stock at a Shopify location the store never mapped must not land in the
default warehouse when the store maps its other locations.

A supplier's quantity opened at the default (HQ) warehouse because its
location had no map row, and routing then read it as HQ's own stock. Pinned:
a store with a location map gets None / no opening row for an unmapped
location; a store with no map at all keeps the single-warehouse behaviour.

Functions are pulled out of the source and run with stand-ins, since what is
pinned is the decision, not a database write.
"""

import ast
import os
import sys
import types
import unittest

_HERE = os.path.dirname(__file__)


def _fn(path, name):
    full = os.path.join(_HERE, "..", path)
    with open(full, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return compile(ast.Module(body=[node], type_ignores=[]), full, "exec")


class _Settings:
    def __init__(self, rows, default="HQ"):
        self.rows = rows
        self.sh_default_warehouse = default
        self.name = "store"

    def get(self, key):
        return self.rows if key == "sh_location_map" else None


def _opening(settings, levels, mapped):
    """_resolve_opening_stock_rows with `mapped` = {location id: warehouse}."""
    logged = []
    frappe = types.SimpleNamespace(
        db=types.SimpleNamespace(
            get_value=lambda doctype, name, field=None: 0,
            exists=lambda doctype, name: True),
        log_error=lambda title, message: logged.append(title),
    )
    fake = types.ModuleType("alaiy_os_connector_shopify.shopify.order.warehouse")
    fake._resolve_warehouse_for_location = lambda location_id, s: mapped.get(location_id)
    sys.modules[fake.__name__] = fake
    ns = {"frappe": frappe}
    exec(_fn("product/stock.py", "_resolve_opening_stock_rows"), ns)
    return ns["_resolve_opening_stock_rows"](5, settings, levels), logged


def _pull_resolver(settings, locations, mapped_wh):
    """inventory_sync._resolve_warehouse_for_location."""
    def get_value(doctype, filters, field=None):
        if doctype == "Shopify Location":
            return locations.get(filters["sh_location_id"])
        return mapped_wh.get(filters["shopify_location"])

    ns = {
        "frappe": types.SimpleNamespace(db=types.SimpleNamespace(get_value=get_value)),
        "owned_by": lambda doctype, conn, filters: dict(filters),
        "connections": types.SimpleNamespace(
            resolve=lambda c: settings, enabled_connection=lambda: settings),
    }
    exec(_fn("inventory_sync.py", "_resolve_warehouse_for_location"), ns)
    return ns["_resolve_warehouse_for_location"]


class OpeningStock(unittest.TestCase):
    def test_unmapped_location_with_a_map_gets_no_default_row(self):
        s = _Settings([object()])
        rows, logged = _opening(s, [("9", 11)], {})
        self.assertEqual(rows, [])
        self.assertEqual(len(logged), 1)

    def test_store_with_no_map_keeps_the_default_warehouse(self):
        rows, logged = _opening(_Settings([]), [("9", 11)], {})
        self.assertEqual(rows, [("HQ", 5)])
        self.assertEqual(logged, [])

    def test_mapped_location_is_unchanged(self):
        rows, _ = _opening(_Settings([object()]), [("1", 7)], {"1": "SUP"})
        self.assertEqual(rows, [("SUP", 7)])

    def test_no_levels_keeps_the_default_warehouse(self):
        rows, _ = _opening(_Settings([object()]), None, {})
        self.assertEqual(rows, [("HQ", 5)])


class PullResolver(unittest.TestCase):
    def test_unmapped_location_with_a_map_resolves_to_nothing(self):
        r = _pull_resolver(_Settings([object()]), {"9": "LOC9"}, {})
        self.assertIsNone(r("9"))

    def test_unmapped_location_without_a_map_uses_the_default(self):
        r = _pull_resolver(_Settings([]), {"9": "LOC9"}, {})
        self.assertEqual(r("9"), "HQ")

    def test_mapped_location_resolves_to_its_warehouse(self):
        r = _pull_resolver(_Settings([object()]), {"1": "LOC1"}, {"LOC1": "SUP"})
        self.assertEqual(r("1"), "SUP")

    def test_unknown_location_resolves_to_nothing(self):
        r = _pull_resolver(_Settings([object()]), {}, {})
        self.assertIsNone(r("5"))


if __name__ == "__main__":
    unittest.main()
