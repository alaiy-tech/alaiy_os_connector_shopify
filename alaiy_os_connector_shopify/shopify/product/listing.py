"""
Shopify Product Listing resolver -- the single place every export read
routes through, so "effective title/description/price/images" and "which
variants push, at what price, is this product live" have exactly one
definition instead of being recomputed (and drifting) across canonical.py,
export.py, and variants.py.

Design (per the 21-07 listings decision):
- A Listing is 1:1 with a TEMPLATE Item and is the sole gate for whether the
  product is live on Shopify (`is_enabled`), fully replacing Item.sync_to_shopify.
- Listing content fields (title/description/price/images, and per-variant
  enable/price) are OVERRIDES: blank inherits the Item's current value at push
  time, so an un-diverged listing needs no copied data.
- The Shopify product/variant ids still physically live on Item this phase
  (relocating them is the separately-gated id-migration work) -- this module
  deliberately does NOT touch them.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.pricing import _price_rate, _variant_price
from alaiy_os_connector_shopify.shopify.product.media import _item_images, _absolute_file_url


def _template_name(item) -> str:
    """The template a Listing would be keyed to for any Item (self if simple)."""
    return item.variant_of or item.name


def get_listing(template_name: str):
    """The Shopify Product Listing for a template Item, or None. Named after
    the template Item (autoname field:item), so this is a direct get."""
    if not template_name or not frappe.db.exists("Shopify Product Listing", template_name):
        return None
    return frappe.get_doc("Shopify Product Listing", template_name)


def get_listing_for(item):
    return get_listing(_template_name(item))


def is_enabled(item) -> bool:
    """
    Replaces item_hooks._sync_enabled: the product is live on Shopify iff its
    template has an enabled Listing AND the template Item isn't disabled.
    No Listing at all -> not live (nothing pushes until a Listing exists).
    """
    template_name = _template_name(item)
    listing = get_listing(template_name)
    if not listing or not listing.is_enabled:
        return False
    return not frappe.db.get_value("Item", template_name, "disabled")


# ── Effective (post-fallback) template content ───────────────────────────────

def effective_title(listing, item) -> str:
    return (listing.listing_title or "").strip() or item.item_name


def effective_description(listing, item) -> str:
    return listing.listing_description or item.description or ""


def effective_price(listing, item, settings):
    """Template-level price for a simple product. None only when neither the
    Listing nor an Item Price row has a value -- callers must skip (never push
    an assumed 0), same rule as pricing.py."""
    if listing and listing.listing_price:
        return float(listing.listing_price)
    return _price_rate(item.item_code, settings.sh_selling_price_list or "Standard Selling")


def effective_images(listing, item, settings) -> list:
    """Listing image rows (by sort_order) as absolute URLs; fall back to the
    Item image/slideshow when the Listing has no image rows."""
    if listing and listing.images:
        rows = sorted(listing.images, key=lambda r: (r.sort_order or 0))
        return [_absolute_file_url(r.image) for r in rows if r.image]
    return _item_images(item, settings)


# ── Variants ─────────────────────────────────────────────────────────────────

def _variant_rows(listing) -> dict:
    """{variant Item code: Shopify Listing Variant row} for a listing."""
    return {r.item_variant: r for r in (listing.variants if listing else [])}


def enabled_variant_names(template_name: str) -> list:
    """
    Variant Item names to include in the push: those whose Shopify Listing
    Variant row is enabled and whose Item isn't disabled. Replaces
    export._variants_of's Item.sync_to_shopify filter. A variant with no
    Listing Variant row is treated as not included (never pushed).
    """
    listing = get_listing(template_name)
    if not listing:
        return []
    enabled = [r.item_variant for r in listing.variants if r.is_enabled]
    if not enabled:
        return []
    return frappe.get_all(
        "Item",
        filters={"name": ["in", enabled], "disabled": 0},
        pluck="name",
    )


def variant_price(listing, variant_code: str, settings):
    """Per-variant price override, falling back to the Item Price lookup when
    blank. None only when neither has a value."""
    row = _variant_rows(listing).get(variant_code)
    if row and row.variant_price:
        return float(row.variant_price)
    return _variant_price(variant_code, settings)


# ── Creation / upkeep ────────────────────────────────────────────────────────

def ensure_listing(template_name: str):
    """
    Get-or-create the Listing for a template Item, built from the Item's
    current state (used by the backfill patch AND on every inbound import so a
    Shopify-linked product always has a manageable Listing). Idempotent: an
    existing Listing is returned untouched, so re-running never duplicates or
    clobbers merchant edits. Returns None if the Item doesn't exist.
    """
    existing = get_listing(template_name)
    if existing:
        return existing
    tmpl = frappe.db.get_value(
        "Item", template_name,
        ["name", "has_variants", "image", "sync_to_shopify",
         "sh_shopify_product_id", "sh_shopify_status"],
        as_dict=True,
    )
    if not tmpl:
        return None

    listing = frappe.new_doc("Shopify Product Listing")
    listing.item = tmpl.name
    listing.is_enabled = 1 if tmpl.sync_to_shopify else 0
    listing.sh_shopify_product_id = tmpl.sh_shopify_product_id or None
    listing.sh_shopify_status = tmpl.sh_shopify_status or "Active"
    # title/description/price left blank -> inherit from Item via the resolver.

    for order, url in enumerate(_template_image_urls(tmpl)):
        listing.append("images", {"image": url, "source": "Original", "sort_order": order})

    if tmpl.has_variants:
        for v in frappe.get_all(
            "Item", filters={"variant_of": tmpl.name},
            fields=["name", "sync_to_shopify", "sh_shopify_variant_id"],
        ):
            listing.append("variants", {
                "item_variant": v.name,
                "is_enabled": 1 if v.sync_to_shopify else 0,
                "sh_shopify_variant_id": v.sh_shopify_variant_id or None,
            })

    # Data mirrored straight from trusted existing Items -- skip the push echo
    # (this is a data provisioning step, not a merchant edit).
    listing.flags.from_shopify_sync = True
    listing.insert(ignore_permissions=True)
    return listing


def _template_image_urls(tmpl) -> list:
    urls = []
    if tmpl.image:
        urls.append(tmpl.image)
    if not frappe.get_meta("Item").has_field("slideshow"):
        return urls
    slideshow_name = frappe.db.get_value("Item", tmpl.name, "slideshow")
    if slideshow_name and frappe.db.exists("Website Slideshow", slideshow_name):
        for row in frappe.get_doc("Website Slideshow", slideshow_name).slideshow_items:
            if row.image and row.image not in urls:
                urls.append(row.image)
    return urls
