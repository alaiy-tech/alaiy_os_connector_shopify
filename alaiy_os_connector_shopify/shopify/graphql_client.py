import time
import uuid

import requests
import frappe

from alaiy_os_connector_shopify import connections
from alaiy_os_connector_shopify.shopify.auth import refresh_and_store_access_token

SHOPIFY_API_VERSION = "2026-07"

# (connect, read) seconds. Without this a stalled Shopify response blocks the
# worker until the RQ job-level death penalty (e.g. 600s) kills the WHOLE
# sync mid-loop; with it a hung call raises requests.Timeout, which callers'
# per-item try/except turns into a single skipped item instead.
REQUEST_TIMEOUT = (10, 60)


class ShopifyGraphQLClient:
    """
    Thin wrapper over the Shopify Admin GraphQL API, scoped to one store.

    `connection` is a Shopify Connection, its id, or None. None means "the only
    store on this bench", which is every single-store site and is why callers
    that predate multiple connections did not have to change; on a bench with
    several it refuses rather than guessing (see connections.resolve).
    """

    def __init__(self, connection=None):
        self.connection = connections.resolve(connection)
        settings = self.connection
        if not settings.sh_shop_url:
            raise RuntimeError("Shopify Shop URL is not configured.")
        if not settings.sh_access_token:
            raise RuntimeError("Shopify Access Token is not configured.")

        shop_url = settings.sh_shop_url.strip().rstrip("/")
        if not shop_url.startswith("http"):
            shop_url = f"https://{shop_url}"

        self.endpoint = f"{shop_url}/admin/api/{SHOPIFY_API_VERSION}/graphql.json"
        self.token = settings.get_password("sh_access_token")

        self.session = requests.Session()
        self.session.headers.update({
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json",
        })

    def _refresh_token(self):
        """Same pattern as the old REST client: mint a fresh token and
        update both the stored setting and this client's own session
        header in place."""
        self.token = refresh_and_store_access_token(self.connection)
        self.session.headers.update({"X-Shopify-Access-Token": self.token})

    # 50 -> 25 -> 13 -> 7 -> 4 -> 2 -> 1: six halvings from the largest
    # realistic default page size (50) reaches the floor of 1, so this
    # caps the number of extra requests one page can cost without ever
    # needing to reach the floor in practice for anything short of a
    # single pathologically heavy product.
    _MAX_COST_RETRIES = 6

    def execute(self, query: str, variables: dict = None, _retried_throttle: bool = False,
                _cost_retries: int = 0) -> dict:
        """
        Run a GraphQL query/mutation. Returns the `data` object.

        Shopify can return HTTP 200 with a top-level `errors` array for
        query-level failures (bad syntax, missing scope, throttling) --
        distinct from `userErrors` inside a mutation's own payload,  which
        callers must still check themselves. Raise on the top-level array
        here so a malformed query never silently reads back as `{}`.

        A THROTTLED error (query-cost bucket exhausted, a transient rate
        limit) is retried once after waiting long enough for the bucket to
        refill, using the `throttleStatus` Shopify includes on the error
        itself.

        MAX_COST_EXCEEDED is a different, non-transient failure -- the
        query's OWN shape costs more than Shopify's single-query ceiling
        (1000 points), independent of any bucket state, so retrying the
        exact same call would fail identically forever. Confirmed live: a
        store with unusually heavy products (many variants/metafields/
        media) pushed a paginated pull's default page size past the
        ceiling, permanently failing run_full_product_import with no way
        to recover short of a code change -- and that store's catalog is
        uniformly heavy, so a single halved retry on just the first page
        would only push the same failure to whichever later page crossed
        the ceiling next.

        When the query has an integer `first` variable, halve it and
        retry, repeating (bounded by _MAX_COST_RETRIES) until it fits or
        the floor of 1 is reached. The mutated dict is returned to the
        caller via `variables.clear()`+update in place (execute_paginated
        reuses the same dict object across every page), so a shrink here
        also lowers every subsequent page's request -- the whole point,
        since the catalog that triggered this is heavy throughout, not
        just on the page that happened to hit the ceiling first.
        """
        payload = {"query": query, "variables": variables or {}}
        resp = self.session.post(self.endpoint, json=payload, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 401:
            self._refresh_token()
            resp = self.session.post(self.endpoint, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()

        body = resp.json()
        if body.get("errors"):
            if not _retried_throttle and self._is_throttled(body["errors"]):
                time.sleep(self._throttle_wait_seconds(body["errors"]))
                return self.execute(query, variables, _retried_throttle=True, _cost_retries=_cost_retries)
            if (_cost_retries < self._MAX_COST_RETRIES and self._is_cost_exceeded(body["errors"])
                    and variables and isinstance(variables.get("first"), int) and variables["first"] > 1):
                variables["first"] = max(1, variables["first"] // 2)
                frappe.logger().info(
                    f"Shopify: query cost exceeded, retrying with first={variables['first']}"
                )
                return self.execute(query, variables, _retried_throttle=_retried_throttle,
                                     _cost_retries=_cost_retries + 1)
            raise RuntimeError(f"Shopify GraphQL error: {body['errors']}")
        return body.get("data") or {}

    @staticmethod
    def _is_throttled(errors: list) -> bool:
        return any(
            (err.get("extensions") or {}).get("code") == "THROTTLED"
            for err in errors
        )

    @staticmethod
    def _is_cost_exceeded(errors: list) -> bool:
        return any(
            (err.get("extensions") or {}).get("code") == "MAX_COST_EXCEEDED"
            for err in errors
        )

    @staticmethod
    def _throttle_wait_seconds(errors: list, default: float = 2.0) -> float:
        for err in errors:
            throttle_status = ((err.get("extensions") or {}).get("cost") or {}).get("throttleStatus") or {}
            available = throttle_status.get("currentlyAvailable")
            restore_rate = throttle_status.get("restoreRate")
            if available is not None and restore_rate:
                # Cost of the next call isn't known ahead of time -- wait
                # long enough to restore a modest buffer (50 points) rather
                # than the whole bucket.
                needed = max(0, 50 - available)
                return needed / restore_rate if needed else default
        return default

    def execute_paginated(self, query: str, variables: dict, connection_path: list):
        """
        Generic cursor-pagination generator. `connection_path` is the list
        of keys to walk from `data` down to the connection object (e.g.
        ["orders"]). Yields each page's list of `node` dicts. Mutates and
        reuses the passed-in `variables` dict across pages, so it must
        already contain every non-pagination variable the query needs.
        """
        variables = dict(variables or {})
        while True:
            data = self.execute(query, variables)
            connection = data
            for key in connection_path:
                connection = (connection or {}).get(key)
            connection = connection or {}
            edges = connection.get("edges") or []
            yield [edge["node"] for edge in edges]

            page_info = connection.get("pageInfo") or {}
            if not page_info.get("hasNextPage"):
                break
            variables["after"] = page_info.get("endCursor")


def new_idempotency_key() -> str:
    """Fresh key for Shopify's now-mandatory @idempotent directive on
    inventory mutations (required as of API 2026-04)."""
    return str(uuid.uuid4())
