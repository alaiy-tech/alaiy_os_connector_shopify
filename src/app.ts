import { shopifyClient } from './client';
import type { AccessScope, App, AppDiscountTypeConnection, AppInstallation, AppInstallationCategory, AppInstallationConnection, AppInstallationPrivacy, AppInstallationSortKeys, AppPurchaseOneTimeCreatePayload, AppRevokeAccessScopesPayload, AppSubscription, AppSubscriptionCancelPayload, AppSubscriptionCreatePayload, AppSubscriptionLineItem, AppSubscriptionLineItemInput, AppSubscriptionLineItemUpdatePayload, AppSubscriptionReplacementBehavior, AppSubscriptionTrialExtendPayload, AppUninstallPayload, AppUsageRecordCreatePayload, MoneyInput } from './types';

// ============================================================
// App Management
// 17 operations
// ============================================================

/** Retrieves an [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) by its ID. If no ID is provided, returns details about the currently authenticated app. The query provides access to app details including title, icon, and pricing information. */
export interface AppArgs {
  id?: string;
}

export async function app(args?: AppArgs): Promise<App | null> {
  const gql = `#graphql
    query app($id: ID) {
      app(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ app: App | null }>(gql, args);
  return data.app;
}

/** Retrieves an app by its unique handle. The handle is a URL-friendly identifier for the app. */
export interface AppByHandleArgs {
  handle: string;
}

export async function appByHandle(args: AppByHandleArgs): Promise<App | null> {
  const gql = `#graphql
    query appByHandle($handle: String!) {
      appByHandle(handle: $handle) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appByHandle: App | null }>(gql, args);
  return data.appByHandle;
}

/** Retrieves an [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) by its client ID (API key). Returns the app's configuration, installation status, [`AccessScope`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope) objects, and developer i... */
export interface AppByKeyArgs {
  apiKey: string;
}

