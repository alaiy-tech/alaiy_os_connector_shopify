"""Products the shot crops — a strap running out of the frame — through the house finish.

Three failures, each pinned on a synthetic photo of the same shape as the real
one it came from:

  * the ground check read a strap crossing the border ring as an uneven
    background, so the photo fell back to the segmentation model, which dropped
    the strap;
  * the fill was seeded at the four corners, and a strap leaving through a corner
    got taken for the ground and erased;
  * a strap cropped at both ends was padded on every side, so its cut ends sat in
    mid-air instead of at the edge of the canvas.

Run via `bench run-tests`; nothing here needs a site.
"""

import io
import unittest

from PIL import Image, ImageDraw, ImageFilter

from alaiy_os_connector_shopify.listing import image_style

GROUND = (244, 244, 244)
STRAP = (218, 192, 186)
CASE = (120, 120, 125)


def _diagonal_strap(size=300):
	"""A strap leaving through the top-right and bottom-left corners, a case in the middle."""
	image = Image.new("RGB", (size, size), GROUND)
	draw = ImageDraw.Draw(image)
	draw.line([(size + size // 3, -size // 3), (-size // 3, size + size // 3)], fill=STRAP, width=size // 5)
	middle = size // 2
	draw.ellipse([middle - 50, middle - 50, middle + 50, middle + 50], fill=CASE)
	return image


def _vertical_strap(width=200, height=340):
	"""A strap cropped at the top and bottom of the frame, a case in the middle."""
	image = Image.new("RGB", (width, height), GROUND)
	draw = ImageDraw.Draw(image)
	middle = width // 2
	draw.rectangle([middle - 35, 0, middle + 35, height - 1], fill=STRAP)
	draw.ellipse([middle - 60, height // 2 - 60, middle + 60, height // 2 + 60], fill=CASE)
	return image


def _tight_cutout(size=1000):
	"""A transparent cutout cropped to the piece: a strap with rounded, finished
	ends that touch the top and bottom of the frame, a case in the middle."""
	image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
	draw = ImageDraw.Draw(image)
	middle = size // 2
	draw.rounded_rectangle([middle - 100, 1, middle + 100, size - 2], radius=90, fill=STRAP + (255,))
	draw.ellipse([middle - 230, middle - 230, middle + 230, middle + 230], fill=CASE + (255,))
	return image


class _NoMatting:
	"""A matting client that fails the test if it is asked for anything."""

	def __getattr__(self, name):
		raise AssertionError(f"the matte was called ({name}) for a photo that is already a cutout")


def _share_kept(alpha, image, color):
	"""What fraction of the pixels of `color` the mask keeps."""
	kept = total = 0
	pixels, mask = image.load(), alpha.load()
	for y in range(image.height):
		for x in range(image.width):
			if pixels[x, y] == color:
				total += 1
				kept += mask[x, y] > 128
	return kept / total


def _finish(image, client=None, **spec):
	buf = io.BytesIO()
	image.save(buf, "PNG")
	style = dict(image_style.DEFAULTS, background="#f4f4f4", matte="flood")
	style.update(spec)
	result = image_style.apply_finish(buf.getvalue(), style, client)
	return result, Image.open(io.BytesIO(result["image"])).convert("RGB")


class StrapCrossingTheBorderIsNotUnevenGround(unittest.TestCase):
	def test_a_strap_through_the_ring_passes(self):
		self.assertIsNone(image_style._ground_complaint(_diagonal_strap()))

	def test_a_graded_backdrop_still_fails(self):
		image = Image.new("RGB", (300, 300))
		draw = ImageDraw.Draw(image)
		for x in range(300):
			shade = 255 - x * 60 // 300
			draw.line([(x, 0), (x, 299)], fill=(shade, shade, shade))
		self.assertIsNotNone(image_style._ground_complaint(image))


class FillIsSeededOnlyOnGround(unittest.TestCase):
	def test_strap_in_the_corners_is_kept(self):
		image = _diagonal_strap()
		alpha = image_style._subject_alpha(image)
		self.assertGreater(_share_kept(alpha, image, STRAP), 0.95)
		self.assertLess(_share_kept(alpha, image, GROUND), 0.05)


class CutEdges(unittest.TestCase):
	def _cut(self, image):
		return image_style._cut_edges(image_style._subject_alpha(image))

	def test_strap_cropped_top_and_bottom(self):
		self.assertEqual(self._cut(_vertical_strap()), {"top", "bottom"})

	def test_strap_leaving_through_corners_cuts_every_side(self):
		self.assertEqual(self._cut(_diagonal_strap()), {"left", "top", "right", "bottom"})

	def test_thin_chain_cropped_at_the_top_is_cut(self):
		# Two strands crossing the top: a small share of the piece's width, but
		# straight at the edge.
		image = Image.new("RGB", (1000, 1000), GROUND)
		draw = ImageDraw.Draw(image)
		draw.line([(310, -60), (470, 420)], fill=CASE, width=14)
		draw.line([(690, -60), (530, 420)], fill=CASE, width=14)
		draw.ellipse([250, 380, 750, 880], fill=CASE)
		self.assertEqual(self._cut(image), {"top"})

	def test_round_piece_touching_a_side_is_not_cut(self):
		# At a photo's resolution, not a thumbnail's: a hard-edged circle's
		# outermost column is ~1/sqrt(radius) of its height.
		image = Image.new("RGB", (1000, 1000), GROUND)
		ImageDraw.Draw(image).ellipse([4, 200, 604, 800], fill=CASE)
		self.assertEqual(self._cut(image), frozenset())

	def test_crop_inside_a_thin_rim_still_counts(self):
		image = Image.new("RGB", (206, 350), (253, 253, 253))
		image.paste(_vertical_strap(200, 344), (3, 3))
		self.assertEqual(self._cut(image), {"top", "bottom"})

	def test_finished_strap_ends_in_a_tight_cutout_are_not_cut(self):
		# The strap's own rounded ends touch the frame because the cutout is
		# cropped to the piece, not because the shot cropped the strap. A mask
		# rebuilt from the flattened photo comes back a pixel or two generous,
		# which broadens each tip's last line; that alone must not make it a cut.
		alpha = _tight_cutout().getchannel("A")
		for grow in (0, 1, 2, 4, 7):
			with self.subTest(grow=grow):
				mask = alpha.filter(ImageFilter.MaxFilter(2 * grow + 1)) if grow else alpha
				self.assertEqual(image_style._cut_edges(mask), frozenset())


class TransparentCutoutKeepsItsOwnOutline(unittest.TestCase):
	def test_tight_cutout_is_padded_at_both_ends(self):
		result, finished = _finish(
			_tight_cutout(), matte="gemini_key", bleed_cut_edges=True, client=_NoMatting()
		)
		self.assertIsNone(result["note"])
		# The strap ends inside the margin at both ends, as the piece itself does.
		for y in (0, finished.height - 1):
			self.assertNotIn(STRAP, {finished.getpixel((x, y)) for x in range(finished.width)})
		self.assertIn(STRAP, {finished.getpixel((finished.width // 2, y)) for y in range(finished.height)})

	def test_cutout_needs_no_matting_provider(self):
		result, _ = _finish(_tight_cutout(), matte="gemini_key")
		self.assertIsNone(result["note"])

	def test_opaque_alpha_is_not_a_cutout(self):
		image = _vertical_strap().convert("RGBA")
		self.assertIsNone(image_style._own_alpha(image))

	def test_fully_transparent_alpha_is_not_a_cutout(self):
		self.assertIsNone(image_style._own_alpha(Image.new("RGBA", (100, 100), (0, 0, 0, 0))))


class CutStrapRunsOffTheCanvas(unittest.TestCase):
	def test_flush_top_and_bottom_and_centred_across(self):
		result, finished = _finish(_vertical_strap(), bleed_cut_edges=True)
		self.assertIsNone(result["note"])
		width, height = finished.size
		middle = width // 2
		self.assertNotEqual(finished.getpixel((middle, 0)), GROUND)
		self.assertNotEqual(finished.getpixel((middle, height - 1)), GROUND)
		# Centred across: the strap's middle is the canvas's middle.
		row = [finished.getpixel((x, 0)) != GROUND for x in range(width)]
		first, last = row.index(True), width - 1 - row[::-1].index(True)
		self.assertLessEqual(abs((first + last) / 2 - middle), 1)

	def test_off_by_default_keeps_the_margin(self):
		result, finished = _finish(_vertical_strap())
		self.assertIsNone(result["note"])
		# The shadow may reach the bottom row; the strap must not reach either.
		for y in (0, finished.height - 1):
			self.assertNotIn(STRAP, {finished.getpixel((x, y)) for x in range(finished.width)})
