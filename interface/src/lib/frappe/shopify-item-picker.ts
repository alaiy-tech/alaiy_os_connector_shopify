/**
 * The connector's own Item picker for "create a Listing" -- unlike the
 * platform's generic searchLinkOptions (plain name search on any doctype),
 * this calls item_without_listing_query directly: template/simple Items
 * only (never a variant), not already listed, and scoped to the current
 * user's store so a multi-store bench never offers another seller's Items.
 * See alaiy_os_connector_shopify/shopify/product/listing.py for the
 * server-side scoping this depends on.
 */
export async function searchItemsWithoutListing(term: string): Promise<string[]> {
  const params = new URLSearchParams();
  params.set("doctype", "Item");
  params.set("txt", term);
  params.set("searchfield", "name");
  params.set("start", "0");
  params.set("page_len", "20");
  params.set("filters", "{}");

  const res = await fetch(
    `/api/method/alaiy_os_connector_shopify.shopify.product.listing.item_without_listing_query?${params.toString()}`,
    { cache: "no-store" },
  );
  const data = await res.json().catch(() => ({}) as Record<string, unknown>);
  if (!res.ok) throw new Error("Could not search items.");
  const rows = (data as { message?: Array<[string, string]> }).message ?? [];
  return rows.map((row) => row[0]);
}
