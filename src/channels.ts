import { shopifyClient } from './client';
import type { CatalogType, Channel, ChannelConnection, ChannelCreateInput, ChannelCreatePayload, ChannelDeletePayload, ChannelFullSyncPayload, ChannelUpdateInput, ChannelUpdatePayload, CheckoutAndAccountsConfigurationBranding, CheckoutAndAccountsConfigurationConnection, CheckoutAndAccountsConfigurationInput, CheckoutAndAccountsConfigurationsGraphQLSortKeys, CheckoutAndAccountsConfigurationUpdatePayload, CheckoutBrandingCustomizations, CheckoutBrandingInput, CheckoutBrandingUpsertPayload, CheckoutProfileConnection, CheckoutProfileSortKeys, ConsentPolicyInput, ConsentPolicyUpdatePayload, Count, CountryCode, LanguageCode, PrivacyCountryCode, Publication, PublicationConnection, PublicationCreateInput, PublicationCreatePayload, PublicationDeletePayload, PublicationInput, PublicationUpdateInput, PublicationUpdatePayload, PublishablePublishPayload, PublishablePublishToCurrentChannelPayload, PublishableUnpublishPayload, PublishableUnpublishToCurrentChannelPayload } from './types';

// ============================================================
// Channels, Publications & Checkout
// 27 operations
// ============================================================

/** Returns a [`Channel`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel) by ID. The channel must belong to the calling application. */
export interface ChannelArgs {
  id: string;
}

export async function channel(args: ChannelArgs): Promise<Channel | null> {
  const gql = `#graphql
    query channel($id: ID!) {
      channel(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ channel: Channel | null }>(gql, args);
  return data.channel;
}

/** Returns a [`Channel`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel) by its unique string handle. The handle is either set explicitly during [`channelCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/channelCreate) or auto-generated from ... */
export interface ChannelByHandleArgs {
  handle: string;
}

