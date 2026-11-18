"""An inventory push where every item failed must not close as "success".

Runs without a bench: frappe and the sibling modules are stood in for.
"""
import importlib
import sys
import types
import unittest
from unittest import mock

TARGET = "alaiy_os_connector_shopify.shopify.inventory_sync"
STUBS = [
    "frappe", "frappe.utils", "erpnext", "erpnext.stock", "erpnext.stock.doctype",
    "erpnext.stock.doctype.stock_reconciliation",
    "erpnext.stock.doctype.stock_reconciliation.stock_reconciliation",
    "alaiy_os_connector_shopify.api", "alaiy_os_connector_shopify.connections",
    "alaiy_os_connector_shopify.shopify.scoping", "alaiy_os_connector_shopify.shopify.sync_guard",
]


def load(core_runs):
    """Import inventory_sync with stand-ins; core_runs is the health.runs module or None."""
    patched = {name: mock.MagicMock() for name in STUBS}
    patched["alaiy_os"] = types.ModuleType("alaiy_os")
    patched["alaiy_os.health"] = types.ModuleType("alaiy_os.health")
    patched["alaiy_os.health.runs"] = core_runs  # None makes the import fail
    ctx = mock.patch.dict(sys.modules, patched)
    ctx.start()
    sys.modules.pop(TARGET, None)
    mod = importlib.import_module(TARGET)
    return mod, ctx


def core():
    m = types.ModuleType("alaiy_os.health.runs")

    def run_status(processed, failed, skipped=0, error=None):
        if processed > 0 and failed >= processed:
            return "failed"
        if processed == 0 and (error or skipped > 0):
            return "failed"
        return "success"
    m.run_status = run_status
    return m


class FinalStatus(unittest.TestCase):
    def setUp(self):
        self.mod, ctx = load(core())
        self.addCleanup(ctx.stop)
        self.addCleanup(sys.modules.pop, TARGET, None)

    def test_every_item_failed(self):
        self.assertEqual(self.mod._final_status(3, 3), "failed")

    def test_some_failed(self):
        self.assertEqual(self.mod._final_status(3, 1), "success")

    def test_nothing_processed(self):
        self.assertEqual(self.mod._final_status(0, 0), "success")


class Fallback(unittest.TestCase):
    def test_old_behaviour_without_core(self):
        mod, ctx = load(None)
        self.addCleanup(ctx.stop)
        self.addCleanup(sys.modules.pop, TARGET, None)
        self.assertEqual(mod._final_status(3, 3), "success")


if __name__ == "__main__":
    unittest.main()
