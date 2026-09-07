# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""Sales reporting over the Sales Orders the Shopify order sync wrote.

`shopify/order/upsert.py` materialises every Shopify order as a Sales Order and
stamps `sh_shopify_order_id`, `sh_shopify_order_name`, `sh_financial_status` and
`sh_fulfillment_status` on it, with `sh_shopify_variant_id` on every line.
Nothing read any of it back out until this module. There is no Shopify call
anywhere here: this is the local half of the sales answer, and unlike Amazon
there is no live half to check it against -- Shopify's Admin API has no endpoint
that returns an authoritative revenue topline the way `getOrderMetrics` does.
`get_store_counts` reports counts, not money, for exactly that reason.

Adapted from the Amazon connector's `sales.py`. The period arithmetic is the
same because a week is a week; everything about *which orders count* is not.

## Which orders count

`so.docstatus = 1`, and nothing else.

That is deliberately simpler than the Amazon version, which additionally has to
exclude orders whose channel status says cancelled, because its sync leaves a
shipped-then-cancelled order submitted on purpose. This sync does not: a Shopify
cancellation arrives as a webhook and `shopify/order/webhook.py:_cancel_order`
calls `so.cancel()`, which moves the order to docstatus 2 and out of every
figure here. A Shopify *draft* order (`#D`-prefixed) is left unsubmitted by
`upsert.py` and is excluded by the same test.

## The under-count that replaces it, and it is worse

`shopify/order/pull.py:run_orders_sync` queries Shopify with
`financial_status:paid`. **Unpaid, pending and authorised orders are not in this
data at all** unless a webhook happened to create one, and no date range widens
that -- it is a filter on the sync, not on the query below.

This is the single most important thing about every number in this module. A
merchant asking "how many orders came in last week" and getting the paid ones,
with nothing saying so, has been answered wrongly rather than partially. So
`_coverage_note` says it on every result, unconditionally, and it is not
conditional on the period the way the date-window clause is: the date window can
be fine and this still applies.

## Which currency

`shopify/order/currency.py:resolve_order_currency` takes the currency from the
order, so `grand_total` on a multi-currency store is dollars in some rows and
rupees in others and summing it is meaningless. Every figure here sums a `base_*`
column -- company currency, via each order's `conversion_rate` -- and every
result names the currency it is in.

That is right rather than perfect. `upsert.py:160-172` records a confirmed live
failure: about 1,481 orders on one site were stamped a `conversion_rate` that
was not 1.0 despite being in the company's own currency, which is now guarded
but was not always. `orders_at_fallback_rate` counts the orders whose rate looks
suspect so an answer can caveat itself instead of the caller never learning.

## These are gross

Shopify's fees, its shipping charges and its refunds are not netted out of
anything here:

- `product_sales` sums `base_net_total` -- items only, no tax. It is the
  headline figure.
- `order_total` sums `base_grand_total` -- items plus whatever tax and shipping
  rows the sync wrote onto the order.

Refunds are counted, not subtracted. `shopify/order/refund.py` writes a Credit
Note stamped `sh_shopify_refund_id`, and `totals.refunds` reports how many landed
in the period so an answer can say "gross, and there were 12 refunds" rather
than either ignoring them or silently netting them. Netting them properly is a
second data model -- partial refunds, restocking, refunded shipping -- and a
half-netted figure is worse than an honestly gross one.

None of this is a payout.

## Envelope width

`csv_export._rows_from` reads a dict as a wrapper around its rows only while it
carries at most `_ENVELOPE_METADATA_KEYS` (5) non-list values; past that the
export writes the summary line instead of the series it summarises. Every result
here therefore keeps its scalars nested -- `period`, `ranking`, `totals`,
`coverage` -- which holds each envelope to four non-list keys with one to spare.
Adding a top-level scalar to any of these is what would break the CSV, silently.

## MariaDB

