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


def _resolve_item_shopify_location(location_levels, settings=None, item_code=None) -> str:
    """
    Real Shopify Location docname to write onto Item.shopify_location, or
    None if it can't be resolved.

    Item.shopify_location is a plain generic field: which single Shopify
    Location does this item have real stock at. It has no opinion about
    supplier ownership -- that's a client-specific concern (some sites map
    a Location to a Supplier via their own custom field, others don't) and
    does not belong hardcoded into the shared connector. A client wanting
    per-supplier scoping resolves that themselves off this generic fact.

    location_levels (from variants._variant_location_levels) is the exact
    same Shopify inventoryLevels data opening stock already resolves through
    per-location warehouses -- this just resolves the SAME pairs to a
    Shopify Location docname instead of a Warehouse.

    Which locations an item is LISTED at and which actually HOLD it are
    different questions, and only the second answers ownership. Confirmed
    live on a real store: products are routinely listed against three or
    four locations while carrying stock at exactly one, the others sitting
    at zero right across the catalogue. Resolving on listing alone made
    almost every product look ambiguous.

    Resolution order:
      - one location listed at all: that one, whatever its quantity
      - stock at exactly one location: that one owns it
      - stock at two or more locations: unresolved and logged, with no
        exception for one of them being the default (HQ) warehouse. Stock
        genuinely sitting in two places is a real question about who
        fulfils it and who gets paid, and answering that in the importer
        would be actively wrong rather than merely incomplete
      - listed in several places, held nowhere: also unresolved and
        logged. On a store where selling out archives the product this
        should never reach an Active import, so it is worth seeing
    """
    if not location_levels:
        return None

    # Item.shopify_location is a client-added custom field, not something
    # the shared connector itself defines. A client site without it should
    # see this helper no-op, not crash on an unknown Item attribute.
    if not frappe.get_meta("Item").get_field("shopify_location"):
        return None

    candidates = set()
    stocked = set()
    for location_id, qty in location_levels:
        location_name = frappe.db.get_value("Shopify Location", {"sh_location_id": str(location_id)}, "name")
        if not location_name:
            continue
        candidates.add(location_name)
        if qty and qty > 0:
            stocked.add(location_name)

    # One location overall: unambiguous on its own, whatever the quantity.
    if len(candidates) == 1:
        return next(iter(candidates))

    # Listed at several locations but held at exactly one: that one owns it.
    # Confirmed live on a real store -- products are routinely listed against
    # three or four locations while only ever carrying stock at a single one,
    # the others sitting at zero across the whole catalogue. Reading listing
    # alone there makes almost every product look ambiguous.
    if len(stocked) == 1:
        return next(iter(stocked))

    if len(stocked) >= 2:
        # No exception for the default (HQ) warehouse being one of the two.
        # Stock genuinely sitting in two places is a real question about who
        # fulfils and who gets paid, and resolving it to the non-HQ location
        # would quietly answer that question in the importer. Flag it and let
        # a human decide.
        frappe.log_error(
            title="Shopify import: item stocked at multiple locations, can't resolve shopify_location",
            message=f"item_code={item_code}, stocked at={sorted(stocked)} "
            f"(listed at={sorted(candidates)}). Two or more real locations hold this "
            "item, so ownership cannot be resolved automatically. Needs a human decision.",
        )
        return None

    if not stocked and len(candidates) >= 2:
        # Listed in several places, held nowhere. On a store where selling out
        # archives the product this should not reach an Active import at all,
        # so it is worth seeing rather than guessing an owner from listing.
        frappe.log_error(
            title="Shopify import: item has no stock at any location, can't resolve shopify_location",
            message=f"item_code={item_code}, candidate locations={sorted(candidates)}. "
            "Needs a human decision -- see Item Supplier / manual review.",
        )

    return None


def _write_shopify_location_from_supplier(item_code: str):
    """Counterpart to the import-direction resolution above, for an item
    that started life the OTHER way: created locally first (a manually-
    built Item, or one promoted through a client's own supplier-submission
    approval flow) and only now getting its first Shopify Product Listing --
    the point that actually makes it a Shopify-linkable product, whether or
    not it has been pushed yet.

    That path already knows its real Item Supplier before any Shopify
    product exists -- there's no ambiguity to resolve from inventory
    levels, unlike a fresh Shopify import. This just goes the other way:
    Item Supplier's known supplier -> the Shopify Location(s) whose
    linked_supplier matches it -> Item.shopify_location, if exactly one.

    Only fires when the field doesn't already have a value, and only when
    both the client-added shopify_location and linked_supplier fields exist
    on this site -- same generic field-guard posture as everywhere else in
    this module.
    """
    if not frappe.get_meta("Item").get_field("shopify_location"):
        return
    if not frappe.get_meta("Shopify Location").get_field("linked_supplier"):
        return
    if frappe.db.get_value("Item", item_code, "shopify_location"):
        return

    suppliers = frappe.get_all(
        "Item Supplier", filters={"parent": item_code, "parenttype": "Item"}, pluck="supplier"
    )
    if len(suppliers) != 1:
        # No supplier, or more than one -- same "don't guess" posture as
        # the multi-location import case. A multi-supplier item has no
        # single correct answer here either.
        return

    locations = frappe.get_all(
        "Shopify Location", filters={"linked_supplier": suppliers[0]}, pluck="name"
    )
    if len(locations) != 1:
        return

    frappe.db.set_value("Item", item_code, "shopify_location", locations[0])


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
