"""
Sales Order creation from a Shopify order -- moved verbatim from
order_sync.py, unchanged.
"""

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.order.locking import _acquire_order_lock, _release_order_lock
from alaiy_os_connector_shopify.shopify.order.customer import _get_or_create_customer
from alaiy_os_connector_shopify.shopify.order.warehouse import _resolve_default_warehouse, _resolve_warehouse_for_item
from alaiy_os_connector_shopify.shopify.order.utils import _resolve_item_code
from alaiy_os_connector_shopify.shopify.order.delivery_notes import (
    _sync_fulfillments,
    _create_delivery_note_if_needed,
    _sync_tracking,
)
from alaiy_os_connector_shopify.shopify.order.tax import _append_tax_lines


def get_active_sales_order(order_id: str):
    """
    Look up the Sales Order for a Shopify order ID, preferring the latest
    non-cancelled document. Once _sync_order_line_items starts amending
    (cancel + recreate) a submitted order, the cancelled original and its
    amended replacement both carry the same sh_shopify_order_id -- a plain
    frappe.db.get_value with no docstatus/order_by picks whichever the DB
    happens to return first, which can silently resurrect the cancelled one.
    """
    return frappe.db.get_value(
        "Sales Order",
        {"sh_shopify_order_id": order_id, "docstatus": ["!=", 2]},
        "name",
        order_by="creation desc",
    )


def _merge_duplicate_item_rows(line_items: list) -> list:
    """
    ERPNext rejects a Sales Order with the same item_code on two rows
    (validate_for_duplicate_items) unless a global setting is flipped --
    hit in practice when 2+ Shopify line items fail catalog matching and
    all fall back to the single shared "Shopify Custom Item" placeholder.
    Merge same-item_code rows into one instead: qty summed, rate set to
    the combined amount / combined qty so the order total stays exact,
    descriptions/titles concatenated so nothing gets silently dropped.
    """
    merged = {}
    order = []
    for row in line_items:
        key = row["item_code"]
        if key not in merged:
            merged[key] = dict(row)
            order.append(key)
            continue
        existing = merged[key]
        existing_amount = flt(existing["qty"]) * flt(existing["rate"])
        new_amount = flt(row["qty"]) * flt(row["rate"])
        existing["qty"] = flt(existing["qty"]) + flt(row["qty"])
        total_amount = existing_amount + new_amount
        existing["rate"] = (total_amount / existing["qty"]) if existing["qty"] else 0
        for field in ("item_name", "description"):
            if row.get(field) and row[field] not in (existing.get(field) or ""):
                existing[field] = f"{existing.get(field, '')}; {row[field]}".strip("; ")
        # item_name is a Data field capped at 140 chars in the DB -- unbounded
        # concatenation of multiple real product names (confirmed live: two
        # long names alone exceeded it) crashed the whole order insert.
        # description has no such length limit, left untouched.
        if existing.get("item_name") and len(existing["item_name"]) > 140:
            existing["item_name"] = existing["item_name"][:137] + "..."
    return [merged[key] for key in order]


def _upsert_order(order):
    """Acquires this order's lock, then defers to _upsert_order_unlocked."""
    order_id = str(order.get("id", ""))
    if not order_id:
        return False
    if not _acquire_order_lock(order_id):
        frappe.log_error(
            title=f"Shopify order {order_id}: upsert lock timed out",
            message="Another process held this order's lock for 30s+ -- skipped to avoid a duplicate.",
        )
        return False
    try:
        return _upsert_order_unlocked(order, order_id)
    finally:
        _release_order_lock(order_id)


