import { shopifyClient } from './client';
import type { AbandonedCheckoutConnection, AbandonedCheckoutSortKeys, Abandonment, AbandonmentDeliveryState, AbandonmentEmailState, AbandonmentEmailStateUpdatePayload, AbandonmentUpdateActivitiesDeliveryStatusesPayload, AutomaticDiscountSortKeys, Catalog, CodeDiscountSortKeys, Count, DiscountAutomatic, DiscountAutomaticActivatePayload, DiscountAutomaticAppCreatePayload, DiscountAutomaticAppInput, DiscountAutomaticAppUpdatePayload, DiscountAutomaticBasicCreatePayload, DiscountAutomaticBasicInput, DiscountAutomaticBasicUpdatePayload, DiscountAutomaticBulkDeletePayload, DiscountAutomaticBxgyCreatePayload, DiscountAutomaticBxgyInput, DiscountAutomaticBxgyUpdatePayload, DiscountAutomaticConnection, DiscountAutomaticDeactivatePayload, DiscountAutomaticDeletePayload, DiscountAutomaticFreeShippingCreatePayload, DiscountAutomaticFreeShippingInput, DiscountAutomaticFreeShippingUpdatePayload, DiscountAutomaticNode, DiscountAutomaticNodeConnection, DiscountBulkTagsAddPayload, DiscountBulkTagsRemovePayload, DiscountCodeActivatePayload, DiscountCodeAppCreatePayload, DiscountCodeAppInput, DiscountCodeAppUpdatePayload, DiscountCodeBasicCreatePayload, DiscountCodeBasicInput, DiscountCodeBasicUpdatePayload, DiscountCodeBulkActivatePayload, DiscountCodeBulkDeactivatePayload, DiscountCodeBulkDeletePayload, DiscountCodeBxgyCreatePayload, DiscountCodeBxgyInput, DiscountCodeBxgyUpdatePayload, DiscountCodeDeactivatePayload, DiscountCodeDeletePayload, DiscountCodeFreeShippingCreatePayload, DiscountCodeFreeShippingInput, DiscountCodeFreeShippingUpdatePayload, DiscountCodeNode, DiscountCodeNodeConnection, DiscountCodeRedeemCodeBulkDeletePayload, DiscountCodeSortKeys, DiscountNode, DiscountNodeConnection, DiscountRedeemCode, DiscountRedeemCodeBulkAddPayload, DiscountRedeemCodeBulkCreation, DiscountSortKeys, DiscountTagSortKeys, MarketingActivitiesDeleteAllExternalPayload, MarketingActivity, MarketingActivityConnection, MarketingActivityCreateExternalInput, MarketingActivityCreateExternalPayload, MarketingActivityCreateInput, MarketingActivityCreatePayload, MarketingActivityDeleteExternalPayload, MarketingActivitySortKeys, MarketingActivityUpdateExternalInput, MarketingActivityUpdateExternalPayload, MarketingActivityUpdateInput, MarketingActivityUpdatePayload, MarketingActivityUpsertExternalInput, MarketingActivityUpsertExternalPayload, MarketingEngagementCreatePayload, MarketingEngagementInput, MarketingEngagementsDeletePayload, MarketingEvent, MarketingEventConnection, MarketingEventSortKeys, PriceList, PriceListConnection, PriceListCreateInput, PriceListCreatePayload, PriceListDeletePayload, PriceListFixedPricesAddPayload, PriceListFixedPricesByProductUpdatePayload, PriceListFixedPricesDeletePayload, PriceListFixedPricesUpdatePayload, PriceListPrice, PriceListSortKeys, PriceListUpdateInput, PriceListUpdatePayload, Product, ProductVariant, QuantityPricingByVariantUpdateInput, QuantityPricingByVariantUpdatePayload, QuantityRulesAddPayload, QuantityRulesDeletePayload, SavedSearchConnection, StringConnection, UTMInput } from './types';

// ============================================================
// Discounts & Marketing
// 77 operations: 26 queries, 51 mutations
// ============================================================

// These are passed as plain objects. See Shopify docs for field shapes:

// ─── Queries ─────────────────────────────────────────────────────────

/**
 * Returns a list of abandoned checkouts. A checkout is considered abandoned when a customer adds contact information but doesn't complete their purchase. Includes both abandoned and recovered checkouts.
 */
export interface AbandonedCheckoutsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: AbandonedCheckoutSortKeys;
}

