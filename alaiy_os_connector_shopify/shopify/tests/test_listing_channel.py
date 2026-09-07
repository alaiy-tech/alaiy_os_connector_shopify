"""Tests for the adopted listing channel: the adapter, and the rules validator.

Run via `bench run-tests` alongside the rest of this directory.

The validator is the interesting half. `prompts/listing.md` states Shopify's
rules as prose and `validate.py` states them again as code, and the whole point
of the second copy is that it catches what the first one only asks for. These
tests pin both directions: a compliant listing must pass untouched (a validator
with false positives would block every run), and each rule must actually fire.
"""

import unittest

from alaiy_os_connector_shopify.listing import channel
from alaiy_os_connector_shopify.listing.validate import (
    SEO_DESCRIPTION_MAX,
    SEO_TITLE_MAX,
    validate,
)


def _good_listing(**overrides):
    listing = {
        "title": "Stainless Steel Insulated Water Bottle, 750 ml",
        "description": (
            "This insulated bottle keeps drinks cold for 24 hours and hot for 12. "
            "The double-walled stainless steel body resists dents and will not sweat.\n\n"
            "A wide mouth takes ice cubes and a bottle brush. The lid seals against "
            "leaks in a bag, and the powder-coated finish keeps its grip when wet."
        ),
        "category": "Home & Garden > Kitchen & Dining > Drinkware",
        "product_type": "Water Bottle",
        "seo_title": "Insulated Steel Water Bottle 750ml",
        "seo_description": "Double-walled stainless steel bottle, 750 ml. Cold 24 hours, hot 12.",
        "shopify_tags": ["drinkware", "stainless steel", "insulated"],
        "attributes": {"material": "Stainless steel", "weight": "380 g", "dimensions": "26 x 7 cm"},
        "images": [{"source_url": "/files/bottle.png", "item_variant": None, "url": None}],
        "variants": [],
        "needs_review": [],
        "confidence": "high",
    }
    listing.update(overrides)
    return listing


class TestChannelAdapter(unittest.TestCase):
    def test_the_adapter_declares_the_contract(self):
        spec = channel.channel()
        self.assertEqual(spec["channel"], "shopify")
        self.assertEqual(spec["source_doctype"], "Shopify Product Listing")
        self.assertEqual(spec["enriched_doctype"], "Shopify Enriched Listing")
        self.assertTrue(spec["spec"]["rules"])
        self.assertEqual(spec["spec"]["fields"]["type"], "object")

    def test_every_handler_resolves(self):
        import frappe

        for name, path in channel.channel()["handlers"].items():
            self.assertTrue(callable(frappe.get_attr(path)), f"{name} -> {path}")

    def test_shopify_declares_an_image_step(self):
        """The first channel to do so -- Amazon's producing side never moved.

        Declaring the handler is the whole signal; there is no `has_image_step`
        key on either side, so an extra one here would be a shape the consumer
        does not know about.
        """
        spec = channel.channel()
        self.assertIn("prepare_images", spec["handlers"])
        self.assertNotIn("has_image_step", spec)

    def test_the_adapter_satisfies_the_hosts_own_check(self):
        """Run `alaiy_os_agents`'s loader against this adapter, not a copy of it.

        `channels._check` is what refuses a malformed adapter at load, and it is
        the only authority on what the contract requires. Skipped where the host
        app is not installed.
        """
        try:
            from alaiy_os_agents.agents.listing import channels
        except ImportError:
            self.skipTest("alaiy_os_agents is not installed or cannot import")
        channels._check("alaiy_os_connector_shopify.listing.channel.channel", channel.channel())

    def test_handlers_accept_the_keywords_the_host_calls_them_with(self):
        """Every handler is called with keywords fixed by the contract.

        `agents/listing/tools.py` calls `prepare_images` as
        `fn(product=, enabled=, image_urls=)` and `save_listing` as
        `fn(product=, listing=)`. A wrapper whose parameter names follow this
        app's own vocabulary instead would TypeError mid-run, which is exactly
        what this catches -- `prepare_images` did, before it was fixed.
        """
        import importlib
        import inspect

        expected = {
            "get_product": {"product"},
            "get_reference_values": set(),
            "save_listing": {"product", "listing"},
            "validate": {"listing"},
            "prepare_images": {"product", "enabled", "image_urls"},
            "register": {"product"},
            "health": {"product"},
        }
        for name, path in channel.channel()["handlers"].items():
            module, _, function = path.rpartition(".")
            accepted = set(
                inspect.signature(getattr(importlib.import_module(module), function)).parameters
            )
            self.assertEqual(
                expected[name] - accepted, set(), f"{name} cannot accept the host's keywords"
            )

    def test_save_listing_does_not_validate_twice(self):
        """The host validates before it ever reaches the adapter.

        `agents/listing/tools.py:save_listing` runs the adapter's `validate` and
        throws on defects without calling `save_listing` at all. Doing it here as
        well would report the same defects from two places -- and the Amazon
        adapter, which is the reference, is a bare passthrough.
        """
        import inspect

        source = inspect.getsource(channel.save_listing)
        self.assertNotIn("validate", source.split('"""')[-1])

    def test_the_adapter_matches_the_amazon_connectors_shape(self):
        """Same contract, different channel -- the top-level keys must agree.

        The consumer is written against one shape. Skipped where the Amazon
        connector is not installed.
        """
        try:
            from alaiy_os_connector_amazon_sp_api.listing import channel as amazon
        except ImportError:
            self.skipTest("the Amazon connector is not on this bench")
        self.assertEqual(sorted(channel.channel()), sorted(amazon.channel()))

    def test_no_health_handler(self):
        """Shopify reports no listing issues, so it cannot answer `health`."""
        self.assertNotIn("health", channel.channel()["handlers"])

    def test_this_app_registers_no_listing_agent(self):
        """One listing agent per site, and `alaiy_os_agents` owns it.

        The retired standalone app registered `shopify_listing` and shipped its
        own run page and Enrich buttons. Re-registering that alongside the
        channel-agnostic `listing` agent would put two listing agents on one
        bench, which is what the migration existed to remove -- so this app
        provides the adapter and nothing else. The Amazon connector is the
        reference, and it registers none either.
        """
        from alaiy_os_connector_shopify import pack_meta
        from alaiy_os_connector_shopify.setup import install

        # The only agent row this app writes is the read-only pack.
        self.assertEqual(pack_meta.PACK_ID, "shopify")
        for name in ("sync_listing_agent", "unregister_listing_agent", "sync_agent_sidebar"):
            self.assertFalse(
                hasattr(install, name),
                f"{name} is back -- this app should register no listing agent",
            )

    def test_the_retired_agents_modules_are_gone(self):
        """agent_meta and bulk belonged to the standalone agent, not the channel."""
        for module in (
            "alaiy_os_connector_shopify.listing.agent_meta",
            "alaiy_os_connector_shopify.listing.bulk",
            "alaiy_os_connector_shopify.api.listing",
        ):
            with self.assertRaises(ImportError):
                __import__(module)


