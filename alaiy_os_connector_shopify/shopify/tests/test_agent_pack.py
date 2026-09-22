"""Pure-logic tests for the agent pack manifest, its CSV export and its arithmetic.

Run via `bench run-tests` alongside the rest of this directory (needs a site
context, same as the other tests in this app -- `frappe.throw` wants translations
and `flt` wants the site's precision, even though nothing here reads a table).

The half that needs a site for real -- resolving every handler through
`frappe.get_attr`, and the roles and doctype permission rows -- is
`test_agent_handlers.py`.

Several of these pin invariants that are load-bearing and silent when broken:
the CSV envelope threshold (an off-by-one exports the summary line instead of
the rows), the handler prefix (a tool pointed past `api/agent.py` runs with the
permission gate removed), and the three separate status vocabularies never
sharing a parameter name.
"""

import inspect
import json
import unittest

from alaiy_os_connector_shopify import csv_export, pack_meta, sales
from alaiy_os_connector_shopify.shopify.product import register


class TestPackManifest(unittest.TestCase):
    def test_tool_ids_are_unique(self):
        ids = [tool["tool_id"] for tool in pack_meta.TOOLS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_tool_is_fully_specified(self):
        for tool in pack_meta.TOOLS:
            for key in ("tool_id", "description", "handler", "parameters_schema"):
                self.assertTrue(tool.get(key), f"{tool.get('tool_id')} is missing {key}")
            self.assertIsInstance(tool["required_permissions"], list)

    def test_every_handler_is_the_whitelisted_layer(self):
        """The permission gate lives in api/agent.py and travels with the call.

        A handler pointed at `shopify/product/register.py` or the GraphQL client
        would run the same code with the gate removed. A string test, so it
        needs no site and no imports.
        """
        for tool in pack_meta.TOOLS:
            self.assertTrue(
                tool["handler"].startswith("alaiy_os_connector_shopify.api.agent."),
                f"{tool['tool_id']} points outside api/agent.py: {tool['handler']}",
            )

    def test_registry_rows_carry_json_and_the_connector(self):
        for tool in pack_meta.TOOLS:
            row = pack_meta.as_registry_tool(tool)
            self.assertEqual(row["connector"], pack_meta.CONNECTOR_ID)
            self.assertEqual(json.loads(row["parameters_schema"])["type"], "object")
            if row["required_permissions"]:
                for entry in json.loads(row["required_permissions"]):
                    self.assertEqual(set(entry), {"doctype", "ptype"})

    def test_live_tools_declare_no_doctype_permission(self):
        """A live Shopify call is gated on a ROLE, which the field cannot express.

        `required_permissions` is a list of {doctype, ptype}; what these tools
        guard is Shopify's rate limit, not a doctype. They declare nothing and
        call `roles.require_manager()` themselves.
        """
        for tool_id in ("compare_listing", "get_store_counts", "get_collection_products"):
            tool = self._tool(tool_id)
            self.assertEqual(tool["required_permissions"], [])

    def test_every_sales_read_declares_the_permission_it_checks(self):
        for tool_id in (
            "get_sales_summary",
            "get_top_selling_products",
            "get_product_sales",
            "compare_sales_periods",
            "list_shopify_orders",
            "get_orders_sync_status",
        ):
            self.assertEqual(
                self._tool(tool_id)["required_permissions"],
                [{"doctype": "Sales Order", "ptype": "read"}],
            )

    def test_export_csv_is_the_only_write_and_is_gated_on_file_create(self):
        self.assertEqual(
            self._tool("export_csv")["required_permissions"],
            [{"doctype": "File", "ptype": "create"}],
        )

    def test_nothing_is_named_issues(self):
        """Shopify has no issues feed; naming a local judgement `issues` would lie.

        See pack_meta's docstring. `get_listing_gaps` is our own judgement and
        `get_listing_drift` is local-vs-last-push; neither is Shopify's verdict,
        because Shopify does not have one.
        """
        for tool in pack_meta.TOOLS:
            self.assertNotIn("issue", tool["tool_id"])

    def test_the_three_status_vocabularies_never_share_a_parameter_name(self):
        """One name covering two enums across one pack is a trap.

        This pack carries three: the listing's Active/Draft/Archived, and the
        order-level financial and fulfillment statuses. A model that has just
        read one tool must not be able to carry a value into another.
        """
        by_param = {}
        for tool in pack_meta.TOOLS:
            for name, spec in tool["parameters_schema"].get("properties", {}).items():
                if "enum" not in spec:
                    continue
                seen = by_param.setdefault(name, set())
                seen.add(tuple(spec["enum"]))
        for name, enums in by_param.items():
            self.assertEqual(len(enums), 1, f"parameter {name} carries {len(enums)} vocabularies")

        # And each vocabulary is reachable under exactly one name.
        self.assertEqual(by_param["status"], {tuple(pack_meta._LISTING_STATUSES)})
        self.assertEqual(by_param["financial_status"], {tuple(pack_meta._FINANCIAL_STATUSES)})
        self.assertEqual(by_param["fulfillment_status"], {tuple(pack_meta._FULFILLMENT_STATUSES)})

    def test_manifest_vocabularies_match_the_modules_that_enforce_them(self):
        """The schema enum and the runtime validator must not drift apart."""
        self.assertEqual(tuple(pack_meta._FINANCIAL_STATUSES), sales.FINANCIAL_STATUSES)
        self.assertEqual(tuple(pack_meta._FULFILLMENT_STATUSES), sales.FULFILLMENT_STATUSES)
        self.assertEqual(tuple(pack_meta._LISTING_STATUSES), register.LISTING_STATUSES)
        self.assertEqual(tuple(pack_meta._GAPS), tuple(register._GAP_SQL))
        self.assertEqual(tuple(pack_meta._GRANULARITIES), sales.GRANULARITIES)

    def test_every_gap_names_the_resolver_it_mirrors(self):
        """register._GAP_SQL restates listing.py's fallback chains in SQL.

        The pairing is the thing to keep in step by hand, so it is written down
        in GAPS and pinned here -- a new gap with no resolver named is a gap
        nobody will know to update.
        """
        self.assertEqual(set(register.GAPS), set(register._GAP_SQL))

    def test_the_pack_and_the_connector_agree_on_the_id(self):
        from alaiy_os_connector_shopify.connector_meta import connector_meta

        self.assertEqual(pack_meta.CONNECTOR_ID, connector_meta["connector_id"])

    def _tool(self, tool_id):
        return next(t for t in pack_meta.TOOLS if t["tool_id"] == tool_id)


class TestCsvRowShapes(unittest.TestCase):
    """csv_export._rows_from against this pack's real envelope shapes."""

    def test_a_paged_envelope_yields_its_rows(self):
        payload = {
            "total": 2,
            "page_no": 1,
            "page_size": 20,
            "has_more": False,
            "listings": [{"item_code": "A"}, {"item_code": "B"}],
        }
        self.assertEqual(csv_export._rows_from(payload), payload["listings"])

    def test_a_sales_summary_yields_its_buckets(self):
        payload = {
            "period": {"date_from": "2026-01-01"},
            "currency": "INR",
            "totals": {"product_sales": 10},
            "coverage": {"note": "..."},
            "buckets": [{"period_start": "2026-01-01"}, {"period_start": "2026-01-02"}],
        }
        self.assertEqual(csv_export._rows_from(payload), payload["buckets"])

    def test_an_order_page_yields_its_orders(self):
        payload = {
            "total": 1,
            "page_no": 1,
            "page_size": 20,
            "has_more": False,
            "orders": [{"shopify_order_name": "#1015"}],
        }
        self.assertEqual(csv_export._rows_from(payload), payload["orders"])

    def test_a_listing_record_stays_one_row(self):
        """get_listing is a record with nested lists, not a wrapper around them.

        Load-bearing: it survives as one row only because it carries more than
        `_ENVELOPE_METADATA_KEYS` scalar fields of its own. Exporting it must
        give one product, not three variant rows.
        """
        payload = {
            "item_code": "SHIRT",
            "item_name": "Shirt",
            "is_enabled": True,
            "status": "Active",
            "product_id": "123",
            "handle": "shirt",
            "pushed": True,
            "title": "Shirt",
            "description": "<p>A shirt</p>",
            "product_type": "Apparel",
            "category": "",
            "seo_title": "Shirt",
            "seo_description": "A shirt",
            "has_variants": True,
            "last_synced_at": "2026-09-01 10:00:00",
            "images": ["/files/a.png", "/files/b.png"],
            "variants": [{"item_code": "SHIRT-S"}, {"item_code": "SHIRT-M"}],
            "metafields": [{"namespace": "custom", "key": "fit"}],
        }
        rows = csv_export._rows_from(payload)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["item_code"], "SHIRT")

    def test_a_period_comparison_stays_one_row(self):
        payload = {
            "current": {"product_sales": 10},
            "baseline": {"product_sales": 5},
            "currency": "INR",
            "change": {"product_sales": {"percent": 100.0}},
            "coverage": {"note": "..."},
        }
        self.assertEqual(len(csv_export._rows_from(payload)), 1)

    def test_a_bare_array_passes_through(self):
        rows = [{"a": 1}, {"a": 2}]
        self.assertEqual(csv_export._rows_from(rows), rows)

    def test_scalars_become_one_named_column(self):
        self.assertEqual(csv_export._rows_from(["x", "y"]), [{"value": "x"}, {"value": "y"}])

    def test_the_envelope_threshold_is_wider_than_every_envelope_here(self):
        """Four is the widest wrapper this pack produces; the cap is five.

        Written as an assertion rather than a comment because raising an
        envelope to five non-list keys breaks the export silently -- it starts
        writing the summary line instead of the series.
        """
        self.assertGreater(csv_export._ENVELOPE_METADATA_KEYS, 4)


