"""
Apply step for resolve_uncategorized.py's proposal CSV: repoint
Item.sh_shopify_category (and Shopify Product Listing.listing_category,
where set as an override) from a raw/loose label ("Dog Supplies") to the
REAL existing Shopify Category record it matched (e.g. "Animals & Pet
Supplies / Pet Supplies / Dog Supplies") -- that record already carries a
resolved shopify_category_id (it's how the proposal step found it), so no
new taxonomy node is created, just repointing the Link value to the
correct existing one.

Then pushes every affected, enabled template directly via push_item --
canonical.py resolves category fresh at push time regardless of the
fingerprint cache, so this doesn't need any fingerprint/entity clearing to
take effect.

Skips any row whose loose_category is in SKIP_CATEGORIES (bad/uncertain
match, needs a human to pick manually) or whose confidence is NO_MATCH.

Run (after reviewing the CSV from resolve_uncategorized.py):
    bench --site <site> console
    exec(open("/home/ubuntu/alaiy_os_bench/apps/alaiy_os_connector_shopify/scripts/apply_category_fixes.py").read(), globals())
    apply_category_fixes(dry_run=True)   # review counts first
    apply_category_fixes(dry_run=False)  # then apply + push
"""
import csv

import frappe

SKIP_CATEGORIES = {
    "Bubble Envelope",       # BEST_GUESS matched "Bubble Levels" -- wrong, packaging vs tool
    "Bathroom storage rack",  # BEST_GUESS matched "Bathroom Suites" -- questionable, rack vs full fixture set
}


def apply_category_fixes(dry_run=True, csv_path=None):
    site_path = frappe.get_site_path("private", "files")
    csv_path = csv_path or f"{site_path}/uncategorized_mapping_proposal.csv"

    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))

    approved = [
        r for r in rows
        if r["loose_category"] not in SKIP_CATEGORIES and r["confidence"] != "NO_MATCH"
        and r["suggested_category_path"]
    ]
    skipped = [r for r in rows if r not in approved]
    print(f"[apply_category_fixes] {len(approved)} approved, {len(skipped)} skipped "
          f"({', '.join(r['loose_category'] for r in skipped)})")

    affected_templates = set()
    for row in approved:
        loose = row["loose_category"]
        target = row["suggested_category_path"]

        item_codes = frappe.get_all("Item", filters={"sh_shopify_category": loose}, pluck="name")
        print(f"  {loose} -> {target} ({len(item_codes)} items)")
        if not dry_run:
            frappe.db.set_value("Item", {"sh_shopify_category": loose}, "sh_shopify_category", target)
            frappe.db.set_value(
                "Shopify Product Listing", {"listing_category": loose}, "listing_category", target)

        for code in item_codes:
            variant_of = frappe.db.get_value("Item", code, "variant_of")
            affected_templates.add(variant_of or code)

    print(f"[apply_category_fixes] {len(affected_templates)} distinct templates affected")
    if dry_run:
        print("[apply_category_fixes] DRY RUN -- nothing written, nothing pushed. "
              "Re-run with dry_run=False to apply and push.")
        return

    frappe.db.commit()

    pushed = failed = 0
    from alaiy_os_connector_shopify.shopify.product.export import push_item
    for code in affected_templates:
        try:
            push_item(code)
            pushed += 1
        except Exception as exc:
            failed += 1
            print(f"  FAILED push {code}: {exc}")
        if (pushed + failed) % 20 == 0:
            print(f"  progress: {pushed + failed}/{len(affected_templates)}")

    frappe.db.commit()
    print(f"[apply_category_fixes] done: pushed={pushed} failed={failed}")
