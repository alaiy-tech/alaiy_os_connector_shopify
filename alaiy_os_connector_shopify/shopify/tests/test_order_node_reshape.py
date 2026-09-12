"""
_order_node_to_rest_shape has to hand the pull path the same dict shape the
webhook path already gets, so everything downstream reads one field name
whichever source an order came from. These pin the fields where the two
sources spell things differently -- province_code/country_code, and
current_quantity, whose absence used to make an edited pulled order
reconcile against the quantity it was placed with rather than the one it
still has.
"""

import unittest

from alaiy_os_connector_shopify.shopify.order.utils import (
    _format_risk_detail,
    _line_item_qty,
    _order_node_to_rest_shape,
)


def _node(**over):
    node = {
        "legacyResourceId": "5001",
        "name": "#1001",
        "createdAt": "2026-09-01T10:00:00Z",
        "updatedAt": "2026-09-02T11:00:00Z",
        "cancelledAt": None,
        "cancelReason": None,
        "currencyCode": "INR",
        "displayFinancialStatus": "PAID",
        "displayFulfillmentStatus": "FULFILLED",
        "email": "buyer@example.com",
        "phone": "+911234567890",
        "discountCodes": ["DIWALI10"],
        "currentTotalPriceSet": {"shopMoney": {"amount": "900.00"}},
        "currentSubtotalPriceSet": {"shopMoney": {"amount": "800.00"}},
        "currentTotalTaxSet": {"shopMoney": {"amount": "100.00"}},
        "currentTotalDiscountsSet": {"shopMoney": {"amount": "50.00"}},
        "customer": {
            "legacyResourceId": "9001",
            "firstName": "A",
            "lastName": "B",
            "defaultEmailAddress": {"emailAddress": "buyer@example.com"},
            "defaultPhoneNumber": {"phoneNumber": "+911234567890"},
        },
        "shippingAddress": {
            "name": "A B",
            "company": "Acme",
            "address1": "1 Road",
            "city": "Chennai",
            "province": "Tamil Nadu",
            "provinceCode": "TN",
            "country": "India",
            "countryCodeV2": "IN",
            "zip": "600001",
        },
        "lineItems": {"nodes": [{
            "sku": "SKU1",
            "title": "Thing",
            "quantity": 2,
            "currentQuantity": 1,
            "vendor": "Acme",
            "variant": {"legacyResourceId": "7001", "barcode": "890000000001"},
            "product": {"legacyResourceId": "6001"},
            "originalUnitPriceSet": {"shopMoney": {"amount": "500.00"}},
            "discountedUnitPriceSet": {"shopMoney": {"amount": "450.00"}},
            "discountedTotalSet": {"shopMoney": {"amount": "450.00"}},
        }]},
    }
    node.update(over)
    return node


