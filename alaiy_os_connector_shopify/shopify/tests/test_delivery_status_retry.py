"""A delivery-status batch is retried once on a Shopify 5xx or timeout."""

import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import requests


def _module():
    sys.modules.setdefault("frappe", MagicMock())
    from alaiy_os_connector_shopify.shopify.order import delivery_status

    return delivery_status


def _http_error(code):
    return requests.exceptions.HTTPError(response=SimpleNamespace(status_code=code))


class _Client:
    def __init__(self, *outcomes):
        self.outcomes, self.calls = list(outcomes), 0

    def execute(self, query, variables):
        self.calls += 1
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return out


class TestExecuteWithRetry(unittest.TestCase):
    def setUp(self):
        self.ds = _module()
        patcher = patch("time.sleep")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_gateway_timeout_then_success(self):
        client = _Client(_http_error(504), {"nodes": []})
        self.assertEqual(self.ds._execute_with_retry(client, "q", {}), {"nodes": []})
        self.assertEqual(client.calls, 2)

    def test_timeout_then_success(self):
        client = _Client(requests.exceptions.ReadTimeout(), {"ok": 1})
        self.assertEqual(self.ds._execute_with_retry(client, "q", {}), {"ok": 1})

    def test_second_failure_propagates(self):
        client = _Client(_http_error(504), _http_error(502))
        with self.assertRaises(requests.exceptions.HTTPError):
            self.ds._execute_with_retry(client, "q", {})
        self.assertEqual(client.calls, 2)

    def test_client_error_is_not_retried(self):
        client = _Client(_http_error(403))
        with self.assertRaises(requests.exceptions.HTTPError):
            self.ds._execute_with_retry(client, "q", {})
        self.assertEqual(client.calls, 1)


if __name__ == "__main__":
    unittest.main()
