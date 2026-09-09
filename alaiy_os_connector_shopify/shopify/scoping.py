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


# The store whose SKUs stay bare. Matches the id the upgrade patch gives the
# connection it migrates out of the old Single, so every bench that has ever
# run this connector keeps its Item codes unchanged.
DEFAULT_ITEM_CODE_CONNECTION = "default"


def item_code_for(connection, sku: str) -> str:
    """
    The Item code a store's SKU maps to.

    item_code is Item's primary key, and the importer used the raw Shopify SKU
    as-is. Two sellers both stocking TSHIRT-RED-M therefore wanted the same
    row, and the importer resolved that by repointing whichever Item already
    existed at the newer store's Shopify ids -- so the first seller's item
    silently started pushing its stock to the second seller's shop.

    Adding a connection field could not fix that on its own: two rows cannot
    share a primary key however many other columns they carry. The key itself
    has to differ.

    The default store keeps bare SKUs. That is not cosmetic -- every existing
    install is a single-store bench whose Item codes appear in Sales Orders,
    Stock Entries, price lists, barcodes, reports and other apps' links, and
    renaming them is not a migration anyone should run. So the first store's
    codes are exactly what they are today, and only stores added afterwards
    take a prefix.

    A blank SKU is handed back untouched. The importer has its own fallbacks
    for that case and this must not turn "no SKU" into a code that looks real.

    Idempotent: a `sku` already carrying THIS connection's own prefix is
    handed back unchanged rather than prefixed again. There is exactly one
    caller today and it never re-namespaces its own output, but the helper
    should not double-prefix if that ever changes -- `sim-a::sim-a::SKU1`
    is a real Item code that no longer matches anything on Shopify.
    """
    if not sku:
        return sku
    name = getattr(connection, "name", connection)
    if not name or name == DEFAULT_ITEM_CODE_CONNECTION:
        return sku
    if sku.startswith(f"{name}::"):
        return sku
    return f"{name}::{sku}"


def tag_doc_name(connection, tag_name: str) -> str:
    """
    The Shopify Tag row name a store's tag maps to.

    Same rule as item_code_for, same reason: tag_name stopped being globally
    unique the moment a second store could have its own "Sale" tag, and the
    row's name is that primary key. The default store keeps bare tag names
    -- every existing install's Item Shopify Tag rows already link to those
    names, and renaming them out from under every Item that references one
    is not a migration worth forcing. Only a store added after this exists
    gets a namespaced name.
    """
    if not tag_name:
        return tag_name
    name = getattr(connection, "name", connection)
    if not name or name == DEFAULT_ITEM_CODE_CONNECTION:
        return tag_name
    if tag_name.startswith(f"{name}::"):
        return tag_name
    return f"{name}::{tag_name}"



def sku_from_item_code(item_code: str) -> str:
    """The Shopify SKU behind an Item code, prefix removed if it has one."""
    if not item_code or "::" not in item_code:
        return item_code
    return item_code.split("::", 1)[1]
