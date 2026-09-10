/**
 * Typed client over the collections.py whitelisted methods — product
 * drill-down and per-channel publish toggling for one Shopify Collection.
 * Kept separate from shopify-sync.ts (that file is for the sync
 * dashboard/triggers; this is bespoke to the collection detail dialog).
 */

export interface CollectionProduct {
  title: string | null;
  image: string | null;
  price: string | null;
  sku: string | null;
  item_code: string | null;
}

export interface CollectionChannel {
  name: string | null;
  publication_id: string | null;
  published: boolean;
}

async function callMethod<T>(method: string, body?: Record<string, unknown>): Promise<T> {
  const res = await fetch(`/api/method/${method}`, {
    method: body ? "POST" : "GET",
    headers: body ? { "content-type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    cache: "no-store",
  });

  const text = await res.text();
  let payload: { message?: T; _server_messages?: string; exception?: string } | null = null;
  try {
    payload = JSON.parse(text) as typeof payload;
  } catch {
    payload = null;
  }

  if (!res.ok) throw new Error(serverMessage(payload) ?? `${method} failed (${res.status}).`);
  if (!payload || payload.message === undefined) throw new Error(`${method} returned nothing.`);
  return payload.message;
}

function serverMessage(payload: { _server_messages?: string; exception?: string } | null): string | null {
  if (!payload) return null;
  try {
    const messages = JSON.parse(payload._server_messages ?? "[]") as string[];
    const first = messages.map((entry) => JSON.parse(entry) as { message?: string }).find((entry) => entry.message);
    if (first?.message) return first.message.replace(/<[^>]+>/g, "");
  } catch {
    // fall through to the raw exception line
  }
  return payload.exception ?? null;
}

export function fetchCollectionProducts(collectionName: string): Promise<CollectionProduct[]> {
  return callMethod<CollectionProduct[]>(
    "alaiy_os_connector_shopify.shopify.product.collections.get_collection_products",
    { collection_name: collectionName },
  );
}

export function fetchCollectionChannels(collectionName: string): Promise<CollectionChannel[]> {
  return callMethod<CollectionChannel[]>(
    "alaiy_os_connector_shopify.shopify.product.collections.get_collection_channels",
    { collection_name: collectionName },
  );
}

export function toggleCollectionChannel(
  collectionName: string,
  publicationId: string,
  publish: boolean,
): Promise<{ ok: boolean; error?: string }> {
  return callMethod<{ ok: boolean; error?: string }>(
    "alaiy_os_connector_shopify.shopify.product.collections.toggle_collection_channel",
    { collection_name: collectionName, publication_id: publicationId, publish: publish ? 1 : 0 },
  );
}
