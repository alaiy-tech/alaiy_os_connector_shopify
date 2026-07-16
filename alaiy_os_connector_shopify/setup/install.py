import json

import frappe


def sync_connector_registry():
    """
    Register or update the Shopify connector row in alaiy_os's OS Connector Registry.
    Called from hooks.py -> after_migrate on every bench migrate. Webhook
    registration still only runs when is_enabled is first set via the form,
    but custom fields are ensured on every migrate (idempotent) so a newly
    added field lands on sites that already had the connector enabled.
    """
    _fix_settings_as_single()
    setup_custom_fields()
    _lock_disabled_field_on_variants()
    _backfill_singles_defaults("Shopify Connector Settings", [
        "sh_token_refresh_interval",
        "sh_push_description", "sh_push_vendor", "sh_push_product_type", "sh_push_images",
    ])
    _ensure_list_view_column("Item", "sync_to_shopify", "Sync to Shopify")
    _ensure_list_view_column("Sales Order", "sh_shopify_order_name", "Shopify Order #")
    _ensure_list_view_column("Sales Order", "sh_fulfillment_status", "Shopify Fulfillment Status")
    _ensure_list_view_column("Sales Order", "sh_financial_status", "Shopify Financial Status")
    _drop_orphaned_singles_value("Shopify Connector Settings", "sh_api_version")

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
    Re-run alaiy_os's workspace/sidebar provisioning so this connector's
    Logs link and Connectors entry (settings button + card) appear right
    after it registers, instead of waiting for the next full bench migrate.
    """
    try:
        from alaiy_os.setup.install import (
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


def _drop_orphaned_singles_value(doctype, fieldname):
    """
    Removing a field from a DocType's JSON doesn't clean up its old stored
    value on a site that already had one -- it just becomes an orphaned,
    invisible row in tabSingles. Delete it explicitly (e.g. sh_api_version,
    removed in favor of a hardcoded SHOPIFY_API_VERSION constant -- it was
    merchant-editable, which meant a stale/wrong value could silently break
    every API call without any code change to point to).
    """
    frappe.db.sql(
        "DELETE FROM `tabSingles` WHERE doctype=%s AND field=%s",
        (doctype, fieldname),
    )
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
    # variant_of is itself a Link to Item -- fetch_from lets a variant
    # auto-pull these values from its template the moment variant_of is
    # set, and read_only_depends_on locks them from manual edit on a
    # variant while leaving them freely editable on the template (where
    # variant_of is blank). Both together satisfy "shows on variant rows,
    # not independently editable there."
    item_fields = [
        {
            "fieldname": "sh_shopify_product_id",
            "label": "Shopify Product ID",
            "fieldtype": "Data",
            "search_index": 1,
            "read_only": 1,
            "fetch_from": "variant_of.sh_shopify_product_id",
            "insert_after": "item_code",
            "description": "Set by the connector when this product is created on or imported from Shopify. Never hand-edited.",
        },
        {
            "fieldname": "sh_shopify_variant_id",
            "label": "Shopify Variant ID",
            "fieldtype": "Data",
            "search_index": 1,
            "read_only": 1,
            "insert_after": "sh_shopify_product_id",
            "description": "Set by the connector when this variant is created on or imported from Shopify. Never hand-edited.",
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
        {
            "fieldname": "sh_shopify_tags",
            "label": "Shopify Tags",
            "fieldtype": "Small Text",
            "insert_after": "sync_to_shopify",
            "fetch_from": "variant_of.sh_shopify_tags",
            "read_only_depends_on": "eval:doc.variant_of",
            "description": "Comma-separated tags, synced both directions with Shopify's product tags field. Fetched from the template on variants -- edit on the template.",
        },
        {
            "fieldname": "sh_shopify_category",
            "label": "Shopify Category",
            "fieldtype": "Data",
            "insert_after": "sh_shopify_tags",
            "fetch_from": "variant_of.sh_shopify_category",
            "read_only_depends_on": "eval:doc.variant_of",
            "description": "Shopify's Standard Product Taxonomy category name. Synced both directions -- outbound resolves this name against Shopify's taxonomy search, so it must match an existing taxonomy category name exactly (case-insensitive) to take effect. Fetched from the template on variants -- edit on the template.",
        },
        {
            "fieldname": "sh_shopify_product_type",
            "label": "Shopify Product Type",
            "fieldtype": "Data",
            "insert_after": "sh_shopify_category",
            "fetch_from": "variant_of.sh_shopify_product_type",
            "read_only_depends_on": "eval:doc.variant_of",
            "description": "Shopify's product_type field, kept separate from Item Group so renaming/reorganizing Item Group locally never affects Shopify. Synced both directions. Fetched from the template on variants -- edit on the template.",
        },
        {
            "fieldname": "sh_seo_title",
            "label": "Shopify SEO Title",
            "fieldtype": "Data",
            "insert_after": "sh_shopify_product_type",
            "description": "Defaults to the Item Name if left blank.",
        },
        {
            "fieldname": "sh_seo_description",
            "label": "Shopify SEO Description",
            "fieldtype": "Small Text",
            "insert_after": "sh_seo_title",
            "description": "Defaults to the Description if left blank.",
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
        {
            "fieldname": "sh_financial_status",
            "label": "Shopify Financial Status",
            "fieldtype": "Data",
            "read_only": 1,
            "in_list_view": 1,
            "insert_after": "sh_shopify_order_name",
        },
        {
            "fieldname": "sh_fulfillment_status",
            "label": "Shopify Fulfillment Status",
            "fieldtype": "Data",
            "read_only": 1,
            "in_list_view": 1,
            "insert_after": "sh_financial_status",
        },
    ]
    sales_order_item_fields = [
        {
            "fieldname": "sh_shopify_variant_id",
            "label": "Shopify Variant ID",
            "fieldtype": "Data",
            "search_index": 1,
            "insert_after": "item_code",
            "description": "Shopify variant ID for this line item. Used to match items when syncing order modifications from Shopify.",
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
    delivery_note_fields = [
        {
            "fieldname": "sh_shopify_fulfillment_id",
            "label": "Shopify Fulfillment ID",
            "fieldtype": "Data",
            "search_index": 1,
            "read_only": 1,
            "description": "Set when this Delivery Note was auto-created from a Shopify fulfillment event. Prevents the same fulfillment from ever creating a duplicate Delivery Note.",
            "insert_after": "customer",
        },
    ]

    custom_fields = {
        "Item": item_fields,
        "Sales Order": sales_order_fields,
        "Sales Order Item": sales_order_item_fields,
        "Customer": customer_fields,
        "Delivery Note": delivery_note_fields,
    }
    # Stamp each field with this app's module so they export under our
    # fixtures, matching how they were created before.
    for fields in custom_fields.values():
        for f in fields:
            f.setdefault("module", "Alaiy OS Connector Shopify")

    # update=True re-syncs properties (description, read_only, ...) on
    # already-existing fields, which is what the old hand-rolled upsert did
    # -- e.g. sh_shopify_category started read-only and later became editable.
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()

    _remove_deprecated_item_fields()


def _remove_deprecated_item_fields():
    """
    sh_country_of_origin and sh_harmonized_system_code were removed from
    scope -- delete the Custom Field itself (not just stop creating it),
    since create_custom_fields only ever adds/updates, never removes.
    """
    for fieldname in ("sh_country_of_origin", "sh_harmonized_system_code"):
        name = f"Item-{fieldname}"
        if frappe.db.exists("Custom Field", name):
            frappe.delete_doc("Custom Field", name, ignore_permissions=True)
    frappe.db.commit()


def _lock_disabled_field_on_variants():
    """
    Item.disabled is a core field, not one of ours, so create_custom_fields
    can't touch it -- a Property Setter is the correct mechanism for
    changing a core field's behavior. Locks it to read-only specifically
    on variant rows (variant_of set); a template's own disabled checkbox
    stays freely editable, and toggling it is what on_item_change reads
    to decide whether to archive the whole product on Shopify.
    """
    frappe.make_property_setter(
        {
            "doctype": "Item",
            "fieldname": "disabled",
            "property": "read_only_depends_on",
            "value": "eval:doc.variant_of",
            "property_type": "Code",
        },
        validate_fields_for_doctype=False,
    )
