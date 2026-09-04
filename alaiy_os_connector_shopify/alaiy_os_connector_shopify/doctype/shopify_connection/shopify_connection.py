# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class ShopifyConnection(Document):
    def validate(self):
        self._normalize_shop_url()
        self._assert_shop_not_taken()

        # Only decide here -- old_enabled is the last-committed DB value, so
        # this comparison has to happen before this save overwrites it.
        old_enabled = (
            frappe.db.get_value(self.doctype, self.name, "is_enabled")
            if not self.is_new()
            else 0
        ) or 0
        self.flags.shopify_just_enabled = bool(self.is_enabled and not old_enabled)
        self.flags.shopify_just_disabled = bool(not self.is_enabled and old_enabled)

        self._assert_single_enabled()
        self._sync_registry_is_enabled()
        self._validate_default_warehouse()

    def _normalize_shop_url(self):
        """
        One spelling of a store, because the webhook receiver routes on it.

        Shopify sends the store as a bare host in X-Shopify-Shop-Domain. If one
        connection is saved as "https://acme.myshopify.com/" and another as
        "acme.myshopify.com", the lookup matches neither and every webhook from
        that store is rejected -- so the scheme and trailing slash come off here
        rather than at each of the places that compare.
        """
        if not self.sh_shop_url:
            return
        shop = self.sh_shop_url.strip().lower()
        shop = shop.removeprefix("https://").removeprefix("http://")
        self.sh_shop_url = shop.split("/")[0]

    def _assert_shop_not_taken(self):
        """
        No two connections on the same store.

        Not a database unique index: the column is empty on a connection an app
        has created but not finished configuring, and MySQL would count those
        empty strings as duplicates of each other. This says the real rule --
        two *configured* connections cannot name one store -- and can say why.

        It is not cosmetic. Webhook delivery is attributed by shop domain, so a
        second connection on the same store makes that attribution ambiguous,
        and whichever row happened to sort first would receive the other
        store's orders.
        """
        if not self.sh_shop_url:
            return
        clash = frappe.db.get_value(
            self.doctype,
            {"sh_shop_url": self.sh_shop_url, "name": ("!=", self.name)},
            "name",
        )
        if clash:
            frappe.throw(
                f"Shopify connection '{clash}' is already on {self.sh_shop_url}. "
                "One connection per store -- edit that one instead."
            )

    def _assert_single_enabled(self):
        """
        One store at a time drives ERPNext.

        Enabling a connection arms this connector's Item and Sales Order
        document events, its inventory push and its order import -- all of
        which write records with nowhere to record which store they came from
        (Shopify Location is keyed on Shopify's own location id; Item and Sales
        Order carry a bare sh_shopify_product_id / sh_shopify_order_id). Two
        enabled stores would silently overwrite each other in every one of
        those places.

        So the limit is stated here rather than discovered later as mixed-up
        data. Holding many connections is still fine and is the reason this
        DocType exists -- they just answer API reads, which is all a
        multi-tenant bench asks of them.
        """
        if not self.is_enabled:
            return
        other = frappe.db.get_value(
            self.doctype, {"is_enabled": 1, "name": ("!=", self.name)}, "name"
        )
        if other:
            frappe.throw(
                f"Shopify connection '{other}' is already the enabled store on this "
                "site, and only one store at a time can drive Alaiy OS orders, "
                "inventory and listings. Disable it first, or leave this connection "
                "switched off -- it can still be used to read from Shopify."
            )

    def _validate_default_warehouse(self):
        """
        Confirmed live: a real site had Default Warehouse set to the
        auto-seeded root Group Warehouse ("All Warehouses - <Co Abbr>") --
        it "looked like" a sensible default (top of the tree) but Alaiy OS
        rejects any stock transaction against a Group Warehouse, so every
        Delivery Note auto-created from a Shopify fulfillment failed. Catch
        this at save time so it can never be configured wrong in the first
        place, on any site.
        """
        if not self.sh_default_warehouse:
            return
        if frappe.db.get_value("Warehouse", self.sh_default_warehouse, "is_group"):
            frappe.throw(
                f"'{self.sh_default_warehouse}' is a Group Warehouse (an organizational "
                "folder, not a real stock location) -- Alaiy OS doesn't allow stock "
                "transactions against it. Pick a leaf warehouse instead, e.g. "
                "'Stores - <Company Abbr>' or 'Finished Goods - <Company Abbr>'."
            )

    def on_update(self):
        # Actually calling out to Shopify has to wait until after this
        # document's own row is written -- ShopifyGraphQLClient builds
        # itself from a fresh read, which during validate() (before the
        # write) would still see the OLD Shop URL/credentials, not
        # whatever was just entered on this save.
        if self.flags.shopify_just_enabled:
            self._on_first_enable()
        elif self.flags.shopify_just_disabled:
            self._on_disable()

    def _on_first_enable(self):
        from alaiy_os_connector_shopify.setup.install import setup_custom_fields
        setup_custom_fields()

        try:
            from alaiy_os_connector_shopify.shopify.webhooks import ensure_webhooks_registered
            ensure_webhooks_registered(self)
        except Exception:
            frappe.log_error(
                title="Shopify: webhook registration failed on enable",
                message=frappe.get_traceback(),
            )

    def _on_disable(self):
        try:
            from alaiy_os_connector_shopify.shopify.webhooks import unregister_webhooks
            unregister_webhooks(self)
        except Exception:
            frappe.log_error(
                title="Shopify: webhook unregistration failed on disable",
                message=frappe.get_traceback(),
            )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------
    def is_connected(self) -> bool:
        """
        True when this connection can actually call Shopify.

        A store reached with a pasted Admin API token has no client id or
        secret and never mints anything; a store set up with a custom app has
        both and mints on demand. Either is connected, so this asks for the
        outcome (a usable token, or the means to get one) rather than for one
        particular way of having arrived at it.
        """
        if not self.sh_shop_url:
            return False
        if self.get_password("sh_access_token", raise_exception=False):
            return True
        return bool(
            self.sh_client_id
            and self.get_password("sh_client_secret", raise_exception=False)
        )

    def set_status(self, status: str, message: str | None = None) -> None:
        """Persist connection status + message without a full form save."""
        self.db_set("last_status", status, update_modified=False)
        if message is not None:
            self.db_set("last_status_message", message[:1000], update_modified=False)
        if status == "connected":
            self.db_set("connected_at", now_datetime(), update_modified=False)
        self._sync_registry_status(status)

    def _sync_registry_status(self, status: str) -> None:
        """Mirror our status onto the OS Connector Registry row so the Alaiy OS
        connector card reflects a real connect, not just a Test click."""
        try:
            if not frappe.db.exists("OS Connector Registry", "shopify"):
                return
            mapped = {
                "connected": "connected",
                "error": "failed",
                "not_configured": "untested",
            }.get(status, "untested")
            values = {"connection_status": mapped}
            if status in ("connected", "error"):
                values["last_tested_at"] = now_datetime()
            frappe.db.set_value(
                "OS Connector Registry", "shopify", values, update_modified=False
            )
        except Exception:
            frappe.log_error(
                title="Shopify connector: registry status sync failed",
                message=frappe.get_traceback(),
            )

    def _sync_registry_is_enabled(self):
        """
        Mirror the enable flag onto the registry card.

        Only the default connection speaks for the card. The registry has one
        row per connector, not per store, so on a multi-tenant bench letting
        every connection write it would mean the last save won -- one seller
        disabling their store would show the whole connector as off.
        """
        if not frappe.db.exists("OS Connector Registry", "shopify"):
            return
        from alaiy_os_connector_shopify import connections

        if not self.is_default and len(connections.names()) > 1:
            return
        frappe.db.set_value(
            "OS Connector Registry", "shopify", "is_enabled", self.is_enabled
        )

    def clear_credentials(self, message: str | None = None) -> None:
        """
        Drop everything this connection could call Shopify with.

        Password values live in the __Auth table; clearing the document column
        alone leaves the encrypted secret behind and still usable, so remove it
        there too.
        """
        from frappe.utils.password import remove_encrypted_password

        for field in ("sh_access_token", "sh_client_secret", "sh_webhook_secret"):
            remove_encrypted_password(self.doctype, self.name, field)
            self.db_set(field, "", update_modified=False)

        self.db_set("sh_token_refreshed_at", None, update_modified=False)
        self.db_set("sh_token_expires_at", None, update_modified=False)
        self.set_status("not_configured", message or "Disconnected")

    def ping(self) -> dict:
        """Verify the connection with the cheapest authenticated query there is."""
        from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

        if not self.is_connected():
            self.set_status("not_configured", "No Shopify credentials stored.")
            return {"status": "not_configured"}

        try:
            data = ShopifyGraphQLClient(self).execute("{ shop { name myshopifyDomain } }")
        except Exception as e:
            self.set_status("error", str(e))
            return {"status": "error", "message": str(e)}

        shop = (data or {}).get("shop") or {}
        self.set_status("connected", f"OK ({shop.get('name') or self.sh_shop_url})")
        return {"status": "connected", "shop": shop.get("name")}
