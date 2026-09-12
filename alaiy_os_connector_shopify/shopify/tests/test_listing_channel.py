"""Tests for the adopted listing channel: the adapter, and the rules validator.

Run via `bench run-tests` alongside the rest of this directory.

The validator is the interesting half. `prompts/listing.md` states Shopify's
rules as prose and `validate.py` states them again as code, and the whole point
of the second copy is that it catches what the first one only asks for. These
tests pin both directions: a compliant listing must pass untouched (a validator
with false positives would block every run), and each rule must actually fire.
"""

import contextlib
import json
import unittest

import frappe

from alaiy_os_connector_shopify.listing import channel, handlers, matrix
from alaiy_os_connector_shopify.listing.validate import (
    SEO_DESCRIPTION_MAX,
    SEO_TITLE_MAX,
    validate,
)


@contextlib.contextmanager
def _matrix(spec):
    """Run the block as if a client app had provided this attribute matrix.

    The cache `matrix.load()` reads is set directly rather than the hook being
    stubbed: what these tests are about is how the rest of the channel behaves
    once a guideline exists, and going through `frappe.get_hooks` would need a
    provider module registered under an installed app to say nothing more.
    """
    previous = getattr(frappe.local, "_listing_attribute_matrix", None)
    frappe.local._listing_attribute_matrix = spec
    try:
        yield
    finally:
        frappe.local._listing_attribute_matrix = previous


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


class TestPublishedMetafieldsReachTheModel(unittest.TestCase):
    """`get_product` must show the model what the store already says.

    Before it did, the agent enriched every product as if it were blank: it
    re-derived values the store held and wrote "Not provided in source data" for
    attributes that were live on the product. These pin the reading, not the
    prompt — a value shown with its JSON brackets still on reaches a shopper's
    screen, and an empty list metafield read as truthy tells the model a product
    "has" a style whose value is the two characters `[]`.
    """

    def test_a_list_metafield_is_unwrapped(self):
        self.assertEqual(handlers.metafield_text('["Black"]'), "Black")

    def test_the_empty_shapes_are_not_values(self):
        for empty in ("[]", "{}", "", "null", "  "):
            self.assertIsNone(handlers.metafield_text(empty), empty)

    def test_a_long_value_is_cut_not_dropped(self):
        text = handlers.metafield_text("x" * (handlers.MAX_METAFIELD_CHARS + 50))
        self.assertEqual(len(text), handlers.MAX_METAFIELD_CHARS + 1)
        self.assertTrue(text.endswith("…"))

    def test_namespaces_stay_apart(self):
        """A key is only unique within a namespace — `custom.style` and
        `uploadify_product.style` are two different facts."""
        listing = {"metafields": [
            {"namespace": "custom", "key": "style", "value": "Dress/Formal"},
            {"namespace": "uploadify_product", "key": "style", "value": "[]"},
            {"namespace": "uploadify_product", "key": "papers", "value": "Yes"},
        ]}
        self.assertEqual(
            handlers.listing_metafields(listing),
            {"custom": {"style": "Dress/Formal"}, "uploadify_product": {"papers": "Yes"}},
        )

    def test_published_attributes_is_the_namespace_approval_overwrites(self):
        listing = {"metafields": [
            {"namespace": handlers.ATTRIBUTE_NAMESPACE, "key": "material", "value": "18K Rose Gold"},
            {"namespace": "other", "key": "material", "value": "Brass"},
        ]}
        self.assertEqual(handlers.published_attributes(listing), {"material": "18K Rose Gold"})


class TestNothingTheModelSendsFailsTheSave(unittest.TestCase):
    """One rejected field must not cost the listing.

    A `confidence` of "high, because the photos agree" used to fail the save; the
    model rebuilt the payload from scratch and its retry dropped six of the nine
    attributes it had already got right. So both clamps read the DocType's own
    meta — never a duplicated literal — and report what they corrected.
    """

    def test_a_qualified_enum_keeps_its_leading_token(self):
        value, rejected = handlers._select_value(
            channel.ENRICHED_DOCTYPE, "confidence", "high, because the photos agree"
        )
        self.assertEqual(value, "high")
        self.assertEqual(rejected, "high, because the photos agree")

    def test_a_clean_enum_is_not_reported(self):
        self.assertEqual(
            handlers._select_value(channel.ENRICHED_DOCTYPE, "confidence", "high"),
            ("high", None),
        )

    def test_an_unrecognisable_enum_is_dropped_and_reported(self):
        value, rejected = handlers._select_value(
            channel.ENRICHED_DOCTYPE, "confidence", "reasonably sure"
        )
        self.assertIsNone(value)
        self.assertEqual(rejected, "reasonably sure")

    def test_an_overlong_title_is_cut_and_its_real_length_reported(self):
        """140 is Data's own default, which is what applies here: the DocType
        declares no explicit length on `title`, so `_clamp_data`'s fallback is
        the cap that actually bites. Pinned rather than read back from the meta,
        so raising the fallback without meaning to fails here."""
        self.assertFalse(frappe.get_meta(channel.ENRICHED_DOCTYPE).get_field("title").length)

        value, was = handlers._clamp_data(channel.ENRICHED_DOCTYPE, "title", "x" * 150)
        self.assertEqual(len(value), 140)
        self.assertEqual(was, 150)

    def test_a_title_that_fits_is_not_reported(self):
        self.assertEqual(
            handlers._clamp_data(channel.ENRICHED_DOCTYPE, "title", "A short title"),
            ("A short title", None),
        )


