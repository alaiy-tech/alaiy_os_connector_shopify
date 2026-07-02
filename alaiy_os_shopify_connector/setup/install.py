import frappe


def sync_connector_registry():
    """
    Register or update the Shopify connector row in alaiy_os_core's OS Connector Registry.
    Called from hooks.py -> after_migrate on every bench migrate.
    Setup (custom fields, webhooks) only runs when is_enabled is first set via the form.
    """
    _fix_settings_as_single()

    if not frappe.db.exists("DocType", "OS Connector Registry"):
        return

    from alaiy_os_shopify_connector.connector_meta import connector_meta

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


def setup_custom_fields():
    """Add Shopify custom fields to ERPNext doctypes. Called on first enable."""
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
            continue
        cf = frappe.new_doc("Custom Field")
        cf.dt = doctype
        cf.fieldname = f["fieldname"]
        cf.label = f["label"]
        cf.fieldtype = f["fieldtype"]
        cf.insert_after = f.get("insert_after", "")
        cf.search_index = 1 if f.get("search_index") else 0
        cf.read_only = 1 if f.get("read_only") else 0
        cf.module = "Alaiy OS Shopify"
        cf.insert(ignore_permissions=True)
