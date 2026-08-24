/**
 * One-off call to alaiy_os_connector_shopify.api.test_connection.test_connection,
 * kept out of shopify-sync.ts on purpose (see that file's header) — mirrors
 * its callMethod error handling exactly.
 */

export interface ShopifyConnectionResult {
  success: boolean;
  message: string;
}

export async function testShopifyConnection(): Promise<ShopifyConnectionResult> {
  const res = await fetch("/api/method/alaiy_os_connector_shopify.api.test_connection.test_connection", {
    method: "GET",
    cache: "no-store",
  });

  const text = await res.text();
  let payload: { message?: ShopifyConnectionResult; _server_messages?: string; exception?: string } | null = null;
  try {
    payload = JSON.parse(text) as typeof payload;
  } catch {
    payload = null;
  }

  if (!res.ok || !payload?.message) {
    return { success: false, message: payload?.exception ?? "Could not reach the connection test." };
  }
  return payload.message;
}
