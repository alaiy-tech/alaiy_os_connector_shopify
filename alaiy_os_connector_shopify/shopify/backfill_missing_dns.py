"""
Fixes the 134 orders confirmed by audit_fulfillment_dn_mismatch.py /
scope_dn_split_fix.py: Shopify reports more real fulfillments than we
have local Delivery Notes, because these orders were pulled before
yesterday's fix (fddf9b6, added fulfillmentLineItems to the GraphQL
pull query) -- each one collapsed 2+ real Shopify shipments into a
single local Delivery Note.

Confirmed safe by scope_dn_split_fix.py: all 134 already have a
submitted Sales Invoice (3 already paid too). NEVER cancels or edits
the existing Delivery Note or the Sales Invoice -- the Sales Invoice is
non-stock (update_stock=0, see order/invoice.py's own docstring) and
keyed to the Sales Order, not to any specific Delivery Note, so it has
no dependency on how many DNs exist. This only ever ADDS a brand-new
Delivery Note for whichever real Shopify fulfillment(s) have no local
DN yet -- same _create_delivery_note_for_fulfillment logic already
used for new orders since yesterday's fix, just run retroactively here.

Never writes back to Shopify (read-only against the Shopify API,
write-only to local Alaiy OS documents).

Per-order safety check before creating anything: compares the existing
Delivery Note's own line items against the missing fulfillment's real
line items. If the existing DN already fully covers a SKU the missing
fulfillment also claims to ship, that order is SKIPPED and reported
separately -- creating a second DN there would double-count stock. Only
orders where the missing fulfillment's items are NOT already on an
existing local DN get a new DN created.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.backfill_missing_dns.run

Dry run by default -- reports exactly what would be created for every
order, creates nothing. Apply for real:

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.backfill_missing_dns.run \
      --kwargs "{'dry_run': False}"
"""

import frappe


def _real_fulfillments(client, shopify_order_id):
    from alaiy_os_connector_shopify.shopify.order.utils import _to_gid

    data = client.execute("""
    query($id: ID!) {
      order(id: $id) {
        fulfillments(first: 10) {
          legacyResourceId
          displayStatus
          trackingInfo { number company url }
          fulfillmentLineItems(first: 50) {
            nodes {
              quantity
              lineItem { sku title variant { legacyResourceId } }
            }
          }
        }
      }
    }
    """, {"id": _to_gid(shopify_order_id)})
    return ((data or {}).get("order") or {}).get("fulfillments") or []


