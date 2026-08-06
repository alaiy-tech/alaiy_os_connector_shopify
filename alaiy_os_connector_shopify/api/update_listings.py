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

Every field actually changed is recorded as an explicit before -> after
diff line on the Sync Log (log_messages) -- applies directly, no separate
dry-run step. The diff log is the audit trail: what changed, from what, to
what, per item.
"""

import csv
import io

import frappe
from frappe.utils import cint, flt

from alaiy_os_connector_shopify.shopify.product.tags import _set_item_tags

# frappe.utils.flt()/cint() silently coerce unparseable input to 0 instead of
# raising -- confirmed a real risk, not hypothetical: a typo'd price
# ("313.5x") or status would otherwise silently write 0/garbage instead of
# failing. These wrappers reject anything that isn't a real number/boolean/
# known status, reporting it as a warning and leaving the field untouched
# rather than trusting flt/cint's silent fallback.
_VALID_STATUSES = {"Active", "Draft", "Archived"}
_TRUE_VALUES = {"1", "true", "yes"}
_FALSE_VALUES = {"0", "false", "no"}


def _parse_number(raw):
    """Real number or None -- unlike flt(), never silently returns 0 for
    unparseable input."""
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _parse_bool01(raw):
    """0/1 or None -- unlike cint(), rejects anything that isn't a
    recognized true/false spelling instead of silently defaulting to 0."""
    value = str(raw).strip().lower()
    if value in _TRUE_VALUES:
        return 1
    if value in _FALSE_VALUES:
        return 0
    return None


# Wrong-file detection: a CSV missing item_code entirely used to parse
# "successfully" into zero groups and silently do nothing -- no error, no
# warning, just a report showing 0 updated with no explanation why.
# Confirmed as a real gap, not hypothetical: nothing validated the header
# before processing it.
_REQUIRED_COLUMN = "item_code"
_MIN_RECOGNIZED_COLUMNS = 3


def _validate_header(fieldnames):
    fieldnames = set(fieldnames or [])
    if _REQUIRED_COLUMN not in fieldnames:
        raise ValueError(
            f"This file has no '{_REQUIRED_COLUMN}' column -- it doesn't look like a "
            "Listings export/update file. Download 'Export Listings (CSV)' first and "
            "use that as your starting point."
        )
    from alaiy_os_connector_shopify.api.export import _COLUMNS as EXPORT_COLUMNS
    overlap = fieldnames & set(EXPORT_COLUMNS)
    if len(overlap) < _MIN_RECOGNIZED_COLUMNS:
        raise ValueError(
            f"Only {len(overlap)} of the expected columns were recognized in this "
            "file's header -- it doesn't look like a Listings export/update file. "
            "Download 'Export Listings (CSV)' first and use that as your starting point."
        )


def _group_rows_by_item(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text))
    _validate_header(reader.fieldnames)
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


def _set_and_log(doc, fieldname, new_value, label, changes):
    """Set doc.fieldname to new_value and record a before -> after diff line,
    but only if the value actually changed -- an unchanged field (CSV value
    happens to match what's already there) isn't a real change worth
    logging."""
    old_value = doc.get(fieldname)
    if (old_value or "") == (new_value or ""):
        return
    doc.set(fieldname, new_value)
    changes.append(f"{label}: {old_value!r} -> {new_value!r}")


def _apply_images(listing, image_urls_value, changes, label):
    urls = [u.strip() for u in image_urls_value.split("|") if u.strip()]
    if not urls:
        return
    old_urls = [r.image for r in (listing.images or [])]
    if old_urls == urls:
        return
    listing.set("images", [
        {"image": u, "source": "Original", "sort_order": i} for i, u in enumerate(urls)
    ])
    changes.append(f"{label}.images: {old_urls!r} -> {urls!r}")


def _apply_metafields(listing, metafields_value, changes, label):
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
    if not rows:
        return
    old_pairs = sorted((m.namespace, m.key, m.value) for m in (listing.metafields or []))
    new_pairs = sorted((r["namespace"], r["key"], r["value"]) for r in rows)
    if old_pairs == new_pairs:
        return
    listing.set("metafields", rows)
    changes.append(f"{label}.metafields: {len(old_pairs)} field(s) -> {len(new_pairs)} field(s)")


def _apply_product_fields(item, listing, row, report):
    changes = report["changes"]

    brand = (row.get("brand") or "").strip()
    if brand:
        _set_and_log(item, "brand", brand, f"{item.name}.brand", changes)

    tags_value = (row.get("tags") or "").strip()
    if tags_value:
        new_tags = sorted(t.strip() for t in tags_value.split(",") if t.strip())
        old_tags = sorted(r.shopify_tag for r in (item.get("sh_shopify_tags") or []))
        if new_tags != old_tags:
            _set_item_tags(item, new_tags)
            changes.append(f"{item.name}.tags: {old_tags!r} -> {new_tags!r}")

    title = (row.get("title") or "").strip()
    if title:
        _set_and_log(listing, "listing_title", title, f"{item.name}.title", changes)

    description = row.get("description")
    if description and description.strip():
        _set_and_log(listing, "listing_description", description, f"{item.name}.description", changes)

    product_type = (row.get("product_type") or "").strip()
    if product_type:
        _set_and_log(listing, "listing_product_type", product_type, f"{item.name}.product_type", changes)

    category_name = (row.get("category") or "").strip()
    if category_name:
        category_doc = frappe.db.get_value(
            "Shopify Category", {"shopify_category_name": category_name}, "name")
        if category_doc:
            _set_and_log(listing, "listing_category", category_doc, f"{item.name}.category", changes)
        else:
            # Never fabricate a disconnected taxonomy node from a plain name
            # -- that produced a tree of junk categories in production once
            # already. Leave the field untouched and report it instead.
            report["warnings"].append(f"{item.name}: category '{category_name}' not found -- left unchanged")

    seo_title = (row.get("seo_title") or "").strip()
    if seo_title:
        _set_and_log(listing, "listing_seo_title", seo_title, f"{item.name}.seo_title", changes)
    seo_description = row.get("seo_description")
    if seo_description and seo_description.strip():
        _set_and_log(listing, "listing_seo_description", seo_description, f"{item.name}.seo_description", changes)

    is_enabled_raw = row.get("is_enabled")
    if is_enabled_raw not in (None, ""):
        parsed = _parse_bool01(is_enabled_raw)
        if parsed is None:
            report["warnings"].append(
                f"{item.name}: is_enabled value {is_enabled_raw!r} isn't 0/1/true/false -- left unchanged")
        else:
            _set_and_log(listing, "is_enabled", parsed, f"{item.name}.is_enabled", changes)

    status = (row.get("sh_shopify_status") or "").strip()
    if status:
        if status not in _VALID_STATUSES:
            report["warnings"].append(
                f"{item.name}: sh_shopify_status {status!r} isn't one of {sorted(_VALID_STATUSES)} -- left unchanged")
        else:
            _set_and_log(listing, "sh_shopify_status", status, f"{item.name}.sh_shopify_status", changes)

    images_value = (row.get("image_urls") or "").strip()
    if images_value:
        _apply_images(listing, images_value, changes, item.name)

    metafields_value = (row.get("metafields") or "").strip()
    if metafields_value:
        _apply_metafields(listing, metafields_value, changes, item.name)


def _apply_variant_fields(listing, variant_rows, report):
    changes = report["changes"]
    listing_variants = {r.item_variant: r for r in (listing.variants or [])}
    for vr in variant_rows:
        variant_code = (vr.get("variant_item_code") or "").strip()
        if not variant_code:
            continue
        if not frappe.db.exists("Item", variant_code):
            report["warnings"].append(
                f"{variant_code}: Item not found -- new variants aren't created here, use product import")
            continue
        row = listing_variants.get(variant_code)
        if not row:
            report["warnings"].append(
                f"{variant_code}: no Listing Variant row yet -- run 'Populate from Item' on the Listing first")
            continue

        price_raw = vr.get("variant_price")
        if price_raw not in (None, ""):
            new_price = _parse_number(price_raw)
            if new_price is None:
                report["warnings"].append(
                    f"{variant_code}: variant_price {price_raw!r} isn't a number -- left unchanged")
            elif flt(row.variant_price) != new_price:
                changes.append(f"{variant_code}.variant_price: {row.variant_price!r} -> {new_price!r}")
                row.variant_price = new_price

        image = (vr.get("variant_image") or "").strip()
        if image and image != row.variant_image:
            changes.append(f"{variant_code}.variant_image: {row.variant_image!r} -> {image!r}")
            row.variant_image = image

        enabled_raw = vr.get("variant_is_enabled")
        if enabled_raw not in (None, ""):
            new_enabled = _parse_bool01(enabled_raw)
            if new_enabled is None:
                report["warnings"].append(
                    f"{variant_code}: variant_is_enabled {enabled_raw!r} isn't 0/1/true/false -- left unchanged")
            elif cint(row.is_enabled) != new_enabled:
                changes.append(f"{variant_code}.variant_is_enabled: {row.is_enabled!r} -> {new_enabled!r}")
                row.is_enabled = new_enabled


def _apply_group(item_code, group, report):
    if not frappe.db.exists("Item", item_code):
        report["skipped"].append(f"{item_code}: Item not found -- new products are created via product import, not this update")
        return
    if not frappe.db.exists("Shopify Product Listing", item_code):
        report["skipped"].append(f"{item_code}: no Shopify Product Listing exists for this Item yet")
        return

    item = frappe.get_doc("Item", item_code)
    listing = frappe.get_doc("Shopify Product Listing", item_code)

    before = len(report["changes"])
    _apply_product_fields(item, listing, group["product_row"], report)
    _apply_variant_fields(listing, group["variant_rows"], report)

    if len(report["changes"]) == before:
        report["unchanged"].append(item_code)
        return

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


def _run_update_listings(csv_content, user):
    from alaiy_os_connector_shopify.shopify.sync_guard import load_or_create_log

    log = load_or_create_log("update_listings", "manual")
    log.status = "running"
    log.save(ignore_permissions=True)
    frappe.db.commit()

    report = {"updated": [], "unchanged": [], "skipped": [], "warnings": [], "changes": [], "error": None}

    try:
        # Header validation happens INSIDE the try -- a wrong file (missing
        # item_code, or a totally unrelated CSV) must fail loudly with a
        # clear message, not crash unhandled or, worse, "succeed" having
        # silently processed zero rows.
        order, groups = _group_rows_by_item(csv_content)

        for i, item_code in enumerate(order):
            try:
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
        # The full before -> after diff is the actual audit trail -- capped
        # so one huge file doesn't blow past the field's own storage limit,
        # not because the detail isn't wanted.
        log.log_messages = frappe.as_json({
            "updated": report["updated"][:500],
            "unchanged": report["unchanged"][:500],
            "skipped": report["skipped"][:500],
            "warnings": report["warnings"][:500],
            "changes": report["changes"][:2000],
        })[:100000]
        log.status = "success"
        log.finished_at = frappe.utils.now_datetime()
        log.save(ignore_permissions=True)
        frappe.db.commit()
    except ValueError as e:
        # A validation error (wrong file) -- clear, user-facing message, not
        # a stack trace. Still recorded on the log for the audit trail.
        report["error"] = str(e)
        log.status = "failed"
        log.error_message = str(e)
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
                "updated_count": len(report["updated"]),
                "unchanged_count": len(report["unchanged"]),
                "skipped_count": len(report["skipped"]),
                "warning_count": len(report["warnings"]),
                "change_count": len(report["changes"]),
                "error": report["error"],
                "log_name": log.name,
            },
            user=user,
        )


@frappe.whitelist()
def trigger_update_listings(file_url):
    """file_url: a private File already uploaded (e.g. via the list view's
    file picker). Enqueued on the long queue -- same size reasoning as the
    export: a whole-site update file has no place running inside one
    request/response cycle. Applies directly, no separate dry-run step --
    every change is logged as an explicit before -> after diff on the
    resulting Shopify Sync Log instead."""
    file_doc = frappe.get_doc("File", {"file_url": file_url})
    csv_content = file_doc.get_content()
    if isinstance(csv_content, bytes):
        csv_content = csv_content.decode("utf-8-sig")

    frappe.enqueue(
        "alaiy_os_connector_shopify.api.update_listings._run_update_listings",
        queue="long",
        timeout=1200,
        csv_content=csv_content,
        user=frappe.session.user,
    )
    return {"queued": True}
