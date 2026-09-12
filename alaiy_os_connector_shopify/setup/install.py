import json

import frappe


def after_install():
    """Everything a fresh install needs, in the order it needs it."""
    _provision()


def after_migrate():
    """The same, because every step is idempotent by construction.

    The ordering is the reason this is a function rather than a list of entries
    in hooks.py: `sync_agent_registry` writes tool rows carrying `connector =
    "shopify"`, and the OS Agent Tool child controller resolves that Link on
    save, so the connector row has to exist first. A hooks list expresses that
    ordering by accident of line order; here it is expressed once, on purpose.
    """
    _provision()


def _provision():
    """Roles, the connector row, the agent pack, and the enrichment field.

    One agent is registered from here: `sync_agent_registry` writes the read-only
    question-answering pack (pack_meta.py). The listing agent is not ours --
    `alaiy_os_agents` owns it and reaches this connector through the
    `listing_channels` hook, so all this app provides for it is the adapter in
    listing/channel.py and the field the review record writes back.
    """
    adopt_enriched_listing_doctypes()
    ensure_base_data()
    sync_connector_registry()
    sync_agent_registry()
    sync_listing_custom_fields()


#: The Module Def the enriched-listing doctypes must belong to for this app to
#: keep them, and for `alaiy_os_agent_shopify_listing`'s uninstall not to drop
#: them. See adopt_enriched_listing_doctypes.
LISTING_MODULE = "Alaiy OS Connector Shopify"

#: The parent and its three child tables. The children matter as much as the
#: parent -- they are separate doctypes with their own tables, so a parent that
#: survived while `tabShopify Enriched Listing Attribute` was dropped would leave
#: every listing with no attributes and no variants.
ENRICHED_DOCTYPES = (
    "Shopify Enriched Listing",
    "Shopify Enriched Listing Attribute",
    "Shopify Enriched Listing Image",
    "Shopify Enriched Listing Variant",
)


def adopt_enriched_listing_doctypes():
    """Make sure the enriched-listing doctypes belong to THIS app's module.

    Without this, uninstalling `alaiy_os_agent_shopify_listing` DROPS THE TABLES
    and every enrichment on the site goes with them.

    `frappe.installer.remove_app` reads no JSON file. It takes the `Module Def`
    rows belonging to the app being removed and, for each, does

        frappe.get_all("DocType", filters={"module": module_name})
        ...
        frappe.db.sql_ddl(f"DROP TABLE IF EXISTS `tab{doctype}`")

    So survival turns on one field on one row in the site database --
    `DocType.module` -- at the instant the uninstall runs. On a site that
    enriched anything before the migration that field still names the old app,
    which is the app that created it: adopting the doctype JSONs into this one
    changed the files, not the database.

    ## Why this runs on every migrate and not just once

    It began as a patch, and a patch was not enough. Patches are recorded in
    `Patch Log` and never run again, while `sync_all()` re-imports every
    installed app's doctype JSONs on every migrate -- and while the old app is
    still installed, its JSON claims these same four doctypes for its own
    module. One migrate to adopt them, a second migrate that re-imported the old
    app's copy, and the field would be back to the old app with the patch marked
    done. The uninstall after that drops the tables.

    `after_migrate` runs in `post_schema_updates`, after patches AND after
    `sync_all()`, so putting it here makes it the last word on every single
    migrate rather than on one of them.

    Idempotent, and a no-op on a site that never had the old app: it writes only
    where the value is not already ours. Safe to keep permanently -- once the old
    app is gone nothing sets the field back, and this finds nothing to do.
    """
    if not frappe.db.exists("Module Def", LISTING_MODULE):
        # This app's own module is created by its install. If it is not here yet
        # there is nothing to move the doctypes onto; the next migrate catches it.
        return

    moved = []
    for doctype in ENRICHED_DOCTYPES:
        if not frappe.db.exists("DocType", doctype):
            # Never installed on this site, or already dropped. Either way there
            # is nothing to rescue and nothing to fail over.
            continue
        if frappe.db.get_value("DocType", doctype, "module") == LISTING_MODULE:
            continue

        # set_value rather than a document save: this is one field on a DocType
        # row, and saving a DocType re-runs the schema updater over a table a
        # migration has no reason to rewrite.
        frappe.db.set_value("DocType", doctype, "module", LISTING_MODULE, update_modified=False)
        moved.append(doctype)

    if moved:
        # Worth a line in the migrate output. Whoever is reading it is often
        # about to uninstall the old app, and this is the step that makes that
        # safe.
        print(f"Adopted {len(moved)} enriched-listing doctype(s) onto {LISTING_MODULE}: {', '.join(moved)}")

    frappe.db.commit()


