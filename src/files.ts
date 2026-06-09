import { shopifyClient } from './client';
import type { FileAcknowledgeUpdateFailedPayload, FileConnection, FileCreateInput, FileCreatePayload, FileDeletePayload, FileSortKeys, FileUpdateInput, FileUpdatePayload, Media, SavedSearchConnection } from './types';

// ============================================================
// Files & Media
// 6 operations
// ============================================================

/** Requires `write_files` access scope. */
export interface FileAcknowledgeUpdateFailedArgs {
  fileIds: string[];
}

export async function fileAcknowledgeUpdateFailed(args: FileAcknowledgeUpdateFailedArgs): Promise<FileAcknowledgeUpdateFailedPayload> {
  const gql = `#graphql
    mutation fileAcknowledgeUpdateFailed($fileIds: [ID!]!) {
      fileAcknowledgeUpdateFailed(fileIds: $fileIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fileAcknowledgeUpdateFailed: FileAcknowledgeUpdateFailedPayload }>(gql, args);
  return data.fileAcknowledgeUpdateFailed;
}

/** Requires `write_files` access scope, `write_themes` access scope or `write_images` access scope. Also: Users must have create files permissions. */
export interface FileCreateArgs {
  files: FileCreateInput[];
}

export async function fileCreate(args: FileCreateArgs): Promise<FileCreatePayload> {
  const gql = `#graphql
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fileCreate: FileCreatePayload }>(gql, args);
  return data.fileCreate;
}

/** Requires `write_files` access scope. Also: Users must have delete files permissions. */
export interface FileDeleteArgs {
  fileIds: string[];
}

export async function fileDelete(args: FileDeleteArgs): Promise<FileDeletePayload> {
  const gql = `#graphql
    mutation fileDelete($fileIds: [ID!]!) {
      fileDelete(fileIds: $fileIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fileDelete: FileDeletePayload }>(gql, args);
  return data.fileDelete;
}

/** Requires `read_files` access scope, `read_themes` access scope or `read_images` access scope. */
export interface FilesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: FileSortKeys;
}

export async function files(args?: FilesArgs): Promise<FileConnection> {
  const gql = `#graphql
    query files($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: FileSortKeys) {
      files(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ files: FileConnection }>(gql, args);
  return data.files;
}

/** Requires `read_files` access scope or `read_themes` access scope. */
export interface FileSavedSearchesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function fileSavedSearches(args?: FileSavedSearchesArgs): Promise<SavedSearchConnection> {
  const gql = `#graphql
    query fileSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      fileSavedSearches(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fileSavedSearches: SavedSearchConnection }>(gql, args);
  return data.fileSavedSearches;
}

/** Requires `write_files` access scope or `write_themes` access scope. Also: Users must have edit files permissions. */
export interface FileUpdateArgs {
  files: FileUpdateInput[];
}

export async function fileUpdate(args: FileUpdateArgs): Promise<FileUpdatePayload> {
  const gql = `#graphql
    mutation fileUpdate($files: [FileUpdateInput!]!) {
      fileUpdate(files: $files) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fileUpdate: FileUpdatePayload }>(gql, args);
  return data.fileUpdate;
}

