/**
 * Single-field is_enabled toggle over the standard Frappe REST resource
 * endpoint. Real and load-bearing: on_listing_update (listing_hooks.py)
 * calls push_item when is_enabled turns on and archive_item when it turns
 * off -- this is a distinct per-row action from the bulk "enable by status"
 * flow already covered elsewhere, and Desk's generic form always exposed it
 * as a plain checkbox + save.
 */
export async function setListingEnabled(name: string, enabled: boolean): Promise<void> {
  const res = await fetch(`/api/resource/${encodeURIComponent("Shopify Product Listing")}/${encodeURIComponent(name)}`, {
    method: "PUT",
    headers: { "content-type": "application/json" },
    cache: "no-store",
    body: JSON.stringify({ is_enabled: enabled ? 1 : 0 }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}) as Record<string, unknown>);
    throw new Error((data as { message?: string }).message ?? "Could not update the listing.");
  }
}
