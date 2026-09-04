"""
One-time backfill: fetch tracking info for existing Delivery Notes created
before fulfillments/create and fulfillments/update webhooks existed.

Manual, not a patch -- makes live Shopify GraphQL calls per order, so it
must not run unattended during `bench migrate`.

Run: bench --site <site> execute alaiy_os_connector_shopify.scripts.backfill_tracking_numbers.execute
"""

import frappe

from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

from alaiy_os_connector_shopify import connections

_QUERY = """
query GetOrderTracking($id: ID!, $after: String) {
  order(id: $id) {
    fulfillments(first: 50, after: $after) {
      edges {
        node {
          id
          trackingInfo(first: 50) {
            company
            number
            url
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""


def execute():
    rows = frappe.db.sql("""
        SELECT dn.name AS dn_name, dn.sh_shopify_fulfillment_id, so.sh_shopify_order_id
        FROM `tabDelivery Note` dn
        JOIN `tabDelivery Note Item` dni ON dni.parent = dn.name
        JOIN `tabSales Order` so ON so.name = dni.against_sales_order
        WHERE dn.sh_shopify_fulfillment_id IS NOT NULL AND dn.sh_shopify_fulfillment_id != ''
          AND (dn.sh_tracking_number IS NULL OR dn.sh_tracking_number = '')
          AND so.sh_shopify_order_id IS NOT NULL AND so.sh_shopify_order_id != ''
        GROUP BY dn.name
    """, as_dict=True)

    if not rows:
        frappe.logger().info("Tracking backfill: nothing to do")
        return

    client = ShopifyGraphQLClient(connections.require_enabled())
    fixed = 0
    # Group by order id -- one GraphQL call covers every fulfillment/DN on
    # that order, not one call per Delivery Note.
    by_order = {}
    for r in rows:
        by_order.setdefault(r.sh_shopify_order_id, []).append(r)

    for order_id, dn_rows in by_order.items():
        gid = order_id if str(order_id).startswith("gid://") else f"gid://shopify/Order/{order_id}"
        try:
            fulfillments = []
            for page in client.execute_paginated(_QUERY, {"id": gid}, ["order", "fulfillments"]):
                fulfillments.extend(page)
        except Exception:
            frappe.log_error(
                title=f"Shopify: tracking backfill failed for order {order_id}",
                message=frappe.get_traceback(),
            )
            continue

        tracking_by_fid = {}
        for f in fulfillments:
            # GraphQL returns "gid://shopify/Fulfillment/123"; the webhook
            # payload (and sh_shopify_fulfillment_id) stores the plain
            # numeric id -- normalize to match.
            fid = str(f.get("id") or "").rsplit("/", 1)[-1]
            infos = f.get("trackingInfo") or []
            if fid and infos:
                # Multi-package shipments carry more than one trackingInfo
                # entry -- comma-join every number/url, same shape
                # _sync_tracking's webhook path already uses, so a fulfillment
                # backfilled here looks identical to one that arrived live.
                tracking_by_fid[fid] = {
                    "company": next((i.get("company") for i in infos if i.get("company")), ""),
                    "number": ",".join(i["number"] for i in infos if i.get("number")),
                    "url": ",".join(i["url"] for i in infos if i.get("url")),
                }

        for r in dn_rows:
            info = tracking_by_fid.get(str(r.sh_shopify_fulfillment_id))
            if not info:
                continue
            frappe.db.set_value("Delivery Note", r.dn_name, {
                "sh_tracking_number": info["number"],
                "sh_tracking_company": info["company"],
                "sh_tracking_url": info["url"],
            })
            fixed += 1

    frappe.db.commit()
    frappe.logger().info(f"Tracking backfill: {fixed} of {len(rows)} Delivery Note(s) fixed")
