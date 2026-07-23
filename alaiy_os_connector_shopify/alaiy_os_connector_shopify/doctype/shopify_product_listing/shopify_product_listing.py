import frappe
from frappe import _
from frappe.model.document import Document


class ShopifyProductListing(Document):
    def before_insert(self):
        # Auto-fill Images + Variants from the Item so a manually created
        # listing (pick a template -> save) gets the same rows an imported one
        # does. No-op if rows are already present.
        from alaiy_os_connector_shopify.shopify.product.listing import fill_children_from_item
        fill_children_from_item(self)

    def validate(self):
        self._validate_item_is_template()
        self._validate_variants()
        self._self_heal_all_variants_off()

    def _self_heal_all_variants_off(self):
        # An enabled listing whose every variant row is off would push an
        # empty variant set (Shopify-invalid) and stick "uploading" forever --
        # same guard the old on_item_change had: enable them all rather than
        # silently stall. Only when at least one variant row exists.
        if self.is_enabled and self.variants and not any(r.is_enabled for r in self.variants):
            for r in self.variants:
                r.is_enabled = 1

    def _validate_item_is_template(self):
        # A Listing is always keyed to the template, matching how
        # product/export.py::push_item resolves variant -> template today.
        it = frappe.db.get_value("Item", self.item, ["variant_of", "has_variants"], as_dict=True)
        if it and it.variant_of:
            frappe.throw(
                _("Shopify Product Listing must link a template Item, not a variant ({0}).").format(self.item)
            )
        # A template with ZERO variant children can't be pushed (Shopify needs
        # at least one variant, and an empty template is invalid). Block manual
        # creation with a clear message rather than letting it save a listing
        # that silently never syncs. The trusted from_shopify_sync path
        # (backfill/import) is exempt -- it only mirrors existing data.
        if not self.flags.from_shopify_sync and it and it.has_variants \
                and not frappe.db.exists("Item", {"variant_of": self.item}):
            frappe.throw(
                _("{0} is a template with no variants -- nothing to list on Shopify. "
                  "Add at least one variant to the product first.").format(self.item)
            )

    def _validate_variants(self):
        seen = set()
        for row in self.variants or []:
            if row.item_variant in seen:
                frappe.throw(
                    _("Variant {0} is listed more than once.").format(row.item_variant)
                )
            seen.add(row.item_variant)
            variant_of = frappe.db.get_value("Item", row.item_variant, "variant_of")
            if variant_of != self.item:
                frappe.throw(
                    _("Variant {0} does not belong to template {1}.").format(row.item_variant, self.item)
                )
