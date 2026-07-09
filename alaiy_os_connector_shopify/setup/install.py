import json

import frappe


def sync_connector_registry():
    """
    Register or update the Shopify connector row in alaiy_os_core's OS Connector Registry.
    Called from hooks.py -> after_migrate on every bench migrate. Webhook
    registration still only runs when is_enabled is first set via the form,
    but custom fields are ensured on every migrate (idempotent) so a newly
    added field lands on sites that already had the connector enabled.
    """
    _fix_settings_as_single()
    setup_custom_fields()
    _backfill_singles_defaults("Shopify Connector Settings", [
        "sh_token_refresh_interval",
        "sh_push_description", "sh_push_vendor", "sh_push_product_type", "sh_push_images",
    ])
    _ensure_list_view_column("Item", "sync_to_shopify", "Sync to Shopify")

    if not frappe.db.exists("DocType", "OS Connector Registry"):
        return

    from alaiy_os_connector_shopify.connector_meta import connector_meta

    connector_id = connector_meta["connector_id"]

    if frappe.db.exists("OS Connector Registry", connector_id):
        doc = frappe.get_doc("OS Connector Registry", connector_id)
    else:
        doc = frappe.new_doc("OS Connector Registry")

    RUNTIME_FIELDS = {"connection_status", "last_tested_at"}

    if doc.is_new():
        for key, val in connector_meta.items():
            if hasattr(doc, key):
                doc.set(key, val)
        doc.insert(ignore_permissions=True)
    else:
        for key, val in connector_meta.items():
            if key not in RUNTIME_FIELDS and hasattr(doc, key):
                doc.set(key, val)
        doc.save(ignore_permissions=True)

    frappe.db.commit()
    _update_alaiy_os_sidebar()


def _update_alaiy_os_sidebar():
    """
    Re-run alaiy_os_core's workspace/sidebar provisioning so this connector's
    Logs link and Connectors entry (settings button + card) appear right
    after it registers, instead of waiting for the next full bench migrate.
    """
    try:
        from alaiy_os_core.setup.install import (
            create_or_update_workspace_sidebar,
            create_or_update_os_settings_workspace,
            create_or_update_os_settings_workspace_sidebar,
        )
        create_or_update_workspace_sidebar()
        create_or_update_os_settings_workspace()
        create_or_update_os_settings_workspace_sidebar()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title="Shopify connector: sidebar update failed",
            message=frappe.get_traceback(),
        )


def _fix_settings_as_single():
    frappe.db.sql(
        "UPDATE `tabDocType` SET issingle=1 WHERE name='Shopify Connector Settings' AND issingle=0"
    )
    frappe.db.commit()


def _backfill_singles_defaults(doctype, fieldnames):
    """
    A field's `default` in its DocType/Custom Field JSON only applies when a
    NEW document is created. For a Single doctype's one pre-existing row,
    adding a field with a default later does not retroactively populate it --
    it silently reads back empty forever unless the admin happens to open
    and save the form. Backfill it here instead, once, idempotently.

    Checks row EXISTENCE in tabSingles directly rather than via
    get_single_value()/the ORM -- for a Check field, "never set" and
    "explicitly set to 0" both read back as plain 0, indistinguishable by
    value alone. Only an actual missing row means "never set".
    """
    meta = frappe.get_meta(doctype)
    for fieldname in fieldnames:
        already_set = frappe.db.sql(
            "SELECT 1 FROM `tabSingles` WHERE doctype=%s AND field=%s LIMIT 1",
            (doctype, fieldname),
        )
        if already_set:
            continue
        field = meta.get_field(fieldname)
        if not field or field.default in (None, ""):
            continue
        frappe.db.set_single_value(doctype, fieldname, field.default)
    frappe.db.commit()


def _ensure_list_view_column(doctype, fieldname, label):
    """
    A doctype's `List View Settings` row, once it exists (created the first
    time anyone customizes columns), takes over from the "show every
    in_list_view field automatically" default -- a newly added in_list_view
    field then never appears until someone re-adds it by hand. Item already
    has a customized column set on this site, so append our field to it
    instead of relying on the automatic behavior.
    """
    if not frappe.db.exists("List View Settings", doctype):
        return  # no customization yet -- in_list_view alone is enough
    settings = frappe.get_doc("List View Settings", doctype)
    fields = json.loads(settings.fields or "[]")
    if any(f.get("fieldname") == fieldname for f in fields):
        return
    fields.append({"fieldname": fieldname, "label": label})
    settings.fields = json.dumps(fields)
    settings.save(ignore_permissions=True)
    frappe.db.commit()


def setup_custom_fields():
    """Add Shopify custom fields to ERPNext doctypes. Idempotent -- safe to call on every migrate."""
    item_fields = [
        {
            "fieldname": "sh_shopify_product_id",
            "label": "Shopify Product ID",
            "fieldtype": "Data",
            "search_index": 1,
            "insert_after": "item_code",
        },
        {
            "fieldname": "sh_shopify_variant_id",
            "label": "Shopify Variant ID",
            "fieldtype": "Data",
            "search_index": 1,
            "insert_after": "sh_shopify_product_id",
        },
        {
            "fieldname": "sync_to_shopify",
            "label": "Sync to Shopify",
            "fieldtype": "Check",
            "default": "0",
            "in_list_view": 1,
            "insert_after": "disabled",
            "description": "Push this Item to Shopify as a product/variant. Variants inherit this flag from their template -- checking/unchecking it on a variant itself has no effect. Unchecking on a template archives the product on Shopify (kept, hidden from sales channels); re-checking unarchives and re-syncs it.",
        },
    ]
    sales_order_fields = [
        {
            "fieldname": "sh_shopify_order_id",
            "label": "Shopify Order ID",
            "fieldtype": "Data",
            "search_index": 1,
            "insert_after": "customer",
        },
        {
            "fieldname": "sh_shopify_order_name",
            "label": "Shopify Order #",
            "fieldtype": "Data",
            "read_only": 1,
            "insert_after": "sh_shopify_order_id",
        },
    ]
    customer_fields = [
        {
            "fieldname": "sh_shopify_customer_id",
            "label": "Shopify Customer ID",
            "fieldtype": "Data",
            "search_index": 1,
            "insert_after": "customer_name",
        },
    ]

    _ensure_custom_fields("Item", item_fields)
    _ensure_custom_fields("Sales Order", sales_order_fields)
    _ensure_custom_fields("Customer", customer_fields)
    frappe.db.commit()


def _ensure_custom_fields(doctype, fields):
    for f in fields:
        key = f"{doctype}-{f['fieldname']}"
        if frappe.db.exists("Custom Field", key):
            # Keep the description in sync even for a field that already
            # exists -- it's just documentation, safe to overwrite.
            if f.get("description"):
                frappe.db.set_value("Custom Field", key,
                                    "description", f["description"])
            continue
        cf = frappe.new_doc("Custom Field")
        cf.dt = doctype
        cf.fieldname = f["fieldname"]
        cf.label = f["label"]
        cf.fieldtype = f["fieldtype"]
        cf.insert_after = f.get("insert_after", "")
        cf.search_index = 1 if f.get("search_index") else 0
        cf.read_only = 1 if f.get("read_only") else 0
        cf.in_list_view = 1 if f.get("in_list_view") else 0
        cf.default = f.get("default")
        cf.description = f.get("description", "")
        cf.module = "Alaiy OS Shopify"
        cf.insert(ignore_permissions=True)
