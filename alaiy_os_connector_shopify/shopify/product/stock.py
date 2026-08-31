"""
Opening-stock / default-warehouse helpers -- moved verbatim from
product_import.py, unchanged.
"""

import frappe

from alaiy_os_connector_shopify.shopify.product.masters import _ensure_cost_center


def _default_warehouse_row(settings) -> dict:
    """
    Item Defaults row (company + default_warehouse) to append on every
    stocked Item at creation time. Without this, Alaiy OS has no warehouse
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


def _resolve_item_shopify_location(location_levels) -> str:
    """
    Real Shopify Location docname to write onto Item.shopify_location, or
    None if it can't be resolved unambiguously.

    Item.shopify_location is a plain generic field: which single Shopify
    Location does this item have real stock at, if exactly one. It has no
    opinion about supplier ownership -- that's a client-specific concern
    (some sites map a Location to a Supplier via their own custom field,
    others don't) and does not belong hardcoded into the shared connector.
    A client wanting per-supplier scoping resolves that themselves off this
    generic fact in their own app code.

    location_levels (from variants._variant_location_levels) is the exact
    same Shopify inventoryLevels data opening stock already resolves through
    per-location warehouses -- this just resolves the SAME pairs to a
    Shopify Location docname instead of a Warehouse.

    Deliberately conservative: only returns a location when exactly ONE
    real Shopify Location shows real stock (qty > 0) for this item.
    Multiple locations, or none, return None -- writing a single value onto
    an item genuinely split across locations would be actively wrong, not
    just incomplete.
    """
    if not location_levels:
        return None

    # Item.shopify_location is a client-added custom field, not something
    # the shared connector itself defines. A client site without it should
    # see this helper no-op, not crash on an unknown Item attribute.
    if not frappe.get_meta("Item").get_field("shopify_location"):
        return None

    candidates = set()
    for location_id, qty in location_levels:
        if not qty:
            continue
        location_name = frappe.db.get_value("Shopify Location", {"sh_location_id": str(location_id)}, "name")
        if location_name:
            candidates.add(location_name)

    if len(candidates) == 1:
        return next(iter(candidates))
    return None


def _sync_item_supplier_from_location(item_code: str, location_name: str):
    """Create an Item Supplier row for item_code from the resolved Shopify
    Location's own supplier mapping, if that mapping exists on this site.

    Item Supplier is real ERPNext core, safe to write to on any site. What's
    NOT generic is knowing which Supplier a Shopify Location belongs to --
    that's only ever answered by a client-added custom field
    (Shopify Location.linked_supplier on the one site that has it today).
    Explicitly guarded on that field existing before reading it -- unlike a
    plain doc attribute, frappe.db.get_value on an unknown column raises a
    real SQL error rather than returning None, so this must check
    get_field() first, same as _resolve_item_shopify_location's own guard
    above, just one hop further down the resolution chain.
    """
    if not location_name:
        return
    if not frappe.get_meta("Shopify Location").get_field("linked_supplier"):
        return
    supplier = frappe.db.get_value("Shopify Location", location_name, "linked_supplier")
    if not supplier:
        return
    if frappe.db.exists("Item Supplier", {"parent": item_code, "parenttype": "Item", "supplier": supplier}):
        return
    frappe.get_doc({
        "doctype": "Item Supplier",
        "parenttype": "Item",
        "parentfield": "supplier_items",
        "parent": item_code,
        "supplier": supplier,
    }).insert(ignore_permissions=True)


def _resolve_opening_stock_rows(qty: float, settings, location_levels=None) -> list:
    """
    [(warehouse, qty), ...] to open this item's stock at -- one row per
    real Shopify location that resolves to a mapped warehouse (via
    order.warehouse._resolve_warehouse_for_location, the same lookup
    already used for Delivery Note/fulfillment routing), instead of
    always dumping the whole quantity into one shared default warehouse
    regardless of which real supplier the item belongs to.

    Falls back to the single default-warehouse row (old behavior,
    unchanged) when location_levels is empty/None, or when none of its
    locations resolve to a mapped warehouse -- so a site with no
    sh_location_map configured at all keeps working exactly as before.
    """
    if location_levels:
        from alaiy_os_connector_shopify.shopify.order.warehouse import _resolve_warehouse_for_location
        rows = {}
        for location_id, level_qty in location_levels:
            warehouse = _resolve_warehouse_for_location(location_id, settings)
            if warehouse and level_qty:
                rows[warehouse] = rows.get(warehouse, 0) + level_qty
        if rows:
            return list(rows.items())

    warehouse = settings.sh_default_warehouse
    if not warehouse:
        frappe.log_error(
            title="Shopify import: no default warehouse configured",
            message=f"Item imported with qty {qty} but no opening stock entry could be made"
        )
        return []
    if not frappe.db.exists("Warehouse", warehouse):
        frappe.log_error(
            title=f"Shopify import: warehouse {warehouse} not found",
            message="Item will not have opening stock set"
        )
        return []
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
                message="Item will not have opening stock set"
            )
            return []
        warehouse = leaf
    return [(warehouse, qty)]


def _set_opening_stock(item_code: str, qty: float, settings, location_levels=None):
    """
    Record Shopify's current available quantity as this Item's opening
    stock via a Material Receipt Stock Entry -- the standard Alaiy OS way
    to set an initial stock balance (Bin.actual_qty is derived from the
    stock ledger, not directly writable). Without this, every imported
    item lands in Alaiy OS with zero stock regardless of what's actually
    available on Shopify.

    location_levels (optional): [(shopify_location_id, qty), ...] -- when
    given and at least one location resolves to a mapped warehouse, opens
    stock directly in the real per-supplier warehouse(s) instead of the
    one shared default. See _resolve_opening_stock_rows.
    """
    rows = _resolve_opening_stock_rows(qty, settings, location_levels)
    if not rows:
        return

    # One Stock Entry per company -- a resolved warehouse can belong to a
    # different company than another (unlikely on a single-company site,
    # but a real possibility once multiple real per-supplier warehouses
    # are in play), and one Stock Entry can only ever have one company.
    rows_by_company = {}
    for warehouse, row_qty in rows:
        company = frappe.db.get_value("Warehouse", warehouse, "company") or frappe.defaults.get_global_default("company")
        if not company:
            frappe.log_error(
                title="Shopify import: no company resolved for opening stock",
                message=f"Item {item_code} warehouse {warehouse} will not have opening stock set"
            )
            continue
        rows_by_company.setdefault(company, []).append((warehouse, row_qty))

    for company, company_rows in rows_by_company.items():
        cost_center = _ensure_cost_center(company)
        if not cost_center:
            frappe.log_error(
                title=f"Shopify import: no usable Cost Center for company {company}",
                message=f"Item {item_code} will not have opening stock set"
            )
            continue

        # Confirmed live: a real site had zero "Stock Entry Type" master
        # records at all (Material Receipt/Issue/etc.), which is standard
        # Alaiy OS seed data -- every Stock Entry insert failed with
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

        # Same class of missing-company-default: Alaiy OS requires a Stock
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
            for warehouse, row_qty in company_rows:
                se.append("items", {
                    "item_code": item_code,
                    "qty": row_qty,
                    "t_warehouse": warehouse,
                    "cost_center": cost_center,
                    # Shopify's price is a selling price, not a cost basis -- we
                    # have no real valuation rate to give this opening stock, and
                    # Alaiy OS otherwise blocks submit with "Valuation Rate Missing"
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
