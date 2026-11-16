# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""A simple product's first photo goes to Shopify once.

A simple product's only Listing Variant row was seeded with Item.image, which is
the gallery's first photo under another file name. Every push sent it as the
variant's photo as well, so Shopify gained a second copy of the first photo, and
the inbound sync added that copy to the gallery. Deleting it from the gallery did
not help: the variant row still named it, and the next edited save sent it again.
"""

from contextlib import ExitStack
from unittest.mock import patch

import frappe
from frappe.tests import UnitTestCase

from alaiy_os_connector_shopify.shopify.product import canonical
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver

FIRST = "https://cdn.shopify.com/s/files/1/0/files/front.jpg"
SECOND = "https://cdn.shopify.com/s/files/1/0/files/side.jpg"
# The first photo again, as Item.image stored it: same picture, other file name.
FIRST_AGAIN = "https://cdn.shopify.com/s/files/1/0/files/front3a9c1e.jpg"
RED = "https://cdn.shopify.com/s/files/1/0/files/red.jpg"


def _variant(code):
	return frappe._dict(item_code=code, attributes=[])


class TestPushPayload(UnitTestCase):
	def build(self, item, variants, gallery, variant_images):
		listing = frappe._dict(sh_shopify_status="Active")
		with ExitStack() as stack:
			for name, value in {
				"effective_title": "A product",
				"effective_description": "",
				"effective_product_type": "",
				"effective_category": None,
				"effective_seo": {"title": "", "description": ""},
				"effective_images": gallery,
			}.items():
				stack.enter_context(patch.object(listing_resolver, name, return_value=value))
			stack.enter_context(patch.object(
				listing_resolver, "effective_variant_image",
				side_effect=lambda _listing, code: variant_images.get(code),
			))
			stack.enter_context(patch.object(
				canonical, "_variant_set_payload",
				side_effect=lambda v, *a, **k: (
					{"sku": v.item_code, "file": {"originalSource": variant_images[v.item_code], "contentType": "IMAGE"}}
					if variant_images.get(v.item_code) else {"sku": v.item_code}
				),
			))
			stack.enter_context(patch.object(canonical, "_item_tags", return_value=set()))
			stack.enter_context(patch("alaiy_os.image_store.presigned_url", side_effect=lambda u: u))
			return canonical._product_set_input(item, variants, None, listing)

	def test_a_simple_product_sends_only_its_gallery(self):
		item = frappe._dict(name="SKU-1", has_variants=0, brand=None)
		payload = self.build(item, [_variant("SKU-1")], [FIRST, SECOND], {"SKU-1": FIRST_AGAIN})
		self.assertEqual([f["originalSource"] for f in payload["files"]], [FIRST, SECOND])
		self.assertNotIn("file", payload["variants"][0])

	def test_a_simple_product_with_no_gallery_sends_no_variant_photo(self):
		item = frappe._dict(name="SKU-1", has_variants=0, brand=None)
		payload = self.build(item, [_variant("SKU-1")], [], {"SKU-1": FIRST_AGAIN})
		self.assertNotIn("files", payload)
		self.assertNotIn("file", payload["variants"][0])

	def test_real_variants_keep_their_own_photos(self):
		item = frappe._dict(name="TPL", has_variants=1, brand=None)
		payload = self.build(item, [_variant("TPL-RED"), _variant("TPL-BLUE")], [FIRST], {"TPL-RED": RED})
		self.assertEqual([f["originalSource"] for f in payload["files"]], [FIRST, RED])
		self.assertEqual(payload["variants"][0]["file"]["originalSource"], RED)
		self.assertNotIn("file", payload["variants"][1])
