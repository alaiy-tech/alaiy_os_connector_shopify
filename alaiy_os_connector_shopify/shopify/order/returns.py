"""
Refund sync -- Shopify refunds/create -> Sales Return (Delivery Note,
is_return=1) + Credit Note (Sales Invoice, is_return=1) + refund Payment Entry.

Driven by the REFUND, not by Shopify's Return object. Shopify models three
separate state machines and this module deliberately only handles the
middle one:

  1. Return lifecycle  -- returns/request, returns/approve, returns/decline,
                          returns/cancel, returns/update, returns/process,
                          returns/close, returns/reopen. The physical
                          goods: requested, approved, received. GraphQL
                          Admin API only. NOT SUBSCRIBED -- see below.
  2. Refund            -- refunds/create. What this module handles: the
                          financial reversal, which carries the refunded
                          line items and restock instructions.
  3. Money settlement  -- each refund's OrderTransaction has its own status
                          (pending / processing / success / failure).
                          refunds/create fires "independent from the
                          movement of money", so a refund existing does not
                          mean the customer has been paid.

Consequence of only handling (2): a return that is requested, approved, and
physically received but not yet refunded produces NOTHING here -- no
document appears in Alaiy OS until money is actually refunded on Shopify.
For merchants who inspect goods before refunding, the warehouse sees the
box arrive with no corresponding Alaiy OS record until the refund is
issued. Subscribing to returns/process (and probably returns/approve) would
close that gap, but it needs a real decision about what an approved-but-
unrefunded return should even create -- a draft Sales Return? nothing but a
flag? -- rather than being wired up by default.
"""

import frappe
from frappe.utils import flt

from alaiy_os_connector_shopify.shopify.order.utils import _as_administrator, _resolve_item_code
from alaiy_os_connector_shopify.shopify.order.upsert import get_active_sales_order
from alaiy_os_connector_shopify.shopify.order.warehouse import _resolve_default_warehouse
from alaiy_os_connector_shopify.shopify.order.delivery_notes import _fill_expense_accounts
from alaiy_os_connector_shopify.shopify.order.invoice import _fill_item_accounts, _resolve_bank_cash_account


def handle_refund_webhook(topic, payload):
    """refunds/create -- payload is the Shopify Refund object (REST-shaped)."""
    try:
        _process_refund(payload)
    except Exception:
        frappe.log_error(
            title=f"Shopify: refund webhook {topic} failed",
            message=frappe.get_traceback(),
        )


def _process_refund(refund):
    refund_id = str(refund.get("id") or "")
    if not refund_id:
        return
    # Idempotent: Shopify redelivers webhooks, and a merchant edit on an
    # already-processed refund shouldn't create a second return. Check BOTH
    # documents -- a no_restock refund never creates a Delivery Note at all,
    # so checking only that would let a redelivery duplicate the Credit Note.
    for doctype in ("Delivery Note", "Sales Invoice"):
        if frappe.db.exists(doctype, {"sh_shopify_refund_id": refund_id}):
            return

    order_id = str(refund.get("order_id") or "")
    so_name = get_active_sales_order(order_id)
    if not so_name or frappe.db.get_value("Sales Order", so_name, "docstatus") != 1:
        return

    # Two separate maps, deliberately -- money and stock are different
    # questions on the same refund.
    #
    # credit_qty: every refunded line, always. Money comes back regardless
    # of what happened to the goods.
    #
    # restock_qty: only lines where the goods physically came back to us.
    # Shopify's restock_type says which:
    #   "return"         -- goods came back. Restock.
    #   "legacy_restock" -- same, from the pre-Returns-API flow. Restock.
    #   "no_restock"     -- damaged/written off, never re-enters stock. Skip.
    #   "cancel"         -- never shipped, so it never left our stock in the
    #                       first place; a Sales Return here would invent a
    #                       unit that was always on the shelf. Skip.
    #
    # Note on double-restock: Shopify ALSO adjusts its own inventory for
    # "return"/"cancel" lines (that's what refund_line_items[].location_id
    # is for). That is not a reason to skip our Sales Return -- it's the
    # same physical unit being recorded in two systems that each keep their
    # own count. Alaiy OS is the stock source of truth here and the
    # scheduled inventory push (inventory_sync.py) overwrites Shopify's
    # number with ours, so our count must include the returned unit or the
    # push would wrongly tell Shopify the return never happened.
    credit_qty = {}
    restock_qty = {}
    for rli in refund.get("refund_line_items") or []:
        li = rli.get("line_item") or {}
        item_code = _resolve_item_code({
            # variant_id is legitimately null on some lines (e.g. a custom
            # line item) -- _resolve_item_code already falls through
            # sku -> variant id -> title, so a null here is handled.
            "sku": li.get("sku"), "variant_id": li.get("variant_id"), "title": li.get("title"),
        })
        if not item_code:
            frappe.log_error(
                title=f"Shopify: refund {refund_id} line item didn't match any Item",
                message=f"line_item: {li}",
            )
            continue
        qty = flt(rli.get("quantity", 0))
        credit_qty[item_code] = credit_qty.get(item_code, 0) + qty
        if (rli.get("restock_type") or "") in ("return", "legacy_restock"):
            restock_qty[item_code] = restock_qty.get(item_code, 0) + qty

    refund_amount = _settled_refund_amount(refund)

    with _as_administrator():
        _make_sales_return(so_name, restock_qty, refund_id)
        si_name = _make_credit_note(so_name, credit_qty, refund_id)
        if si_name:
            if refund_amount > 0:
                _refund_payment_entry(si_name, refund_amount)
            else:
                _log_unsettled_refund(refund, refund_id, si_name)
    frappe.db.commit()


