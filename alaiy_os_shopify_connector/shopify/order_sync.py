import frappe
from frappe.utils import flt, now_datetime


# ── Webhook handler ────────────────────────────────────────────────────────────

def handle_order_webhook(topic, payload):
    if topic == "orders/cancelled":
        _cancel_order(payload)
    else:
        _upsert_order(payload)


# ── Scheduled / manual pull ────────────────────────────────────────────────────

def run_orders_sync(trigger="manual"):
    log = _open_log("orders", trigger)
    try:
        from alaiy_os_shopify_connector.shopify.client import ShopifyClient
        client = ShopifyClient()
        settings = frappe.get_single("Shopify Connector Settings")

        params = {
            "status": settings.sh_order_status_filter or "open",
            "financial_status": "paid",
            "fields": "id,name,customer,line_items,financial_status,fulfillment_status",
        }

        processed = created = failed = pages = 0
        for page_data in client.get_paginated("orders.json", params):
            pages += 1
            for order in page_data.get("orders", []):
                processed += 1
                try:
                    _upsert_order(order)
                    created += 1
                except Exception as exc:
                    failed += 1
                    _append_log(log, f"ERROR order={order.get('name')}: {exc}")
                    frappe.log_error(
                        title=f"Shopify: order {order.get('name')} failed",
                        message=frappe.get_traceback(),
                    )

        log.status = "success"
        log.items_processed = processed
        log.items_created = created
        log.items_failed = failed
        log.pages_done = pages
        log.finished_at = now_datetime()
        log.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        log.status = "failed"
        log.error_message = frappe.get_traceback()[:500]
        log.finished_at = now_datetime()
        log.save(ignore_permissions=True)
        frappe.db.commit()
        raise


# ── Internal helpers ───────────────────────────────────────────────────────────

def _upsert_order(order):
    order_id = str(order.get("id", ""))
    if not order_id:
        return
    if frappe.db.exists("Sales Order", {"sh_shopify_order_id": order_id}):
        return  # already processed

    settings = frappe.get_single("Shopify Connector Settings")
    customer_name = _get_or_create_customer(order.get("customer") or {}, settings)

    line_items = []
    for li in order.get("line_items", []):
        item_code = _resolve_item_code(li)
        if not item_code:
            continue
        line_items.append({
            "item_code": item_code,
            "qty": flt(li.get("quantity", 1)),
            "rate": flt(li.get("price", 0)),
            "delivery_date": frappe.utils.today(),
        })

    if not line_items:
        frappe.log_error(
            title=f"Shopify order {order.get('name')}: no mappable items",
            message=str(order.get("line_items")),
        )
        return

    so = frappe.new_doc("Sales Order")
    so.customer = customer_name
    so.company = settings.sh_company or frappe.defaults.get_global_default("company")
    so.transaction_date = frappe.utils.today()
    so.delivery_date = frappe.utils.today()
    so.selling_price_list = settings.sh_selling_price_list or "Standard Selling"
    so.set_warehouse = settings.sh_default_warehouse
    if settings.sh_cost_center:
        so.cost_center = settings.sh_cost_center
    so.sh_shopify_order_id = order_id
    so.sh_shopify_order_name = order.get("name", "")
    for li in line_items:
        so.append("items", li)

    so.flags.ignore_permissions = True
    so.insert()
    so.submit()
    frappe.db.commit()


def _cancel_order(order):
    order_id = str(order.get("id", ""))
    so_name = frappe.db.get_value("Sales Order", {"sh_shopify_order_id": order_id}, "name")
    if so_name:
        so = frappe.get_doc("Sales Order", so_name)
        if so.docstatus == 1:
            so.cancel()
            frappe.db.commit()


def _get_or_create_customer(customer_data, settings):
    shopify_id = str(customer_data.get("id", ""))
    if shopify_id:
        existing = frappe.db.get_value(
            "Customer", {"sh_shopify_customer_id": shopify_id}, "name"
        )
        if existing:
            return existing

    first = customer_data.get("first_name", "")
    last = customer_data.get("last_name", "")
    full_name = f"{first} {last}".strip() or customer_data.get("email", "") or f"Shopify {shopify_id}"

    if frappe.db.exists("Customer", full_name):
        return full_name

    c = frappe.new_doc("Customer")
    c.customer_name = full_name
    c.customer_type = "Individual"
    c.customer_group = settings.sh_customer_group or "All Customer Groups"
    c.territory = "All Territories"
    if shopify_id:
        c.sh_shopify_customer_id = shopify_id
    c.flags.ignore_permissions = True
    c.insert()
    frappe.db.commit()
    return c.name


def _resolve_item_code(line_item):
    sku = (line_item.get("sku") or "").strip()
    if sku and frappe.db.exists("Item", sku):
        return sku

    variant_id = str(line_item.get("variant_id") or "")
    if variant_id:
        by_variant = frappe.db.get_value(
            "Item", {"sh_shopify_variant_id": variant_id}, "name"
        )
        if by_variant:
            return by_variant

    title = (line_item.get("title") or "").strip()
    if title and frappe.db.exists("Item", title):
        return title

    return None


# ── Sync log helpers ───────────────────────────────────────────────────────────

def _open_log(sync_type, trigger):
    log = frappe.new_doc("Shopify Sync Log")
    log.sync_type = sync_type
    log.trigger = trigger
    log.status = "running"
    log.started_at = now_datetime()
    log.insert(ignore_permissions=True)
    frappe.db.commit()
    return log


def _append_log(log, message: str):
    """Append a line to log.log_messages without saving."""
    existing = log.log_messages or ""
    log.log_messages = (existing + "\n" + message).strip()
