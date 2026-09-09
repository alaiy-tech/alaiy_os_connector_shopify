# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
The guard in front of the connector's two bulk deletes.

`_wipe_all_items` and `api.clear_orders` both select their victims by "the
Shopify id is set" and nothing else. On a single-store bench that reads as
"everything this connector imported", which is what they were written for. On
a bench holding two sellers it reads as "everything BOTH sellers imported" --
one seller re-importing their catalogue deletes the other's Items, zeroes the
other's stock, and drops the other's Sales Orders with the invoices and
delivery notes hanging off them.

The rows carry nothing that says which store they came from yet, so there is
no filter to add here: the column does not exist. Until it does, the only
honest answer on a multi-store bench is to refuse.

That is deliberately not a stopgap for its own sake. It is the ordering the
work needs -- the column arrives next, the backfill after it, and only then
can these two selects be narrowed to one store. Refusing first means the
window where a second connection exists and these deletes are still bench-wide
never opens.

`ack_multi_store` is the override, and it is not a convenience. It exists for
the one legitimate case -- an operator who genuinely means "clear every
store's data on this bench" -- and it has to be passed explicitly, so it can
never be reached by a default argument or a forgotten parameter.
"""

import frappe
from frappe import _

from alaiy_os_connector_shopify import connections


class CrossStoreDeletion(frappe.ValidationError):
    """A bulk delete would have crossed a store boundary."""


def assert_safe(operation: str, ack_multi_store: bool = False) -> None:
    """
    Refuse a bench-wide delete when more than one store's rows are in range.

    `operation` names the caller in the error, because the person who hits
    this is at a bench console and needs to know which command stopped and
    why, not that an assertion somewhere failed.
    """
    stores = connections.names()
    if len(stores) <= 1 or ack_multi_store:
        return

    frappe.throw(
        _(
            "{0} deletes every Shopify-linked record on this site, and this site "
            "has {1} Shopify connections ({2}). The records do not yet record "
            "which store they belong to, so this cannot be limited to one of "
            "them -- running it would delete the other stores' data too.\n\n"
            "If you really do mean every store on this bench, pass "
            "ack_multi_store=1."
        ).format(operation, len(stores), ", ".join(stores)),
        CrossStoreDeletion,
    )
