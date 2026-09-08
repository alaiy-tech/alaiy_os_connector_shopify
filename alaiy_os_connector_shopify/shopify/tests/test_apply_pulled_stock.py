"""
apply_pulled_stock's grouping, which decides what one Stock Reconciliation
document contains.

ERPNext rejects the WHOLE document if any item appears twice for the same
warehouse, so nine duplicate rows once took down a batch of about a hundred
real corrections on a live site. Corrections are built one per Shopify
LOCATION and several locations can resolve to a single warehouse -- most
easily because a location with no map row falls back to the default
warehouse -- so duplicates are a normal input, not bad data.

These pin the grouping only. The insert/submit path needs a real bench.
"""

import sys
import types
import unittest


def _load(disabled_items=()):
    """apply_pulled_stock with frappe stubbed, plus a capture of what it built."""
    built = []

    frappe = types.ModuleType("frappe")

    class _Doc:
        def __init__(self):
            self.items = []
            self.flags = types.SimpleNamespace(ignore_permissions=False)
            self.name = f"SR-{len(built) + 1:03d}"

        def append(self, table, row):
            self.items.append(row)

        def insert(self):
            built.append(self)

        def submit(self):
            pass

    def get_value(doctype, filters=None, fieldname=None, *a, **k):
        if doctype == "Item" and fieldname == "disabled":
            return 1 if filters in disabled_items else 0
        if doctype == "Warehouse":
            return "Test Co"
        return None

    frappe.new_doc = lambda doctype: _Doc()
    frappe.db = types.SimpleNamespace(
        get_value=get_value, commit=lambda: None, rollback=lambda: None)
    frappe.log_error = lambda *a, **k: None
    frappe.whitelist = lambda *a, **k: (lambda fn: fn)
    frappe.get_cached_doc = lambda *a, **k: None
    frappe.get_all = lambda *a, **k: []
    frappe.get_doc = lambda *a, **k: None
    frappe._ = lambda s: s
    frappe.throw = lambda *a, **k: None
    frappe.get_traceback = lambda *a, **k: ""
    frappe.enqueue = lambda *a, **k: None
    frappe.logger = lambda *a, **k: types.SimpleNamespace(
        debug=lambda *a, **k: None, info=lambda *a, **k: None)
    frappe.ValidationError = type("ValidationError", (Exception,), {})
    sys.modules["frappe"] = frappe

    utils = types.ModuleType("frappe.utils")
    utils.flt = lambda v, *a, **k: float(v or 0)
    utils.now_datetime = lambda *a, **k: None
    utils.add_to_date = lambda *a, **k: None
    utils.get_datetime = lambda v=None, *a, **k: v
    sys.modules["frappe.utils"] = utils
    frappe.utils = utils

    # inventory_sync imports this at module level for the empty-batch case.
    for name in ("erpnext", "erpnext.stock", "erpnext.stock.doctype",
                 "erpnext.stock.doctype.stock_reconciliation",
                 "erpnext.stock.doctype.stock_reconciliation.stock_reconciliation"):
        sys.modules.setdefault(name, types.ModuleType(name))
    sys.modules[
        "erpnext.stock.doctype.stock_reconciliation.stock_reconciliation"
    ].EmptyStockReconciliationItemsError = type(
        "EmptyStockReconciliationItemsError", (Exception,), {})

    for mod in list(sys.modules):
        if mod.startswith("alaiy_os_connector_shopify"):
            del sys.modules[mod]
    sys.path.insert(0, ".")
    from alaiy_os_connector_shopify.shopify import inventory_sync

    return inventory_sync.apply_pulled_stock, built


def _c(item, warehouse, qty):
    return {"item_code": item, "warehouse": warehouse, "qty": qty}


class TestDuplicateRows(unittest.TestCase):
    def test_one_item_twice_in_a_warehouse_becomes_a_single_summed_row(self):
        # The bug: two rows for the same item+warehouse made ERPNext reject
        # the entire document. Summed, not deduplicated -- a warehouse
        # standing behind two locations physically holds both quantities.
        apply, built = _load()
        apply([_c("SHIRT", "Main", 3), _c("SHIRT", "Main", 5)])
        self.assertEqual(len(built), 1)
        self.assertEqual(len(built[0].items), 1)
        self.assertEqual(built[0].items[0]["qty"], 8)

    def test_three_locations_collapsing_onto_one_warehouse(self):
        apply, built = _load()
        apply([_c("SHIRT", "Main", 1), _c("SHIRT", "Main", 2), _c("SHIRT", "Main", 4)])
        self.assertEqual(len(built[0].items), 1)
        self.assertEqual(built[0].items[0]["qty"], 7)

    def test_same_item_in_different_warehouses_stays_separate(self):
        # Not a duplicate: two warehouses genuinely hold their own stock,
        # and each gets its own document.
        apply, built = _load()
        apply([_c("SHIRT", "Main", 3), _c("SHIRT", "Supplier A", 5)])
        self.assertEqual(len(built), 2)
        for doc in built:
            self.assertEqual(len(doc.items), 1)

    def test_different_items_in_one_warehouse_stay_separate(self):
        apply, built = _load()
        apply([_c("SHIRT", "Main", 3), _c("SHOE", "Main", 5)])
        self.assertEqual(len(built), 1)
        self.assertEqual(
            sorted(r["item_code"] for r in built[0].items), ["SHIRT", "SHOE"])

    def test_a_zero_from_one_location_still_sums(self):
        # Zero is a real quantity, not a missing one.
        apply, built = _load()
        apply([_c("SHIRT", "Main", 0), _c("SHIRT", "Main", 6)])
        self.assertEqual(built[0].items[0]["qty"], 6)


class TestExistingSkipsStillApply(unittest.TestCase):
    def test_a_disabled_item_is_skipped_not_summed(self):
        apply, built = _load(disabled_items=("SHIRT",))
        result = apply([_c("SHIRT", "Main", 3), _c("SHOE", "Main", 5)])
        self.assertEqual([r["item_code"] for r in built[0].items], ["SHOE"])
        self.assertIn(("SHIRT", "item disabled"), result["skipped"])

    def test_a_negative_qty_is_skipped_before_it_can_be_summed(self):
        # Skipping first matters: summing -2 into a good 5 would write 3,
        # a plausible-looking number that is simply wrong.
        apply, built = _load()
        result = apply([_c("SHIRT", "Main", 5), _c("SHIRT", "Main", -2)])
        self.assertEqual(built[0].items[0]["qty"], 5)
        self.assertEqual(len(result["skipped"]), 1)

    def test_no_corrections_builds_nothing(self):
        apply, built = _load()
        result = apply([])
        self.assertEqual(built, [])
        self.assertEqual(result["reconciliations"], [])


if __name__ == "__main__":
    unittest.main()
