"""
Compatibility re-export shim.

This module's actual content was split into alaiy_os_connector_shopify/
shopify/product/{utils,item_hooks,pricing,variants,media,seo,tags,
canonical,taxonomy,export,webhooks,archive,queries}.py as part of a
pure architectural refactor -- no behavior changed. Every name that used
to live directly in this file is re-exported here unchanged, so existing
dotted-path references (hooks.py doc_events/schedulers, frappe.enqueue
string paths like "...product_sync.push_item", api/sync.py, other
modules' inline imports, tests) keep working exactly as before without
modification.
"""

from alaiy_os_connector_shopify.shopify.product.utils import (
    _to_utc_naive,
)
from alaiy_os_connector_shopify.shopify.product.queries import (
    _PRODUCT_SET_MUTATION,
    _PRODUCT_UPDATE_MUTATION,
)
from alaiy_os_connector_shopify.shopify.product.item_hooks import (
    validate_item_uoms,
    on_item_change,
    on_item_delete,
    on_item_price_change,
    _sync_enabled,
)
from alaiy_os_connector_shopify.shopify.product.tags import (
    copy_template_tags_to_variant,
    _item_tags,
    sync_shopify_tags,
)
from alaiy_os_connector_shopify.shopify.product.pricing import (
    _price_rate,
    _variant_price,
    _variant_compare_at_price,
    _variant_cost,
)
from alaiy_os_connector_shopify.shopify.product.variants import (
    _variant_inventory_item_payload,
    _variant_canonical,
    _variant_set_payload,
)
from alaiy_os_connector_shopify.shopify.product.media import (
    _absolute_file_url,
    _item_images,
)
from alaiy_os_connector_shopify.shopify.product.seo import (
    _seo_values,
)
from alaiy_os_connector_shopify.shopify.product.canonical import (
    _product_canonical,
    _product_options_payload,
    _product_set_input,
)
from alaiy_os_connector_shopify.shopify.product.taxonomy import (
    _resolve_category_id,
    fetch_shopify_taxonomy,
)
from alaiy_os_connector_shopify.shopify.product.export import (
    LOCK_TIMEOUT_SECONDS,
    push_item,
    run_bulk_export_to_shopify,
    _variants_of,
    _all_variants_of,
    _push_product,
    _push_product_unlocked,
    push_changed_items_only,
)
from alaiy_os_connector_shopify.shopify.product.webhooks import (
    handle_product_webhook,
    _webhook_product_to_graphql_node,
    _handle_product_create,
    _handle_product_update,
    _update_item_from_shopify,
    _handle_product_delete,
)
from alaiy_os_connector_shopify.shopify.product.archive import (
    archive_item,
)
