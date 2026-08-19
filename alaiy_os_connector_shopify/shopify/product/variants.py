"""
Variant-level helpers: weight/UOM maps, physical attribute apply, cost,
available qty, and the variant payload/canonical builders -- moved
verbatim from product_import.py and product_sync.py, unchanged.
"""

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.product.pricing import (
    _variant_price, _variant_compare_at_price, _variant_cost, _set_item_cost,
)
from alaiy_os_connector_shopify.shopify.product.masters import _ensure_uom
from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver
from alaiy_os_connector_shopify.shopify.product.media import _absolute_file_url

# Shopify's GraphQL WeightUnit enum <-> a plain Alaiy OS UOM name. Alaiy OS's
# weight_uom is a Link to UOM with no fixed seeded names, so these are
# auto-created (see _ensure_uom) rather than assumed to already exist.
_WEIGHT_UNIT_TO_UOM = {
    "GRAMS": "Gram", "KILOGRAMS": "Kg", "OUNCES": "Ounce", "POUNDS": "Pound",
}
_UOM_TO_WEIGHT_UNIT = {v: k for k, v in _WEIGHT_UNIT_TO_UOM.items()}

# Shopify's REST webhook payload uses a different, lowercase-abbreviation
# weight_unit string ("g"/"kg"/"oz"/"lb") than the GraphQL WeightUnit enum
# used everywhere else -- keeping this mapping separate rather than trying
# to normalize both into one dict avoids silently mixing up the two APIs'
# conventions.
_REST_WEIGHT_UNIT_TO_UOM = {
    "g": "Gram", "kg": "Kg", "oz": "Ounce", "lb": "Pound",
}


def _apply_variant_physical(doc, variant: dict):
    """
    Weight lives under Shopify's inventoryItem, not the variant itself.
    Sets plain Item fields -- call BEFORE insert. Unit cost is handled
    separately by _set_item_variant_cost since it requires the Item to
    already exist (Item Price validates item_code) -- call that one AFTER
    insert.
    """
    inv = variant.get("inventoryItem") or {}
    weight = (inv.get("measurement") or {}).get("weight")
    if weight and weight.get("value"):
        doc.weight_per_unit = flt(weight["value"])
        doc.weight_uom = _ensure_uom(_WEIGHT_UNIT_TO_UOM.get(weight.get("unit"), "Kg"))

    # Read-only mirrors of Shopify-side variant settings. Stored because each one
    # changes how a number from Shopify should be read: CONTINUE means stock can
    # go negative there, tracked=0 means an inventory push to this variant does
    # nothing at all, and requiresShipping=0 marks a digital product that should
    # never appear in a delivery.
    if variant.get("barcode"):
        doc.sh_barcode = variant["barcode"]
    if variant.get("inventoryPolicy"):
        doc.sh_inventory_policy = variant["inventoryPolicy"]
    if "tracked" in inv:
        doc.sh_tracked = 1 if inv.get("tracked") else 0
    if "requiresShipping" in inv:
        doc.sh_requires_shipping = 1 if inv.get("requiresShipping") else 0
    if "taxable" in variant:
        doc.sh_taxable = 1 if variant.get("taxable") else 0

    # These two already had custom fields and were PUSHED, but nothing ever read
    # them back -- the same one-directional gap as the status field. Only filled
    # when Shopify has a value, so a local edit is not wiped by a blank.
    if inv.get("harmonizedSystemCode"):
        doc.sh_harmonized_system_code = inv["harmonizedSystemCode"]
    country_code = inv.get("countryCodeOfOrigin")
    if country_code:
        country = frappe.db.get_value("Country", {"code": str(country_code).lower()}, "name")
        if country:
            doc.sh_country_of_origin = country


def _set_item_variant_cost(item_code: str, variant: dict, settings):
    cost = flt(((variant.get("inventoryItem") or {}).get("unitCost") or {}).get("amount") or 0)
    if cost > 0:
        _set_item_cost(item_code, cost, settings)


def _variant_available_qty(variant: dict) -> float:
    """
    Total available quantity across every location Shopify reports for
    this variant (up to the 3 the query requests -- asking for more than
    that per variant on a 100-variant product pushed Shopify's query
    cost over its 1000 hard limit, confirmed live). Taking only the
    first location undercounted every multi-location item's real total,
    on top of routing its opening stock into one shared default
    warehouse regardless of which real supplier it belongs to (see
    _variant_location_levels for the per-location split
    opening stock is now created from).
    """
    levels = ((variant.get("inventoryItem") or {}).get("inventoryLevels") or {}).get("nodes") or []
    total = 0
    for level in levels:
        quantities = level.get("quantities") or []
        if quantities:
            total += flt(quantities[0].get("quantity"))
    return total