export async function channelByHandle(args: ChannelByHandleArgs): Promise<Channel | null> {
  const gql = `#graphql
    query channelByHandle($handle: String!) {
      channelByHandle(handle: $handle) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ channelByHandle: Channel | null }>(gql, args);
  return data.channelByHandle;
}

/** The list of [`Channel`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel) objects on the shop. When the calling application supports multi-channel, only channels established by the calling application are returned. Each channel represents an authenticated conn... */
export interface ChannelsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function channels(args?: ChannelsArgs): Promise<ChannelConnection> {
  const gql = `#graphql
    query channels($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      channels(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ channels: ChannelConnection }>(gql, args);
  return data.channels;
}

/** A checkout and accounts configuration for a shop. */
export interface CheckoutAndAccountsConfigurationArgs {
  id: string;
}

export async function checkoutAndAccountsConfiguration(args: CheckoutAndAccountsConfigurationArgs): Promise<CheckoutAndAccountsConfigurationBranding | null> {
  const gql = `#graphql
    query checkoutAndAccountsConfiguration($id: ID!) {
      checkoutAndAccountsConfiguration(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ checkoutAndAccountsConfiguration: CheckoutAndAccountsConfigurationBranding | null }>(gql, args);
  return data.checkoutAndAccountsConfiguration;
}

/** List of checkout and accounts configurations on a shop. */
export interface CheckoutAndAccountsConfigurationsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: CheckoutAndAccountsConfigurationsGraphQLSortKeys;
}

export async function checkoutAndAccountsConfigurations(args?: CheckoutAndAccountsConfigurationsArgs): Promise<CheckoutAndAccountsConfigurationConnection | null> {
  const gql = `#graphql
    query checkoutAndAccountsConfigurations($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CheckoutAndAccountsConfigurationsGraphQLSortKeys) {
      checkoutAndAccountsConfigurations(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ checkoutAndAccountsConfigurations: CheckoutAndAccountsConfigurationConnection | null }>(gql, args);
  return data.checkoutAndAccountsConfigurations;
}

/** Deprecated. Use [checkoutAndAccountsConfiguration](https://shopify.dev/docs/api/admin-graphql/latest/queries/checkoutAndAccountsConfiguration) instead. */
export interface CheckoutBrandingArgs {
  checkoutProfileId: string;
}

export async function checkoutBranding(args: CheckoutBrandingArgs): Promise<CheckoutBrandingCustomizations | null> {
  const gql = `#graphql
    query checkoutBranding($checkoutProfileId: ID!) {
      checkoutBranding(checkoutProfileId: $checkoutProfileId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ checkoutBranding: CheckoutBrandingCustomizations | null }>(gql, args);
  return data.checkoutBranding;
}

/** Requires access to the checkout and accounts editor. */
export interface CheckoutProfileArgs {
  id: string;
}

export async function checkoutProfile(args: CheckoutProfileArgs): Promise<string> {
  const gql = `#graphql
    query checkoutProfile($id: ID!) {
      checkoutProfile(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ checkoutProfile: string }>(gql, args);
  return data.checkoutProfile;
}

/** Requires access to the checkout and accounts editor. */
export interface CheckoutProfilesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: CheckoutProfileSortKeys;
}

export async function checkoutProfiles(args?: CheckoutProfilesArgs): Promise<CheckoutProfileConnection> {
  const gql = `#graphql
    query checkoutProfiles($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CheckoutProfileSortKeys) {
      checkoutProfiles(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ checkoutProfiles: CheckoutProfileConnection }>(gql, args);
  return data.checkoutProfiles;
}

/** Returns the customer privacy consent policies of a shop. */
export interface ConsentPolicyArgs {
  consentRequired?: boolean;
  countryCode?: PrivacyCountryCode;
  dataSaleOptOutRequired?: boolean;
  id?: string;
  regionCode?: string;
}

export async function consentPolicy(args?: ConsentPolicyArgs): Promise<string> {
  const gql = `#graphql
    query consentPolicy($consentRequired: Boolean, $countryCode: PrivacyCountryCode, $dataSaleOptOutRequired: Boolean, $id: ID, $regionCode: String) {
      consentPolicy(consentRequired: $consentRequired, countryCode: $countryCode, dataSaleOptOutRequired: $dataSaleOptOutRequired, id: $id, regionCode: $regionCode) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ consentPolicy: string }>(gql, args);
  return data.consentPolicy;
}

/** List of countries and regions for which consent policies can be created or updated. */
export async function consentPolicyRegions(): Promise<unknown> {
  const gql = `#graphql
    query consentPolicyRegions {
      consentPolicyRegions {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ consentPolicyRegions: unknown }>(gql);
  return data.consentPolicyRegions;
}

/** Retrieves a [`Publication`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication) by [`ID`](https://shopify.dev/docs/api/usage/gids). */
export interface PublicationArgs {
  id: string;
}

export async function publication(args: PublicationArgs): Promise<Publication | null> {
  const gql = `#graphql
    query publication($id: ID!) {
      publication(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publication: Publication | null }>(gql, args);
  return data.publication;
}

/** Requires `read_publications` access scope. */
export interface PublicationsArgs {
  after?: string;
  before?: string;
  catalogType?: CatalogType;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function publications(args?: PublicationsArgs): Promise<PublicationConnection> {
  const gql = `#graphql
    query publications($after: String, $before: String, $catalogType: CatalogType, $first: Int, $last: Int, $reverse: Boolean) {
      publications(after: $after, before: $before, catalogType: $catalogType, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publications: PublicationConnection }>(gql, args);
  return data.publications;
}

/** Requires `read_publications` access scope. */
export interface PublicationsCountArgs {
  catalogType?: CatalogType;
  limit?: number;
}

export async function publicationsCount(args?: PublicationsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query publicationsCount($catalogType: CatalogType, $limit: Int) {
      publicationsCount(catalogType: $catalogType, limit: $limit) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publicationsCount: Count | null }>(gql, args);
  return data.publicationsCount;
}

/** Creates a [`Channel`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel) representing a connection between the shop and an external selling platform account. Use this mutation after a merchant authenticates with an external platform to establish the publishing ... */
export interface ChannelCreateArgs {
  input: ChannelCreateInput;
}

export async function channelCreate(args: ChannelCreateArgs): Promise<ChannelCreatePayload> {
  const gql = `#graphql
    mutation channelCreate($input: ChannelCreateInput!) {
      channelCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ channelCreate: ChannelCreatePayload }>(gql, args);
  return data.channelCreate;
}

/** Deletes a [`Channel`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel) from the shop. All associated product feeds are removed. Existing orders attributed to the channel are preserved. The channel must have been created via [`channelCreate`](https://shopify.d... */
export interface ChannelDeleteArgs {
  id: string;
}

export async function channelDelete(args: ChannelDeleteArgs): Promise<ChannelDeletePayload> {
  const gql = `#graphql
    mutation channelDelete($id: ID!) {
      channelDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ channelDelete: ChannelDeletePayload }>(gql, args);
  return data.channelDelete;
}

/** Requires Access allowed for apps with `read_product_listings` scope. */
export interface ChannelFullSyncArgs {
  beforeUpdatedAt?: string;
  channelId: string;
  country?: CountryCode;
  language?: LanguageCode;
  updatedAtSince?: string;
}

export async function channelFullSync(args: ChannelFullSyncArgs): Promise<ChannelFullSyncPayload> {
  const gql = `#graphql
    mutation channelFullSync($beforeUpdatedAt: DateTime, $channelId: ID!, $country: CountryCode, $language: LanguageCode, $updatedAtSince: DateTime) {
      channelFullSync(beforeUpdatedAt: $beforeUpdatedAt, channelId: $channelId, country: $country, language: $language, updatedAtSince: $updatedAtSince) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ channelFullSync: ChannelFullSyncPayload }>(gql, args);
  return data.channelFullSync;
}

/** Updates the properties of an existing [`Channel`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel). Use this mutation to update account information — such as the display name shown in Shopify Admin — or to bind the channel to a different channel specification. */
export interface ChannelUpdateArgs {
  id: string;
  input: ChannelUpdateInput;
}

export async function channelUpdate(args: ChannelUpdateArgs): Promise<ChannelUpdatePayload> {
  const gql = `#graphql
    mutation channelUpdate($id: ID!, $input: ChannelUpdateInput!) {
      channelUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ channelUpdate: ChannelUpdatePayload }>(gql, args);
  return data.channelUpdate;
}

/** Requires `write_checkout_and_accounts_configurations` access scope or `write_checkout_settings` access scope. Also: User must have `manage_checkout_settings` permission and shop must have access to the checkout and accounts editor as well as the contextualized checkouts and cu... */
export interface CheckoutAndAccountsConfigurationUpdateArgs {
  configuration: CheckoutAndAccountsConfigurationInput;
  id: string;
}

export async function checkoutAndAccountsConfigurationUpdate(args: CheckoutAndAccountsConfigurationUpdateArgs): Promise<CheckoutAndAccountsConfigurationUpdatePayload> {
  const gql = `#graphql
    mutation checkoutAndAccountsConfigurationUpdate($configuration: CheckoutAndAccountsConfigurationInput!, $id: ID!) {
      checkoutAndAccountsConfigurationUpdate(configuration: $configuration, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ checkoutAndAccountsConfigurationUpdate: CheckoutAndAccountsConfigurationUpdatePayload }>(gql, args);
  return data.checkoutAndAccountsConfigurationUpdate;
}

/** Requires access to checkout branding settings and the shop must be on a Plus plan or a Development store plan. User must have `preferences` permission to modify. */
export interface CheckoutBrandingUpsertArgs {
  checkoutBrandingInput?: CheckoutBrandingInput;
  checkoutProfileId: string;
}

export async function checkoutBrandingUpsert(args: CheckoutBrandingUpsertArgs): Promise<CheckoutBrandingUpsertPayload> {
  const gql = `#graphql
    mutation checkoutBrandingUpsert($checkoutBrandingInput: CheckoutBrandingInput, $checkoutProfileId: ID!) {
      checkoutBrandingUpsert(checkoutBrandingInput: $checkoutBrandingInput, checkoutProfileId: $checkoutProfileId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ checkoutBrandingUpsert: CheckoutBrandingUpsertPayload }>(gql, args);
  return data.checkoutBrandingUpsert;
}

/** Requires `write_privacy_settings` access scope. */
export interface ConsentPolicyUpdateArgs {
  consentPolicies: ConsentPolicyInput[];
}

export async function consentPolicyUpdate(args: ConsentPolicyUpdateArgs): Promise<ConsentPolicyUpdatePayload> {
  const gql = `#graphql
    mutation consentPolicyUpdate($consentPolicies: [ConsentPolicyInput!]!) {
      consentPolicyUpdate(consentPolicies: $consentPolicies) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ consentPolicyUpdate: ConsentPolicyUpdatePayload }>(gql, args);
  return data.consentPolicyUpdate;
}

/** Requires `write_publications` access scope. Also: The user must have a permission to create and edit catalogs. */
export interface PublicationCreateArgs {
  input: PublicationCreateInput;
}

export async function publicationCreate(args: PublicationCreateArgs): Promise<PublicationCreatePayload> {
  const gql = `#graphql
    mutation publicationCreate($input: PublicationCreateInput!) {
      publicationCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publicationCreate: PublicationCreatePayload }>(gql, args);
  return data.publicationCreate;
}

/** Requires `write_publications` access scope. Also: The user must have a permission to create and edit catalogs. */
export interface PublicationDeleteArgs {
  id: string;
}

export async function publicationDelete(args: PublicationDeleteArgs): Promise<PublicationDeletePayload> {
  const gql = `#graphql
    mutation publicationDelete($id: ID!) {
      publicationDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publicationDelete: PublicationDeletePayload }>(gql, args);
  return data.publicationDelete;
}

/** Requires `write_publications` access scope. Also: The user must have a permission to create and edit catalogs. */
export interface PublicationUpdateArgs {
  id: string;
  input: PublicationUpdateInput;
}

export async function publicationUpdate(args: PublicationUpdateArgs): Promise<PublicationUpdatePayload> {
  const gql = `#graphql
    mutation publicationUpdate($id: ID!, $input: PublicationUpdateInput!) {
      publicationUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publicationUpdate: PublicationUpdatePayload }>(gql, args);
  return data.publicationUpdate;
}

/** Requires `write_publications` access scope. Also: The user must have permission to create and edit products or create and edit catalogs. */
export interface PublishablePublishArgs {
  id: string;
  input: PublicationInput[];
}

export async function publishablePublish(args: PublishablePublishArgs): Promise<PublishablePublishPayload> {
  const gql = `#graphql
    mutation publishablePublish($id: ID!, $input: [PublicationInput!]!) {
      publishablePublish(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publishablePublish: PublishablePublishPayload }>(gql, args);
  return data.publishablePublish;
}

/** Requires `write_publications` access scope. Also: The user must have a permission to create and edit products. */
export interface PublishablePublishToCurrentChannelArgs {
  id: string;
}

export async function publishablePublishToCurrentChannel(args: PublishablePublishToCurrentChannelArgs): Promise<PublishablePublishToCurrentChannelPayload> {
  const gql = `#graphql
    mutation publishablePublishToCurrentChannel($id: ID!) {
      publishablePublishToCurrentChannel(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publishablePublishToCurrentChannel: PublishablePublishToCurrentChannelPayload }>(gql, args);
  return data.publishablePublishToCurrentChannel;
}

/** Requires `write_publications` access scope. Also: The user must have permission to create and edit products or create and edit catalogs. */
export interface PublishableUnpublishArgs {
  id: string;
  input: PublicationInput[];
}

export async function publishableUnpublish(args: PublishableUnpublishArgs): Promise<PublishableUnpublishPayload> {
  const gql = `#graphql
    mutation publishableUnpublish($id: ID!, $input: [PublicationInput!]!) {
      publishableUnpublish(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publishableUnpublish: PublishableUnpublishPayload }>(gql, args);
  return data.publishableUnpublish;
}

/** Requires `write_publications` access scope. Also: The user must have a permission to create and edit products. */
export interface PublishableUnpublishToCurrentChannelArgs {
  id: string;
}

export async function publishableUnpublishToCurrentChannel(args: PublishableUnpublishToCurrentChannelArgs): Promise<PublishableUnpublishToCurrentChannelPayload> {
  const gql = `#graphql
    mutation publishableUnpublishToCurrentChannel($id: ID!) {
      publishableUnpublishToCurrentChannel(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publishableUnpublishToCurrentChannel: PublishableUnpublishToCurrentChannelPayload }>(gql, args);
  return data.publishableUnpublishToCurrentChannel;
}