class TestOrderNodeReshape(unittest.TestCase):
    def test_current_totals_survive_the_reshape(self):
        out = _order_node_to_rest_shape(_node())
        self.assertEqual(out["current_total_price"], "900.00")
        self.assertEqual(out["current_subtotal_price"], "800.00")
        self.assertEqual(out["current_total_tax"], "100.00")
        self.assertEqual(out["current_total_discounts"], "50.00")

    def test_missing_money_bag_reads_as_zero_not_none(self):
        out = _order_node_to_rest_shape(_node(currentTotalPriceSet=None))
        self.assertEqual(out["current_total_price"], "0")

    def test_address_codes_are_renamed_to_the_webhook_spelling(self):
        addr = _order_node_to_rest_shape(_node())["shipping_address"]
        self.assertEqual(addr["province_code"], "TN")
        self.assertEqual(addr["country_code"], "IN")
        self.assertEqual(addr["company"], "Acme")

    def test_absent_address_stays_none(self):
        out = _order_node_to_rest_shape(_node(shippingAddress=None))
        self.assertIsNone(out["shipping_address"])

    def test_line_item_carries_post_edit_quantity_and_discounted_price(self):
        li = _order_node_to_rest_shape(_node())["line_items"][0]
        self.assertEqual(li["current_quantity"], 1)
        self.assertEqual(li["discounted_price"], "450.00")
        self.assertEqual(li["barcode"], "890000000001")
        # A line edited down to 1 must not still bill for the 2 placed.
        self.assertEqual(_line_item_qty(li), 1)

    def test_line_removed_by_an_edit_counts_zero(self):
        node = _node()
        node["lineItems"]["nodes"][0]["currentQuantity"] = 0
        li = _order_node_to_rest_shape(node)["line_items"][0]
        self.assertEqual(_line_item_qty(li), 0)

    def test_absent_current_quantity_falls_back_and_is_not_read_as_removed(self):
        node = _node()
        del node["lineItems"]["nodes"][0]["currentQuantity"]
        li = _order_node_to_rest_shape(node)["line_items"][0]
        self.assertNotIn("current_quantity", li)
        self.assertEqual(_line_item_qty(li), 2)

    def test_cancel_fields_map(self):
        out = _order_node_to_rest_shape(_node(
            cancelledAt="2026-09-03T09:00:00Z", cancelReason="CUSTOMER"))
        self.assertEqual(out["cancelled_at"], "2026-09-03T09:00:00Z")
        self.assertEqual(out["cancel_reason"], "customer")

    def test_discount_codes_and_contact_map(self):
        out = _order_node_to_rest_shape(_node())
        self.assertEqual(out["discount_codes"], ["DIWALI10"])
        self.assertEqual(out["email"], "buyer@example.com")
        self.assertEqual(out["customer"]["phone"], "+911234567890")
        self.assertEqual(out["updated_at"], "2026-09-02T11:00:00Z")


class TestOrderRisk(unittest.TestCase):
    def test_no_risk_block_is_blank_not_a_false_flag(self):
        out = _order_node_to_rest_shape(_node())
        self.assertEqual(out["risk_level"], "")
        self.assertEqual(out["risk_recommendation"], "")
        self.assertEqual(out["risk_assessments"], [])

    def test_shopifys_own_recommendation_is_kept_alongside_the_level(self):
        # recommendation is Shopify's aggregate call and is NOT derived from
        # the assessments -- the two can disagree, so both are stored.
        out = _order_node_to_rest_shape(_node(risk={
            "recommendation": "CANCEL",
            "assessments": [
                {"riskLevel": "MEDIUM", "provider": {"title": "Shopify"}, "facts": []},
            ],
        }))
        self.assertEqual(out["risk_recommendation"], "CANCEL")
        self.assertEqual(out["risk_level"], "MEDIUM")

    def test_pending_ranks_below_every_real_verdict(self):
        # PENDING means "not assessed yet", not a severity. An order with a
        # PENDING and a HIGH is HIGH, not PENDING.
        out = _order_node_to_rest_shape(_node(risk={"assessments": [
            {"riskLevel": "PENDING", "provider": {"title": "Slow"}, "facts": []},
            {"riskLevel": "HIGH", "provider": {"title": "Shopify"}, "facts": []},
        ]}))
        self.assertEqual(out["risk_level"], "HIGH")

    def test_pending_still_beats_blank_when_it_is_all_there_is(self):
        # Blank would read as a clean order that had been checked.
        out = _order_node_to_rest_shape(_node(risk={"assessments": [
            {"riskLevel": "PENDING", "provider": {"title": "Slow"}, "facts": []},
        ]}))
        self.assertEqual(out["risk_level"], "PENDING")

    def test_none_outranks_pending(self):
        out = _order_node_to_rest_shape(_node(risk={"assessments": [
            {"riskLevel": "PENDING", "provider": {"title": "Slow"}, "facts": []},
            {"riskLevel": "NONE", "provider": {"title": "Shopify"}, "facts": []},
        ]}))
        self.assertEqual(out["risk_level"], "NONE")

    def test_worst_provider_wins(self):
        # One provider saying HIGH is the whole point of the flag, even when
        # another says LOW on the same order.
        out = _order_node_to_rest_shape(_node(risk={"assessments": [
            {"riskLevel": "LOW", "provider": {"title": "Shopify"}, "facts": []},
            {"riskLevel": "HIGH", "provider": {"title": "Fraud Filter"}, "facts": []},
            {"riskLevel": "MEDIUM", "provider": {"title": "Other"}, "facts": []},
        ]}))
        self.assertEqual(out["risk_level"], "HIGH")
        self.assertEqual(len(out["risk_assessments"]), 3)

    def test_single_none_assessment_stays_none(self):
        out = _order_node_to_rest_shape(_node(risk={"assessments": [
            {"riskLevel": "NONE", "provider": {"title": "Shopify"}, "facts": []},
        ]}))
        self.assertEqual(out["risk_level"], "NONE")

    def test_unknown_level_does_not_outrank_a_real_one(self):
        out = _order_node_to_rest_shape(_node(risk={"assessments": [
            {"riskLevel": "WEIRD", "provider": {"title": "X"}, "facts": []},
            {"riskLevel": "LOW", "provider": {"title": "Shopify"}, "facts": []},
        ]}))
        self.assertEqual(out["risk_level"], "LOW")

    def test_facts_survive_into_the_detail_text(self):
        out = _order_node_to_rest_shape(_node(risk={"assessments": [
            {"riskLevel": "HIGH", "provider": {"title": "Shopify"}, "facts": [
                {"description": "Card issuer country differs", "sentiment": "NEGATIVE"},
                {"description": "Billing matches shipping", "sentiment": "POSITIVE"},
            ]},
        ]}))
        detail = _format_risk_detail(out["risk_assessments"])
        self.assertIn("HIGH -- Shopify", detail)
        self.assertIn("[NEGATIVE] Card issuer country differs", detail)
        self.assertIn("[POSITIVE] Billing matches shipping", detail)

    def test_empty_assessments_format_to_empty_string(self):
        self.assertEqual(_format_risk_detail([]), "")


