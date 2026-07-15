import frappe
from frappe.model.document import Document


class ShopifyConnectorSettings(Document):
    def validate(self):
        # Only decide here -- old_enabled is the last-committed DB value, so
        # this comparison has to happen before this save overwrites it.
        old_enabled = frappe.db.get_single_value(
            "Shopify Connector Settings", "is_enabled"
        ) or 0
        self.flags.shopify_just_enabled = bool(self.is_enabled and not old_enabled)
        self.flags.shopify_just_disabled = bool(not self.is_enabled and old_enabled)
        self._sync_registry_is_enabled()
        self._validate_default_warehouse()

    def _validate_default_warehouse(self):
        """
        Confirmed live: a real site had Default Warehouse set to the
        auto-seeded root Group Warehouse ("All Warehouses - <Co Abbr>") --
        it "looked like" a sensible default (top of the tree) but ERPNext
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
                "folder, not a real stock location) -- ERPNext doesn't allow stock "
                "transactions against it. Pick a leaf warehouse instead, e.g. "
                "'Stores - <Company Abbr>' or 'Finished Goods - <Company Abbr>'."
            )

    def on_update(self):
        # Actually calling out to Shopify has to wait until after this
        # document's own row is written -- ShopifyGraphQLClient builds
        # itself from a fresh frappe.get_single() read, which during
        # validate() (before the write) would still see the OLD Shop
        # URL/credentials, not whatever was just entered on this save.
        if self.flags.shopify_just_enabled:
            self._on_first_enable()
        elif self.flags.shopify_just_disabled:
            self._on_disable()

    def _on_first_enable(self):
        from alaiy_os_connector_shopify.setup.install import setup_custom_fields
        setup_custom_fields()

        try:
            from alaiy_os_connector_shopify.shopify.webhooks import ensure_webhooks_registered
            ensure_webhooks_registered()
        except Exception:
            frappe.log_error(
                title="Shopify: webhook registration failed on enable",
                message=frappe.get_traceback(),
            )

    def _on_disable(self):
        try:
            from alaiy_os_connector_shopify.shopify.webhooks import unregister_webhooks
            unregister_webhooks()
        except Exception:
            frappe.log_error(
                title="Shopify: webhook unregistration failed on disable",
                message=frappe.get_traceback(),
            )

    def _sync_registry_is_enabled(self):
        if frappe.db.exists("OS Connector Registry", "shopify"):
            frappe.db.set_value(
                "OS Connector Registry", "shopify", "is_enabled", self.is_enabled
            )
