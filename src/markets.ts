import { shopifyClient } from './client';
import type { BuyerSignalInput, CountryCode, Locale, Market, MarketCatalogConnection, MarketConnection, MarketCreateInput, MarketCreatePayload, MarketCurrencySettingsUpdateInput, MarketCurrencySettingsUpdatePayload, MarketDeletePayload, MarketLocalizableResourceConnection, MarketLocalizableResourceType, MarketLocalizationRegisterInput, MarketLocalizationsRegisterPayload, MarketLocalizationsRemovePayload, MarketRegionCreateInput, MarketRegionDeletePayload, MarketRegionsCreatePayload, MarketRegionsDeletePayload, MarketsSortKeys, MarketType, MarketUpdateInput, MarketUpdatePayload, MarketWebPresenceConnection, MarketWebPresenceCreateInput, MarketWebPresenceCreatePayload, MarketWebPresenceDeletePayload, MarketWebPresenceUpdateInput, MarketWebPresenceUpdatePayload, TranslatableResourceConnection, TranslatableResourceType, TranslationInput, TranslationsRegisterPayload, TranslationsRemovePayload, WebPresenceCreateInput, WebPresenceCreatePayload, WebPresenceDeletePayload, WebPresenceUpdateInput, WebPresenceUpdatePayload } from './types';

// ============================================================
// Markets & Localization
// 30 operations
// ============================================================

/** Returns a `Market` resource by ID. */
export interface MarketArgs {
  id: string;
}

export async function market(args: MarketArgs): Promise<Market | null> {
  const gql = `#graphql
    query market($id: ID!) {
      market(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ market: Market | null }>(gql, args);
  return data.market;
}

/** Requires The user must have markets API access. */
export interface MarketByGeographyArgs {
  countryCode: CountryCode;
}

export async function marketByGeography(args: MarketByGeographyArgs): Promise<Market | null> {
  const gql = `#graphql
    query marketByGeography($countryCode: CountryCode!) {
      marketByGeography(countryCode: $countryCode) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketByGeography: Market | null }>(gql, args);
  return data.marketByGeography;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: MarketsSortKeys;
  type?: MarketType;
}

export async function markets(args?: MarketsArgs): Promise<MarketConnection> {
  const gql = `#graphql
    query markets($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: MarketsSortKeys, $type: MarketType) {
      markets(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey, type: $type) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ markets: MarketConnection }>(gql, args);
  return data.markets;
}

/** The resolved values for a buyer signal. */
export interface MarketsResolvedValuesArgs {
  buyerSignal: BuyerSignalInput;
}

export async function marketsResolvedValues(args: MarketsResolvedValuesArgs): Promise<MarketCatalogConnection> {
  const gql = `#graphql
    query marketsResolvedValues($buyerSignal: BuyerSignalInput!) {
      marketsResolvedValues(buyerSignal: $buyerSignal) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketsResolvedValues: MarketCatalogConnection }>(gql, args);
  return data.marketsResolvedValues;
}

