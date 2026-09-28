"""
The review queue for Shopify Enriched Listing -- what the "Enrichment" list
page reads. Shopify Enriched Listing has no `connection` field of its own
(it's keyed by item_code, one row per product, and a product belongs to
exactly one store via its Shopify Product Listing), so scoping by store
means joining through the Listing rather than filtering the doctype
directly -- the generic REST list can't do that join.
"""

import frappe

from alaiy_os_connector_shopify.listing.handlers import ENRICHED_DOCTYPE, LISTING_DOCTYPE


@frappe.whitelist()
def list_enriched_listings(status=None, connection=None):
    """
    Enriched listings for the review queue, newest first.

    Excludes Draft by default (status=None still means "not Draft"): a Draft
    is retouch-only work nobody has asked a human to read yet -- see
    ensure_enriched_listing's own docstring. Pass status="Draft" explicitly
    to see those anyway.
    """
    frappe.has_permission(ENRICHED_DOCTYPE, "read", throw=True)

    conditions = ["e.status != 'Draft'"] if not status else ["e.status = %(status)s"]
    values = {"status": status} if status else {}

    if connection:
        conditions.append("l.connection = %(connection)s")
        values["connection"] = connection

    where = " AND ".join(conditions)
    return frappe.db.sql(
        f"""
        SELECT e.name, e.item_code, e.status, e.title, e.confidence,
               e.image_status, e.needs_review, e.modified,
               l.connection
        FROM `tab{ENRICHED_DOCTYPE}` e
        LEFT JOIN `tab{LISTING_DOCTYPE}` l ON l.item = e.item_code
        WHERE {where}
        ORDER BY e.modified DESC
        LIMIT 200
        """,
        values,
        as_dict=True,
    )
