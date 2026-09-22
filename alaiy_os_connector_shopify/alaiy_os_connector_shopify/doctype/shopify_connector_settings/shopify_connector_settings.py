# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
Backward-compat shim, not a real settings document.

This app moved from one Shopify Connector Settings Single per bench to
Shopify Connection, a normal DocType with one row per store (see
connections.py). Client-site code we don't all control -- Solist, Commerce,
others we may not know about -- still reads this doctype directly via
frappe.get_single / get_cached_doc / db.get_single_value, so it stays
registered rather than being retired, and every load returns whatever the
currently enabled Shopify Connection holds.

Read-only: nothing writes through this doctype any more. A save here would
have nowhere real to go, so the desk form is locked read-only field by
field, and this controller does not implement validate/on_update at all --
there is nothing left for either to do.
"""

import frappe
from frappe.model.document import Document

from alaiy_os_connector_shopify import connections


class ShopifyConnectorSettings(Document):
    def load_from_db(self):
        """Populate every field from the enabled Shopify Connection.

        `frappe.get_single()`, `frappe.get_cached_doc()` and a manual
        `frappe.get_doc("Shopify Connector Settings")` all end up here --
        Frappe's Single-loading path calls `load_from_db` the same as any
        other document. `frappe.db.get_single_value()` does NOT go through
        this class at all (it queries tabSingles by SQL directly); that
        path is covered separately by keeping tabSingles in sync, see
        `sync_legacy_settings_mirror()` below.
        """
        super().load_from_db()

        connection = connections.enabled_connection()
        if not connection:
            return

        mine = {df.fieldname for df in self.meta.fields if df.fieldname}
        for fieldname in mine:
            if connection.meta.has_field(fieldname):
                self.set(fieldname, connection.get(fieldname))


def sync_legacy_settings_mirror(doc=None, method=None):
    """
    Keep tabSingles for the retired doctype in step with the enabled
    connection, for the one read path `load_from_db` cannot reach:
    `frappe.db.get_single_value("Shopify Connector Settings", field)`
    queries tabSingles directly, bypassing the Document class entirely.

    Called once right after the Single-to-Connection migration, and again
    on every `Shopify Connection` change (see hooks.py's doc_events, which
    calls every on_update handler as fn(doc, method) -- doc/method are
    accepted and ignored here, since the source of truth is always
    connections.enabled_connection(), never the specific doc that changed).

    Leaves the previous values in place when nothing is enabled, rather
    than blanking them: a caller mid-read during a brief "switching stores"
    window sees the last real configuration instead of a false "nothing is
    configured here" for benches that have never gone truly unconfigured.
    """
    if not frappe.db.exists("DocType", "Shopify Connector Settings"):
        return

    connection = connections.enabled_connection()
    if not connection:
        return

    meta = frappe.get_meta("Shopify Connector Settings")
    mine = {
        df.fieldname
        for df in meta.fields
        if df.fieldname and df.fieldtype not in ("Section Break", "Column Break", "Tab Break", "HTML", "Table")
    }
    connection_meta = connection.meta
    for fieldname in mine:
        if not connection_meta.has_field(fieldname):
            continue
        if connection_meta.get_field(fieldname).fieldtype == "Password":
            # Password fields aren't in tabSingles even for the old Single --
            # get_password() reads __Auth, not this table. A caller reading a
            # secret via db.get_single_value has always gotten the masked
            # placeholder or nothing; nothing to mirror here.
            continue
        frappe.db.set_value(
            "Shopify Connector Settings",
            "Shopify Connector Settings",
            fieldname,
            connection.get(fieldname),
            update_modified=False,
        )
    # No explicit commit: this runs either inside the migration patch (which
    # commits on its own) or inside a request via the Shopify Connection
    # on_update hook, where Frappe's own request lifecycle owns the commit --
    # committing here would end the request's transaction early.
