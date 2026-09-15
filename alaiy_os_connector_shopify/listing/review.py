# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""Approving an enrichment somebody has read.

The listing agent writes a `Shopify Enriched Listing` in *Needs Review* and stops
there. Approval is the deliberate human act that moves its content onto the real
`Shopify Product Listing`, and it is deliberately not something the agent can do:
nothing in `channel.py`'s handlers reaches this module.

The per-document path is the doctype's own `on_update` -- a reviewer sets the
status on the form and saves. This is the list view's bulk version of the same
act, and it works by doing exactly that save per row rather than by writing the
fields itself. Bypassing the hook would let a bulk approval publish content a
single approval would have transformed, which is the kind of divergence nobody
finds until a listing is wrong on the storefront.

One bad listing does not stop the rest. Each row commits on its own and a failure
is rolled back, logged and reported against its name, because the alternative --
one exception abandoning a fifty-row approval halfway with no record of where it
got to -- is worse than a partial success that says so.

Lives in `listing/` beside the tools rather than in `api/`, mirroring the Amazon
connector's `listing/review.py`. Approval belongs to the review record, and the
review record belongs to the channel.
"""

import json

import frappe

ENRICHED_DOCTYPE = "Shopify Enriched Listing"


@frappe.whitelist()
def approve_listings(names):
    """Approve many enriched listings at once -- the list view's "Approve" action.

    Each listing is approved through a normal document save, so the same
    `on_update` hook that fires for a one-at-a-time approval pushes each one to
    its Shopify Product Listing. Returns {approved, skipped, failed, errors}:
    already-approved rows are counted as skipped.
    """
    if isinstance(names, str):
        names = json.loads(names)
    if not names:
        frappe.throw("approve_listings needs at least one listing name.")

    approved, skipped, errors = 0, 0, {}
    for name in names:
        doc = frappe.get_doc(ENRICHED_DOCTYPE, name)
        doc.check_permission("write")
        if doc.status == "Approved":
            skipped += 1
            continue
        try:
            doc.status = "Approved"
            doc.save()
            frappe.db.commit()
            approved += 1
        except Exception:
            frappe.db.rollback()
            errors[name] = str(frappe.get_traceback().splitlines()[-1])
            frappe.log_error(
                title=f"Bulk approve failed: {name}",
                message=frappe.get_traceback(),
            )

    return {
        "approved": approved,
        "skipped": skipped,
        "failed": len(errors),
        "errors": errors,
    }
