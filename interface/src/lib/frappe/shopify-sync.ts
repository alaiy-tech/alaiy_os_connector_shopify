/**
 * Typed client over alaiy_os_connector_shopify.api.sync / api.test_connection.
 *
 * Settings themselves (read/save/test) go through the base's generic
 * `@alaiy-os/frappe/connectors` — Shopify registers `settings_doctype` and
 * `test_method` in connector_meta.py, so that screen needs no bespoke
 * endpoint. This file is only for what IS bespoke: the sync triggers, the
 * dashboard stat cards, and the sync log, none of which the generic registry
 * API knows about.
 */

export interface SyncLogRow {
  name: string;
  sync_type: string;
  trigger: string;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  items_processed: number;
  items_created: number;
  items_failed: number;
  pages_total: number;
  pages_done: number;
  error_message: string | null;
}

export interface DashboardStats {
  items_total: number;
  templates_total: number;
  templates_pushed: number;
  templates_pending: number;
  variants_total: number;
  variants_pushed: number;
  listings_total: number;
  listings_enabled: number;
  templates_active: number;
  templates_draft: number;
  templates_archived: number;
  orders_synced: number;
  last_runs: Record<string, { sync_type: string; status: string; started_at: string }>;
}

export interface ShopifySideStats {
  shopify_products: number | null;
  shopify_orders: number | null;
  shopify_variants: number;
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

export function fetchDashboardStats(connection?: string): Promise<DashboardStats> {
  return callMethod<DashboardStats>("alaiy_os_connector_shopify.api.sync.get_dashboard_stats", { connection });
}

/** Hits the live Shopify API — slower, called separately so it never blocks the fast local numbers. */
export function fetchShopifySideStats(connection?: string): Promise<ShopifySideStats> {
  return callMethod<ShopifySideStats>("alaiy_os_connector_shopify.api.sync.get_shopify_side_stats", { connection });
}

export function fetchSyncStatus(syncType?: "categories" | "items" | "products", connection?: string): Promise<SyncLogRow[]> {
  const params = new URLSearchParams();
  if (syncType) params.set("sync_type", syncType);
  if (connection) params.set("connection", connection);
  const qs = params.toString();
  return callMethod<SyncLogRow[]>(`alaiy_os_connector_shopify.api.sync.get_sync_status${qs ? `?${qs}` : ""}`);
}

export function triggerOrdersSync(connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.trigger_orders_sync", { connection });
}

export function triggerInventoryPush(connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.trigger_inventory_push", { connection });
}

/** Manual on-demand pull -- full catalogue sweep, same backend job as the daily scheduled one. */
export function triggerInventoryPull(connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.trigger_inventory_pull", { connection });
}

export function triggerProductImport(statuses?: string[], connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.trigger_product_import", { statuses, connection });
}

/** Catch-up import: only products never linked locally, never re-verifies existing ones. */
export function triggerMissingProductImport(
  opts?: { statuses?: string[]; collectionId?: string; locationId?: string },
  connection?: string,
): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.trigger_missing_product_import", {
    statuses: opts?.statuses,
    collection_id: opts?.collectionId,
    location_id: opts?.locationId,
    connection,
  });
}

export interface ShopifyProductSearchResult {
  product_id: string;
  title: string;
  handle: string;
  status: string;
  image: string | null;
}

/** Live Shopify title/SKU search -- synchronous, for the "Search for a product…" picker. */
export function searchShopifyProducts(term: string, connection?: string, limit = 20): Promise<ShopifyProductSearchResult[]> {
  return callMethod("alaiy_os_connector_shopify.api.sync.search_shopify_products", { term, limit, connection });
}

/** Pull and import exactly one Shopify product by id -- the pull step after picking a search result. */
export function importShopifyProduct(productId: string, connection?: string): Promise<{ created: boolean; reason: string }> {
  return callMethod("alaiy_os_connector_shopify.api.sync.import_shopify_product", { product_id: productId, connection });
}

