import { shopifyClient } from './client';
import type { App, BankingFinanceAppAccess, Channel, CookieBanner, CurrencyCode, Customer, DataSaleOptOutPayload, DelegateAccessToken, DelegateAccessTokenCreatePayload, DelegateAccessTokenDestroyPayload, DelegateAccessTokenInput, PrivacyFeaturesDisablePayload, PrivacyFeaturesEnum, ResourceFeedbackCreateInput, Shop, ShopifyFunctionConnection, ShopifyPaymentsMerchantCategoryCode, ShopifyPaymentsPayoutAlternateCurrencyCreatePayload, ShopLocaleDisablePayload, ShopLocaleEnablePayload, ShopLocaleInput, ShopLocaleUpdatePayload, ShopPolicyInput, ShopPolicyUpdatePayload, ShopResourceFeedbackCreatePayload, StaffMember, StaffMemberConnection, StaffMembersSortKeys, StagedUploadInput, StagedUploadsCreatePayload, StagedUploadTargetGenerateInput, StagedUploadTargetGeneratePayload, StagedUploadTargetsGeneratePayload, StageImageInput, TagsAddPayload, TagsRemovePayload, TaxAppConfigurePayload, TaxSummaryCreatePayload } from './types';

// ============================================================
// Shop Configuration
// 31 operations
// ============================================================