def _settled_refund_amount(refund):
    """
    Only money that has actually moved. A Refund object existing does NOT
    mean the customer has been paid -- Shopify documents refunds/create as
    firing "independent from the movement of money", and each
    OrderTransaction carries its own status (pending / processing /
    success / failure). Booking a Payment Entry for a pending or failed
    transaction would claim we refunded money we haven't.
    """
    return sum(
        flt(t.get("amount")) for t in (refund.get("transactions") or [])
        if t.get("kind") == "refund" and t.get("status") == "success"
    )


def _log_unsettled_refund(refund, refund_id, si_name):
    """
    Credit Note stands (the sale IS reversed), but no money has settled yet
    -- so it deliberately sits outstanding rather than being marked paid.

    Shopify does not re-fire refunds/create when a pending transaction
    later succeeds, so nothing revisits this automatically. The invoice
    being visibly unpaid is the intended signal: it shows up in
    Accounts Receivable until someone books the payment, rather than
    silently looking settled.
    """
    statuses = [
        f"{t.get('kind')}/{t.get('status')}={t.get('amount')}"
        for t in (refund.get("transactions") or [])
    ]
    frappe.log_error(
        title=f"Shopify: refund {refund_id} has no settled money yet ({si_name} left unpaid)",
        message=(
            f"Credit Note {si_name} was created, but no refund transaction has "
            f"status=success, so no Payment Entry was booked.\n\n"
            f"Transactions: {statuses or 'none on payload'}\n\n"
            f"Shopify fires refunds/create independent of money movement and does "
            f"not re-fire it when a pending transaction later settles. Book the "
            f"Payment Entry against {si_name} manually once the refund clears."
        ),
    )


def _trim_return_items(doc, qty_by_item):
    """
    make_return_doc() maps every still-returnable line at its full
    (negative) quantity -- keep only the items and quantities this specific
    refund actually covers, same shape as delivery_notes.py's
    per-fulfillment trim.

    Treats qty_by_item as a BUDGET that each row draws down, rather than a
    per-row cap. Two source rows can carry the same item_code -- the same
    SKU ordered twice, or two unmatched Shopify lines that both resolved to
    the shared "Shopify Custom Item" placeholder (see upsert.py's
    _merge_duplicate_item_rows) -- and capping each row independently
    against the same total would return that quantity twice over.

    make_return_doc has already netted off quantities from earlier returns
    against the same document, so abs(row.qty) here is what's genuinely
    still returnable. A refund for more than that (a merchant refunding the
    same line across two separate refunds) therefore lands short rather
    than going negative, which is correct.
    """
    remaining = dict(qty_by_item)
    kept = []
    for row in doc.items:
        budget = remaining.get(row.item_code, 0)
        if budget <= 0:
            continue
        take = min(abs(flt(row.qty)), budget)
        if take <= 0:
            continue
        row.qty = -take
        remaining[row.item_code] = budget - take
        kept.append(row)
    doc.items = kept
    return bool(doc.items)