export function triggerProductExport(statuses?: string[], connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.trigger_product_export", { statuses, connection });
}

/** A one-off backfill for a date range, distinct from the regular incremental orders sync. */
export function importExistingOrders(dateFrom?: string, dateTo?: string, connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.import_existing_orders", {
    date_from: dateFrom,
    date_to: dateTo,
    connection,
  });
}

/** Bulk-enable every disabled listing whose own status matches one of `statuses`. */
export function enableListingsByStatus(statuses?: string[], connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.enable_listings_by_status", { statuses, connection });
}

export function refreshShopifyTaxonomy(connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.refresh_shopify_taxonomy", { connection });
}

export function refreshShopifyTags(connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.refresh_shopify_tags", { connection });
}

export function refreshShopifyCollections(connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.refresh_shopify_collections", { connection });
}

export function refreshShopifyLocations(connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.sync.refresh_shopify_locations", { connection });
}

/** Stops a queued/running sync on its next poll. No effect on one that already finished. */
export function requestCancelSync(logName: string): Promise<{ cancelled: boolean; reason?: string }> {
  return callMethod("alaiy_os_connector_shopify.shopify.sync_guard.request_cancel", { log_name: logName });
}

export function exportListingsCsv(opts?: {
  listingNames?: string[];
  onlyEnabled?: boolean;
  onlyDisabled?: boolean;
  connection?: string;
}): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.export.trigger_background_export", {
    listing_names: opts?.listingNames,
    only_enabled: opts?.onlyEnabled ? 1 : undefined,
    only_disabled: opts?.onlyDisabled ? 1 : undefined,
    connection: opts?.connection,
  });
}

/** `fileUrl` is a Frappe File doc's `file_url`, from the normal upload dialog. */
export function triggerUpdateListingsCsv(fileUrl: string, connection?: string): Promise<unknown> {
  return callMethod("alaiy_os_connector_shopify.api.update_listings.trigger_update_listings", {
    file_url: fileUrl,
    connection,
  });
}

/**
 * Standard Frappe file upload (`/api/method/upload_file`) — distinct from
 * a bespoke multipart endpoint. `trigger_update_listings` above needs a
 * real File document's `file_url` to already exist, not raw CSV content.
 */
export async function uploadPrivateFile(file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  form.append("is_private", "1");
  const res = await fetch("/api/method/upload_file", { method: "POST", body: form, cache: "no-store" });
  const data = await res.json().catch(() => ({}) as Record<string, unknown>);
  if (!res.ok) throw new Error((data as { message?: string }).message ?? "Could not upload the file.");
  const fileUrl = (data as { message?: { file_url?: string } }).message?.file_url;
  if (!fileUrl) throw new Error("Upload succeeded but returned no file URL.");
  return fileUrl;
}

export function shopifyErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error && error.message ? error.message : fallback;
}

/**
 * A plain read-only list off `/api/resource/<doctype>` — the base's generic
 * Frappe REST proxy (see PATH.md). Used for the simple Shopify masters
 * (Category, Collection, Location, Tag) that have no bespoke Python of
 * their own; no reason to write one just to re-shape a list Frappe already
 * serves.
 */
export async function fetchResourceList<T extends Record<string, unknown>>(
  doctype: string,
  fields: string[],
  opts?: { orderBy?: string; filters?: Array<[string, string, unknown]> },
): Promise<T[]> {
  const params = new URLSearchParams();
  params.set("fields", JSON.stringify(fields));
  params.set("limit_page_length", "0");
  if (opts?.orderBy) params.set("order_by", opts.orderBy);
  if (opts?.filters) params.set("filters", JSON.stringify(opts.filters));

  const res = await fetch(`/api/resource/${encodeURIComponent(doctype)}?${params.toString()}`, { cache: "no-store" });
  const data = await res.json().catch(() => ({}) as Record<string, unknown>);
  if (!res.ok) {
    throw new Error((data as { message?: string }).message ?? `Could not load ${doctype}.`);
  }
  return (data as { data: T[] }).data;
}
