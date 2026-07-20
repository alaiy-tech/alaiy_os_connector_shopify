"""
Compatibility re-export shim.

order_sync.py was split into the alaiy_os_connector_shopify.shopify.order
package (queries, utils, customer, warehouse, locking, delivery_notes,
line_items, upsert, update, pull, webhook) for maintainability. Every name
that was previously importable from this module -- including hardcoded
frappe.enqueue dotted-path strings, hooks.py doc_events, api/sync.py,
api/webhooks.py, and the test suite -- is re-exported here unchanged so no
external caller needs to change.
"""

from alaiy_os_connector_shopify.shopify.order.queries import (
    _ORDERS_COUNT_QUERY,
    _ORDERS_QUERY,
)
from alaiy_os_connector_shopify.shopify.order.utils import (
    _as_administrator,
    _order_node_to_rest_shape,
    _line_item_qty,
    _resolve_item_code,
)
from alaiy_os_connector_shopify.shopify.order.customer import (
    _get_or_create_customer,
    _resolve_default_territory,
    _create_root_territory,
)
from alaiy_os_connector_shopify.shopify.order.warehouse import (
    _resolve_default_warehouse,
    _force_valid_warehouse,
)
from alaiy_os_connector_shopify.shopify.order.locking import (
    _acquire_order_lock,
    _release_order_lock,
)
from alaiy_os_connector_shopify.shopify.order.delivery_notes import (
    _create_delivery_note_if_needed,
    _sync_fulfillments,
    _create_delivery_note_for_fulfillment,
)
from alaiy_os_connector_shopify.shopify.order.line_items import (
    _apply_line_item_diff,
    _sync_order_line_items,
)
from alaiy_os_connector_shopify.shopify.order.upsert import (
    get_active_sales_order,
    _upsert_order,
    _upsert_order_unlocked,
)
from alaiy_os_connector_shopify.shopify.order.update import (
    _update_order,
    _update_order_unlocked,
    _can_modify_order_items,
)
from alaiy_os_connector_shopify.shopify.order.pull import (
    run_orders_sync,
    _run_orders_pull,
    get_shopify_orders_count,
    import_existing_orders,
    run_full_import,
)
from alaiy_os_connector_shopify.shopify.order.webhook import (
    handle_order_webhook,
    _cancel_order,
)
from alaiy_os_connector_shopify.shopify.order.tax import (
    _resolve_tax_account,
    _create_tax_account,
    _append_tax_lines,
)
from alaiy_os_connector_shopify.shopify.order.invoice import (
    create_sales_invoice_if_paid,
    on_sales_invoice_submit,
    push_order_paid,
)
