/** Connect to Shopify OAuth -- alaiy_os_connector_shopify.api.oauth. */

async function callMethod<T>(method: string, params?: Record<string, string>): Promise<T> {
  const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
  const res = await fetch(`/api/method/${method}${qs}`, { cache: "no-store" });
  const data = await res.json().catch(() => ({}) as Record<string, unknown>);
  if (!res.ok) throw new Error((data as { message?: string; exception?: string }).message ?? `${method} failed.`);
  const message = (data as { message?: T }).message;
  if (message === undefined) throw new Error(`${method} returned nothing.`);
  return message;
}

export function isOAuthConfigured(): Promise<{ configured: boolean }> {
  return callMethod("alaiy_os_connector_shopify.api.oauth.is_configured");
}

/** Redirects the browser to Shopify's own authorize page. Never resolves on success. */
export async function startShopifyInstall(shop: string, connectionId?: string, label?: string): Promise<void> {
  const params: Record<string, string> = { shop };
  if (connectionId) params.connection_id = connectionId;
  if (label) params.label = label;
  const { redirect_url } = await callMethod<{ redirect_url: string }>(
    "alaiy_os_connector_shopify.api.oauth.start_install",
    params,
  );
  window.location.href = redirect_url;
}
