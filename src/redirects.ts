import { shopifyClient } from './client';
import type { Count, SavedSearchConnection, UrlRedirect, UrlRedirectBulkDeleteAllPayload, UrlRedirectBulkDeleteByIdsPayload, UrlRedirectBulkDeleteBySavedSearchPayload, UrlRedirectBulkDeleteBySearchPayload, UrlRedirectConnection, UrlRedirectCreatePayload, UrlRedirectDeletePayload, UrlRedirectImport, UrlRedirectImportCreatePayload, UrlRedirectImportSubmitPayload, UrlRedirectInput, UrlRedirectSortKeys, UrlRedirectUpdatePayload } from './types';

// ============================================================
// URL Redirects
// 14 operations
// ============================================================

/** Returns a `UrlRedirect` resource by ID. */
export interface UrlRedirectArgs {
  id: string;
}

export async function urlRedirect(args: UrlRedirectArgs): Promise<string> {
  const gql = `#graphql
    query urlRedirect($id: ID!) {
      urlRedirect(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirect: string }>(gql, args);
  return data.urlRedirect;
}

/** A list of redirects for a shop. */
export interface UrlRedirectsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: UrlRedirectSortKeys;
}

export async function urlRedirects(args?: UrlRedirectsArgs): Promise<UrlRedirectConnection> {
  const gql = `#graphql
    query urlRedirects($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: UrlRedirectSortKeys) {
      urlRedirects(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirects: UrlRedirectConnection }>(gql, args);
  return data.urlRedirects;
}

/** Requires `read_online_store_navigation` access scope. */
export interface UrlRedirectSavedSearchesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function urlRedirectSavedSearches(args?: UrlRedirectSavedSearchesArgs): Promise<SavedSearchConnection> {
  const gql = `#graphql
    query urlRedirectSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      urlRedirectSavedSearches(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectSavedSearches: SavedSearchConnection }>(gql, args);
  return data.urlRedirectSavedSearches;
}

/** Requires `read_online_store_navigation` access scope. */
export interface UrlRedirectsCountArgs {
  limit?: number;
  query?: string;
  savedSearchId?: string;
}

export async function urlRedirectsCount(args?: UrlRedirectsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query urlRedirectsCount($limit: Int, $query: String, $savedSearchId: ID) {
      urlRedirectsCount(limit: $limit, query: $query, savedSearchId: $savedSearchId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectsCount: Count | null }>(gql, args);
  return data.urlRedirectsCount;
}

/** Requires `write_online_store_navigation` access scope. Also: Requires an active user. */
export async function urlRedirectBulkDeleteAll(): Promise<UrlRedirectBulkDeleteAllPayload> {
  const gql = `#graphql
    mutation urlRedirectBulkDeleteAll {
      urlRedirectBulkDeleteAll {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectBulkDeleteAll: UrlRedirectBulkDeleteAllPayload }>(gql);
  return data.urlRedirectBulkDeleteAll;
}

/** Requires `write_online_store_navigation` access scope. Also: Requires an active user. */
export interface UrlRedirectBulkDeleteByIdsArgs {
  ids: string[];
}

export async function urlRedirectBulkDeleteByIds(args: UrlRedirectBulkDeleteByIdsArgs): Promise<UrlRedirectBulkDeleteByIdsPayload> {
  const gql = `#graphql
    mutation urlRedirectBulkDeleteByIds($ids: [ID!]!) {
      urlRedirectBulkDeleteByIds(ids: $ids) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectBulkDeleteByIds: UrlRedirectBulkDeleteByIdsPayload }>(gql, args);
  return data.urlRedirectBulkDeleteByIds;
}

/** Requires `write_online_store_navigation` access scope. Also: Requires an active user. */
export interface UrlRedirectBulkDeleteBySavedSearchArgs {
  savedSearchId: string;
}

export async function urlRedirectBulkDeleteBySavedSearch(args: UrlRedirectBulkDeleteBySavedSearchArgs): Promise<UrlRedirectBulkDeleteBySavedSearchPayload> {
  const gql = `#graphql
    mutation urlRedirectBulkDeleteBySavedSearch($savedSearchId: ID!) {
      urlRedirectBulkDeleteBySavedSearch(savedSearchId: $savedSearchId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectBulkDeleteBySavedSearch: UrlRedirectBulkDeleteBySavedSearchPayload }>(gql, args);
  return data.urlRedirectBulkDeleteBySavedSearch;
}

/** Requires `write_online_store_navigation` access scope. Also: Requires an active user. */
export interface UrlRedirectBulkDeleteBySearchArgs {
  search: string;
}

export async function urlRedirectBulkDeleteBySearch(args: UrlRedirectBulkDeleteBySearchArgs): Promise<UrlRedirectBulkDeleteBySearchPayload> {
  const gql = `#graphql
    mutation urlRedirectBulkDeleteBySearch($search: String!) {
      urlRedirectBulkDeleteBySearch(search: $search) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectBulkDeleteBySearch: UrlRedirectBulkDeleteBySearchPayload }>(gql, args);
  return data.urlRedirectBulkDeleteBySearch;
}

/** Requires `write_online_store_navigation` access scope. */
export interface UrlRedirectCreateArgs {
  urlRedirect: UrlRedirectInput;
}

export async function urlRedirectCreate(args: UrlRedirectCreateArgs): Promise<UrlRedirectCreatePayload> {
  const gql = `#graphql
    mutation urlRedirectCreate($urlRedirect: UrlRedirectInput!) {
      urlRedirectCreate(urlRedirect: $urlRedirect) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectCreate: UrlRedirectCreatePayload }>(gql, args);
  return data.urlRedirectCreate;
}

/** Requires `write_online_store_navigation` access scope. */
export interface UrlRedirectDeleteArgs {
  id: string;
}

export async function urlRedirectDelete(args: UrlRedirectDeleteArgs): Promise<UrlRedirectDeletePayload> {
  const gql = `#graphql
    mutation urlRedirectDelete($id: ID!) {
      urlRedirectDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectDelete: UrlRedirectDeletePayload }>(gql, args);
  return data.urlRedirectDelete;
}

/** Returns a `UrlRedirectImport` resource by ID. */
export interface UrlRedirectImportArgs {
  id: string;
}

export async function urlRedirectImport(args: UrlRedirectImportArgs): Promise<number | null> {
  const gql = `#graphql
    query urlRedirectImport($id: ID!) {
      urlRedirectImport(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectImport: number | null }>(gql, args);
  return data.urlRedirectImport;
}

/** Requires `write_online_store_navigation` access scope. */
export interface UrlRedirectImportCreateArgs {
  url: string;
}

export async function urlRedirectImportCreate(args: UrlRedirectImportCreateArgs): Promise<UrlRedirectImportCreatePayload> {
  const gql = `#graphql
    mutation urlRedirectImportCreate($url: URL!) {
      urlRedirectImportCreate(url: $url) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectImportCreate: UrlRedirectImportCreatePayload }>(gql, args);
  return data.urlRedirectImportCreate;
}

/** Requires `write_online_store_navigation` access scope. */
export interface UrlRedirectImportSubmitArgs {
  id: string;
}

export async function urlRedirectImportSubmit(args: UrlRedirectImportSubmitArgs): Promise<UrlRedirectImportSubmitPayload> {
  const gql = `#graphql
    mutation urlRedirectImportSubmit($id: ID!) {
      urlRedirectImportSubmit(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectImportSubmit: UrlRedirectImportSubmitPayload }>(gql, args);
  return data.urlRedirectImportSubmit;
}

/** Requires `write_online_store_navigation` access scope. */
export interface UrlRedirectUpdateArgs {
  id: string;
  urlRedirect: UrlRedirectInput;
}

export async function urlRedirectUpdate(args: UrlRedirectUpdateArgs): Promise<UrlRedirectUpdatePayload> {
  const gql = `#graphql
    mutation urlRedirectUpdate($id: ID!, $urlRedirect: UrlRedirectInput!) {
      urlRedirectUpdate(id: $id, urlRedirect: $urlRedirect) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ urlRedirectUpdate: UrlRedirectUpdatePayload }>(gql, args);
  return data.urlRedirectUpdate;
}