def _land_return_in_warehouse(dn):
    """
    sh_return_warehouse if configured, else the connector's Default
    Warehouse -- same self-heal shape as warehouse.py's
    _force_valid_warehouse, kept separate here since a return's landing
    spot is deliberately allowed to differ from where orders normally ship
    FROM. Whatever's downstream (a supplier portal's own returns routing,
    a manual quality check) decides where the item really ends up from
    here -- this just gives it somewhere valid to land first.
    """
    settings = frappe.get_single("Shopify Connector Settings")
    warehouse = settings.sh_return_warehouse or _resolve_default_warehouse(settings)
    for item in dn.items:
        item.warehouse = warehouse
    dn.set_warehouse = warehouse


def _source_delivery_note(so_name, qty_by_item):
    """
    The Delivery Note to return against -- one that actually SHIPPED at
    least one of the refunded items, not just the order's first Delivery
    Note. A partially-shipped order has several (see delivery_notes.py's
    one-DN-per-Shopify-fulfillment rule), and returning against the wrong
    one makes make_return_doc map lines the refund never touched, which
    _trim_return_items would then drop entirely -- a silently empty return.
    Prefers the most recent qualifying one, since a re-ship of the same SKU
    is more likely what came back.
    """
    if not qty_by_item:
        return None
    rows = frappe.get_all(
        "Delivery Note Item",
        filters={
            "against_sales_order": so_name,
            "docstatus": 1,
            "item_code": ["in", list(qty_by_item)],
        },
        fields=["parent"],
        order_by="creation desc",
        limit=1,
    )
    return rows[0].parent if rows else None


def _make_sales_return(so_name, qty_by_item, refund_id):
    dn_name = _source_delivery_note(so_name, qty_by_item)
    if not dn_name:
        return None  # nothing restockable shipped -- no stock to bring back

    try:
        # Same last-point re-check as _make_credit_note -- see that
        # function's comment for why.
        if frappe.db.exists("Delivery Note", {"sh_shopify_refund_id": refund_id}):
            return None
        from erpnext.controllers.sales_and_purchase_return import make_return_doc
        dn = make_return_doc("Delivery Note", dn_name)
        if not _trim_return_items(dn, qty_by_item):
            return None
        _land_return_in_warehouse(dn)
        for row in dn.items:
            row.allow_zero_valuation_rate = 1
        _fill_expense_accounts(dn)
        dn.sh_shopify_refund_id = refund_id
        # ERPNext's own validate_return_against requires a return's
        # conversion_rate to exactly match the document it's returning
        # against -- confirmed live that make_return_doc doesn't always
        # carry this over (e.g. a source doc created while a since-fixed
        # currency bug had it set to a wrong non-1.0 value on a same-currency
        # order still has that same wrong value baked in). Copying it
        # explicitly satisfies the check regardless of what the source's
        # rate actually is, correct or not -- this fix is scoped to
        # unblocking the return, not correcting historical rate data.
        dn.conversion_rate = frappe.db.get_value("Delivery Note", dn_name, "conversion_rate")
        dn.flags.ignore_permissions = True
        dn.insert()
        dn.submit()
        return dn.name
    except Exception:
        frappe.log_error(
            title=f"Shopify: Sales Return failed for refund {refund_id}",
            message=f"Sales Order: {so_name}\n{frappe.get_traceback()}",
        )
        return None


def _source_sales_invoice(so_name, qty_by_item):
    """
    Same reasoning as _source_delivery_note: pick an invoice that actually
    billed one of the refunded items. An order invoiced per-shipment has
    more than one, and crediting against the wrong one trims to nothing.
    Excludes existing return invoices (is_return=1) -- crediting a credit
    note is not a thing.
    """
    if not qty_by_item:
        return None
    rows = frappe.get_all(
        "Sales Invoice Item",
        filters={
            "sales_order": so_name,
            "docstatus": 1,
            "item_code": ["in", list(qty_by_item)],
        },
        fields=["parent"],
        order_by="creation desc",
    )
    for row in rows:
        if not frappe.db.get_value("Sales Invoice", row.parent, "is_return"):
            return row.parent
    return None