def run(dry_run=True, order_names=None):
    """order_names (optional list of Sales Order names) skips the full
    1,553-order rescan entirely -- pass the exact orders a prior dry run
    already identified (e.g. the 10 confirmed-safe ones) instead of
    re-checking everything against Shopify again just to land on the
    same result."""
    if isinstance(dry_run, str):
        dry_run = dry_run.lower() not in ("false", "0", "")
    if isinstance(order_names, str):
        import json as _json
        order_names = _json.loads(order_names)

    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
    from alaiy_os_connector_shopify.shopify.order.delivery_notes import _create_delivery_note_for_fulfillment
    from alaiy_os_connector_shopify.shopify.order.utils import _resolve_item_code

    filters = {"docstatus": 1, "sh_shopify_order_id": ["!=", ""]}
    if order_names:
        filters["name"] = ["in", order_names]
    sos = frappe.get_all(
        "Sales Order", filters=filters, fields=["name", "sh_shopify_order_id"], order_by="creation",
    )

    print(f"{'DRY RUN: ' if dry_run else ''}Checking {len(sos)} order(s)...", flush=True)

    client = ShopifyGraphQLClient()

    created, skipped_matched, skipped_conflict, skipped_no_fulfillment_id, errors = [], 0, [], 0, []

    for i, so in enumerate(sos, 1):
        if i % 100 == 0 or i == len(sos):
            print(f"  ...{i}/{len(sos)} checked", flush=True)

        existing_dn_names = frappe.get_all(
            "Delivery Note Item", filters={"against_sales_order": so.name},
            pluck="parent", distinct=True,
        )
        existing_fulfillment_ids = set(frappe.get_all(
            "Delivery Note", filters={"name": ["in", existing_dn_names]}, pluck="sh_shopify_fulfillment_id",
        )) if existing_dn_names else set()

        try:
            fulfillments = _real_fulfillments(client, so.sh_shopify_order_id)
        except Exception as e:
            errors.append((so.name, str(e)))
            continue

        if len(fulfillments) <= len(existing_dn_names):
            continue  # not one of the 134 -- already matched

        # Items already covered by an existing DN for this order (per SKU).
        covered_items = set()
        if existing_dn_names:
            covered_items = set(frappe.get_all(
                "Delivery Note Item", filters={"parent": ["in", existing_dn_names]}, pluck="item_code",
            ))

        for f in fulfillments:
            fulfillment_id = str(f.get("legacyResourceId") or "")
            if not fulfillment_id:
                skipped_no_fulfillment_id += 1
                continue
            if fulfillment_id in existing_fulfillment_ids:
                continue  # this exact fulfillment already has its own DN
            if frappe.db.exists("Delivery Note", {"sh_shopify_fulfillment_id": fulfillment_id}):
                continue  # tagged under a different order somehow -- leave alone

            line_items = []
            conflict_skus = []
            for node in ((f.get("fulfillmentLineItems") or {}).get("nodes") or []):
                li = node.get("lineItem") or {}
                variant = li.get("variant") or {}
                sku = li.get("sku")
                item_code = _resolve_item_code({"sku": sku, "variant_id": variant.get("legacyResourceId"), "title": li.get("title")})
                if item_code and item_code in covered_items:
                    conflict_skus.append(item_code)
                line_items.append({
                    "sku": sku, "title": li.get("title"),
                    "quantity": node.get("quantity"),
                    "variant_id": variant.get("legacyResourceId"),
                })

            if conflict_skus:
                skipped_conflict.append({"so": so.name, "fulfillment_id": fulfillment_id, "conflict_skus": conflict_skus})
                continue

            tracking = (f.get("trackingInfo") or [{}])[0]
            if dry_run:
                created.append({
                    "so": so.name, "fulfillment_id": fulfillment_id,
                    "items": [(li["sku"], li["quantity"]) for li in line_items],
                    "status": f.get("displayStatus"), "tracking": tracking.get("number"),
                })
                continue

            try:
                so_doc = frappe.get_doc("Sales Order", so.name)
                _create_delivery_note_for_fulfillment(so_doc, fulfillment_id, line_items, None)
                dn_name = frappe.db.get_value("Delivery Note", {"sh_shopify_fulfillment_id": fulfillment_id}, "name")
                if dn_name:
                    status = (f.get("displayStatus") or "").strip()
                    values = {}
                    if status:
                        values["sh_delivery_status"] = status.upper()
                    if tracking.get("number"):
                        values.update({
                            "sh_tracking_number": tracking.get("number"),
                            "sh_tracking_company": tracking.get("company") or "",
                            "sh_tracking_url": tracking.get("url") or "",
                        })
                    if values:
                        frappe.db.set_value("Delivery Note", dn_name, values, update_modified=False)
                        frappe.db.commit()
                    created.append({"so": so.name, "fulfillment_id": fulfillment_id, "dn": dn_name})
                else:
                    skipped_conflict.append({"so": so.name, "fulfillment_id": fulfillment_id, "reason": "DN creation silently produced nothing (no mappable items)"})
            except Exception as e:
                errors.append((so.name, str(e)))
                frappe.db.rollback()

    print(f"\n=== {'DRY RUN' if dry_run else 'APPLIED'} ===")
    print(f"{'Would create' if dry_run else 'Created'}: {len(created)} Delivery Note(s)")
    for row in created[:30]:
        print(f"  {row}")
    if len(created) > 30:
        print(f"  ... and {len(created) - 30} more")

    print(f"\nSkipped -- item already on an existing local DN (would double-count stock): {len(skipped_conflict)}")
    for row in skipped_conflict[:20]:
        print(f"  {row}")

    print(f"\nSkipped -- fulfillment had no id at all: {skipped_no_fulfillment_id}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for name, err in errors[:15]:
            print(f"  {name}: {err}")

    if dry_run:
        print("\nDry run only -- nothing created. Re-run with dry_run=false to apply.")

    return {
        "created": len(created), "conflict_skipped": len(skipped_conflict),
        "no_fulfillment_id": skipped_no_fulfillment_id, "errors": len(errors),
    }
