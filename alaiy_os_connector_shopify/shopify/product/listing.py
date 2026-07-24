"""
Shopify Product Listing resolver -- the single place every export read
routes through, so "effective title/description/price/images" and "which
variants push, at what price, is this product live" have exactly one
definition instead of being recomputed (and drifting) across canonical.py,
export.py, and variants.py.

Design:
- A Listing is 1:1 with a TEMPLATE Item and is the sole gate for whether the
  product is live on Shopify (`is_enabled`), fully replacing Item.sync_to_shopify.
- Listing content fields (title/description/price/images, and per-variant
  enable/price) are OVERRIDES: blank inherits the Item's current value at push
  time, so an un-diverged listing needs no copied data.

The Listing's sh_shopify_product_id / Shopify Listing Variant's
sh_shopify_variant_id are real, independently writable fields (not a
fetch_from view of Item). Every read site resolves the Listing's copy
first, falling back to Item's when blank -- both sides are kept in sync
on every write so the two never drift.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.pricing import _price_rate, _variant_price
from alaiy_os_connector_shopify.shopify.product.media import _item_images, _absolute_file_url


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_without_listing_query(doctype, txt, searchfield, start, page_len, filters):
    """Link-field query for the Listing's `item`: only template/simple Items
    (never variants) that don't already have a Shopify Product Listing -- so
    the picker can't offer a variant or an already-listed product (both of
    which would fail on save)."""
    like = f"%{txt}%"
    return frappe.db.sql(
        """
        SELECT i.name, i.item_name
        FROM `tabItem` i
        WHERE (i.variant_of IS NULL OR i.variant_of = '')
          AND NOT EXISTS (
              SELECT 1 FROM `tabShopify Product Listing` l WHERE l.item = i.name
          )
          AND (i.name LIKE %(txt)s OR i.item_name LIKE %(txt)s)
        ORDER BY i.modified DESC
        LIMIT %(start)s, %(page_len)s
        """,
        {"txt": like, "start": start, "page_len": page_len},
    )


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
    """
    Effective price for a variant on push:
    1. the variant row's variant_price override, else
    2. for a SIMPLE product (the template Item is its own single variant),
       the template-level listing_price override, else
    3. the Item Price on the selling list.
    None only when none of these has a value (caller must skip, never push 0).
    """
    row = _variant_rows(listing).get(variant_code)
    if row and row.variant_price:
        return float(row.variant_price)
    if listing and variant_code == listing.item and listing.listing_price:
        return float(listing.listing_price)
    return _variant_price(variant_code, settings)


# ── ID ownership ──────────────────────────────────────────────────────────
# Listing-based lookups, with the Item as fallback for any row that hasn't
# been dual-written to yet.

def item_by_variant_id(variant_id: str):
    """Shopify variant id -> the Alaiy OS variant Item code, via the Listing
    Variant row. Falls back to the Item-side lookup if the Listing doesn't
    have it (e.g. a row that hasn't been dual-written to). None if neither
    has it."""
    if not variant_id:
        return None
    row_parent = frappe.db.get_value(
        "Shopify Listing Variant", {"sh_shopify_variant_id": variant_id}, "item_variant")
    if row_parent:
        return row_parent
    return frappe.db.get_value("Item", {"sh_shopify_variant_id": variant_id}, "name")


def template_by_product_id(product_id: str):
    """Shopify product id -> the Alaiy OS template Item code, via the Listing.
    Falls back to the Item-side lookup the same way."""
    if not product_id:
        return None
    listing_item = frappe.db.get_value(
        "Shopify Product Listing", {"sh_shopify_product_id": product_id}, "item")
    if listing_item:
        return listing_item
    return frappe.db.get_value("Item", {"sh_shopify_product_id": product_id}, "name")


def set_product_id(template_name: str, product_id):
    """Dual-write: keep the Listing's copy in step with the Item's. No-op if
    there's no Listing for this template yet."""
    if frappe.db.exists("Shopify Product Listing", template_name):
        frappe.db.set_value("Shopify Product Listing", template_name,
                             "sh_shopify_product_id", product_id)


def variant_id_of_item(variant_item_code: str):
    """Shopify variant id for a variant Item code, Listing Variant row first,
    Item as fallback -- same direction as variant_shopify_id but without
    needing a Listing doc already loaded (order push callers only have the
    item_code)."""
    if not variant_item_code:
        return None
    row_id = frappe.db.get_value(
        "Shopify Listing Variant", {"item_variant": variant_item_code}, "sh_shopify_variant_id")
    if row_id:
        return row_id
    return frappe.db.get_value("Item", variant_item_code, "sh_shopify_variant_id")


def variant_shopify_id(listing, variant_item_code: str):
    """The Shopify variant id for a variant, Listing row first (real field
    now), falling back to the Item's own copy."""
    row = _variant_rows(listing).get(variant_item_code) if listing else None
    if row and row.sh_shopify_variant_id:
        return row.sh_shopify_variant_id
    return frappe.db.get_value("Item", variant_item_code, "sh_shopify_variant_id")


def set_variant_id(template_name: str, variant_item_code: str, variant_id):
    """Dual-write during the transition: mirror a variant id onto its Listing
    Variant row, if one exists. No-op otherwise (row gets it on next
    sync_listing_variants / ensure_listing pass)."""
    listing = get_listing(template_name)
    if not listing:
        return
    row = next((r for r in listing.variants if r.item_variant == variant_item_code), None)
    if row and row.sh_shopify_variant_id != variant_id:
        frappe.db.set_value("Shopify Listing Variant", row.name, "sh_shopify_variant_id", variant_id)


# ── Creation / upkeep ────────────────────────────────────────────────────────

def ensure_listing(template_name: str, default_enabled: int = 0):
    """
    Get-or-create the Listing for a template Item, built from the Item's
    current state (used on every inbound import so a Shopify-linked product
    always has a manageable Listing). Idempotent: an existing Listing is
    returned untouched, so re-running never duplicates or clobbers merchant
    edits. Returns None if the Item doesn't exist.

    is_enabled defaults to 0 -- an inbound import came FROM Shopify, so it must
    not auto-push back. The backfill patch passes the Item's old
    sync_to_shopify value to preserve which products were already syncing;
    nothing else reads that (now-removed) field.
    """
    existing = get_listing(template_name)
    if existing:
        return existing
    tmpl = frappe.db.get_value(
        "Item", template_name,
        ["name", "has_variants", "image", "sh_shopify_product_id", "sh_shopify_status"],
        as_dict=True,
    )
    if not tmpl:
        return None

    listing = frappe.new_doc("Shopify Product Listing")
    listing.item = tmpl.name
    listing.is_enabled = 1 if default_enabled else 0
    listing.sh_shopify_status = tmpl.sh_shopify_status or "Active"
    # sh_shopify_product_id is a real, independently-writable field (not a
    # fetch_from view) -- copy the Item's current value explicitly, or a
    # freshly-created Listing would start with a blank id.
    listing.sh_shopify_product_id = tmpl.sh_shopify_product_id or None
    # title/description/price left blank -> inherit from Item via the resolver.
    # Image/variant child rows are filled by the controller's before_insert
    # (fill_children_from_item) -- same path as a manually created listing.
    # Data mirrored straight from trusted existing Items -- skip the push echo.
    listing.flags.from_shopify_sync = True
    listing.insert(ignore_permissions=True)
    return listing


@frappe.whitelist()
def get_item_children(item):
    """Return a template Item's images + variant rows for the form's
    'Populate from Item' button (client fills the grids so they're visible
    before save). Mirrors fill_children_from_item, for the UI path."""
    tmpl = frappe.db.get_value("Item", item, ["name", "image", "has_variants"], as_dict=True)
    if not tmpl:
        return {"images": [], "variants": []}
    images = [
        {"image": url, "source": "Original", "sort_order": i}
        for i, url in enumerate(_template_image_urls(tmpl))
    ]
    variants = []
    if tmpl.has_variants:
        variants = [
            {"item_variant": v.name, "is_enabled": 1, "sh_shopify_variant_id": v.sh_shopify_variant_id or None}
            for v in frappe.get_all("Item", filters={"variant_of": tmpl.name},
                                     fields=["name", "sh_shopify_variant_id"])
        ]
    return {"images": images, "variants": variants}


def sync_listing_variants(template_name):
    """
    Add a Listing Variant row (enabled) for any Item variant of the template
    that isn't listed yet -- e.g. a variant added on a re-import, which the
    desk after_insert hook skips because it's flagged from_shopify_sync.
    Never REMOVES rows: disabling/dropping a variant is a deliberate,
    separate action (Listing edit or an inbound 'variant missing' reconcile),
    not something a routine re-sync should do. No-op without a listing.
    """
    listing = get_listing(template_name)
    if not listing:
        return
    listed = {r.item_variant for r in listing.variants}
    added = False
    for v in frappe.get_all("Item", filters={"variant_of": template_name},
                             fields=["name", "sh_shopify_variant_id"]):
        if v.name not in listed:
            # Copy the variant id explicitly (real field now, not fetch_from).
            listing.append("variants", {
                "item_variant": v.name, "is_enabled": 1,
                "sh_shopify_variant_id": v.sh_shopify_variant_id or None,
            })
            added = True
    if added:
        listing.flags.from_shopify_sync = True
        listing.save(ignore_permissions=True)


def apply_inbound_from_shopify(template_name, images=None, variant_prices=None, template_price=None):
    """
    Route inbound Shopify ABSTRACTED fields (images, per-variant price, and a
    simple product's template-level price) onto the Listing -- never the Item.
    Used by the re-import update path so a re-import can't clobber the Item's
    marketplace-agnostic defaults (same rule the webhook update path follows).
    Returns True if a Listing existed and was handled, False if none (caller
    then keeps the un-abstracted Item fallback). One save, from_shopify_sync so
    it doesn't echo a push.
    """
    listing = get_listing(template_name)
    if not listing:
        return False
    dirty = False

    if images:
        existing = [r.image for r in listing.images]
        if existing != images:
            listing.set("images", [])
            for order, url in enumerate(images):
                listing.append("images", {"image": url, "source": "Original", "sort_order": order})
            dirty = True

    if template_price is not None and float(listing.listing_price or 0) != float(template_price):
        listing.listing_price = template_price
        dirty = True

    for code, price in (variant_prices or {}).items():
        row = next((r for r in listing.variants if r.item_variant == code), None)
        if row and float(row.variant_price or 0) != float(price):
            row.variant_price = price
            dirty = True

    if dirty:
        listing.flags.from_shopify_sync = True
        listing.save(ignore_permissions=True)
    return True


def fill_children_from_item(listing):
    """
    Populate a listing's Images and Variants tables from its Item when they're
    empty -- so both a manually created listing (pick a template -> save) and
    an imported/backfilled one end up with the same rows. No-op for rows that
    already exist (won't clobber merchant edits or re-add on every save).
    """
    if not listing.item:
        return
    tmpl = frappe.db.get_value(
        "Item", listing.item, ["name", "image", "has_variants", "sh_shopify_product_id"], as_dict=True)
    if not tmpl:
        return

    # Real field now, not fetch_from -- copy explicitly if still blank.
    if not listing.sh_shopify_product_id and tmpl.sh_shopify_product_id:
        listing.sh_shopify_product_id = tmpl.sh_shopify_product_id

    if not listing.images:
        for order, url in enumerate(_template_image_urls(tmpl)):
            listing.append("images", {"image": url, "source": "Original", "sort_order": order})

    if not listing.variants and tmpl.has_variants:
        for v in frappe.get_all("Item", filters={"variant_of": tmpl.name},
                                 fields=["name", "sh_shopify_variant_id"]):
            listing.append("variants", {
                "item_variant": v.name, "is_enabled": 1,
                "sh_shopify_variant_id": v.sh_shopify_variant_id or None,
            })


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
