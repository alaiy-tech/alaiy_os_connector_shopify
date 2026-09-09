"""
Import a Shopify order's shipping/billing address into an Alaiy OS Address and
link it to the customer + Sales Order.
"""

import frappe

from alaiy_os_connector_shopify import connections

_ADDRESS_TEMPLATE = """{{ address_line1 }}<br>
{% if address_line2 %}{{ address_line2 }}<br>{% endif -%}
{{ city }}<br>
{% if state %}{{ state }}<br>{% endif -%}
{% if pincode %}{{ pincode }}<br>{% endif -%}
{{ country }}<br>
{% if phone %}Phone: {{ phone }}<br>{% endif -%}
"""


def ensure_default_address_template(connection=None):
    """
    Alaiy OS refuses to save/render ANY Address (and any Sales Order that
    references one) if there's no default Address Template -- confirmed live:
    a fresh site had none, so order import crashed with "No default Address
    Template found". Self-heal a standard one instead of making the merchant
    create it by hand.

    Not store-specific data -- one default template covers every store on the
    bench -- so `connection` here is only about which store's Company to read,
    not about isolating the template itself.
    """
    if frappe.db.exists("Address Template", {"is_default": 1}):
        return
    try:
        settings = connections.resolve(connection) if connection else connections.require_enabled()
        company = settings.sh_company or frappe.defaults.get_global_default("company")
        country = frappe.db.get_value("Company", company, "country") or "India"
        if not frappe.db.exists("Country", country):
            country = frappe.db.get_value("Country", {}, "name") or "India"
        # Address Template is named by country; reuse if one exists, else create.
        if frappe.db.exists("Address Template", country):
            frappe.db.set_value("Address Template", country, "is_default", 1)
        else:
            doc = frappe.new_doc("Address Template")
            doc.country = country
            doc.is_default = 1
            doc.template = _ADDRESS_TEMPLATE
            doc.flags.ignore_permissions = True
            doc.insert()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title="Shopify: failed to create default Address Template",
            message=frappe.get_traceback(),
        )


def sync_order_address(order, customer_name, connection=None):
    """
    Create/update an Address from the order's shipping address (falls back to
    billing), link it to the customer, return its name for the Sales Order.
    Best-effort: returns None (order still imports address-less) on any problem.
    """
    a = order.get("shipping_address") or order.get("billing_address")
    if not a or not (a.get("address1") or a.get("city")):
        return None

    try:
        # Found through the Customer link, not by address_title alone --
        # customer_name is already store-scoped (_get_or_create_customer
        # never merges two sellers' customers), but address_title is a bare
        # display name. Two sellers each with a "John Smith" customer would
        # otherwise share -- and silently overwrite -- one Address row.
        existing = frappe.db.get_value(
            "Dynamic Link",
            {"link_doctype": "Customer", "link_name": customer_name, "parenttype": "Address"},
            "parent",
        )
        if existing and frappe.db.get_value("Address", existing, "address_type") != "Shipping":
            existing = None
        addr = frappe.get_doc("Address", existing) if existing else frappe.new_doc("Address")
        addr.address_title = customer_name
        addr.address_type = "Shipping"
        addr.address_line1 = a.get("address1") or a.get("city") or "N/A"
        addr.address_line2 = a.get("address2") or ""
        addr.city = a.get("city") or ""
        addr.state = a.get("province") or ""
        addr.pincode = a.get("zip") or ""
        addr.phone = a.get("phone") or ""

        # country is a mandatory Link to Country -- use Shopify's value only if
        # it's a real Country record, else the company's country as a fallback.
        country = a.get("country")
        if not country or not frappe.db.exists("Country", country):
            settings = connections.resolve(connection) if connection else connections.require_enabled()
            country = frappe.db.get_value(
                "Company",
                settings.sh_company or frappe.defaults.get_global_default("company"),
                "country",
            ) or "India"
        addr.country = country

        if not existing:
            addr.append("links", {"link_doctype": "Customer", "link_name": customer_name})
        addr.flags.ignore_permissions = True
        addr.save()
        return addr.name
    except Exception:
        frappe.log_error(
            title=f"Shopify: failed to sync address for {customer_name}",
            message=frappe.get_traceback(),
        )
        return None
