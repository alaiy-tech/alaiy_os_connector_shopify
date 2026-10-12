"""The `gemini_key` matte: Gemini isolates the product onto a vivid key colour, and
the key is removed by colour, including ground the product encloses.

The client is a stand-in that returns a synthetic render, so what is pinned is
what the matte does with a render, not what Gemini draws.

Run via `bench run-tests`; nothing here needs a site.
"""

import base64
import io
import unittest

from PIL import Image, ImageDraw

from alaiy_os_connector_shopify.listing import image_style

GROUND = (250, 250, 250)
METAL = (150, 150, 155)
MAGENTA = (255, 0, 255)
GREEN = (0, 255, 0)


def _bangle(size=300, ground=GROUND):
	"""A ring of metal whose middle is ground the product encloses."""
	image = Image.new("RGB", (size, size), ground)
	draw = ImageDraw.Draw(image)
	draw.ellipse([60, 60, 240, 240], fill=METAL)
	draw.ellipse([100, 100, 200, 200], fill=ground)
	return image


class _Client:
	"""Returns `render(photo, key)` for every generate_image call, and records them."""

	def __init__(self, render):
		self.render = render
		self.calls = []

	def generate_image(self, prompt, reference_data_uri=None, model=None):
		self.calls.append({"prompt": prompt, "model": model})
		photo = Image.open(io.BytesIO(base64.b64decode(reference_data_uri.split(",", 1)[1]))).convert("RGB")
		key = next(k for k in image_style._KEY_COLORS if k in prompt)
		buf = io.BytesIO()
		self.render(photo, image_style._rgb(key)).save(buf, "PNG")
		return {"b64": base64.b64encode(buf.getvalue()).decode()}


def _onto_key(photo, key, ground=GROUND):
	"""A faithful render: every ground pixel, enclosed or not, becomes the key."""
	render = photo.copy()
	pixels = render.load()
	for y in range(render.height):
		for x in range(render.width):
			if pixels[x, y] == ground:
				pixels[x, y] = key
	return render


class EnclosedGroundIsRemoved(unittest.TestCase):
	def test_the_inside_of_a_bangle_is_ground(self):
		alpha = image_style._gemini_keyed(_Client(_onto_key), _bangle())
		self.assertEqual(alpha.getpixel((150, 150)), 0)
		self.assertEqual(alpha.getpixel((80, 150)), 255)
		self.assertEqual(alpha.getpixel((5, 5)), 0)

	def test_the_flood_matte_keeps_it_which_is_the_failure(self):
		alpha = image_style._subject_alpha(_bangle())
		self.assertGreater(alpha.getpixel((150, 150)), 128)


class KeyIsChosenPerPhoto(unittest.TestCase):
	def test_magenta_when_nothing_clashes(self):
		self.assertEqual(image_style._pick_key(_bangle()), "#ff00ff")

	def test_a_magenta_product_gets_another_key(self):
		image = _bangle()
		ImageDraw.Draw(image).rectangle([120, 20, 180, 50], fill=(230, 20, 200))
		self.assertEqual(image_style._pick_key(image), "#00ff00")

	def test_no_clear_key_falls_back(self):
		image = Image.new("RGB", (300, 300), GROUND)
		draw = ImageDraw.Draw(image)
		for i, color in enumerate(((240, 10, 230), (10, 240, 20), (20, 10, 240))):
			draw.rectangle([20 + i * 90, 100, 90 + i * 90, 200], fill=color)
		self.assertIsNone(image_style._pick_key(image))
		client = _Client(_onto_key)
		self.assertIsNone(image_style._gemini_keyed(client, image))
		self.assertEqual(client.calls, [])


class ProductNearTheKeyIsKept(unittest.TestCase):
	def test_a_sliver_of_key_colour_in_the_product_survives(self):
		# Small enough that magenta is still chosen; the render shows it as the
		# key, as a faithful render of the product would.
		image = _bangle()
		ImageDraw.Draw(image).rectangle([70, 148, 73, 151], fill=(250, 5, 250))
		self.assertEqual(image_style._pick_key(image), "#ff00ff")
		alpha = image_style._gemini_keyed(_Client(_onto_key), image)
		self.assertEqual(alpha.getpixel((71, 150)), 255)


INNER_WALL = (205, 205, 210)


