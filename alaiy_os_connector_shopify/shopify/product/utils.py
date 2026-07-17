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