/** Returns the Shop resource corresponding to the access token used in the request. The Shop resource contains business and store management settings for the shop. */
export async function shop(): Promise<Shop> {
  const gql = `#graphql
    query shop {
      shop {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shop: Shop }>(gql);
  return data.shop;
}

/** The shop's billing preferences, including the currency for paying for apps and services. Use this to create [app charges in the merchant's local billing currency](https://shopify.dev/docs/apps/launch/billing#supported-currencies), helping them budget their app spend without ex... */
export async function shopBillingPreferences(): Promise<CurrencyCode> {
  const gql = `#graphql
    query shopBillingPreferences {
      shopBillingPreferences {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopBillingPreferences: CurrencyCode }>(gql);
  return data.shopBillingPreferences;
}

/** Requires `read_locales` access scope or `read_markets_home` access scope. */
export interface ShopLocalesArgs {
  published?: boolean;
}

export async function shopLocales(args?: ShopLocalesArgs): Promise<string> {
  const gql = `#graphql
    query shopLocales($published: Boolean) {
      shopLocales(published: $published) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopLocales: string }>(gql, args);
  return data.shopLocales;
}

/** Returns a Shopify Function by its ID. [Functions](https://shopify.dev/apps/build/functions) enable you to customize Shopify's backend logic at defined parts of the commerce loop. */
export interface ShopifyFunctionArgs {
  id: string;
}

export async function shopifyFunction(args: ShopifyFunctionArgs): Promise<App> {
  const gql = `#graphql
    query shopifyFunction($id: String!) {
      shopifyFunction(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopifyFunction: App }>(gql, args);
  return data.shopifyFunction;
}

/** Returns Shopify Functions owned by the querying API client installed on the shop. [Functions](https://shopify.dev/docs/apps/build/functions) enable you to customize Shopify's backend logic at specific points in the commerce loop, such as discounts, checkout validation, and ful... */
export interface ShopifyFunctionsArgs {
  after?: string;
  apiType?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
  useCreationUi?: boolean;
}

export async function shopifyFunctions(args?: ShopifyFunctionsArgs): Promise<ShopifyFunctionConnection> {
  const gql = `#graphql
    query shopifyFunctions($after: String, $apiType: String, $before: String, $first: Int, $last: Int, $reverse: Boolean, $useCreationUi: Boolean) {
      shopifyFunctions(after: $after, apiType: $apiType, before: $before, first: $first, last: $last, reverse: $reverse, useCreationUi: $useCreationUi) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopifyFunctions: ShopifyFunctionConnection }>(gql, args);
  return data.shopifyFunctions;
}

/** Requires `read_reports` access scope. Also: Level 2 access to Customer data including name, address, phone, and email fields. Please refer to protected customer data [requirements](https://shopify.dev/docs/apps/launch/protected-customer-data). */
export interface ShopifyqlQueryArgs {
  query: string;
}

export async function shopifyqlQuery(args: ShopifyqlQueryArgs): Promise<unknown> {
  const gql = `#graphql
    query shopifyqlQuery($query: String!) {
      shopifyqlQuery(query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopifyqlQuery: unknown }>(gql, args);
  return data.shopifyqlQuery;
}

/** Returns the Shopify Payments account information for the shop. Includes current balances across all currencies, payout schedules, and bank account configurations. */
export async function shopifyPaymentsAccount(): Promise<boolean> {
  const gql = `#graphql
    query shopifyPaymentsAccount {
      shopifyPaymentsAccount {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopifyPaymentsAccount: boolean }>(gql);
  return data.shopifyPaymentsAccount;
}

/** Retrieves a [staff member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember) by ID. If no ID is provided, the query returns the staff member that's making the request. A staff member is a user who can access the Shopify admin to manage store operations. */
export interface StaffMemberArgs {
  id?: string;
}

export async function staffMember(args?: StaffMemberArgs): Promise<boolean> {
  const gql = `#graphql
    query staffMember($id: ID) {
      staffMember(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ staffMember: boolean }>(gql, args);
  return data.staffMember;
}

/** Returns a paginated list of [`StaffMember`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember) objects for the shop. Staff members are users who can access the Shopify admin to manage store operations. */
export interface StaffMembersArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: StaffMembersSortKeys;
}

export async function staffMembers(args?: StaffMembersArgs): Promise<StaffMemberConnection | null> {
  const gql = `#graphql
    query staffMembers($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: StaffMembersSortKeys) {
      staffMembers(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ staffMembers: StaffMemberConnection | null }>(gql, args);
  return data.staffMembers;
}

/** The staff member making the API request. */
export async function currentStaffMember(): Promise<boolean> {
  const gql = `#graphql
    query currentStaffMember {
      currentStaffMember {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ currentStaffMember: boolean }>(gql);
  return data.currentStaffMember;
}

/** Privacy related settings for a shop. */
export async function privacySettings(): Promise<CookieBanner | null> {
  const gql = `#graphql
    query privacySettings {
      privacySettings {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ privacySettings: CookieBanner | null }>(gql);
  return data.privacySettings;
}

/** The list of publicly-accessible Admin API versions, including supported versions, the release candidate, and unstable versions. */
export async function publicApiVersions(): Promise<string> {
  const gql = `#graphql
    query publicApiVersions {
      publicApiVersions {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publicApiVersions: string }>(gql);
  return data.publicApiVersions;
}

/** Requires `write_locales` access scope. */
export interface ShopLocaleDisableArgs {
  locale: string;
}

export async function shopLocaleDisable(args: ShopLocaleDisableArgs): Promise<ShopLocaleDisablePayload> {
  const gql = `#graphql
    mutation shopLocaleDisable($locale: String!) {
      shopLocaleDisable(locale: $locale) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopLocaleDisable: ShopLocaleDisablePayload }>(gql, args);
  return data.shopLocaleDisable;
}

/** Requires `write_locales` access scope. */
export interface ShopLocaleEnableArgs {
  locale: string;
  marketWebPresenceIds?: string[];
}

export async function shopLocaleEnable(args: ShopLocaleEnableArgs): Promise<ShopLocaleEnablePayload> {
  const gql = `#graphql
    mutation shopLocaleEnable($locale: String!, $marketWebPresenceIds: [ID!]!) {
      shopLocaleEnable(locale: $locale, marketWebPresenceIds: $marketWebPresenceIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopLocaleEnable: ShopLocaleEnablePayload }>(gql, args);
  return data.shopLocaleEnable;
}

/** Requires `write_locales` access scope. */
export interface ShopLocaleUpdateArgs {
  locale: string;
  shopLocale: ShopLocaleInput;
}

export async function shopLocaleUpdate(args: ShopLocaleUpdateArgs): Promise<ShopLocaleUpdatePayload> {
  const gql = `#graphql
    mutation shopLocaleUpdate($locale: String!, $shopLocale: ShopLocaleInput!) {
      shopLocaleUpdate(locale: $locale, shopLocale: $shopLocale) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopLocaleUpdate: ShopLocaleUpdatePayload }>(gql, args);
  return data.shopLocaleUpdate;
}

/** Requires `write_legal_policies` access scope. */
export interface ShopPolicyUpdateArgs {
  shopPolicy: ShopPolicyInput;
}

export async function shopPolicyUpdate(args: ShopPolicyUpdateArgs): Promise<ShopPolicyUpdatePayload> {
  const gql = `#graphql
    mutation shopPolicyUpdate($shopPolicy: ShopPolicyInput!) {
      shopPolicyUpdate(shopPolicy: $shopPolicy) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopPolicyUpdate: ShopPolicyUpdatePayload }>(gql, args);
  return data.shopPolicyUpdate;
}

/** Requires `write_resource_feedbacks` access scope. Also: App must be configured to use the Storefront API or as a Sales Channel. */
export interface ShopResourceFeedbackCreateArgs {
  input: ResourceFeedbackCreateInput;
}

export async function shopResourceFeedbackCreate(args: ShopResourceFeedbackCreateArgs): Promise<ShopResourceFeedbackCreatePayload> {
  const gql = `#graphql
    mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopResourceFeedbackCreate: ShopResourceFeedbackCreatePayload }>(gql, args);
  return data.shopResourceFeedbackCreate;
}

/** Requires `write_shopify_payments_tooling` access scope. */
export interface ShopifyPaymentsPayoutAlternateCurrencyCreateArgs {
  accountId?: string;
  currency: CurrencyCode;
}

export async function shopifyPaymentsPayoutAlternateCurrencyCreate(args: ShopifyPaymentsPayoutAlternateCurrencyCreateArgs): Promise<ShopifyPaymentsPayoutAlternateCurrencyCreatePayload> {
  const gql = `#graphql
    mutation shopifyPaymentsPayoutAlternateCurrencyCreate($accountId: ID, $currency: CurrencyCode!) {
      shopifyPaymentsPayoutAlternateCurrencyCreate(accountId: $accountId, currency: $currency) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopifyPaymentsPayoutAlternateCurrencyCreate: ShopifyPaymentsPayoutAlternateCurrencyCreatePayload }>(gql, args);
  return data.shopifyPaymentsPayoutAlternateCurrencyCreate;
}

/** Creates staged upload targets for file uploads such as images, videos, and 3D models. */
export interface StagedUploadsCreateArgs {
  input: StagedUploadInput[];
}

export async function stagedUploadsCreate(args: StagedUploadsCreateArgs): Promise<StagedUploadsCreatePayload> {
  const gql = `#graphql
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ stagedUploadsCreate: StagedUploadsCreatePayload }>(gql, args);
  return data.stagedUploadsCreate;
}

/** Deprecated. Use [stagedUploadsCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/stagedUploadsCreate) instead. */
export interface StagedUploadTargetGenerateArgs {
  input: StagedUploadTargetGenerateInput;
}

export async function stagedUploadTargetGenerate(args: StagedUploadTargetGenerateArgs): Promise<StagedUploadTargetGeneratePayload> {
  const gql = `#graphql
    mutation stagedUploadTargetGenerate($input: StagedUploadTargetGenerateInput!) {
      stagedUploadTargetGenerate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ stagedUploadTargetGenerate: StagedUploadTargetGeneratePayload }>(gql, args);
  return data.stagedUploadTargetGenerate;
}

/** Deprecated. Use [stagedUploadsCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/stagedUploadsCreate) instead. */
export interface StagedUploadTargetsGenerateArgs {
  input: StageImageInput[];
}

export async function stagedUploadTargetsGenerate(args: StagedUploadTargetsGenerateArgs): Promise<StagedUploadTargetsGeneratePayload> {
  const gql = `#graphql
    mutation stagedUploadTargetsGenerate($input: [StageImageInput!]!) {
      stagedUploadTargetsGenerate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ stagedUploadTargetsGenerate: StagedUploadTargetsGeneratePayload }>(gql, args);
  return data.stagedUploadTargetsGenerate;
}

/** Adds tags to a resource. If the resource type doesn't support tagging, the `id` argument returns a resource-not-found error. */
export interface TagsAddArgs {
  id: string;
  tags: string[];
}

export async function tagsAdd(args: TagsAddArgs): Promise<TagsAddPayload> {
  const gql = `#graphql
    mutation tagsAdd($id: ID!, $tags: [String!]!) {
      tagsAdd(id: $id, tags: $tags) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ tagsAdd: TagsAddPayload }>(gql, args);
  return data.tagsAdd;
}

/** Removes tags from a resource. If the resource type doesn't support tagging, the `id` argument returns a resource-not-found error. */
export interface TagsRemoveArgs {
  id: string;
  tags: string[];
}

export async function tagsRemove(args: TagsRemoveArgs): Promise<TagsRemovePayload> {
  const gql = `#graphql
    mutation tagsRemove($id: ID!, $tags: [String!]!) {
      tagsRemove(id: $id, tags: $tags) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ tagsRemove: TagsRemovePayload }>(gql, args);
  return data.tagsRemove;
}

/** Creates a [`DelegateAccessToken`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DelegateAccessToken) with a subset of the parent token's permissions. */
export interface DelegateAccessTokenCreateArgs {
  input: DelegateAccessTokenInput;
}

export async function delegateAccessTokenCreate(args: DelegateAccessTokenCreateArgs): Promise<DelegateAccessTokenCreatePayload> {
  const gql = `#graphql
    mutation delegateAccessTokenCreate($input: DelegateAccessTokenInput!) {
      delegateAccessTokenCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ delegateAccessTokenCreate: DelegateAccessTokenCreatePayload }>(gql, args);
  return data.delegateAccessTokenCreate;
}

/** Destroys a delegate access token. */
export interface DelegateAccessTokenDestroyArgs {
  accessToken: string;
}

export async function delegateAccessTokenDestroy(args: DelegateAccessTokenDestroyArgs): Promise<DelegateAccessTokenDestroyPayload> {
  const gql = `#graphql
    mutation delegateAccessTokenDestroy($accessToken: String!) {
      delegateAccessTokenDestroy(accessToken: $accessToken) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ delegateAccessTokenDestroy: DelegateAccessTokenDestroyPayload }>(gql, args);
  return data.delegateAccessTokenDestroy;
}

/** Requires `write_privacy_settings` access scope. */
export interface DataSaleOptOutArgs {
  email: string;
}

export async function dataSaleOptOut(args: DataSaleOptOutArgs): Promise<DataSaleOptOutPayload> {
  const gql = `#graphql
    mutation dataSaleOptOut($email: String!) {
      dataSaleOptOut(email: $email) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ dataSaleOptOut: DataSaleOptOutPayload }>(gql, args);
  return data.dataSaleOptOut;
}

/** Requires `write_taxes` access scope. Also: The caller must be a tax calculations app. */
export interface TaxAppConfigureArgs {
  ready: boolean;
}

export async function taxAppConfigure(args: TaxAppConfigureArgs): Promise<TaxAppConfigurePayload> {
  const gql = `#graphql
    mutation taxAppConfigure($ready: Boolean!) {
      taxAppConfigure(ready: $ready) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ taxAppConfigure: TaxAppConfigurePayload }>(gql, args);
  return data.taxAppConfigure;
}

/** Requires `write_taxes` access scope. Also: The caller must be a tax calculations app and the relevant feature must be on. */
export interface TaxSummaryCreateArgs {
  endTime?: string;
  orderId?: string;
  startTime?: string;
}

export async function taxSummaryCreate(args?: TaxSummaryCreateArgs): Promise<TaxSummaryCreatePayload> {
  const gql = `#graphql
    mutation taxSummaryCreate($endTime: DateTime, $orderId: ID, $startTime: DateTime) {
      taxSummaryCreate(endTime: $endTime, orderId: $orderId, startTime: $startTime) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ taxSummaryCreate: TaxSummaryCreatePayload }>(gql, args);
  return data.taxSummaryCreate;
}

/** Requires `write_privacy_settings` access scope. */
export interface PrivacyFeaturesDisableArgs {
  featuresToDisable: PrivacyFeaturesEnum[];
}

export async function privacyFeaturesDisable(args: PrivacyFeaturesDisableArgs): Promise<PrivacyFeaturesDisablePayload> {
  const gql = `#graphql
    mutation privacyFeaturesDisable($featuresToDisable: [PrivacyFeaturesEnum!]!) {
      privacyFeaturesDisable(featuresToDisable: $featuresToDisable) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ privacyFeaturesDisable: PrivacyFeaturesDisablePayload }>(gql, args);
  return data.privacyFeaturesDisable;
}

/** Requires User session and api client must be valid. */
export async function financeAppAccessPolicy(): Promise<BankingFinanceAppAccess[]> {
  const gql = `#graphql
    query financeAppAccessPolicy {
      financeAppAccessPolicy {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ financeAppAccessPolicy: BankingFinanceAppAccess[] }>(gql);
  return data.financeAppAccessPolicy;
}

/** Returns Know Your Customer (KYC) information for the shop's Shopify Payments account. KYC data includes verified identity and business details collected during onboarding. This is primarily used by embedded finance apps (e.g., Shopify Balance, Bill Pay) that need to verify the... */
export async function financeKycInformation(): Promise<ShopifyPaymentsMerchantCategoryCode | null> {
  const gql = `#graphql
    query financeKycInformation {
      financeKycInformation {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ financeKycInformation: ShopifyPaymentsMerchantCategoryCode | null }>(gql);
  return data.financeKycInformation;
}

