"""
The ownership backfill stamps the right rows and only those.

Two ways this patch can be wrong, and both are quiet. Stamping too much sweeps
hand-made Items and desk-typed Sales Orders into the connector's reads -- and
into the scope of its bulk deletes. Stamping on a bench with several stores
picks one seller's connection for another seller's rows.

These pin the SQL it builds and the decision to run at all. A frappe stub
stands in for the DB and records the statements instead of executing them.
"""

import sys
import types
import unittest


def _load(connection_names, columns=None, doctypes=None):
    """Reload the patch against a described bench. Returns (module, log)."""
    log = {"sql": [], "errors": []}

    frappe = types.ModuleType("frappe")

    def has_column(table, column):
        return True if columns is None else (table, column) in columns

    def exists(doctype, name=None):
        if doctype == "DocType" and doctypes is not None:
            return name in doctypes
        return True

    def sql(statement, *args):
        log["sql"].append((" ".join(statement.split()), args))
        return [[0]]

    frappe.db = types.SimpleNamespace(
        has_column=has_column, exists=exists, sql=sql, commit=lambda: None)
    frappe.log_error = lambda **kw: log["errors"].append(kw)
    frappe.ValidationError = type("ValidationError", (Exception,), {})
    frappe._ = lambda s: s
    frappe.throw = lambda msg, exc=None, **k: (_ for _ in ()).throw(
        (exc or Exception)(msg))
    sys.modules["frappe"] = frappe

    for mod in list(sys.modules):
        if mod.startswith("alaiy_os_connector_shopify"):
            del sys.modules[mod]
    from alaiy_os_connector_shopify.patches import backfill_connection_ownership as mod
    mod.connections = types.SimpleNamespace(names=lambda: list(connection_names))
    return mod, log


def _updates(log):
    return [s for s, _ in log["sql"] if s.startswith("UPDATE")]


class TestItOnlyRunsWhenUnambiguous(unittest.TestCase):
    def test_one_connection_backfills(self):
        mod, log = _load(["default"])
        mod.execute()
        self.assertTrue(_updates(log))

    def test_no_connection_writes_nothing(self):
        # A site that never configured Shopify. Creating attribution out of
        # nothing would make an unconfigured site look configured.
        mod, log = _load([])
        mod.execute()
        self.assertEqual(_updates(log), [])

    def test_several_connections_refuse_and_say_so(self):
        # The dangerous case: picking one would hand one seller's catalogue
        # to another. It must decline AND leave a trace, or the operator
        # never learns the rows are unattributed.
        mod, log = _load(["seller-a", "seller-b"])
        mod.execute()
        self.assertEqual(_updates(log), [])
        self.assertTrue(log["errors"])


class TestItStampsOnlyShopifyRows(unittest.TestCase):
    def test_core_doctypes_require_a_shopify_id(self):
        # An Item somebody typed in by hand has no sh_shopify_product_id and
        # is not the connector's to claim.
        mod, log = _load(["default"])
        mod.execute()
        item = [s for s in _updates(log) if "`tabItem`" in s]
        self.assertEqual(len(item), 1)
        self.assertIn("sh_shopify_product_id", item[0])
        self.assertIn("IS NOT NULL", item[0])

    def test_connector_owned_doctypes_take_every_row(self):
        # A Shopify Location exists only because of Shopify; there is no
        # "did this come from Shopify" column to test.
        mod, log = _load(["default"])
        mod.execute()
        loc = [s for s in _updates(log) if "`tabShopify Location`" in s]
        self.assertEqual(len(loc), 1)
        self.assertNotIn("IS NOT NULL", loc[0])

    def test_every_statement_skips_already_stamped_rows(self):
        # What makes a re-run finish the job instead of redoing it.
        mod, log = _load(["default"])
        mod.execute()
        for statement in _updates(log):
            self.assertIn("IS NULL", statement)

    def test_the_right_field_name_per_doctype(self):
        # Custom field on ERPNext's doctypes, real field on the connector's.
        mod, log = _load(["default"])
        mod.execute()
        for statement in _updates(log):
            if "`tabShopify " in statement:
                self.assertIn("SET `connection`", statement)
            else:
                self.assertIn("SET `sh_shopify_connection`", statement)

    def test_it_covers_every_doctype_it_claims_to(self):
        mod, log = _load(["default"])
        mod.execute()
        statements = _updates(log)
        expected = [d for d, _ in mod.CORE] + list(mod.OWNED)
        self.assertEqual(len(statements), len(expected))
        for doctype in expected:
            self.assertTrue(
                any(f"`tab{doctype}`" in s for s in statements), doctype)


class TestItSkipsWhatIsNotThereYet(unittest.TestCase):
    def test_a_missing_column_is_skipped_not_failed(self):
        # Before this release's schema sync the column does not exist.
        # Writing would error; skipping lets the migrate proceed.
        mod, log = _load(["default"], columns=set())
        mod.execute()
        self.assertEqual(_updates(log), [])

    def test_a_missing_doctype_is_skipped(self):
        mod, log = _load(["default"], doctypes={"Item"})
        mod.execute()
        self.assertTrue(all("`tabItem`" in s for s in _updates(log)))


if __name__ == "__main__":
    unittest.main()
