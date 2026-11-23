"""_refresh_item_locations: an already-imported product follows its stock to a
new Shopify location.

The product fingerprint leaves inventory out on purpose, so a product whose
stock moved to another location looks unchanged and the importer skipped it,
leaving Item.shopify_location on the old location. These pin the refresh that
runs in that unchanged branch.

The function is pulled out of importer.py and run with stand-ins, because what
is pinned is the decision (move, leave alone, never blank), not a database
write. The save path needs a real bench.
"""

import ast
import os
import types
import unittest

_IMPORTER = os.path.join(os.path.dirname(__file__), "..", "product", "importer.py")


def _load(items, resolved, product_location, has_field=True):
    """The refresh function plus a record of what it saved.

    items: {variant id: (item code, current location)}
    resolved: {item code: location the per-variant resolution returns, or None}
    """
    source = open(_IMPORTER, encoding="utf-8").read()
    fn = next(
        n for n in ast.parse(source).body
        if isinstance(n, ast.FunctionDef) and n.name == "_refresh_item_locations"
    )
    code = compile(ast.Module(body=[fn], type_ignores=[]), _IMPORTER, "exec")

    saved, supplier_synced = [], []
    state = {code_: loc for code_, loc in items.values()}

    class _Doc:
        def __init__(self, name):
            self.name = name
            self.flags = types.SimpleNamespace()

        def save(self):
            saved.append((self.name, self.shopify_location))
            state[self.name] = self.shopify_location

    frappe = types.SimpleNamespace(
        get_meta=lambda doctype: types.SimpleNamespace(
            get_field=lambda field: object() if has_field else None),
        db=types.SimpleNamespace(get_value=lambda doctype, filters, field=None: (
            items[filters["sh_shopify_variant_id"]][0]
            if isinstance(filters, dict) else state.get(filters))),
        get_doc=lambda doctype, name: _Doc(name),
    )

    ns = {
        "frappe": frappe,
        "owned_by": lambda doctype, connection, filters: dict(filters),
        "resolve_product_shopify_location": lambda variants, settings, pid, quiet=False: product_location,
        "_variant_location_levels": lambda variant, settings: variant["levels"],
        "_resolve_item_shopify_location": lambda levels, settings, code, quiet=False: resolved.get(code),
        "_sync_item_supplier_from_location": lambda code, loc: supplier_synced.append((code, loc)),
    }
    exec(code, ns)
    return ns["_refresh_item_locations"], saved, supplier_synced


def _node(*variant_ids):
    return {"variants": {"nodes": [{"legacyResourceId": v, "levels": []} for v in variant_ids]}}


def _entity():
    return types.SimpleNamespace(external_id="1")


class RefreshItemLocations(unittest.TestCase):
    def test_moves_item_to_the_location_holding_its_stock(self):
        fn, saved, synced = _load({"11": ("A", "old")}, {"A": "new"}, None)
        self.assertEqual(fn(_entity(), _node("11"), None), 1)
        self.assertEqual(saved, [("A", "new")])
        self.assertEqual(synced, [("A", "new")])

    def test_item_already_on_the_right_location_is_left_alone(self):
        fn, saved, synced = _load({"11": ("A", "new")}, {"A": "new"}, None)
        self.assertEqual(fn(_entity(), _node("11"), None), 0)
        self.assertEqual(saved, [])
        self.assertEqual(synced, [])

    def test_unresolved_item_keeps_its_current_location(self):
        fn, saved, _ = _load({"11": ("A", "old")}, {"A": None}, None)
        self.assertEqual(fn(_entity(), _node("11"), None), 0)
        self.assertEqual(saved, [])

    def test_sold_out_variant_follows_the_product_location(self):
        fn, saved, _ = _load({"11": ("A", "old")}, {"A": None}, "new")
        self.assertEqual(fn(_entity(), _node("11"), None), 1)
        self.assertEqual(saved, [("A", "new")])

    def test_variant_with_no_local_item_is_skipped(self):
        fn, saved, _ = _load({"11": (None, None)}, {}, "new")
        self.assertEqual(fn(_entity(), _node("11"), None), 0)
        self.assertEqual(saved, [])

    def test_site_without_the_location_field_is_a_no_op(self):
        fn, saved, _ = _load({"11": ("A", "old")}, {"A": "new"}, None, has_field=False)
        self.assertEqual(fn(_entity(), _node("11"), None), 0)
        self.assertEqual(saved, [])


if __name__ == "__main__":
    unittest.main()
