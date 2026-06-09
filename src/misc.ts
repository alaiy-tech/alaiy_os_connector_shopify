import { shopifyClient } from './client';
import type { BusinessEntity, BusinessEntityAddress, CartTransformConnection, CartTransformCreatePayload, CartTransformDeletePayload, Domain, Job, MetafieldInput, MobilePlatformApplicationConnection, MobilePlatformApplicationCreateInput, MobilePlatformApplicationCreatePayload, MobilePlatformApplicationDeletePayload, MobilePlatformApplicationUpdateInput, MobilePlatformApplicationUpdatePayload, Node, Order, Shop, ShopPayPaymentRequestReceiptConnection, ShopPayPaymentRequestReceiptsSortKeys, StorefrontAccessTokenCreatePayload, StorefrontAccessTokenDeleteInput, StorefrontAccessTokenDeletePayload, StorefrontAccessTokenInput, Validation, ValidationConnection, ValidationCreateInput, ValidationCreatePayload, ValidationDeletePayload, ValidationSortKeys, ValidationUpdateInput, ValidationUpdatePayload } from './types';

// ============================================================
// Miscellaneous
// 23 operations
// ============================================================

/** Returns a specific node (any object that implements the [Node](https://shopify.dev/api/admin-graphql/latest/interfaces/Node) interface) by ID, in accordance with the [Relay specification](https://relay.dev/docs/guides/graphql-server-specification/#object-identification). This ... */
export interface NodeArgs {
  id: string;
}

export async function node(args: NodeArgs): Promise<Node | null> {
  const gql = `#graphql
    query node($id: ID!) {
      node(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ node: Node | null }>(gql, args);
  return data.node;
}

/** Returns the list of nodes (any objects that implement the [Node](https://shopify.dev/api/admin-graphql/latest/interfaces/Node) interface) with the given IDs, in accordance with the [Relay specification](https://relay.dev/docs/guides/graphql-server-specification/#object-identif... */
export interface NodesArgs {
  ids: string[];
}

export async function nodes(args: NodesArgs): Promise<Node | null[]> {
  const gql = `#graphql
    query nodes($ids: [ID!]!) {
      nodes(ids: $ids) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ nodes: Node | null[] }>(gql, args);
  return data.nodes;
}

/** Returns a Job resource by ID. Used to check the status of internal jobs and any applicable changes. */
export interface JobArgs {
  id: string;
}

