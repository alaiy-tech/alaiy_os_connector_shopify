"""
Two helpers introduced when Product.images and ProductVariant.image were
retired in favour of media, and the product query started asking for more
than one inventory state.

Both replace an index-based read that was correct only while the shape had
exactly one entry, so these pin the cases where an index would now be wrong:
media that isn't a photo, and a quantities list where "available" isn't
first.
"""

import unittest

from alaiy_os_connector_shopify.shopify.product.media import product_image_urls
from alaiy_os_connector_shopify.shopify.product.variants import level_quantity


def _img(url):
    return {"preview": {"image": {"url": url}}}


class TestProductImageUrls(unittest.TestCase):
    def test_featured_comes_first(self):
        # Callers take [0] as the main image; Shopify does not guarantee
        # media order matches featuredMedia.
        urls = product_image_urls({
            "featuredMedia": _img("https://cdn/featured.jpg"),
            "media": {"nodes": [
                dict(mediaContentType="IMAGE", **_img("https://cdn/other.jpg")),
                dict(mediaContentType="IMAGE", **_img("https://cdn/featured.jpg")),
            ]},
        })
        self.assertEqual(urls[0], "https://cdn/featured.jpg")

    def test_featured_is_not_duplicated_when_it_also_appears_in_media(self):
        urls = product_image_urls({
            "featuredMedia": _img("https://cdn/a.jpg"),
            "media": {"nodes": [dict(mediaContentType="IMAGE", **_img("https://cdn/a.jpg"))]},
        })
        self.assertEqual(urls, ["https://cdn/a.jpg"])

    def test_video_and_3d_previews_are_skipped(self):
        # A video's preview is a poster frame, not a product photo -- it must
        # not become an Item's image.
        urls = product_image_urls({"media": {"nodes": [
            dict(mediaContentType="VIDEO", **_img("https://cdn/poster.jpg")),
            dict(mediaContentType="MODEL_3D", **_img("https://cdn/model.jpg")),
            dict(mediaContentType="IMAGE", **_img("https://cdn/real.jpg")),
        ]}})
        self.assertEqual(urls, ["https://cdn/real.jpg"])

    def test_media_still_processing_has_no_url_and_is_dropped(self):
        # preview.image is null until status is READY.
        urls = product_image_urls({"media": {"nodes": [
            {"mediaContentType": "IMAGE", "preview": {"image": None}},
            dict(mediaContentType="IMAGE", **_img("https://cdn/ok.jpg")),
        ]}})
        self.assertEqual(urls, ["https://cdn/ok.jpg"])

    def test_product_with_no_media_is_an_empty_list(self):
        self.assertEqual(product_image_urls({}), [])
        self.assertEqual(product_image_urls({"media": {"nodes": []}}), [])


class TestLevelQuantity(unittest.TestCase):
    def test_reads_by_name_not_by_position(self):
        # The whole point: available is not first here, and an index read
        # would return on_hand as if it were sellable stock.
        level = {"quantities": [
            {"name": "on_hand", "quantity": 10},
            {"name": "available", "quantity": 4},
            {"name": "committed", "quantity": 6},
        ]}
        self.assertEqual(level_quantity(level), 4)
        self.assertEqual(level_quantity(level, "on_hand"), 10)
        self.assertEqual(level_quantity(level, "committed"), 6)

    def test_unnamed_single_entry_still_works(self):
        # A query asking for one state omits the name field, and those
        # queries still exist elsewhere in the connector.
        self.assertEqual(level_quantity({"quantities": [{"quantity": 7}]}), 7)

    def test_missing_state_is_zero_not_a_wrong_number(self):
        level = {"quantities": [{"name": "on_hand", "quantity": 10}]}
        self.assertEqual(level_quantity(level, "available"), 0.0)

    def test_empty_and_absent_quantities_are_zero(self):
        self.assertEqual(level_quantity({"quantities": []}), 0.0)
        self.assertEqual(level_quantity({}), 0.0)


if __name__ == "__main__":
    unittest.main()
