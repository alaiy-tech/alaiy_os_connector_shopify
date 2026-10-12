/**
 * Read/write for the Listing detail page: plain Frappe REST GET/PUT/DELETE
 * on `Shopify Product Listing` (same pattern as shopify-listing-toggle.ts
 * and shopify-listing-create.ts), plus the two bespoke whitelisted reads the
 * page needs from listing.py -- effective_values (resolved override/fallback
 * preview).
 */

import { serverMessage } from "./shopify-sync";

export interface ShopifyListingImage {
  name: string | null;
  image: string;
  source: string | null;
  sort_order: number | null;
  generated_by_agent: string | null;
}

export interface ShopifyListingVariant {
  name: string | null;
  item_variant: string;
  is_enabled: 0 | 1;
  variant_price: number | null;
  variant_image: string | null;
  sh_shopify_variant_id: string | null;
  metafields: ShopifyProductMetafield[];
}

export interface ShopifyProductMetafield {
  name: string | null;
  namespace: string;
  key: string;
  type: string | null;
  value: string | null;
}

export interface ShopifyListingDetail {
  name: string;
  item: string;
  is_enabled: 0 | 1;
  sh_shopify_status: string;
  listing_title: string | null;
  listing_description: string | null;
  listing_price: number | null;
  listing_category: string | null;
  listing_product_type: string | null;
  listing_tags: string | null;
  listing_seo_title: string | null;
  listing_seo_description: string | null;
  sh_shopify_product_id: string | null;
  last_synced_at: string | null;
  images: ShopifyListingImage[];
  variants: ShopifyListingVariant[];
  metafields: ShopifyProductMetafield[];
}

/** What listing.effective_values(listing_name) resolves overrides to -- see
 * alaiy_os_connector_shopify/shopify/product/listing.py:effective_values. */
export interface ShopifyListingEffectiveValues {
  title?: string;
  description?: string;
  product_type?: string;
  category?: string;
  seo_title?: string;
  seo_description?: string;
  image_count?: number;
  /** The Item's own price on the selling list; null when it has none. */
  price?: number | null;
  variant_prices?: Record<string, number | null>;
}

const RESOURCE = `/api/resource/${encodeURIComponent("Shopify Product Listing")}`;

async function resourceFetch(name: string, init: RequestInit): Promise<Record<string, unknown>> {
  const res = await fetch(`${RESOURCE}/${encodeURIComponent(name)}`, {
    cache: "no-store",
    ...init,
  });
  const data = await res.json().catch(() => ({}) as Record<string, unknown>);
  if (!res.ok) {
    throw new Error(serverMessage(data as { _server_messages?: string; exception?: string }) ?? `Request failed (${res.status}).`);
  }
  return data;
}

export async function fetchListingDetail(name: string): Promise<ShopifyListingDetail> {
  const data = await resourceFetch(name, { method: "GET" });
  return (data as { data: ShopifyListingDetail }).data;
}

/** Whole-document save (top-level override fields + all three child tables)
 * -- this is what fires on_listing_update server-side (listing_hooks.py). */
export async function saveListing(name: string, patch: Record<string, unknown>): Promise<ShopifyListingDetail> {
  const data = await resourceFetch(name, {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(patch),
  });
  return (data as { data: ShopifyListingDetail }).data;
}

/** Deletes the Listing -- fires on_listing_trash (listing_hooks.py), which
 * archives the product on Shopify if it had a sh_shopify_product_id. */
export async function deleteListing(name: string): Promise<void> {
  await resourceFetch(name, { method: "DELETE" });
}

async function callMethod<T>(method: string, params: Record<string, string>): Promise<T> {
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`/api/method/${method}?${qs}`, { cache: "no-store" });
  const data = await res.json().catch(() => ({}) as Record<string, unknown>);
  if (!res.ok) {
    throw new Error(serverMessage(data as { _server_messages?: string; exception?: string }) ?? `${method} failed.`);
  }
  const message = (data as { message?: T }).message;
  if (message === undefined) throw new Error(`${method} returned nothing.`);
  return message;
}

export function fetchEffectiveValues(listingName: string): Promise<ShopifyListingEffectiveValues> {
  return callMethod("alaiy_os_connector_shopify.shopify.product.listing.effective_values", {
    listing_name: listingName,
  });
}
