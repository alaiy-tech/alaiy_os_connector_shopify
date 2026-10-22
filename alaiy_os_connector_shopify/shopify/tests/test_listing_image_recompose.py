"""A kept cutout finished again, and a photo or cutout placed in the frame by hand.

`apply_finish` records in the cutout's PNG the photo it was cut from and the sides
that photo cropped the piece at; `recompose` reads both back and makes the finish
exactly as first made. `place` sets the piece where a reviewer framed it: a square
of the (optionally cropped) image, running past it wherever room was left.

Run via `bench run-tests`; nothing here needs a site.
"""

import io
import unittest

from PIL import Image, ImageDraw

from alaiy_os_connector_shopify.listing import image_style

GROUND = (244, 244, 244)
PIECE = (120, 120, 125)
# Detail inside the piece, which the finish needs to tell a product from a blank.
LINE = (60, 60, 64)

# No shadow, so the piece's own pixels are all that differ from the ground.
STYLE = dict(
	image_style.DEFAULTS,
	background="#f4f4f4",
	matte="flood",
	keep_cutout=True,
	bleed_cut_edges=True,
	shadow={"opacity": 0},
)


def _photo(size, box):
	image = Image.new("RGB", size, GROUND)
	draw = ImageDraw.Draw(image)
	draw.rectangle(box, fill=PIECE)
	x0, y0, x1, y1 = box
	for y in range(y0 + 20, y1 - 10, 40):
		draw.line([(x0 + 10, y), (x1 - 10, y)], fill=LINE, width=4)
	return image


def _small_piece():
	"""A small piece with plenty of room around it, cropped at no side."""
	return _photo((1000, 1000), [400, 400, 599, 599])


def _strap():
	"""A strap cropped at the top and bottom of the frame."""
	return _photo((400, 600), [150, 0, 249, 599])


def _finish(image):
	buf = io.BytesIO()
	image.save(buf, "PNG")
	result = image_style.apply_finish(buf.getvalue(), STYLE)
	assert result["note"] is None, result["note"]
	return result


def _open(content):
	return Image.open(io.BytesIO(content)).convert("RGB")


def _margins(image):
	"""(left, top, right, bottom) clear of the piece, as shares of the canvas."""
	# Anything off the ground counts, the piece's soft edge included: the margin
	# is measured from the cutout's outline, and that is where its edge ends.
	mask = image.convert("L").point(lambda v: 255 if v < 242 else 0)
	x0, y0, x1, y1 = mask.getbbox()
	width, height = image.size
	return x0 / width, y0 / height, (width - x1) / width, (height - y1) / height


class FramingIsRecorded(unittest.TestCase):
	def test_frame_and_cut_sides_ride_in_the_cutout(self):
		cutout = Image.open(io.BytesIO(_finish(_strap())["cutout"]))
		self.assertEqual(image_style._read_framing(cutout), ((400, 600), {"top", "bottom"}))

	def test_a_cutout_without_framing_reads_as_none(self):
		buf = io.BytesIO()
		Image.new("RGBA", (10, 10), PIECE + (255,)).save(buf, "PNG")
		self.assertEqual(image_style._read_framing(Image.open(buf)), (None, frozenset()))


class RecomposeIsTheFirstFinish(unittest.TestCase):
	def test_same_pixels_as_apply_finish(self):
		for photo in (_small_piece(), _strap()):
			with self.subTest(size=photo.size):
				result = _finish(photo)
				again = image_style.recompose(result["cutout"], STYLE)
				self.assertEqual(_open(again).tobytes(), _open(result["image"]).tobytes())


def _cutout():
	"""The small piece's kept cutout: 204px square, the piece filling it."""
	return _finish(_small_piece())["cutout"]


def _centred(padding):
	"""The frame a reviewer gets from "fit with `padding`" on a square image."""
	side = 1 / (1 - 2 * padding)
	return {"x": (1 - side) / 2, "y": (1 - side) / 2, "width": side, "height": side}


class Place(unittest.TestCase):
	def test_room_left_around_the_piece_is_the_margin(self):
		for padding in (0.0, 0.1, 0.3):
			with self.subTest(padding=padding):
				placed = _open(image_style.place(_cutout(), STYLE, _centred(padding)))
				# A few pixels of the matte's soft edge on a ~200-600px canvas.
				for side in _margins(placed):
					self.assertAlmostEqual(side, padding, delta=0.015)

	def test_moved_off_centre(self):
		frame = dict(_centred(0.2), x=_centred(0.2)["x"] - 0.2)
		left, _, right, _ = _margins(_open(image_style.place(_cutout(), STYLE, frame)))
		self.assertGreater(left, right + 0.1)

	def test_never_scaled_up_only_down_to_max_size(self):
		self.assertEqual(_open(image_style.place(_cutout(), STYLE, _centred(0.0))).size, (204, 204))
		big = _open(image_style.place(_cutout(), STYLE, _centred(0.1), max_size=120))
		self.assertEqual(big.size, (120, 120))

	def test_crop_trims_before_framing(self):
		# The right half of the strap photo, framed edge to edge: only strap remains,
		# with the ground the crop kept to its right.
		crop = {"x": 0.5, "y": 0.0, "width": 0.5, "height": 1.0}
		frame = {"x": 0.0, "y": 0.0, "width": 1.0, "height": 200 / 600}
		placed = _open(image_style.place(_png(_strap()), STYLE, frame, crop=crop))
		self.assertEqual(placed.size, (200, 200))
		self.assertIn(placed.getpixel((0, 100)), (PIECE, LINE))
		self.assertEqual(placed.getpixel((199, 100)), GROUND)

	def test_a_photo_with_its_own_background_is_pasted_as_it_is(self):
		photo = Image.new("RGB", (100, 100), (255, 255, 255))
		placed = _open(image_style.place(_png(photo), STYLE, _centred(0.25)))
		self.assertEqual(placed.size, (200, 200))
		self.assertEqual(placed.getpixel((100, 100)), (255, 255, 255))
		self.assertEqual(placed.getpixel((10, 10)), GROUND)

	def test_a_crop_that_leaves_nothing_is_refused(self):
		with self.assertRaises(ValueError):
			image_style.place(_cutout(), STYLE, _centred(0), crop={"x": 1, "y": 0, "width": 0, "height": 1})


def _png(image):
	buf = io.BytesIO()
	image.save(buf, "PNG")
	return buf.getvalue()