export async function abandonedCheckouts(args?: AbandonedCheckoutsArgs): Promise<AbandonedCheckoutConnection> {
  const gql = `#graphql
    query abandonedCheckouts($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: AbandonedCheckoutSortKeys) {
      abandonedCheckouts(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ abandonedCheckouts: AbandonedCheckoutConnection }>(gql, args);
  return data.abandonedCheckouts;
}

/**
 * Returns the count of abandoned checkouts for the given shop. Limited to a maximum of 10000 by default.
 * @scope read_orders
 */
export interface AbandonedCheckoutsCountArgs {
  limit?: number;
  query?: string;
  savedSearchId?: string;
}

export async function abandonedCheckoutsCount(args?: AbandonedCheckoutsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query abandonedCheckoutsCount($limit: Int, $query: String, $savedSearchId: ID) {
      abandonedCheckoutsCount(limit: $limit, query: $query, savedSearchId: $savedSearchId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ abandonedCheckoutsCount: Count | null }>(gql, args);
  return data.abandonedCheckoutsCount;
}

/**
 * Returns a Abandonment resource by ID.
 */
export interface AbandonmentArgs {
  id: string;
}

export async function abandonment(args: AbandonmentArgs): Promise<Abandonment | null> {
  const gql = `#graphql
    query abandonment($id: ID!) {
      abandonment(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ abandonment: Abandonment | null }>(gql, args);
  return data.abandonment;
}

/**
 * Returns an Abandonment by the Abandoned Checkout ID.
 */
export interface AbandonmentByAbandonedCheckoutIdArgs {
  abandonedCheckoutId: string;
}

export async function abandonmentByAbandonedCheckoutId(args: AbandonmentByAbandonedCheckoutIdArgs): Promise<Abandonment | null> {
  const gql = `#graphql
    query abandonmentByAbandonedCheckoutId($abandonedCheckoutId: ID!) {
      abandonmentByAbandonedCheckoutId(abandonedCheckoutId: $abandonedCheckoutId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ abandonmentByAbandonedCheckoutId: Abandonment | null }>(gql, args);
  return data.abandonmentByAbandonedCheckoutId;
}

/**
 * Returns a DiscountAutomatic resource by ID.
 */
export interface AutomaticDiscountArgs {
  id: string;
}

export async function automaticDiscount(args: AutomaticDiscountArgs): Promise<DiscountAutomatic | null> {
  const gql = `#graphql
    query automaticDiscount($id: ID!) {
      automaticDiscount(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ automaticDiscount: DiscountAutomatic | null }>(gql, args);
  return data.automaticDiscount;
}

/**
 * Returns a DiscountAutomaticNode resource by ID.
 */
export interface AutomaticDiscountNodeArgs {
  id: string;
}

export async function automaticDiscountNode(args: AutomaticDiscountNodeArgs): Promise<DiscountAutomaticNode | null> {
  const gql = `#graphql
    query automaticDiscountNode($id: ID!) {
      automaticDiscountNode(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ automaticDiscountNode: DiscountAutomaticNode | null }>(gql, args);
  return data.automaticDiscountNode;
}

/**
 * Returns a list of automatic discounts.
 */
export interface AutomaticDiscountNodesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: AutomaticDiscountSortKeys;
}

export async function automaticDiscountNodes(args?: AutomaticDiscountNodesArgs): Promise<DiscountAutomaticNodeConnection> {
  const gql = `#graphql
    query automaticDiscountNodes($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: AutomaticDiscountSortKeys) {
      automaticDiscountNodes(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ automaticDiscountNodes: DiscountAutomaticNodeConnection }>(gql, args);
  return data.automaticDiscountNodes;
}

/**
 * List of the shop's automatic discount saved searches.
 */
export interface AutomaticDiscountSavedSearchesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function automaticDiscountSavedSearches(args?: AutomaticDiscountSavedSearchesArgs): Promise<SavedSearchConnection> {
  const gql = `#graphql
    query automaticDiscountSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      automaticDiscountSavedSearches(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ automaticDiscountSavedSearches: SavedSearchConnection }>(gql, args);
  return data.automaticDiscountSavedSearches;
}

/**
 * Returns a list of automatic discounts that are applied in the cart and at checkout without requiring a discount code.
 */
export interface AutomaticDiscountsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: AutomaticDiscountSortKeys;
}

export async function automaticDiscounts(args?: AutomaticDiscountsArgs): Promise<DiscountAutomaticConnection> {
  const gql = `#graphql
    query automaticDiscounts($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: AutomaticDiscountSortKeys) {
      automaticDiscounts(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ automaticDiscounts: DiscountAutomaticConnection }>(gql, args);
  return data.automaticDiscounts;
}

/**
 * Returns a code discount resource by ID.
 */
export interface CodeDiscountNodeArgs {
  id: string;
}

export async function codeDiscountNode(args: CodeDiscountNodeArgs): Promise<DiscountCodeNode | null> {
  const gql = `#graphql
    query codeDiscountNode($id: ID!) {
      codeDiscountNode(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ codeDiscountNode: DiscountCodeNode | null }>(gql, args);
  return data.codeDiscountNode;
}

/**
 * Retrieves a code discount by its discount code. The search is case-insensitive, enabling you to find discounts regardless of how customers enter the code.
 */
export interface CodeDiscountNodeByCodeArgs {
  code: string;
}

export async function codeDiscountNodeByCode(args: CodeDiscountNodeByCodeArgs): Promise<DiscountCodeNode | null> {
  const gql = `#graphql
    query codeDiscountNodeByCode($code: String!) {
      codeDiscountNodeByCode(code: $code) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ codeDiscountNodeByCode: DiscountCodeNode | null }>(gql, args);
  return data.codeDiscountNodeByCode;
}

/**
 * Returns a list of code-based discounts.
 */
export interface CodeDiscountNodesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: CodeDiscountSortKeys;
}

export async function codeDiscountNodes(args?: CodeDiscountNodesArgs): Promise<DiscountCodeNodeConnection> {
  const gql = `#graphql
    query codeDiscountNodes($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: CodeDiscountSortKeys) {
      codeDiscountNodes(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ codeDiscountNodes: DiscountCodeNodeConnection }>(gql, args);
  return data.codeDiscountNodes;
}

/**
 * List of the shop's code discount saved searches.
 */
export interface CodeDiscountSavedSearchesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function codeDiscountSavedSearches(args?: CodeDiscountSavedSearchesArgs): Promise<SavedSearchConnection> {
  const gql = `#graphql
    query codeDiscountSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      codeDiscountSavedSearches(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ codeDiscountSavedSearches: SavedSearchConnection }>(gql, args);
  return data.codeDiscountSavedSearches;
}

/**
 * The total number of discount codes for the shop. Limited to a maximum of 10000 by default.
 * @scope read_discounts
 */
export interface DiscountCodesCountArgs {
  limit?: number;
  query?: string;
}

export async function discountCodesCount(args?: DiscountCodesCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query discountCodesCount($limit: Int, $query: String) {
      discountCodesCount(limit: $limit, query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodesCount: Count | null }>(gql, args);
  return data.discountCodesCount;
}

/**
 * Returns a DiscountNode resource by ID.
 */
export interface DiscountNodeArgs {
  id: string;
}

export async function discountNode(args: DiscountNodeArgs): Promise<DiscountNode | null> {
  const gql = `#graphql
    query discountNode($id: ID!) {
      discountNode(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountNode: DiscountNode | null }>(gql, args);
  return data.discountNode;
}

/**
 * Returns a list of discounts.
 */
export interface DiscountNodesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: DiscountSortKeys;
}

export async function discountNodes(args?: DiscountNodesArgs): Promise<DiscountNodeConnection> {
  const gql = `#graphql
    query discountNodes($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: DiscountSortKeys) {
      discountNodes(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountNodes: DiscountNodeConnection }>(gql, args);
  return data.discountNodes;
}

/**
 * The total number of discounts for the shop. Limited to a maximum of 10000 by default.
 * @scope read_discounts
 */
export interface DiscountNodesCountArgs {
  limit?: number;
  query?: string;
  savedSearchId?: string;
}

export async function discountNodesCount(args?: DiscountNodesCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query discountNodesCount($limit: Int, $query: String, $savedSearchId: ID) {
      discountNodesCount(limit: $limit, query: $query, savedSearchId: $savedSearchId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountNodesCount: Count | null }>(gql, args);
  return data.discountNodesCount;
}

/**
 * Returns a DiscountRedeemCodeBulkCreation resource by ID.
 */
export interface DiscountRedeemCodeBulkCreationArgs {
  id: string;
}

export async function discountRedeemCodeBulkCreation(args: DiscountRedeemCodeBulkCreationArgs): Promise<DiscountRedeemCodeBulkCreation | null> {
  const gql = `#graphql
    query discountRedeemCodeBulkCreation($id: ID!) {
      discountRedeemCodeBulkCreation(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountRedeemCodeBulkCreation: DiscountRedeemCodeBulkCreation | null }>(gql, args);
  return data.discountRedeemCodeBulkCreation;
}

/**
 * List of the shop's redeemed discount code saved searches.
 * @scope read_discounts
 */
export interface DiscountRedeemCodeSavedSearchesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: DiscountCodeSortKeys;
}

export async function discountRedeemCodeSavedSearches(args?: DiscountRedeemCodeSavedSearchesArgs): Promise<SavedSearchConnection> {
  const gql = `#graphql
    query discountRedeemCodeSavedSearches($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: DiscountCodeSortKeys) {
      discountRedeemCodeSavedSearches(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountRedeemCodeSavedSearches: SavedSearchConnection }>(gql, args);
  return data.discountRedeemCodeSavedSearches;
}

/**
 * List of tags associated to discounts.
 */
export interface DiscountTagsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: DiscountTagSortKeys;
}

export async function discountTags(args?: DiscountTagsArgs): Promise<StringConnection> {
  const gql = `#graphql
    query discountTags($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: DiscountTagSortKeys) {
      discountTags(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountTags: StringConnection }>(gql, args);
  return data.discountTags;
}

/**
 * A list of marketing activities associated with the marketing app.
 */
export interface MarketingActivitiesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  marketingActivityIds?: unknown;
  query?: string;
  remoteIds?: unknown;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: MarketingActivitySortKeys;
  utm?: UTMInput;
}

export async function marketingActivities(args?: MarketingActivitiesArgs): Promise<MarketingActivityConnection> {
  const gql = `#graphql
    query marketingActivities($after: String, $before: String, $first: Int, $last: Int, $marketingActivityIds: String, $query: String, $remoteIds: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: MarketingActivitySortKeys, $utm: UTMInput) {
      marketingActivities(after: $after, before: $before, first: $first, last: $last, marketingActivityIds: $marketingActivityIds, query: $query, remoteIds: $remoteIds, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey, utm: $utm) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingActivities: MarketingActivityConnection }>(gql, args);
  return data.marketingActivities;
}

/**
 * Returns a MarketingActivity resource by ID.
 */
export interface MarketingActivityArgs {
  id: string;
}

export async function marketingActivity(args: MarketingActivityArgs): Promise<MarketingActivity | null> {
  const gql = `#graphql
    query marketingActivity($id: ID!) {
      marketingActivity(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingActivity: MarketingActivity | null }>(gql, args);
  return data.marketingActivity;
}

/**
 * Returns a MarketingEvent resource by ID.
 */
export interface MarketingEventArgs {
  id: string;
}

export async function marketingEvent(args: MarketingEventArgs): Promise<MarketingEvent | null> {
  const gql = `#graphql
    query marketingEvent($id: ID!) {
      marketingEvent(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingEvent: MarketingEvent | null }>(gql, args);
  return data.marketingEvent;
}

/**
 * A list of marketing events associated with the marketing app.
 */
export interface MarketingEventsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: MarketingEventSortKeys;
}

export async function marketingEvents(args?: MarketingEventsArgs): Promise<MarketingEventConnection> {
  const gql = `#graphql
    query marketingEvents($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: MarketingEventSortKeys) {
      marketingEvents(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingEvents: MarketingEventConnection }>(gql, args);
  return data.marketingEvents;
}

/**
 * Returns a PriceList by ID. You can use price lists to specify either fixed prices or adjusted relative prices that override initial Product prices.
 */
export interface PriceListArgs {
  id: string;
}

export async function priceList(args: PriceListArgs): Promise<PriceList | null> {
  const gql = `#graphql
    query priceList($id: ID!) {
      priceList(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ priceList: PriceList | null }>(gql, args);
  return data.priceList;
}

/**
 * All price lists for a shop.
 */
export interface PriceListsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
  sortKey?: PriceListSortKeys;
}

export async function priceLists(args?: PriceListsArgs): Promise<PriceListConnection> {
  const gql = `#graphql
    query priceLists($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean, $sortKey: PriceListSortKeys) {
      priceLists(after: $after, before: $before, first: $first, last: $last, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ priceLists: PriceListConnection }>(gql, args);
  return data.priceLists;
}

// ─── Mutations ─────────────────────────────────────────────────────────

/**
 * Updates the email state value for an abandonment.
 * @scope write_marketing_events
 */
export interface AbandonmentEmailStateUpdateArgs {
  emailSentAt?: string;
  emailState: AbandonmentEmailState;
  emailStateChangeReason?: string;
  id: string;
}

export async function abandonmentEmailStateUpdate(args: AbandonmentEmailStateUpdateArgs): Promise<AbandonmentEmailStateUpdatePayload> {
  const gql = `#graphql
    mutation abandonmentEmailStateUpdate($emailSentAt: DateTime, $emailState: AbandonmentEmailState!, $emailStateChangeReason: String, $id: ID!) {
      abandonmentEmailStateUpdate(emailSentAt: $emailSentAt, emailState: $emailState, emailStateChangeReason: $emailStateChangeReason, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ abandonmentEmailStateUpdate: AbandonmentEmailStateUpdatePayload }>(gql, args);
  return data.abandonmentEmailStateUpdate;
}

/**
 * Updates the marketing activities delivery statuses for an abandonment.
 * @scope write_marketing_events
 */
export interface AbandonmentUpdateActivitiesDeliveryStatusesArgs {
  abandonmentId: string;
  deliveredAt?: string;
  deliveryStatus: AbandonmentDeliveryState;
  deliveryStatusChangeReason?: string;
  marketingActivityId: string;
}

export async function abandonmentUpdateActivitiesDeliveryStatuses(args: AbandonmentUpdateActivitiesDeliveryStatusesArgs): Promise<AbandonmentUpdateActivitiesDeliveryStatusesPayload> {
  const gql = `#graphql
    mutation abandonmentUpdateActivitiesDeliveryStatuses($abandonmentId: ID!, $deliveredAt: DateTime, $deliveryStatus: AbandonmentDeliveryState!, $deliveryStatusChangeReason: String, $marketingActivityId: ID!) {
      abandonmentUpdateActivitiesDeliveryStatuses(abandonmentId: $abandonmentId, deliveredAt: $deliveredAt, deliveryStatus: $deliveryStatus, deliveryStatusChangeReason: $deliveryStatusChangeReason, marketingActivityId: $marketingActivityId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ abandonmentUpdateActivitiesDeliveryStatuses: AbandonmentUpdateActivitiesDeliveryStatusesPayload }>(gql, args);
  return data.abandonmentUpdateActivitiesDeliveryStatuses;
}

/**
 * Activates an automatic discount.
 */
export interface DiscountAutomaticActivateArgs {
  id: string;
}

export async function discountAutomaticActivate(args: DiscountAutomaticActivateArgs): Promise<DiscountAutomaticActivatePayload> {
  const gql = `#graphql
    mutation discountAutomaticActivate($id: ID!) {
      discountAutomaticActivate(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticActivate: DiscountAutomaticActivatePayload }>(gql, args);
  return data.discountAutomaticActivate;
}

/**
 * Creates an automatic discount that's managed by an app.
 * @scope write_discounts
 */
export interface DiscountAutomaticAppCreateArgs {
  automaticAppDiscount: DiscountAutomaticAppInput;
}

export async function discountAutomaticAppCreate(args: DiscountAutomaticAppCreateArgs): Promise<DiscountAutomaticAppCreatePayload> {
  const gql = `#graphql
    mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
      discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticAppCreate: DiscountAutomaticAppCreatePayload }>(gql, args);
  return data.discountAutomaticAppCreate;
}

/**
 * Updates an existing automatic discount that's managed by an app using
 * @scope write_discounts
 */
export interface DiscountAutomaticAppUpdateArgs {
  automaticAppDiscount: DiscountAutomaticAppInput;
  id: string;
}

export async function discountAutomaticAppUpdate(args: DiscountAutomaticAppUpdateArgs): Promise<DiscountAutomaticAppUpdatePayload> {
  const gql = `#graphql
    mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
      discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticAppUpdate: DiscountAutomaticAppUpdatePayload }>(gql, args);
  return data.discountAutomaticAppUpdate;
}

/**
 * Creates an
 */
export interface DiscountAutomaticBasicCreateArgs {
  automaticBasicDiscount: DiscountAutomaticBasicInput;
}

export async function discountAutomaticBasicCreate(args: DiscountAutomaticBasicCreateArgs): Promise<DiscountAutomaticBasicCreatePayload> {
  const gql = `#graphql
    mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticBasicCreate: DiscountAutomaticBasicCreatePayload }>(gql, args);
  return data.discountAutomaticBasicCreate;
}

/**
 * Updates an existing
 */
export interface DiscountAutomaticBasicUpdateArgs {
  automaticBasicDiscount: DiscountAutomaticBasicInput;
  id: string;
}

export async function discountAutomaticBasicUpdate(args: DiscountAutomaticBasicUpdateArgs): Promise<DiscountAutomaticBasicUpdatePayload> {
  const gql = `#graphql
    mutation discountAutomaticBasicUpdate($automaticBasicDiscount: DiscountAutomaticBasicInput!, $id: ID!) {
      discountAutomaticBasicUpdate(automaticBasicDiscount: $automaticBasicDiscount, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticBasicUpdate: DiscountAutomaticBasicUpdatePayload }>(gql, args);
  return data.discountAutomaticBasicUpdate;
}

/**
 * Deletes multiple automatic discounts in a single operation, providing efficient bulk management for stores with extensive discount catalogs. This mutation processes deletions asynchronously to handle large volumes without blocking other operations.
 */
export interface DiscountAutomaticBulkDeleteArgs {
  ids?: unknown;
  savedSearchId?: string;
  search?: string;
}

export async function discountAutomaticBulkDelete(args?: DiscountAutomaticBulkDeleteArgs): Promise<DiscountAutomaticBulkDeletePayload> {
  const gql = `#graphql
    mutation discountAutomaticBulkDelete($ids: String, $savedSearchId: ID, $search: String) {
      discountAutomaticBulkDelete(ids: $ids, savedSearchId: $savedSearchId, search: $search) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticBulkDelete: DiscountAutomaticBulkDeletePayload }>(gql, args);
  return data.discountAutomaticBulkDelete;
}

/**
 * Creates a
 */
export interface DiscountAutomaticBxgyCreateArgs {
  automaticBxgyDiscount: DiscountAutomaticBxgyInput;
}

export async function discountAutomaticBxgyCreate(args: DiscountAutomaticBxgyCreateArgs): Promise<DiscountAutomaticBxgyCreatePayload> {
  const gql = `#graphql
    mutation discountAutomaticBxgyCreate($automaticBxgyDiscount: DiscountAutomaticBxgyInput!) {
      discountAutomaticBxgyCreate(automaticBxgyDiscount: $automaticBxgyDiscount) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticBxgyCreate: DiscountAutomaticBxgyCreatePayload }>(gql, args);
  return data.discountAutomaticBxgyCreate;
}

/**
 * Updates an existing
 */
export interface DiscountAutomaticBxgyUpdateArgs {
  automaticBxgyDiscount: DiscountAutomaticBxgyInput;
  id: string;
}

export async function discountAutomaticBxgyUpdate(args: DiscountAutomaticBxgyUpdateArgs): Promise<DiscountAutomaticBxgyUpdatePayload> {
  const gql = `#graphql
    mutation discountAutomaticBxgyUpdate($automaticBxgyDiscount: DiscountAutomaticBxgyInput!, $id: ID!) {
      discountAutomaticBxgyUpdate(automaticBxgyDiscount: $automaticBxgyDiscount, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticBxgyUpdate: DiscountAutomaticBxgyUpdatePayload }>(gql, args);
  return data.discountAutomaticBxgyUpdate;
}

/**
 * Deactivates an automatic discount.
 */
export interface DiscountAutomaticDeactivateArgs {
  id: string;
}

export async function discountAutomaticDeactivate(args: DiscountAutomaticDeactivateArgs): Promise<DiscountAutomaticDeactivatePayload> {
  const gql = `#graphql
    mutation discountAutomaticDeactivate($id: ID!) {
      discountAutomaticDeactivate(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticDeactivate: DiscountAutomaticDeactivatePayload }>(gql, args);
  return data.discountAutomaticDeactivate;
}

/**
 * Deletes an existing automatic discount from the store, permanently removing it from all future order calculations. This mutation provides a clean way to remove promotional campaigns that are no longer needed.
 */
export interface DiscountAutomaticDeleteArgs {
  id: string;
}

export async function discountAutomaticDelete(args: DiscountAutomaticDeleteArgs): Promise<DiscountAutomaticDeletePayload> {
  const gql = `#graphql
    mutation discountAutomaticDelete($id: ID!) {
      discountAutomaticDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticDelete: DiscountAutomaticDeletePayload }>(gql, args);
  return data.discountAutomaticDelete;
}

/**
 * Creates automatic free shipping discounts that apply to qualifying orders without requiring discount codes. These promotions automatically activate when customers meet specified criteria, streamlining the checkout experience.
 */
export interface DiscountAutomaticFreeShippingCreateArgs {
  freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput;
}

export async function discountAutomaticFreeShippingCreate(args: DiscountAutomaticFreeShippingCreateArgs): Promise<DiscountAutomaticFreeShippingCreatePayload> {
  const gql = `#graphql
    mutation discountAutomaticFreeShippingCreate($freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput!) {
      discountAutomaticFreeShippingCreate(freeShippingAutomaticDiscount: $freeShippingAutomaticDiscount) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticFreeShippingCreate: DiscountAutomaticFreeShippingCreatePayload }>(gql, args);
  return data.discountAutomaticFreeShippingCreate;
}

/**
 * Updates existing automatic free shipping discounts, allowing merchants to modify promotion criteria, shipping destinations, and eligibility requirements without recreating the entire discount structure.
 */
export interface DiscountAutomaticFreeShippingUpdateArgs {
  freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput;
  id: string;
}

export async function discountAutomaticFreeShippingUpdate(args: DiscountAutomaticFreeShippingUpdateArgs): Promise<DiscountAutomaticFreeShippingUpdatePayload> {
  const gql = `#graphql
    mutation discountAutomaticFreeShippingUpdate($freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput!, $id: ID!) {
      discountAutomaticFreeShippingUpdate(freeShippingAutomaticDiscount: $freeShippingAutomaticDiscount, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountAutomaticFreeShippingUpdate: DiscountAutomaticFreeShippingUpdatePayload }>(gql, args);
  return data.discountAutomaticFreeShippingUpdate;
}

/**
 * Adds tags to multiple discounts asynchronously using one of the following:
 */
export interface DiscountBulkTagsAddArgs {
  ids?: unknown;
  savedSearchId?: string;
  search?: string;
  tags: unknown;
}

export async function discountBulkTagsAdd(args: DiscountBulkTagsAddArgs): Promise<DiscountBulkTagsAddPayload> {
  const gql = `#graphql
    mutation discountBulkTagsAdd($ids: String, $savedSearchId: ID, $search: String, $tags: String) {
      discountBulkTagsAdd(ids: $ids, savedSearchId: $savedSearchId, search: $search, tags: $tags) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountBulkTagsAdd: DiscountBulkTagsAddPayload }>(gql, args);
  return data.discountBulkTagsAdd;
}

/**
 * Removes tags from multiple discounts asynchronously using one of the following:
 */
export interface DiscountBulkTagsRemoveArgs {
  ids?: unknown;
  savedSearchId?: string;
  search?: string;
  tags: unknown;
}

export async function discountBulkTagsRemove(args: DiscountBulkTagsRemoveArgs): Promise<DiscountBulkTagsRemovePayload> {
  const gql = `#graphql
    mutation discountBulkTagsRemove($ids: String, $savedSearchId: ID, $search: String, $tags: String) {
      discountBulkTagsRemove(ids: $ids, savedSearchId: $savedSearchId, search: $search, tags: $tags) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountBulkTagsRemove: DiscountBulkTagsRemovePayload }>(gql, args);
  return data.discountBulkTagsRemove;
}

/**
 * Activates a previously created code discount, making it available for customers to use during checkout. This mutation transitions inactive discount codes into an active state where they can be applied to orders.
 */
export interface DiscountCodeActivateArgs {
  id: string;
}

export async function discountCodeActivate(args: DiscountCodeActivateArgs): Promise<DiscountCodeActivatePayload> {
  const gql = `#graphql
    mutation discountCodeActivate($id: ID!) {
      discountCodeActivate(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeActivate: DiscountCodeActivatePayload }>(gql, args);
  return data.discountCodeActivate;
}

/**
 * Creates a code discount. The discount type must be provided by an app extension that uses Shopify Functions. Functions can implement order, product, or shipping discount functions. Use this mutation with Shopify Functions when you need custom logic beyond Shopify's native discount types.
 * @scope write_discounts
 */
export interface DiscountCodeAppCreateArgs {
  codeAppDiscount: DiscountCodeAppInput;
}

export async function discountCodeAppCreate(args: DiscountCodeAppCreateArgs): Promise<DiscountCodeAppCreatePayload> {
  const gql = `#graphql
    mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
      discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeAppCreate: DiscountCodeAppCreatePayload }>(gql, args);
  return data.discountCodeAppCreate;
}

/**
 * Updates a code discount, where the discount type is provided by an app extension that uses Shopify Functions. Use this mutation when you need advanced, custom, or dynamic discount capabilities that aren't supported by Shopify's native discount types.
 * @scope write_discounts
 */
export interface DiscountCodeAppUpdateArgs {
  codeAppDiscount: DiscountCodeAppInput;
  id: string;
}

export async function discountCodeAppUpdate(args: DiscountCodeAppUpdateArgs): Promise<DiscountCodeAppUpdatePayload> {
  const gql = `#graphql
    mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
      discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeAppUpdate: DiscountCodeAppUpdatePayload }>(gql, args);
  return data.discountCodeAppUpdate;
}

/**
 * Creates an amount off discount that's applied on a cart and at checkout when a customer enters a code. Amount off discounts can be a percentage off or a fixed amount off.
 */
export interface DiscountCodeBasicCreateArgs {
  basicCodeDiscount: DiscountCodeBasicInput;
}

export async function discountCodeBasicCreate(args: DiscountCodeBasicCreateArgs): Promise<DiscountCodeBasicCreatePayload> {
  const gql = `#graphql
    mutation discountCodeBasicCreate($basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeBasicCreate: DiscountCodeBasicCreatePayload }>(gql, args);
  return data.discountCodeBasicCreate;
}

/**
 * Updates an amount off discount that's applied on a cart and at checkout when a customer enters a code. Amount off discounts can be a percentage off or a fixed amount off.
 */
export interface DiscountCodeBasicUpdateArgs {
  basicCodeDiscount: DiscountCodeBasicInput;
  id: string;
}

export async function discountCodeBasicUpdate(args: DiscountCodeBasicUpdateArgs): Promise<DiscountCodeBasicUpdatePayload> {
  const gql = `#graphql
    mutation discountCodeBasicUpdate($basicCodeDiscount: DiscountCodeBasicInput!, $id: ID!) {
      discountCodeBasicUpdate(basicCodeDiscount: $basicCodeDiscount, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeBasicUpdate: DiscountCodeBasicUpdatePayload }>(gql, args);
  return data.discountCodeBasicUpdate;
}

/**
 * Activates multiple code discounts asynchronously using one of the following:
 */
export interface DiscountCodeBulkActivateArgs {
  ids?: unknown;
  savedSearchId?: string;
  search?: string;
}

export async function discountCodeBulkActivate(args?: DiscountCodeBulkActivateArgs): Promise<DiscountCodeBulkActivatePayload> {
  const gql = `#graphql
    mutation discountCodeBulkActivate($ids: String, $savedSearchId: ID, $search: String) {
      discountCodeBulkActivate(ids: $ids, savedSearchId: $savedSearchId, search: $search) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeBulkActivate: DiscountCodeBulkActivatePayload }>(gql, args);
  return data.discountCodeBulkActivate;
}

/**
 * Deactivates multiple code-based discounts asynchronously using one of the following:
 */
export interface DiscountCodeBulkDeactivateArgs {
  ids?: unknown;
  savedSearchId?: string;
  search?: string;
}

export async function discountCodeBulkDeactivate(args?: DiscountCodeBulkDeactivateArgs): Promise<DiscountCodeBulkDeactivatePayload> {
  const gql = `#graphql
    mutation discountCodeBulkDeactivate($ids: String, $savedSearchId: ID, $search: String) {
      discountCodeBulkDeactivate(ids: $ids, savedSearchId: $savedSearchId, search: $search) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeBulkDeactivate: DiscountCodeBulkDeactivatePayload }>(gql, args);
  return data.discountCodeBulkDeactivate;
}

/**
 * Deletes multiple code-based discounts asynchronously using one of the following:
 */
export interface DiscountCodeBulkDeleteArgs {
  ids?: unknown;
  savedSearchId?: string;
  search?: string;
}

export async function discountCodeBulkDelete(args?: DiscountCodeBulkDeleteArgs): Promise<DiscountCodeBulkDeletePayload> {
  const gql = `#graphql
    mutation discountCodeBulkDelete($ids: String, $savedSearchId: ID, $search: String) {
      discountCodeBulkDelete(ids: $ids, savedSearchId: $savedSearchId, search: $search) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeBulkDelete: DiscountCodeBulkDeletePayload }>(gql, args);
  return data.discountCodeBulkDelete;
}

/**
 * Creates a
 */
export interface DiscountCodeBxgyCreateArgs {
  bxgyCodeDiscount: DiscountCodeBxgyInput;
}

export async function discountCodeBxgyCreate(args: DiscountCodeBxgyCreateArgs): Promise<DiscountCodeBxgyCreatePayload> {
  const gql = `#graphql
    mutation discountCodeBxgyCreate($bxgyCodeDiscount: DiscountCodeBxgyInput!) {
      discountCodeBxgyCreate(bxgyCodeDiscount: $bxgyCodeDiscount) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeBxgyCreate: DiscountCodeBxgyCreatePayload }>(gql, args);
  return data.discountCodeBxgyCreate;
}

/**
 * Updates a
 */
export interface DiscountCodeBxgyUpdateArgs {
  bxgyCodeDiscount: DiscountCodeBxgyInput;
  id: string;
}

export async function discountCodeBxgyUpdate(args: DiscountCodeBxgyUpdateArgs): Promise<DiscountCodeBxgyUpdatePayload> {
  const gql = `#graphql
    mutation discountCodeBxgyUpdate($bxgyCodeDiscount: DiscountCodeBxgyInput!, $id: ID!) {
      discountCodeBxgyUpdate(bxgyCodeDiscount: $bxgyCodeDiscount, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeBxgyUpdate: DiscountCodeBxgyUpdatePayload }>(gql, args);
  return data.discountCodeBxgyUpdate;
}

/**
 * Temporarily suspends a code discount without permanently removing it from the store. Deactivation allows merchants to pause promotional campaigns while preserving the discount configuration for potential future use.
 */
export interface DiscountCodeDeactivateArgs {
  id: string;
}

export async function discountCodeDeactivate(args: DiscountCodeDeactivateArgs): Promise<DiscountCodeDeactivatePayload> {
  const gql = `#graphql
    mutation discountCodeDeactivate($id: ID!) {
      discountCodeDeactivate(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeDeactivate: DiscountCodeDeactivatePayload }>(gql, args);
  return data.discountCodeDeactivate;
}

/**
 * Removes a code discount from the store, making it permanently unavailable for customer use. This mutation provides a clean way to eliminate discount codes that are no longer needed or have been replaced.
 */
export interface DiscountCodeDeleteArgs {
  id: string;
}

export async function discountCodeDelete(args: DiscountCodeDeleteArgs): Promise<DiscountCodeDeletePayload> {
  const gql = `#graphql
    mutation discountCodeDelete($id: ID!) {
      discountCodeDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeDelete: DiscountCodeDeletePayload }>(gql, args);
  return data.discountCodeDelete;
}

/**
 * Creates an free shipping discount that's applied on a cart and at checkout when a customer enters a code.
 */
export interface DiscountCodeFreeShippingCreateArgs {
  freeShippingCodeDiscount: DiscountCodeFreeShippingInput;
}

export async function discountCodeFreeShippingCreate(args: DiscountCodeFreeShippingCreateArgs): Promise<DiscountCodeFreeShippingCreatePayload> {
  const gql = `#graphql
    mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
      discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeFreeShippingCreate: DiscountCodeFreeShippingCreatePayload }>(gql, args);
  return data.discountCodeFreeShippingCreate;
}

/**
 * Updates a free shipping discount that's applied on a cart and at checkout when a customer enters a code.
 */
export interface DiscountCodeFreeShippingUpdateArgs {
  freeShippingCodeDiscount: DiscountCodeFreeShippingInput;
  id: string;
}

export async function discountCodeFreeShippingUpdate(args: DiscountCodeFreeShippingUpdateArgs): Promise<DiscountCodeFreeShippingUpdatePayload> {
  const gql = `#graphql
    mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
      discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeFreeShippingUpdate: DiscountCodeFreeShippingUpdatePayload }>(gql, args);
  return data.discountCodeFreeShippingUpdate;
}

/**
 * Asynchronously delete
 */
export interface DiscountCodeRedeemCodeBulkDeleteArgs {
  discountId: string;
  ids?: DiscountRedeemCode;
  savedSearchId?: string;
  search?: string;
}

export async function discountCodeRedeemCodeBulkDelete(args: DiscountCodeRedeemCodeBulkDeleteArgs): Promise<DiscountCodeRedeemCodeBulkDeletePayload> {
  const gql = `#graphql
    mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $ids: DiscountRedeemCode, $savedSearchId: ID, $search: String) {
      discountCodeRedeemCodeBulkDelete(discountId: $discountId, ids: $ids, savedSearchId: $savedSearchId, search: $search) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountCodeRedeemCodeBulkDelete: DiscountCodeRedeemCodeBulkDeletePayload }>(gql, args);
  return data.discountCodeRedeemCodeBulkDelete;
}

/**
 * Asynchronously add
 */
export interface DiscountRedeemCodeBulkAddArgs {
  codes: unknown;
  discountId: string;
}

export async function discountRedeemCodeBulkAdd(args: DiscountRedeemCodeBulkAddArgs): Promise<DiscountRedeemCodeBulkAddPayload> {
  const gql = `#graphql
    mutation discountRedeemCodeBulkAdd($codes: String, $discountId: ID!) {
      discountRedeemCodeBulkAdd(codes: $codes, discountId: $discountId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ discountRedeemCodeBulkAdd: DiscountRedeemCodeBulkAddPayload }>(gql, args);
  return data.discountRedeemCodeBulkAdd;
}

/**
 * Deletes all external marketing activities. Deletion is performed by a background job, as it may take a bit of time to complete if a large number of activities are to be deleted. Attempting to create or modify external activities before the job has completed will result in the create/update/upsert mutation returning an error.
 * @scope write_marketing_events
 */
export async function marketingActivitiesDeleteAllExternal(): Promise<MarketingActivitiesDeleteAllExternalPayload> {
  const gql = `#graphql
    mutation marketingActivitiesDeleteAllExternal {
      marketingActivitiesDeleteAllExternal {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingActivitiesDeleteAllExternal: MarketingActivitiesDeleteAllExternalPayload }>(gql);
  return data.marketingActivitiesDeleteAllExternal;
}

/**
 * Create new marketing activity. Marketing activity app extensions are deprecated and will be removed in the near future.
 * @scope write_marketing_events
 */
export interface MarketingActivityCreateArgs {
  input: MarketingActivityCreateInput;
}

export async function marketingActivityCreate(args: MarketingActivityCreateArgs): Promise<MarketingActivityCreatePayload> {
  const gql = `#graphql
    mutation marketingActivityCreate($input: MarketingActivityCreateInput!) {
      marketingActivityCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingActivityCreate: MarketingActivityCreatePayload }>(gql, args);
  return data.marketingActivityCreate;
}

/**
 * Creates a new external marketing activity.
 * @scope write_marketing_events
 */
export interface MarketingActivityCreateExternalArgs {
  input: MarketingActivityCreateExternalInput;
}

export async function marketingActivityCreateExternal(args: MarketingActivityCreateExternalArgs): Promise<MarketingActivityCreateExternalPayload> {
  const gql = `#graphql
    mutation marketingActivityCreateExternal($input: MarketingActivityCreateExternalInput!) {
      marketingActivityCreateExternal(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingActivityCreateExternal: MarketingActivityCreateExternalPayload }>(gql, args);
  return data.marketingActivityCreateExternal;
}

/**
 * Deletes an external marketing activity.
 * @scope write_marketing_events
 */
export interface MarketingActivityDeleteExternalArgs {
  marketingActivityId?: string;
  remoteId?: string;
}

export async function marketingActivityDeleteExternal(args?: MarketingActivityDeleteExternalArgs): Promise<MarketingActivityDeleteExternalPayload> {
  const gql = `#graphql
    mutation marketingActivityDeleteExternal($marketingActivityId: ID, $remoteId: String) {
      marketingActivityDeleteExternal(marketingActivityId: $marketingActivityId, remoteId: $remoteId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingActivityDeleteExternal: MarketingActivityDeleteExternalPayload }>(gql, args);
  return data.marketingActivityDeleteExternal;
}

/**
 * Updates a marketing activity with the latest information. Marketing activity app extensions are deprecated and will be removed in the near future.
 * @scope write_marketing_events
 */
export interface MarketingActivityUpdateArgs {
  input: MarketingActivityUpdateInput;
}

export async function marketingActivityUpdate(args: MarketingActivityUpdateArgs): Promise<MarketingActivityUpdatePayload> {
  const gql = `#graphql
    mutation marketingActivityUpdate($input: MarketingActivityUpdateInput!) {
      marketingActivityUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingActivityUpdate: MarketingActivityUpdatePayload }>(gql, args);
  return data.marketingActivityUpdate;
}

/**
 * Update an external marketing activity.
 * @scope write_marketing_events
 */
export interface MarketingActivityUpdateExternalArgs {
  input: MarketingActivityUpdateExternalInput;
  marketingActivityId?: string;
  remoteId?: string;
  utm?: UTMInput;
}

export async function marketingActivityUpdateExternal(args: MarketingActivityUpdateExternalArgs): Promise<MarketingActivityUpdateExternalPayload> {
  const gql = `#graphql
    mutation marketingActivityUpdateExternal($input: MarketingActivityUpdateExternalInput!, $marketingActivityId: ID, $remoteId: String, $utm: UTMInput) {
      marketingActivityUpdateExternal(input: $input, marketingActivityId: $marketingActivityId, remoteId: $remoteId, utm: $utm) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingActivityUpdateExternal: MarketingActivityUpdateExternalPayload }>(gql, args);
  return data.marketingActivityUpdateExternal;
}

/**
 * Creates a new external marketing activity or updates an existing one. When optional fields are absent or null, associated information will be removed from an existing marketing activity.
 * @scope write_marketing_events
 */
export interface MarketingActivityUpsertExternalArgs {
  input: MarketingActivityUpsertExternalInput;
}

export async function marketingActivityUpsertExternal(args: MarketingActivityUpsertExternalArgs): Promise<MarketingActivityUpsertExternalPayload> {
  const gql = `#graphql
    mutation marketingActivityUpsertExternal($input: MarketingActivityUpsertExternalInput!) {
      marketingActivityUpsertExternal(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingActivityUpsertExternal: MarketingActivityUpsertExternalPayload }>(gql, args);
  return data.marketingActivityUpsertExternal;
}

/**
 * Creates a new marketing engagement for a marketing activity or a marketing channel.
 * @scope write_marketing_events
 */
export interface MarketingEngagementCreateArgs {
  channelHandle?: string;
  marketingActivityId?: string;
  marketingEngagement: MarketingEngagementInput;
  remoteId?: string;
}

export async function marketingEngagementCreate(args: MarketingEngagementCreateArgs): Promise<MarketingEngagementCreatePayload> {
  const gql = `#graphql
    mutation marketingEngagementCreate($channelHandle: String, $marketingActivityId: ID, $marketingEngagement: MarketingEngagementInput!, $remoteId: String) {
      marketingEngagementCreate(channelHandle: $channelHandle, marketingActivityId: $marketingActivityId, marketingEngagement: $marketingEngagement, remoteId: $remoteId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingEngagementCreate: MarketingEngagementCreatePayload }>(gql, args);
  return data.marketingEngagementCreate;
}

/**
 * |-
 * @scope write_marketing_events
 */
export interface MarketingEngagementsDeleteArgs {
  channelHandle?: string;
  deleteEngagementsForAllChannels?: boolean;
}

export async function marketingEngagementsDelete(args?: MarketingEngagementsDeleteArgs): Promise<MarketingEngagementsDeletePayload> {
  const gql = `#graphql
    mutation marketingEngagementsDelete($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
      marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ marketingEngagementsDelete: MarketingEngagementsDeletePayload }>(gql, args);
  return data.marketingEngagementsDelete;
}

/**
 * Creates a PriceList. Price lists enable contextual pricing by defining fixed prices or percentage-based adjustments.
 * @scope write_products
 */
export interface PriceListCreateArgs {
  input: PriceListCreateInput;
}

export async function priceListCreate(args: PriceListCreateArgs): Promise<PriceListCreatePayload> {
  const gql = `#graphql
    mutation priceListCreate($input: PriceListCreateInput!) {
      priceListCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ priceListCreate: PriceListCreatePayload }>(gql, args);
  return data.priceListCreate;
}

/**
 * Deletes a price list. For example, you can delete a price list so that it no longer applies for products in the associated market.
 * @scope write_products
 */
export interface PriceListDeleteArgs {
  id: string;
}

export async function priceListDelete(args: PriceListDeleteArgs): Promise<PriceListDeletePayload> {
  const gql = `#graphql
    mutation priceListDelete($id: ID!) {
      priceListDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ priceListDelete: PriceListDeletePayload }>(gql, args);
  return data.priceListDelete;
}

/**
 * Creates or updates fixed prices on a PriceList. Use this mutation to set specific prices for ProductVariant objects that override the price list's default percentage-based adjustments.
 * @scope write_products
 */
export interface PriceListFixedPricesAddArgs {
  priceListId: string;
  prices: unknown;
}

export async function priceListFixedPricesAdd(args: PriceListFixedPricesAddArgs): Promise<PriceListFixedPricesAddPayload> {
  const gql = `#graphql
    mutation priceListFixedPricesAdd($priceListId: ID!, $prices: String) {
      priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ priceListFixedPricesAdd: PriceListFixedPricesAddPayload }>(gql, args);
  return data.priceListFixedPricesAdd;
}

/**
 * Sets or removes fixed prices for all variants of a Product on a PriceList. Simplifies pricing management when all variants of a product should have the same price on a price list, rather than setting individual variant prices.
 * @scope write_products
 */
export interface PriceListFixedPricesByProductUpdateArgs {
  priceListId: string;
  pricesToAdd?: unknown;
  pricesToDeleteByProductIds?: unknown;
}

export async function priceListFixedPricesByProductUpdate(args: PriceListFixedPricesByProductUpdateArgs): Promise<PriceListFixedPricesByProductUpdatePayload> {
  const gql = `#graphql
    mutation priceListFixedPricesByProductUpdate($priceListId: ID!, $pricesToAdd: String, $pricesToDeleteByProductIds: String) {
      priceListFixedPricesByProductUpdate(priceListId: $priceListId, pricesToAdd: $pricesToAdd, pricesToDeleteByProductIds: $pricesToDeleteByProductIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ priceListFixedPricesByProductUpdate: PriceListFixedPricesByProductUpdatePayload }>(gql, args);
  return data.priceListFixedPricesByProductUpdate;
}

/**
 * Deletes specific fixed prices from a price list using a product variant ID. You can use the priceListFixedPricesDelete mutation to delete a set of fixed prices from a price list. After deleting the set of fixed prices from the price list, the price of each product variant reverts to the original price that was determined by the price list adjustment.
 * @scope write_products
 */
export interface PriceListFixedPricesDeleteArgs {
  priceListId: string;
  variantIds: unknown;
}

export async function priceListFixedPricesDelete(args: PriceListFixedPricesDeleteArgs): Promise<PriceListFixedPricesDeletePayload> {
  const gql = `#graphql
    mutation priceListFixedPricesDelete($priceListId: ID!, $variantIds: String) {
      priceListFixedPricesDelete(priceListId: $priceListId, variantIds: $variantIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ priceListFixedPricesDelete: PriceListFixedPricesDeletePayload }>(gql, args);
  return data.priceListFixedPricesDelete;
}

/**
 * Updates fixed prices on a PriceList. This mutation lets you add new fixed prices for specific ProductVariant objects and remove existing prices in a single operation.
 * @scope write_products
 */
export interface PriceListFixedPricesUpdateArgs {
  priceListId: string;
  pricesToAdd: unknown;
  variantIdsToDelete: unknown;
}

export async function priceListFixedPricesUpdate(args: PriceListFixedPricesUpdateArgs): Promise<PriceListFixedPricesUpdatePayload> {
  const gql = `#graphql
    mutation priceListFixedPricesUpdate($priceListId: ID!, $pricesToAdd: String, $variantIdsToDelete: String) {
      priceListFixedPricesUpdate(priceListId: $priceListId, pricesToAdd: $pricesToAdd, variantIdsToDelete: $variantIdsToDelete) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ priceListFixedPricesUpdate: PriceListFixedPricesUpdatePayload }>(gql, args);
  return data.priceListFixedPricesUpdate;
}

/**
 * Updates a PriceList's configuration, including its name, currency, Catalog association, and pricing adjustments.
 * @scope write_products
 */
export interface PriceListUpdateArgs {
  id: string;
  input: PriceListUpdateInput;
}

export async function priceListUpdate(args: PriceListUpdateArgs): Promise<PriceListUpdatePayload> {
  const gql = `#graphql
    mutation priceListUpdate($id: ID!, $input: PriceListUpdateInput!) {
      priceListUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ priceListUpdate: PriceListUpdatePayload }>(gql, args);
  return data.priceListUpdate;
}

/**
 * Updates quantity pricing on a PriceList for specific ProductVariant objects. You can set fixed prices (see PriceListPrice), quantity rules, and quantity price breaks in a single operation.
 * @scope write_products
 */
export interface QuantityPricingByVariantUpdateArgs {
  input: QuantityPricingByVariantUpdateInput;
  priceListId: string;
}

export async function quantityPricingByVariantUpdate(args: QuantityPricingByVariantUpdateArgs): Promise<QuantityPricingByVariantUpdatePayload> {
  const gql = `#graphql
    mutation quantityPricingByVariantUpdate($input: QuantityPricingByVariantUpdateInput!, $priceListId: ID!) {
      quantityPricingByVariantUpdate(input: $input, priceListId: $priceListId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ quantityPricingByVariantUpdate: QuantityPricingByVariantUpdatePayload }>(gql, args);
  return data.quantityPricingByVariantUpdate;
}

/**
 * Creates or updates existing quantity rules on a price list.
 * @scope write_products
 */
export interface QuantityRulesAddArgs {
  priceListId: string;
  quantityRules: unknown;
}

export async function quantityRulesAdd(args: QuantityRulesAddArgs): Promise<QuantityRulesAddPayload> {
  const gql = `#graphql
    mutation quantityRulesAdd($priceListId: ID!, $quantityRules: String) {
      quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ quantityRulesAdd: QuantityRulesAddPayload }>(gql, args);
  return data.quantityRulesAdd;
}

/**
 * Deletes specific quantity rules from a price list using a product variant ID.
 * @scope write_products
 */
export interface QuantityRulesDeleteArgs {
  priceListId: string;
  variantIds: unknown;
}

export async function quantityRulesDelete(args: QuantityRulesDeleteArgs): Promise<QuantityRulesDeletePayload> {
  const gql = `#graphql
    mutation quantityRulesDelete($priceListId: ID!, $variantIds: String) {
      quantityRulesDelete(priceListId: $priceListId, variantIds: $variantIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ quantityRulesDelete: QuantityRulesDeletePayload }>(gql, args);
  return data.quantityRulesDelete;
}










