# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
Image plumbing shared by the agent's two image tools.

Nothing here is a tool: these are the primitives the image tools are built out
of. The base app deliberately ships NO image tool of its own — what counts as
"the image step" differs per customer (The Solist generates editorial shots; naya
translates the Chinese text printed on supplier photos), and that judgement
belongs in the customer app. What is genuinely common is everything around it:
turning a photo into something the model can see, and re-hosting a result so it
survives.

The provider CALLS are no longer part of that split. Both image steps now go
through Alaiy OS core's `ai_client` seam, so no app on the bench holds a provider
credential or speaks a provider's wire format — the managed client serves both
via the billing service. What stays here is the local half the seam cannot do:
reading a Frappe File, and writing one back.

Names here are public (no leading underscore) because the tool modules import them.
"""

import base64
import os

import frappe

# Anthropic vision accepts JPEG, PNG, GIF, WEBP.
MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}
MEDIA_TYPES_BY_MIME = {v: k for k, v in MEDIA_TYPES.items()}

# Some product-photo CDNs block requests with no browser-like User-Agent
# (confirmed: Anthropic's own url-source fetch got refused on one such CDN) — so
# we always fetch external images ourselves rather than passing a bare URL for
# the model to fetch.
FETCH_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AlaiyOS-ShopifyListing/1.0)"}


def file_stem(url):
    """A photo's file name without its folder, query string or extension.

    How one photo is recognised across the addresses it lives at: a Shopify
    push re-hosts /files/listing-worn-abc.jpeg as
    https://cdn.shopify.com/.../listing-worn-abc.jpg?v=123 - another host, a
    version suffix, and sometimes a different extension.
    """
    name = (url or "").split("?", 1)[0].rsplit("/", 1)[-1]
    return name.rsplit(".", 1)[0]


def media_type(path_or_name):
    """Guess an image media type from a filename or URL extension, or None."""
    ext = os.path.splitext(path_or_name or "")[1].lower()
    return MEDIA_TYPES.get(ext)


def _as_png(content):
    """PNG bytes for an image in a format the vision API does not accept (AVIF,
    BMP, TIFF ...), or None when Pillow cannot decode it."""
    import io

    try:
        from PIL import Image

        img = Image.open(io.BytesIO(content))
        img.load()
        out = io.BytesIO()
        img.convert("RGBA" if "A" in img.getbands() else "RGB").save(out, "PNG")
        return out.getvalue()
    except Exception:
        return None


def image_block_from_file(file_name):
    """Build a base64 Anthropic image block from a File docname, or None."""
    mime = media_type(file_name)
    try:
        file_doc = frappe.get_doc("File", file_name)
        mime = mime or media_type(file_doc.file_name or file_doc.file_url)
        content = file_doc.get_content()  # bytes for a binary/image file
        if isinstance(content, str):
            content = content.encode("utf-8", "ignore")
        if not mime:
            content = _as_png(content)
            if not content:
                return None
            mime = "image/png"
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime,
                "data": base64.b64encode(content).decode("ascii"),
            },
        }
    except Exception:
        return None


def fetch_image_bytes(image_url):
    """Download an external image URL ourselves. Returns (bytes, media_type)."""
    import requests

    resp = requests.get(image_url, timeout=30, headers=FETCH_HEADERS)
    resp.raise_for_status()
    mime = (resp.headers.get("Content-Type") or "").split(";")[0].strip()
    if not mime or not mime.startswith("image/"):
        mime = media_type(image_url) or "image/jpeg"
    return resp.content, mime


def fetch_image_block(image_url):
    """Build a base64 Anthropic image block from an external image URL."""
    content, mime = fetch_image_bytes(image_url)
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": mime,
            "data": base64.b64encode(content).decode("ascii"),
        },
    }


def _stored_block(url):
    """A vision block for an image the site holds in its S3 bucket, read with the
    site's own access, or None. A stored object is private, so a plain HTTP GET of its
    URL is refused; this is how the model still sees it."""
    from alaiy_os import image_store

    if not image_store.is_stored_url(url):
        return None
    try:
        stored = image_store.read(url)
    except Exception:
        return None
    if not stored:
        return None
    content, mime = stored
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": mime or media_type(url) or "image/jpeg",
            "data": base64.b64encode(content).decode("ascii"),
        },
    }


def image_block_from_url(url):
    """
    Build a vision block from an image URL stored on a listing row: read an image
    in the site's S3 bucket with the site's own access, resolve a local /files or
    /private/files URL to its File doc, otherwise fetch an external http(s) URL
    directly. Returns None if it cannot be read.
    """
    if not url:
        return None
    block = _stored_block(url)
    if block:
        return block
    file_name = frappe.db.get_value("File", {"file_url": url}, "name")
    if file_name:
        return image_block_from_file(file_name)
    if url.startswith("http"):
        try:
            return fetch_image_block(url)
        except Exception:
            return None
    return None


def reference_source(url):
    """
    An Anthropic-style image `source` (base64) for a reference photo, resolving
    both a stored Frappe File url (e.g. '/files/x.jpg', which is not
    HTTP-fetchable on its own) by reading the File directly, and an external
    http(s) url by downloading it. Used to ground an image call in the real
    product photo.
    """
    block = _stored_block(url)
    if block:
        return block["source"]
    file_name = frappe.db.get_value("File", {"file_url": url}, "name")
    if file_name:
        block = image_block_from_file(file_name)
        if block:
            return block["source"]
    if not url.startswith(("http://", "https://")):
        # A stored path that could not be turned into a block is a missing file
        # or an undecodable format; fetching a site-relative path can only fail
        # with a misleading "No scheme supplied".
        raise ValueError(f"the stored file {url} is missing or is not a readable image")
    return fetch_image_block(url)["source"]


def data_uri(source):
    """A resolved `reference_source` as a data: URI, the form most image APIs want.

    Split out from `reference_data_uri` so a caller that already holds the source —
    because it also wants the raw bytes, as the compositing-only path does — does
    not have to read or download the photo a second time to get both.
    """
    return f"data:{source['media_type']};base64,{source['data']}"


def reference_data_uri(url):
    """`reference_source` as a data: URI, the form most image APIs want."""
    return data_uri(reference_source(url))


def public_image_url(url):
    """
    An absolute URL a third-party service can fetch for itself.

    See `alaiy_os.image_store.fetchable_url`: an image in the site's S3 bucket comes
    back presigned, a local File is moved to the bucket on first use and presigned (or,
    on a site with no bucket, expanded against the site URL), and a supplier CDN photo
    passes straight through.
    """
    from alaiy_os import image_store

    return image_store.fetchable_url(url)


#: Prefixes of photos rendered from a translated supplier photo; everything else this
#: connector saves (enhanced, cutout, lifestyle, worn) is generated.
_TRANSLATED_PREFIXES = ("listing-prepared",)


def save_public_image(prefix, content, mime, default_ext=".png"):
    """
    Store produced image bytes where the site keeps them and return the URL to record:
    the site's S3 bucket when it has one, else a standalone public File (see
    `alaiy_os.image_store.save`). The URL stored is the object's own, never a signed
    link -- those expire, and this URL is matched on and copied onto listings.

    Standalone (attached to no doctype) on purpose: an image a run produced shows
    up in that run's own output instead of mutating the product it came from, and
    the original photo is never overwritten — so a bad result is always
    recoverable.
    """
    from alaiy_os import image_store

    ext = MEDIA_TYPES_BY_MIME.get(mime, default_ext)
    file_name = f"{prefix}-{frappe.generate_hash(length=8)}{ext}"
    category = image_store.TRANSLATED if prefix in _TRANSLATED_PREFIXES else image_store.GENERATED
    return image_store.save(file_name, content, mime, category=category)


def follow_rehosted_urls(item_code, shopify_urls):
    """Point the product's enriched draft at the addresses Shopify now hosts its
    photos at. Returns how many row fields moved.

    A push uploads each /files/ photo to Shopify, and the products/update webhook
    then rewrites the listing's images to Shopify's own CDN urls - but the draft
    kept the local ones. Everything that pairs a draft row with a listing photo by
    url then stopped matching: the admin grid showed each published worn photo
    twice and kept offering Save for photos already live, trashing the extra
    tile removed the draft row but not the live photo, and reordering lost track
    of them. Rewritten here, the draft and the listing name each photo the same
    way again.

    Matched by file_stem. A row still waiting on a render (no `url`) keeps its
    `source_url`: that is what the job in flight will deliver against (see
    image_stage._match), and moving it would make the result land as a new row.
    Written straight to the rows, like image_stage's own state writes, so no
    document hook fires for what is only a change of address.
    """
    by_stem = {file_stem(url): url for url in shopify_urls if url}
    if not by_stem:
        return 0

    rows = frappe.get_all(
        "Shopify Enriched Listing Image",
        filters={"parent": item_code, "parenttype": "Shopify Enriched Listing"},
        fields=["name", "url", "source_url"],
    )
    moved = 0
    for row in rows:
        values = {}
        if row.url and by_stem.get(file_stem(row.url), row.url) != row.url:
            values["url"] = by_stem[file_stem(row.url)]
        if row.url and row.source_url and by_stem.get(file_stem(row.source_url), row.source_url) != row.source_url:
            values["source_url"] = by_stem[file_stem(row.source_url)]
        if values:
            frappe.db.set_value("Shopify Enriched Listing Image", row.name, values, update_modified=False)
            moved += len(values)
    return moved
