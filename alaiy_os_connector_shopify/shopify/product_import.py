"""
Compatibility re-export shim.

This module's actual content was split into alaiy_os_connector_shopify/
shopify/product/{queries,masters,pricing,variants,stock,media,taxonomy,
tags,importer}.py as part of a pure architectural refactor -- no
behavior changed. Every name that used to live directly in this file is
re-exported here unchanged, so existing dotted-path references (hooks.py,
api/sync.py, other modules' inline imports, tests) keep working exactly
as before without modification.
"""

from alaiy_os_connector_shopify.shopify.product.queries import (
    _PRODUCTS_COUNT_QUERY,
    _PRODUCTS_QUERY,
)
from alaiy_os_connector_shopify.shopify.product.masters import (
    _ensure_brand,
    _ensure_item_group,
    _make_attribute_abbr,
    _ensure_item_attribute,
    _ensure_uom,
    _ensure_cost_center,
)
from alaiy_os_connector_shopify.shopify.product.pricing import (
    _upsert_item_price,
    _ensure_price_list,
    _set_item_price,
    _COMPARE_AT_PRICE_LIST,
    _set_item_compare_at_price,
    _COST_PRICE_LIST,
    _set_item_cost,
)
from alaiy_os_connector_shopify.shopify.product.variants import (
    _WEIGHT_UNIT_TO_UOM,
    _UOM_TO_WEIGHT_UNIT,
    _REST_WEIGHT_UNIT_TO_UOM,
    _apply_variant_physical,
    _set_item_variant_cost,
    _variant_available_qty,
)
from alaiy_os_connector_shopify.shopify.product.stock import (
    _default_warehouse_row,
    _set_opening_stock,
)
from alaiy_os_connector_shopify.shopify.product.media import (
    _download_to_file,
    _set_item_image,
    _set_item_slideshow,
)
from alaiy_os_connector_shopify.shopify.product.taxonomy import (
    ensure_shopify_category,
)
from alaiy_os_connector_shopify.shopify.product.tags import (
    _normalize_tags,
    _set_item_tags,
)
from alaiy_os_connector_shopify.shopify.product.importer import (
    run_full_product_import,
    _wipe_all_items,
    _import_product,
    _apply_existing_variant_content,
    _apply_existing_template_content,
    _import_simple_product,
    _import_product_with_variants,
    _apply_product_meta,
)
