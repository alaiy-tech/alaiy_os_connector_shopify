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
            from alaiy_os_connector_shopify.shopify.webhooks import register_webhooks
            register_webhooks()
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
