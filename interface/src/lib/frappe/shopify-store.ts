/**
 * Typed client over alaiy_os_connector_shopify.api.sync.list_connections --
 * the enabled Shopify Connections a user may act on, for the store switcher.
 * Kept separate from shopify-connection.ts, which despite its name is only
 * the connection-test helper, not the Shopify Connection doctype.
 */

export interface ShopifyStore {
  name: string;
  label: string;
  shop_url: string;
}

export interface ShopifyStoreList {
  connections: ShopifyStore[];
  selected: string | null;
}

export async function fetchShopifyStores(): Promise<ShopifyStoreList> {
  const res = await fetch("/api/method/alaiy_os_connector_shopify.api.sync.list_connections", {
    method: "GET",
    cache: "no-store",
  });

  const text = await res.text();
  let payload: { message?: ShopifyStoreList; exception?: string } | null = null;
  try {
    payload = JSON.parse(text) as typeof payload;
  } catch {
    payload = null;
  }

  if (!res.ok || !payload?.message) {
    throw new Error(payload?.exception ?? "Could not load Shopify stores.");
  }
  return payload.message;
}
