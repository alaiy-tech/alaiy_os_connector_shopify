"""
Master-data ensure-helpers (Brand, Item Group, Item Attribute, UOM, Cost
Center) -- moved verbatim from product_import.py, unchanged.
"""

import frappe


def _dedupe_item_uoms(item):
    """
    Self-heal duplicated UOM rows in the conversion factor table before
    saving `item` -- confirmed live: Alaiy OS's own Item.validate() appends
    a default UOM row if it doesn't see one yet, and two near-simultaneous
    saves of the same freshly-created template can each independently
    decide "no row yet" and append one, leaving a duplicate. Since saving
    a template cascades save() calls to all its variants, both the
    template and all its variants must be cleaned at the database level
    before the save runs, or ERPNext's own validate_conversion_factor
    throws "Unit of Measure ... entered more than once".

    Shared by both inbound paths that can hit this: webhook product
    updates (product/webhooks.py) and the product-import update path
    (product/importer.py) -- confirmed live to hit the exact same error
    on a real re-import once a duplicate already existed from an earlier
    race.
    """
    all_item_names = [item.name]
    if item.has_variants:
        all_item_names += frappe.get_all("Item", filters={"variant_of": item.name}, pluck="name")

    for name in all_item_names:
        duplicates = frappe.db.sql("""
            SELECT uom, MIN(name) as keep_name
            FROM `tabUOM Conversion Detail`
            WHERE parent = %s
            GROUP BY uom
            HAVING COUNT(*) > 1
        """, name, as_dict=True)

        for dup in duplicates:
            frappe.db.sql("""
                DELETE FROM `tabUOM Conversion Detail`
                WHERE parent = %s AND uom = %s AND name != %s
            """, (name, dup.uom, dup.keep_name))

    seen_uoms = set()
    deduped = []
    for row in item.uoms:
        if row.uom in seen_uoms:
            continue
        seen_uoms.add(row.uom)
        deduped.append(row)
    item.uoms = deduped


def _ensure_brand(name: str) -> str:
    """
    Item.brand is also a mandatory-shaped Link field (to the Brand
    doctype), not free text -- Shopify's vendor string fails the same way
    productType does if no Brand of that exact name exists yet.
    """
    name = (name or "").strip()
    if not name:
        return None
    if frappe.db.exists("Brand", name):
        return name
    try:
        doc = frappe.new_doc("Brand")
        doc.brand = name
        doc.flags.ignore_permissions = True
        doc.insert()
        frappe.db.commit()
        return name
    except Exception:
        frappe.log_error(
            title=f"Shopify import: failed to create Brand {name}",
            message=frappe.get_traceback(),
        )
        return None


def _ensure_item_group(name: str) -> str:
    """
    Item.item_group is a mandatory Link field, not free text -- inserting
    Shopify's productType string directly (e.g. "Demo Item Group") fails
    outright if no Item Group of that exact name exists yet. Creates one
    under the root "All Item Groups" if needed, and falls back to that
    root itself if the name is blank or the create fails for any reason.
    """
    name = (name or "").strip()
    if not name:
        return "All Item Groups"
    if frappe.db.exists("Item Group", name):
        return name
    try:
        doc = frappe.new_doc("Item Group")
        doc.item_group_name = name
        doc.parent_item_group = "All Item Groups"
        doc.is_group = 0
        doc.flags.ignore_permissions = True
        doc.insert()
        frappe.db.commit()
        return name
    except Exception:
        frappe.log_error(
            title=f"Shopify import: failed to create Item Group {name}",
            message=frappe.get_traceback(),
        )
        return "All Item Groups"


def _ensure_item_group_path(full_name: str) -> str:
    """
    Build a nested Item Group hierarchy from a Shopify taxonomy fullName
    ("Apparel & Accessories > Clothing > Shirts") and return the leaf group
    name -- so Shopify products land in a real category tree (the way the
    cloudstore connector builds Item Groups) instead of everything flat under
    "All Item Groups" keyed off productType.

    Reuses existing groups by name; a node that will carry children is forced
    to is_group=1, the leaf is a normal assignable group. On any failure,
    falls back to the deepest group created so far (or None to let the caller
    fall back to productType).

    NOTE: Alaiy OS Item Group names are globally unique, so a leaf name that
    repeats across branches (e.g. "Shirts" under both Men and Women) resolves
    to a single shared group -- an Alaiy OS constraint, not a bug here.
    """
    parts = [p.strip() for p in (full_name or "").split(">") if p.strip()]
    if not parts:
        return None
    parent = "All Item Groups"
    leaf = None
    for i, name in enumerate(parts):
        is_last = i == len(parts) - 1
        if frappe.db.exists("Item Group", name):
            # A node that now needs children must be a group.
            if not is_last and not frappe.db.get_value("Item Group", name, "is_group"):
                frappe.db.set_value("Item Group", name, "is_group", 1)
        else:
            try:
                doc = frappe.new_doc("Item Group")
                doc.item_group_name = name
                doc.parent_item_group = parent
                doc.is_group = 0 if is_last else 1
                doc.flags.ignore_permissions = True
                doc.insert()
            except Exception:
                frappe.log_error(
                    title=f"Shopify import: failed to create Item Group {name}",
                    message=frappe.get_traceback(),
                )
                return leaf
        parent = name
        leaf = name
    frappe.db.commit()
    return leaf


