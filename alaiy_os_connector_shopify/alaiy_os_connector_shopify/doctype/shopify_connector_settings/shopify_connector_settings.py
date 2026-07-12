import frappe
from frappe.model.document import Document


class ShopifyConnectorSettings(Document):
    def validate(self):
        old_enabled = frappe.db.get_single_value(
            "Shopify Connector Settings", "is_enabled"
        ) or 0
        if self.is_enabled and not old_enabled:
            self._on_first_enable()
        elif not self.is_enabled and old_enabled:
            self._on_disable()
        self._sync_registry_is_enabled()

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
