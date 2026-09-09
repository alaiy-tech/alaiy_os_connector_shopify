"""
Customer/Territory resolution.

`settings` is the Shopify Connection the order came from, which is what scopes
the lookups here: a Shopify customer id is only unique inside one shop, so two
sellers both have a customer 12345.
"""

import frappe

from alaiy_os_connector_shopify.shopify.scoping import owned_by


def _get_or_create_customer(customer_data, settings):
    connection = getattr(settings, "name", None)
    shopify_id = str(customer_data.get("id", ""))
    if shopify_id:
        existing = frappe.db.get_value(
            "Customer",
            owned_by("Customer", connection, {"sh_shopify_customer_id": shopify_id}),
            "name",
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

    # Matching an existing Customer by display name, deliberately only when
    # this store is the only one on the bench.
    #
    # Two sellers each with a "John Smith" are two different people, and
    # returning the first seller's Customer for the second seller's order
    # attaches one merchant's buyer -- with their address, contact and order
    # history -- to another merchant's books. There is no way to tell the two
    # apart from a name, so on a bench with several stores this does not try:
    # it creates a Customer for this store instead.
    #
    # The single-store path is left exactly as it was. It is how a bench that
    # has been running for months keeps matching the customers it already has,
    # including the ones created before the connector recorded Shopify ids.
    if _is_only_store(connection) and frappe.db.exists("Customer", full_name):
        return full_name

    c = frappe.new_doc("Customer")
    c.customer_name = full_name
    c.customer_type = "Individual"
    c.customer_group = settings.sh_customer_group or "All Customer Groups"
    c.territory = _resolve_default_territory(settings)
    if shopify_id:
        c.sh_shopify_customer_id = shopify_id
    if connection:
        c.sh_shopify_connection = connection
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


def _is_only_store(connection) -> bool:
    """
    True when this bench holds at most one Shopify store.

    Guards the name match above. Kept as its own function because the reason
    is not obvious from the call: it is not asking "is this connection valid",
    it is asking "could a name collision here be two different people".
    """
    from alaiy_os_connector_shopify import connections

    return len(connections.names()) <= 1
