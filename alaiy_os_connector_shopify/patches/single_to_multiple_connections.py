# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
Move the one store out of Shopify Connector Settings and into a real row.

Shopify Connector Settings was a Single. Every bench running this connector has
its store's configuration -- and its Shopify credentials -- stored as
(doctype, field, value) rows in tabSingles, addressed by the doctype name. The
replacement, Shopify Connection, is a normal DocType, so nothing carries over
on its own: without this patch every one of those benches comes up with no
store, an unregistered webhook endpoint and a merchant who has to re-enter
their client secret.

Four halves, and only the first is the obvious one:

  * the field values, which live in tabSingles;
  * the child table. sh_location_map's rows are in tabShopify Location Map with
    parent = 'Shopify Connector Settings'. Left alone they belong to a document
    that no longer exists, and a multi-location store silently falls back to
    pushing stock to Shopify's primary location only;
  * the two secrets that are already encrypted. Password fields live in __Auth
    keyed by (doctype, name, fieldname), and for a Single the name *is* the
    doctype. Those rows have to be re-keyed to the new document name or the
    secret is orphaned: still encrypted in the table, no longer reachable by
    get_password, and silently gone;
  * the one secret that is not encrypted. The access token was written with
    `frappe.db.set_single_value`, which puts the raw value in tabSingles and
    never touches __Auth -- so it is sitting there in plaintext. It is moved
    into __Auth properly on the way past, which is also what makes deleting
    the Singles rows at the end safe to do.

