/** Bulk approve for the enrichment queue -- alaiy_os_connector_shopify.listing.review.approve_listings. */

export interface BulkApproveResult {
  approved: number;
  skipped: number;
  failed: number;
  errors: Record<string, string>;
}

export function approveListings(names: string[], connection?: string): Promise<BulkApproveResult> {
  return fetch("/api/method/alaiy_os_connector_shopify.listing.review.approve_listings", {
    method: "POST",
    headers: { "content-type": "application/json" },
    cache: "no-store",
    body: JSON.stringify({ names, connection }),
  })
    .then(async (res) => {
      const data = await res.json().catch(() => ({}) as Record<string, unknown>);
      if (!res.ok) throw new Error((data as { message?: string; exception?: string }).message ?? "Could not approve.");
      return (data as { message: BulkApproveResult }).message;
    });
}
