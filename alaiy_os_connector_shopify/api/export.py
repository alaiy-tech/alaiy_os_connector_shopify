# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
Export every Shopify Product Listing's data to CSV -- one row per variant,
same convention as Shopify's own product-export shape (a template's fields
repeat on every variant row, only the first row's copy matters for anything
product-level).

Reads through the SAME effective_* resolvers export.py/canonical.py push
from (listing.py) -- so what this shows is exactly what would actually be
sent to Shopify, not a raw possibly-blank override field that reads as
"nothing" when it really means "inherited from the Item".

Two paths:
  - export_listings_csv: synchronous, streams the file back directly. The
    list view only routes a hand-checked (deliberately bounded) selection
    here.
  - trigger_background_export: enqueues the build on the long queue,
    writes the result to a private File, and notifies the browser via
    realtime once ready -- used for an unfiltered All/Enabled/Disabled
    export, since a whole site's Listings (thealtomoda alone has 1,577)
    built inside one HTTP request/response cycle risks the web worker's
    request timeout.

`category` (sh_shopify_category / listing_category) is populated for very
few Items on most sites -- confirmed live on thealtomoda: only 6 of 896
templates have it set at all, vs 764 with sh_shopify_product_type. That's
a real data gap (category was never resolved against the taxonomy tree
for most imports), not an export bug -- `item_group` is included
alongside it as a fallback that's *always* set, so the export still shows
something to categorize by even where the real Shopify category is blank.
"""

import csv
import io

import frappe

from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver

_COLUMNS = [
    "item_code", "title", "description", "category", "item_group",
    "product_type", "brand", "tags", "seo_title", "seo_description",
    "is_enabled", "sh_shopify_status", "sh_shopify_product_id",
    "last_synced_at", "image_urls",
    "variant_item_code", "variant_attributes", "variant_price",
    "variant_sh_shopify_variant_id", "variant_image", "variant_is_enabled",
]


def _tags_for(item_name):
    return ", ".join(frappe.get_all(
        "Item Shopify Tag", filters={"parent": item_name}, pluck="shopify_tag"))


def _variant_attributes(variant_code):
    rows = frappe.get_all(
        "Item Variant Attribute", filters={"parent": variant_code},
        fields=["attribute", "attribute_value"], order_by="idx")
    return " | ".join(f"{r.attribute}: {r.attribute_value}" for r in rows if r.attribute_value)


def _variant_rows(listing, item, settings):
    """One row per sellable variant -- template's own children, or the
    template itself for a simple (no-variant) product."""
    if item.has_variants:
        codes = frappe.get_all("Item", filters={"variant_of": item.name}, pluck="name")
    else:
        codes = [item.name]

    listing_variants = {r.item_variant: r for r in (listing.variants if listing else [])}
    for code in codes:
        row = listing_variants.get(code)
        yield {
            "variant_item_code": code,
            "variant_attributes": _variant_attributes(code),
            "variant_price": listing_resolver.variant_price(listing, code, settings) or "",
            "variant_sh_shopify_variant_id": listing_resolver.variant_shopify_id(listing, code) or "",
            "variant_image": listing_resolver.effective_variant_image(listing, code) or "",
            "variant_is_enabled": (row.is_enabled if row else 1),
        }


def _listing_rows(listing_name, settings):
    listing = frappe.get_doc("Shopify Product Listing", listing_name)
    if not frappe.db.exists("Item", listing.item):
        return
    item = frappe.get_doc("Item", listing.item)
    seo = listing_resolver.effective_seo(listing, item)
    product_fields = {
        "item_code": item.name,
        "title": listing_resolver.effective_title(listing, item),
        "description": listing_resolver.effective_description(listing, item),
        "category": listing_resolver.effective_category(listing, item),
        "item_group": item.item_group or "",
        "product_type": listing_resolver.effective_product_type(listing, item),
        "brand": item.brand or "",
        "tags": _tags_for(item.name),
        "seo_title": seo["title"],
        "seo_description": seo["description"],
        "is_enabled": listing.is_enabled,
        "sh_shopify_status": listing.sh_shopify_status,
        "sh_shopify_product_id": listing.sh_shopify_product_id or "",
        "last_synced_at": listing.last_synced_at or "",
        "image_urls": " | ".join(listing_resolver.effective_images(listing, item, settings)),
    }
    for variant_fields in _variant_rows(listing, item, settings):
        yield {**product_fields, **variant_fields}


def _resolve_names(listing_names, only_enabled, only_disabled):
    filters = {}
    if only_enabled and frappe.utils.cint(only_enabled):
        filters["is_enabled"] = 1
    elif only_disabled and frappe.utils.cint(only_disabled):
        filters["is_enabled"] = 0
    if listing_names:
        names = frappe.parse_json(listing_names) if isinstance(listing_names, str) else listing_names
        filters["name"] = ["in", names]
    return frappe.get_all("Shopify Product Listing", filters=filters, pluck="name")


def _build_csv(names, settings):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for listing_name in names:
        try:
            for row in _listing_rows(listing_name, settings):
                writer.writerow(row)
        except Exception:
            frappe.log_error(
                title=f"Shopify listing export failed: {listing_name}",
                message=frappe.get_traceback(),
            )
    return buf.getvalue()


@frappe.whitelist()
def export_listings_csv(listing_names=None, only_enabled=None, only_disabled=None):
    """Synchronous direct download -- no size limit. The list view only
    routes a hand-checked (deliberately bounded) selection here; an
    unfiltered All/Enabled/Disabled export always goes through
    trigger_background_export instead, so this path never sees the whole
    site's Listings by accident."""
    settings = frappe.get_single("Shopify Connector Settings")
    names = _resolve_names(listing_names, only_enabled, only_disabled)

    frappe.response.filename = "shopify_listings_export.csv"
    frappe.response.filecontent = _build_csv(names, settings)
    frappe.response.type = "download"


def _run_background_export(listing_names, only_enabled, only_disabled, user):
    settings = frappe.get_single("Shopify Connector Settings")
    names = _resolve_names(listing_names, only_enabled, only_disabled)
    content = _build_csv(names, settings)

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": "shopify_listings_export.csv",
        "content": content,
        "is_private": 1,
    })
    file_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    frappe.publish_realtime(
        "shopify_listings_export_ready",
        {"file_url": file_doc.file_url, "row_count": len(names)},
        user=user,
    )


@frappe.whitelist()
def trigger_background_export(listing_names=None, only_enabled=None, only_disabled=None):
    """Enqueues the export on the long queue and notifies the browser via
    realtime with a download link once the File is ready -- the real path
    for exporting an entire site's Listings (thealtomoda alone has 1,577)."""
    frappe.enqueue(
        "alaiy_os_connector_shopify.api.export._run_background_export",
        queue="long",
        timeout=600,
        listing_names=listing_names,
        only_enabled=only_enabled,
        only_disabled=only_disabled,
        user=frappe.session.user,
    )
    return {"queued": True}
