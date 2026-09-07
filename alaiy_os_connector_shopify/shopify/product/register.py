# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""Reading the register: what is listed, what a push would send, what is missing.

Everything else under `shopify/product/` exists to *change* something -- build a
payload, push it, import a change back. This module only reads, and it exists
because the agent pack had nothing to answer from: before it, every whitelisted
method in this app was a trigger, a stat card or a CSV download, and none of
them is shaped like "which of my products have no image".

Reads `Shopify Product Listing` rows and the `Item` behind each, so answers are
as fresh as each row's `last_synced_at` and no fresher. Every result carries it
for that reason.

## The listing name is the item code

`Shopify Product Listing` is `autoname: field:item`, so the row's name and its
template Item's code are the same string. Callers pass `item_code` throughout
because that is the name a merchant recognises; nothing here needs a second
identifier, and offering both would only invite passing the wrong one.

## Why the gap queries are SQL and not the resolvers

`listing.py` has the real answer to "what would a push send" in
`effective_title`, `effective_description`, `effective_images` and
`variant_price`. Calling them is right for one listing -- `listing_details` does
exactly that -- and impossible for the whole register: each one wants a loaded
`Item` doc, and a 20k-item catalogue is 20k `get_doc` calls inside a tool call
that has to return inside a turn.

So `listing_gaps` restates each fallback chain as a SQL join. That is a real
duplication and the honest cost of the tool: **a change to a resolver in
`listing.py` has to be mirrored here**, or the gap report will disagree with
what a push actually does. The chains are short and each one is commented with
the resolver it mirrors. `tests/test_agent_pack.py` pins the pairing.