class TestValidatorAcceptsGoodWork(unittest.TestCase):
    def test_a_compliant_listing_passes(self):
        self.assertEqual(validate(_good_listing()), [])

    def test_ampersands_and_comparisons_are_not_html(self):
        """A validator that rejects '&' or '< 5 kg' would block honest copy."""
        listing = _good_listing(
            description=(
                "Rated for loads under 5 kg and built for speed & durability.\n\n"
                "The 2 m USB-C to HDMI lead is rated < 60 W, which suits any laptop."
            )
        )
        self.assertEqual(validate(listing), [])

    def test_acronyms_are_not_shouting(self):
        self.assertEqual(validate(_good_listing(title="USB-C to HDMI Cable, 2 m")), [])

    def test_a_hyphenated_word_is_not_markdown(self):
        listing = _good_listing(
            description=(
                "A powder-coated, double-walled bottle for everyday carry.\n\n"
                "Dishwasher-safe and built to last a decade of use."
            )
        )
        self.assertEqual(validate(listing), [])


class TestValidatorCatchesRealDefects(unittest.TestCase):
    def _defects(self, **overrides):
        return " ".join(validate(_good_listing(**overrides)))

    def test_seo_title_over_the_snippet_limit(self):
        self.assertIn("seo_title", self._defects(seo_title="x" * (SEO_TITLE_MAX + 1)))

    def test_seo_description_over_shopifys_limit(self):
        self.assertIn(
            "seo_description", self._defects(seo_description="x" * (SEO_DESCRIPTION_MAX + 1))
        )

    def test_seo_copy_that_just_repeats_the_page_copy(self):
        good = _good_listing()
        self.assertIn("identical to title", self._defects(seo_title=good["title"]))
        self.assertIn("repeats the description", self._defects(seo_description=good["description"]))

    def test_html_and_markdown_in_the_description(self):
        self.assertIn("HTML", self._defects(description="<p>One</p>\n\n<p>Two</p>"))
        self.assertIn("markdown", self._defects(description="Intro line here.\n\n* one\n* two"))

    def test_a_single_paragraph_description(self):
        self.assertIn("paragraph", self._defects(description="Just the one paragraph, alone."))

    def test_promotional_filler(self):
        self.assertIn("banned promotional phrase", self._defects(title="Bottle HOT SALE today"))

    def test_shouting(self):
        self.assertIn("shouting", self._defects(title="BOTTLES FOR EVERYONE"))

    def test_a_measurement_with_no_unit(self):
        listing = _good_listing(attributes={"weight": "380", "dimensions": "26 x 7 cm"})
        self.assertIn("no unit", " ".join(validate(listing)))

    def test_duplicate_and_empty_tags(self):
        defects = self._defects(shopify_tags=["Bottle", "bottle", ""])
        self.assertIn("empty tag", defects)
        self.assertIn("repeats", defects)

    def test_a_price_in_a_variant_suggestion(self):
        listing = _good_listing(
            variants=[{"item_variant": "V1", "suggestions": ["should really be $19.99"]}]
        )
        self.assertIn("price", " ".join(validate(listing)))

    def test_an_image_with_no_source_url(self):
        self.assertIn("source_url", self._defects(images=[{"item_variant": None, "url": None}]))

    def test_empty_required_copy(self):
        self.assertIn("category", self._defects(category=""))
        self.assertIn("product_type", self._defects(product_type=""))