export async function appByKey(args: AppByKeyArgs): Promise<App | null> {
  const gql = `#graphql
    query appByKey($apiKey: String!) {
      appByKey(apiKey: $apiKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appByKey: App | null }>(gql, args);
  return data.appByKey;
}

/** Requires Apps must have `read_discounts` access scope. */
export interface AppDiscountTypeArgs {
  functionId: string;
}

export async function appDiscountType(args: AppDiscountTypeArgs): Promise<App> {
  const gql = `#graphql
    query appDiscountType($functionId: String!) {
      appDiscountType(functionId: $functionId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appDiscountType: App }>(gql, args);
  return data.appDiscountType;
}

/** Requires Apps must have `read_discounts` access scope. */
export async function appDiscountTypes(): Promise<App> {
  const gql = `#graphql
    query appDiscountTypes {
      appDiscountTypes {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appDiscountTypes: App }>(gql);
  return data.appDiscountTypes;
}

/** A list of app discount types installed by apps. */
export interface AppDiscountTypesNodesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function appDiscountTypesNodes(args?: AppDiscountTypesNodesArgs): Promise<AppDiscountTypeConnection> {
  const gql = `#graphql
    query appDiscountTypesNodes($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      appDiscountTypesNodes(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appDiscountTypesNodes: AppDiscountTypeConnection }>(gql, args);
  return data.appDiscountTypesNodes;
}

/** Retrieves an [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation) by ID. If no ID is provided, returns the installation for the currently authenticated [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App). The query p... */
export interface AppInstallationArgs {
  id?: string;
}

export async function appInstallation(args?: AppInstallationArgs): Promise<number | null> {
  const gql = `#graphql
    query appInstallation($id: ID) {
      appInstallation(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appInstallation: number | null }>(gql, args);
  return data.appInstallation;
}

/** A paginated list of [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation) objects across multiple stores where your app is installed. Use this query to monitor installation status, track billing and subscriptions through [`AppSubscripti... */
export interface AppInstallationsArgs {
  after?: string;
  before?: string;
  category?: AppInstallationCategory;
  first?: number;
  last?: number;
  privacy?: AppInstallationPrivacy;
  reverse?: boolean;
  sortKey?: AppInstallationSortKeys;
}

export async function appInstallations(args?: AppInstallationsArgs): Promise<AppInstallationConnection> {
  const gql = `#graphql
    query appInstallations($after: String, $before: String, $category: AppInstallationCategory, $first: Int, $last: Int, $privacy: AppInstallationPrivacy, $reverse: Boolean, $sortKey: AppInstallationSortKeys) {
      appInstallations(after: $after, before: $before, category: $category, first: $first, last: $last, privacy: $privacy, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appInstallations: AppInstallationConnection }>(gql, args);
  return data.appInstallations;
}

/** Returns the [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation) for the currently authenticated app. Provides access to granted access scopes, active [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSub... */
export async function currentAppInstallation(): Promise<number | null> {
  const gql = `#graphql
    query currentAppInstallation {
      currentAppInstallation {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ currentAppInstallation: number | null }>(gql);
  return data.currentAppInstallation;
}

/** Creates a one-time charge for app features or services that don't require recurring billing. This mutation is ideal for apps that sell individual features, premium content, or services on a per-use basis rather than subscription models. */
export interface AppPurchaseOneTimeCreateArgs {
  name: string;
  price: MoneyInput;
  returnUrl: string;
  test?: boolean;
}

export async function appPurchaseOneTimeCreate(args: AppPurchaseOneTimeCreateArgs): Promise<AppPurchaseOneTimeCreatePayload> {
  const gql = `#graphql
    mutation appPurchaseOneTimeCreate($name: String!, $price: MoneyInput!, $returnUrl: URL!, $test: Boolean) {
      appPurchaseOneTimeCreate(name: $name, price: $price, returnUrl: $returnUrl, test: $test) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appPurchaseOneTimeCreate: AppPurchaseOneTimeCreatePayload }>(gql, args);
  return data.appPurchaseOneTimeCreate;
}

/** Requires This mutation can only be run on the current app. */
export interface AppRevokeAccessScopesArgs {
  scopes: string[];
}

export async function appRevokeAccessScopes(args: AppRevokeAccessScopesArgs): Promise<AppRevokeAccessScopesPayload> {
  const gql = `#graphql
    mutation appRevokeAccessScopes($scopes: [String!]!) {
      appRevokeAccessScopes(scopes: $scopes) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appRevokeAccessScopes: AppRevokeAccessScopesPayload }>(gql, args);
  return data.appRevokeAccessScopes;
}

/** Cancels an active app subscription, stopping future billing cycles. The cancellation behavior depends on the `replacementBehavior` setting - it can either disable auto-renewal (allowing the subscription to continue until the end of the current billing period) or immediately ca... */
export interface AppSubscriptionCancelArgs {
  id: string;
  prorate?: boolean;
}

export async function appSubscriptionCancel(args: AppSubscriptionCancelArgs): Promise<AppSubscriptionCancelPayload> {
  const gql = `#graphql
    mutation appSubscriptionCancel($id: ID!, $prorate: Boolean) {
      appSubscriptionCancel(id: $id, prorate: $prorate) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appSubscriptionCancel: AppSubscriptionCancelPayload }>(gql, args);
  return data.appSubscriptionCancel;
}

/** Creates a recurring or usage-based [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription) that charges merchants for app features and services. The subscription includes one or more [`AppSubscriptionLineItem`](https://shopify.dev/docs/ap... */
export interface AppSubscriptionCreateArgs {
  lineItems: AppSubscriptionLineItemInput[];
  name: string;
  replacementBehavior?: AppSubscriptionReplacementBehavior;
  returnUrl: string;
  test?: boolean;
  trialDays?: number;
}

export async function appSubscriptionCreate(args: AppSubscriptionCreateArgs): Promise<AppSubscriptionCreatePayload> {
  const gql = `#graphql
    mutation appSubscriptionCreate($lineItems: [AppSubscriptionLineItemInput!]!, $name: String!, $replacementBehavior: AppSubscriptionReplacementBehavior, $returnUrl: URL!, $test: Boolean, $trialDays: Int) {
      appSubscriptionCreate(lineItems: $lineItems, name: $name, replacementBehavior: $replacementBehavior, returnUrl: $returnUrl, test: $test, trialDays: $trialDays) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appSubscriptionCreate: AppSubscriptionCreatePayload }>(gql, args);
  return data.appSubscriptionCreate;
}

/** Updates the capped amount on usage-based billing for an [`AppSubscriptionLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscriptionLineItem). Enables you to modify the maximum charge limit that prevents merchants from exceeding a specified threshold d... */
export interface AppSubscriptionLineItemUpdateArgs {
  cappedAmount: MoneyInput;
  id: string;
}

export async function appSubscriptionLineItemUpdate(args: AppSubscriptionLineItemUpdateArgs): Promise<AppSubscriptionLineItemUpdatePayload> {
  const gql = `#graphql
    mutation appSubscriptionLineItemUpdate($cappedAmount: MoneyInput!, $id: ID!) {
      appSubscriptionLineItemUpdate(cappedAmount: $cappedAmount, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appSubscriptionLineItemUpdate: AppSubscriptionLineItemUpdatePayload }>(gql, args);
  return data.appSubscriptionLineItemUpdate;
}

/** Requires This must be a third party developed application that you can access. */
export interface AppSubscriptionTrialExtendArgs {
  days: number;
  id: string;
}

export async function appSubscriptionTrialExtend(args: AppSubscriptionTrialExtendArgs): Promise<AppSubscriptionTrialExtendPayload> {
  const gql = `#graphql
    mutation appSubscriptionTrialExtend($days: Int!, $id: ID!) {
      appSubscriptionTrialExtend(days: $days, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appSubscriptionTrialExtend: AppSubscriptionTrialExtendPayload }>(gql, args);
  return data.appSubscriptionTrialExtend;
}

/** Requires This mutation can only be used by apps to uninstall themselves. */
export async function appUninstall(): Promise<AppUninstallPayload> {
  const gql = `#graphql
    mutation appUninstall {
      appUninstall {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appUninstall: AppUninstallPayload }>(gql);
  return data.appUninstall;
}

/** Creates a usage charge for an app subscription with usage-based pricing. The charge counts toward the capped amount limit set when creating the subscription. */
export interface AppUsageRecordCreateArgs {
  description: string;
  idempotencyKey?: string;
  price: MoneyInput;
  subscriptionLineItemId: string;
}

export async function appUsageRecordCreate(args: AppUsageRecordCreateArgs): Promise<AppUsageRecordCreatePayload> {
  const gql = `#graphql
    mutation appUsageRecordCreate($description: String!, $idempotencyKey: String, $price: MoneyInput!, $subscriptionLineItemId: ID!) {
      appUsageRecordCreate(description: $description, idempotencyKey: $idempotencyKey, price: $price, subscriptionLineItemId: $subscriptionLineItemId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ appUsageRecordCreate: AppUsageRecordCreatePayload }>(gql, args);
  return data.appUsageRecordCreate;
}

