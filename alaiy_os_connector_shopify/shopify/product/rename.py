"""Change an Item's code, which is the SKU the product is sent to Shopify under.

Shopify's SKU is always the Item code, and the connector matches variants and order
lines back to Items by it, so the SKU cannot be changed on its own: the Item is
renamed, and everything named after the old code moves with it.

frappe.rename_doc already updates every Link field that points at the Item (Bin,
Item Price, stock ledger, Listing Variant, Supplier Product, ...). Three things it
does not reach are handled here:
  - Shopify Product Listing and Shopify Enriched Listing are named after the Item,
    so their names stay on the old code unless renamed too.
  - Shopify Synced Entity keeps the Item code in a plain text field. Left behind,
    the next push finds no record for the product and creates a second one.

Not whitelisted: the caller owns the permission check.
"""

import frappe

_ITEM_NAMED_DOCTYPES = (
    ("Shopify Product Listing", "item"),
    ("Shopify Enriched Listing", "item_code"),
)


def rename_item_code(old_code: str, new_code: str) -> str:
    """Rename Item `old_code` to `new_code` and keep the Shopify records in step.

    Returns the new code. Any failure rolls the whole change back and re-raises.
    """
    new_code = (new_code or "").strip()
    if not frappe.db.exists("Item", old_code):
        frappe.throw(frappe._("Item {0} does not exist.").format(old_code))
    if not new_code:
        frappe.throw(frappe._("Enter a SKU."))
    if len(new_code) > 140:
        frappe.throw(frappe._("A SKU can be at most 140 characters."))
    if new_code == old_code:
        return old_code
    if frappe.db.exists("Item", new_code):
        frappe.throw(frappe._("Another product already uses the SKU {0}.").format(new_code))
    # A record named after the new code would make the renames below collide.
    for doctype, _field in _ITEM_NAMED_DOCTYPES:
        if frappe.db.exists(doctype, new_code):
            frappe.throw(frappe._("{0} {1} already exists.").format(doctype, new_code))

    try:
        frappe.rename_doc("Item", old_code, new_code, force=True, ignore_permissions=True, show_alert=False)

        # The Link field on each is already on the new code; only the name is stale.
        for doctype, field in _ITEM_NAMED_DOCTYPES:
            for name in frappe.get_all(doctype, filters={field: new_code}, pluck="name"):
                if name != new_code:
                    frappe.rename_doc(doctype, name, new_code, force=True, ignore_permissions=True, show_alert=False)

        frappe.db.sql(
            """UPDATE `tabShopify Synced Entity` SET erpnext_name = %s
               WHERE erpnext_doctype = 'Item' AND erpnext_name = %s""",
            (new_code, old_code),
        )
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        raise
    return new_code
