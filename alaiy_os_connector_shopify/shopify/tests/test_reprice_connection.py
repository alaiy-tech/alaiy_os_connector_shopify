"""
Repricing a store's live products (issue #203): the price resolver hook
contract, and the connection-scoped run built on top of it.

The hook half (TestPriceResolverHookContract) is pure logic over
`frappe.get_hooks`/`frappe.get_attr`/`frappe.local` and needs nothing more
than a fake `frappe` module -- same technique test_scoping.py and
test_connection_backfill.py already use to test real logic without a bench.

The run half needs `shopify.product.export`, which transitively imports a
good part of the product-push stack (canonical/variants/listing/pricing/
tags/media/graphql_client/auth). None of those touch a real database at
IMPORT time -- only when called -- so a sufficiently-stocked fake `frappe`
(plus a stub `requests`, which this sandbox has neither installed) lets the
module itself load, and the tests then monkeypatch the specific calls
(`update_variant_prices`, `listing_resolver`, `entities`, `retry_queue`,
`sync_guard`) each test cares about, the same way TestConnectionBackfill
stubs `frappe.db` and records what a patch tried to do instead of running
it for real.

None of this replaces `bench run-tests`, which is what this repo's CI
actually runs these suites under -- it is what's left when a bench isn't on
hand at all.
"""

import sys
import types
import unittest
from unittest import mock


# ── a frappe fake big enough to import shopify.product.export ────────────