class TestRemainingFields(unittest.TestCase):
    def test_presentment_currency_is_kept_alongside_shop_currency(self):
        node = _node()
        node["currentTotalPriceSet"]["presentmentMoney"] = {
            "amount": "10.80", "currencyCode": "USD"}
        out = _order_node_to_rest_shape(node)
        self.assertEqual(out["current_total_price"], "900.00")
        self.assertEqual(out["presentment_total_price"], "10.80")
        self.assertEqual(out["presentment_currency"], "USD")

    def test_product_and_variant_detail_map(self):
        li = _order_node_to_rest_shape(_node())["line_items"][0]
        self.assertEqual(li["product_id"], "6001")
        self.assertEqual(li["variant_id"], "7001")
        self.assertEqual(li["vendor"], "Acme")

    def test_test_order_flag_and_confirmation_number(self):
        out = _order_node_to_rest_shape(_node(
            test=True, confirmationNumber="ABC123"))
        self.assertTrue(out["test"])
        self.assertEqual(out["confirmation_number"], "ABC123")

    def test_customer_default_address_reuses_the_address_mapper(self):
        node = _node()
        node["customer"]["defaultAddress"] = {
            "address1": "9 Lane", "provinceCode": "KA", "countryCodeV2": "IN"}
        cust = _order_node_to_rest_shape(node)["customer"]
        self.assertEqual(cust["default_address"]["province_code"], "KA")
        self.assertEqual(cust["default_address"]["country_code"], "IN")

    def test_customer_contact_reads_the_non_deprecated_objects(self):
        # Customer.email/.phone are deprecated on 2026-07; the values now
        # arrive under defaultEmailAddress/defaultPhoneNumber but must land
        # on the same keys every consumer already reads.
        cust = _order_node_to_rest_shape(_node())["customer"]
        self.assertEqual(cust["email"], "buyer@example.com")
        self.assertEqual(cust["phone"], "+911234567890")

    def test_customer_contact_falls_back_to_the_legacy_keys(self):
        # A cached or webhook-shaped payload may still carry the flat fields.
        node = _node()
        node["customer"] = {
            "legacyResourceId": "9001",
            "email": "old@example.com",
            "phone": "+910000000000",
        }
        cust = _order_node_to_rest_shape(node)["customer"]
        self.assertEqual(cust["email"], "old@example.com")
        self.assertEqual(cust["phone"], "+910000000000")

    def test_customer_without_id_stays_empty(self):
        out = _order_node_to_rest_shape(_node(customer=None))
        self.assertEqual(out["customer"], {})


if __name__ == "__main__":
    unittest.main()
