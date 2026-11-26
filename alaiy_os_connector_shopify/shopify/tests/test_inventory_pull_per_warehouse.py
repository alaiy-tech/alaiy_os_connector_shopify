"""The scheduled stock pull compares a warehouse's stock with the TOTAL Shopify
holds for it, not with one location at a time.

A warehouse can sit behind several Shopify locations (here two, holding 96 and
0). Comparing each location with the warehouse stock and dropping the matching
ones before the rest were summed made that warehouse read as changed on every
run: the 0 beat a stock of 96, then the 96 beat a stock of 0, so the stock
flipped each hour.

These stub frappe and the Shopify client and drive the real
pull_stock_for_items in dry-run mode.
"""

import sys
import types
import unittest


def _load(bins, levels, mapped=(), complete=None):
    """pull_stock_for_items with frappe, the Shopify client and the location
    lookup stubbed. `bins` is {warehouse: current qty}; `levels` is
    [(location_id, warehouse, qty), ...] for the one item under test.
    `mapped` lists the warehouses behind an active Shopify location; `complete`
    is Shopify's hasNextPage answer (None leaves pageInfo out)."""
    frappe = types.ModuleType("frappe")

    def get_all(doctype, *a, **k):
        if doctype == "Item":
            return [types.SimpleNamespace(name="ITEM", sh_shopify_inventory_item_id="1")]
        if doctype == "Shopify Location":
            return ["LOC"] if mapped else []
        if doctype == "Shopify Location Map":
            return list(mapped)
        if doctype == "Bin":
            wanted = a[0]["warehouse"][1] if a else k["filters"]["warehouse"][1]
            return [types.SimpleNamespace(warehouse=w, actual_qty=q)
                    for w, q in bins.items() if w in wanted and q > 0]
        return []

    def get_value(doctype, filters=None, fieldname=None, *a, **k):
        if doctype == "Bin":
            return bins.get(filters["warehouse"])
        return None

    frappe.get_all = get_all
    frappe.db = types.SimpleNamespace(
        get_value=get_value, set_value=lambda *a, **k: None,
        commit=lambda: None, rollback=lambda: None)
    frappe.log_error = lambda *a, **k: None
    frappe.whitelist = lambda *a, **k: (lambda fn: fn)
    frappe.get_cached_doc = lambda *a, **k: None
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

    client_module = types.ModuleType("alaiy_os_connector_shopify.shopify.graphql_client")

    class _Client:
        def __init__(self, connection):
            pass

        def execute(self, query, variables):
            nodes = {"nodes": [
                {"location": {"legacyResourceId": location},
                 "quantities": [{"quantity": qty}]}
                for location, _warehouse, qty in levels
            ]}
            if complete is not None:
                nodes["pageInfo"] = {"hasNextPage": not complete}
            return {"nodes": [{"legacyResourceId": "1", "inventoryLevels": nodes}]}

    client_module.ShopifyGraphQLClient = _Client
    sys.modules["alaiy_os_connector_shopify.shopify.graphql_client"] = client_module

    sys.path.insert(0, ".")
    from alaiy_os_connector_shopify.shopify import inventory_sync

    warehouse_by_location = {location: warehouse for location, warehouse, _qty in levels}
    inventory_sync._resolve_warehouse_for_location = (
        lambda location_id, connection=None: warehouse_by_location.get(location_id))
    inventory_sync.connections.resolve_optional = lambda connection=None: types.SimpleNamespace(name="STORE")
    inventory_sync.owned_by = lambda doctype, connection, filters=None: filters or {}
    return inventory_sync


_LEVELS = [("L1", "HQ", 96), ("L2", "RH", 60), ("L3", "HQ", 0)]


class TestSumByWarehouse(unittest.TestCase):
    def test_locations_behind_one_warehouse_are_added_up(self):
        sync = _load({}, _LEVELS)
        self.assertEqual(
            sync._sum_by_warehouse([("HQ", 96), ("RH", 60), ("HQ", 0)]),
            {"HQ": 96.0, "RH": 60.0})

    def test_a_missing_quantity_counts_as_zero(self):
        sync = _load({}, _LEVELS)
        self.assertEqual(sync._sum_by_warehouse([("HQ", None), ("HQ", 5)]), {"HQ": 5.0})


class TestPullDoesNotFlip(unittest.TestCase):
    def test_stock_matching_the_total_is_left_alone(self):
        # Stock 96 against locations holding 96 and 0: nothing to correct.
        sync = _load({"HQ": 96.0, "RH": 60.0}, _LEVELS)
        result = sync.pull_stock_for_items(["ITEM"], dry_run=True)
        self.assertEqual(result["corrections"], [])
        self.assertEqual(result["unchanged"], 2)

    def test_the_other_half_of_the_old_flip_is_left_alone_too(self):
        # Locations holding 0 and 96 in the other order: still nothing.
        levels = [("L3", "HQ", 0), ("L2", "RH", 60), ("L1", "HQ", 96)]
        sync = _load({"HQ": 96.0, "RH": 60.0}, levels)
        result = sync.pull_stock_for_items(["ITEM"], dry_run=True)
        self.assertEqual(result["corrections"], [])

    def test_a_real_difference_is_corrected_to_the_total(self):
        sync = _load({"HQ": 50.0, "RH": 60.0}, _LEVELS)
        result = sync.pull_stock_for_items(["ITEM"], dry_run=True)
        self.assertEqual(
            result["corrections"],
            [{"item_code": "ITEM", "warehouse": "HQ", "qty": 96.0, "old_qty": 50.0}])


class TestUnreportedWarehouse(unittest.TestCase):
    """A warehouse Shopify holds nothing for is zeroed, never left with old stock."""

    _SUPPLIER = [("L2", "SUP", 11)]

    def _pull(self, bins, mapped, complete):
        sync = _load(bins, self._SUPPLIER, mapped=mapped, complete=complete)
        return sync.pull_stock_for_items(["ITEM"], dry_run=True)["corrections"]

    def test_stock_in_a_mapped_warehouse_shopify_does_not_report_is_zeroed(self):
        corrections = self._pull({"SUP": 11.0, "HQ": 6.0}, ["SUP", "HQ"], complete=True)
        self.assertEqual(
            corrections, [{"item_code": "ITEM", "warehouse": "HQ", "qty": 0, "old_qty": 6.0}])

    def test_a_truncated_level_list_is_never_read_as_empty(self):
        self.assertEqual(self._pull({"SUP": 11.0, "HQ": 6.0}, ["SUP", "HQ"], complete=False), [])

    def test_a_response_that_does_not_say_is_never_read_as_empty(self):
        self.assertEqual(self._pull({"SUP": 11.0, "HQ": 6.0}, ["SUP", "HQ"], complete=None), [])

    def test_a_warehouse_with_no_shopify_location_is_left_alone(self):
        self.assertEqual(self._pull({"SUP": 11.0, "HQ": 6.0}, ["SUP"], complete=True), [])

    def test_a_warehouse_already_at_zero_makes_no_correction(self):
        self.assertEqual(self._pull({"SUP": 11.0, "HQ": 0.0}, ["SUP", "HQ"], complete=True), [])


if __name__ == "__main__":
    unittest.main()