class _FakeDoc(dict):
    """Stands in for a frappe Document: attribute access over a dict, plus
    the handful of methods export.py's new code calls on one."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def __setattr__(self, name, value):
        self[name] = value

    def get(self, key, default=None):
        return dict.get(self, key, default)

    def save(self, **kw):
        pass

    def insert(self, **kw):
        pass


def _install_fake_frappe():
    frappe = types.ModuleType("frappe")

    frappe.local = types.SimpleNamespace()

    def whitelist(*a, **kw):
        # Bare @frappe.whitelist and @frappe.whitelist(methods=[...]) both
        # just need to hand the function back unchanged.
        if a and callable(a[0]) and not kw:
            return a[0]
        return lambda fn: fn

    frappe.whitelist = whitelist
    frappe.validate_and_sanitize_search_inputs = lambda fn: fn

    frappe._ = lambda s: s
    frappe.ValidationError = type("ValidationError", (Exception,), {})
    frappe.PermissionError = type("PermissionError", (Exception,), {})

    def throw(msg, exc=None, **kw):
        raise (exc or Exception)(msg)

    frappe.throw = throw
    frappe.has_permission = lambda *a, **kw: True
    frappe.log_error = lambda **kw: None
    frappe.get_hooks = lambda name=None: []
    frappe.get_attr = lambda path: _resolve_dotted(path)
    frappe.enqueue = mock.Mock(name="frappe.enqueue")

    frappe.db = types.SimpleNamespace(
        get_value=mock.Mock(return_value=None),
        set_value=mock.Mock(),
        exists=mock.Mock(return_value=True),
        count=mock.Mock(return_value=0),
        sql=mock.Mock(return_value=[]),
        commit=lambda: None,
    )
    frappe.get_all = mock.Mock(return_value=[])
    frappe.get_doc = mock.Mock(side_effect=lambda doctype, name=None: _FakeDoc(
        doctype=doctype, name=name))
    frappe.new_doc = mock.Mock(side_effect=lambda doctype: _FakeDoc(doctype=doctype))
    frappe.get_cached_doc = frappe.get_doc

    utils = types.ModuleType("frappe.utils")
    utils.flt = lambda v=0, *a, **kw: float(v or 0)
    utils.now_datetime = lambda: "now"
    utils.add_to_date = lambda *a, **kw: "later"
    utils.get_datetime = lambda v=None: v
    frappe.utils = utils

    password = types.ModuleType("frappe.utils.password")
    password.set_encrypted_password = lambda *a, **kw: None
    utils.password = password

    exceptions = types.ModuleType("frappe.exceptions")
    exceptions.QueueOverloaded = type("QueueOverloaded", (Exception,), {})
    exceptions.TimestampMismatchError = type("TimestampMismatchError", (Exception,), {})
    frappe.exceptions = exceptions

    sys.modules["frappe"] = frappe
    sys.modules["frappe.utils"] = utils
    sys.modules["frappe.utils.password"] = password
    sys.modules["frappe.exceptions"] = exceptions
    sys.modules.setdefault("requests", types.ModuleType("requests"))
    return frappe


def _resolve_dotted(path):
    module_path, _, attr = path.rpartition(".")
    import importlib
    return getattr(importlib.import_module(module_path), attr)


def _load_export():
    """A fresh shopify.product.export, imported against the fake frappe."""
    _install_fake_frappe()
    for mod in list(sys.modules):
        if mod.startswith("alaiy_os_connector_shopify"):
            del sys.modules[mod]
    from alaiy_os_connector_shopify.shopify.product import export
    return export


# ── the hook contract ─────────────────────────────────────────────────────


class TestPriceResolverHookContract(unittest.TestCase):
    """shopify_price_resolver: exactly one provider, validated before use."""

    def _load(self, providers):
        frappe = _install_fake_frappe()
        frappe.get_hooks = lambda name=None: list(providers)
        for mod in list(sys.modules):
            if mod.startswith("alaiy_os_connector_shopify"):
                del sys.modules[mod]
        from alaiy_os_connector_shopify.shopify.product import pricing_resolver
        return pricing_resolver

    def test_zero_providers_throws(self):
        mod = self._load([])
        with self.assertRaises(Exception):
            mod.resolve("conn", ["ITEM-1"])

    def test_two_providers_throws(self):
        mod = self._load(["app_a.pricing.resolve", "app_b.pricing.resolve"])
        with self.assertRaises(Exception):
            mod.resolve("conn", ["ITEM-1"])

    def test_one_provider_is_called_with_connection_and_item_codes(self):
        calls = []

        def _provider(connection, item_codes):
            calls.append((connection, list(item_codes)))
            return {"ITEM-1": 19.99}

        sys.modules["a_fake_pricing_provider"] = types.SimpleNamespace(resolve=_provider)
        mod = self._load(["a_fake_pricing_provider.resolve"])

        result = mod.resolve("conn-a", ["ITEM-1", "ITEM-2"])

        self.assertEqual(calls, [("conn-a", ["ITEM-1", "ITEM-2"])])
        self.assertEqual(result, {"ITEM-1": 19.99})

    def test_a_provider_declining_everything_is_not_an_error(self):
        sys.modules["a_fake_pricing_provider"] = types.SimpleNamespace(
            resolve=lambda connection, item_codes: {})
        mod = self._load(["a_fake_pricing_provider.resolve"])
        self.assertEqual(mod.resolve("conn-a", ["ITEM-1"]), {})

    def test_validation_result_is_cached_per_request(self):
        """Same cache-on-frappe.local shape as matrix.load() -- a second
        call in the same request must not re-walk the hook registry."""
        frappe = _install_fake_frappe()
        seen = []

        def get_hooks(name=None):
            seen.append(1)
            return []

        frappe.get_hooks = get_hooks
        for mod in list(sys.modules):
            if mod.startswith("alaiy_os_connector_shopify"):
                del sys.modules[mod]
        from alaiy_os_connector_shopify.shopify.product import pricing_resolver

        with self.assertRaises(Exception):
            pricing_resolver.resolve("conn", ["X"])
        with self.assertRaises(Exception):
            pricing_resolver.resolve("conn", ["X"])
        self.assertEqual(len(seen), 1)


# ── the connection-scoped run ─────────────────────────────────────────────


def _listing(name, connection, product_id, rows):
    """A fake Shopify Product Listing carrying fake Shopify Listing Variant
    rows -- just enough attribute access for the code under test."""
    listing = _FakeDoc(
        name=name, connection=connection, item=name,
        sh_shopify_product_id=product_id,
    )
    listing.variants = [
        _FakeDoc(name=f"{name}-row-{code}", item_variant=code,
                 variant_price=price, sh_shopify_variant_id=f"v-{code}",
                 is_enabled=1)
        for code, price in rows
    ]
    return listing


class TestNeverPushedIsSkippedNotFailed(unittest.TestCase):
    def test_candidates_require_both_a_product_id_and_a_variant_id(self):
        export = _load_export()

        captured = {}

        def fake_get_all(doctype, filters=None, fields=None, pluck=None, **kw):
            captured[doctype] = filters
            if doctype == "Shopify Product Listing":
                return ["TEMPLATE-1"]
            if doctype == "Shopify Listing Variant":
                return [_FakeDoc(parent="TEMPLATE-1", item_variant="ITEM-1")]
            return []

        export.frappe.get_all = fake_get_all
        connection = _FakeDoc(name="store-a")

        result = export._reprice_candidates(connection)

        self.assertEqual(result, [("TEMPLATE-1", "ITEM-1")])
        listing_filters = captured["Shopify Product Listing"]
        self.assertEqual(listing_filters["is_enabled"], 1)
        self.assertEqual(listing_filters["sh_shopify_product_id"], ["is", "set"])
        variant_filters = captured["Shopify Listing Variant"]
        self.assertEqual(variant_filters["is_enabled"], 1)
        self.assertEqual(variant_filters["sh_shopify_variant_id"], ["is", "set"])

    def test_no_listings_short_circuits_without_a_second_query(self):
        export = _load_export()
        export.frappe.get_all = mock.Mock(return_value=[])
        result = export._reprice_candidates(_FakeDoc(name="store-a"))
        self.assertEqual(result, [])
        export.frappe.get_all.assert_called_once()


class TestConnectionScoping(unittest.TestCase):
    def test_candidates_are_filtered_to_the_calling_store(self):
        export = _load_export()
        seen_connection = {}

        def fake_get_all(doctype, filters=None, **kw):
            if doctype == "Shopify Product Listing":
                seen_connection["value"] = filters.get("connection")
            return []

        export.frappe.get_all = fake_get_all
        export._reprice_candidates(_FakeDoc(name="naya-pets"))
        self.assertEqual(seen_connection["value"], "naya-pets")


class TestSkipUnchangedMakesNoShopifyCall(unittest.TestCase):
    """The chunk loop inside run_reprice_connection: an item whose resolved
    price matches what's already stored must never reach _apply_price_updates
    (and so never reach update_variant_prices/Shopify)."""

    def _run(self, resolved, stored_price, connection_name="store-a"):
        export = _load_export()

        connection = _FakeDoc(name=connection_name)
        export.connections = types.SimpleNamespace(
            resolve=lambda c=None: connection, require_enabled=lambda: connection)

        export.sync_guard = types.SimpleNamespace(
            has_active_sync=lambda *a, **kw: False,
            load_or_create_log=lambda *a, **kw: _FakeDoc(name="SYNC-LOG-1"),
            is_cancel_requested=lambda *a, **kw: False,
        )

        listing = _listing("TEMPLATE-1", connection_name, "111", [("ITEM-1", stored_price)])
        export._reprice_candidates = lambda conn: [("TEMPLATE-1", "ITEM-1")]
        export.listing_resolver = types.SimpleNamespace(
            get_listing=lambda name: listing,
            variant_price=lambda listing, code, settings: stored_price,
        )
        export.pricing_resolver = types.SimpleNamespace(resolve=lambda conn, codes: resolved)

        apply_calls = []
        export._apply_price_updates = mock.Mock(
            side_effect=lambda changed, conn: apply_calls.append(dict(changed)) or
            {"updated": list(changed), "failed": {}}
        )

        export.run_reprice_connection(connection=connection_name)
        return apply_calls

    def test_an_unchanged_resolved_price_is_never_pushed(self):
        calls = self._run(resolved={"ITEM-1": 25.00}, stored_price=25.00)
        self.assertEqual(calls, [])

    def test_a_changed_resolved_price_is_pushed(self):
        calls = self._run(resolved={"ITEM-1": 30.00}, stored_price=25.00)
        self.assertEqual(calls, [{"ITEM-1": 30.00}])

    def test_an_item_the_resolver_declines_is_skipped_not_pushed(self):
        calls = self._run(resolved={}, stored_price=25.00)
        self.assertEqual(calls, [])


class TestFailedBatchGoesToRetryQueue(unittest.TestCase):
    def test_a_failed_item_is_enqueued_with_entity_type_price(self):
        export = _load_export()
        connection = _FakeDoc(name="store-a")
        export.connections = types.SimpleNamespace(
            resolve=lambda c=None: connection, require_enabled=lambda: connection)
        export.sync_guard = types.SimpleNamespace(
            has_active_sync=lambda *a, **kw: False,
            load_or_create_log=lambda *a, **kw: _FakeDoc(name="SYNC-LOG-1"),
            is_cancel_requested=lambda *a, **kw: False,
        )
        listing = _listing("TEMPLATE-1", "store-a", "111", [("ITEM-1", 25.00)])
        export._reprice_candidates = lambda conn: [("TEMPLATE-1", "ITEM-1")]
        export.listing_resolver = types.SimpleNamespace(
            get_listing=lambda name: listing,
            variant_price=lambda listing, code, settings: 25.00,
        )
        export.pricing_resolver = types.SimpleNamespace(
            resolve=lambda conn, codes: {"ITEM-1": 30.00})
        export._apply_price_updates = mock.Mock(
            return_value={"updated": [], "failed": {"ITEM-1": "Request to Shopify failed."}})
        export.retry_queue = mock.Mock()

        export.run_reprice_connection(connection="store-a")

        export.retry_queue.enqueue.assert_called_once()
        args, kwargs = export.retry_queue.enqueue.call_args
        self.assertEqual(args[0], "outbound")
        self.assertEqual(args[1], "price")
        self.assertEqual(args[2]["item_code_to_price"], {"ITEM-1": 30.00})
        self.assertEqual(kwargs.get("connection"), connection)

    def test_never_falls_back_to_push_item(self):
        """The one thing the issue calls unacceptable under any
        circumstance. Static rather than behavioural: push_item is never
        CALLED anywhere in the reprice code path -- it may still be named
        in prose (these functions' own docstrings explain why they avoid
        it), so this checks for a call expression, not the bare word."""
        import ast
        import inspect
        export = _load_export()
        for fn in (export.run_reprice_connection, export._apply_price_updates,
                   export.reprice_connection):
            tree = ast.parse(inspect.getsource(fn))
            called = {
                n.func.id for n in ast.walk(tree)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            }
            self.assertNotIn("push_item", called, fn.__name__)


class TestFingerprintRefreshAfterAPricePush(unittest.TestCase):
    """The gap the issue calls out by name: update_variant_prices writes
    neither fingerprint nor Shopify Synced Entity, so a repriced product
    would otherwise echo back as an unrecognised remote change and get
    re-pushed by the next push_item for nothing."""

    def test_a_successful_push_refreshes_the_stored_fingerprint(self):
        export = _load_export()

        listing = _listing("TEMPLATE-1", "store-a", "111", [("ITEM-1", 30.00)])
        export.listing_resolver = types.SimpleNamespace(get_listing=lambda name: listing)
        export.frappe.db.exists = lambda *a, **kw: True
        export.frappe.get_doc = lambda doctype, name: _FakeDoc(
            doctype=doctype, name=name, sh_shopify_product_id="111")
        export._variants_of = lambda item: ["variant-stub"]
        export._product_canonical = lambda item, variants, settings, listing: {"price": "30.00"}

        saved = {}
        entity = _FakeDoc(name="ENTITY-1", erpnext_fingerprint="stale")
        export.entities = types.SimpleNamespace(
            get_by_erpnext=lambda *a, **kw: entity,
            get_or_new=lambda *a, **kw: entity,
            save=lambda ent, **fields: saved.update(fields),
        )

        export._refresh_fingerprint_after_price_push("TEMPLATE-1", _FakeDoc(name="store-a"))

        expected_fp = export.fingerprint.fingerprint({"price": "30.00"})
        self.assertEqual(saved.get("erpnext_fingerprint"), expected_fp)
        self.assertEqual(saved.get("external_id"), "111")
        self.assertEqual(saved.get("erpnext_doctype"), "Item")
        self.assertEqual(saved.get("erpnext_name"), "TEMPLATE-1")

    def test_apply_price_updates_writes_back_price_and_refreshes_fingerprint(self):
        export = _load_export()
        connection = _FakeDoc(name="store-a")
        export.connections = types.SimpleNamespace(resolve=lambda c=None: connection)
        export.update_variant_prices = mock.Mock(
            return_value={"updated": ["ITEM-1"], "failed": {}})

        listing = _listing("TEMPLATE-1", "store-a", "111", [("ITEM-1", 25.00)])
        export.frappe.db.get_value = mock.Mock(
            return_value=_FakeDoc(variant_of=None, name="TEMPLATE-1"))
        export.listing_resolver = types.SimpleNamespace(get_listing=lambda name: listing)

        refreshed = []
        export._refresh_fingerprint_after_price_push = lambda template_name, settings: \
            refreshed.append(template_name)

        result = export._apply_price_updates({"ITEM-1": 30.00}, "store-a")

        self.assertEqual(result["updated"], ["ITEM-1"])
        export.frappe.db.set_value.assert_called_once_with(
            "Shopify Listing Variant", listing.variants[0].name, "variant_price", 30.00)
        self.assertEqual(refreshed, ["TEMPLATE-1"])


if __name__ == "__main__":
    unittest.main()