def ensure_base_data():
    """Create this app's roles if they are missing. Safe to run repeatedly."""
    _create_roles()
    frappe.db.commit()


def _create_roles():
    from alaiy_os_connector_shopify.roles import APP_ROLES

    for role_name in APP_ROLES:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc(
                {
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1,
                }
            ).insert(ignore_permissions=True)


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
    _unlock_disabled_field_on_variants()
    _backfill_singles_defaults("Shopify Connector Settings", [
        "sh_token_refresh_interval",
        "sh_auto_sales_invoice", "sh_invoice_trigger",
        # Confirmed live: never backfilled on a site whose Settings singleton
        # predated these fields -- read back as 0, not None, so status.py's
        # own _selected() safeguard (written for the None case) didn't catch
        # it, and every export was silently blocked regardless of status.
        "sh_import_status_active", "sh_import_status_draft", "sh_import_status_archived",
        "sh_export_status_active", "sh_export_status_draft", "sh_export_status_archived",
    ])
    _drop_orphaned_singles_value("Shopify Connector Settings", "sh_push_description")
    _drop_orphaned_singles_value("Shopify Connector Settings", "sh_push_vendor")
    _drop_orphaned_singles_value("Shopify Connector Settings", "sh_push_product_type")
    _drop_orphaned_singles_value("Shopify Connector Settings", "sh_push_images")
    _ensure_list_view_column("Sales Order", "sh_shopify_order_name", "Shopify Order #")
    _ensure_list_view_column("Sales Order", "sh_fulfillment_status", "Shopify Fulfillment Status")
    _ensure_list_view_column("Sales Order", "sh_financial_status", "Shopify Financial Status")
    _ensure_list_view_column("Sales Order", "sh_risk_level", "Shopify Risk")
    _ensure_list_view_column("Delivery Note", "sh_delivery_status", "Shopify Delivery Status")
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
            create_or_update_workspace,
            create_or_update_workspace_sidebar,
            create_or_update_os_settings_workspace,
            create_or_update_os_settings_workspace_sidebar,
        )
        create_or_update_workspace()
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
    """Add Shopify custom fields to Alaiy OS doctypes. Idempotent -- safe to call on every migrate."""
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
            "fieldname": "sh_shopify_inventory_item_id",
            "label": "Shopify Inventory Item ID",
            "fieldtype": "Data",
            "search_index": 1,
            "read_only": 1,
            "insert_after": "sh_shopify_variant_id",
            "description": "Shopify's own inventory_item_id for this variant -- the real key the inventory_levels/update webhook reports changes against (not the variant id). Lets the inbound inventory sync resolve a webhook straight to this Item without an extra API call.",
        },
        {
            "fieldname": "sh_shopify_status",
            "label": "Shopify Status",
            "fieldtype": "Select",
            "options": "Active\nDraft\nArchived",
            "default": "Active",
            "insert_after": "disabled",
            "fetch_from": "variant_of.sh_shopify_status",
            "read_only_depends_on": "eval:doc.variant_of",
            "description": "Product visibility on Shopify. Active = live on sales channels; Draft = hidden from customers. Synced both directions. Archived is controlled separately by unchecking Sync to Shopify (or disabling the Item). Set on the template; variants inherit.",
        },
        {
            "fieldname": "sh_shopify_tags",
            "label": "Shopify Tags",
            "fieldtype": "Table MultiSelect",
            "options": "Item Shopify Tag",
            "insert_after": "sh_shopify_status",
            # Table MultiSelect can't use fetch_from (child-table data, not a
            # scalar) -- variant inheritance is instead handled by
            # _copy_template_tags_to_variant on Item's validate hook.
            "read_only_depends_on": "eval:doc.variant_of",
            "description": "Tags synced both directions with Shopify's product tags field, picked from the cached Shopify Tag list -- no free typing. Copied from the template on variants -- edit on the template.",
        },
        {
            "fieldname": "sh_shopify_category",
            "label": "Shopify Category",
            "fieldtype": "Link",
            "options": "Shopify Category",
            "insert_after": "sh_shopify_tags",
            "fetch_from": "variant_of.sh_shopify_category",
            "read_only_depends_on": "eval:doc.variant_of",
            "description": "Shopify's Standard Product Taxonomy category. Fetched from the template on variants -- edit on the template.",
        },
        {
            "fieldname": "sh_shopify_category_gid",
            "label": "Shopify Category GID",
            "fieldtype": "Data",
            "insert_after": "sh_shopify_category",
            "description": "Staging field for bulk CSV import -- paste a Shopify taxonomy GID (gid://shopify/TaxonomyCategory/...) here instead of the category path. Frappe's Data Import tool pre-validates Link field values against existing doc names before a row ever reaches Item's validate hook, so a raw GID in Shopify Category itself fails import outright. This plain Data field has no such check -- resolve_shopify_category_gid reads it on save, resolves the GID to the real Shopify Category doc, and clears this field.",
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
            "fieldname": "sh_country_of_origin",
            "label": "Country of Origin",
            "fieldtype": "Link",
            "options": "Country",
            "insert_after": "sh_shopify_product_type",
            "description": "Pushed as Shopify's inventoryItem.countryCodeOfOrigin (ISO 3166-1 alpha-2, read from the Country doctype's own code field).",
        },
        {
            "fieldname": "sh_harmonized_system_code",
            "label": "Harmonized System Code",
            "fieldtype": "Data",
            "insert_after": "sh_country_of_origin",
            "description": "Pushed as Shopify's inventoryItem.harmonizedSystemCode -- required by some countries' customs for cross-border orders.",
        },
        {
            "fieldname": "sh_seo_title",
            "label": "Shopify SEO Title",
            "fieldtype": "Data",
            "insert_after": "sh_harmonized_system_code",
            "description": "Defaults to the Item Name if left blank.",
        },
        {
            "fieldname": "sh_seo_description",
            "label": "Shopify SEO Description",
            "fieldtype": "Small Text",
            "insert_after": "sh_seo_title",
            "description": "Defaults to the Description if left blank.",
        },
        {
            "fieldname": "sh_shopify_collections",
            "label": "Shopify Collections",
            "fieldtype": "Table MultiSelect",
            "options": "Item Shopify Collection",
            "insert_after": "sh_seo_description",
            # Table MultiSelect can't use fetch_from (child-table data, not a
            # scalar) -- variant inheritance is handled by
            # copy_template_collections_to_variant on Item's validate hook.
            "read_only_depends_on": "eval:doc.variant_of",
            "description": "Manual Shopify collections this product belongs to, picked from the cached Shopify Collection list (run Sync Collections first). Membership syncs to Shopify on push. Copied from the template on variants -- edit on the template.",
        },
        {
            "fieldname": "sh_shopify_handle",
            "label": "Shopify Handle",
            "fieldtype": "Data",
            "read_only": 1,
            "insert_after": "sh_shopify_collections",
            "description": "The product's storefront URL slug on Shopify. Read-only: renaming it here would not rename it there.",
        },
        {
            "fieldname": "sh_published_at",
            "label": "Shopify Published On",
            "fieldtype": "Datetime",
            "read_only": 1,
            "insert_after": "sh_shopify_handle",
            "description": "When the product was first published on Shopify. Blank on a product that has never been published.",
        },
        {
            "fieldname": "sh_barcode",
            "label": "Shopify Barcode",
            "fieldtype": "Data",
            "read_only": 1,
            "insert_after": "sh_published_at",
            "description": "Barcode (ISBN, UPC, GTIN) as held on the Shopify variant. Kept separate from ERPNext's own Item Barcode table, which stays the local source of truth.",
        },
        {
            "fieldname": "sh_inventory_policy",
            "label": "Shopify Inventory Policy",
            "fieldtype": "Select",
            "options": "\nDENY\nCONTINUE",
            "read_only": 1,
            "insert_after": "sh_barcode",
            "description": "CONTINUE means Shopify keeps selling this variant after stock reaches zero. Worth knowing before trusting a stock figure.",
        },
        {
            "fieldname": "sh_tracked",
            "label": "Shopify Tracks Inventory",
            "fieldtype": "Check",
            "read_only": 1,
            "insert_after": "sh_inventory_policy",
            "description": "Unticked means Shopify does not track stock for this variant at all, so an inventory push to it is meaningless.",
        },
        {
            "fieldname": "sh_requires_shipping",
            "label": "Shopify Requires Shipping",
            "fieldtype": "Check",
            "read_only": 1,
            "insert_after": "sh_tracked",
            "description": "Unticked for a digital or service product.",
        },
        {
            "fieldname": "sh_taxable",
            "label": "Shopify Taxable",
            "fieldtype": "Check",
            "read_only": 1,
            "insert_after": "sh_requires_shipping",
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
        {
            "fieldname": "sh_risk_recommendation",
            "label": "Shopify Risk Recommendation",
            "fieldtype": "Select",
            "options": "\nNONE\nACCEPT\nINVESTIGATE\nCANCEL",
            "read_only": 1,
            "in_standard_filter": 1,
            "insert_after": "sh_fulfillment_status",
            "description": "Shopify's own recommended action for this order.",
        },
        {
            "fieldname": "sh_risk_level",
            "label": "Shopify Risk",
            "fieldtype": "Select",
            "options": "\nPENDING\nNONE\nLOW\nMEDIUM\nHIGH",
            "read_only": 1,
            # On the list view because a HIGH-risk order has to be visible
            # before someone opens it -- the point of the flag is to stop a
            # fraudulent order shipping, which happens from the list.
            "in_list_view": 1,
            "in_standard_filter": 1,
            "insert_after": "sh_risk_recommendation",
            "description": "Shopify's fraud analysis. The worst level across all assessing providers.",
        },
        {
            "fieldname": "sh_risk_detail",
            "label": "Shopify Risk Detail",
            "fieldtype": "Small Text",
            "read_only": 1,
            "insert_after": "sh_risk_level",
            "depends_on": "eval:doc.sh_risk_level && doc.sh_risk_level != 'NONE'",
            "description": "Per-provider risk level and the facts behind it.",
        },
        {
            "fieldname": "sh_handling_hours",
            "label": "Handling Hours",
            "fieldtype": "Float",
            "precision": "2",
            "read_only": 1,
            "insert_after": "sh_risk_detail",
            "description": (
                "Hours from the order being placed to its dispatch being confirmed, "
                "written once on the first Delivery Note. Measured from midnight on "
                "the order date, since a Sales Order carries no order time -- so a "
                "same-day dispatch reads as hours rather than zero."
            ),
        },
        {
            "fieldname": "sh_payment_fee",
            "label": "Payment Processing Fee",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "sh_handling_hours",
            "description": (
                "What the payment gateway charged on this order, summed across its "
                "successful sale and capture transactions. Shopify Payments reports "
                "a real fee; most third-party gateways report none, so blank means "
                "not reported rather than free."
            ),
        },
        {
            "fieldname": "sh_shopify_notes",
            "label": "Shopify Notes",
            "fieldtype": "Small Text",
            "insert_after": "sh_risk_detail",
            "description": "Synced both directions with Shopify's order note field.",
            # Orders here are typically submitted immediately -- without
            # this, the field is silently read-only the moment the Sales
            # Order submits, which is effectively always.
            "allow_on_submit": 1,
        },
        {
            "fieldname": "sh_shopify_order_tags",
            "label": "Shopify Order Tags",
            "fieldtype": "Data",
            "insert_after": "sh_shopify_notes",
            "description": "Synced both directions with Shopify's order tags (comma-separated). Alaiy OS's own status tag is kept out of this field and merged in separately on push.",
            "allow_on_submit": 1,
        },
        {
            "fieldname": "sh_delivery_method",
            "label": "Shopify Delivery Method",
            "fieldtype": "Data",
            "read_only": 1,
            "insert_after": "sh_shopify_order_tags",
            "description": "The shipping method the customer chose, straight from Shopify's shippingLine.title (e.g. \"Free Standard Shipping\", \"2nd air\"). Stored as its own field so it stays filterable/reportable -- the shipping COST rides separately on the Sales Taxes and Charges table, and a free-shipping order carries no charge row at all yet still has a real method name here.",
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
            "description": "Set when this Delivery Note was auto-created from a Shopify fulfillment event, or once a Delivery Note created here has been pushed out as one (two-way mode). Either way, prevents the same fulfillment from ever being represented twice.",
            "insert_after": "customer",
        },
        {
            # No longer read-only: in two-way mode this is also an INPUT --
            # set before submit to attach tracking to the fulfillment this
            # Delivery Note creates, or after submit to push a tracking edit
            # to an already-linked one. The inbound direction (_sync_tracking)
            # still writes it the same way either way (frappe.db.set_value
            # bypasses read_only regardless), so relaxing this costs nothing
            # there.
            "fieldname": "sh_tracking_number",
            "label": "Shopify Tracking Number",
            "fieldtype": "Data",
            "description": "Tracking number synced with the Shopify fulfillment -- set automatically inbound, or set here (before or after submit) to push it out in two-way mode.",
            "insert_after": "sh_shopify_fulfillment_id",
            "allow_on_submit": 1,
        },
        {
            "fieldname": "sh_tracking_company",
            "label": "Shopify Tracking Company",
            "fieldtype": "Data",
            "description": "Carrier synced with the Shopify fulfillment -- set automatically inbound, or set here (before or after submit) to push it out in two-way mode.",
            "insert_after": "sh_tracking_number",
            "allow_on_submit": 1,
        },
        {
            "fieldname": "sh_tracking_url",
            "label": "Shopify Tracking URL",
            "fieldtype": "Small Text",
            "read_only": 1,
            "insert_after": "sh_tracking_company",
        },
        {
            "fieldname": "sh_delivery_status",
            "label": "Shopify Delivery Status",
            "fieldtype": "Data",
            "read_only": 1,
            "in_list_view": 1,
            "insert_after": "sh_tracking_url",
            "description": "Shopify's own delivery state for this fulfillment (fulfillment.displayStatus -- IN_TRANSIT, DELIVERED, ATTEMPTED_DELIVERY, ...). Distinct from the order's fulfillment status, which only says whether it shipped at all. Blank until Shopify reports a delivery state.",
        },
        {
            "fieldname": "sh_shopify_refund_id",
            "label": "Shopify Refund ID",
            "fieldtype": "Data",
            "search_index": 1,
            "read_only": 1,
            "description": "Set when this Sales Return was auto-created from a Shopify refund event. Prevents the same refund from ever creating a duplicate return.",
            "insert_after": "sh_delivery_status",
        },
    ]
    sales_invoice_fields = [
        {
            "fieldname": "sh_shopify_refund_id",
            "label": "Shopify Refund ID",
            "fieldtype": "Data",
            "search_index": 1,
            "read_only": 1,
            "description": "Set when this Credit Note was auto-created from a Shopify refund event. Prevents the same refund from ever creating a duplicate credit note.",
            "insert_after": "customer",
        },
    ]

    custom_fields = {
        "Item": item_fields,
        "Sales Order": sales_order_fields,
        "Sales Order Item": sales_order_item_fields,
        "Customer": customer_fields,
        "Delivery Note": delivery_note_fields,
        "Sales Invoice": sales_invoice_fields,
    }
    # Stamp each field with this app's module so they export under our
    # fixtures, matching how they were created before.
    for fields in custom_fields.values():
        for f in fields:
            f.setdefault("module", "Alaiy OS Connector Shopify")

    # update=True re-syncs properties (description, read_only, ...) on
    # already-existing fields, which is what the old hand-rolled upsert did
    # -- e.g. sh_shopify_category started read-only and later became editable.
    _remove_deprecated_item_fields()
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()


