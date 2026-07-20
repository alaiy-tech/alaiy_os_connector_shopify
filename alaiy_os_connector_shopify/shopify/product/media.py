"""
Image/media helpers -- moved verbatim from product_import.py and
product_sync.py, unchanged.
"""

import frappe


def _download_to_file(url: str, doctype: str, name: str) -> str:
    """
    Fetch an image URL and attach it as a File on (doctype, name); return the
    stored file_url. Raises on network/HTTP failure -- callers decide whether
    to skip or log.

    Fetches the bytes via requests (already a hard dependency, used the same
    way in graphql_client.py) and saves through save_file, a stable public
    Frappe API -- frappe.integrations.utils.download_file was removed/renamed
    in this Frappe version (confirmed live: ImportError on every image, so
    image sync was silently 100% broken), and internal module paths can move
    again.
    """
    import requests
    from frappe.utils.file_manager import save_file

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    filename = url.split("?")[0].rsplit("/", 1)[-1] or f"{name}.jpg"
    return save_file(filename, resp.content, doctype, name, is_private=0).file_url


def _set_item_image(item_code: str, image_url: str):
    """Download image from URL and set as Item's main image."""
    if not image_url:
        return
    try:
        file_url = _download_to_file(image_url, "Item", item_code)
        frappe.db.set_value("Item", item_code, "image", file_url)
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Failed to download image for {item_code}",
            message=f"URL: {image_url}\n{frappe.get_traceback()}"
        )


def _set_item_slideshow(item_code: str, image_urls: list, settings):
    """
    Create a Website Slideshow from multiple images and link to Item.
    """
    if len(image_urls) < 2:
        return

    # "slideshow" is a core Item field on some Alaiy OS builds but not
    # others -- confirmed live on a second client site: "Unknown column
    # 'slideshow' in 'SET'" crashed every multi-image import outright.
    # Registering our own custom field with the same name risks colliding
    # with the real core field on sites where it DOES exist, so just skip
    # gracefully wherever the column itself is genuinely absent.
    if not frappe.get_meta("Item").has_field("slideshow"):
        return

    try:
        slideshow_name = f"{item_code}-images"

        # Check if slideshow already exists
        if frappe.db.exists("Website Slideshow", slideshow_name):
            return  # Don't overwrite

        slideshow = frappe.new_doc("Website Slideshow")
        # Website Slideshow autonames via "field:slideshow_name" -- setting
        # doc.name directly (the old code here) never satisfies that; only
        # setting the real slideshow_name field does. This was dormant the
        # entire time image download was broken (fixed earlier this
        # session) since insert() was never actually reached before now.
        slideshow.slideshow_name = slideshow_name

        for image_url in image_urls[1:]:  # First image is already set as main
            try:
                file_url = _download_to_file(image_url, "Website Slideshow", slideshow_name)
            except Exception:
                continue  # Skip failed images
            slideshow.append("slideshow_items", {
                "image": file_url,
                "image_url": image_url,
            })

        if slideshow.slideshow_items:
            slideshow.flags.ignore_permissions = True
            slideshow.insert()

            # Link to Item
            frappe.db.set_value("Item", item_code, "slideshow", slideshow_name)
            frappe.db.commit()

    except Exception:
        frappe.log_error(
            title=f"Failed to create slideshow for {item_code}",
            message=frappe.get_traceback()
        )


def _absolute_file_url(url: str) -> str:
    """
    Alaiy OS's own file fields (Item.image, Website Slideshow's image rows)
    store root-relative paths like "/files/xyz.jpg" -- fine for our own
    UI, but Shopify's productSet rejected every single one live with
    "File URL is invalid" since originalSource needs a real, publicly
    reachable absolute URL, not a path relative to nothing as far as
    Shopify's servers are concerned.
    """
    if url.startswith("/"):
        return frappe.utils.get_url(url)
    return url


def _item_images(item, settings) -> list:
    if not settings.sh_push_images:
        return []
    urls = []
    if item.image:
        urls.append(item.image)
    if item.get("slideshow") and frappe.db.exists("Website Slideshow", item.slideshow):
        slideshow = frappe.get_doc("Website Slideshow", item.slideshow)
        for row in slideshow.slideshow_items:
            if row.image and row.image not in urls:
                urls.append(row.image)
    return [_absolute_file_url(u) for u in urls]
