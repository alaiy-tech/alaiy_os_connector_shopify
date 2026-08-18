"""
Variant swap, shipping-line push, and custom-item push via Shopify's Order
Editing API (#88's remaining gaps). A swap is not a single Shopify mutation
-- orderEditAddVariant is additive-only -- so it composes
orderEditSetQuantity(old, 0) + orderEditAddVariant(new), and must carry the
old line's LINE-level discount over explicitly since Shopify doesn't. These
tests mock frappe and the GraphQL client to prove the payloads/sequencing
are correct without touching a real store.
"""

import unittest
from unittest.mock import patch, MagicMock

from alaiy_os_connector_shopify.shopify.order.push_line_items import (
    _apply_shopify_line_item_changes, _line_item_discount_total,
)


def _begin_response(line_items):
    return {
        "orderEditBegin": {
            "calculatedOrder": {"id": "gid://shopify/CalculatedOrder/1", "lineItems": {"nodes": line_items}},
            "userErrors": [],
        }
    }


class TestLineItemDiscountTotal(unittest.TestCase):
    def test_sums_only_line_level_allocations(self):
        li = {
            "calculatedDiscountAllocations": [
                {"allocatedAmountSet": {"shopMoney": {"amount": "5.00"}}, "discountApplication": {"targetType": "LINE_ITEM"}},
                {"allocatedAmountSet": {"shopMoney": {"amount": "10.00"}}, "discountApplication": {"targetType": "ORDER"}},
            ]
        }
        self.assertEqual(_line_item_discount_total(li), 5.0)

    def test_no_allocations_is_zero(self):
        self.assertEqual(_line_item_discount_total({}), 0.0)


class TestVariantSwap(unittest.TestCase):
    def test_swap_zeroes_old_and_adds_new_and_carries_discount(self):
        old_line = {
            "id": "gid://shopify/CalculatedLineItem/OLD",
            "variant": {"legacyResourceId": "111"},
            "calculatedDiscountAllocations": [
                {"allocatedAmountSet": {"shopMoney": {"amount": "8.00"}}, "discountApplication": {"targetType": "LINE_ITEM"}},
            ],
        }
        client = MagicMock()
        client.execute.side_effect = [
            _begin_response([old_line]),
            {"orderEditSetQuantity": {"userErrors": []}},
            {"orderEditAddVariant": {"calculatedLineItem": {"id": "gid://shopify/CalculatedLineItem/NEW"}, "userErrors": []}},
            {"orderEditAddLineItemDiscount": {"userErrors": []}},
            {"orderEditCommit": {"userErrors": []}},
        ]
        with patch("alaiy_os_connector_shopify.shopify.graphql_client.ShopifyGraphQLClient", return_value=client), \
             patch("frappe.db.get_value", return_value="USD"), \
             patch("frappe.log_error"):
            ok = _apply_shopify_line_item_changes(
                order_id="999", removed_variant_ids=[], added_items=[], sales_order="SO-1",
                swapped_variants=[{"from_variant_id": "111", "to_variant_id": "222", "qty": 2}],
            )
        self.assertTrue(ok)
        calls = client.execute.call_args_list
        # call 2: zero the old line
        self.assertEqual(calls[1].args[1]["lineItemId"], "gid://shopify/CalculatedLineItem/OLD")
        self.assertEqual(calls[1].args[1]["quantity"], 0)
        # call 3: add the new variant
        self.assertIn("222", calls[2].args[1]["variantId"])
        self.assertEqual(calls[2].args[1]["quantity"], 2)
        # call 4: discount carried over onto the NEW line, not the old one
        self.assertEqual(calls[3].args[1]["lineItemId"], "gid://shopify/CalculatedLineItem/NEW")
        self.assertEqual(calls[3].args[1]["discount"]["fixedValue"]["amount"], "8.0")

    def test_swap_without_discount_skips_discount_call(self):
        old_line = {"id": "gid://shopify/CalculatedLineItem/OLD", "variant": {"legacyResourceId": "111"}}
        client = MagicMock()
        client.execute.side_effect = [
            _begin_response([old_line]),
            {"orderEditSetQuantity": {"userErrors": []}},
            {"orderEditAddVariant": {"calculatedLineItem": {"id": "gid://shopify/CalculatedLineItem/NEW"}, "userErrors": []}},
            {"orderEditCommit": {"userErrors": []}},
        ]
        with patch("alaiy_os_connector_shopify.shopify.graphql_client.ShopifyGraphQLClient", return_value=client), \
             patch("frappe.db.get_value", return_value="USD"), \
             patch("frappe.log_error"):
            ok = _apply_shopify_line_item_changes(
                order_id="999", removed_variant_ids=[], added_items=[], sales_order="SO-1",
                swapped_variants=[{"from_variant_id": "111", "to_variant_id": "222", "qty": 1}],
            )
        self.assertTrue(ok)
        self.assertEqual(client.execute.call_count, 4)  # no 5th discount call

    def test_swap_from_variant_not_found_fails_closed(self):
        client = MagicMock()
        client.execute.side_effect = [_begin_response([])]
        with patch("alaiy_os_connector_shopify.shopify.graphql_client.ShopifyGraphQLClient", return_value=client), \
             patch("frappe.db.get_value", return_value="USD"), \
             patch("frappe.log_error"):
            ok = _apply_shopify_line_item_changes(
                order_id="999", removed_variant_ids=[], added_items=[], sales_order="SO-1",
                swapped_variants=[{"from_variant_id": "999", "to_variant_id": "222", "qty": 1}],
            )
        self.assertFalse(ok)


class TestShippingLinePush(unittest.TestCase):
    def test_add_shipping_line(self):
        client = MagicMock()
        client.execute.side_effect = [
            _begin_response([]),
            {"orderEditAddShippingLine": {"userErrors": []}},
            {"orderEditCommit": {"userErrors": []}},
        ]
        with patch("alaiy_os_connector_shopify.shopify.graphql_client.ShopifyGraphQLClient", return_value=client), \
             patch("frappe.db.get_value", return_value="INR"), \
             patch("frappe.log_error"):
            ok = _apply_shopify_line_item_changes(
                order_id="999", removed_variant_ids=[], added_items=[], sales_order="SO-1",
                shipping_line={"title": "Express", "price": 15},
            )
        self.assertTrue(ok)
        add_call = client.execute.call_args_list[1]
        self.assertEqual(add_call.args[1]["shippingLine"]["title"], "Express")
        self.assertEqual(add_call.args[1]["shippingLine"]["price"]["currencyCode"], "INR")


class TestCustomItemPush(unittest.TestCase):
    def test_add_custom_item(self):
        client = MagicMock()
        client.execute.side_effect = [
            _begin_response([]),
            {"orderEditAddCustomItem": {"calculatedLineItem": {"id": "x"}, "userErrors": []}},
            {"orderEditCommit": {"userErrors": []}},
        ]
        with patch("alaiy_os_connector_shopify.shopify.graphql_client.ShopifyGraphQLClient", return_value=client), \
             patch("frappe.db.get_value", return_value="USD"), \
             patch("frappe.log_error"):
            ok = _apply_shopify_line_item_changes(
                order_id="999", removed_variant_ids=[], added_items=[], sales_order="SO-1",
                custom_items=[{"title": "Gift Wrap", "price": 5, "qty": 1}],
            )
        self.assertTrue(ok)
        custom_call = client.execute.call_args_list[1]
        self.assertEqual(custom_call.args[1]["title"], "Gift Wrap")
        self.assertEqual(custom_call.args[1]["price"]["amount"], "5")


if __name__ == "__main__":
    unittest.main()