def _remove_deprecated_item_fields():
    """
    Fields that changed fieldtype or were removed entirely -- delete the
    Custom Field itself so create_custom_fields can recreate it with the
    new fieldtype (Frappe blocks fieldtype changes on existing fields).
    """
    for fieldname in ("sh_country_of_origin", "sh_harmonized_system_code", "sh_shopify_tags", "sh_shopify_category"):
        name = f"Item-{fieldname}"
        if frappe.db.exists("Custom Field", name):
            frappe.delete_doc("Custom Field", name, ignore_permissions=True)
    frappe.db.commit()


def _unlock_disabled_field_on_variants():
    """
    Unlock the 'disabled' field on variant items so users can disable
    individual variants in the Alaiy OS UI, and ensure 'disabled' is added
    to Item Variant Settings so template saves do not overwrite it.
    """
    # 1. Remove the property setter that was making it read-only on variants
    frappe.db.sql("""
        DELETE FROM `tabProperty Setter` 
        WHERE doc_type = 'Item' AND field_name = 'disabled' AND property = 'read_only_depends_on'
    """)
    frappe.clear_cache(doctype="Item")

    # 2. Add 'disabled' to Item Variant Settings so that saving the template
    # doesn't overwrite individual variant disabled values.
    if frappe.db.exists("DocType", "Item Variant Settings"):
        try:
            settings = frappe.get_doc("Item Variant Settings", "Item Variant Settings")
            if not any(d.field_name == "disabled" for d in settings.fields):
                settings.append("fields", {"field_name": "disabled"})
                settings.save(ignore_permissions=True)
                frappe.db.commit()
        except Exception:
            pass


