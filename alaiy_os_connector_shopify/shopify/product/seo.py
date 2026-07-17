"""
SEO title/description default helper -- moved verbatim from
product_sync.py, unchanged.
"""

import frappe


def _seo_values(item) -> dict:
    """
    Shopify's own admin shows the product title/description as the SEO
    title/description whenever no explicit override is set -- mirror that
    default instead of pushing nothing when our fields are blank. The
    description default is Item.description, which is HTML (imported from
    body_html) -- an SEO meta description must be plain text, and Shopify
    caps it at 320 chars in its own admin.

    Shared by _product_set_input (what gets pushed) and _product_canonical
    (what gets fingerprinted) -- if these two ever computed defaults
    differently, every push would see a phantom "change" and re-push
    forever, or worse, never notice a real one.
    """
    title = (item.get("sh_seo_title") or item.item_name or "").strip()
    description = item.get("sh_seo_description") or frappe.utils.strip_html_tags(item.description or "")
    description = (description or "").strip()[:320]
    return {"title": title, "description": description}
