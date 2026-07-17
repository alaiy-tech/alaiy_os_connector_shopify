"""
Opening-stock / default-warehouse helpers -- moved verbatim from
product_import.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.masters import _ensure_cost_center


def _default_warehouse_row(settings) -> dict:
    """
    Item Defaults row (company + default_warehouse) to append on every
    stocked Item at creation time. Without this, ERPNext has no warehouse
    to suggest when an Item is picked on any document created directly in
    the desk UI (not through our own webhook/import code, which always
    resolves a warehouse itself) -- confirmed live: manually creating a
    Sales Order for an imported item hit "Source warehouse required",
    forcing the warehouse to be typed in by hand every single time.
    """
    warehouse = settings.sh_default_warehouse
    if not warehouse or not frappe.db.exists("Warehouse", warehouse):
        return None
    company = frappe.db.get_value("Warehouse", warehouse, "company") or frappe.defaults.get_global_default("company")
    if not company:
        return None
    return {"company": company, "default_warehouse": warehouse}


def _set_opening_stock(item_code: str, qty: float, settings):
    """
    Record Shopify's current available quantity as this Item's opening
    stock via a Material Receipt Stock Entry -- the standard ERPNext way
    to set an initial stock balance (Bin.actual_qty is derived from the
    stock ledger, not directly writable). Without this, every imported
    item lands in ERPNext with zero stock regardless of what's actually
    available on Shopify.
    """
    warehouse = settings.sh_default_warehouse
    if not warehouse:
        frappe.log_error(
            title="Shopify import: no default warehouse configured",
            message=f"Item {item_code} imported with qty {qty} but no opening stock entry could be made"
        )
        return
    if not frappe.db.exists("Warehouse", warehouse):
        frappe.log_error(
            title=f"Shopify import: warehouse {warehouse} not found",
            message=f"Item {item_code} will not have opening stock set"
        )
        return
    if frappe.db.get_value("Warehouse", warehouse, "is_group"):
        # Same class of bug order_sync._resolve_default_warehouse already
        # self-heals for orders -- confirmed live on a second client site
        # that this opening-stock path never got the same fallback, so a
        # Group Warehouse configured as default blocked every single
        # opening stock entry with "Group node warehouse is not allowed."
        leaf = frappe.db.get_value("Warehouse", {"is_group": 0, "company": frappe.db.get_value("Warehouse", warehouse, "company")}, "name")
        if not leaf:
            leaf = frappe.db.get_value("Warehouse", {"is_group": 0}, "name")
        if not leaf:
            frappe.log_error(
                title="Shopify import: Default Warehouse is a Group Warehouse, no leaf fallback found",
                message=f"Item {item_code} will not have opening stock set"
            )
            return
        warehouse = leaf

    company = frappe.db.get_value("Warehouse", warehouse, "company") or frappe.defaults.get_global_default("company")
    if not company:
        frappe.log_error(
            title="Shopify import: no company resolved for opening stock",
            message=f"Item {item_code} will not have opening stock set"
        )
        return

    cost_center = _ensure_cost_center(company)
    if not cost_center:
        frappe.log_error(
            title=f"Shopify import: no usable Cost Center for company {company}",
            message=f"Item {item_code} will not have opening stock set"
        )
        return

    # Confirmed live: a real site had zero "Stock Entry Type" master
    # records at all (Material Receipt/Issue/etc.), which is standard
    # ERPNext seed data -- every Stock Entry insert failed with
    # "Could not find Stock Entry Type: Material Receipt" regardless of
    # warehouse/cost center being correct. Self-heal the one type we
    # actually need rather than requiring console setup per client.
    if not frappe.db.exists("Stock Entry Type", "Material Receipt"):
        frappe.get_doc({
            "doctype": "Stock Entry Type",
            "name": "Material Receipt",
            "purpose": "Material Receipt",
        }).insert(ignore_permissions=True)
        frappe.db.commit()

    # Same class of missing-company-default: ERPNext requires a Stock
    # Adjustment Account (or a per-entry Difference Account) for any
    # Material Receipt. Confirmed live: company had the account itself
    # but never had it set as the default. Pick any existing "Stock
    # Adjustment" account for this company rather than requiring
    # someone to configure it by hand on every client site.
    if not frappe.db.get_value("Company", company, "stock_adjustment_account"):
        fallback_account = frappe.db.get_value(
            "Account", {"company": company, "account_name": ["like", "%Stock Adjustment%"]}, "name"
        )
        if fallback_account:
            frappe.db.set_value("Company", company, "stock_adjustment_account", fallback_account)
            frappe.db.commit()

    try:
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Receipt"
        se.company = company
        se.append("items", {
            "item_code": item_code,
            "qty": qty,
            "t_warehouse": warehouse,
            "cost_center": cost_center,
            # Shopify's price is a selling price, not a cost basis -- we
            # have no real valuation rate to give this opening stock, and
            # ERPNext otherwise blocks submit with "Valuation Rate Missing"
            # on an item's very first stock-in.
            "allow_zero_valuation_rate": 1,
        })
        se.flags.ignore_permissions = True
        se.insert()
        se.submit()
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title=f"Failed to set opening stock for {item_code}",
            message=frappe.get_traceback()
        )