class TestAPlaceholderIsNotAValue(unittest.TestCase):
    """"Not provided in source data" is a note about the absence of a fact.

    Left in the attributes table it counts as filled, hides the gap from the
    completeness check, and — because the metafield sync only skips falsy values
    — publishes to the live storefront on approval.
    """

    def test_the_notes_about_absence(self):
        for value in ("Not provided in source data", "TBD", "unknown",
                      "To be determined upon manual review", "N/A", "Not applicable"):
            self.assertTrue(matrix.is_placeholder(value), value)

    def test_real_answers_survive(self):
        for value in ("18K Rose Gold", "36.0 mm", "Small Second", "No", "Yes"):
            self.assertFalse(matrix.is_placeholder(value), value)

    def test_no_length_heuristic(self):
        """`features` and `complications` are legitimately long, so "it reads
        like a sentence" would blank real answers."""
        long_answer = (
            "Manual-wind movement with small seconds at six, blued steel hands and "
            "a snap-on case back finished with Geneva stripes"
        )
        self.assertFalse(matrix.is_placeholder(long_answer))


class TestTheSellersRulesAreTheSellers(unittest.TestCase):
    """The matrix half, with no client app installed — which is every bench today.

    All of it has to degrade to "no matrix" rather than to an empty rule set that
    silently enforces nothing, and the two generic helpers have to work either
    way because they are text handling, not policy.
    """

    def test_no_provider_means_no_matrix(self):
        self.assertIsNone(matrix.load())
        self.assertEqual(matrix.profiles(), [])
        self.assertIsNone(matrix.category_field())
        self.assertEqual(matrix.mandatory("Watches"), [])

    def test_no_opinion_is_not_an_empty_allow_list(self):
        """None and empty mean opposite things: None allows anything, a set is
        closed. Confusing them drops every good value."""
        self.assertIsNone(matrix.applicable("Watches"))

    def test_the_channel_spec_gains_no_field_it_has_no_values_for(self):
        fields = channel.channel()["spec"]["fields"]
        self.assertNotIn("watch_category", fields["properties"])
        self.assertEqual(
            sorted(fields["required"]),
            sorted(json.loads(
                (channel._DIR / "fields.json").read_text(encoding="utf-8"))["required"]),
        )

    def test_the_same_value_in_different_clothes(self):
        self.assertTrue(matrix.same_value("18K rose gold", "18K Rose Gold"))
        self.assertTrue(matrix.same_value("Small seconds", "Small Seconds"))

    def test_word_order_and_numeric_punctuation_are_not_normalised(self):
        """A reviewer may well prefer one wording, and "1.68 ct" is not "168 ct"."""
        self.assertFalse(matrix.same_value("Leather, Black", "Black leather"))
        self.assertFalse(matrix.same_value("1.68 ct", "168 ct"))

    def test_only_the_longest_label_on_a_line_matches(self):
        """A plain substring test makes "Dial Color (not visible)" look like the
        `color` attribute too, and then `Color` is reported as covered."""
        labels = {"color": "Color", "dial_color": "Dial Color",
                  "size": "Size", "case_size": "Case Size"}
        with _matrix({"field_labels": labels}):
            self.assertEqual(matrix.match_keys(["Dial Color (not visible)"]), ["dial_color"])
            self.assertEqual(matrix.match_keys(["Case Size (see Dimensions)"]), ["case_size"])

    def test_a_provided_matrix_puts_the_clients_field_in_front_of_the_model(self):
        spec = {
            "category_field": "watch_category",
            "category_field_label": "Watch Category",
            "field_labels": {"material": "Material"},
            "profiles": {"Watches": {"mandatory": ["material"], "optional": []}},
        }
        with _matrix(spec):
            fields = channel.channel()["spec"]["fields"]
            self.assertIn("watch_category", fields["properties"])
            self.assertIn("watch_category", fields["required"])
            self.assertEqual(fields["properties"]["watch_category"]["enum"], ["Watches"])
            # The one confusion worth spelling out: this is not `category`.
            self.assertIn("NOT", fields["properties"]["watch_category"]["description"])
