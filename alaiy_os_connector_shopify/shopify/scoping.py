# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
Pair a Shopify id with the store it came from, in one place.

A Shopify id is only unique inside one shop. Two sellers both have a product
12345, both have a location 1, and both have an order 1001. Every lookup in
this connector was written when a bench held one store, so it asks for the id
alone -- and the moment a second seller connects, that question has two
answers and the code takes whichever row was written first.

`owned_by` is the filter those lookups should have been using. It adds the
connection to the filters a caller already has, which keeps the change at each
call site to wrapping the dict rather than restating it:

    frappe.db.get_value("Item", owned_by({"sh_shopify_variant_id": vid}), "name")

The field name differs between ERPNext's doctypes and the connector's own --
`sh_shopify_connection` on the first, matching the sh_ prefix the other custom
fields use, and `connection` on the second -- so callers do not have to
remember which they are addressing.

Two deliberate non-behaviours:

`owned_by` never resolves a connection itself. It takes one, or it takes None
and returns the filters untouched. A helper that quietly fell back to "the
default store" would turn every caller that forgot to thread a connection into
a silent cross-store read -- exactly the bug this exists to stop -- and it
would do it invisibly, because the lookup would still return something
plausible. Passing None is how a caller says "I have not been scoped yet", and
it reads as the old bench-wide behaviour on purpose: this lands before the
callers are converted, and an unconverted caller has to keep working.

There is no write-side counterpart. Stamping the connection onto a new
document is one assignment at the point of creation, and wrapping that in a
helper would hide which documents get attributed and which are missed.
"""

# ERPNext's own doctypes carry the connector's custom field; the connector's
# own doctypes carry a plain one. Anything not named here is assumed to be
# the connector's.
_CUSTOM_FIELD_DOCTYPES = frozenset({
	"Item",
	"Sales Order",
	"Sales Order Item",
	"Customer",
	"Delivery Note",
	"Sales Invoice",
})

CUSTOM_FIELD = "sh_shopify_connection"
OWN_FIELD = "connection"


def connection_field(doctype: str) -> str:
	"""Which column on this doctype names the store."""
	return CUSTOM_FIELD if doctype in _CUSTOM_FIELD_DOCTYPES else OWN_FIELD


def owned_by(doctype: str, connection, filters: dict = None) -> dict:
	"""
	`filters`, narrowed to one store.

	`connection` is a document, a name, or None. None returns the filters
	unchanged -- see the module docstring for why that is not a fallback to
	the default store.
	"""
	filters = dict(filters or {})
	if connection is None:
		return filters
	filters[connection_field(doctype)] = getattr(connection, "name", connection)
	return filters