class TestCsvCells(unittest.TestCase):
    def test_text_starting_with_a_formula_character_is_guarded(self):
        for text in ("=SUM(A1)", "+1", "@ref", "-cmd"):
            self.assertTrue(csv_export._cell(text).startswith("'"))

    def test_a_negative_number_is_not_guarded(self):
        self.assertEqual(csv_export._cell(-5), -5)
        self.assertEqual(csv_export._cell(-5.5), -5.5)

    def test_none_becomes_empty(self):
        self.assertEqual(csv_export._cell(None), "")

    def test_booleans_are_words(self):
        self.assertEqual(csv_export._cell(True), "true")
        self.assertEqual(csv_export._cell(False), "false")

    def test_nested_values_become_compact_json(self):
        self.assertEqual(csv_export._cell({"b": 1, "a": 2}), '{"b":1,"a":2}')

    def test_a_long_cell_is_truncated(self):
        out = csv_export._cell("x" * (csv_export.MAX_CELL_CHARS + 50))
        self.assertLessEqual(len(out), csv_export.MAX_CELL_CHARS + 1)
        self.assertTrue(out.endswith("…"))

    def test_header_honours_a_requested_order(self):
        rows = [{"b": 1, "a": 2}]
        self.assertEqual(csv_export._header(rows, "a, b"), ["a", "b"])

    def test_header_defaults_to_first_seen_order(self):
        self.assertEqual(csv_export._header([{"b": 1}, {"a": 2}], ""), ["b", "a"])

    def test_an_unreadable_payload_comes_back_as_a_result_not_a_throw(self):
        self.assertFalse(csv_export.export_csv("not json")["saved"])
        self.assertFalse(csv_export.export_csv("")["saved"])
        self.assertFalse(csv_export.export_csv("[]")["saved"])


