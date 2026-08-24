/**
 * Single-record read for the Listing detail page — kept out of
 * shopify-sync.ts (bespoke sync endpoints only) since this is a plain
 * Frappe REST GET, same pattern as fetchResourceList uses internally.
 */

export interface ShopifyListingImage {
  name: string;
  image: string;
  source: string | null;
  sort_order: number | null;
}

export interface ShopifyListingVariant {
  name: string;
  item_variant: string;
  is_enabled: 0 | 1;
  variant_price: number | null;
  variant_image: string | null;
  sh_shopify_variant_id: string | null;
}

export interface ShopifyProductMetafield {
  name: string;
  namespace: string | null;
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
  listing_seo_title: string | null;
  listing_seo_description: string | null;
  sh_shopify_product_id: string | null;
  last_synced_at: string | null;
  images: ShopifyListingImage[];
  variants: ShopifyListingVariant[];
  metafields: ShopifyProductMetafield[];
}

export async function fetchListingDetail(name: string): Promise<ShopifyListingDetail> {
  const res = await fetch(
    `/api/resource/${encodeURIComponent("Shopify Product Listing")}/${encodeURIComponent(name)}`,
    { cache: "no-store" },
  );
  const data = await res.json().catch(() => ({}) as Record<string, unknown>);
  if (!res.ok) {
    throw new Error((data as { message?: string }).message ?? `Could not load listing ${name}.`);
  }
  return (data as { data: ShopifyListingDetail }).data;
}
