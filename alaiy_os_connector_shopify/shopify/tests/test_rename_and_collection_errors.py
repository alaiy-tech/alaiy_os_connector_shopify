"""
Two errors that were filling the Error Log.

rename_item_code passed `ignore_permissions` to frappe.rename_doc, which this
Frappe's rename_doc does not accept, so every SKU change failed with a
TypeError and rolled back. The fake rename_doc below has the real signature, so
passing the argument again fails here the same way.

Removing a product from a collection that was deleted on Shopify returns "does
not exist". The product is already out of a collection that is gone, so that is
not an error to log.

Modules are loaded with their neighbours stubbed, so this runs without a bench.
"""

import importlib.util
import pathlib
import sys
import types
import unittest

PRODUCT = pathlib.Path(__file__).resolve().parents[1] / "product"


def _load(filename, stubs):
    saved = {k: sys.modules.get(k) for k in stubs}
    sys.modules.update(stubs)
    try:
        spec = importlib.util.spec_from_file_location(f"{filename}_under_test", PRODUCT / filename)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        for k, v in saved.items():
            sys.modules.pop(k, None) if v is None else sys.modules.__setitem__(k, v)
    return mod


class RenameTests(unittest.TestCase):
    def test_renames_without_an_argument_this_frappe_does_not_have(self):
        renamed = []

        def rename_doc(doctype, old, new, force=False, merge=False, *, ignore_if_exists=False,
                       show_alert=True, rebuild_search=True):
            renamed.append((doctype, old, new))

        frappe = types.ModuleType("frappe")
        frappe._ = lambda s: s
        frappe.throw = lambda msg: (_ for _ in ()).throw(RuntimeError(msg))
        frappe.rename_doc = rename_doc
        frappe.db = types.SimpleNamespace(
            exists=lambda doctype, name=None: doctype == "Item" and name == "OLD",
            sql=lambda *a, **k: None, commit=lambda: None, rollback=lambda: None,
        )
        frappe.get_all = lambda *a, **k: []
        mod = _load("rename.py", {"frappe": frappe})
        self.assertEqual(mod.rename_item_code("OLD", "NEW"), "NEW")
        self.assertEqual(renamed, [("Item", "OLD", "NEW")])


class CollectionRemoveTests(unittest.TestCase):
    def call(self, verb, errors):
        logged = []
        frappe = types.ModuleType("frappe")
        frappe.log_error = lambda **kw: logged.append(kw)
        frappe.get_traceback = lambda: ""
        frappe.db = types.SimpleNamespace()
        # collections.py imports a lot; only _collection_membership_call is used.
        stub_names = [
            "alaiy_os_connector_shopify", "alaiy_os_connector_shopify.connections",
            "alaiy_os_connector_shopify.shopify", "alaiy_os_connector_shopify.shopify.product",
        ]
        stubs = {"frappe": frappe}
        for name in stub_names:
            stubs[name] = types.ModuleType(name)
        src = (PRODUCT / "collections.py").read_text(encoding="utf-8")
        start = src.index("def _collection_membership_call(")
        end = src.index("# ── Collection CRUD push")
        namespace = {"frappe": frappe}
        exec(compile(src[start:end], "collections_membership", "exec"), namespace)

        class Client:
            def execute(self, mutation, variables):
                key = "collectionAddProducts" if verb == "add" else "collectionRemoveProducts"
                return {key: {"userErrors": errors}}

        namespace["_collection_membership_call"](Client(), "m", "gid://c/1", "gid://p/1", verb, "IT-1")
        return logged

    def test_removing_from_a_deleted_collection_is_not_an_error(self):
        self.assertEqual(self.call("remove", [{"field": ["id"], "message": "Collection does not exist"}]), [])

    def test_other_remove_errors_are_still_logged(self):
        self.assertEqual(len(self.call("remove", [{"message": "Something else went wrong"}])), 1)

    def test_adding_to_a_deleted_collection_is_still_logged(self):
        self.assertEqual(len(self.call("add", [{"message": "Collection does not exist"}])), 1)


if __name__ == "__main__":
    unittest.main()