def _make_attribute_abbr(value: str, existing_abbrs: set) -> str:
    """Item Attribute Value rows require a short, unique-per-attribute
    `abbr` alongside the display value -- derive one from the value itself
    and disambiguate on collision."""
    base = "".join(ch for ch in value.upper() if ch.isalnum())[:5] or "VAL"
    abbr = base
    i = 1
    while abbr in existing_abbrs:
        i += 1
        abbr = f"{base}{i}"
    return abbr


def _ensure_item_attribute(attribute_name: str, values: list):
    """
    Ensure an Item Attribute exists with this name, and that every value
    in `values` is registered in its allowed Item Attribute Value list --
    Alaiy OS rejects a variant whose attribute_value isn't pre-registered
    on the attribute, separately from the template needing the attribute
    declared at all.
    """
    if frappe.db.exists("Item Attribute", attribute_name):
        doc = frappe.get_doc("Item Attribute", attribute_name)
    else:
        doc = frappe.new_doc("Item Attribute")
        doc.attribute_name = attribute_name

    existing_values = {row.attribute_value for row in (doc.item_attribute_values or [])}
    existing_abbrs = {row.abbr for row in (doc.item_attribute_values or [])}
    changed = False
    for value in values:
        if not value or value in existing_values:
            continue
        abbr = _make_attribute_abbr(value, existing_abbrs)
        doc.append("item_attribute_values", {"attribute_value": value, "abbr": abbr})
        existing_values.add(value)
        existing_abbrs.add(abbr)
        changed = True

    if doc.is_new():
        doc.flags.ignore_permissions = True
        doc.insert()
        frappe.db.commit()
    elif changed:
        doc.flags.ignore_permissions = True
        doc.save()
        frappe.db.commit()


def _ensure_uom(name: str) -> str:
    if not frappe.db.exists("UOM", name):
        frappe.get_doc({"doctype": "UOM", "uom_name": name}).insert(ignore_permissions=True)
    return name


def _ensure_cost_center(company: str) -> str:
    """
    Return a usable leaf Cost Center for this company, self-healing broken
    setups instead of requiring manual console fixes on every client site.

    Confirmed live: a real site's root Cost Center had its own
    parent_cost_center dangling (pointing at "<company>", a plain string
    that isn't itself a Cost Center -- the real root is always named
    "<company> - <abbr>"), which corrupted its lft/rgt to 0/0 and made
    every attempt to create a child fail with "Item cannot be added to
    its own descendants". A root's parent must be blank, not a dangling
    reference, for the nested-set tree to be valid -- clear it and
    rebuild before trying to create anything.
    """
    company_default = frappe.db.get_value("Company", company, "cost_center")
    if company_default and not frappe.db.get_value("Cost Center", company_default, "is_group"):
        return company_default

    existing_leaf = frappe.db.get_value(
        "Cost Center", {"company": company, "is_group": 0}, "name"
    )
    if existing_leaf:
        frappe.db.set_value("Company", company, "cost_center", existing_leaf)
        return existing_leaf

    abbr = frappe.db.get_value("Company", company, "abbr")
    root = f"{company} - {abbr}" if abbr else None
    if not root or not frappe.db.exists("Cost Center", root):
        return None

    parent = frappe.db.get_value("Cost Center", root, "parent_cost_center")
    # A parent literally shaped like "<company>" is unsubstituted ERPNext
    # seed-data placeholder text, not a real reference -- even if a Cost
    # Center row happens to exist under that exact broken name (leftover
    # corrupt seed data), it's still not a valid parent. Checking
    # `not exists(...)` alone missed this case: the corrupt row's mere
    # presence let the dangling reference stand, and every later nested-set
    # operation that touched it re-threw "Name cannot contain special
    # characters like '<', '>'" -- identically, for every single product,
    # since nothing ever cleared it.
    parent_is_placeholder = bool(parent) and ("<" in parent or ">" in parent)
    if parent and parent != root and (parent_is_placeholder or not frappe.db.exists("Cost Center", parent)):
        frappe.db.set_value("Cost Center", root, "parent_cost_center", "")

    root_lft = frappe.db.get_value("Cost Center", root, "lft")
    if not root_lft:
        from frappe.utils.nestedset import rebuild_tree
        rebuild_tree("Cost Center")

    try:
        cc = frappe.new_doc("Cost Center")
        cc.cost_center_name = "Main"
        cc.parent_cost_center = root
        cc.company = company
        cc.is_group = 0
        cc.insert(ignore_permissions=True)
        frappe.db.set_value("Company", company, "cost_center", cc.name)
        frappe.db.commit()
        return cc.name
    except Exception:
        frappe.log_error(
            title=f"Shopify import: failed to auto-create Cost Center for {company}",
            message=frappe.get_traceback(),
        )
        return None
