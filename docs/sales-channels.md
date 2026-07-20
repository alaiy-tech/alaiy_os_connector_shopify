# Sales Channels (Publications)

Shopify **Publications** are the sales channels a resource can be published to (Online Store, POS, headless storefronts, etc.). Shopify has no "sales channel" object as such — a channel is a Publication, and a product/collection is either published to it or not. This connector surfaces and controls **collection** publication state. Code: `shopify/product/collections.py`, form in `shopify_collection.js`.

---

## Display

On the `Shopify Collection` form, `get_collection_channels(collection_name)` lists **every** publication as a chip, marking each published (●) or not (○):
- Fetches all publications (`_PUBLICATIONS_QUERY`) as the master list.
- Fetches the collection's published set (`_COLLECTION_CHANNELS_QUERY`, `resourcePublications` where `onlyPublished`).
- Merges: a publication the collection isn't on still shows (as a not-published chip), so it never disappears and can be re-published.

The chip count can exceed Shopify's admin "channels" popup because the API returns app/headless publications that the popup groups out — both are real publications.

---

## Control — publish / unpublish

Chips are clickable. Clicking calls `toggle_collection_channel(collection_name, publication_id, publish)`:
- `publish` truthy → `publishablePublish`; falsy → `publishableUnpublish`, with `input: [{ publicationId }]` for the collection's GID.
- On success a toast confirms and the chip list refreshes to the new state; user errors are logged and surfaced.

This gives Alaiy OS-side control over where a collection appears, closing the sales-channel item of the product-operations scope.

> **Scope:** publication control is implemented for **collections**. Product-level per-channel publishing is not wired.
