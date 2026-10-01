"""
push_item_stock: one item, one warehouse, pushed straight to the live variant.

The cases that matter are the ones where a quiet success would be wrong: a
variant with no level at the location (it must be activated, not just set), a
warehouse with no mapped location, an item with no stock record (never push an
assumed zero), and a refusal from Shopify (must come back as a reason).

Shopify and the database are faked, so this runs without a bench.
"""

import importlib.util
import pathlib
import sys
import types
import unittest

MODULE = pathlib.Path(__file__).resolve().parents[1] / "inventory_item_push.py"
VARIANT = "gid://shopify/ProductVariant/55"
LOCATION = "gid://shopify/Location/9"


class FakeClient:
    """Answers the state query from `state` and records every mutation."""

    def __init__(self, level, tracked=True, set_errors=None, activate_errors=None, track_errors=None, raises=None):
        self.level = level  # None = no level at the location, else the available quantity
        self.tracked = tracked
        self.set_errors = set_errors or []
        self.activate_errors = activate_errors or []
        self.track_errors = track_errors or []
        self.raises = raises
        self.mutations = []

    def execute(self, query, variables=None):
        if self.raises:
            raise self.raises
        if "ItemStockState" in query:
            level = None if self.level is None else {"quantities": [{"quantity": self.level}]}
            return {"productVariant": {"inventoryItem": {"id": "gid://shopify/InventoryItem/7", "tracked": self.tracked, "inventoryLevel": level}}}
        if "TrackInventory" in query:
            self.mutations.append(("track", variables))
            if not self.track_errors:
                self.tracked = True
            return {"inventoryItemUpdate": {"userErrors": self.track_errors}}
        if "ActivateInventory" in query:
            self.mutations.append(("activate", variables))
            if not self.activate_errors:
                self.level = variables["available"]
            return {"inventoryActivate": {"userErrors": self.activate_errors}}
        self.mutations.append(("set", variables))
        if not self.set_errors:
            self.level = variables["input"]["quantities"][0]["quantity"]
        return {"inventorySetQuantities": {"userErrors": self.set_errors}}


def _load(bin_qty=3, mapped=True, listing=True, variant_id="55", item=True):
    """inventory_item_push with frappe, the connection and the listing stubbed."""
    logged = []
    frappe = types.ModuleType("frappe")

    def get_value(doctype, filters=None, fieldname=None, *a, **k):
        if doctype == "Item":
            return types.SimpleNamespace(name="IT-1", variant_of=None) if item else None
        if doctype == "Bin":
            return bin_qty
        if doctype == "Shopify Location":
            return LOCATION
        return None

    frappe.db = types.SimpleNamespace(get_value=get_value)
    frappe.log_error = lambda **kw: logged.append(kw)
    utils = types.ModuleType("frappe.utils")
    utils.flt = lambda v, *a: float(v or 0)
    frappe.utils = utils

    row = types.SimpleNamespace(warehouse="WH - TS", shopify_location="loc-1")
    settings = types.SimpleNamespace(get=lambda key: [row] if mapped and key == "sh_location_map" else [])
    connections = types.ModuleType("alaiy_os_connector_shopify.connections")
    connections.resolve = lambda c=None: settings
    connections.require_enabled = lambda: settings

    gql = types.ModuleType("alaiy_os_connector_shopify.shopify.graphql_client")
    gql.ShopifyGraphQLClient = lambda s: None
    gql.new_idempotency_key = lambda: "key"

    inv = types.ModuleType("alaiy_os_connector_shopify.shopify.inventory_sync")
    inv._INVENTORY_SET_MUTATION = "mutation SetInventory { inventorySetQuantities }"

    product = types.ModuleType("alaiy_os_connector_shopify.shopify.product")
    resolver = types.ModuleType("alaiy_os_connector_shopify.shopify.product.listing")
    resolver.get_listing = lambda name: object() if listing else None
    resolver.variant_shopify_id = lambda l, code: variant_id
    product.listing = resolver

    root = types.ModuleType("alaiy_os_connector_shopify")
    root.connections = connections
    shopify = types.ModuleType("alaiy_os_connector_shopify.shopify")
    stubs = {
        "frappe": frappe, "frappe.utils": utils,
        "alaiy_os_connector_shopify": root,
        "alaiy_os_connector_shopify.connections": connections,
        "alaiy_os_connector_shopify.shopify": shopify,
        "alaiy_os_connector_shopify.shopify.graphql_client": gql,
        "alaiy_os_connector_shopify.shopify.inventory_sync": inv,
        "alaiy_os_connector_shopify.shopify.product": product,
        "alaiy_os_connector_shopify.shopify.product.listing": resolver,
    }
    saved = {k: sys.modules.get(k) for k in stubs}
    sys.modules.update(stubs)
    try:
        spec = importlib.util.spec_from_file_location("inventory_item_push_under_test", MODULE)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return mod, logged


