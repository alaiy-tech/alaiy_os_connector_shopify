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


def _set_item_variant_cost(item_code: str, variant: dict, settings):
    cost = flt(((variant.get("inventoryItem") or {}).get("unitCost") or {}).get("amount") or 0)
    if cost > 0:
        _set_item_cost(item_code, cost, settings)


def _variant_available_qty(variant: dict) -> float:
    """
    Extract available quantity from the inventoryItem.inventoryLevels
    shape requested in _PRODUCTS_QUERY. Takes the first location Shopify
    returns -- fine for the common single-location shop this bulk import
    is aimed at; a multi-location shop's true total is a sum across
    inventory_sync.py's own inventory push, not this one-time import.
    """
    levels = ((variant.get("inventoryItem") or {}).get("inventoryLevels") or {}).get("nodes") or []
    if not levels:
        return 0
    quantities = levels[0].get("quantities") or []
    return flt(quantities[0].get("quantity")) if quantities else 0


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
    return payload


def _variant_canonical(variant, settings) -> dict:
    # Fingerprint-only dict (diffed to decide "needs push", never pushed
    # itself) -- safe to default missing prices to 0 here, unlike the
    # payload builders below which must skip instead of guessing.
    return {
        "sku": variant.item_code,
        "title": variant.item_name,
        "price": _variant_price(variant.item_code, settings) or 0,
        "compare_at_price": _variant_compare_at_price(variant.item_code) or 0,
        "cost": _variant_cost(variant.item_code) or 0,
        "weight_per_unit": flt(variant.get("weight_per_unit") or 0),
        "weight_uom": variant.get("weight_uom") or "",
        "attributes": [
            {"attribute": a.attribute, "value": a.attribute_value}
            for a in (variant.attributes or [])
        ],
        "barcode": variant.barcodes[0].barcode if variant.get("barcodes") else "",
    }


def _variant_set_payload(variant, settings, option_names: list) -> dict:
    attrs = {a.attribute: a.attribute_value for a in (variant.attributes or [])}
    payload = {
        "sku": variant.item_code,
        "optionValues": [
            {"optionName": name, "name": attrs.get(name) or "Default"}
            for name in option_names
        ],
    }
    price = _variant_price(variant.item_code, settings)
    if price is not None:
        payload["price"] = f"{price:.2f}"
    else:
        # No Item Price row for this item at all -- NOT the same as a real
        # price of 0. Skip the field (leave Shopify's price untouched)
        # rather than pushing an assumed 0 (same bug shape as the
        # missing-Bin-as-zero inventory incident).
        frappe.log_error(
            title=f"Shopify: no local price for {variant.item_code}, skipping price push",
            message="Item Price row missing on the configured selling price list.",
        )
    if variant.get("sh_shopify_variant_id"):
        payload["id"] = f"gid://shopify/ProductVariant/{variant.sh_shopify_variant_id}"
    if variant.get("barcodes"):
        payload["barcode"] = variant.barcodes[0].barcode
    compare_at = _variant_compare_at_price(variant.item_code)
    if compare_at is not None and compare_at > 0:
        payload["compareAtPrice"] = f"{compare_at:.2f}"
    inventory_item = _variant_inventory_item_payload(variant)
    if inventory_item:
        payload["inventoryItem"] = inventory_item
    return payload
