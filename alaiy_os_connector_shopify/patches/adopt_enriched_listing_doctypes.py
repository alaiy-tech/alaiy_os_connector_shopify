# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""Move the four enriched-listing doctypes onto this app's module.

Without this, uninstalling `alaiy_os_agent_shopify_listing` DROPS THE TABLES and
every enrichment on the site goes with them.

`frappe.installer.remove_app` does not consult any JSON file. It reads the
`Module Def` rows belonging to the app being removed, then, for each, does

    frappe.get_all("DocType", filters={"module": module_name})
    ...
    frappe.db.sql_ddl(f"DROP TABLE IF EXISTS `tab{doctype}`")

So what decides whether `tabShopify Enriched Listing` survives is one field on
one row in THIS SITE'S DATABASE — `DocType.module` — at the moment the uninstall
runs. On any site that enriched a listing before the migration, that field still
says "Alaiy Os Agent Shopify Listing", because that is the app that created it.

A migrate alone cannot be trusted to fix it while both apps are installed. Both
ship a `shopify_enriched_listing.json`, `sync_all()` imports every installed
app's doctypes, and the last writer wins — which is decided by installed-app
order, not by which app should own the doctype. A site where the old app happens
to sync second would flip the field back and then drop the tables on uninstall.

Hence a patch, and specifically a **post_model_sync** patch: `frappe.migrate`
runs pre_model_sync patches, then `sync_all()` for every app, then
post_model_sync patches. Running after the whole sync is what makes this the last
word regardless of app order.

Idempotent, and a no-op on a site that never had the old app: it only writes
where the value is not already ours.

Safe to leave in place permanently. Once the old app is gone nothing sets the
field back, and this finds nothing to do.
"""

import frappe

MODULE = "Alaiy OS Connector Shopify"

#: The parent and its three child tables. The children matter as much as the
#: parent — they are separate doctypes with their own tables, so a parent that
#: survived while `tabShopify Enriched Listing Attribute` was dropped would leave
#: every listing with no attributes and no variants.
DOCTYPES = (
	"Shopify Enriched Listing",
	"Shopify Enriched Listing Attribute",
	"Shopify Enriched Listing Image",
	"Shopify Enriched Listing Variant",
)


def execute():
	if not frappe.db.exists("Module Def", MODULE):
		# This app's own module is created by its install; if it is not here yet
		# there is nothing to move the doctypes onto, and our next migrate catches
		# it once there is.
		return

	moved = []
	for doctype in DOCTYPES:
		if not frappe.db.exists("DocType", doctype):
			# Never installed on this site, or already dropped. Either way there is
			# nothing to rescue and nothing to fail over.
			continue
		if frappe.db.get_value("DocType", doctype, "module") == MODULE:
			continue

		# set_value rather than a document save: this is a single field on a
		# DocType row, and saving a DocType re-runs the schema updater over a table
		# a migration has no reason to rewrite.
		frappe.db.set_value("DocType", doctype, "module", MODULE, update_modified=False)
		moved.append(doctype)

	if moved:
		# Worth a line in the migrate output. Someone reading it is usually about
		# to uninstall the old app, and this is the step that makes that safe.
		print(f"Adopted {len(moved)} enriched-listing doctype(s) onto {MODULE}: {', '.join(moved)}")

	frappe.db.commit()