# --- the agent pack ----------------------------------------------------------
# The manifest is pack_meta.py; these only write it. Editing a tool description
# or prompts/pack.md and running `bench migrate` is the whole reconcile loop.

#: Fields an admin owns once the row exists. `is_enabled` is the switch that
#: turns the pack on for a site, and a migrate that reset it would turn every
#: pack back on behind whoever switched it off.
_AGENT_RUNTIME_FIELDS = {"is_enabled"}

#: Not fields on the row at all: `agent_id` is the name, and `tools` is a child
#: table that is rebuilt wholesale below rather than set like a scalar.
_AGENT_NON_REGISTRY_FIELDS = {"agent_id", "tools"}


def sync_agent_registry():
    """Upsert this connector's OS Agent Registry pack. Safe to call repeatedly."""
    if not frappe.db.exists("DocType", "OS Agent Registry"):
        # Core not installed yet, or predates the agent engine.
        return

    from alaiy_os_connector_shopify import pack_meta

    meta = pack_meta.build_pack_meta()
    agent_id = meta["agent_id"]

    if frappe.db.exists("OS Agent Registry", agent_id):
        doc = frappe.get_doc("OS Agent Registry", agent_id)
    else:
        doc = frappe.new_doc("OS Agent Registry")
        doc.agent_id = agent_id

    for key, value in meta.items():
        if key in _AGENT_NON_REGISTRY_FIELDS or key in _AGENT_RUNTIME_FIELDS:
            continue
        doc.set(key, value)

    doc.set("tools", [pack_meta.as_registry_tool(tool) for tool in meta["tools"]])

    # save() inserts when new. The OS Agent Tool child controller validates every
    # handler dotted path and every parameters_schema here, so a typo in the
    # manifest fails at migrate with the tool named, rather than mid-run.
    doc.save(ignore_permissions=True)
    frappe.db.commit()


