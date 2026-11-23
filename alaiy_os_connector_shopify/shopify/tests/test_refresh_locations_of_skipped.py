"""_refresh_locations_of_imported: a product kept out of the import by its
status still has its Items' location refreshed, and never raises.

Pulled out of importer.py and run with stand-ins -- the decision is pinned,
not the database write.
"""

import ast
import os
import types
import unittest

_IMPORTER = os.path.join(os.path.dirname(__file__), "..", "product", "importer.py")


def _load(entity, item_exists=True, boom=False):
    with open(_IMPORTER, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "_refresh_locations_of_imported")
    code = compile(ast.Module(body=[fn], type_ignores=[]), _IMPORTER, "exec")
    refreshed, logged = [], []

    def refresh(ent, node, settings):
        if boom:
            raise RuntimeError("x")
        refreshed.append(ent)

    ns = {
        "frappe": types.SimpleNamespace(
            db=types.SimpleNamespace(exists=lambda doctype, name: item_exists),
            log_error=lambda title, message: logged.append(title),
            get_traceback=lambda: "tb"),
        "entities": types.SimpleNamespace(get_by_external_id=lambda kind, pid, conn: entity),
        "connections": types.SimpleNamespace(
            resolve=lambda c: "s", require_enabled=lambda: "s"),
        "_refresh_item_locations": refresh,
    }
    exec(code, ns)
    return ns["_refresh_locations_of_imported"], refreshed, logged


class RefreshLocationsOfImported(unittest.TestCase):
    def test_imported_product_is_refreshed(self):
        ent = types.SimpleNamespace(erpnext_name="T")
        fn, refreshed, _ = _load(ent)
        fn({"legacyResourceId": "1"})
        self.assertEqual(refreshed, [ent])

    def test_never_imported_product_is_left_alone(self):
        fn, refreshed, _ = _load(None)
        fn({"legacyResourceId": "1"})
        self.assertEqual(refreshed, [])

    def test_missing_local_item_is_left_alone(self):
        fn, refreshed, _ = _load(types.SimpleNamespace(erpnext_name="T"), item_exists=False)
        fn({"legacyResourceId": "1"})
        self.assertEqual(refreshed, [])

    def test_failure_is_logged_not_raised(self):
        fn, _, logged = _load(types.SimpleNamespace(erpnext_name="T"), boom=True)
        fn({"legacyResourceId": "1"})
        self.assertEqual(len(logged), 1)


if __name__ == "__main__":
    unittest.main()
