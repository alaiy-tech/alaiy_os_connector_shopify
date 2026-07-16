import frappe
from frappe.utils.nestedset import NestedSet


class ShopifyCategory(NestedSet):
    def autoname(self):
        if not self.name:
            self.name = self.shopify_category_name
