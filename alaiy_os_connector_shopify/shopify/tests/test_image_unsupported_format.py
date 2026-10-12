"""A stored photo in a format the vision API rejects is converted, not fetched as a URL."""

import base64
import io
import sys
import unittest
from unittest.mock import MagicMock

from PIL import Image


def _images():
    sys.modules.setdefault("frappe", MagicMock())
    from alaiy_os_connector_shopify.listing import images

    return images


def _avif_bytes():
    out = io.BytesIO()
    Image.new("RGB", (4, 4), (200, 30, 30)).save(out, "AVIF")
    return out.getvalue()


class TestUnsupportedFormat(unittest.TestCase):
    def setUp(self):
        self.images = _images()

    def _file_doc(self, name, content):
        doc = MagicMock(file_name=name, file_url="/files/" + name)
        doc.get_content.return_value = content
        self.images.frappe.get_doc.return_value = doc

    def test_avif_is_converted_to_png(self):
        self._file_doc("photo.avif", _avif_bytes())
        block = self.images.image_block_from_file("photo.avif")
        self.assertEqual(block["source"]["media_type"], "image/png")
        png = base64.b64decode(block["source"]["data"])
        self.assertEqual(Image.open(io.BytesIO(png)).format, "PNG")

    def test_supported_format_is_untouched(self):
        self._file_doc("photo.jpg", b"jpegbytes")
        block = self.images.image_block_from_file("photo.jpg")
        self.assertEqual(block["source"]["media_type"], "image/jpeg")

    def test_undecodable_file_returns_none(self):
        self._file_doc("photo.avif", b"not an image")
        self.assertIsNone(self.images.image_block_from_file("photo.avif"))

    def test_unreadable_stored_path_is_not_fetched(self):
        self.images.frappe.db.get_value.return_value = None
        with self.assertRaises(ValueError):
            self.images.reference_source("/files/gone.avif")


if __name__ == "__main__":
    unittest.main()
