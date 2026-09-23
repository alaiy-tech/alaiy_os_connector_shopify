"""
The ERPNext-side custom fields land on benches that use Shopify, and nowhere else.

`setup_custom_fields` runs from `after_migrate` on every bench that has this app
installed, and it writes ~19 columns onto `tabItem` -- four of them `search_index`,
which `frappe.db.updatedb` turns into four indexes. On a bench with a Shopify store
that is the point. On a bench that has never had a `Shopify Connection` it is empty
columns and, if the Item table is large, a very long ALTER in the middle of a
migrate.

A frappe stub stands in for the DB, so these pin the decision to write at all --
and that when it does write, it does not ask Frappe to re-validate the parent
doctype's unique fields, which costs a full table scan per field written.
"""

import sys
import types
import unittest


def _load(*, connections=0, marker_field=False, doctypes=("Shopify Connection",)):
    """Reload install.py against a described bench. Returns (module, log)."""
    log = {"created": [], "deleted": []}

    frappe = types.ModuleType("frappe")

    def exists(doctype, name=None, **kwargs):
        if doctype == "DocType":
            return name in doctypes
        if doctype == "Custom Field":
            return marker_field and name == "Item-sh_shopify_product_id"
        return False

    frappe.db = types.SimpleNamespace(
        exists=exists,
        a_row_exists=lambda doctype: connections > 0,
        commit=lambda: None,
        sql=lambda *a, **k: [],
    )
    frappe.delete_doc = lambda *a, **k: log["deleted"].append(a)
    frappe.get_doc = lambda *a, **k: types.SimpleNamespace()
    frappe.new_doc = lambda *a, **k: types.SimpleNamespace()
    frappe.clear_cache = lambda **k: None
    frappe._ = lambda s: s
    sys.modules["frappe"] = frappe

    custom_field = types.ModuleType("frappe.custom.doctype.custom_field.custom_field")
    custom_field.create_custom_fields = lambda fields, **kwargs: log["created"].append(
        (fields, kwargs))
    for name in ("frappe.custom", "frappe.custom.doctype",
                 "frappe.custom.doctype.custom_field"):
        sys.modules.setdefault(name, types.ModuleType(name))
    sys.modules["frappe.custom.doctype.custom_field.custom_field"] = custom_field

    for mod in list(sys.modules):
        if mod.startswith("alaiy_os_connector_shopify"):
            del sys.modules[mod]
    from alaiy_os_connector_shopify.setup import install as mod
    return mod, log


class TestItWritesOnlyWhereShopifyIsUsed(unittest.TestCase):
    def test_a_bench_with_no_connection_is_left_alone(self):
        # The case this exists for: this app installed beside a 14M-row catalogue
        # that has no Shopify store. Writing the columns costs an index build.
        mod, log = _load(connections=0, marker_field=False)
        mod.setup_custom_fields()
        self.assertEqual(log["created"], [])
        self.assertEqual(log["deleted"], [])

    def test_a_connection_is_enough_even_if_it_is_disabled(self):
        # `is_enabled` is set by hand and by script as well as through the form,
        # so the row existing -- not its flag -- is what says Shopify is in use.
        mod, log = _load(connections=1)
        mod.setup_custom_fields()
        self.assertTrue(log["created"])

    def test_a_provisioned_bench_keeps_being_maintained(self):
        # Its last connection may be gone; its columns are not, and a newly added
        # field still has to reach them.
        mod, log = _load(connections=0, marker_field=True)
        mod.setup_custom_fields()
        self.assertTrue(log["created"])

    def test_a_bench_without_the_doctype_yet_writes_nothing(self):
        # after_install can run before this app's own doctypes are in place.
        mod, log = _load(connections=1, doctypes=())
        mod.setup_custom_fields()
        self.assertEqual(log["created"], [])


class TestItDoesNotRevalidateTheParentDoctype(unittest.TestCase):
    def test_fields_are_written_with_ignore_validate(self):
        # Without it, Custom Field's on_update re-runs validate_fields_for_doctype
        # per field, which full-scans the parent once per UNIQUE column to look for
        # duplicates -- ~100s a scan on tabItem, asking whether a column that
        # carries a unique index has duplicates in it.
        mod, log = _load(connections=1)
        mod.setup_custom_fields()
        self.assertTrue(log["created"])
        for _fields, kwargs in log["created"]:
            self.assertIs(kwargs.get("ignore_validate"), True)

    def test_item_is_still_among_the_doctypes_written(self):
        # The fix is about WHEN, not about dropping the fields: inventory_sync and
        # shopify/scoping.py both filter Items on them.
        mod, log = _load(connections=1)
        mod.setup_custom_fields()
        fields, _kwargs = log["created"][0]
        self.assertIn("Item", fields)


if __name__ == "__main__":
    unittest.main()
