import { shopifyClient } from './client';
import type { BackupRegionUpdateInput, BackupRegionUpdatePayload, OnlineStoreThemeConnection, OnlineStoreThemeFileConnection, OnlineStoreThemeFilesUpsertFileInput, OnlineStoreThemeInput, Shop, ThemeCreatePayload, ThemeDeletePayload, ThemeDuplicatePayload, ThemeFilesCopyFileInput, ThemeFilesCopyPayload, ThemeFilesDeletePayload, ThemeFilesUpsertPayload, ThemePublishPayload, ThemeRole, ThemeUpdatePayload } from './types';

// ============================================================
// Themes & Online Store
// 14 operations
// ============================================================

/** Requires `read_themes` access scope. */
export interface ThemeArgs {
  id: string;
}

export async function theme(args: ThemeArgs): Promise<OnlineStoreThemeFileConnection | null> {
  const gql = `#graphql
    query theme($id: ID!) {
      theme(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ theme: OnlineStoreThemeFileConnection | null }>(gql, args);
  return data.theme;
}

/** Requires `read_themes` access scope. */
export interface ThemesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  names?: string[];
  reverse?: boolean;
  roles?: ThemeRole[];
}

export async function themes(args?: ThemesArgs): Promise<OnlineStoreThemeConnection | null> {
  const gql = `#graphql
    query themes($after: String, $before: String, $first: Int, $last: Int, $names: [String!]!, $reverse: Boolean, $roles: [ThemeRole!]!) {
      themes(after: $after, before: $before, first: $first, last: $last, names: $names, reverse: $reverse, roles: $roles) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ themes: OnlineStoreThemeConnection | null }>(gql, args);
  return data.themes;
}

/** The shop's online store channel. */
export async function onlineStore(): Promise<unknown> {
  const gql = `#graphql
    query onlineStore {
      onlineStore {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ onlineStore: unknown }>(gql);
  return data.onlineStore;
}

/** The geographic regions that you can set as the [`Shop`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)'s backup region. The backup region serves as a fallback when the system can't determine a buyer's actual location. */
export async function availableBackupRegions(): Promise<string> {
  const gql = `#graphql
    query availableBackupRegions {
      availableBackupRegions {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ availableBackupRegions: string }>(gql);
  return data.availableBackupRegions;
}

/** The backup region of the shop. */
export async function backupRegion(): Promise<string> {
  const gql = `#graphql
    query backupRegion {
      backupRegion {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ backupRegion: string }>(gql);
  return data.backupRegion;
}

/** Requires The user needs write\_themes and an exemption from Shopify to modify themes. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-G... */
export interface ThemeCreateArgs {
  name?: string;
  role?: ThemeRole;
  source: string;
}

export async function themeCreate(args: ThemeCreateArgs): Promise<ThemeCreatePayload> {
  const gql = `#graphql
    mutation themeCreate($name: String, $role: ThemeRole, $source: URL!) {
      themeCreate(name: $name, role: $role, source: $source) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ themeCreate: ThemeCreatePayload }>(gql, args);
  return data.themeCreate;
}

/** Requires The user needs write\_themes and an exemption from Shopify to modify themes. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-G... */
export interface ThemeDeleteArgs {
  id: string;
}

export async function themeDelete(args: ThemeDeleteArgs): Promise<ThemeDeletePayload> {
  const gql = `#graphql
    mutation themeDelete($id: ID!) {
      themeDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ themeDelete: ThemeDeletePayload }>(gql, args);
  return data.themeDelete;
}

/** Requires The user needs write\_themes and an exemption from Shopify to modify themes. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-G... */
export interface ThemeDuplicateArgs {
  id: string;
  name?: string;
}

export async function themeDuplicate(args: ThemeDuplicateArgs): Promise<ThemeDuplicatePayload> {
  const gql = `#graphql
    mutation themeDuplicate($id: ID!, $name: String) {
      themeDuplicate(id: $id, name: $name) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ themeDuplicate: ThemeDuplicatePayload }>(gql, args);
  return data.themeDuplicate;
}

/** Requires The user needs write\_themes and an exemption from Shopify to modify theme files. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC... */
export interface ThemeFilesCopyArgs {
  files: ThemeFilesCopyFileInput[];
  themeId: string;
}

export async function themeFilesCopy(args: ThemeFilesCopyArgs): Promise<ThemeFilesCopyPayload> {
  const gql = `#graphql
    mutation themeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!) {
      themeFilesCopy(files: $files, themeId: $themeId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ themeFilesCopy: ThemeFilesCopyPayload }>(gql, args);
  return data.themeFilesCopy;
}

/** Requires The user needs write\_themes and an exemption from Shopify to modify theme files. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC... */
export interface ThemeFilesDeleteArgs {
  files: string[];
  themeId: string;
}

export async function themeFilesDelete(args: ThemeFilesDeleteArgs): Promise<ThemeFilesDeletePayload> {
  const gql = `#graphql
    mutation themeFilesDelete($files: [String!]!, $themeId: ID!) {
      themeFilesDelete(files: $files, themeId: $themeId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ themeFilesDelete: ThemeFilesDeletePayload }>(gql, args);
  return data.themeFilesDelete;
}

/** Requires The user needs write\_themes and an exemption from Shopify to modify theme files. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC... */
export interface ThemeFilesUpsertArgs {
  files: OnlineStoreThemeFilesUpsertFileInput[];
  themeId: string;
}

export async function themeFilesUpsert(args: ThemeFilesUpsertArgs): Promise<ThemeFilesUpsertPayload> {
  const gql = `#graphql
    mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
      themeFilesUpsert(files: $files, themeId: $themeId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ themeFilesUpsert: ThemeFilesUpsertPayload }>(gql, args);
  return data.themeFilesUpsert;
}

/** Requires The user needs write\_themes and an exemption from Shopify to modify themes. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-G... */
export interface ThemePublishArgs {
  id: string;
}

export async function themePublish(args: ThemePublishArgs): Promise<ThemePublishPayload> {
  const gql = `#graphql
    mutation themePublish($id: ID!) {
      themePublish(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ themePublish: ThemePublishPayload }>(gql, args);
  return data.themePublish;
}

/** Requires The user needs write\_themes and an exemption from Shopify to modify themes. If you think that your app is eligible for an exemption and should have access to this API, then you can [submit an exception request](https://docs.google.com/forms/d/e/1FAIpQLSfZTB1vxFC5d1-G... */
export interface ThemeUpdateArgs {
  id: string;
  input: OnlineStoreThemeInput;
}

export async function themeUpdate(args: ThemeUpdateArgs): Promise<ThemeUpdatePayload> {
  const gql = `#graphql
    mutation themeUpdate($id: ID!, $input: OnlineStoreThemeInput!) {
      themeUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ themeUpdate: ThemeUpdatePayload }>(gql, args);
  return data.themeUpdate;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface BackupRegionUpdateArgs {
  region?: BackupRegionUpdateInput;
}

export async function backupRegionUpdate(args?: BackupRegionUpdateArgs): Promise<BackupRegionUpdatePayload> {
  const gql = `#graphql
    mutation backupRegionUpdate($region: BackupRegionUpdateInput) {
      backupRegionUpdate(region: $region) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ backupRegionUpdate: BackupRegionUpdatePayload }>(gql, args);
  return data.backupRegionUpdate;
}

