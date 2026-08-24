import { STATUS_TONE } from "@alaiy-os/constants/list";

/** Shopify Sync Log.status. */
export const SYNC_STATUS_BADGE_CLASS: Record<string, (typeof STATUS_TONE)[keyof typeof STATUS_TONE]> = {
  Success: STATUS_TONE.success,
  Running: STATUS_TONE.info,
  Failed: STATUS_TONE.destructive,
  Skipped: STATUS_TONE.neutral,
};
export const DEFAULT_SYNC_STATUS_BADGE_CLASS = STATUS_TONE.neutral;

/** Shopify Product Listing.sh_shopify_status — blank reads as Active, same rule the backend uses. */
export const LISTING_STATUS_BADGE_CLASS: Record<string, (typeof STATUS_TONE)[keyof typeof STATUS_TONE]> = {
  Active: STATUS_TONE.success,
  Draft: STATUS_TONE.warning,
  Archived: STATUS_TONE.neutral,
};
export const DEFAULT_LISTING_STATUS_BADGE_CLASS = STATUS_TONE.success;

export function getSyncStatusBadgeClass(status: string): string {
  return SYNC_STATUS_BADGE_CLASS[status] ?? DEFAULT_SYNC_STATUS_BADGE_CLASS;
}

export function getListingStatusBadgeClass(status: string): string {
  if (!status) return DEFAULT_LISTING_STATUS_BADGE_CLASS;
  return LISTING_STATUS_BADGE_CLASS[status] ?? STATUS_TONE.neutral;
}
