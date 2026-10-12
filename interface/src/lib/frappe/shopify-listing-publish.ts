/** Publish Now -- alaiy_os_connector_shopify.shopify.product.export.publish_now.
 * A one-time push regardless of whether continuous sync (Enable Sync) is
 * on, distinct from the is_enabled toggle. */
export function publishListingNow(itemCode: string, status?: string): Promise<{ ok: boolean; published: boolean }> {
  return fetch("/api/method/alaiy_os_connector_shopify.shopify.product.export.publish_now", {
    method: "POST",
    headers: { "content-type": "application/json" },
    cache: "no-store",
    body: JSON.stringify({ item_code: itemCode, status }),
  }).then(async (res) => {
    const data = await res.json().catch(() => ({}) as Record<string, unknown>);
    if (!res.ok) throw new Error((data as { message?: string; exception?: string }).message ?? "Could not publish.");
    return (data as { message: { ok: boolean; published: boolean } }).message;
  });
}