def _make_credit_note(so_name, qty_by_item, refund_id):
    si_name = _source_sales_invoice(so_name, qty_by_item)
    if not si_name:
        return None  # not invoiced yet -- nothing to credit

    try:
        # Re-check right before inserting, not just at _process_refund's own
        # entry point -- confirmed live that a duplicate Credit Note can
        # still get created for one refund_id despite that earlier check
        # (two Sales Invoices, same refund_id, half a second apart, from
        # what traced back to a single _process_refund call -- exact
        # mechanism unconfirmed, but the failure mode is real). This is the
        # last point before an irreversible insert, so it's the last chance
        # to catch a redundant run regardless of cause.
        if frappe.db.exists("Sales Invoice", {"sh_shopify_refund_id": refund_id}):
            return None
        from erpnext.controllers.sales_and_purchase_return import make_return_doc
        settings = frappe.get_single("Shopify Connector Settings")
        si = make_return_doc("Sales Invoice", si_name)
        if not _trim_return_items(si, qty_by_item):
            return None
        si.update_stock = 0  # stock already returned via the Sales Return above
        _fill_item_accounts(si, settings)
        si.sh_shopify_refund_id = refund_id
        # Same reasoning as _make_sales_return: ERPNext requires an exact
        # conversion_rate match against the document being returned against,
        # and make_return_doc doesn't always carry it over.
        si.conversion_rate = frappe.db.get_value("Sales Invoice", si_name, "conversion_rate")
        si.flags.from_shopify_sync = True
        si.flags.ignore_permissions = True
        si.insert()
        si.submit()
        return si.name
    except Exception:
        frappe.log_error(
            title=f"Shopify: Credit Note failed for refund {refund_id}",
            message=f"Sales Order: {so_name}\n{frappe.get_traceback()}",
        )
        return None


def _refund_payment_entry(si_name, refund_amount):
    """
    Shopify already sent the money back to the customer -- book a Payment
    Entry against the Credit Note so it doesn't sit open, mirroring
    invoice.py's _mark_invoice_paid on the forward side.

    Deliberately does NOT force Shopify's own refund total onto the Payment
    Entry. Shopify's refund transaction amount can legitimately exceed what
    this Credit Note covers -- it may also include refunded shipping,
    duties, or a manual adjustment, none of which are line items on the
    trimmed credit note. Over-allocating against the invoice is an
    ERPNext validation error ("Allocated amount cannot be greater than
    outstanding"), so let get_payment_entry settle exactly the credit
    note's own outstanding amount, and log the difference for a human to
    book separately rather than guessing where it belongs.
    """
    try:
        from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
        si = frappe.get_doc("Sales Invoice", si_name)
        paid_from = _resolve_bank_cash_account(si.company)
        if not paid_from:
            frappe.log_error(
                title=f"Shopify: no bank/cash account to refund {si_name}",
                message="Set a Default Cash/Bank Account on the Company to auto-settle Shopify refunds.",
            )
            return
        pe = get_payment_entry("Sales Invoice", si_name)
        pe.paid_from = paid_from
        pe.reference_no = si_name
        pe.posting_date = si.posting_date
        pe.reference_date = si.posting_date
        pe.flags.from_shopify_sync = True
        pe.flags.ignore_permissions = True
        pe.insert()
        pe.submit()

        credited = abs(flt(si.grand_total))
        shortfall = flt(refund_amount) - credited
        if abs(shortfall) > 0.01:
            frappe.log_error(
                title=f"Shopify: refund total differs from credit note {si_name}",
                message=(
                    f"Shopify refunded {refund_amount}, this credit note covers {credited} "
                    f"(difference {shortfall}). Usually refunded shipping, duties, or a "
                    f"manual adjustment that has no line item to credit -- book it manually."
                ),
            )
    except Exception:
        frappe.log_error(
            title=f"Shopify: refund Payment Entry failed for {si_name}",
            message=frappe.get_traceback(),
        )