export async function job(args: JobArgs): Promise<Job | null> {
  const gql = `#graphql
    query job($id: ID!) {
      job(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ job: Job | null }>(gql, args);
  return data.job;
}

/** Returns a `Domain` resource by ID. */
export interface DomainArgs {
  id: string;
}

export async function domain(args: DomainArgs): Promise<Domain | null> {
  const gql = `#graphql
    query domain($id: ID!) {
      domain(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ domain: Domain | null }>(gql, args);
  return data.domain;
}

/** Requires `read_mobile_platform_applications` access scope. Please contact Shopify Support to enable this scope for your app. */
export interface MobilePlatformApplicationArgs {
  id: string;
}

export async function mobilePlatformApplication(args: MobilePlatformApplicationArgs): Promise<string> {
  const gql = `#graphql
    query mobilePlatformApplication($id: ID!) {
      mobilePlatformApplication(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ mobilePlatformApplication: string }>(gql, args);
  return data.mobilePlatformApplication;
}

/** Requires `read_mobile_platform_applications` access scope. Please contact Shopify Support to enable this scope for your app. */
export interface MobilePlatformApplicationsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function mobilePlatformApplications(args?: MobilePlatformApplicationsArgs): Promise<MobilePlatformApplicationConnection> {
  const gql = `#graphql
    query mobilePlatformApplications($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      mobilePlatformApplications(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ mobilePlatformApplications: MobilePlatformApplicationConnection }>(gql, args);
  return data.mobilePlatformApplications;
}

/** Requires `write_mobile_platform_applications` access scope. Please contact Shopify Support to enable this scope for your app. */
export interface MobilePlatformApplicationCreateArgs {
  input: MobilePlatformApplicationCreateInput;
}

export async function mobilePlatformApplicationCreate(args: MobilePlatformApplicationCreateArgs): Promise<MobilePlatformApplicationCreatePayload> {
  const gql = `#graphql
    mutation mobilePlatformApplicationCreate($input: MobilePlatformApplicationCreateInput!) {
      mobilePlatformApplicationCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ mobilePlatformApplicationCreate: MobilePlatformApplicationCreatePayload }>(gql, args);
  return data.mobilePlatformApplicationCreate;
}

/** Requires `write_mobile_platform_applications` access scope. Please contact Shopify Support to enable this scope for your app. */
export interface MobilePlatformApplicationDeleteArgs {
  id: string;
}

export async function mobilePlatformApplicationDelete(args: MobilePlatformApplicationDeleteArgs): Promise<MobilePlatformApplicationDeletePayload> {
  const gql = `#graphql
    mutation mobilePlatformApplicationDelete($id: ID!) {
      mobilePlatformApplicationDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ mobilePlatformApplicationDelete: MobilePlatformApplicationDeletePayload }>(gql, args);
  return data.mobilePlatformApplicationDelete;
}

/** Requires `write_mobile_platform_applications` access scope. Please contact Shopify Support to enable this scope for your app. */
export interface MobilePlatformApplicationUpdateArgs {
  id: string;
  input: MobilePlatformApplicationUpdateInput;
}

export async function mobilePlatformApplicationUpdate(args: MobilePlatformApplicationUpdateArgs): Promise<MobilePlatformApplicationUpdatePayload> {
  const gql = `#graphql
    mutation mobilePlatformApplicationUpdate($id: ID!, $input: MobilePlatformApplicationUpdateInput!) {
      mobilePlatformApplicationUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ mobilePlatformApplicationUpdate: MobilePlatformApplicationUpdatePayload }>(gql, args);
  return data.mobilePlatformApplicationUpdate;
}

/** Requires `write_cart_transforms` access scope. Also: The shop must have [upgraded to Checkout Extensibility](https://help.shopify.com/manual/checkout-settings/checkout-extensibility/checkout-upgrade) and the user must have [products and preferences permission](https://help.sho... */
export interface CartTransformCreateArgs {
  blockOnFailure?: boolean;
  functionHandle?: string;
  metafields?: MetafieldInput[];
  functionId?: string;
}

export async function cartTransformCreate(args?: CartTransformCreateArgs): Promise<CartTransformCreatePayload> {
  const gql = `#graphql
    mutation cartTransformCreate($blockOnFailure: Boolean, $functionHandle: String, $metafields: [MetafieldInput!]!, $functionId: String) {
      cartTransformCreate(blockOnFailure: $blockOnFailure, functionHandle: $functionHandle, metafields: $metafields, functionId: $functionId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cartTransformCreate: CartTransformCreatePayload }>(gql, args);
  return data.cartTransformCreate;
}

/** Requires `write_cart_transforms` access scope. Also: The user must have products and preferences permission to delete a cart transform function. */
export interface CartTransformDeleteArgs {
  id: string;
}

export async function cartTransformDelete(args: CartTransformDeleteArgs): Promise<CartTransformDeletePayload> {
  const gql = `#graphql
    mutation cartTransformDelete($id: ID!) {
      cartTransformDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cartTransformDelete: CartTransformDeletePayload }>(gql, args);
  return data.cartTransformDelete;
}

/** Requires `read_cart_transforms` access scope. */
export interface CartTransformsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function cartTransforms(args?: CartTransformsArgs): Promise<CartTransformConnection> {
  const gql = `#graphql
    query cartTransforms($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      cartTransforms(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cartTransforms: CartTransformConnection }>(gql, args);
  return data.cartTransforms;
}

/** Creates a storefront access token that delegates unauthenticated access scopes to clients using the [Storefront API](https://shopify.dev/docs/api/storefront). The token provides public access to storefront resources without requiring customer authentication. */
export interface StorefrontAccessTokenCreateArgs {
  input: StorefrontAccessTokenInput;
}

export async function storefrontAccessTokenCreate(args: StorefrontAccessTokenCreateArgs): Promise<StorefrontAccessTokenCreatePayload> {
  const gql = `#graphql
    mutation storefrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
      storefrontAccessTokenCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ storefrontAccessTokenCreate: StorefrontAccessTokenCreatePayload }>(gql, args);
  return data.storefrontAccessTokenCreate;
}

/** Deletes a storefront access token. */
export interface StorefrontAccessTokenDeleteArgs {
  input: StorefrontAccessTokenDeleteInput;
}

export async function storefrontAccessTokenDelete(args: StorefrontAccessTokenDeleteArgs): Promise<StorefrontAccessTokenDeletePayload> {
  const gql = `#graphql
    mutation storefrontAccessTokenDelete($input: StorefrontAccessTokenDeleteInput!) {
      storefrontAccessTokenDelete(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ storefrontAccessTokenDelete: StorefrontAccessTokenDeletePayload }>(gql, args);
  return data.storefrontAccessTokenDelete;
}

/** Returns a single Shop Pay payment request receipt by its ID. Payment request receipts document completed Shop Pay transactions, including the amount, customer details, and payment status. Use this to look up a specific Shop Pay transaction for order reconciliation or customer ... */
export interface ShopPayPaymentRequestReceiptArgs {
  token: string;
}

export async function shopPayPaymentRequestReceipt(args: ShopPayPaymentRequestReceiptArgs): Promise<Order | null> {
  const gql = `#graphql
    query shopPayPaymentRequestReceipt($token: String!) {
      shopPayPaymentRequestReceipt(token: $token) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopPayPaymentRequestReceipt: Order | null }>(gql, args);
  return data.shopPayPaymentRequestReceipt;
}

/** Returns a paginated list of Shop Pay payment request receipts for the shop. Each receipt documents a completed Shop Pay transaction. Use this to review Shop Pay transaction history, generate reports, or audit Shop Pay payment activity. */
export interface ShopPayPaymentRequestReceiptsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: ShopPayPaymentRequestReceiptsSortKeys;
}

export async function shopPayPaymentRequestReceipts(args?: ShopPayPaymentRequestReceiptsArgs): Promise<ShopPayPaymentRequestReceiptConnection | null> {
  const gql = `#graphql
    query shopPayPaymentRequestReceipts($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: ShopPayPaymentRequestReceiptsSortKeys) {
      shopPayPaymentRequestReceipts(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shopPayPaymentRequestReceipts: ShopPayPaymentRequestReceiptConnection | null }>(gql, args);
  return data.shopPayPaymentRequestReceipts;
}

/** Requires `read_validations` access scope. */
export interface ValidationArgs {
  id: string;
}

export async function validation(args: ValidationArgs): Promise<Validation | null> {
  const gql = `#graphql
    query validation($id: ID!) {
      validation(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ validation: Validation | null }>(gql, args);
  return data.validation;
}

/** Requires `read_validations` access scope. */
export interface ValidationsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
  sortKey?: ValidationSortKeys;
}

export async function validations(args?: ValidationsArgs): Promise<ValidationConnection> {
  const gql = `#graphql
    query validations($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean, $sortKey: ValidationSortKeys) {
      validations(after: $after, before: $before, first: $first, last: $last, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ validations: ValidationConnection }>(gql, args);
  return data.validations;
}

/** Requires `write_validations` access scope. */
export interface ValidationCreateArgs {
  validation: ValidationCreateInput;
}

export async function validationCreate(args: ValidationCreateArgs): Promise<ValidationCreatePayload> {
  const gql = `#graphql
    mutation validationCreate($validation: ValidationCreateInput!) {
      validationCreate(validation: $validation) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ validationCreate: ValidationCreatePayload }>(gql, args);
  return data.validationCreate;
}

/** Requires `write_validations` access scope. */
export interface ValidationDeleteArgs {
  id: string;
}

export async function validationDelete(args: ValidationDeleteArgs): Promise<ValidationDeletePayload> {
  const gql = `#graphql
    mutation validationDelete($id: ID!) {
      validationDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ validationDelete: ValidationDeletePayload }>(gql, args);
  return data.validationDelete;
}

/** Requires `write_validations` access scope. */
export interface ValidationUpdateArgs {
  id: string;
  validation: ValidationUpdateInput;
}

export async function validationUpdate(args: ValidationUpdateArgs): Promise<ValidationUpdatePayload> {
  const gql = `#graphql
    mutation validationUpdate($id: ID!, $validation: ValidationUpdateInput!) {
      validationUpdate(id: $id, validation: $validation) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ validationUpdate: ValidationUpdatePayload }>(gql, args);
  return data.validationUpdate;
}

/** Returns the list of [business entities](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessEntity) associated with the shop. Use this query to retrieve business entities for assigning to markets, managing payment providers per entity, or viewing entity attributi... */
export async function businessEntities(): Promise<BusinessEntityAddress> {
  const gql = `#graphql
    query businessEntities {
      businessEntities {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ businessEntities: BusinessEntityAddress }>(gql);
  return data.businessEntities;
}

/** Returns a Business Entity by ID. */
export interface BusinessEntityArgs {
  id?: string;
}

export async function businessEntity(args?: BusinessEntityArgs): Promise<BusinessEntityAddress> {
  const gql = `#graphql
    query businessEntity($id: ID) {
      businessEntity(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ businessEntity: BusinessEntityAddress }>(gql, args);
  return data.businessEntity;
}

