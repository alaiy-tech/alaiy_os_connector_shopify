"""A supplier photo larger than the house size, and a photo whose result cannot be saved.

The kept cutout is held to the same `max_size` as the finished image, so a very
large supplier shot does not produce a file past the site's upload limit. When a
save does fail anyway, only that photo fails: the other photos of the product
still get their results.

Run via `bench run-tests`; nothing here needs a site.
"""

import base64
import io
import unittest
from unittest import mock

from PIL import Image, ImageDraw

from alaiy_os_connector_shopify.listing import image_generation, image_style

GROUND = (244, 244, 244)
PIECE = (120, 120, 125)
LINE = (60, 60, 64)

STYLE = dict(
	image_style.DEFAULTS,
	background="#f4f4f4",
	matte="flood",
	keep_cutout=True,
	bleed_cut_edges=True,
	shadow={"opacity": 0},
	retouch=False,
	max_size=400,
)


def _photo(size=(1000, 1000), box=(200, 150, 799, 899)):
	image = Image.new("RGB", size, GROUND)
	draw = ImageDraw.Draw(image)
	draw.rectangle(box, fill=PIECE)
	x0, y0, x1, y1 = box
	for y in range(y0 + 20, y1 - 10, 40):
		draw.line([(x0 + 10, y), (x1 - 10, y)], fill=LINE, width=4)
	return image


def _png(image):
	buf = io.BytesIO()
	image.save(buf, "PNG")
	return buf.getvalue()


class CutoutIsHeldToMaxSize(unittest.TestCase):
	def setUp(self):
		self.result = image_style.apply_finish(_png(_photo()), STYLE)
		self.assertIsNone(self.result["note"])
		self.cutout = Image.open(io.BytesIO(self.result["cutout"]))

	def test_cutout_is_no_larger_than_max_size(self):
		self.assertLessEqual(max(self.cutout.size), 400)

	def test_recorded_frame_is_scaled_with_it(self):
		self.assertEqual(image_style._read_framing(self.cutout)[0], (400, 400))

	def test_recompose_still_matches_the_first_finish(self):
		again = image_style.recompose(self.result["cutout"], STYLE)
		first = Image.open(io.BytesIO(self.result["image"])).convert("RGB")
		self.assertEqual(Image.open(io.BytesIO(again)).convert("RGB").tobytes(), first.tobytes())

	def test_a_photo_within_max_size_keeps_its_resolution(self):
		result = image_style.apply_finish(_png(_photo((300, 300), (60, 40, 239, 269))), STYLE)
		cutout = Image.open(io.BytesIO(result["cutout"]))
		self.assertEqual(image_style._read_framing(cutout)[0], (300, 300))


class OneFailedSaveFailsOnePhoto(unittest.TestCase):
	def test_other_photos_still_get_their_results(self):
		source = {"type": "base64", "media_type": "image/png", "data": base64.b64encode(_png(_photo())).decode()}

		def save(prefix, content, mime, default_ext=".png"):
			if prefix == "listing-cutout" and save.calls == 1:
				raise RuntimeError("File size exceeded the maximum allowed size of 10.0 MB")
			save.calls += prefix == "listing-cutout"
			return f"/files/{prefix}-{save.calls}.png"

		save.calls = 0
		with (
			mock.patch.object(image_style, "load", return_value=STYLE),
			mock.patch.object(image_generation.images, "reference_source", return_value=source),
			mock.patch.object(image_generation.images, "save_public_image", side_effect=save),
			mock.patch.object(image_generation.frappe, "log_error"),
		):
			result = image_generation.render_generated(None, {"urls": ["/files/a.jpg", "/files/b.jpg"]})

		rows = {row["source_url"]: row for row in result["images"]}
		self.assertTrue(rows["/files/a.jpg"]["url"])
		self.assertIsNone(rows["/files/b.jpg"]["url"])
		self.assertIn("maximum allowed size", rows["/files/b.jpg"]["note"])
