"""A product cannot be added to a collection deleted on Shopify, and retrying
never helps, so that answer is not logged as an error on every push. Removing
from a deleted collection was already quiet. Any other Shopify error is still
reported.

The function is pulled out of collections.py and run with stand-ins.
"""

import ast
import os
import types
import unittest

_SRC = os.path.join(os.path.dirname(__file__), "..", "product", "collections.py")


def _run(verb, errors):
    with open(_SRC, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "_collection_membership_call")
    code = compile(ast.Module(body=[fn], type_ignores=[]), _SRC, "exec")
    logged, info = [], []
    key = "collectionAddProducts" if verb == "add" else "collectionRemoveProducts"
    client = types.SimpleNamespace(execute=lambda mutation, variables: {key: {"userErrors": errors}})
    ns = {
        "frappe": types.SimpleNamespace(
            log_error=lambda title, message: logged.append(title),
            logger=lambda name: types.SimpleNamespace(info=lambda m: info.append(m)),
            get_traceback=lambda: "tb"),
    }
    exec(code, ns)
    ns["_collection_membership_call"](client, "m", "gid://c/1", "gid://p/1", verb, "ITEM")
    return logged, info


_GONE = [{"field": ["id"], "message": "Collection does not exist"}]


class CollectionMembership(unittest.TestCase):
    def test_add_to_deleted_collection_is_not_an_error(self):
        logged, info = _run("add", _GONE)
        self.assertEqual(logged, [])
        self.assertEqual(len(info), 1)

    def test_remove_from_deleted_collection_stays_quiet(self):
        logged, info = _run("remove", _GONE)
        self.assertEqual((logged, info), ([], []))

    def test_other_add_errors_are_still_reported(self):
        logged, _ = _run("add", [{"field": ["id"], "message": "Something else"}])
        self.assertEqual(len(logged), 1)

    def test_mixed_errors_are_still_reported(self):
        logged, _ = _run("add", _GONE + [{"field": ["x"], "message": "Other"}])
        self.assertEqual(len(logged), 1)


if __name__ == "__main__":
    unittest.main()