def unregister_agent():
    """Drop the pack row on uninstall, keeping the run history that points at it.

    `force=True` because past `OS Agent Run` rows link to this row, and Frappe
    would otherwise refuse the delete to protect them. Deleting the runs instead
    would throw away the record of what the pack actually did on this site,
    which is the opposite of what an uninstall should cost.
    """
    if not frappe.db.exists("DocType", "OS Agent Registry"):
        return

    from alaiy_os_connector_shopify.pack_meta import PACK_ID

    if frappe.db.exists("OS Agent Registry", PACK_ID):
        frappe.delete_doc("OS Agent Registry", PACK_ID, force=True, ignore_permissions=True)
        frappe.db.commit()


# --- the listing channel -----------------------------------------------------
# The enrichment tools, the rules, the validator and the four Shopify Enriched
# Listing doctypes were adopted from the retired `alaiy_os_agent_shopify_listing`
# app. What was genuinely Shopify's in it is knowledge about *the channel*, and
# the app that owns the channel is this one.
#
# The agent itself is NOT registered here. `alaiy_os_agents` owns one
# channel-agnostic listing agent for the whole site and reaches this connector
# through the `listing_channels` hook (see listing/channel.py), so registering a
# second Shopify-specific agent would put two listing agents on one bench --
# which is the thing that migration existed to remove. The Amazon connector draws
# the same line.
#
# What stays here is the one field the review record writes back.

