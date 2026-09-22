"""
The name extraction behind the deprecation sweep.

Only the offline half is testable here -- introspection needs a live store.
What matters is that _selected_names doesn't mistake an argument VALUE for a
selected field, because that is what would produce phantom findings and get
the whole report ignored.
"""

import unittest

from alaiy_os_connector_shopify.shopify.deprecation_audit import _selected_names


class TestSelectedNames(unittest.TestCase):
    def test_finds_plain_selected_fields(self):
        names = _selected_names("query { product { id title handle } }")
        self.assertIn("title", names)
        self.assertIn("handle", names)

    def test_argument_values_are_not_selected_fields(self):
        # quantities(names: ["available"]) selects "quantities", not
        # "available" -- counting the argument value would report a field
        # nobody selected.
        names = _selected_names('{ quantities(names: ["available"]) { quantity } }')
        self.assertIn("quantities", names)
        self.assertIn("quantity", names)
        self.assertNotIn("available", names)

    def test_pagination_arguments_are_stripped(self):
        names = _selected_names("{ media(first: 25) { nodes { id } } }")
        self.assertIn("media", names)
        self.assertIn("nodes", names)
        self.assertNotIn("first", names)

    def test_catches_the_real_deprecated_fields_this_was_written_for(self):
        # The four that were live in this connector undetected.
        for field, text in [
            ("images", "{ product { images(first: 10) { nodes { src } } } }"),
            ("featuredImage", "{ product { featuredImage { url } } }"),
            ("image", "{ variants { nodes { image { id } } } }"),
            ("email", "{ customer { email } }"),
        ]:
            self.assertIn(field, _selected_names(text), field)

    def test_a_field_named_only_in_a_comment_is_not_a_finding(self):
        # The fix for a deprecated field usually leaves a comment explaining
        # why -- which would otherwise report the field as still selected.
        names = _selected_names(
            "{ product {\n"
            "  # Product.images is deprecated, superseded by media\n"
            "  media { nodes { id } }\n"
            "} }")
        self.assertIn("media", names)
        self.assertNotIn("images", names)
        self.assertNotIn("deprecated", names)

    def test_replacement_fields_do_not_trip_the_old_names(self):
        # featuredMedia must not read as featuredImage, or the fix looks
        # like it never landed.
        names = _selected_names("{ product { featuredMedia { preview { image { url } } } } }")
        self.assertIn("featuredMedia", names)
        self.assertNotIn("featuredImage", names)
        self.assertNotIn("images", names)


if __name__ == "__main__":
    unittest.main()
