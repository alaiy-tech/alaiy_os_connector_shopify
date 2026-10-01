"""
A product's photos as Shopify holds them now, read from the Admin API rather
than from the webhook that announced a change.

A products/update payload is a snapshot taken when the event fired, and
Shopify documents neither the order deliveries arrive in nor that one is sent
when a photo finishes processing. Photos sent by URL are fetched and processed
asynchronously (MediaStatus UPLOADED -> PROCESSING -> READY), so a payload built
in that window lists only the photos that were already ready. Applying it as
the product's photo set drops every photo still being processed -- a listing
pushed with five photos was cut to the one Shopify happened to finish first,
and the later delivery that listed all five arrived out of the window the
staleness check allowed.

So inbound photo sync asks Shopify directly, and only acts on an answer in
which every photo has finished. While any is still processing, nothing is
changed and a re-check is queued on the retry queue, whose backoff keeps
asking until the photos settle and alerts an admin if they never do.
"""

import frappe

from alaiy_os_connector_shopify import connections
from alaiy_os_connector_shopify.shopify.product.media import product_image_urls

#: Statuses of a photo Shopify has accepted but not finished processing. A
#: photo list read while any photo is in one of these is a partial list.
NOT_YET_READY = {"UPLOADED", "PROCESSING"}

#: A failed photo will never become ready, so it must not hold the rest back.
FAILED = "FAILED"

#: Shopify's own cap on media per product.
_MEDIA_LIMIT = 250

_PRODUCT_MEDIA_QUERY = """
query ProductMedia($id: ID!) {
  product(id: $id) {
    featuredMedia {
      preview {
        image {
          url
        }
      }
    }
    media(first: %d) {
      nodes {
        mediaContentType
        status
        preview {
          image {
            url
          }
        }
      }
    }
  }
}
""" % _MEDIA_LIMIT

#: (direction, entity_type) of the retry-queue entry that re-checks photos.
RECHECK_KEY = ("inbound", "product")


class PhotosStillProcessing(Exception):
    """Raised by a re-check that found photos still processing, so the retry
    queue backs off and asks again rather than marking the work done."""


def fetch_product_images(product_id, connection=None):
    """Return (urls, settled) for a Shopify product, or None if it is gone.

    `urls` is every ready photo, featured first, in the same form the importer
    stores. `settled` is False while any photo is still processing: the list
    is then incomplete and must not replace anything.
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient

    settings = connections.resolve(connection) if connection else connections.require_enabled()
    data = ShopifyGraphQLClient(settings).execute(
        _PRODUCT_MEDIA_QUERY, {"id": f"gid://shopify/Product/{product_id}"}
    )
    node = (data or {}).get("product")
    if not node:
        return None

    settled = media_settled(node)
    failed = sum(1 for m in _photos(node) if m.get("status") == FAILED)
    if failed:
        # Left out of the list by product_image_urls (a failed photo has no
        # image url), which is right: it is not a photo the product has. Said
        # out loud so a photo that never appears is explainable.
        frappe.logger().warning(
            f"Shopify product {product_id}: {failed} photo(s) failed processing on Shopify "
            "and were left out of the inbound photo sync."
        )
    return product_image_urls(node), settled


def _photos(node):
    return [
        m for m in ((node.get("media") or {}).get("nodes") or [])
        if m.get("mediaContentType") == "IMAGE"
    ]


def media_settled(node) -> bool:
    """Whether no photo on a product node is still being processed.

    A node read without media status (an older query shape, or a webhook
    payload reshaped into a node) has nothing to say otherwise and reads as
    settled, which is the behaviour it had before status was read at all.
    """
    return not any(m.get("status") in NOT_YET_READY for m in _photos(node))


def schedule_recheck(product_id, synced_entity, connection=None):
    """Queue a photo re-check for this product, once.

    Keyed on the synced entity, so a burst of webhooks for one product queues
    one re-check rather than one each.
    """
    from alaiy_os_connector_shopify.shopify.sync_engine import retry_queue

    direction, entity_type = RECHECK_KEY
    if frappe.db.exists("Shopify Retry Queue Entry", {
        "direction": direction,
        "entity_type": entity_type,
        "synced_entity": synced_entity,
        "status": ["in", ["pending", "in_progress"]],
    }):
        return None
    return retry_queue.enqueue(
        direction, entity_type,
        {"product_id": str(product_id), "connection": getattr(connection, "name", connection)},
        synced_entity=synced_entity,
    )