The bucket expressions use `WEEKDAY` and `DAYOFMONTH`. The app is already
MariaDB-only through `shopify/sync_guard.py`'s `GET_LOCK`, so this adds no
constraint that was not there; it is worth knowing it is here.
"""

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, get_last_day, getdate, nowdate

SETTINGS = "Shopify Connector Settings"

# Bucket start per granularity, as a MariaDB expression over `so.transaction_date`.
# `total` groups on a constant expression so one code path serves every
# granularity: it yields a single group whose start is the period's own start.
BUCKET_SQL = {
    "day": "so.transaction_date",
    "week": "DATE_SUB(so.transaction_date, INTERVAL WEEKDAY(so.transaction_date) DAY)",
    "month": "DATE_SUB(so.transaction_date, INTERVAL DAYOFMONTH(so.transaction_date) - 1 DAY)",
    "total": "DATE(%(date_from)s)",
}
GRANULARITIES = tuple(BUCKET_SQL)

# Shopify's own order vocabularies, lowercased, as `shopify/order/utils.py`
# writes them from `displayFinancialStatus` / `displayFulfillmentStatus`.
#
# These are free-text Data custom fields and not doctype Selects, so there is no
# schema to validate against and `_one_of` does it here instead -- a wrong value
# comes back naming the real ones rather than silently matching no rows. The
# cost is that a Shopify API version that renames a display status makes this a
# code change; `SHOPIFY_API_VERSION` is pinned in `shopify/graphql_client.py`,
# so that is a scheduled event rather than a surprise.
#
# Two vocabularies, two parameter names, and neither is ever called `status`.
# One name covering two enums across one pack is a trap for a model that has
# just read the other tool -- `list_listings` already has a `status` and its
# values are Active/Draft/Archived, which is a third vocabulary again.
FINANCIAL_STATUSES = (
    "pending",
    "authorized",
    "partially_paid",
    "paid",
    "partially_refunded",
    "refunded",
    "voided",
    "expired",
)
FULFILLMENT_STATUSES = (
    "unfulfilled",
    "partially_fulfilled",
    "fulfilled",
    "restocked",
    "scheduled",
    "on_hold",
)

# Two years of days is 731 buckets and about as many lines in a completion. Past
# this the request is refused naming a coarser granularity, rather than truncated:
# a series silently missing its tail is worse than one that was not produced.
MAX_BUCKETS = 400

TOP_DEFAULT_LIMIT = 10
TOP_MAX_LIMIT = 50

ORDERS_PAGE_SIZE = 20
ORDERS_MAX_PAGE_SIZE = 50

COMPARE_BASELINES = ("previous_period", "previous_year")

#: Said on every result, because it is true of every result. See the module
#: docstring: this is a filter on the sync, not on the query.
PAID_ONLY_NOTE = (
    "The order sync only fetches orders Shopify reports as financially paid, so "
    "unpaid, pending and authorised orders are missing from these figures "
    "regardless of the period asked for."
)


# --- validation --------------------------------------------------------------
def _one_of(value, allowed, label, default=None):
    """Validate against a fixed set, naming the real values when it fails.

    The alternative -- falling through to a default -- answers a different
    question from the one asked without saying so.
    """
    if value in (None, ""):
        if default is None:
            frappe.throw(_("{0} is required. One of: {1}.").format(label, ", ".join(allowed)))
        return default
    value = str(value).strip()
    if value not in allowed:
        frappe.throw(_("Unknown {0} {1}. One of: {2}.").format(label, value, ", ".join(allowed)))
    return value


def _period(date_from, date_to=None, label="date_from"):
    """A validated, inclusive (from, to) pair of dates.

    `date_to` defaults to today rather than to `date_from`: "sales since March"
    is a whole question, "sales on the single day of March 1st" is not the one
    being asked.

    `label` names the parameter in the error, because `compare_sales_periods`
    validates two pairs and an error saying `date_from` when what was missing is
    `baseline_from` sends a caller to fix the wrong argument.
    """
    if not date_from:
        frappe.throw(_("{0} is required (YYYY-MM-DD).").format(label))
    start = getdate(date_from)
    end = getdate(date_to) if date_to else getdate(nowdate())
    if start > end:
        frappe.throw(
            _("{0} {1} is after {2} {3}.").format(label, start, label.replace("from", "to"), end)
        )
    return start, end


def _assert_bucket_count(date_from, date_to, granularity):
    if granularity == "total":
        return
    days = (date_to - date_from).days + 1
    buckets = {"day": days, "week": days // 7 + 1, "month": days // 28 + 1}[granularity]
    if buckets > MAX_BUCKETS:
        frappe.throw(
            _(
                "{0} days at {1} granularity is about {2} buckets, over the limit of {3}. "
                "Ask for a coarser granularity (week, month or total) or a shorter period."
            ).format(days, granularity, buckets, MAX_BUCKETS)
        )


# --- company & currency ------------------------------------------------------
def _company():
    """The company Shopify orders book to.

    `Shopify Connector Settings` is a Single, so unlike the Amazon connector
    there is no connection to resolve -- but the same three-step fallback
    applies for the same reason. If `sh_company` was cleared after orders were
    already synced, the orders themselves still name the company they were
    booked to, and answering from them beats refusing.
    """
    company = frappe.db.get_single_value(SETTINGS, "sh_company") or frappe.defaults.get_global_default(
        "company"
    )
    if not company:
        company = frappe.db.get_value(
            "Sales Order",
            {"sh_shopify_order_id": ["is", "set"]},
            "company",
            order_by="modified desc",
        )
    if not company:
        frappe.throw(
            _(
                "No company is set for Shopify orders and none has ever been booked, so there "
                "is no currency to report these figures in. Set 'Company' under Defaults on "
                "Shopify Connector Settings."
            )
        )
    return company


def _currency(company):
    return frappe.get_cached_value("Company", company, "default_currency")


# --- coverage ----------------------------------------------------------------
def coverage(company=None):
    """The date span of what the order sync has actually fetched.

    Deliberately unfiltered by docstatus: a cancelled or draft order is data the
    sync reached, and this answers how far it reached, not what sold.

    Without this every total below lies by omission. A store whose sync has only
    ever run back to March answers "sales in January" with a confident zero, and
    nothing in the number says which of "you sold nothing" and "we have no data"
    it means.
    """
    where = ["so.sh_shopify_order_id IS NOT NULL", "so.sh_shopify_order_id != ''"]
    params = {}
    if company:
        where.append("so.company = %(company)s")
        params["company"] = company

    # Raw SQL like the rest of this module, rather than `frappe.get_all` with
    # aggregate fields: from v16 the query builder rejects a SQL function written
    # as a string in `fields` and wants `{"MIN": "transaction_date"}` instead, and
    # a module that already speaks SQL does not need a second dialect to say MIN.
    row = frappe.db.sql(
        f"""
        SELECT MIN(so.transaction_date) AS first_order_date,
               MAX(so.transaction_date) AS last_order_date,
               COUNT(so.name) AS synced_orders
        FROM `tabSales Order` so
        WHERE {" AND ".join(where)}
        """,
        params,
        as_dict=True,
    )[0]
    return {
        "first_order_date": str(row.first_order_date) if row.first_order_date else None,
        "last_order_date": str(row.last_order_date) if row.last_order_date else None,
        "synced_orders": cint(row.synced_orders),
    }


def _coverage_note(cov, date_from, date_to):
    """Why a figure might not mean what it looks like, in words the answer can pass on.

    Always returns something, unlike the Amazon version which returns None when
    the date window is fine. The paid-only filter is true of every period, so
    there is no case where this module has nothing to caveat.
    """
    first = cov["first_order_date"]
    last = cov["last_order_date"]

    if not first:
        return (
            "No Shopify orders have ever synced to this site, so every figure below is zero "
            "because there is no data -- not because nothing sold. " + PAID_ONLY_NOTE
        )

    first, last = getdate(first), getdate(last)
    if date_to < first or date_from > last:
        window = (
            f"This period lies entirely outside the synced order data, which runs "
            f"{first} to {last}. The figures below are zero because there is no data for "
            f"this period, not because nothing sold. "
        )
    elif date_from < first:
        window = (
            f"Synced order data starts {first}, after this period does. Everything before "
            f"{first} is missing rather than empty. "
        )
    else:
        window = ""

    return window + PAID_ONLY_NOTE


def _refund_count(company, date_from, date_to):
    """Credit Notes the refund sync wrote inside the period.

    Counted, never subtracted -- see the module docstring. A count is enough for
    an answer to say the gross figure is gross; netting is a different job.
    """
    return cint(
        frappe.db.sql(
            """
            SELECT COUNT(*)
            FROM `tabSales Invoice` si
            WHERE si.docstatus = 1
              AND si.is_return = 1
              AND si.sh_shopify_refund_id IS NOT NULL
              AND si.sh_shopify_refund_id != ''
              AND si.company = %(company)s
              AND si.posting_date BETWEEN %(date_from)s AND %(date_to)s
            """,
            {"company": company, "date_from": date_from, "date_to": date_to},
        )[0][0]
    )


# --- the shared WHERE --------------------------------------------------------
def _sold_where(company, date_from, date_to, financial_status=None, fulfillment_status=None):
    """The conditions every figure in this module is built on, and its params.

    See the module docstring for why `docstatus = 1` is the whole of the sold
    test here, where the Amazon connector needs a status check beside it.
    """
    where = [
        "so.docstatus = 1",
        "so.sh_shopify_order_id IS NOT NULL",
        "so.sh_shopify_order_id != ''",
        "so.company = %(company)s",
        "so.transaction_date BETWEEN %(date_from)s AND %(date_to)s",
    ]
    params = {
        "company": company,
        "date_from": date_from,
        "date_to": date_to,
    }
    if financial_status:
        where.append("so.sh_financial_status = %(financial_status)s")
        params["financial_status"] = financial_status
    if fulfillment_status:
        where.append("so.sh_fulfillment_status = %(fulfillment_status)s")
        params["fulfillment_status"] = fulfillment_status
    return where, params


# --- bucket shaping ----------------------------------------------------------
def _bucket_bounds(start, granularity, date_from, date_to):
    """One bucket's real coverage, clamped to the period it was asked for.

    A month bucket for a period starting mid-month covers half a month, and
    saying "2026-08-15 to 2026-08-31" is what makes that visible. Reporting the
    calendar month would invite a comparison against a whole one.
    """
    if granularity == "total":
        return date_from, date_to
    start = getdate(start)
    if granularity == "day":
        end = start
    elif granularity == "week":
        end = add_days(start, 6)
    else:
        end = get_last_day(start)
    return max(start, date_from), min(getdate(end), date_to)


def _series(rows, granularity, date_from, date_to):
    """Grouped SQL rows -> the bucket list, ordered, with real dates on each.

    Buckets with no qualifying orders are absent rather than zero-filled. Filling
    them would be the friendlier default for a chart and the wrong one here: a
    year of days is 365 rows of mostly nothing in a completion, and the tool
    descriptions say plainly that a missing bucket is an empty one.
    """
    out = []
    for row in rows:
        start, end = _bucket_bounds(row["bucket"], granularity, date_from, date_to)
        out.append(
            {
                "period_start": str(start),
                "period_end": str(end),
                "product_sales": flt(row.get("product_sales"), 2),
                "order_total": flt(row.get("order_total"), 2),
                "units": cint(row.get("units")),
                "order_count": cint(row.get("order_count")),
            }
        )
    return out


def _totals_from(buckets):
    """Totals as the sum of the buckets, never as a separate query.

    Two queries would let a rounding or filter difference put a total beside a
    series that does not add up to it, which reads as a bug in the data rather
    than in the tool. `avg_order_value` is computed from the summed totals, not
    averaged across buckets, because an average of averages is not one.
    """
    product_sales = flt(sum(b["product_sales"] for b in buckets), 2)
    order_count = sum(b["order_count"] for b in buckets)
    return {
        "product_sales": product_sales,
        "order_total": flt(sum(b["order_total"] for b in buckets), 2),
        "units": sum(b["units"] for b in buckets),
        "order_count": order_count,
        "avg_order_value": flt(product_sales / order_count, 2) if order_count else 0.0,
    }


def _merge_units(money_rows, unit_rows):
    """Fold the item-level unit counts into the order-level money rows.

    Two queries because one cannot answer both: `SUM(so.base_net_total)` over a
    join to the item table multiplies every order's total by its line count. So
    money and counts come from the order table, units come from the item table,
    and they meet here on the bucket key.

    A unit bucket with no money bucket cannot normally happen -- same WHERE, same
    grouping -- but if it did, dropping it would hide units that were sold. It is
    carried through with zero money instead.
    """
    units = {str(row["bucket"]): cint(row["units"]) for row in unit_rows}
    merged = []
    for row in money_rows:
        row = dict(row)
        row["units"] = units.pop(str(row["bucket"]), 0)
        merged.append(row)
    for bucket, count in units.items():
        merged.append({"bucket": bucket, "units": count})
    merged.sort(key=lambda row: str(row["bucket"]))
    return merged


def _validated_statuses(financial_status, fulfillment_status):
    """Both optional status filters, validated together."""
    if financial_status:
        financial_status = _one_of(financial_status, FINANCIAL_STATUSES, "financial status")
    if fulfillment_status:
        fulfillment_status = _one_of(fulfillment_status, FULFILLMENT_STATUSES, "fulfillment status")
    return financial_status, fulfillment_status


# --- the reads ---------------------------------------------------------------
def sales_summary(
    date_from,
    date_to=None,
    granularity="day",
    financial_status=None,
    fulfillment_status=None,
):
    """Revenue, units, orders and average order value over a period, bucketed."""
    date_from, date_to = _period(date_from, date_to)
    granularity = _one_of(granularity, GRANULARITIES, "granularity", default="day")
    financial_status, fulfillment_status = _validated_statuses(financial_status, fulfillment_status)
    _assert_bucket_count(date_from, date_to, granularity)

    company = _company()
    where, params = _sold_where(company, date_from, date_to, financial_status, fulfillment_status)
    bucket = BUCKET_SQL[granularity]
    conditions = " AND ".join(where)
    company_currency = _currency(company)

    money_rows = frappe.db.sql(
        f"""
        SELECT {bucket} AS bucket,
               COUNT(DISTINCT so.name) AS order_count,
               SUM(so.base_net_total) AS product_sales,
               SUM(so.base_grand_total) AS order_total,
               SUM(CASE WHEN (so.currency != %(company_currency)s AND so.conversion_rate = 1)
                          OR so.conversion_rate = 0
                        THEN 1 ELSE 0 END) AS fallback_rate_orders
        FROM `tabSales Order` so
        WHERE {conditions}
        GROUP BY bucket
        ORDER BY bucket
        """,
        {**params, "company_currency": company_currency},
        as_dict=True,
    )
    unit_rows = frappe.db.sql(
        f"""
        SELECT {bucket} AS bucket, SUM(soi.qty) AS units
        FROM `tabSales Order Item` soi
        INNER JOIN `tabSales Order` so ON so.name = soi.parent
        WHERE {conditions}
        GROUP BY bucket
        ORDER BY bucket
        """,
        params,
        as_dict=True,
    )

    buckets = _series(_merge_units(money_rows, unit_rows), granularity, date_from, date_to)
    totals = _totals_from(buckets)
    # A conversion rate that is 1.0 on a foreign-currency order, or 0 outright,
    # means the base columns for that order are not really company currency.
    # `upsert.py` guards this now; historical rows are why the count is reported
    # rather than assumed to be zero.
    totals["orders_at_fallback_rate"] = sum(cint(r.get("fallback_rate_orders")) for r in money_rows)
    totals["refunds"] = _refund_count(company, date_from, date_to)

    cov = coverage(company)
    return {
        "period": {
            "date_from": str(date_from),
            "date_to": str(date_to),
            "granularity": granularity,
            "financial_status": financial_status,
            "fulfillment_status": fulfillment_status,
        },
        "currency": company_currency,
        "totals": totals,
        "coverage": {**cov, "note": _coverage_note(cov, date_from, date_to)},
        "buckets": buckets,
    }


def top_selling_products(
    date_from,
    date_to=None,
    by="revenue",
    group_by="item",
    limit=None,
    financial_status=None,
    fulfillment_status=None,
):
    """The best-selling items or variants over a period, ranked.

    `item` is the default rather than `variant` because merchants think in
    products -- "what sold best" means the t-shirt, not the medium blue one --
    even though the revenue actually lands on variant lines. `variant` is there
    for when the size mix is the question.
    """
    date_from, date_to = _period(date_from, date_to)
    by = _one_of(by, ("revenue", "units"), "ranking", default="revenue")
    group_by = _one_of(group_by, ("item", "variant"), "grouping", default="item")
    financial_status, fulfillment_status = _validated_statuses(financial_status, fulfillment_status)
    limit = min(cint(limit) or TOP_DEFAULT_LIMIT, TOP_MAX_LIMIT)

    company = _company()
    where, params = _sold_where(company, date_from, date_to, financial_status, fulfillment_status)
    conditions = " AND ".join(where)

    key = "soi.item_code" if group_by == "item" else "soi.sh_shopify_variant_id"
    order = "product_sales DESC" if by == "revenue" else "units DESC"

    # Lines whose grouping key was never stamped are excluded from the ranking and
    # counted separately below: a row keyed on the empty string would rank as a
    # product, and it is several unrelated ones. That matters more for `variant`
    # than for `item` -- every line has an item_code, but a line written before
    # the variant id was mapped has no variant.
    rows = frappe.db.sql(
        f"""
        SELECT {key} AS group_key,
               MAX(soi.item_code) AS item_code,
               MAX(soi.item_name) AS item_name,
               COUNT(DISTINCT soi.sh_shopify_variant_id) AS variant_count,
               COUNT(DISTINCT so.name) AS order_count,
               SUM(soi.qty) AS units,
               SUM(soi.base_net_amount) AS product_sales
        FROM `tabSales Order Item` soi
        INNER JOIN `tabSales Order` so ON so.name = soi.parent
        WHERE {conditions} AND IFNULL({key}, '') != ''
        GROUP BY group_key
        ORDER BY {order}
        LIMIT %(limit)s
        """,
        {**params, "limit": limit},
        as_dict=True,
    )
    overall = frappe.db.sql(
        f"""
        SELECT SUM(soi.qty) AS units,
               SUM(soi.base_net_amount) AS product_sales,
               COUNT(DISTINCT CASE WHEN IFNULL({key}, '') != '' THEN {key} END) AS products,
               SUM(CASE WHEN IFNULL({key}, '') = '' THEN soi.base_net_amount ELSE 0 END)
                   AS unattributed_product_sales
        FROM `tabSales Order Item` soi
        INNER JOIN `tabSales Order` so ON so.name = soi.parent
        WHERE {conditions}
        """,
        params,
        as_dict=True,
    )[0]

    period_sales = flt(overall.product_sales, 2)
    ranked = []
    for row in rows:
        sales = flt(row.product_sales, 2)
        ranked.append(
            {
                ("item_code" if group_by == "item" else "sh_shopify_variant_id"): row.group_key,
                **(
                    {"variant_count": cint(row.variant_count)}
                    if group_by == "item"
                    else {"item_code": row.item_code}
                ),
                "item_name": row.item_name,
                "units": cint(row.units),
                "order_count": cint(row.order_count),
                "product_sales": sales,
                "share_of_product_sales": flt(sales / period_sales, 4) if period_sales else None,
            }
        )

    cov = coverage(company)
    return {
        "period": {
            "date_from": str(date_from),
            "date_to": str(date_to),
            "financial_status": financial_status,
            "fulfillment_status": fulfillment_status,
        },
        "ranking": {"by": by, "group_by": group_by, "limit": limit},
        "currency": _currency(company),
        "totals": {
            "product_sales": period_sales,
            "units": cint(overall.units),
            "products": cint(overall.products),
            "ranked_product_sales": flt(sum(r["product_sales"] for r in ranked), 2),
            "unattributed_product_sales": flt(overall.unattributed_product_sales, 2),
            "coverage_note": _coverage_note(cov, date_from, date_to),
        },
        "rows": ranked,
    }


def product_sales(
    item_code=None,
    variant_id=None,
    date_from=None,
    date_to=None,
    granularity="month",
):
    """How one item or variant sold over a period, bucketed."""
    item_code = (item_code or "").strip()
    variant_id = (variant_id or "").strip()
    if bool(item_code) == bool(variant_id):
        frappe.throw(_("Pass exactly one of item_code or variant_id."))
    date_from, date_to = _period(date_from, date_to)
    granularity = _one_of(granularity, GRANULARITIES, "granularity", default="month")
    _assert_bucket_count(date_from, date_to, granularity)

    company = _company()
    where, params = _sold_where(company, date_from, date_to)
    if item_code:
        where.append("soi.item_code = %(item_code)s")
        params["item_code"] = item_code
    else:
        where.append("soi.sh_shopify_variant_id = %(variant_id)s")
        params["variant_id"] = variant_id
    bucket = BUCKET_SQL[granularity]

    # One query, unlike sales_summary: money is per line here (base_net_amount),
    # so the join does not multiply anything and there is nothing to merge.
    rows = frappe.db.sql(
        f"""
        SELECT {bucket} AS bucket,
               COUNT(DISTINCT so.name) AS order_count,
               SUM(soi.qty) AS units,
               SUM(soi.base_net_amount) AS product_sales,
               SUM(soi.base_net_amount) AS order_total
        FROM `tabSales Order Item` soi
        INNER JOIN `tabSales Order` so ON so.name = soi.parent
        WHERE {" AND ".join(where)}
        GROUP BY bucket
        ORDER BY bucket
        """,
        params,
        as_dict=True,
    )

    buckets = _series(rows, granularity, date_from, date_to)
    totals = _totals_from(buckets)
    # `order_total` on a per-line read would just repeat product_sales -- the tax
    # rows it would add are per order, not per line -- so it is dropped rather than
    # reported as a second figure that is the same number. Dropped after the
    # totals are summed, because `_totals_from` reads the key it removes.
    for entry in buckets:
        entry.pop("order_total", None)
    totals.pop("order_total", None)

    cov = coverage(company)
    return {
        "product": {"item_code": item_code or None, "variant_id": variant_id or None},
        "period": {"date_from": str(date_from), "date_to": str(date_to), "granularity": granularity},
        "currency": _currency(company),
        "totals": {**totals, "coverage_note": _coverage_note(cov, date_from, date_to)},
        "buckets": buckets,
    }


def _baseline_period(date_from, date_to, compare_to):
    """The period to measure against.

    `previous_period` is the same number of days ending the day before this one
    starts, so a 30-day window is compared with 30 days and not with a calendar
    month of a different length. `previous_year` shifts the same dates back a
    year, which is the right comparison for anything seasonal and the wrong one
    for a window that crosses a leap day -- 365 days back, stated as dates, is
    what it is.
    """
    if compare_to == "previous_year":
        return add_days(date_from, -365), add_days(date_to, -365)
    span = (date_to - date_from).days
    end = add_days(date_from, -1)
    return add_days(end, -span), end


def _change(current, baseline):
    """Absolute and percentage movement, with no percentage invented from zero.

    Growth from nothing has no percentage -- 0 to 500 is not "infinite" or "100%"
    -- so `percent` is null there and the absolute figure carries the answer. A
    model handed a number would quote it.
    """
    out = {}
    for key in ("product_sales", "order_total", "units", "order_count", "avg_order_value"):
        now, before = flt(current.get(key)), flt(baseline.get(key))
        out[key] = {
            "current": now,
            "baseline": before,
            "absolute": flt(now - before, 2),
            "percent": flt((now - before) / abs(before) * 100, 2) if before else None,
        }
    return out


def compare_sales_periods(
    date_from,
    date_to,
    compare_to="previous_period",
    baseline_from=None,
    baseline_to=None,
    financial_status=None,
    fulfillment_status=None,
):
    """One period's totals against another's, with the deltas already computed.

    Its own tool rather than two summary calls, because the arithmetic is the
    part that goes wrong: a percentage change worked out inside a completion
    comes out plausible, unlabelled and occasionally wrong, and this is the
    question people ask most.
    """
    date_from, date_to = _period(date_from, date_to)
    if baseline_from or baseline_to:
        base_from, base_to = _period(baseline_from, baseline_to or baseline_from, label="baseline_from")
        compare_to = "explicit"
    else:
        compare_to = _one_of(compare_to, COMPARE_BASELINES, "baseline", default="previous_period")
        base_from, base_to = _baseline_period(date_from, date_to, compare_to)

    current = sales_summary(
        date_from,
        date_to,
        "total",
        financial_status=financial_status,
        fulfillment_status=fulfillment_status,
    )
    baseline = sales_summary(
        base_from,
        base_to,
        "total",
        financial_status=financial_status,
        fulfillment_status=fulfillment_status,
    )

    return {
        "current": {**current["period"], **current["totals"]},
        "baseline": {**baseline["period"], **baseline["totals"], "basis": compare_to},
        "currency": current["currency"],
        "change": _change(current["totals"], baseline["totals"]),
        "coverage": current["coverage"],
    }


def list_shopify_orders(
    date_from,
    date_to=None,
    financial_status=None,
    fulfillment_status=None,
    item_code=None,
    page_no=1,
    page_size=None,
):
    """A page of the Shopify orders behind the figures above.

    Paged and shaped like `register.list_listings` on purpose: it is the same
    move -- a total, a page, and `has_more` -- and the pack already teaches a
    model to read that shape and quote the denominator.

    Unlike every other read here this one does NOT apply the sold filter. It
    takes both status parameters, so refusing to show a cancelled or unpaid
    order would make them a lie; each row carries `counts_as_sold` instead, so a
    caller can see which rows the totals were built from and which were excluded.

    Every row carries `sh_shopify_order_name` -- the `#1015` a merchant actually
    says out loud. The Sales Order `name` is an Alaiy OS id and means nothing to
    them; the numeric `sh_shopify_order_id` means nothing to anyone.

    Two currencies land on every row, which is the price of showing an order
    rather than a total. `product_sales` and `order_total` are company currency,
    as everywhere else in this module; `order_currency` names the currency the
    buyer was actually charged in. On a single-currency store they are the same
    and the distinction costs nothing; on a multi-currency one it is the
    difference between a column that can be summed and one that cannot.
    """
    date_from, date_to = _period(date_from, date_to)
    financial_status, fulfillment_status = _validated_statuses(financial_status, fulfillment_status)
    page_no = max(cint(page_no), 1)
    page_size = min(cint(page_size) or ORDERS_PAGE_SIZE, ORDERS_MAX_PAGE_SIZE)

    company = _company()
    where = [
        "so.sh_shopify_order_id IS NOT NULL",
        "so.sh_shopify_order_id != ''",
        "so.company = %(company)s",
        "so.transaction_date BETWEEN %(date_from)s AND %(date_to)s",
    ]
    params = {"company": company, "date_from": date_from, "date_to": date_to}
    if financial_status:
        where.append("so.sh_financial_status = %(financial_status)s")
        params["financial_status"] = financial_status
    if fulfillment_status:
        where.append("so.sh_fulfillment_status = %(fulfillment_status)s")
        params["fulfillment_status"] = fulfillment_status
    if item_code:
        where.append(
            "EXISTS (SELECT 1 FROM `tabSales Order Item` soi "
            "WHERE soi.parent = so.name AND soi.item_code = %(item_code)s)"
        )
        params["item_code"] = item_code
    conditions = " AND ".join(where)

    total = frappe.db.sql(
        f"SELECT COUNT(*) FROM `tabSales Order` so WHERE {conditions}", params
    )[0][0]
    rows = frappe.db.sql(
        f"""
        SELECT so.name AS sales_order,
               so.sh_shopify_order_id,
               so.sh_shopify_order_name,
               so.transaction_date,
               so.sh_financial_status,
               so.sh_fulfillment_status,
               so.sh_delivery_method,
               so.docstatus,
               so.currency AS order_currency,
               so.base_net_total AS product_sales,
               so.base_grand_total AS order_total,
               (SELECT SUM(soi.qty) FROM `tabSales Order Item` soi WHERE soi.parent = so.name) AS units
        FROM `tabSales Order` so
        WHERE {conditions}
        ORDER BY so.transaction_date DESC, so.name DESC
        LIMIT %(page_size)s OFFSET %(offset)s
        """,
        {**params, "page_size": page_size, "offset": (page_no - 1) * page_size},
        as_dict=True,
    )

    orders = []
    for row in rows:
        orders.append(
            {
                "shopify_order_name": row.sh_shopify_order_name,
                "shopify_order_id": row.sh_shopify_order_id,
                "sales_order": row.sales_order,
                "transaction_date": str(row.transaction_date),
                "financial_status": row.sh_financial_status,
                "fulfillment_status": row.sh_fulfillment_status,
                "delivery_method": row.sh_delivery_method,
                "units": cint(row.units),
                "order_currency": row.order_currency,
                "product_sales": flt(row.product_sales, 2),
                "order_total": flt(row.order_total, 2),
                # docstatus 1 is submitted; 0 is a Shopify draft order the sync
                # left unsubmitted, 2 is one a cancellation webhook cancelled.
                # This is the whole of the sold test -- see the module docstring.
                "counts_as_sold": cint(row.docstatus) == 1,
            }
        )

    return {
        "total": cint(total),
        "page_no": page_no,
        "page_size": page_size,
        "has_more": page_no * page_size < cint(total),
        "orders": orders,
    }


def orders_sync_status():
    """Is the order sync working, and how far back does its data reach?

    The two halves belong together: a status of "completed" with a coverage
    window starting in March is a working sync that still cannot answer January,
    and either fact alone is misleading. Its own tool rather than a key on every
    result because it is also the answer to "why is this zero".
    """
    company = _company()
    cov = coverage(company)

    last_run = frappe.db.get_value(
        "Shopify Sync Log",
        {"sync_type": "orders"},
        [
            "name",
            "status",
            "trigger",
            "started_at",
            "finished_at",
            "items_processed",
            "items_created",
            "items_failed",
            "error_message",
        ],
        order_by="started_at desc",
        as_dict=True,
    )
    if last_run:
        last_run = {
            **last_run,
            "started_at": str(last_run["started_at"]) if last_run["started_at"] else None,
            "finished_at": str(last_run["finished_at"]) if last_run["finished_at"] else None,
        }

    return {
        "company": company,
        "last_run": last_run,
        "coverage": cov,
        "note": (
            PAID_ONLY_NOTE
            if cov["first_order_date"]
            else "No Shopify orders have ever synced to this site. " + PAID_ONLY_NOTE
        ),
    }
