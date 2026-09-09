# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
Attribute every Shopify-origin row to the store it came from.

The previous patch moved the one store out of tabSingles and into a Shopify
Connection row. This one goes back over everything that store already imported
-- Items, Sales Orders, Customers, Delivery Notes, Sales Invoices, and the
connector's own Listings, Locations, Collections, Tags, mappings and queued
updates -- and records which store that was.

Until now nothing needed to: there was one store, so "the Shopify id is set"
and "belongs to this store" were the same statement. They stop being the same
the moment a second connection exists, and every lookup that pairs an id with
a connection needs the existing rows to carry one, or a bench that has been
syncing for months comes up looking like it has imported nothing.

Unambiguous by construction. A bench reaching this patch has exactly one
connection -- the connector still refuses to enable a second -- so there is
only one answer for every row, and no guessing. On a bench with several
connections already the patch declines rather than picking one; that bench
predates this work and has to be attributed by hand.

Only rows with a Shopify id are touched. A hand-made Item or a Sales Order
typed into the desk is not this connector's to claim, and stamping it would
sweep it into the connector's reads and, worse, into the scope of the bulk
deletes.

Idempotent: every statement skips rows that already carry a connection, so a
re-run after a partial migration finishes the job rather than redoing it.
"""

import frappe

from alaiy_os_connector_shopify import connections

# (table, the column that says the row came from Shopify). A row qualifies
# when that column holds something.
CORE = (
	("Item", "sh_shopify_product_id"),
	("Sales Order", "sh_shopify_order_id"),
	("Customer", "sh_shopify_customer_id"),
	("Delivery Note", "sh_shopify_fulfillment_id"),
	("Sales Invoice", "sh_shopify_refund_id"),
)

# The connector's own doctypes. Every row in these exists because of Shopify,
# so there is no "did this come from Shopify" column to test -- all of them
# belong to the store.
OWNED = (
	"Shopify Product Listing",
	"Shopify Location",
	"Shopify Collection",
	"Shopify Tag",
	"Shopify Synced Entity",
	"Shopify Inventory Update",
	"Shopify Retry Queue Entry",
)


def execute():
	names = connections.names()
	if len(names) != 1:
		# Nothing to migrate on a bench with no store; ambiguous on a bench
		# with several, and a wrong guess here hands one seller's catalogue to
		# another. Either way, do not write.
		if len(names) > 1:
			frappe.log_error(
				title="Shopify: connection backfill skipped",
				message=(
					"This site has %d Shopify connections, so existing rows "
					"cannot be attributed automatically. Set the connection "
					"field by hand before enabling a second store."
					% len(names)
				),
			)
		return

	connection = names[0]

	for doctype, marker in CORE:
		_stamp(doctype, connection, marker=marker)
	for doctype in OWNED:
		_stamp(doctype, connection)

	frappe.db.commit()


def _stamp(doctype: str, connection: str, marker: str = None) -> None:
	"""
	Set the connection on every unattributed row of one doctype.

	Raw SQL on purpose. Loading each Item to save it would fire the connector's
	own document events on a catalogue of thousands of rows -- which on a big
	site is what turned an earlier migration into an afternoon -- and this
	writes one column that no hook reads.

	The field differs by doctype: a custom field on ERPNext's own doctypes,
	a real one on the connector's.
	"""
	field = "sh_shopify_connection" if marker else "connection"
	table = f"tab{doctype}"

	if not frappe.db.exists("DocType", doctype):
		return
	# The doctype, not `table`. has_column prefixes "tab" itself, so handing it
	# one asks for `tabtabItem`, and get_table_columns raises TableMissingError
	# on a table that is not there rather than returning no columns -- so the
	# skip below became a failed migrate on the first doctype that did exist.
	if not frappe.db.has_column(doctype, field):
		# The column arrives with this release's migrate. If it is missing the
		# schema sync has not run yet, and writing would fail rather than skip.
		return

	where = [f"(`{field}` IS NULL OR `{field}` = '')"]
	if marker:
		if not frappe.db.has_column(doctype, marker):
			return
		where.append(f"(`{marker}` IS NOT NULL AND `{marker}` != '')")

	frappe.db.sql(
		f"UPDATE `{table}` SET `{field}` = %s WHERE " + " AND ".join(where),
		connection,
	)


def unattributed() -> dict:
	"""
	Rows that still carry no store, by doctype.

	The verification step: this has to come back empty before a second
	connection is allowed to exist, and it is worth being able to ask that
	question from a console without re-reading the patch.
	"""
	left = {}
	for doctype, marker in CORE:
		count = _count_unattributed(doctype, "sh_shopify_connection", marker)
		if count:
			left[doctype] = count
	for doctype in OWNED:
		count = _count_unattributed(doctype, "connection", None)
		if count:
			left[doctype] = count
	return left


def _count_unattributed(doctype: str, field: str, marker: str) -> int:
	table = f"tab{doctype}"
	if not frappe.db.exists("DocType", doctype):
		return 0
	# The doctype, not `table` -- see _stamp.
	if not frappe.db.has_column(doctype, field):
		return 0
	where = [f"(`{field}` IS NULL OR `{field}` = '')"]
	if marker:
		if not frappe.db.has_column(doctype, marker):
			return 0
		where.append(f"(`{marker}` IS NOT NULL AND `{marker}` != '')")
	rows = frappe.db.sql(
		f"SELECT COUNT(*) FROM `{table}` WHERE " + " AND ".join(where)
	)
	return rows[0][0] if rows else 0
