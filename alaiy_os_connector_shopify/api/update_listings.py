# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
Update existing Shopify Product Listings/Items from a CSV in the exact same
shape export.py produces -- the reverse direction of that export, update
only. Creating brand-new products is explicitly out of scope here: that
happens through the existing product-import path (upload.py /
import_shopify_generation.py), which already auto-creates a Shopify Product
Listing for a new Item (listing.py's ensure_listing/fill_children_from_item).
So a row whose item_code doesn't already exist is skipped and reported, not
created.

Writes go to the same place each field was READ from in export.py:
  - title/description/product_type/category/SEO/is_enabled/status/images/
    metafields -> the Listing's own override fields (never the Item directly
    -- Item stays the merchant's own default, the Listing is the per-channel
    copy, same architecture as everywhere else in this connector).
  - brand/tags -> the Item (that's where export.py reads them from).
  - variant price/image/enabled -> the matching Shopify Listing Variant row.

Deliberately NOT written, even if present in the CSV:
  - sh_shopify_product_id, variant_sh_shopify_variant_id, last_synced_at,
    category_id, item_group -- connector-managed/derived, never
    user-editable via import.
  - variant_attributes -- structural Item Variant Attribute data, not a
    Listing override. Editing it here would silently rename/redefine the
    variant's own identity instead of updating a channel-specific value.
    Attribute changes are an Item-variant concern, out of scope for a
    listing update.

Blank cell convention, same as the supplier CSV format: blank means "leave
unchanged", not "clear this field".
"""

import csv
import io

import frappe
from frappe.utils import cint, flt

from alaiy_os_connector_shopify.shopify.product.tags import _set_item_tags


def _group_rows_by_item(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text))
    order = []
    groups = {}
    for row in reader:
        code = (row.get("item_code") or "").strip()
        if not code:
            continue
        if code not in groups:
            groups[code] = {"product_row": row, "variant_rows": []}
            order.append(code)
        groups[code]["variant_rows"].append(row)
    return order, groups


def _apply_images(listing, image_urls_value):
    urls = [u.strip() for u in image_urls_value.split("|") if u.strip()]
    if not urls:
        return
    listing.set("images", [
        {"image": u, "source": "Original", "sort_order": i} for i, u in enumerate(urls)
    ])


def _apply_metafields(listing, metafields_value):
    rows = []
    for part in metafields_value.split("|"):
        part = part.strip()
        key_part, sep, value = part.partition("=")
        if not sep or "." not in key_part:
            continue
        namespace, _, key = key_part.partition(".")
        namespace, key, value = namespace.strip(), key.strip(), value.strip()
        if namespace and key:
            rows.append({"namespace": namespace, "key": key,
                         "type": "single_line_text_field", "value": value})
    if rows:
        listing.set("metafields", rows)


def _apply_product_fields(item, listing, row, warnings):
    brand = (row.get("brand") or "").strip()
    if brand:
        item.brand = brand

    tags_value = (row.get("tags") or "").strip()
    if tags_value:
        _set_item_tags(item, [t.strip() for t in tags_value.split(",") if t.strip()])

    title = (row.get("title") or "").strip()
    if title:
        listing.listing_title = title

    description = row.get("description")
    if description and description.strip():
        listing.listing_description = description

    product_type = (row.get("product_type") or "").strip()
    if product_type:
        listing.listing_product_type = product_type

    category_name = (row.get("category") or "").strip()
    if category_name:
        category_doc = frappe.db.get_value(
            "Shopify Category", {"shopify_category_name": category_name}, "name")
        if category_doc:
            listing.listing_category = category_doc
        else:
            # Never fabricate a disconnected taxonomy node from a plain name
            # -- that produced a tree of junk categories in production once
            # already. Leave the field untouched and report it instead.
            warnings.append(f"{item.name}: category '{category_name}' not found -- left unchanged")

    seo_title = (row.get("seo_title") or "").strip()
    if seo_title:
        listing.listing_seo_title = seo_title
    seo_description = row.get("seo_description")
    if seo_description and seo_description.strip():
        listing.listing_seo_description = seo_description

    is_enabled = row.get("is_enabled")
    if is_enabled not in (None, ""):
        listing.is_enabled = cint(is_enabled)

    status = (row.get("sh_shopify_status") or "").strip()
    if status:
        listing.sh_shopify_status = status

    images_value = (row.get("image_urls") or "").strip()
    if images_value:
        _apply_images(listing, images_value)

    metafields_value = (row.get("metafields") or "").strip()
    if metafields_value:
        _apply_metafields(listing, metafields_value)


def _apply_variant_fields(listing, variant_rows, warnings):
    listing_variants = {r.item_variant: r for r in (listing.variants or [])}
    for vr in variant_rows:
        variant_code = (vr.get("variant_item_code") or "").strip()
        if not variant_code:
            continue
        if not frappe.db.exists("Item", variant_code):
            warnings.append(
                f"{variant_code}: Item not found -- new variants aren't created here, use product import")
            continue
        row = listing_variants.get(variant_code)
        if not row:
            warnings.append(
                f"{variant_code}: no Listing Variant row yet -- run 'Populate from Item' on the Listing first")
            continue

        price = vr.get("variant_price")
        if price not in (None, ""):
            row.variant_price = flt(price)

        image = (vr.get("variant_image") or "").strip()
        if image:
            row.variant_image = image

        enabled = vr.get("variant_is_enabled")
        if enabled not in (None, ""):
            row.is_enabled = cint(enabled)


def _apply_group(item_code, group, report):
    if not frappe.db.exists("Item", item_code):
        report["skipped"].append(f"{item_code}: Item not found -- new products are created via product import, not this update")
        return
    if not frappe.db.exists("Shopify Product Listing", item_code):
        report["skipped"].append(f"{item_code}: no Shopify Product Listing exists for this Item yet")
        return

    item = frappe.get_doc("Item", item_code)
    listing = frappe.get_doc("Shopify Product Listing", item_code)

    _apply_product_fields(item, listing, group["product_row"], report["warnings"])
    _apply_variant_fields(listing, group["variant_rows"], report["warnings"])

    item.flags.ignore_permissions = True
    listing.flags.ignore_permissions = True
    # Set BEFORE save -- this update originated FROM a CSV, not from Shopify
    # echoing its own state back, but it still shouldn't trigger a push as a
    # side effect of the import itself. Pushing is a separate, deliberate
    # step (the existing "Push" action), same discipline as every other
    # bulk-write path in this connector.
    listing.flags.from_shopify_sync = True
    item.save()
    listing.save()
    report["updated"].append(item_code)


def _run_update_listings(csv_content, dry_run, user):
    from alaiy_os_connector_shopify.shopify.sync_guard import load_or_create_log

    log = load_or_create_log("update_listings", "manual")
    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    order, groups = _group_rows_by_item(csv_content)
    report = {"updated": [], "skipped": [], "warnings": []}

    try:
        for i, item_code in enumerate(order):
            try:
                if dry_run:
                    # Dry run validates existence/lookups without writing --
                    # same skip/warning checks, no save() calls.
                    group = groups[item_code]
                    if not frappe.db.exists("Item", item_code) or not frappe.db.exists("Shopify Product Listing", item_code):
                        report["skipped"].append(f"{item_code}: would be skipped (not found)")
                    else:
                        report["updated"].append(f"{item_code} (dry run)")
                else:
                    _apply_group(item_code, groups[item_code], report)
                    frappe.db.commit()
            except Exception:
                report["skipped"].append(f"{item_code}: failed -- see Error Log")
                frappe.log_error(
                    title=f"Shopify listing update failed: {item_code}",
                    message=frappe.get_traceback(),
                )

            if (i + 1) % 20 == 0:
                log.items_processed = i + 1
                log.items_created = len(report["updated"])
                log.items_failed = len(report["skipped"])
                log.save(ignore_permissions=True)
                frappe.db.commit()

        log.items_processed = len(order)
        log.items_created = len(report["updated"])
        log.items_failed = len(report["skipped"])
        log.log_messages = frappe.as_json({
            "dry_run": bool(dry_run),
            "updated": report["updated"][:200],
            "skipped": report["skipped"][:200],
            "warnings": report["warnings"][:200],
        })[:100000]
        log.status = "success"
        log.finished_at = frappe.utils.now_datetime()
        log.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        log.status = "failed"
        log.error_message = frappe.get_traceback()[:2000]
        log.finished_at = frappe.utils.now_datetime()
        log.save(ignore_permissions=True)
        frappe.db.commit()
        raise
    finally:
        frappe.publish_realtime(
            "shopify_update_listings_done",
            {
                "dry_run": bool(dry_run),
                "updated_count": len(report["updated"]),
                "skipped_count": len(report["skipped"]),
                "warning_count": len(report["warnings"]),
                "log_name": log.name,
            },
            user=user,
        )


@frappe.whitelist()
def trigger_update_listings(file_url, dry_run=1):
    """file_url: a private File already uploaded (e.g. via the list view's
    file picker). Enqueued on the long queue -- same size reasoning as the
    export: a whole-site update file has no place running inside one
    request/response cycle."""
    file_doc = frappe.get_doc("File", {"file_url": file_url})
    csv_content = file_doc.get_content()
    if isinstance(csv_content, bytes):
        csv_content = csv_content.decode("utf-8-sig")

    frappe.enqueue(
        "alaiy_os_connector_shopify.api.update_listings._run_update_listings",
        queue="long",
        timeout=1200,
        csv_content=csv_content,
        dry_run=cint(dry_run),
        user=frappe.session.user,
    )
    return {"queued": True}
