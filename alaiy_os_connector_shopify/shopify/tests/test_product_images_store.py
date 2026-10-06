# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""Produced images go through the site's image store, and reach Shopify as links it can fetch.

Shopify downloads every `originalSource` itself, so a produced image in the site's
private S3 bucket has to go out signed. Two things must not happen while it does: the
product's fingerprint must not change because of a signature, or every product would
re-push forever, and a variant's `file` must still name exactly one of the product's
`files`, or Shopify drops the variant's image.

The store itself is tested in `alaiy_os`; here it is replaced by stand-ins.
"""

from unittest.mock import patch

from frappe.tests import UnitTestCase

from alaiy_os_connector_shopify.listing import handlers, images
from alaiy_os_connector_shopify.shopify.product import canonical

STORED = "https://bucket.s3.ap-south-1.amazonaws.com/images/generated/2026/10/listing-enhanced-x.png"
SUPPLIER = "https://cdn.supplier.example/a.jpg"


def _sign(url):
	return f"{url}?X-Amz-Signature=fake" if url.startswith("https://bucket.") else url


class TestPayloadFiles(UnitTestCase):
	def payload(self, variant_files):
		return {"variants": [{"file": {"originalSource": url, "contentType": "IMAGE"}} if url else {} for url in variant_files]}

	def test_stored_images_go_out_signed_and_variants_still_match(self):
		payload = self.payload([STORED, SUPPLIER])
		with patch("alaiy_os.image_store.presigned_url", side_effect=_sign) as presign:
			canonical._set_files(payload, [STORED, SUPPLIER])
		files = [f["originalSource"] for f in payload["files"]]
		self.assertEqual(files, [_sign(STORED), SUPPLIER])
		variant_sources = [v["file"]["originalSource"] for v in payload["variants"]]
		self.assertEqual(variant_sources, files)
		# Once per URL: two signatures for one image would stop the variant matching.
		self.assertEqual(presign.call_count, 2)

	def test_a_variant_image_the_product_does_not_list_is_dropped_before_signing(self):
		payload = self.payload(["https://elsewhere.example/b.jpg"])
		with patch("alaiy_os.image_store.presigned_url", side_effect=_sign):
			canonical._set_files(payload, [STORED])
		self.assertNotIn("file", payload["variants"][0])

	def test_the_urls_given_are_left_unsigned(self):
		"""They are what the fingerprint is built from."""
		images_ = [STORED]
		with patch("alaiy_os.image_store.presigned_url", side_effect=_sign):
			canonical._set_files(self.payload([]), images_)
		self.assertEqual(images_, [STORED])


class TestSavingAProducedImage(UnitTestCase):
	def test_translated_and_generated_photos_are_filed_apart(self):
		with patch("alaiy_os.image_store.save", return_value=STORED) as save:
			self.assertEqual(images.save_public_image("listing-prepared", b"jpg", "image/jpeg"), STORED)
			images.save_public_image("listing-enhanced", b"png", "image/png")
		prepared, enhanced = save.call_args_list
		self.assertEqual(prepared.kwargs["category"], "translated")
		self.assertEqual(enhanced.kwargs["category"], "generated")
		self.assertTrue(prepared.args[0].startswith("listing-prepared-"))


class TestReadingForTheModel(UnitTestCase):
	def test_a_stored_image_is_read_with_the_sites_own_access(self):
		with patch("alaiy_os.image_store.is_stored_url", return_value=True), \
				patch("alaiy_os.image_store.read", return_value=(b"\x89PNG", "image/png")), \
				patch.object(images, "fetch_image_block") as fetched:
			block = images.image_block_from_url(STORED)
		fetched.assert_not_called()
		self.assertEqual(block["source"]["media_type"], "image/png")

	def test_view_image_reads_a_stored_image_rather_than_downloading_it(self):
		with patch.object(images, "image_block_from_url", return_value={"type": "image"}) as read, \
				patch.object(images, "fetch_image_block") as fetched:
			result = handlers.view_image(STORED)
		read.assert_called_once_with(STORED)
		fetched.assert_not_called()
		self.assertEqual(result["_content_blocks"][1], {"type": "image"})
