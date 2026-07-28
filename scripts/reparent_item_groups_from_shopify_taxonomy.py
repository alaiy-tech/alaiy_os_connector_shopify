"""
One-time fix: reparent Item Groups that got imported flat (each landed
directly under "All Item Groups") back under their real Shopify Standard
Taxonomy ancestors -- using the already-fetched Shopify Category tree as
the source of truth, not the original import CSV.

Prerequisite: Shopify Category tree must be populated first --
    bench execute alaiy_os_connector_shopify.shopify.product.taxonomy.fetch_shopify_taxonomy

Matches each flat Item Group to a Shopify Category node by an EXACT name
match only -- never guesses/fuzzy-matches, since a wrong parent silently
misfiles every product under it.

Confirmed live: a bare name can match BOTH a real nested taxonomy node
(has a parent_shopify_category) AND a standalone root-level duplicate
with no parent (an artifact of ensure_shopify_category having been called
with just a leaf name somewhere, before the full path was known). When
that's the only kind of duplicate, prefer the nested one -- it's not a
real ambiguity, just noise from an earlier partial write. Only genuinely
ambiguous (2+ REAL nested matches, e.g. the same leaf name under two
different Shopify root categories) or truly unmatched names are reported,
not auto-fixed.

Reparents the EXISTING Item Group doc in place (only its parent_item_group
changes) -- Items already pointing at it by name are unaffected, nothing
is recreated or renamed.

Run:
    bench --site <site> console
    exec(open("apps/alaiy_os_connector_shopify/scripts/reparent_item_groups_from_shopify_taxonomy.py").read(), globals())
    run(apply=False)   # dry run first -- review the printed mapping
    run(apply=True)    # then actually reparent
"""

import frappe


def _ancestor_chain(item_group_name):
    """Root -> leaf list of Shopify Category bare names for the node whose
    bare name exactly matches this Item Group. Returns (None, match_count)
    if zero or more than one REAL (nested) Shopify Category shares that
    bare name -- ambiguous/no match, never guess. A standalone root-level
    duplicate with no parent is filtered out first if a real nested match
    also exists (see module docstring) -- it's noise, not ambiguity."""
    matches = frappe.get_all(
        "Shopify Category", filters={"shopify_category_name": item_group_name},
        fields=["name", "shopify_category_name", "parent_shopify_category"],
    )
    nested = [m for m in matches if m.parent_shopify_category]
    if len(nested) == 1:
        matches = nested
    if len(matches) != 1:
        return None, len(matches)

    chain = []
    node = matches[0]
    seen = set()
    while node:
        if node.name in seen:
            break  # guard against any bad cyclical data
        seen.add(node.name)
        chain.append(node.shopify_category_name)
        if not node.parent_shopify_category:
            break
        node = frappe.db.get_value(
            "Shopify Category", node.parent_shopify_category,
            ["name", "shopify_category_name", "parent_shopify_category"], as_dict=True,
        )
    chain.reverse()  # root first, leaf last
    return chain, 1


def _ensure_item_group(name, parent_name):
    if frappe.db.exists("Item Group", name):
        # Already exists -- an ancestor level that also happens to already be
        # a real Item Group. Leave its parent alone here; only the final
        # leaf reparent below is this script's actual fix.
        return name
    frappe.get_doc({
        "doctype": "Item Group", "item_group_name": name,
        "parent_item_group": parent_name, "is_group": 1,
    }).insert(ignore_permissions=True)
    return name


def run(apply=False):
    """apply=False (default): dry run, only prints what would change.
    apply=True: actually creates missing ancestor Item Groups and reparents
    the flat leaf groups under them."""
    root_groups = frappe.get_all(
        "Item Group", filters={"parent_item_group": "All Item Groups"}, fields=["name"],
    )
    print(f"TOTAL {len(root_groups)} root-level Item Groups to check", flush=True)

    fixed, no_match, ambiguous, already_correct = [], [], [], []

    for i, row in enumerate(root_groups, 1):
        print(f"[{i}/{len(root_groups)}] checking {row.name!r} ...", flush=True)
        chain, match_count = _ancestor_chain(row.name)
        if chain is None:
            bucket = "AMBIGUOUS" if match_count > 1 else "NO MATCH"
            print(f"  -> {bucket}", flush=True)
            (ambiguous if match_count > 1 else no_match).append(row.name)
            continue
        if len(chain) <= 1:
            # This name IS a real Shopify top-level category -- correctly root-level.
            print("  -> already correct (real top-level category)", flush=True)
            already_correct.append(row.name)
            continue

        ancestors = chain[:-1]  # exclude the leaf itself (that's row.name)
        print(f"  -> {row.name}  <-  {' > '.join(ancestors)}", flush=True)
        if apply:
            parent = "All Item Groups"
            for name in ancestors:
                parent = _ensure_item_group(name, parent)
            frappe.db.set_value("Item Group", row.name, "parent_item_group", parent)
            print(f"  -> reparented under {parent!r}", flush=True)
        fixed.append(row.name)

    if apply:
        from frappe.utils.nestedset import rebuild_tree
        rebuild_tree("Item Group")
        frappe.db.commit()

    print(
        f"\nDONE. fixed={len(fixed)} already_correct={len(already_correct)} "
        f"no_match={len(no_match)} ambiguous={len(ambiguous)}", flush=True,
    )
    if no_match:
        print("NO MATCH (name not found anywhere in Shopify's taxonomy):", no_match, flush=True)
    if ambiguous:
        print("AMBIGUOUS (name matches multiple Shopify taxonomy nodes, pick manually):", ambiguous, flush=True)

    return {"fixed": fixed, "no_match": no_match, "ambiguous": ambiguous, "already_correct": already_correct}
