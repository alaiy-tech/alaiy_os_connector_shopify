/**
 * Manual listing creation over the standard Frappe REST resource endpoint --
 * Shopify Product Listing has no bespoke create method (confirmed by
 * grepping every @frappe.whitelist() in shopify/product/*.py), and its
 * doctype permissions already allow create (create: 1) with `item` as the
 * only required field, same as Desk's own generic "+ New" would have done.
 */
export async function createListing(item: string): Promise<{ name: string }> {
  const res = await fetch(`/api/resource/${encodeURIComponent("Shopify Product Listing")}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    cache: "no-store",
    body: JSON.stringify({ item }),
  });
  const data = await res.json().catch(() => ({}) as Record<string, unknown>);
  if (!res.ok) {
    throw new Error((data as { message?: string; exception?: string }).message ?? "Could not create the listing.");
  }
  const name = (data as { data?: { name?: string } }).data?.name;
  if (!name) throw new Error("Listing created but returned no name.");
  return { name };
}