def _upsert_order_unlocked(order, order_id):
    """Returns True if a new Sales Order was created, False if skipped."""
    if get_active_sales_order(order_id):
        return False  # already processed

    settings = frappe.get_single("Shopify Connector Settings")
    # A missing default Address Template makes Alaiy OS throw while rendering the
    # customer's address during Sales Order validate -- ensure one exists first.
    from alaiy_os_connector_shopify.shopify.order.address import ensure_default_address_template
    ensure_default_address_template()

    # Real Shopify order date, not the date this pull/webhook happens to run
    # on -- computed here (not just on the parent so.transaction_date below)
    # because each Sales Order Item row also carries its own delivery_date,
    # and ERPNext's own validate() resyncs the PARENT delivery_date from the
    # child rows -- confirmed live: setting only so.delivery_date further
    # down still showed today's date after insert, because every row here
    # was hardcoded to frappe.utils.today() and won by that resync.
    order_date = frappe.utils.getdate(order.get("created_at")) if order.get("created_at") else frappe.utils.today()
    customer_name = _get_or_create_customer(
        order.get("customer") or {}, settings)
    warehouse = _resolve_default_warehouse(settings)

    from alaiy_os_connector_shopify.shopify.order.utils import _line_item_qty

    from alaiy_os_connector_shopify.shopify.order.charges import build_custom_line_item

    line_items = []
    for li in order.get("line_items", []):
        item_code = _resolve_item_code(li)
        if not item_code:
            # No catalog match -- keep it as a custom line item rather than
            # silently dropping it (Shopify allows one-off/custom products).
            custom = build_custom_line_item(li, warehouse, delivery_date=order_date)
            if custom:
                line_items.append(custom)
            continue
        qty = _line_item_qty(li)
        if qty <= 0:
            continue
        line_items.append({
            "item_code": item_code,
            "qty": qty,
            "rate": flt(li.get("price", 0)),
            # Real per-line warehouse, not the order-level default -- an
            # order with items from 2+ real suppliers needs each line
            # recorded against its own supplier's warehouse, not one
            # shared fallback. Falls back to the order-level default
            # itself when the item has no resolved location yet.
            "warehouse": _resolve_warehouse_for_item(item_code, settings, warehouse),
            "delivery_date": order_date,
            "sh_shopify_variant_id": str(li.get("variant_id", "")),
        })

    if not line_items:
        # Say WHICH of the two very different reasons this is. A cancelled or
        # fully refunded order comes back with every line at quantity 0, and
        # reporting that as "no mappable items" reads as a catalogue problem --
        # it sent two separate investigations looking for a missing item mapping
        # that did not exist.
        raw_lines = order.get("line_items") or []
        all_zero = bool(raw_lines) and all(
            _line_item_qty(li) <= 0 for li in raw_lines
        )
        if all_zero:
            title = f"Shopify order {order.get('name')}: every line refunded or cancelled"
            reason = (
                "Every line on this order has quantity 0, so there is nothing to import. "
                "This is the normal shape of a cancelled or fully refunded order, not a "
                "catalogue gap."
            )
        else:
            title = f"Shopify order {order.get('name')}: no mappable items"
            reason = (
                "None of this order's lines resolved to a local Item, by SKU, variant id or "
                "title. The products are missing from the catalogue, or their Shopify ids "
                "were never linked."
            )
        frappe.log_error(title=title, message=f"{reason}\n\n{raw_lines}")
        return False

    line_items = _merge_duplicate_item_rows(line_items)

    company = settings.sh_company or frappe.defaults.get_global_default("company")

    from alaiy_os_connector_shopify.shopify.order.currency import (
        resolve_order_currency, ensure_customer_currency_account, get_order_exchange_rate,
    )
    order_currency = resolve_order_currency(order, company)
    company_currency = frappe.get_cached_value("Company", company, "default_currency")
    if order_currency != company_currency:
        ensure_customer_currency_account(customer_name, company, order_currency)

    conversion_rate = get_order_exchange_rate(order_currency, company_currency, order_date)
    if order_currency == company_currency and conversion_rate != 1.0:
        # Caught live on a real site: ~1,481 same-currency orders got stamped with
        # a real exchange rate instead of 1.0 during a since-unexplained
        # window, silently blocking every refund/return on them months
        # later. get_order_exchange_rate's own same-currency guard should
        # make this impossible -- if it ever fires again, log it loudly
        # right away rather than letting it surface as a mystery refund
        # failure later.
        frappe.log_error(
            title="Shopify: same-currency order got a non-1.0 conversion_rate",
            message=f"order_currency={order_currency} company_currency={company_currency} conversion_rate={conversion_rate}",
        )
        conversion_rate = 1.0

    so = frappe.new_doc("Sales Order")
    so.customer = customer_name
    so.company = company
    so.currency = order_currency
    so.conversion_rate = conversion_rate
    so.transaction_date = order_date
    so.delivery_date = order_date
    so.selling_price_list = settings.sh_selling_price_list or "Standard Selling"
    so.set_warehouse = warehouse
    if settings.sh_cost_center:
        so.cost_center = settings.sh_cost_center
    # Generic cross-connector field (alaiy_os core) -- answers "which channel
    # did this order come from" the same way regardless of which connector
    # is installed, so a site running Shopify + Amazon + Unicommerce can
    # filter/report on Sales Order.sales_channel uniformly.
    so.sales_channel = "Shopify"
    so.sh_shopify_order_id = order_id
    so.sh_shopify_order_name = order.get("name", "")
    so.sh_financial_status = order.get("financial_status", "")
    so.sh_fulfillment_status = order.get("fulfillment_status", "")
    so.sh_shopify_notes = order.get("note") or ""
    # The method NAME, independent of what it cost. The shipping charge
    # itself rides on the Sales Taxes and Charges table (charges.py), which
    # skips the row entirely when shipping is free -- so that description
    # can't be relied on as the source of the method name.
    shipping_lines = order.get("shipping_lines") or []
    so.sh_delivery_method = (shipping_lines[0].get("title") or "") if shipping_lines else ""
    from alaiy_os_connector_shopify.shopify.order.push import parse_tags, strip_status_tag
    so.sh_shopify_order_tags = ",".join(strip_status_tag(parse_tags(order.get("tags"))))
    for li in line_items:
        so.append("items", li)

    # Shipping address
    from alaiy_os_connector_shopify.shopify.order.address import sync_order_address
    from alaiy_os_connector_shopify.shopify.order.charges import (
        append_shipping_charge, apply_order_discount,
    )
    addr = sync_order_address(order, customer_name)
    if addr:
        so.customer_address = addr
        so.shipping_address_name = addr

    _append_tax_lines(so, order.get("tax_lines"), order.get("taxes_included"), settings)
    append_shipping_charge(so, order, settings)
    apply_order_discount(so, order)

    # Set BEFORE insert/submit -- Sales Order's on_update/on_submit doc_events
    # check this flag to skip pushing back to Shopify, since this save
    # originated FROM Shopify (webhook or pull) and pushing it back would
    # just be echoing the same data Shopify already has.
    so.flags.from_shopify_sync = True
    so.flags.ignore_permissions = True
    so.insert()

    # Draft orders from Shopify should stay as draft in Alaiy OS until customer completes checkout.
    # Real orders are submitted immediately and ready for fulfillment.
    # Draft orders have Order # like #D9, #D10; real orders are numeric like #1015
    order_name = order.get("name", "")
    is_draft_order = order_name.startswith("#D")
    if not is_draft_order:
        so.submit()

    frappe.db.commit()

    fulfillments = order.get("fulfillments") or []
    # Both the REST webhook payload and the GraphQL pull (via
    # fulfillmentLineItems, added to fix a confirmed live bug -- an order
    # shipped in more than one real Shopify fulfillment was being collapsed
    # into a single Delivery Note by the full-order fallback below) now
    # carry per-fulfillment line_items, so _sync_fulfillments can create one
    # Delivery Note per real fulfillment regardless of source. The
    # full-order fallback is now only for the rare case where Shopify
    # itself reports the order fulfilled but with no fulfillments array at
    # all (e.g. a quick manual "Complete order" -- see
    # _create_delivery_note_if_needed's own docstring).
    if any(f.get("line_items") for f in fulfillments):
        _sync_fulfillments(so.name, fulfillments)
    elif so.sh_fulfillment_status == "fulfilled":
        _create_delivery_note_if_needed(so.name)

    # Delivery status/tracking is independent of which path created the
    # Delivery Note -- _sync_tracking matches on fulfillment id and falls
    # back to the order's own Delivery Note.
    for fulfillment in fulfillments:
        if fulfillment.get("display_status") or fulfillment.get("tracking_number"):
            # order_id is on the standalone fulfillments/* webhook payload but
            # not on a fulfillment nested inside an order -- _sync_tracking
            # needs it for its no-fulfillment-id fallback.
            _sync_tracking({**fulfillment, "order_id": order_id})

    # Orders often arrive already paid (and sometimes already fulfilled) at
    # create time -- invoice right away if the trigger is met.
    if not is_draft_order:
        from alaiy_os_connector_shopify.shopify.order.invoice import create_sales_invoice_if_paid
        create_sales_invoice_if_paid(
            so.name, order.get("financial_status", ""), order.get("fulfillment_status", ""))
    return True
