import frappe
from frappe.model.document import Document


class ShopifyListingVariant(Document):
    # Row-level checks (variant_of match, no duplicates) live on the parent
    # Shopify Product Listing.validate -- only it can see the parent's `item`
    # and the full sibling set in one place.
    pass