def _variant_location_levels(variant: dict) -> list:
    """
    [(shopify_location_id, qty), ...] for this variant, one pair per real
    Shopify location it's stocked at -- lets opening stock be split into
    each location's own real per-supplier warehouse (via
    order.warehouse._resolve_warehouse_for_location, the same lookup the
    fulfillment/Delivery Note path already uses) instead of always
    landing in one shared default warehouse. A location with no
    legacyResourceId is skipped -- nothing to resolve a warehouse from.
    """
    levels = ((variant.get("inventoryItem") or {}).get("inventoryLevels") or {}).get("nodes") or []
    pairs = []
    for level in levels:
        location_id = ((level.get("location") or {}).get("legacyResourceId"))
        if not location_id:
            continue
        quantities = level.get("quantities") or []
        qty = flt(quantities[0].get("quantity")) if quantities else 0
        pairs.append((str(location_id), qty))
    return pairs


def _variant_inventory_item_payload(variant) -> dict:
    """inventoryItem sub-input for ProductVariantSetInput -- cost and
    weight live here, not flat on the variant."""
    payload = {}
    cost = _variant_cost(variant.item_code)
    if cost is not None and cost > 0:
        payload["cost"] = f"{cost:.2f}"
    if variant.get("weight_per_unit") and variant.get("weight_uom"):
        weight_unit = _UOM_TO_WEIGHT_UNIT.get(variant.weight_uom)
        if weight_unit:
            payload["measurement"] = {
                "weight": {"value": flt(variant.weight_per_unit), "unit": weight_unit}
            }
    if variant.get("sh_harmonized_system_code"):
        payload["harmonizedSystemCode"] = variant.sh_harmonized_system_code
    if variant.get("sh_country_of_origin"):
        # sh_country_of_origin is a Link to Country (full name); Shopify wants
        # the ISO 3166-1 alpha-2 code, which the Country doctype stores in
        # its own `code` field.
        country_code = frappe.db.get_value("Country", variant.sh_country_of_origin, "code")
        if country_code:
            payload["countryCodeOfOrigin"] = country_code.upper()
    return payload


def _variant_canonical(variant, settings, listing) -> dict:
    # Fingerprint-only dict (diffed to decide "needs push", never pushed
    # itself) -- safe to default missing prices to 0 here, unlike the
    # payload builders below which must skip instead of guessing.
    return {
        "sku": variant.item_code,
        "title": variant.item_name,
        "price": listing_resolver.variant_price(listing, variant.item_code, settings) or 0,
        "compare_at_price": _variant_compare_at_price(variant.item_code) or 0,
        "cost": _variant_cost(variant.item_code) or 0,
        "weight_per_unit": flt(variant.get("weight_per_unit") or 0),
        "weight_uom": variant.get("weight_uom") or "",
        "length": flt(variant.get("length") or 0),
        "width": flt(variant.get("width") or 0),
        "height": flt(variant.get("height") or 0),
        "attributes": [
            {"attribute": a.attribute, "value": a.attribute_value}
            for a in (variant.attributes or [])
        ],
        "barcode": variant.barcodes[0].barcode if variant.get("barcodes") else "",
        "variant_image": listing_resolver.effective_variant_image(listing, variant.item_code) or "",
        "harmonized_system_code": variant.get("sh_harmonized_system_code") or "",
        "country_of_origin": variant.get("sh_country_of_origin") or "",
    }


def _variant_set_payload(variant, settings, option_names: list, listing) -> dict:
    attrs = {a.attribute: a.attribute_value for a in (variant.attributes or [])}
    payload = {
        "sku": variant.item_code,
        "optionValues": [
            {"optionName": name, "name": attrs.get(name) or "Default"}
            for name in option_names
        ],
    }
    price = listing_resolver.variant_price(listing, variant.item_code, settings)
    if price is not None:
        payload["price"] = f"{price:.2f}"
    else:
        # No Item Price row for this item at all -- NOT the same as a real
        # price of 0. Skip the field (leave Shopify's price untouched)
        # rather than pushing an assumed 0 (same bug shape as the
        # missing-Bin-as-zero inventory incident). A missing price is an
        # expected data gap, not an error -- log quietly so it doesn't fill
        # the Error Log on every reconciliation of an unpriced item.
        frappe.logger().warning(
            f"Shopify: no local price for {variant.item_code}; skipping price push "
            "(no Item Price on the selling list)."
        )
    # Listing row's id first (real field now), falls back to Item's.
    shopify_variant_id = listing_resolver.variant_shopify_id(listing, variant.item_code)
    if shopify_variant_id:
        payload["id"] = f"gid://shopify/ProductVariant/{shopify_variant_id}"
    if variant.get("barcodes"):
        payload["barcode"] = variant.barcodes[0].barcode
    compare_at = _variant_compare_at_price(variant.item_code)
    if compare_at is not None and compare_at > 0:
        payload["compareAtPrice"] = f"{compare_at:.2f}"
    inventory_item = _variant_inventory_item_payload(variant)
    if inventory_item:
        payload["inventoryItem"] = inventory_item
    variant_image = listing_resolver.effective_variant_image(listing, variant.item_code)
    if variant_image:
        payload["file"] = {"originalSource": _absolute_file_url(variant_image), "contentType": "IMAGE"}
    return payload
