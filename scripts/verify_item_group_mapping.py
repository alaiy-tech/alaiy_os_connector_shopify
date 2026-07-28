"""
Read-only check: for every Item Group, does its CURRENT parent_item_group
match what Shopify's taxonomy tree says it should be? Catches groups that
were reparented once but drifted, or were never touched by
reparent_item_groups_from_shopify_taxonomy.py at all (already non-root when
that script ran, so it never looked at them).

Run:
    bench --site <site> console
    exec(open("apps/alaiy_os_connector_shopify/scripts/verify_item_group_mapping.py").read(), globals())
    r = check()
"""

import frappe


def _ancestor_chain(item_group_name):
    """Root -> leaf list of Shopify Category bare names for the node whose
    bare name exactly matches this Item Group. Returns (None, match_count)
    if zero or more than one REAL (nested) Shopify Category shares that
    bare name -- ambiguous/no match, never guess. A standalone root-level
    duplicate with no parent is filtered out first if a real nested match
    also exists -- it's noise, not ambiguity."""
    matches = frappe.get_all(
        "Shopify Category", filters={"shopify_category_name": item_group_name},
        fields=["name", "shopify_category_name", "parent_shopify_category"],
    )
    nested = [m for m in matches if m.parent_shopify_category]
    if len(nested) == 1:
        matches = nested
    if len(matches) != 1:
        return None, len(matches)
    if not matches[0].parent_shopify_category:
        # Only match is a standalone root node -- if it also has no GID it's
        # junk from a partial import (see script docstring), not a real
        # top-level taxonomy category. Report as no_match, don't accept it.
        gid = frappe.db.get_value("Shopify Category", matches[0].name, "shopify_category_id")
        if not gid:
            return None, 1

    chain = []
    node = matches[0]
    seen = set()
    while node:
        if node.name in seen:
            break
        seen.add(node.name)
        chain.append(node.shopify_category_name)
        if not node.parent_shopify_category:
            break
        node = frappe.db.get_value(
            "Shopify Category", node.parent_shopify_category,
            ["name", "shopify_category_name", "parent_shopify_category"], as_dict=True,
        )
    chain.reverse()
    return chain, 1


def check():
    groups = frappe.get_all("Item Group", fields=["name", "parent_item_group"])
    mismatched, no_match, ambiguous, ok = [], [], [], []

    for row in groups:
        if row.name == "All Item Groups":
            continue
        chain, match_count = _ancestor_chain(row.name)
        if chain is None:
            (ambiguous if match_count > 1 else no_match).append(row.name)
            continue
        expected_parent = chain[-2] if len(chain) >= 2 else "All Item Groups"
        if row.parent_item_group == expected_parent:
            ok.append(row.name)
        else:
            mismatched.append((row.name, row.parent_item_group, expected_parent))

    print(f"OK={len(ok)} MISMATCHED={len(mismatched)} NO_MATCH={len(no_match)} AMBIGUOUS={len(ambiguous)}", flush=True)
    if mismatched:
        print("\nMISMATCHED (name, current_parent, expected_parent):", flush=True)
        for m in mismatched:
            print(" ", m, flush=True)
    if no_match:
        print("\nNO_MATCH:", no_match, flush=True)
    if ambiguous:
        print("\nAMBIGUOUS:", ambiguous, flush=True)

    return {"ok": ok, "mismatched": mismatched, "no_match": no_match, "ambiguous": ambiguous}