_LISTING_CUSTOM_FIELDS = {
    "Shopify Product Listing": [
        {
            "fieldname": "is_enriched",
            "label": "Enriched",
            "fieldtype": "Check",
            "insert_after": "is_enabled",
            "default": "0",
            "read_only": 1,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "description": (
                "An approved AI enrichment is live on this listing. Set when its "
                "Shopify Enriched Listing is approved; cleared when the listing agent "
                "re-runs, so it always means the CURRENT content passed review."
            ),
        }
    ],
}


def sync_listing_custom_fields():
    """Create `is_enriched` on Shopify Product Listing. Idempotent.

    A Custom Field rather than a column in the doctype's own JSON, even though
    this app owns that doctype: it describes the enrichment lifecycle rather than
    the listing, `shopify_enriched_listing.py` is what sets and clears it, and
    keeping it a Custom Field lets an uninstall drop the field without touching
    the column.
    """
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    present = {
        doctype: fields
        for doctype, fields in _LISTING_CUSTOM_FIELDS.items()
        if frappe.db.exists("DocType", doctype)
    }
    if not present:
        return

    create_custom_fields(present, update=True)
    frappe.db.commit()
    frappe.clear_cache()


def remove_listing_custom_fields():
    """Drop the listing agent's custom fields on uninstall.

    The underlying column is left in place -- dropping it would destroy the
    enriched flag for every listing, and a reinstall re-adopts the column as-is.
    """
    for doctype, fields in _LISTING_CUSTOM_FIELDS.items():
        for field in fields:
            name = f"{doctype}-{field['fieldname']}"
            if frappe.db.exists("Custom Field", name):
                frappe.delete_doc("Custom Field", name, ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