/** Requires The user must have markets API access. */
export async function primaryMarket(): Promise<Market> {
  const gql = `#graphql
    query primaryMarket {
      primaryMarket {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ primaryMarket: Market }>(gql);
  return data.primaryMarket;
}

/** Returns all locales that Shopify supports. Each [`Locale`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Locale) includes an ISO code and human-readable name. Use this query to discover which locales you can enable on a shop with the [`shopLocaleEnable`](https://sh... */
export async function availableLocales(): Promise<Locale[]> {
  const gql = `#graphql
    query availableLocales {
      availableLocales {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ availableLocales: Locale[] }>(gql);
  return data.availableLocales;
}

/** Requires `read_translations` access scope. */
export interface TranslatableResourceArgs {
  resourceId: string;
}

export async function translatableResource(args: TranslatableResourceArgs): Promise<number | null> {
  const gql = `#graphql
    query translatableResource($resourceId: ID!) {
      translatableResource(resourceId: $resourceId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ translatableResource: number | null }>(gql, args);
  return data.translatableResource;
}

/** Requires `read_translations` access scope. */
export interface TranslatableResourcesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  resourceType: TranslatableResourceType;
  reverse?: boolean;
}

export async function translatableResources(args: TranslatableResourcesArgs): Promise<TranslatableResourceConnection> {
  const gql = `#graphql
    query translatableResources($after: String, $before: String, $first: Int, $last: Int, $resourceType: TranslatableResourceType!, $reverse: Boolean) {
      translatableResources(after: $after, before: $before, first: $first, last: $last, resourceType: $resourceType, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ translatableResources: TranslatableResourceConnection }>(gql, args);
  return data.translatableResources;
}

/** Requires `read_translations` access scope. */
export interface TranslatableResourcesByIdsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  resourceIds: string[];
  reverse?: boolean;
}

export async function translatableResourcesByIds(args: TranslatableResourcesByIdsArgs): Promise<TranslatableResourceConnection> {
  const gql = `#graphql
    query translatableResourcesByIds($after: String, $before: String, $first: Int, $last: Int, $resourceIds: [ID!]!, $reverse: Boolean) {
      translatableResourcesByIds(after: $after, before: $before, first: $first, last: $last, resourceIds: $resourceIds, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ translatableResourcesByIds: TranslatableResourceConnection }>(gql, args);
  return data.translatableResourcesByIds;
}

/** Requires `read_translations` access scope. */
export interface MarketLocalizableResourceArgs {
  resourceId: string;
}

export async function marketLocalizableResource(args: MarketLocalizableResourceArgs): Promise<unknown> {
  const gql = `#graphql
    query marketLocalizableResource($resourceId: ID!) {
      marketLocalizableResource(resourceId: $resourceId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketLocalizableResource: unknown }>(gql, args);
  return data.marketLocalizableResource;
}

/** Requires `read_translations` access scope. */
export interface MarketLocalizableResourcesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  resourceType: MarketLocalizableResourceType;
  reverse?: boolean;
}

export async function marketLocalizableResources(args: MarketLocalizableResourcesArgs): Promise<MarketLocalizableResourceConnection> {
  const gql = `#graphql
    query marketLocalizableResources($after: String, $before: String, $first: Int, $last: Int, $resourceType: MarketLocalizableResourceType!, $reverse: Boolean) {
      marketLocalizableResources(after: $after, before: $before, first: $first, last: $last, resourceType: $resourceType, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketLocalizableResources: MarketLocalizableResourceConnection }>(gql, args);
  return data.marketLocalizableResources;
}

/** Requires `read_translations` access scope. */
export interface MarketLocalizableResourcesByIdsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  resourceIds: string[];
  reverse?: boolean;
}

export async function marketLocalizableResourcesByIds(args: MarketLocalizableResourcesByIdsArgs): Promise<MarketLocalizableResourceConnection> {
  const gql = `#graphql
    query marketLocalizableResourcesByIds($after: String, $before: String, $first: Int, $last: Int, $resourceIds: [ID!]!, $reverse: Boolean) {
      marketLocalizableResourcesByIds(after: $after, before: $before, first: $first, last: $last, resourceIds: $resourceIds, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketLocalizableResourcesByIds: MarketLocalizableResourceConnection }>(gql, args);
  return data.marketLocalizableResourcesByIds;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketCreateArgs {
  input: MarketCreateInput;
}

export async function marketCreate(args: MarketCreateArgs): Promise<MarketCreatePayload> {
  const gql = `#graphql
    mutation marketCreate($input: MarketCreateInput!) {
      marketCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketCreate: MarketCreatePayload }>(gql, args);
  return data.marketCreate;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketCurrencySettingsUpdateArgs {
  input: MarketCurrencySettingsUpdateInput;
  marketId: string;
}

export async function marketCurrencySettingsUpdate(args: MarketCurrencySettingsUpdateArgs): Promise<MarketCurrencySettingsUpdatePayload> {
  const gql = `#graphql
    mutation marketCurrencySettingsUpdate($input: MarketCurrencySettingsUpdateInput!, $marketId: ID!) {
      marketCurrencySettingsUpdate(input: $input, marketId: $marketId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketCurrencySettingsUpdate: MarketCurrencySettingsUpdatePayload }>(gql, args);
  return data.marketCurrencySettingsUpdate;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketDeleteArgs {
  id: string;
}

export async function marketDelete(args: MarketDeleteArgs): Promise<MarketDeletePayload> {
  const gql = `#graphql
    mutation marketDelete($id: ID!) {
      marketDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketDelete: MarketDeletePayload }>(gql, args);
  return data.marketDelete;
}

/** Requires `write_translations` access scope. */
export interface MarketLocalizationsRegisterArgs {
  marketLocalizations: MarketLocalizationRegisterInput[];
  resourceId: string;
}

export async function marketLocalizationsRegister(args: MarketLocalizationsRegisterArgs): Promise<MarketLocalizationsRegisterPayload> {
  const gql = `#graphql
    mutation marketLocalizationsRegister($marketLocalizations: [MarketLocalizationRegisterInput!]!, $resourceId: ID!) {
      marketLocalizationsRegister(marketLocalizations: $marketLocalizations, resourceId: $resourceId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketLocalizationsRegister: MarketLocalizationsRegisterPayload }>(gql, args);
  return data.marketLocalizationsRegister;
}

/** Requires `write_translations` access scope. */
export interface MarketLocalizationsRemoveArgs {
  marketIds: string[];
  marketLocalizationKeys: string[];
  resourceId: string;
}

export async function marketLocalizationsRemove(args: MarketLocalizationsRemoveArgs): Promise<MarketLocalizationsRemovePayload> {
  const gql = `#graphql
    mutation marketLocalizationsRemove($marketIds: [ID!]!, $marketLocalizationKeys: [String!]!, $resourceId: ID!) {
      marketLocalizationsRemove(marketIds: $marketIds, marketLocalizationKeys: $marketLocalizationKeys, resourceId: $resourceId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketLocalizationsRemove: MarketLocalizationsRemovePayload }>(gql, args);
  return data.marketLocalizationsRemove;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketRegionDeleteArgs {
  id: string;
}

export async function marketRegionDelete(args: MarketRegionDeleteArgs): Promise<MarketRegionDeletePayload> {
  const gql = `#graphql
    mutation marketRegionDelete($id: ID!) {
      marketRegionDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketRegionDelete: MarketRegionDeletePayload }>(gql, args);
  return data.marketRegionDelete;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketRegionsCreateArgs {
  marketId: string;
  regions: MarketRegionCreateInput[];
}

export async function marketRegionsCreate(args: MarketRegionsCreateArgs): Promise<MarketRegionsCreatePayload> {
  const gql = `#graphql
    mutation marketRegionsCreate($marketId: ID!, $regions: [MarketRegionCreateInput!]!) {
      marketRegionsCreate(marketId: $marketId, regions: $regions) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketRegionsCreate: MarketRegionsCreatePayload }>(gql, args);
  return data.marketRegionsCreate;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketRegionsDeleteArgs {
  ids: string[];
}

export async function marketRegionsDelete(args: MarketRegionsDeleteArgs): Promise<MarketRegionsDeletePayload> {
  const gql = `#graphql
    mutation marketRegionsDelete($ids: [ID!]!) {
      marketRegionsDelete(ids: $ids) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketRegionsDelete: MarketRegionsDeletePayload }>(gql, args);
  return data.marketRegionsDelete;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketUpdateArgs {
  id: string;
  input: MarketUpdateInput;
}

export async function marketUpdate(args: MarketUpdateArgs): Promise<MarketUpdatePayload> {
  const gql = `#graphql
    mutation marketUpdate($id: ID!, $input: MarketUpdateInput!) {
      marketUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketUpdate: MarketUpdatePayload }>(gql, args);
  return data.marketUpdate;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketWebPresenceCreateArgs {
  marketId: string;
  webPresence: MarketWebPresenceCreateInput;
}

export async function marketWebPresenceCreate(args: MarketWebPresenceCreateArgs): Promise<MarketWebPresenceCreatePayload> {
  const gql = `#graphql
    mutation marketWebPresenceCreate($marketId: ID!, $webPresence: MarketWebPresenceCreateInput!) {
      marketWebPresenceCreate(marketId: $marketId, webPresence: $webPresence) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketWebPresenceCreate: MarketWebPresenceCreatePayload }>(gql, args);
  return data.marketWebPresenceCreate;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketWebPresenceDeleteArgs {
  webPresenceId: string;
}

export async function marketWebPresenceDelete(args: MarketWebPresenceDeleteArgs): Promise<MarketWebPresenceDeletePayload> {
  const gql = `#graphql
    mutation marketWebPresenceDelete($webPresenceId: ID!) {
      marketWebPresenceDelete(webPresenceId: $webPresenceId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketWebPresenceDelete: MarketWebPresenceDeletePayload }>(gql, args);
  return data.marketWebPresenceDelete;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface MarketWebPresenceUpdateArgs {
  webPresence: MarketWebPresenceUpdateInput;
  webPresenceId: string;
}

export async function marketWebPresenceUpdate(args: MarketWebPresenceUpdateArgs): Promise<MarketWebPresenceUpdatePayload> {
  const gql = `#graphql
    mutation marketWebPresenceUpdate($webPresence: MarketWebPresenceUpdateInput!, $webPresenceId: ID!) {
      marketWebPresenceUpdate(webPresence: $webPresence, webPresenceId: $webPresenceId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketWebPresenceUpdate: MarketWebPresenceUpdatePayload }>(gql, args);
  return data.marketWebPresenceUpdate;
}

/** Requires `write_translations` access scope. */
export interface TranslationsRegisterArgs {
  resourceId: string;
  translations: TranslationInput[];
}

export async function translationsRegister(args: TranslationsRegisterArgs): Promise<TranslationsRegisterPayload> {
  const gql = `#graphql
    mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
      translationsRegister(resourceId: $resourceId, translations: $translations) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ translationsRegister: TranslationsRegisterPayload }>(gql, args);
  return data.translationsRegister;
}

/** Requires `write_translations` access scope. */
export interface TranslationsRemoveArgs {
  locales: string[];
  marketIds?: string[];
  resourceId: string;
  translationKeys: string[];
}

export async function translationsRemove(args: TranslationsRemoveArgs): Promise<TranslationsRemovePayload> {
  const gql = `#graphql
    mutation translationsRemove($locales: [String!]!, $marketIds: [ID!]!, $resourceId: ID!, $translationKeys: [String!]!) {
      translationsRemove(locales: $locales, marketIds: $marketIds, resourceId: $resourceId, translationKeys: $translationKeys) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ translationsRemove: TranslationsRemovePayload }>(gql, args);
  return data.translationsRemove;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface WebPresenceCreateArgs {
  input: WebPresenceCreateInput;
}

export async function webPresenceCreate(args: WebPresenceCreateArgs): Promise<WebPresenceCreatePayload> {
  const gql = `#graphql
    mutation webPresenceCreate($input: WebPresenceCreateInput!) {
      webPresenceCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webPresenceCreate: WebPresenceCreatePayload }>(gql, args);
  return data.webPresenceCreate;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface WebPresenceDeleteArgs {
  id: string;
}

export async function webPresenceDelete(args: WebPresenceDeleteArgs): Promise<WebPresenceDeletePayload> {
  const gql = `#graphql
    mutation webPresenceDelete($id: ID!) {
      webPresenceDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webPresenceDelete: WebPresenceDeletePayload }>(gql, args);
  return data.webPresenceDelete;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface WebPresenceUpdateArgs {
  id: string;
  input: WebPresenceUpdateInput;
}

export async function webPresenceUpdate(args: WebPresenceUpdateArgs): Promise<WebPresenceUpdatePayload> {
  const gql = `#graphql
    mutation webPresenceUpdate($id: ID!, $input: WebPresenceUpdateInput!) {
      webPresenceUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webPresenceUpdate: WebPresenceUpdatePayload }>(gql, args);
  return data.webPresenceUpdate;
}

/** Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations. */
export interface WebPresencesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function webPresences(args?: WebPresencesArgs): Promise<MarketWebPresenceConnection | null> {
  const gql = `#graphql
    query webPresences($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      webPresences(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webPresences: MarketWebPresenceConnection | null }>(gql, args);
  return data.webPresences;
}

