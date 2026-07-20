"""
Customer/Territory resolution -- moved verbatim from order_sync.py,
unchanged.
"""

import frappe


def _get_or_create_customer(customer_data, settings):
    shopify_id = str(customer_data.get("id", ""))
    if shopify_id:
        existing = frappe.db.get_value(
            "Customer", {"sh_shopify_customer_id": shopify_id}, "name"
        )
        if existing:
            return existing

    # .get(key, "") only falls back when the key is MISSING -- Shopify
    # sends first_name/last_name present but explicitly null fairly often
    # (observed live), which .get() happily returns as None, and .strip()
    # on None crashes the whole webhook.
    first = (customer_data.get("first_name") or "").strip()
    last = (customer_data.get("last_name") or "").strip()
    # Only use last_name if it exists and isn't the literal string "None"
    # (some Shopify integrations send "None" instead of null/empty)
    if first and last and last.lower() != "none":
        full_name = f"{first} {last}"
    else:
        full_name = first or customer_data.get("email", "") or f"Shopify {shopify_id}"

    if frappe.db.exists("Customer", full_name):
        return full_name

    c = frappe.new_doc("Customer")
    c.customer_name = full_name
    c.customer_type = "Individual"
    c.customer_group = settings.sh_customer_group or "All Customer Groups"
    c.territory = _resolve_default_territory(settings)
    if shopify_id:
        c.sh_shopify_customer_id = shopify_id
    c.flags.ignore_permissions = True
    c.insert()
    frappe.db.commit()
    return c.name


def _resolve_default_territory(settings):
    """
    "All Territories" is Alaiy OS's usual seeded root, but nothing guarantees
    it exists under that exact name on every site (renamed, demo data never
    loaded, or a from-scratch site with zero Territory rows at all --
    confirmed live on a real site). Order import must never hard-fail over
    a missing master record the merchant didn't know they needed, so this
    self-heals: configured setting, then the conventional name if present,
    then any existing Territory, then create a root one as a last resort.
    """
    if settings.sh_default_territory:
        return settings.sh_default_territory
    if frappe.db.exists("Territory", "All Territories"):
        return "All Territories"
    fallback = frappe.db.get_value("Territory", {}, "name")
    if fallback:
        return fallback
    return _create_root_territory()


def _create_root_territory():
    territory = frappe.new_doc("Territory")
    territory.territory_name = "All Territories"
    territory.is_group = 1
    territory.flags.ignore_permissions = True
    territory.insert()
    frappe.db.commit()
    return territory.name
