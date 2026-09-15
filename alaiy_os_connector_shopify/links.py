# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""Shopify URLs, for a caller that has been asked for a link rather than for data.

Everything else in this app answers with ids and fields. A person who wants to
*see* a product wants one of two pages, and they are not interchangeable:

    https://<shop>/admin/products/<product id>   the merchant's own editor
    https://<shop>/products/<handle>             the buyer's product page

The admin page routes on the **numeric product id**, which only exists once the
product has actually been pushed -- `sh_shopify_product_id` is empty on every
listing the export has not reached yet. The storefront page routes on the
**handle**, which Shopify assigns on creation and which the importer writes back
to `Item.sh_shopify_handle`. Neither is derivable from the other, and a listing
can legitimately have the first and not the second.

No HTTP call and nothing read from Shopify -- the ids are already on the row and
the host is configuration, so a link costs a string format. Deliberately not
inside `shopify/`: everything there talks to Shopify, and a reader who found a
URL builder among those modules would reasonably assume this one did too.

## Why a missing piece is an absence and not a fallback

A listing with no `sh_shopify_product_id` has never been pushed. The tempting
fallback -- link to the admin product *list* instead -- hands a person a page
that loads fine and does not contain what they asked for, which reads as "the
product is gone" rather than "it was never sent". Same for a missing handle.
Both come back `None` beside a `note` saying which, because a broken link is
worse than a stated absence: it looks like the answer was known.

## The storefront link is the myshopify one

`sh_shop_url` is the `*.myshopify.com` host the Admin API is addressed at. A
merchant on a custom domain is not serving the buyer page from it, and this app
stores that domain nowhere -- `shop.primaryDomain` is not in any query here. The
myshopify URL redirects to the custom domain rather than 404ing, so the link
works; it just is not the URL the merchant would recognise. `storefront_note`
says so, rather than the caller having to know.
"""

import frappe

_ADMIN_PATH = "admin/products"
_STOREFRONT_PATH = "products"

_STOREFRONT_NOTE = (
    "This is the myshopify.com address. If the store serves a custom domain, "
    "this URL redirects to it rather than being the address the merchant would "
    "recognise -- the custom domain is not stored in Alaiy OS."
)


def shop_host():
    """The store's host, scheme included, with no trailing slash.

    `sh_shop_url` is stored however whoever configured the site typed it, with
    or without a scheme -- `graphql_client` normalises the same way before
    building its endpoint. Returns None rather than throwing, because a link is
    a convenience and an unconfigured site should get an absence here, not an
    exception in the middle of an otherwise fine answer.
    """
    shop_url = (frappe.db.get_single_value("Shopify Connector Settings", "sh_shop_url") or "").strip()
    shop_url = shop_url.rstrip("/")
    if not shop_url:
        return None
    if not shop_url.startswith("http"):
        shop_url = f"https://{shop_url}"
    return shop_url


def admin_link(product_id):
    """The merchant's product editor, or None if this listing was never pushed."""
    host = shop_host()
    if not host or not product_id:
        return None
    return f"{host}/{_ADMIN_PATH}/{product_id}"


def storefront_link(handle):
    """The buyer's product page, or None if Shopify never gave us a handle."""
    host = shop_host()
    if not host or not handle:
        return None
    return f"{host}/{_STOREFRONT_PATH}/{handle}"


def listing_link(item_code=None, product_id=None):
    """Both links for one product, and a note for whichever could not be built.

    Takes an `item_code` and reads the ids off the register, or a `product_id`
    directly for a caller that already holds one -- the second form cannot build
    a storefront link, because the handle lives on the Item and nothing here
    maps an id back to it without the look-up the first form already does.
    """
    if not item_code and not product_id:
        frappe.throw("Pass an item_code or a product_id.")

    handle = None
    notes = []

    if item_code:
        row = frappe.db.get_value(
            "Item", item_code, ["sh_shopify_product_id", "sh_shopify_handle"], as_dict=True
        )
        if not row:
            frappe.throw(f"No Item '{item_code}'.")
        product_id = product_id or row.sh_shopify_product_id
        handle = row.sh_shopify_handle

    if not shop_host():
        notes.append("No Shopify shop URL is configured, so neither link can be built.")
    else:
        if not product_id:
            notes.append(
                "No Shopify product id on this row, so it has never been pushed and "
                "has no admin page yet."
            )
        if not handle:
            notes.append(
                "No Shopify handle on this row, so there is no storefront page -- "
                "Shopify assigns the handle when the product is created."
                if item_code
                else "Called with a product id alone, which cannot resolve a storefront handle."
            )

    return {
        "item_code": item_code,
        "product_id": product_id,
        "handle": handle,
        "admin_url": admin_link(product_id),
        "storefront_url": storefront_link(handle),
        "storefront_note": _STOREFRONT_NOTE if handle and shop_host() else None,
        "note": " ".join(notes) or None,
    }
