"""ShopifyGraphQLClient.execute's MAX_COST_EXCEEDED retry.

A store with unusually heavy products (many variants/metafields/media) can
push a paginated pull's page size past Shopify's single-query cost ceiling
(1000 points) -- confirmed live on a real store: run_full_product_import
failed permanently with no way to recover short of a code change, since
MAX_COST_EXCEEDED is not a transient rate limit and retrying the identical
query would fail identically forever.

execute() now halves the query's `first` variable and retries, repeating
(bounded) until it fits or a floor of 1 is reached -- and since
execute_paginated reuses the same variables dict object across every page,
a shrink here also lowers every later page's request, not just the one
that happened to hit the ceiling first.

Run via `bench run-tests`, but this needs no site: frappe and requests are
stubbed, and the client under test is built with __new__ (skipping
__init__'s connection/token resolution) since only `execute`'s own logic is
being pinned here.
"""

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _stub_frappe():
    frappe = types.ModuleType("frappe")
    frappe.logger = lambda: types.SimpleNamespace(info=lambda *a, **k: None)
    frappe._ = lambda s: s
    frappe.ValidationError = Exception
    sys.modules["frappe"] = frappe
    sys.modules.setdefault("requests", types.ModuleType("requests"))

    # graphql_client.py imports these at module scope purely for __init__
    # (connection resolution, token refresh) -- neither is exercised by
    # this test, which builds the client via __new__ and never calls
    # __init__. Stubbed rather than pulling in their own real frappe
    # dependency chains. Real package __path__ preserved so the actual
    # alaiy_os_connector_shopify.shopify.graphql_client submodule can still
    # be found and imported normally.
    connections = types.ModuleType("alaiy_os_connector_shopify.connections")
    connections.resolve = lambda connection=None: None
    auth = types.ModuleType("alaiy_os_connector_shopify.shopify.auth")
    auth.refresh_and_store_access_token = lambda connection=None: ""
    sys.modules["alaiy_os_connector_shopify.connections"] = connections
    sys.modules["alaiy_os_connector_shopify.shopify.auth"] = auth
    return frappe


def _client(responses):
    """A ShopifyGraphQLClient whose session.post replays `responses` in
    order (each a dict body), skipping the real __init__ entirely -- no
    connection doc, no token, no network."""
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    client = ShopifyGraphQLClient.__new__(ShopifyGraphQLClient)
    client.endpoint = "https://example.myshopify.com/admin/api/2026-07/graphql.json"
    client.token = "shpat_test"

    calls = []

    class _Resp:
        def __init__(self, body):
            self.status_code = 200
            self._body = body

        def raise_for_status(self):
            pass

        def json(self):
            return self._body

    class _Session:
        def post(self, url, json=None, timeout=None):
            calls.append(dict(json["variables"]))
            return _Resp(responses[len(calls) - 1])

    client.session = _Session()
    return client, calls


_COST_ERROR = [{
    "message": "Query cost is 1066, which exceeds the single query max cost limit (1000).",
    "extensions": {"code": "MAX_COST_EXCEEDED", "cost": 1066, "maxCost": 1000},
}]


class CostExceededRetriesWithSmallerPage(unittest.TestCase):
    def setUp(self):
        _stub_frappe()

    def test_halves_first_on_cost_exceeded_and_succeeds(self):
        client, calls = _client([
            {"errors": _COST_ERROR},
            {"data": {"products": {"edges": []}}},
        ])
        data = client.execute("query {}", {"first": 50, "after": None})

        self.assertEqual(data, {"products": {"edges": []}})
        self.assertEqual([c["first"] for c in calls], [50, 25],
                          "first retry must halve the page size, not repeat it unchanged")

    def test_keeps_halving_across_several_failures(self):
        client, calls = _client([
            {"errors": _COST_ERROR},
            {"errors": _COST_ERROR},
            {"errors": _COST_ERROR},
            {"data": {"products": {"edges": []}}},
        ])
        client.execute("query {}", {"first": 50, "after": None})

        self.assertEqual([c["first"] for c in calls], [50, 25, 12, 6])

    def test_stops_at_the_floor_of_one(self):
        # Always fails -- proves the retry loop terminates rather than
        # halving forever or crashing once first reaches 1.
        client, calls = _client([{"errors": _COST_ERROR}] * 10)
        with self.assertRaises(RuntimeError):
            client.execute("query {}", {"first": 50, "after": None})

        firsts = [c["first"] for c in calls]
        self.assertEqual(firsts[-1], 1, "must reach the floor of 1, not stop above it")
        self.assertTrue(
            all(a >= b for a, b in zip(firsts, firsts[1:])),
            f"first must never increase between retries, got {firsts}",
        )

    def test_gives_up_after_the_retry_cap_even_if_still_too_big(self):
        # More failures than _MAX_COST_RETRIES allows -- must raise, not
        # loop forever or silently succeed on a call that never returned data.
        client, calls = _client([{"errors": _COST_ERROR}] * 20)
        with self.assertRaises(RuntimeError):
            client.execute("query {}", {"first": 1000, "after": None})

        self.assertLessEqual(len(calls), 8, "must not retry unboundedly")

    def test_no_first_variable_raises_immediately(self):
        # A mutation or a non-paginated query has no `first` to shrink --
        # must not crash trying to halve a missing/non-int value, must
        # just surface the real error.
        client, calls = _client([{"errors": _COST_ERROR}])
        with self.assertRaises(RuntimeError):
            client.execute("mutation {}", {"id": "gid://shopify/Product/1"})
        self.assertEqual(len(calls), 1, "must not retry when there's no first to shrink")

    def test_non_cost_error_is_not_retried_by_this_path(self):
        client, calls = _client([{"errors": [{
            "message": "Field 'bogus' doesn't exist",
            "extensions": {"code": "GRAPHQL_VALIDATION_FAILED"},
        }]}])
        with self.assertRaises(RuntimeError):
            client.execute("query {}", {"first": 50})
        self.assertEqual(len(calls), 1, "an unrelated error must not trigger the cost retry")

    def test_shrunk_first_carries_forward_in_the_same_variables_object(self):
        """execute_paginated reuses one variables dict across every page --
        a shrink on page 1 must still be in effect on page 2, not reset,
        since the store that triggered this is heavy throughout its
        catalog, not just on the first page."""
        client, calls = _client([
            {"errors": _COST_ERROR},
            {"data": {"products": {"edges": [], "pageInfo": {"hasNextPage": False}}}},
        ])
        variables = {"first": 50, "after": None}
        client.execute("query {}", variables)

        self.assertEqual(variables["first"], 25,
                          "the caller's own variables dict must reflect the shrink, "
                          "so a later page reusing it inherits the smaller size")


if __name__ == "__main__":
    unittest.main(verbosity=2)
