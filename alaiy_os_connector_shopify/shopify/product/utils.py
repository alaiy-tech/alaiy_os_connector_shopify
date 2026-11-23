"""
Small shared utility -- moved verbatim from product_sync.py, unchanged.
"""

from zoneinfo import ZoneInfo

import frappe


def _to_utc_naive(dt):
    """
    Normalize a datetime to naive UTC so two datetimes from different
    sources can be compared safely. Shopify's updated_at parses to a
    timezone-AWARE datetime (it carries a UTC offset); Frappe's own
    Datetime fields (e.g. Shopify Synced Entity.last_synced_at) are
    always naive, implicitly in the site's system timezone. Comparing
    aware to naive directly raises TypeError.
    """
    if dt.tzinfo is not None:
        return dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    system_tz = ZoneInfo(frappe.utils.get_system_timezone())
    return dt.replace(tzinfo=system_tz).astimezone(ZoneInfo("UTC")).replace(tzinfo=None)


_ITEM_NAME_MAX_LENGTH = 140


def _fit_item_name(name: str) -> str:
    """Item.item_name and Shopify Product Listing.listing_title are plain Data
    fields (140-char limit) -- a long real product title (confirmed live)
    crashes the whole product's import or webhook update over a display name,
    same class of bug already fixed for sh_seo_title and downloaded image
    filenames."""
    return (name or "")[:_ITEM_NAME_MAX_LENGTH]