One known and deliberate imprecision: `no_image` treats an Item with a
`slideshow` set as having images without checking the slideshow actually
contains any, because confirming it is a second join per row for an edge case
that means someone built an empty slideshow. It can therefore under-report, and
the tool description says the count is a floor.
"""

import frappe
from frappe.utils import cint

LISTING_DOCTYPE = "Shopify Product Listing"
SETTINGS = "Shopify Connector Settings"

#: `Shopify Product Listing.sh_shopify_status` -- what the product's state on
#: Shopify should be. Not to be confused with the two order status vocabularies
#: in sales.py, which is why nothing here calls its parameter anything but
#: `status` and nothing there does.
LISTING_STATUSES = ("Active", "Draft", "Archived")

PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

GAP_LIMIT = 50
GAP_MAX_LIMIT = 200

#: Every gap this can report, with the resolver in `listing.py` whose fallback
#: chain each SQL condition below mirrors. Keeping the map here rather than
#: inline gives the tool schema one place to read its enum from.
GAPS = {
    "no_image": "effective_images",
    "no_description": "effective_description",
    "no_price": "variant_price",
    "no_product_type": "effective_product_type",
    "never_pushed": None,
}


def _selling_price_list():
    return frappe.db.get_single_value(SETTINGS, "sh_selling_price_list") or "Standard Selling"


# --- list --------------------------------------------------------------------
def list_listings(status=None, is_enabled=None, pushed=None, search=None, page_no=1, page_size=None):
    """A page of the register -- which products are listed and the state of each.

    The entry point: it is the only read here that answers without being handed
    an id, and everything else needs one. Before it existed the pack could only
    answer about a product someone had already named, which is a strange shape
    for a pack whose most common question is "what is wrong with my listings".
    """
    if status:
        status = str(status).strip().title()
        if status not in LISTING_STATUSES:
            frappe.throw(f"Unknown status {status}. One of: {', '.join(LISTING_STATUSES)}.")

    page_no = max(cint(page_no), 1)
    page_size = min(cint(page_size) or PAGE_SIZE, MAX_PAGE_SIZE)

    where = ["1 = 1"]
    params = {}
    if status:
        where.append("spl.sh_shopify_status = %(status)s")
        params["status"] = status
    if is_enabled is not None and str(is_enabled) != "":
        where.append("spl.is_enabled = %(is_enabled)s")
        params["is_enabled"] = cint(is_enabled)
    if pushed is not None and str(pushed) != "":
        # "Pushed" is "Shopify has given this product an id", which is the only
        # durable evidence the export ever reached it.
        where.append(
            "IFNULL(it.sh_shopify_product_id, '') != ''"
            if cint(pushed)
            else "IFNULL(it.sh_shopify_product_id, '') = ''"
        )
    if search:
        where.append(
            "(spl.item LIKE %(search)s OR spl.listing_title LIKE %(search)s "
            "OR it.item_name LIKE %(search)s OR it.sh_shopify_product_id LIKE %(search)s)"
        )
        params["search"] = f"%{search}%"
    conditions = " AND ".join(where)

    total = frappe.db.sql(
        f"""
        SELECT COUNT(*)
        FROM `tab{LISTING_DOCTYPE}` spl
        LEFT JOIN `tabItem` it ON it.name = spl.item
        WHERE {conditions}
        """,
        params,
    )[0][0]

    rows = frappe.db.sql(
        f"""
        SELECT spl.name AS item_code,
               spl.is_enabled,
               spl.sh_shopify_status AS status,
               spl.listing_price,
               spl.listing_product_type,
               spl.last_synced_at,
               it.item_name,
               it.sh_shopify_product_id AS product_id,
               it.sh_shopify_handle AS handle,
               it.has_variants,
               (SELECT COUNT(*) FROM `tabShopify Listing Variant` v
                 WHERE v.parent = spl.name AND v.is_enabled = 1) AS enabled_variants
        FROM `tab{LISTING_DOCTYPE}` spl
        LEFT JOIN `tabItem` it ON it.name = spl.item
        WHERE {conditions}
        ORDER BY spl.modified DESC
        LIMIT %(page_size)s OFFSET %(offset)s
        """,
        {**params, "page_size": page_size, "offset": (page_no - 1) * page_size},
        as_dict=True,
    )

    listings = [
        {
            "item_code": row.item_code,
            "item_name": row.item_name,
            "is_enabled": bool(cint(row.is_enabled)),
            "status": row.status or "Active",
            "product_id": row.product_id or None,
            "handle": row.handle or None,
            "pushed": bool(row.product_id),
            "listing_price": row.listing_price,
            "product_type": row.listing_product_type or None,
            "has_variants": bool(cint(row.has_variants)),
            "enabled_variants": cint(row.enabled_variants),
            "last_synced_at": str(row.last_synced_at) if row.last_synced_at else None,
        }
        for row in rows
    ]

    return {
        "total": cint(total),
        "page_no": page_no,
        "page_size": page_size,
        "has_more": page_no * page_size < cint(total),
        "listings": listings,
    }


# --- one listing -------------------------------------------------------------
def listing_details(item_code):
    """One listing's effective values -- what a push would actually send.

    The form and `listing.effective_values` answer a narrower version of this
    for the desk: seven resolved fields and an image *count*. That is right for
    a form, which already shows everything else on the screen beside it, and too
    thin for a caller holding nothing but this result -- it cannot say whether
    the product is enabled, whether it has ever been pushed, or what its variants
    cost. This returns the resolved values and the state around them.

    Deliberately more than five top-level scalar keys: `csv_export._rows_from`
    reads a dict with nested lists as an envelope only while it has at most five
    non-list keys, and this record carries `variants`, `images` and `metafields`
    while being one product. Exporting it must produce one row, not three
    variant rows. See csv_export's own note on the threshold.
    """
    from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver

    if not frappe.db.exists(LISTING_DOCTYPE, item_code):
        frappe.throw(f"No Shopify Product Listing for '{item_code}'.")
    listing = frappe.get_doc(LISTING_DOCTYPE, item_code)
    if not listing.item or not frappe.db.exists("Item", listing.item):
        frappe.throw(f"Listing '{item_code}' points at Item '{listing.item}', which does not exist.")

    item = frappe.get_doc("Item", listing.item)
    settings = frappe.get_single(SETTINGS)
    seo = listing_resolver.effective_seo(listing, item)
    images = listing_resolver.effective_images(listing, item, settings)

    variants = []
    for code in listing_resolver.enabled_variant_names(listing.name):
        variants.append(
            {
                "item_code": code,
                "price": listing_resolver.variant_price(listing, code, settings),
                "variant_id": listing_resolver.variant_shopify_id(listing, code),
                "image": listing_resolver.effective_variant_image(listing, code),
            }
        )

    return {
        "item_code": listing.name,
        "item_name": item.item_name,
        "is_enabled": bool(cint(listing.is_enabled)),
        "status": listing.sh_shopify_status or "Active",
        "product_id": item.sh_shopify_product_id or None,
        "handle": item.sh_shopify_handle or None,
        "pushed": bool(item.sh_shopify_product_id),
        "title": listing_resolver.effective_title(listing, item),
        "description": listing_resolver.effective_description(listing, item),
        "product_type": listing_resolver.effective_product_type(listing, item),
        "category": listing_resolver.effective_category(listing, item),
        "seo_title": seo["title"],
        "seo_description": seo["description"],
        "has_variants": bool(cint(item.has_variants)),
        "last_synced_at": str(listing.last_synced_at) if listing.last_synced_at else None,
        "images": images,
        "variants": variants,
        "metafields": [
            {"namespace": row.namespace, "key": row.key, "type": row.type}
            for row in (listing.metafields or [])
        ],
    }


# --- gaps --------------------------------------------------------------------
#: Each gap as the SQL that detects it, mirroring the named resolver's fallback
#: chain. See the module docstring: these must be kept in step by hand.
_GAP_SQL = {
    # effective_images: listing image rows, else item.image, else the slideshow.
    "no_image": (
        "NOT EXISTS (SELECT 1 FROM `tabShopify Listing Image` img "
        "            WHERE img.parent = spl.name AND IFNULL(img.image, '') != '') "
        "AND IFNULL(it.image, '') = '' AND IFNULL(it.slideshow, '') = ''"
    ),
    # effective_description: the listing override, else the Item's description.
    "no_description": (
        "IFNULL(spl.listing_description, '') = '' AND IFNULL(it.description, '') = ''"
    ),
    # variant_price: a variant row override, else the template listing_price for
    # a simple product, else an Item Price on the selling list. A product with
    # no priced variant at all is one the push has to skip.
    "no_price": (
        "IFNULL(spl.listing_price, 0) = 0 "
        "AND NOT EXISTS (SELECT 1 FROM `tabShopify Listing Variant` v "
        "                WHERE v.parent = spl.name AND v.is_enabled = 1 "
        "                  AND IFNULL(v.variant_price, 0) != 0) "
        "AND NOT EXISTS (SELECT 1 FROM `tabItem Price` ip "
        "                WHERE ip.price_list = %(price_list)s "
        "                  AND IFNULL(ip.price_list_rate, 0) != 0 "
        "                  AND (ip.item_code = spl.item "
        "                       OR ip.item_code IN (SELECT v2.item_variant "
        "                                             FROM `tabShopify Listing Variant` v2 "
        "                                            WHERE v2.parent = spl.name "
        "                                              AND v2.is_enabled = 1)))"
    ),
    # effective_product_type: the listing override, else the Item's.
    "no_product_type": (
        "IFNULL(spl.listing_product_type, '') = '' "
        "AND IFNULL(it.sh_shopify_product_type, '') = ''"
    ),
    # Nothing to mirror: an id from Shopify is the only evidence of a push.
    "never_pushed": "IFNULL(it.sh_shopify_product_id, '') = ''",
}


def listing_gaps(gap=None, limit=None, enabled_only=1):
    """Data-quality gaps across the register, counted and sampled.

    Not "issues". Shopify has no issues feed -- it does not adjudicate listings,
    does not suppress them, and reports nothing back about their quality. Every
    gap here is this app's own judgement about what a push would be missing, and
    the naming keeps that distinction visible: a caller must not report these as
    Shopify complaining.

    With no `gap`, returns the count of each. With one, returns the count and a
    sample of the products in it.

    `enabled_only` defaults on, because a disabled listing is one nobody intends
    to push and its gaps are not problems.
    """
    if gap:
        gap = str(gap).strip()
        if gap not in _GAP_SQL:
            frappe.throw(f"Unknown gap {gap}. One of: {', '.join(_GAP_SQL)}.")
    limit = min(cint(limit) or GAP_LIMIT, GAP_MAX_LIMIT)

    base = ["1 = 1"]
    params = {"price_list": _selling_price_list()}
    if cint(enabled_only):
        base.append("spl.is_enabled = 1")
    base_conditions = " AND ".join(base)

    from_clause = (
        f"FROM `tab{LISTING_DOCTYPE}` spl LEFT JOIN `tabItem` it ON it.name = spl.item"
    )

    counts = {}
    for name, condition in _GAP_SQL.items():
        counts[name] = cint(
            frappe.db.sql(
                f"SELECT COUNT(*) {from_clause} WHERE {base_conditions} AND ({condition})",
                params,
            )[0][0]
        )

    total = cint(
        frappe.db.sql(f"SELECT COUNT(*) {from_clause} WHERE {base_conditions}", params)[0][0]
    )

    result = {
        "scope": {
            "enabled_only": bool(cint(enabled_only)),
            "listings_considered": total,
            "price_list": params["price_list"],
        },
        "counts": counts,
        "gap": gap,
        "note": (
            "These are Alaiy OS's own judgements about what a push would be missing. "
            "Shopify reports no listing issues of its own -- there is nothing here that "
            "Shopify has complained about. `no_image` can under-report: an Item with an "
            "empty Website Slideshow counts as having images."
        ),
    }

    if not gap:
        result["listings"] = []
        return result

    rows = frappe.db.sql(
        f"""
        SELECT spl.name AS item_code, it.item_name, spl.sh_shopify_status AS status,
               it.sh_shopify_product_id AS product_id, spl.last_synced_at
        {from_clause}
        WHERE {base_conditions} AND ({_GAP_SQL[gap]})
        ORDER BY spl.modified DESC
        LIMIT %(limit)s
        """,
        {**params, "limit": limit},
        as_dict=True,
    )
    result["listings"] = [
        {
            "item_code": row.item_code,
            "item_name": row.item_name,
            "status": row.status or "Active",
            "product_id": row.product_id or None,
            "last_synced_at": str(row.last_synced_at) if row.last_synced_at else None,
        }
        for row in rows
    ]
    result["sampled"] = len(rows)
    result["truncated"] = counts[gap] > len(rows)
    return result


# --- drift -------------------------------------------------------------------
def listing_drift(item_code):
    """Has this listing changed since Alaiy OS last pushed it?

    Costs no Shopify call. `shopify/product/export.py` fingerprints the payload
    it is about to send and stores it on the `Shopify Synced Entity` row, then
    skips the push when the next fingerprint matches. This recomputes that same
    fingerprint through the same functions and compares it to the same stored
    value -- so the answer is exactly the push's own skip decision, read out
    loud instead of acted on.

    What it cannot say is **which field** changed. The Synced Entity stores the
    hash, not the canonical it was taken from, so there is nothing to diff
    against. `compare_listing` is the tool that answers that, and it costs a
    live call. This one is free and exact about the question it does answer.
    """
    from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver
    from alaiy_os_connector_shopify.shopify.product.canonical import _product_canonical

    # The same private helper the push uses. Imported rather than reimplemented
    # precisely because a second copy could disagree with the push, which is the
    # one thing this tool must never do.
    from alaiy_os_connector_shopify.shopify.product.export import _variants_of
    from alaiy_os_connector_shopify.shopify.sync_engine import entities, fingerprint

    if not frappe.db.exists(LISTING_DOCTYPE, item_code):
        frappe.throw(f"No Shopify Product Listing for '{item_code}'.")
    listing = frappe.get_doc(LISTING_DOCTYPE, item_code)
    if not listing.item or not frappe.db.exists("Item", listing.item):
        frappe.throw(f"Listing '{item_code}' points at Item '{listing.item}', which does not exist.")

    item = frappe.get_doc("Item", listing.item)
    entity = entities.get_by_erpnext("product", "Item", item.name)
    pushed_fingerprint = entity.erpnext_fingerprint if entity else None

    if not pushed_fingerprint:
        return {
            "item_code": listing.name,
            "pushed": bool(item.sh_shopify_product_id),
            "in_sync": False,
            "changed_since_push": None,
            "note": (
                "This product has never been pushed from Alaiy OS, so there is no "
                "recorded state to compare against. 'Changed' is not the right question "
                "yet -- nothing has been sent."
            ),
        }

    settings = frappe.get_single(SETTINGS)
    variants = _variants_of(item)
    if item.has_variants and not variants:
        return {
            "item_code": listing.name,
            "pushed": True,
            "in_sync": False,
            "changed_since_push": None,
            "note": (
                "Every variant row on this listing is disabled, so there is no payload to "
                "fingerprint. The push skips this product and disables the listing rather "
                "than sending a product with no variants."
            ),
        }

    current = fingerprint.fingerprint(_product_canonical(item, variants, settings, listing))
    changed = current != pushed_fingerprint

    return {
        "item_code": listing.name,
        "pushed": True,
        "in_sync": not changed,
        "changed_since_push": changed,
        "last_synced_at": str(listing.last_synced_at) if listing.last_synced_at else None,
        "note": (
            "Local data has changed since the last push, so Shopify is showing something "
            "older. This does not say which field -- use compare_listing for that, which "
            "costs a live Shopify call."
            if changed
            else "Local data matches what was last pushed. This compares Alaiy OS against "
            "its own record of the push, not against Shopify -- a change made directly in "
            "the Shopify admin would not show up here. compare_listing is the live check."
        ),
    }