def _band(size=300):
	"""A wide band seen from above: a metal rim around an inner wall that is also
	metal - pale, but not the backdrop - with grooves cut across its face."""
	image = Image.new("RGB", (size, size), GROUND)
	draw = ImageDraw.Draw(image)
	draw.ellipse([40, 40, 260, 260], fill=METAL)
	draw.ellipse([90, 90, 210, 210], fill=INNER_WALL)
	for y in range(225, 250, 8):
		draw.line([(110, y), (190, y)], fill=(120, 120, 125), width=2)
	return image


def _keys_too_much(photo, key):
	"""A render that over-reads "every gap and opening": the inner wall and the
	grooves come back as key, alongside the real ground."""
	render = _onto_key(photo, key)
	draw = ImageDraw.Draw(render)
	draw.ellipse([90, 90, 210, 210], fill=key)
	for y in range(225, 250, 8):
		draw.line([(110, y), (190, y)], fill=key, width=2)
	return render


class EnclosedProductIsKept(unittest.TestCase):
	"""Ground the product encloses is only ground where the photo shows backdrop."""

	def test_an_inner_wall_the_render_keyed_out_is_kept(self):
		alpha = image_style._gemini_keyed(_Client(_keys_too_much), _band())
		self.assertEqual(alpha.getpixel((150, 150)), 255)

	def test_grooves_the_render_keyed_out_are_kept(self):
		alpha = image_style._gemini_keyed(_Client(_keys_too_much), _band())
		self.assertEqual(alpha.getpixel((150, 233)), 255)

	def test_the_backdrop_around_the_band_is_still_ground(self):
		alpha = image_style._gemini_keyed(_Client(_keys_too_much), _band())
		self.assertEqual(alpha.getpixel((5, 5)), 0)

	def test_a_shadowed_bangle_hole_is_still_ground(self):
		# Mostly backdrop, with a soft shadow across part of it: still the hole.
		image = _bangle()
		ImageDraw.Draw(image).rectangle([100, 175, 200, 200], fill=(200, 200, 200))
		def render(photo, key):
			out = _onto_key(photo, key)
			ImageDraw.Draw(out).ellipse([100, 100, 200, 200], fill=key)
			return out
		alpha = image_style._gemini_keyed(_Client(render), image)
		self.assertEqual(alpha.getpixel((150, 140)), 0)


class RenderOffTheKeyIsRefused(unittest.TestCase):
	def test_render_on_the_wrong_colour(self):
		client = _Client(lambda photo, key: photo)
		self.assertIsNone(image_style._gemini_keyed(client, _bangle()))

	def test_render_on_an_uneven_ground(self):
		def patchy(photo, key):
			render = _onto_key(photo, key)
			draw = ImageDraw.Draw(render)
			for x in range(0, render.width, 20):
				draw.rectangle([x, 0, x + 9, render.height], fill=(40, 200, 60))
			return render

		self.assertIsNone(image_style._gemini_keyed(_Client(patchy), _bangle()))


class ThroughTheFinish(unittest.TestCase):
	def test_gemini_key_matte_finishes_with_the_gap_on_the_house_ground(self):
		# Textured: a perfectly flat product is refused as featureless.
		image = _bangle()
		draw = ImageDraw.Draw(image)
		for y in range(64, 240, 12):
			draw.line([(60, y), (240, y)], fill=(110, 110, 115))
		draw.ellipse([100, 100, 200, 200], fill=GROUND)
		buf = io.BytesIO()
		image.save(buf, "PNG")
		style = dict(image_style.DEFAULTS, background="#f4f4f4", matte="gemini_key", shadow={"opacity": 0})
		client = _Client(_onto_key)
		result = image_style.apply_finish(buf.getvalue(), style, client)
		self.assertIsNone(result["note"])
		self.assertEqual(len(client.calls), 1)
		self.assertEqual(client.calls[0]["model"], image_style._GEMINI_MASK_MODEL)
		finished = Image.open(io.BytesIO(result["image"])).convert("RGB")
		middle = (finished.width // 2, finished.height // 2)
		self.assertEqual(finished.getpixel(middle), (244, 244, 244))

	def test_capability(self):
		self.assertEqual(image_style.finish_capability({"matte": "gemini_key"}), "generate")