class PushItemStockTests(unittest.TestCase):
    def push(self, client, **load_kw):
        mod, logged = _load(**load_kw)
        self.logged = logged
        return mod.push_item_stock("IT-1", "WH - TS", client=client)

    def test_sets_when_level_differs(self):
        client = FakeClient(level=1)
        r = self.push(client, bin_qty=3)
        self.assertTrue(r["ok"])
        self.assertEqual((r["action"], r["before"], r["after"], r["verified"]), ("set", 1, 3, True))
        kind, variables = client.mutations[0]
        self.assertEqual(kind, "set")
        q = variables["input"]["quantities"][0]
        self.assertEqual((q["quantity"], q["changeFromQuantity"], q["locationId"]), (3, 1, LOCATION))

    def test_activates_when_variant_has_no_level_there(self):
        client = FakeClient(level=None)
        r = self.push(client, bin_qty=1)
        self.assertTrue(r["ok"])
        self.assertEqual(r["action"], "activated")
        self.assertEqual([m[0] for m in client.mutations], ["activate"])
        self.assertEqual(client.mutations[0][1]["available"], 1)

    def test_unchanged_sends_nothing(self):
        client = FakeClient(level=3)
        r = self.push(client, bin_qty=3)
        self.assertTrue(r["ok"])
        self.assertEqual(r["action"], "unchanged")
        self.assertEqual(client.mutations, [])

    def test_zero_is_pushed_when_the_bin_says_zero(self):
        client = FakeClient(level=4)
        r = self.push(client, bin_qty=0)
        self.assertTrue(r["ok"])
        self.assertEqual(client.mutations[0][1]["input"]["quantities"][0]["quantity"], 0)

    def test_no_bin_is_not_an_assumed_zero(self):
        client = FakeClient(level=4)
        r = self.push(client, bin_qty=None)
        self.assertFalse(r["ok"])
        self.assertIn("assumed zero", r["reason"])
        self.assertEqual(client.mutations, [])

    def test_unmapped_warehouse_fails_before_shopify(self):
        client = FakeClient(level=1)
        r = self.push(client, mapped=False)
        self.assertFalse(r["ok"])
        self.assertIn("not mapped", r["reason"])
        self.assertEqual(client.mutations, [])

    def test_unlinked_item_fails(self):
        self.assertIn("variant id", self.push(FakeClient(level=1), variant_id=None)["reason"])
        self.assertIn("Listing", self.push(FakeClient(level=1), listing=False)["reason"])
        self.assertIn("not found", self.push(FakeClient(level=1), item=False)["reason"])

    def test_fractional_stock_is_refused(self):
        client = FakeClient(level=1)
        r = self.push(client, bin_qty=2.5)
        self.assertFalse(r["ok"])
        self.assertIn("whole", r["reason"])
        self.assertEqual(client.mutations, [])

    def test_shopify_refusal_comes_back_as_a_reason(self):
        client = FakeClient(level=1, set_errors=[{"message": "The quantity changed."}])
        r = self.push(client, bin_qty=3)
        self.assertFalse(r["ok"])
        self.assertIn("The quantity changed.", r["reason"])

    def test_untracked_is_reported_and_left_alone(self):
        client = FakeClient(level=1, tracked=False)
        r = self.push(client, bin_qty=3)
        self.assertTrue(r["ok"])
        self.assertFalse(r["tracked"])
        self.assertNotIn("track", [m[0] for m in client.mutations])

    def test_tracking_switched_on_only_when_asked(self):
        client = FakeClient(level=1, tracked=False)
        mod, _ = _load(bin_qty=3)
        r = mod.push_item_stock("IT-1", "WH - TS", enable_tracking=True, client=client)
        self.assertTrue(r["ok"])
        self.assertTrue(r["tracked"])
        self.assertEqual([m[0] for m in client.mutations], ["track", "set"])

    def test_tracking_refusal_stops_before_the_quantity(self):
        client = FakeClient(level=1, tracked=False, track_errors=[{"message": "No."}])
        mod, _ = _load(bin_qty=3)
        r = mod.push_item_stock("IT-1", "WH - TS", enable_tracking=True, client=client)
        self.assertFalse(r["ok"])
        self.assertEqual([m[0] for m in client.mutations], ["track"])

    def test_exception_is_a_failed_result_and_is_logged(self):
        client = FakeClient(level=1, raises=RuntimeError("boom"))
        r = self.push(client, bin_qty=3)
        self.assertFalse(r["ok"])
        self.assertIn("RuntimeError", r["reason"])
        self.assertEqual(len(self.logged), 1)


if __name__ == "__main__":
    unittest.main()
