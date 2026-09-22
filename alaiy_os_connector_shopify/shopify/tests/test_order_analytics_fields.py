"""
Three reporting fields the order pull was not carrying (#153, #155, #157).

None of them change how an order syncs. They record facts Shopify already
had and we were dropping, so the numbers behind per-SKU margin, handling
time and processing cost can be computed at all.

The two parsers are pure and are executed here against real payload shapes.
The rest is structural -- the write paths need a bench.

    python -m unittest alaiy_os_connector_shopify.shopify.tests.test_order_analytics_fields
"""

import ast
import pathlib
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_UTILS = _ROOT / "shopify" / "order" / "utils.py"
_QUERIES = _ROOT / "shopify" / "order" / "queries.py"
_DN = _ROOT / "shopify" / "order" / "delivery_notes.py"
_INSTALL = _ROOT / "setup" / "install.py"
_UPSERT = _ROOT / "shopify" / "order" / "upsert.py"
_UPDATE = _ROOT / "shopify" / "order" / "update.py"


def _load(name):
    """One pure helper out of utils.py, without importing frappe."""
    src = _UTILS.read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = {"flt": lambda v: float(v or 0)}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<x>", "exec"), ns)
    return ns[name]


class DiscountAllocations(unittest.TestCase):
    """#157 -- which discount reduced which line."""

    def setUp(self):
        self.fn = _load("_discount_allocations")

    def test_a_discount_code_is_named(self):
        got = self.fn({"discountAllocations": [{
            "allocatedAmountSet": {"shopMoney": {"amount": "12.50"}},
            "discountApplication": {"code": "SUMMER20"}}]})
        self.assertEqual(got, [{"code": "SUMMER20", "amount": 12.5}])

    def test_an_automatic_discount_falls_back_to_its_title(self):
        """Shopify names a code on DiscountCodeApplication and a title on the
        automatic and manual ones -- never both, so one field has to serve."""
        got = self.fn({"discountAllocations": [{
            "allocatedAmountSet": {"shopMoney": {"amount": "5"}},
            "discountApplication": {"title": "Auto 10%"}}]})
        self.assertEqual(got, [{"code": "Auto 10%", "amount": 5.0}])

    def test_two_codes_on_one_line_stay_separate(self):
        """The whole point: an order-level total cannot tell these apart."""
        got = self.fn({"discountAllocations": [
            {"allocatedAmountSet": {"shopMoney": {"amount": "3"}},
             "discountApplication": {"code": "A"}},
            {"allocatedAmountSet": {"shopMoney": {"amount": "7"}},
             "discountApplication": {"title": "B"}}]})
        self.assertEqual([g["code"] for g in got], ["A", "B"])

    def test_no_discount_is_an_empty_list(self):
        self.assertEqual(self.fn({}), [])

    def test_the_query_asks_for_it(self):
        self.assertIn("discountAllocations", _QUERIES.read_text(encoding="utf-8"))


class PaymentFee(unittest.TestCase):
    """#153 -- what the gateway charged."""

    def setUp(self):
        self.fn = _load("_payment_fee")

    def test_a_sale_fee_is_counted(self):
        self.assertEqual(self.fn({"transactions": [
            {"kind": "SALE", "status": "SUCCESS",
             "fees": [{"amount": {"amount": "2.90"}}]}]}), 2.90)

    def test_a_refund_fee_is_not_netted_out(self):
        """A refund carries its own fee entry. Including it reports nearly
        nothing on a refunded order, when the figure worth having is what
        the processor actually kept."""
        self.assertEqual(self.fn({"transactions": [
            {"kind": "SALE", "status": "SUCCESS",
             "fees": [{"amount": {"amount": "2.90"}}]},
            {"kind": "REFUND", "status": "SUCCESS",
             "fees": [{"amount": {"amount": "-2.90"}}]}]}), 2.90)

    def test_a_failed_transaction_is_ignored(self):
        self.assertIsNone(self.fn({"transactions": [
            {"kind": "SALE", "status": "FAILURE",
             "fees": [{"amount": {"amount": "2.90"}}]}]}))

    def test_no_reported_fee_is_none_not_zero(self):
        """Most third-party gateways report nothing here. A 0 would read as
        'this order cost nothing to process' when the truth is unknown."""
        self.assertIsNone(self.fn({"transactions": [
            {"kind": "SALE", "status": "SUCCESS", "fees": []}]}))
        self.assertIsNone(self.fn({}))

    def test_several_captures_sum(self):
        self.assertEqual(self.fn({"transactions": [
            {"kind": "CAPTURE", "status": "SUCCESS",
             "fees": [{"amount": {"amount": "1.00"}}]},
            {"kind": "CAPTURE", "status": "SUCCESS",
             "fees": [{"amount": {"amount": "0.50"}}]}]}), 1.50)

    def test_an_absent_fee_never_blanks_a_recorded_one(self):
        """The REST webhook carries no transactions at all, so writing
        unconditionally would erase the pull's figure on the next update."""
        for path in (_UPSERT, _UPDATE):
            self.assertIn('payment_fee") is not None', path.read_text(encoding="utf-8"))

    def test_the_field_exists(self):
        self.assertIn("sh_payment_fee", _INSTALL.read_text(encoding="utf-8"))


class HandlingHours(unittest.TestCase):
    """#155 -- order placed to dispatch confirmed."""

    def _fn_source(self):
        src = _DN.read_text(encoding="utf-8")
        return src[src.index("def _record_handling_hours"):src.index("def _create_delivery_note_if_needed")]

    def test_it_is_written_once_not_per_parcel(self):
        """A split shipment produces several Delivery Notes. Overwriting on
        each leaves the figure describing the last parcel rather than how
        long the customer waited to hear their order had shipped."""
        self.assertIn("sh_handling_hours", self._fn_source())
        self.assertIn("if frappe.db.get_value", self._fn_source())

    def test_a_negative_is_refused(self):
        """A Delivery Note dated before its own order is a data problem, not
        a fast dispatch -- recording it would drag an average below zero."""
        self.assertIn("hours < 0", self._fn_source())

    def test_it_cannot_fail_the_delivery_note(self):
        """The DN has already submitted by then. A reporting figure must not
        be the reason its transaction rolls back."""
        self.assertIn("except Exception", self._fn_source())

    def test_both_delivery_note_paths_record_it(self):
        """_sync_fulfillments and the _create_delivery_note_if_needed
        fallback both submit a DN, and an order can arrive down either."""
        self.assertEqual(_DN.read_text(encoding="utf-8").count("_record_handling_hours("), 3)

    def test_the_field_exists(self):
        self.assertIn("sh_handling_hours", _INSTALL.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