class TestSalesArithmetic(unittest.TestCase):
    """The period maths, with no database anywhere near it."""

    def test_one_of_names_the_real_values(self):
        import frappe

        with self.assertRaises(frappe.ValidationError) as caught:
            sales._one_of("weekly", sales.GRANULARITIES, "granularity", default="day")
        self.assertIn("day", str(caught.exception))

    def test_one_of_falls_through_to_a_default_only_when_blank(self):
        self.assertEqual(sales._one_of(None, sales.GRANULARITIES, "g", default="day"), "day")
        self.assertEqual(sales._one_of("", sales.GRANULARITIES, "g", default="day"), "day")

    def test_period_defaults_the_end_to_today(self):
        from frappe.utils import getdate, nowdate

        start, end = sales._period("2026-01-01")
        self.assertEqual(start, getdate("2026-01-01"))
        self.assertEqual(end, getdate(nowdate()))

    def test_period_refuses_reversed_dates_naming_the_argument(self):
        import frappe

        with self.assertRaises(frappe.ValidationError) as caught:
            sales._period("2026-03-01", "2026-01-01", label="baseline_from")
        self.assertIn("baseline_from", str(caught.exception))

    def test_too_many_buckets_is_refused_naming_a_coarser_granularity(self):
        import frappe
        from frappe.utils import getdate

        with self.assertRaises(frappe.ValidationError) as caught:
            sales._assert_bucket_count(getdate("2020-01-01"), getdate("2026-01-01"), "day")
        self.assertIn("week", str(caught.exception))

    def test_total_granularity_is_never_refused(self):
        from frappe.utils import getdate

        sales._assert_bucket_count(getdate("1990-01-01"), getdate("2026-01-01"), "total")

    def test_a_month_bucket_is_clamped_to_the_period(self):
        from frappe.utils import getdate

        start, end = sales._bucket_bounds(
            "2026-08-01", "month", getdate("2026-08-15"), getdate("2026-08-20")
        )
        self.assertEqual((str(start), str(end)), ("2026-08-15", "2026-08-20"))

    def test_previous_period_is_the_same_length_immediately_before(self):
        from frappe.utils import getdate

        base_from, base_to = sales._baseline_period(
            getdate("2026-03-01"), getdate("2026-03-30"), "previous_period"
        )
        self.assertEqual(str(base_to), "2026-02-28")
        self.assertEqual((base_to - base_from).days, 29)

    def test_previous_year_shifts_365_days(self):
        from frappe.utils import getdate

        base_from, base_to = sales._baseline_period(
            getdate("2026-03-01"), getdate("2026-03-30"), "previous_year"
        )
        self.assertEqual(str(base_from), "2025-03-01")

    def test_growth_from_zero_has_no_percentage(self):
        change = sales._change({"product_sales": 500}, {"product_sales": 0})
        self.assertIsNone(change["product_sales"]["percent"])
        self.assertEqual(change["product_sales"]["absolute"], 500.0)

    def test_average_order_value_comes_from_the_summed_totals(self):
        """An average of averages is not one."""
        buckets = [
            {"product_sales": 100.0, "order_total": 100.0, "units": 1, "order_count": 1},
            {"product_sales": 300.0, "order_total": 300.0, "units": 3, "order_count": 3},
        ]
        totals = sales._totals_from(buckets)
        self.assertEqual(totals["product_sales"], 400.0)
        self.assertEqual(totals["order_count"], 4)
        self.assertEqual(totals["avg_order_value"], 100.0)

    def test_units_are_folded_onto_the_money_buckets(self):
        merged = sales._merge_units(
            [{"bucket": "2026-01-01", "product_sales": 10}],
            [{"bucket": "2026-01-01", "units": 3}],
        )
        self.assertEqual(merged[0]["units"], 3)

    def test_units_with_no_money_bucket_are_carried_not_dropped(self):
        merged = sales._merge_units([], [{"bucket": "2026-01-02", "units": 5}])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["units"], 5)

    def test_the_paid_only_caveat_is_on_every_coverage_note(self):
        """Unlike the date-window clause, this one is true of every period."""
        from frappe.utils import getdate

        cov = {"first_order_date": "2026-01-01", "last_order_date": "2026-12-31", "synced_orders": 5}
        inside = sales._coverage_note(cov, getdate("2026-06-01"), getdate("2026-06-30"))
        outside = sales._coverage_note(cov, getdate("2020-01-01"), getdate("2020-02-01"))
        empty = sales._coverage_note(
            {"first_order_date": None, "last_order_date": None, "synced_orders": 0},
            getdate("2026-06-01"),
            getdate("2026-06-30"),
        )
        for note in (inside, outside, empty):
            self.assertIn("paid", note)
        self.assertIn("outside the synced order data", outside)
