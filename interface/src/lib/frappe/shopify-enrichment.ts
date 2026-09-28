/**
 * Shopify Enriched Listing -- the AI photo/content enrichment review queue
 * and per-photo retouch/lifestyle/worn workspace. Reads/writes the doctype
 * through the standard REST resource endpoint (approval is just saving
 * status="Approved", which fires on_update -> _push_to_listing server-side);
 * the bespoke calls below are the ones with no doctype-CRUD equivalent --
 * listing/api.py's per-photo pipeline and listing/queue.py's cross-doctype
 * queue list.
 */

export interface EnrichedListingQueueRow {
  name: string;
  item_code: string;
  status: "Draft" | "Needs Review" | "Approved";
  title: string | null;
  confidence: "high" | "medium" | "low" | null;
  image_status: string;
  needs_review: string | null;
  modified: string;
  connection: string | null;
}

export interface EnrichedListingAttribute {
  name: string | null;
  key: string;
  value: string | null;
  source: string | null;
  source_url: string | null;
}

export interface EnrichedListingVariant {
  name: string | null;
  item_variant: string;
  observed: string | null;
  suggestions: string | null;
  notes: string | null;
}

export interface EnrichedListingImageRow {
  name: string | null;
  kind: string;
  item_variant: string | null;
  source_url: string | null;
  url: string | null;
  cutout_url: string | null;
  brief: string | null;
  note: string | null;
}

export interface EnrichedListingDetail {
  name: string;
  item_code: string;
  status: "Draft" | "Needs Review" | "Approved";
  title: string | null;
  description: string | null;
  category: string | null;
  product_type: string | null;
  confidence: "high" | "medium" | "low" | null;
  seo_title: string | null;
  seo_description: string | null;
  shopify_tags: string | null;
  attributes: EnrichedListingAttribute[];
  variants: EnrichedListingVariant[];
  images: EnrichedListingImageRow[];
  image_status: string;
  image_error: string | null;
  needs_review: string | null;
  notes: string | null;
}

export interface ListingImagesPoll {
  item_code: string;
  image_status: string | null;
  image_error: string | null;
  image_tokens: number;
  images: Array<{
    source_url: string | null;
    item_variant: string | null;
    url: string | null;
    cutout_url: string | null;
    note: string | null;
    brief: string | null;
    kind: string;
    pending: boolean;
  }>;
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
    // fall through
  }
  return payload.exception ?? null;
}

const RESOURCE = `/api/resource/${encodeURIComponent("Shopify Enriched Listing")}`;

async function resourceFetch(name: string, init: RequestInit): Promise<Record<string, unknown>> {
  const res = await fetch(`${RESOURCE}/${encodeURIComponent(name)}`, { cache: "no-store", ...init });
  const data = await res.json().catch(() => ({}) as Record<string, unknown>);
  if (!res.ok) throw new Error((data as { message?: string }).message ?? `Request failed (${res.status}).`);
  return data;
}

export function fetchEnrichmentQueue(connection?: string, status?: string): Promise<EnrichedListingQueueRow[]> {
  const params = new URLSearchParams();
  if (connection) params.set("connection", connection);
  if (status) params.set("status", status);
  const qs = params.toString();
  return callMethod<EnrichedListingQueueRow[]>(
    `alaiy_os_connector_shopify.listing.queue.list_enriched_listings${qs ? `?${qs}` : ""}`,
  );
}

export async function fetchEnrichedListing(itemCode: string): Promise<EnrichedListingDetail | null> {
  try {
    const data = await resourceFetch(itemCode, { method: "GET" });
    return (data as { data: EnrichedListingDetail }).data;
  } catch {
    return null;
  }
}

export async function saveEnrichedListing(itemCode: string, patch: Record<string, unknown>): Promise<EnrichedListingDetail> {
  const data = await resourceFetch(itemCode, {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(patch),
  });
  return (data as { data: EnrichedListingDetail }).data;
}

export function ensureEnrichedListing(itemCode: string): Promise<string> {
  return callMethod("alaiy_os_connector_shopify.listing.api.ensure_enriched_listing", { item_code: itemCode });
}

export function fetchListingImages(itemCode: string): Promise<ListingImagesPoll> {
  return callMethod(
    `alaiy_os_connector_shopify.listing.api.get_listing_images?item_code=${encodeURIComponent(itemCode)}`,
  );
}

export function enrichListingImage(itemCode: string, sourceUrl: string, force?: boolean): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.listing.api.enrich_listing_image", {
    item_code: itemCode,
    source_url: sourceUrl,
    force: force ? 1 : 0,
  });
}

export function revertListingImage(itemCode: string, sourceUrl: string): Promise<{ reverted: number }> {
  return callMethod("alaiy_os_connector_shopify.listing.api.revert_listing_image", {
    item_code: itemCode,
    source_url: sourceUrl,
  });
}

export function publishListingImages(itemCode: string): Promise<{ published: number; images: string[] }> {
  return callMethod("alaiy_os_connector_shopify.listing.api.publish_listing_images", { item_code: itemCode });
}

export function previewLifestyleImage(itemCode: string, sourceUrl: string, query: string): Promise<{ url: string }> {
  return callMethod("alaiy_os_connector_shopify.listing.api.preview_lifestyle_image", {
    item_code: itemCode,
    source_url: sourceUrl,
    query,
  });
}

export function previewWornImage(itemCode: string, sourceUrl: string, prompt?: string): Promise<{ url: string }> {
  return callMethod("alaiy_os_connector_shopify.listing.api.preview_worn_image", {
    item_code: itemCode,
    source_url: sourceUrl,
    prompt,
  });
}

export function previewRegenerateAdditionalImage(itemCode: string, sourceUrl: string, url: string): Promise<{ url: string; query: string | null }> {
  return callMethod("alaiy_os_connector_shopify.listing.api.preview_regenerate_additional_image", {
    item_code: itemCode,
    source_url: sourceUrl,
    url,
  });
}

export function acceptAdditionalImage(
  itemCode: string,
  sourceUrl: string,
  kind: "lifestyle" | "worn",
  url: string,
  opts?: { query?: string; replaceUrl?: string },
): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.listing.api.accept_additional_image", {
    item_code: itemCode,
    source_url: sourceUrl,
    kind,
    url,
    query: opts?.query,
    replace_url: opts?.replaceUrl,
  });
}

export function discardPreviewImage(url: string): Promise<{ discarded: number }> {
  return callMethod("alaiy_os_connector_shopify.listing.api.discard_preview_image", { url });
}

export function removeAdditionalImage(itemCode: string, sourceUrl: string, url: string): Promise<{ removed: number }> {
  return callMethod("alaiy_os_connector_shopify.listing.api.remove_additional_image", {
    item_code: itemCode,
    source_url: sourceUrl,
    url,
  });
}

export function enrichmentErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error && error.message ? error.message : fallback;
}