Idempotent. Runs post-model-sync, so the new table exists by the time it does.
"""

import frappe

OLD = "Shopify Connector Settings"
NEW = "Shopify Connection"
NEW_NAME = "default"

# Encrypted through the form, so already in __Auth under the Single's name.
REKEY_FIELDS = ("sh_client_secret", "sh_webhook_secret")
# Written straight to tabSingles in the clear, so it has to be encrypted here.
PLAINTEXT_FIELDS = ("sh_access_token",)


def execute():
	if not frappe.db.exists("DocType", NEW):
		# The DocType JSON has not been synced yet, so there is nothing to
		# migrate into. Nothing to do rather than half a migration.
		return

	if not frappe.db.exists(NEW, NEW_NAME):
		_migrate_single()

	_backfill_sync_log_connection()
	_retire_old_doctype()


def _migrate_single() -> None:
	stored = dict(
		frappe.db.sql("select field, value from `tabSingles` where doctype = %s", OLD) or []
	)
	if not stored:
		# A site that never configured Shopify. Leaving it with no connection is
		# right -- `connections.resolve` says so clearly, and creating an empty
		# row would make an unconfigured site look configured.
		return

	meta = frappe.get_meta(NEW)
	writable = {
		df.fieldname
		for df in meta.fields
		if df.fieldname
		and not df.get("is_virtual")
		and df.fieldtype not in ("Section Break", "Column Break", "Tab Break", "HTML", "Table")
	}
	reserved = {"connection_id", "label", "is_default", "owner_app", "is_enabled"}

	doc = frappe.new_doc(NEW)
	doc.connection_id = NEW_NAME
	doc.label = stored.get("sh_shop_url") or "Shopify"
	# The only connection on the site, so it answers every call that names none.
	doc.is_default = 1
	doc.owner_app = "alaiy_os_connector_shopify"

	for field, value in stored.items():
		if field in writable and field not in reserved:
			doc.set(field, value)

	# The secrets are moved below rather than re-encrypted through the document,
	# so make sure the insert does not write a masked placeholder over them.
	for field in REKEY_FIELDS + PLAINTEXT_FIELDS:
		doc.set(field, None)

	# Inserted switched off whatever the Single said, then corrected with a
	# direct write. `is_enabled` going 0 -> 1 through the ORM is what fires
	# _on_first_enable, and a migrate is no place to start calling Shopify to
	# register webhooks -- the store was already enabled, so there is nothing
	# for that hook to do anyway. sync_jobs' own self-heal check re-registers
	# anything genuinely missing on the next scheduler tick.
	doc.is_enabled = 0
	doc.flags.ignore_permissions = True
	doc.flags.ignore_mandatory = True
	doc.insert(ignore_permissions=True)

	_move_passwords(doc.name)
	_reparent_location_map(doc.name)

	if frappe.utils.cint(stored.get("is_enabled")):
		frappe.db.set_value(NEW, doc.name, "is_enabled", 1, update_modified=False)

	frappe.db.delete("Singles", {"doctype": OLD})
	frappe.db.commit()

	frappe.logger().info(f"Shopify connector: migrated the Single settings to {NEW} {doc.name}")


def _move_passwords(new_name: str) -> None:
	"""
	Get every secret to __Auth, keyed by the new document's name.

	Through Frappe's own helpers rather than SQL against __Auth: they own that
	table's shape, and the round trip re-encrypts with the site key the same way
	a normal save would.
	"""
	from frappe.utils.password import (
		get_decrypted_password,
		remove_encrypted_password,
		set_encrypted_password,
	)

	for field in REKEY_FIELDS:
		secret = get_decrypted_password(OLD, OLD, field, raise_exception=False)
		if not secret:
			continue
		set_encrypted_password(NEW, new_name, secret, field)
		remove_encrypted_password(OLD, OLD, field)
		_mask(new_name, field, secret)

	for field in PLAINTEXT_FIELDS:
		# Straight out of tabSingles: this one was never encrypted. Raw SQL,
		# not frappe.db.get_value -- tabSingles has no `creation` column and
		# the query builder orders by it, so the ORM cannot read this table.
		row = frappe.db.sql(
			"select value from `tabSingles` where doctype = %s and field = %s limit 1",
			(OLD, field),
		)
		secret = row[0][0] if row else None
		if not secret:
			continue
		set_encrypted_password(NEW, new_name, secret, field)
		_mask(new_name, field, secret)


def _mask(new_name: str, field: str, secret: str) -> None:
	"""The document column carries the placeholder a Password field shows."""
	frappe.db.set_value(NEW, new_name, field, "*" * len(secret), update_modified=False)


def _reparent_location_map(new_name: str) -> None:
	"""Hand the warehouse-to-location rows to their new owner."""
	if not frappe.db.exists("DocType", "Shopify Location Map"):
		return
	frappe.db.sql(
		"""
		update `tabShopify Location Map`
		set parent = %s, parenttype = %s
		where parenttype = %s
		""",
		(new_name, NEW, OLD),
	)


def _backfill_sync_log_connection() -> None:
	"""
	Attribute the history to the store it was for.

	Every existing log row was written when there was only one store, so they
	all belong to the migrated connection. Without this the dashboard's
	"recent runs" -- now filtered per store -- would come up empty on a bench
	that has been syncing for months.
	"""
	if not frappe.db.exists("DocType", "Shopify Sync Log"):
		return
	if not frappe.db.exists(NEW, NEW_NAME):
		return
	frappe.db.sql(
		"update `tabShopify Sync Log` set connection = %s where connection is null or connection = ''",
		NEW_NAME,
	)
	frappe.db.commit()


def _retire_old_doctype() -> None:
	"""
	Delete the Single itself, once nothing of it is left worth keeping.

	Removing the folder from the app does not remove the DocType record from a
	site that already has it: it would sit in the desk forever, still listed
	under the module, offering a settings form that nothing reads any more.

	Only ever after the values are out. The guard is the Singles rows -- if any
	survive, the migration above did not finish, and dropping the DocType would
	take the site's only copy of its Shopify configuration with it.
	"""
	if not frappe.db.exists("DocType", OLD):
		return
	leftover = frappe.db.sql(
		"select 1 from `tabSingles` where doctype = %s limit 1", OLD
	)
	if leftover:
		frappe.logger().warning(
			f"Shopify connector: {OLD} still holds values; leaving the DocType in place."
		)
		return
	try:
		frappe.delete_doc("DocType", OLD, ignore_missing=True, force=True)
		frappe.db.commit()
	except Exception:
		# Not worth failing a migrate over a leftover form.
		frappe.db.rollback()
		frappe.log_error(
			title="Shopify connector: could not remove the old settings DocType",
			message=frappe.get_traceback(),
		)
