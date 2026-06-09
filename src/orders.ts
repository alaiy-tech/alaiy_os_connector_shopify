import { shopifyClient } from './client';
import type { CalculatedDraftOrderLineItem, CalculatedOrder, CalculatedReturn, CalculateReturnInput, Count, Customer, DisputeEvidenceUpdatePayload, DraftOrder, DraftOrderAvailableDeliveryOptions, DraftOrderAvailableDeliveryOptionsInput, DraftOrderBulkAddTagsPayload, DraftOrderBulkDeletePayload, DraftOrderBulkRemoveTagsPayload, DraftOrderCalculatePayload, DraftOrderCompletePayload, DraftOrderConnection, DraftOrderCreateFromOrderPayload, DraftOrderCreatePayload, DraftOrderDeleteInput, DraftOrderDeletePayload, DraftOrderDuplicatePayload, DraftOrderInput, DraftOrderInvoicePreviewPayload, DraftOrderInvoiceSendPayload, DraftOrderSortKeys, DraftOrderTag, DraftOrderUpdatePayload, EmailInput, ExchangeLineItem, GiftCard, GiftCardConfiguration, GiftCardConnection, GiftCardCreateInput, GiftCardCreatePayload, GiftCardCreditInput, GiftCardCreditPayload, GiftCardDeactivatePayload, GiftCardDebitInput, GiftCardDebitPayload, GiftCardSendNotificationToCustomerPayload, GiftCardSendNotificationToRecipientPayload, GiftCardSortKeys, GiftCardUpdateInput, GiftCardUpdatePayload, LineItem, MailingAddress, MoneyInput, Order, OrderCancelPayload, OrderCancelReason, OrderCancelRefundMethodInput, OrderCaptureInput, OrderCapturePayload, OrderCloseInput, OrderClosePayload, OrderConnection, OrderCreateMandatePaymentPayload, OrderCreateManualPaymentPayload, OrderCreateOptionsInput, OrderCreateOrderInput, OrderCreatePayload, OrderCustomerRemovePayload, OrderCustomerSetPayload, OrderDeletePayload, OrderEditAddCustomItemPayload, OrderEditAddLineItemDiscountPayload, OrderEditAddShippingLineInput, OrderEditAddShippingLinePayload, OrderEditAddVariantPayload, OrderEditAppliedDiscountInput, OrderEditBeginPayload, OrderEditCommitPayload, OrderEditRemoveDiscountPayload, OrderEditRemoveLineItemDiscountPayload, OrderEditRemoveShippingLinePayload, OrderEditSession, OrderEditSetQuantityPayload, OrderEditUpdateDiscountPayload, OrderEditUpdateShippingLineInput, OrderEditUpdateShippingLinePayload, OrderIdentifierInput, OrderInput, OrderInvoiceSendPayload, OrderMarkAsPaidInput, OrderMarkAsPaidPayload, OrderOpenInput, OrderOpenPayload, OrderPaymentStatus, OrderRiskAssessmentCreateInput, OrderRiskAssessmentCreatePayload, OrderSortKeys, OrderUpdatePayload, PaymentMandate, PaymentReminderSendPayload, PaymentTermsCreateInput, PaymentTermsCreatePayload, PaymentTermsDeleteInput, PaymentTermsDeletePayload, PaymentTermsType, PaymentTermsUpdateInput, PaymentTermsUpdatePayload, ProductVariant, Refund, RefundCreatePayload, RefundInput, RemoveFromReturnPayload, Return, ReturnableFulfillment, ReturnableFulfillmentConnection, ReturnApproveRequestInput, ReturnApproveRequestPayload, ReturnCancelPayload, ReturnClosePayload, ReturnCreatePayload, ReturnDeclineRequestInput, ReturnDeclineRequestPayload, ReturnInput, ReturnLineItem, ReturnLineItemRemoveFromReturnPayload, ReturnProcessInput, ReturnProcessPayload, ReturnReasonDefinitionConnection, ReturnReasonDefinitionSortKeys, ReturnRefundInput, ReturnRefundPayload, ReturnReopenPayload, ReturnRequestInput, ReturnRequestPayload, ReverseDelivery, ReverseDeliveryCreateWithShippingPayload, ReverseDeliveryLabelInput, ReverseDeliveryShippingUpdatePayload, ReverseDeliveryTrackingInput, ReverseFulfillmentOrder, ReverseFulfillmentOrderDisposePayload, SavedSearch, SavedSearchConnection, ShippingLine, ShopifyPaymentsDispute, ShopifyPaymentsDisputeConnection, ShopifyPaymentsDisputeEvidence, ShopifyPaymentsDisputeEvidenceUpdateInput, TenderTransactionConnection, TransactionVoidPayload } from './types';

// ============================================================
// Orders
// 97 operations: 31 queries, 66 mutations
// ============================================================

// These are passed as plain objects. See Shopify docs for field shapes:

// ─── Queries ─────────────────────────────────────────────────────────

/**
 * Returns a ShopifyPaymentsDispute resource by ID.
 */
export interface DisputeArgs {
  id: string;
}

export async function dispute(args: DisputeArgs): Promise<ShopifyPaymentsDispute | null> {
  const gql = `#graphql
    query dispute($id: ID!) {
      dispute(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ dispute: ShopifyPaymentsDispute | null }>(gql, args);
  return data.dispute;
}

/**
 * Returns a ShopifyPaymentsDisputeEvidence resource by ID.
 */
export interface DisputeEvidenceArgs {
  id: string;
}

export async function disputeEvidence(args: DisputeEvidenceArgs): Promise<ShopifyPaymentsDisputeEvidence | null> {
  const gql = `#graphql
    query disputeEvidence($id: ID!) {
      disputeEvidence(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ disputeEvidence: ShopifyPaymentsDisputeEvidence | null }>(gql, args);
  return data.disputeEvidence;
}

/**
 * Returns a paginated list of all Shopify Payments disputes for the shop. Disputes occur when a buyer files a complaint with their payments provider, and the merchant must provide evidence to contest it. Each dispute includes the status, amount, reason, and associated order. Use this to monitor and manage open chargebacks and track dispute resolution outcomes.
 */
export interface DisputesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
}

export async function disputes(args?: DisputesArgs): Promise<ShopifyPaymentsDisputeConnection> {
  const gql = `#graphql
    query disputes($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean) {
      disputes(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ disputes: ShopifyPaymentsDisputeConnection }>(gql, args);
  return data.disputes;
}

/**
 * Retrieves a draft order by its ID.
 */
export interface DraftOrderArgs {
  id: string;
}

export async function draftOrder(args: DraftOrderArgs): Promise<DraftOrder | null> {
  const gql = `#graphql
    query draftOrder($id: ID!) {
      draftOrder(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrder: DraftOrder | null }>(gql, args);
  return data.draftOrder;
}

/**
 * Available delivery options for a DraftOrder based on the provided input. The query returns shipping rates, local delivery rates, and pickup locations that merchants can choose from when creating draft orders.
 * @scope read_draft_orders
 */
export interface DraftOrderAvailableDeliveryOptionsArgs {
  input: DraftOrderAvailableDeliveryOptionsInput;
  localPickupCount?: number;
  localPickupFrom?: number;
  search?: string;
  sessionToken?: string;
}

export async function draftOrderAvailableDeliveryOptions(args: DraftOrderAvailableDeliveryOptionsArgs): Promise<DraftOrderAvailableDeliveryOptions | null> {
  const gql = `#graphql
    query draftOrderAvailableDeliveryOptions($input: DraftOrderAvailableDeliveryOptionsInput!, $localPickupCount: Int, $localPickupFrom: Int, $search: String, $sessionToken: String) {
      draftOrderAvailableDeliveryOptions(input: $input, localPickupCount: $localPickupCount, localPickupFrom: $localPickupFrom, search: $search, sessionToken: $sessionToken) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderAvailableDeliveryOptions: DraftOrderAvailableDeliveryOptions | null }>(gql, args);
  return data.draftOrderAvailableDeliveryOptions;
}

/**
 * List of the shop's draft order saved searches.
 * @scope read_draft_orders
 */
export interface DraftOrderSavedSearchesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function draftOrderSavedSearches(args?: DraftOrderSavedSearchesArgs): Promise<SavedSearchConnection> {
  const gql = `#graphql
    query draftOrderSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      draftOrderSavedSearches(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderSavedSearches: SavedSearchConnection }>(gql, args);
  return data.draftOrderSavedSearches;
}

/**
 * Returns a DraftOrderTag resource by ID.
 */
export interface DraftOrderTagArgs {
  id: string;
}

export async function draftOrderTag(args: DraftOrderTagArgs): Promise<DraftOrderTag | null> {
  const gql = `#graphql
    query draftOrderTag($id: ID!) {
      draftOrderTag(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderTag: DraftOrderTag | null }>(gql, args);
  return data.draftOrderTag;
}

/**
 * List of saved draft orders.
 */
export interface DraftOrdersArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: DraftOrderSortKeys;
}

export async function draftOrders(args?: DraftOrdersArgs): Promise<DraftOrderConnection> {
  const gql = `#graphql
    query draftOrders($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: DraftOrderSortKeys) {
      draftOrders(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrders: DraftOrderConnection }>(gql, args);
  return data.draftOrders;
}

/**
 * Returns the number of draft orders that match the query. Limited to a maximum of 10000 by default.
 * @scope read_draft_orders
 */
export interface DraftOrdersCountArgs {
  limit?: number;
  query?: string;
  savedSearchId?: string;
}

export async function draftOrdersCount(args?: DraftOrdersCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query draftOrdersCount($limit: Int, $query: String, $savedSearchId: ID) {
      draftOrdersCount(limit: $limit, query: $query, savedSearchId: $savedSearchId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrdersCount: Count | null }>(gql, args);
  return data.draftOrdersCount;
}

/**
 * Retrieves a GiftCard by its ID. Returns the gift card's balance, transaction history, Customer information, and whether it's enabled.
 * @scope read_gift_cards
 */
export interface GiftCardArgs {
  id: string;
}

export async function giftCard(args: GiftCardArgs): Promise<GiftCard | null> {
  const gql = `#graphql
    query giftCard($id: ID!) {
      giftCard(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCard: GiftCard | null }>(gql, args);
  return data.giftCard;
}

/**
 * The configuration for the shop's gift cards.
 */
export async function giftCardConfiguration(): Promise<GiftCardConfiguration | null> {
  const gql = `#graphql
    query giftCardConfiguration {
      giftCardConfiguration {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCardConfiguration: GiftCardConfiguration | null }>(gql);
  return data.giftCardConfiguration;
}

/**
 * Returns a paginated list of GiftCard objects issued for the shop.
 * @scope read_gift_cards
 */
export interface GiftCardsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: GiftCardSortKeys;
}

export async function giftCards(args?: GiftCardsArgs): Promise<GiftCardConnection> {
  const gql = `#graphql
    query giftCards($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: GiftCardSortKeys) {
      giftCards(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCards: GiftCardConnection }>(gql, args);
  return data.giftCards;
}

/**
 * Returns the total count of gift cards that have been issued by the shop. Use this for dashboard summaries or to understand the scale of a merchant's gift card program. The count includes all gift cards regardless of status (active, disabled, or fully redeemed). Limited to a maximum of 10000 by default.
 * @scope read_gift_cards
 */
export interface GiftCardsCountArgs {
  limit?: number;
  query?: string;
  savedSearchId?: string;
}

export async function giftCardsCount(args?: GiftCardsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query giftCardsCount($limit: Int, $query: String, $savedSearchId: ID) {
      giftCardsCount(limit: $limit, query: $query, savedSearchId: $savedSearchId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCardsCount: Count | null }>(gql, args);
  return data.giftCardsCount;
}

/**
 * The order query retrieves an order by its ID. This query provides access to comprehensive order information such as customer details, line items, financial data, and fulfillment status.
 */
export interface OrderArgs {
  id: string;
}

export async function order(args: OrderArgs): Promise<Order | null> {
  const gql = `#graphql
    query order($id: ID!) {
      order(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ order: Order | null }>(gql, args);
  return data.order;
}

/**
 * Return an order by an identifier.
 * @scope read_orders
 */
export interface OrderByIdentifierArgs {
  identifier: OrderIdentifierInput;
}

export async function orderByIdentifier(args: OrderByIdentifierArgs): Promise<Order | null> {
  const gql = `#graphql
    query orderByIdentifier($identifier: OrderIdentifierInput!) {
      orderByIdentifier(identifier: $identifier) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderByIdentifier: Order | null }>(gql, args);
  return data.orderByIdentifier;
}

/**
 * Returns a OrderEditSession resource by ID.
 */
export interface OrderEditSessionArgs {
  id: string;
}

export async function orderEditSession(args: OrderEditSessionArgs): Promise<OrderEditSession | null> {
  const gql = `#graphql
    query orderEditSession($id: ID!) {
      orderEditSession(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditSession: OrderEditSession | null }>(gql, args);
  return data.orderEditSession;
}

/**
 * Retrieves the status of a deferred payment by its payment reference ID. Use this query to monitor the processing status of payments that are initiated through payment mutations. Deferred payments are called payment terms in the API.
 */
export interface OrderPaymentStatusArgs {
  orderId: string;
  paymentReferenceId: string;
}

export async function orderPaymentStatus(args: OrderPaymentStatusArgs): Promise<OrderPaymentStatus | null> {
  const gql = `#graphql
    query orderPaymentStatus($orderId: ID!, $paymentReferenceId: String!) {
      orderPaymentStatus(orderId: $orderId, paymentReferenceId: $paymentReferenceId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderPaymentStatus: OrderPaymentStatus | null }>(gql, args);
  return data.orderPaymentStatus;
}

/**
 * Returns saved searches for orders in the shop. Saved searches store search queries with their filters and search terms.
 * @scope read_orders
 */
export interface OrderSavedSearchesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function orderSavedSearches(args?: OrderSavedSearchesArgs): Promise<SavedSearchConnection> {
  const gql = `#graphql
    query orderSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      orderSavedSearches(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderSavedSearches: SavedSearchConnection }>(gql, args);
  return data.orderSavedSearches;
}

/**
 * Returns a list of orders placed in the store, including data such as order status, customer, and line item details.
 */
export interface OrdersArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: OrderSortKeys;
}

export async function orders(args?: OrdersArgs): Promise<OrderConnection> {
  const gql = `#graphql
    query orders($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: OrderSortKeys) {
      orders(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orders: OrderConnection }>(gql, args);
  return data.orders;
}

/**
 * Returns the number of orders in the shop. You can filter orders using search syntax or a SavedSearch, and set a maximum count limit to control query performance.
 * @scope read_orders
 */
export interface OrdersCountArgs {
  limit?: number;
  query?: string;
  savedSearchId?: string;
}

export async function ordersCount(args?: OrdersCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query ordersCount($limit: Int, $query: String, $savedSearchId: ID) {
      ordersCount(limit: $limit, query: $query, savedSearchId: $savedSearchId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ ordersCount: Count | null }>(gql, args);
  return data.ordersCount;
}

/**
 * The list of payment terms templates eligible for all shops and users.
 */
export interface PaymentTermsTemplatesArgs {
  paymentTermsType?: PaymentTermsType;
}

export async function paymentTermsTemplates(args?: PaymentTermsTemplatesArgs): Promise<string> {
  const gql = `#graphql
    query paymentTermsTemplates($paymentTermsType: PaymentTermsType) {
      paymentTermsTemplates(paymentTermsType: $paymentTermsType) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentTermsTemplates: string }>(gql, args);
  return data.paymentTermsTemplates;
}

/**
 * The number of pendings orders. Limited to a maximum of 10000.
 * @scope read_orders
 */
export async function pendingOrdersCount(): Promise<Count | null> {
  const gql = `#graphql
    query pendingOrdersCount {
      pendingOrdersCount {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pendingOrdersCount: Count | null }>(gql);
  return data.pendingOrdersCount;
}

/**
 * Retrieves a refund by its ID.
 * @scope read_orders
 */
export interface RefundArgs {
  id: string;
}

export async function refund(args: RefundArgs): Promise<Refund | null> {
  const gql = `#graphql
    query refund($id: ID!) {
      refund(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ refund: Refund | null }>(gql, args);
  return data.refund;
}

/**
 * Retrieves a return by its ID. A return represents the intent of a buyer to ship one or more items from an
 * @scope read_returns
 */
export interface GetReturnArgs {
  id: string;
}

export async function getReturn(args: GetReturnArgs): Promise<Return | null> {
  const gql = `#graphql
    query return($id: ID!) {
      return(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ return: Return | null }>(gql, args);
  return data.return;
}

/**
 * Calculates the financial outcome of a Return without creating it. Use this query to preview return costs before initiating the actual return process.
 * @scope read_returns
 */
export interface ReturnCalculateArgs {
  input: CalculateReturnInput;
}

export async function returnCalculate(args: ReturnCalculateArgs): Promise<CalculatedReturn | null> {
  const gql = `#graphql
    query returnCalculate($input: CalculateReturnInput!) {
      returnCalculate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnCalculate: CalculatedReturn | null }>(gql, args);
  return data.returnCalculate;
}

/**
 * Returns the full library of available return reason definitions.
 * @scope read_returns
 */
export interface ReturnReasonDefinitionsArgs {
  after?: string;
  before?: string;
  first?: number;
  handles?: unknown;
  ids?: unknown;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: ReturnReasonDefinitionSortKeys;
}

export async function returnReasonDefinitions(args?: ReturnReasonDefinitionsArgs): Promise<ReturnReasonDefinitionConnection> {
  const gql = `#graphql
    query returnReasonDefinitions($after: String, $before: String, $first: Int, $handles: String, $ids: String, $last: Int, $query: String, $reverse: Boolean, $sortKey: ReturnReasonDefinitionSortKeys) {
      returnReasonDefinitions(after: $after, before: $before, first: $first, handles: $handles, ids: $ids, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnReasonDefinitions: ReturnReasonDefinitionConnection }>(gql, args);
  return data.returnReasonDefinitions;
}

/**
 * Returns a ReturnableFulfillment resource by ID.
 */
export interface ReturnableFulfillmentArgs {
  id: string;
}

export async function returnableFulfillment(args: ReturnableFulfillmentArgs): Promise<ReturnableFulfillment | null> {
  const gql = `#graphql
    query returnableFulfillment($id: ID!) {
      returnableFulfillment(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnableFulfillment: ReturnableFulfillment | null }>(gql, args);
  return data.returnableFulfillment;
}

/**
 * List of returnable fulfillments.
 */
export interface ReturnableFulfillmentsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  orderId: string;
  reverse?: boolean;
}

export async function returnableFulfillments(args: ReturnableFulfillmentsArgs): Promise<ReturnableFulfillmentConnection> {
  const gql = `#graphql
    query returnableFulfillments($after: String, $before: String, $first: Int, $last: Int, $orderId: ID!, $reverse: Boolean) {
      returnableFulfillments(after: $after, before: $before, first: $first, last: $last, orderId: $orderId, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnableFulfillments: ReturnableFulfillmentConnection }>(gql, args);
  return data.returnableFulfillments;
}

/**
 * Lookup a reverse delivery by ID.
 * @scope read_returns
 */
export interface ReverseDeliveryArgs {
  id: string;
}

export async function reverseDelivery(args: ReverseDeliveryArgs): Promise<ReverseDelivery | null> {
  const gql = `#graphql
    query reverseDelivery($id: ID!) {
      reverseDelivery(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ reverseDelivery: ReverseDelivery | null }>(gql, args);
  return data.reverseDelivery;
}

/**
 * Lookup a reverse fulfillment order by ID.
 * @scope read_returns
 */
export interface ReverseFulfillmentOrderArgs {
  id: string;
}

export async function reverseFulfillmentOrder(args: ReverseFulfillmentOrderArgs): Promise<ReverseFulfillmentOrder | null> {
  const gql = `#graphql
    query reverseFulfillmentOrder($id: ID!) {
      reverseFulfillmentOrder(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ reverseFulfillmentOrder: ReverseFulfillmentOrder | null }>(gql, args);
  return data.reverseFulfillmentOrder;
}

/**
 * Transactions representing a movement of money between customers and the shop. Each transaction records the amount, payment method, processing details, and the associated Order.
 */
export interface TenderTransactionsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
}

export async function tenderTransactions(args?: TenderTransactionsArgs): Promise<TenderTransactionConnection> {
  const gql = `#graphql
    query tenderTransactions($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean) {
      tenderTransactions(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ tenderTransactions: TenderTransactionConnection }>(gql, args);
  return data.tenderTransactions;
}

// ─── Mutations ─────────────────────────────────────────────────────────

/**
 * Updates the evidence package for a Shopify Payments dispute. Merchants submit evidence â€” such as shipping confirmations, customer communications, and refund policies â€” to contest a dispute filed by a cardholder. This mutation updates the evidence fields.
 * @scope write_shopify_payments_dispute_evidences
 */
export interface DisputeEvidenceUpdateArgs {
  id: string;
  input: ShopifyPaymentsDisputeEvidenceUpdateInput;
}

export async function disputeEvidenceUpdate(args: DisputeEvidenceUpdateArgs): Promise<DisputeEvidenceUpdatePayload> {
  const gql = `#graphql
    mutation disputeEvidenceUpdate($id: ID!, $input: ShopifyPaymentsDisputeEvidenceUpdateInput!) {
      disputeEvidenceUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ disputeEvidenceUpdate: DisputeEvidenceUpdatePayload }>(gql, args);
  return data.disputeEvidenceUpdate;
}

/**
 * Adds tags to multiple draft orders.
 * @scope write_draft_orders
 */
export interface DraftOrderBulkAddTagsArgs {
  ids?: unknown;
  savedSearchId?: string;
  search?: string;
  tags: unknown;
}

export async function draftOrderBulkAddTags(args: DraftOrderBulkAddTagsArgs): Promise<DraftOrderBulkAddTagsPayload> {
  const gql = `#graphql
    mutation draftOrderBulkAddTags($ids: String, $savedSearchId: ID, $search: String, $tags: String) {
      draftOrderBulkAddTags(ids: $ids, savedSearchId: $savedSearchId, search: $search, tags: $tags) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderBulkAddTags: DraftOrderBulkAddTagsPayload }>(gql, args);
  return data.draftOrderBulkAddTags;
}

/**
 * Deletes multiple draft orders.
 * @scope write_draft_orders
 */
export interface DraftOrderBulkDeleteArgs {
  ids?: unknown;
  savedSearchId?: string;
  search?: string;
}

export async function draftOrderBulkDelete(args?: DraftOrderBulkDeleteArgs): Promise<DraftOrderBulkDeletePayload> {
  const gql = `#graphql
    mutation draftOrderBulkDelete($ids: String, $savedSearchId: ID, $search: String) {
      draftOrderBulkDelete(ids: $ids, savedSearchId: $savedSearchId, search: $search) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderBulkDelete: DraftOrderBulkDeletePayload }>(gql, args);
  return data.draftOrderBulkDelete;
}

/**
 * Removes tags from multiple draft orders.
 * @scope write_draft_orders
 */
export interface DraftOrderBulkRemoveTagsArgs {
  ids?: unknown;
  savedSearchId?: string;
  search?: string;
  tags: unknown;
}

export async function draftOrderBulkRemoveTags(args: DraftOrderBulkRemoveTagsArgs): Promise<DraftOrderBulkRemoveTagsPayload> {
  const gql = `#graphql
    mutation draftOrderBulkRemoveTags($ids: String, $savedSearchId: ID, $search: String, $tags: String) {
      draftOrderBulkRemoveTags(ids: $ids, savedSearchId: $savedSearchId, search: $search, tags: $tags) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderBulkRemoveTags: DraftOrderBulkRemoveTagsPayload }>(gql, args);
  return data.draftOrderBulkRemoveTags;
}

/**
 * Calculates the properties of a DraftOrder without creating it. Returns pricing information including CalculatedDraftOrderLineItem totals, shipping charges, applicable discounts, and tax calculations based on the provided Customer and MailingAddress information.
 * @scope write_draft_orders
 */
export interface DraftOrderCalculateArgs {
  input: DraftOrderInput;
}

export async function draftOrderCalculate(args: DraftOrderCalculateArgs): Promise<DraftOrderCalculatePayload> {
  const gql = `#graphql
    mutation draftOrderCalculate($input: DraftOrderInput!) {
      draftOrderCalculate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderCalculate: DraftOrderCalculatePayload }>(gql, args);
  return data.draftOrderCalculate;
}

/**
 * Completes a draft order and
 * @scope write_draft_orders
 */
export interface DraftOrderCompleteArgs {
  id: string;
  paymentGatewayId?: string;
  sourceName?: string;
  paymentPending?: boolean;
}

export async function draftOrderComplete(args: DraftOrderCompleteArgs): Promise<DraftOrderCompletePayload> {
  const gql = `#graphql
    mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID, $sourceName: String, $paymentPending: Boolean) {
      draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId, sourceName: $sourceName, paymentPending: $paymentPending) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderComplete: DraftOrderCompletePayload }>(gql, args);
  return data.draftOrderComplete;
}

/**
 * Creates a draft order
 * @scope write_draft_orders
 */
export interface DraftOrderCreateArgs {
  input: DraftOrderInput;
}

export async function draftOrderCreate(args: DraftOrderCreateArgs): Promise<DraftOrderCreatePayload> {
  const gql = `#graphql
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderCreate: DraftOrderCreatePayload }>(gql, args);
  return data.draftOrderCreate;
}

/**
 * Creates a draft order from order.
 * @scope write_draft_orders
 */
export interface DraftOrderCreateFromOrderArgs {
  orderId: string;
}

export async function draftOrderCreateFromOrder(args: DraftOrderCreateFromOrderArgs): Promise<DraftOrderCreateFromOrderPayload> {
  const gql = `#graphql
    mutation draftOrderCreateFromOrder($orderId: ID!) {
      draftOrderCreateFromOrder(orderId: $orderId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderCreateFromOrder: DraftOrderCreateFromOrderPayload }>(gql, args);
  return data.draftOrderCreateFromOrder;
}

/**
 * Deletes a draft order.
 * @scope write_draft_orders
 */
export interface DraftOrderDeleteArgs {
  input: DraftOrderDeleteInput;
}

export async function draftOrderDelete(args: DraftOrderDeleteArgs): Promise<DraftOrderDeletePayload> {
  const gql = `#graphql
    mutation draftOrderDelete($input: DraftOrderDeleteInput!) {
      draftOrderDelete(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderDelete: DraftOrderDeletePayload }>(gql, args);
  return data.draftOrderDelete;
}

/**
 * Duplicates a draft order.
 * @scope write_draft_orders
 */
export interface DraftOrderDuplicateArgs {
  id?: string;
  draftOrderId?: string;
}

export async function draftOrderDuplicate(args?: DraftOrderDuplicateArgs): Promise<DraftOrderDuplicatePayload> {
  const gql = `#graphql
    mutation draftOrderDuplicate($id: ID, $draftOrderId: ID) {
      draftOrderDuplicate(id: $id, draftOrderId: $draftOrderId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderDuplicate: DraftOrderDuplicatePayload }>(gql, args);
  return data.draftOrderDuplicate;
}

/**
 * Previews a draft order invoice email.
 * @scope write_draft_orders
 */
export interface DraftOrderInvoicePreviewArgs {
  email?: EmailInput;
  id: string;
}

export async function draftOrderInvoicePreview(args: DraftOrderInvoicePreviewArgs): Promise<DraftOrderInvoicePreviewPayload> {
  const gql = `#graphql
    mutation draftOrderInvoicePreview($email: EmailInput, $id: ID!) {
      draftOrderInvoicePreview(email: $email, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderInvoicePreview: DraftOrderInvoicePreviewPayload }>(gql, args);
  return data.draftOrderInvoicePreview;
}

/**
 * Sends an invoice email for a DraftOrder. The invoice includes a secure checkout link for reviewing and paying for the order. Use the email argument to customize the email, such as the subject and message.
 * @scope write_draft_orders
 */
export interface DraftOrderInvoiceSendArgs {
  email?: EmailInput;
  id: string;
}

export async function draftOrderInvoiceSend(args: DraftOrderInvoiceSendArgs): Promise<DraftOrderInvoiceSendPayload> {
  const gql = `#graphql
    mutation draftOrderInvoiceSend($email: EmailInput, $id: ID!) {
      draftOrderInvoiceSend(email: $email, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderInvoiceSend: DraftOrderInvoiceSendPayload }>(gql, args);
  return data.draftOrderInvoiceSend;
}

/**
 * Updates a draft order.
 * @scope write_draft_orders
 */
export interface DraftOrderUpdateArgs {
  id: string;
  input: DraftOrderInput;
}

export async function draftOrderUpdate(args: DraftOrderUpdateArgs): Promise<DraftOrderUpdatePayload> {
  const gql = `#graphql
    mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
      draftOrderUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ draftOrderUpdate: DraftOrderUpdatePayload }>(gql, args);
  return data.draftOrderUpdate;
}

/**
 * Creates a new GiftCard with a specified initial value. You can assign the gift card to a Customer or create it without assignment for manual distribution.
 * @scope write_gift_cards
 */
export interface GiftCardCreateArgs {
  input: GiftCardCreateInput;
}

export async function giftCardCreate(args: GiftCardCreateArgs): Promise<GiftCardCreatePayload> {
  const gql = `#graphql
    mutation giftCardCreate($input: GiftCardCreateInput!) {
      giftCardCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCardCreate: GiftCardCreatePayload }>(gql, args);
  return data.giftCardCreate;
}

/**
 * Adds funds to an existing gift card, increasing its available balance. Use this when a merchant wants to top up a customer's gift card â€” for example, as a promotional bonus, a customer service gesture, or to reload a reusable gift card.
 * @scope write_gift_card_transactions
 */
export interface GiftCardCreditArgs {
  creditInput: GiftCardCreditInput;
  id: string;
}

export async function giftCardCredit(args: GiftCardCreditArgs): Promise<GiftCardCreditPayload> {
  const gql = `#graphql
    mutation giftCardCredit($creditInput: GiftCardCreditInput!, $id: ID!) {
      giftCardCredit(creditInput: $creditInput, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCardCredit: GiftCardCreditPayload }>(gql, args);
  return data.giftCardCredit;
}

/**
 * |-
 * @scope write_gift_cards
 */
export interface GiftCardDeactivateArgs {
  id: string;
}

export async function giftCardDeactivate(args: GiftCardDeactivateArgs): Promise<GiftCardDeactivatePayload> {
  const gql = `#graphql
    mutation giftCardDeactivate($id: ID!) {
      giftCardDeactivate(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCardDeactivate: GiftCardDeactivatePayload }>(gql, args);
  return data.giftCardDeactivate;
}

/**
 * Removes funds from a gift card, decreasing its available balance. Use this for manual balance adjustments â€” for example, correcting an accidental over-credit or applying a fee.
 * @scope write_gift_card_transactions
 */
export interface GiftCardDebitArgs {
  debitInput: GiftCardDebitInput;
  id: string;
}

export async function giftCardDebit(args: GiftCardDebitArgs): Promise<GiftCardDebitPayload> {
  const gql = `#graphql
    mutation giftCardDebit($debitInput: GiftCardDebitInput!, $id: ID!) {
      giftCardDebit(debitInput: $debitInput, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCardDebit: GiftCardDebitPayload }>(gql, args);
  return data.giftCardDebit;
}

/**
 * Sends a notification to the customer who purchased a gift card, including the gift card details and code. The notification is delivered using the customer's available contact method. Use this to resend the purchase confirmation or remind the purchaser about a gift card they bought.
 * @scope write_gift_cards
 */
export interface GiftCardSendNotificationToCustomerArgs {
  id: string;
}

export async function giftCardSendNotificationToCustomer(args: GiftCardSendNotificationToCustomerArgs): Promise<GiftCardSendNotificationToCustomerPayload> {
  const gql = `#graphql
    mutation giftCardSendNotificationToCustomer($id: ID!) {
      giftCardSendNotificationToCustomer(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCardSendNotificationToCustomer: GiftCardSendNotificationToCustomerPayload }>(gql, args);
  return data.giftCardSendNotificationToCustomer;
}

/**
 * Sends a notification to the designated recipient of a gift card, delivering the gift card code and redemption instructions. The notification is delivered using the recipient's available contact method. Use this to deliver or re-deliver the gift card to the intended recipient.
 * @scope write_gift_cards
 */
export interface GiftCardSendNotificationToRecipientArgs {
  id: string;
}

export async function giftCardSendNotificationToRecipient(args: GiftCardSendNotificationToRecipientArgs): Promise<GiftCardSendNotificationToRecipientPayload> {
  const gql = `#graphql
    mutation giftCardSendNotificationToRecipient($id: ID!) {
      giftCardSendNotificationToRecipient(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCardSendNotificationToRecipient: GiftCardSendNotificationToRecipientPayload }>(gql, args);
  return data.giftCardSendNotificationToRecipient;
}

/**
 * Updates the properties of an existing gift card, such as its expiration date, note, or template suffix. Use this to modify gift card details â€” for example, extending an expiration date for a loyal customer or adding an internal note for tracking purposes.
 * @scope write_gift_cards
 */
export interface GiftCardUpdateArgs {
  id: string;
  input: GiftCardUpdateInput;
}

export async function giftCardUpdate(args: GiftCardUpdateArgs): Promise<GiftCardUpdatePayload> {
  const gql = `#graphql
    mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
      giftCardUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ giftCardUpdate: GiftCardUpdatePayload }>(gql, args);
  return data.giftCardUpdate;
}

/**
 * Cancels an order, with options for refunding, restocking inventory, and customer notification.
 * @scope write_orders
 */
export interface OrderCancelArgs {
  notifyCustomer?: boolean;
  orderId: string;
  reason: OrderCancelReason;
  refundMethod?: OrderCancelRefundMethodInput;
  restock: boolean;
  staffNote?: string;
  refund?: boolean;
}

export async function orderCancel(args: OrderCancelArgs): Promise<OrderCancelPayload> {
  const gql = `#graphql
    mutation orderCancel($notifyCustomer: Boolean, $orderId: ID!, $reason: OrderCancelReason!, $refundMethod: OrderCancelRefundMethodInput, $restock: Boolean!, $staffNote: String, $refund: Boolean) {
      orderCancel(notifyCustomer: $notifyCustomer, orderId: $orderId, reason: $reason, refundMethod: $refundMethod, restock: $restock, staffNote: $staffNote, refund: $refund) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderCancel: OrderCancelPayload }>(gql, args);
  return data.orderCancel;
}

/**
 * Captures payment for an authorized transaction on an order. Use this mutation to claim the money that was previously
 * @scope write_orders
 */
export interface OrderCaptureArgs {
  input: OrderCaptureInput;
}

export async function orderCapture(args: OrderCaptureArgs): Promise<OrderCapturePayload> {
  const gql = `#graphql
    mutation orderCapture($input: OrderCaptureInput!) {
      orderCapture(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderCapture: OrderCapturePayload }>(gql, args);
  return data.orderCapture;
}

/**
 * Marks an open Order as closed. A closed order is one where merchants fulfill or cancel all LineItem objects and complete all financial transactions.
 * @scope write_orders
 */
export interface OrderCloseArgs {
  input: OrderCloseInput;
}

export async function orderClose(args: OrderCloseArgs): Promise<OrderClosePayload> {
  const gql = `#graphql
    mutation orderClose($input: OrderCloseInput!) {
      orderClose(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderClose: OrderClosePayload }>(gql, args);
  return data.orderClose;
}

/**
 * Creates an order with attributes such as customer information, line items, and shipping and billing addresses.
 * @scope write_orders
 */
export interface OrderCreateArgs {
  options?: OrderCreateOptionsInput;
  order: OrderCreateOrderInput;
}

export async function orderCreate(args: OrderCreateArgs): Promise<OrderCreatePayload> {
  const gql = `#graphql
    mutation orderCreate($options: OrderCreateOptionsInput, $order: OrderCreateOrderInput!) {
      orderCreate(options: $options, order: $order) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderCreate: OrderCreatePayload }>(gql, args);
  return data.orderCreate;
}

/**
 * Creates a payment for an Order using a stored PaymentMandate. A payment mandate represents the customer's authorization to charge their payment method for deferred payments, such as pre-orders or try-before-you-buy purchases.
 * @scope write_payment_mandate
 */
export interface OrderCreateMandatePaymentArgs {
  amount?: MoneyInput;
  autoCapture?: boolean;
  id: string;
  idempotencyKey: string;
  mandateId: string;
  paymentScheduleId?: string;
}

export async function orderCreateMandatePayment(args: OrderCreateMandatePaymentArgs): Promise<OrderCreateMandatePaymentPayload> {
  const gql = `#graphql
    mutation orderCreateMandatePayment($amount: MoneyInput, $autoCapture: Boolean, $id: ID!, $idempotencyKey: String!, $mandateId: ID!, $paymentScheduleId: ID) {
      orderCreateMandatePayment(amount: $amount, autoCapture: $autoCapture, id: $id, idempotencyKey: $idempotencyKey, mandateId: $mandateId, paymentScheduleId: $paymentScheduleId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderCreateMandatePayment: OrderCreateMandatePaymentPayload }>(gql, args);
  return data.orderCreateMandatePayment;
}

/**
 * Records a manual payment for an Order that isn't fully paid. Use this mutation to track payments received outside the standard checkout process, such as cash, check, bank transfer, or other offline payment methods.
 * @scope write_orders
 */
export interface OrderCreateManualPaymentArgs {
  amount?: MoneyInput;
  id: string;
  paymentMethodName?: string;
  processedAt?: string;
}

export async function orderCreateManualPayment(args: OrderCreateManualPaymentArgs): Promise<OrderCreateManualPaymentPayload> {
  const gql = `#graphql
    mutation orderCreateManualPayment($amount: MoneyInput, $id: ID!, $paymentMethodName: String, $processedAt: DateTime) {
      orderCreateManualPayment(amount: $amount, id: $id, paymentMethodName: $paymentMethodName, processedAt: $processedAt) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderCreateManualPayment: OrderCreateManualPaymentPayload }>(gql, args);
  return data.orderCreateManualPayment;
}

/**
 * Removes customer from an order.
 * @scope write_orders
 */
export interface OrderCustomerRemoveArgs {
  orderId: string;
}

export async function orderCustomerRemove(args: OrderCustomerRemoveArgs): Promise<OrderCustomerRemovePayload> {
  const gql = `#graphql
    mutation orderCustomerRemove($orderId: ID!) {
      orderCustomerRemove(orderId: $orderId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderCustomerRemove: OrderCustomerRemovePayload }>(gql, args);
  return data.orderCustomerRemove;
}

/**
 * Sets a customer on an order.
 * @scope write_orders
 */
export interface OrderCustomerSetArgs {
  customerId: string;
  orderId: string;
}

export async function orderCustomerSet(args: OrderCustomerSetArgs): Promise<OrderCustomerSetPayload> {
  const gql = `#graphql
    mutation orderCustomerSet($customerId: ID!, $orderId: ID!) {
      orderCustomerSet(customerId: $customerId, orderId: $orderId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderCustomerSet: OrderCustomerSetPayload }>(gql, args);
  return data.orderCustomerSet;
}

/**
 * Permanently deletes an Order from the store.
 * @scope write_orders
 */
export interface OrderDeleteArgs {
  orderId: string;
}

export async function orderDelete(args: OrderDeleteArgs): Promise<OrderDeletePayload> {
  const gql = `#graphql
    mutation orderDelete($orderId: ID!) {
      orderDelete(orderId: $orderId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderDelete: OrderDeletePayload }>(gql, args);
  return data.orderDelete;
}

/**
 * Adds a custom line item to an existing Order. Custom line items represent products or services not in your catalog, such as gift wrapping, installation fees, or one-off charges.
 * @scope write_order_edits
 */
export interface OrderEditAddCustomItemArgs {
  id: string;
  locationId?: string;
  price: MoneyInput;
  quantity: number;
  requiresShipping?: boolean;
  taxable?: boolean;
  title: string;
}

export async function orderEditAddCustomItem(args: OrderEditAddCustomItemArgs): Promise<OrderEditAddCustomItemPayload> {
  const gql = `#graphql
    mutation orderEditAddCustomItem($id: ID!, $locationId: ID, $price: MoneyInput!, $quantity: Int!, $requiresShipping: Boolean, $taxable: Boolean, $title: String!) {
      orderEditAddCustomItem(id: $id, locationId: $locationId, price: $price, quantity: $quantity, requiresShipping: $requiresShipping, taxable: $taxable, title: $title) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditAddCustomItem: OrderEditAddCustomItemPayload }>(gql, args);
  return data.orderEditAddCustomItem;
}

/**
 * Applies a discount to a LineItem during an order edit session. The discount can be either a fixed amount or percentage value.
 * @scope write_order_edits
 */
export interface OrderEditAddLineItemDiscountArgs {
  discount: OrderEditAppliedDiscountInput;
  id: string;
  lineItemId: string;
}

export async function orderEditAddLineItemDiscount(args: OrderEditAddLineItemDiscountArgs): Promise<OrderEditAddLineItemDiscountPayload> {
  const gql = `#graphql
    mutation orderEditAddLineItemDiscount($discount: OrderEditAppliedDiscountInput!, $id: ID!, $lineItemId: ID!) {
      orderEditAddLineItemDiscount(discount: $discount, id: $id, lineItemId: $lineItemId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditAddLineItemDiscount: OrderEditAddLineItemDiscountPayload }>(gql, args);
  return data.orderEditAddLineItemDiscount;
}

/**
 * Adds a custom shipping line to an Order during an edit session. Specify the shipping title and price to create a new ShippingLine.
 * @scope write_order_edits
 */
export interface OrderEditAddShippingLineArgs {
  id: string;
  shippingLine: OrderEditAddShippingLineInput;
}

export async function orderEditAddShippingLine(args: OrderEditAddShippingLineArgs): Promise<OrderEditAddShippingLinePayload> {
  const gql = `#graphql
    mutation orderEditAddShippingLine($id: ID!, $shippingLine: OrderEditAddShippingLineInput!) {
      orderEditAddShippingLine(id: $id, shippingLine: $shippingLine) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditAddShippingLine: OrderEditAddShippingLinePayload }>(gql, args);
  return data.orderEditAddShippingLine;
}

/**
 * Adds a ProductVariant as a line item to an Order that's being edited. The mutation respects the variant's contextual pricing.
 * @scope write_order_edits
 */
export interface OrderEditAddVariantArgs {
  allowDuplicates?: boolean;
  id: string;
  locationId?: string;
  quantity: number;
  variantId: string;
}

export async function orderEditAddVariant(args: OrderEditAddVariantArgs): Promise<OrderEditAddVariantPayload> {
  const gql = `#graphql
    mutation orderEditAddVariant($allowDuplicates: Boolean, $id: ID!, $locationId: ID, $quantity: Int!, $variantId: ID!) {
      orderEditAddVariant(allowDuplicates: $allowDuplicates, id: $id, locationId: $locationId, quantity: $quantity, variantId: $variantId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditAddVariant: OrderEditAddVariantPayload }>(gql, args);
  return data.orderEditAddVariant;
}

/**
 * Starts an order editing session that enables you to modify an existing Order. This mutation creates an OrderEditSession and returns a CalculatedOrder showing how the order looks with your changes applied.
 * @scope write_order_edits
 */
export interface OrderEditBeginArgs {
  id: string;
}

export async function orderEditBegin(args: OrderEditBeginArgs): Promise<OrderEditBeginPayload> {
  const gql = `#graphql
    mutation orderEditBegin($id: ID!) {
      orderEditBegin(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditBegin: OrderEditBeginPayload }>(gql, args);
  return data.orderEditBegin;
}

/**
 * Applies staged changes from an order editing session to the original order. This finalizes all modifications made during the edit session, including changes to line items, quantities, discounts, and shipping lines.
 * @scope write_order_edits
 */
export interface OrderEditCommitArgs {
  id: string;
  notifyCustomer?: boolean;
  staffNote?: string;
}

export async function orderEditCommit(args: OrderEditCommitArgs): Promise<OrderEditCommitPayload> {
  const gql = `#graphql
    mutation orderEditCommit($id: ID!, $notifyCustomer: Boolean, $staffNote: String) {
      orderEditCommit(id: $id, notifyCustomer: $notifyCustomer, staffNote: $staffNote) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditCommit: OrderEditCommitPayload }>(gql, args);
  return data.orderEditCommit;
}

/**
 * Removes a discount on the current order edit. For more information on how to use the GraphQL Admin API to edit an existing order, refer to Edit existing orders.
 * @scope write_order_edits
 */
export interface OrderEditRemoveDiscountArgs {
  discountApplicationId: string;
  id: string;
}

export async function orderEditRemoveDiscount(args: OrderEditRemoveDiscountArgs): Promise<OrderEditRemoveDiscountPayload> {
  const gql = `#graphql
    mutation orderEditRemoveDiscount($discountApplicationId: ID!, $id: ID!) {
      orderEditRemoveDiscount(discountApplicationId: $discountApplicationId, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditRemoveDiscount: OrderEditRemoveDiscountPayload }>(gql, args);
  return data.orderEditRemoveDiscount;
}

/**
 * Removes a line item discount that was applied as part of an order edit.
 * @scope write_order_edits
 */
export interface OrderEditRemoveLineItemDiscountArgs {
  discountApplicationId: string;
  id: string;
}

export async function orderEditRemoveLineItemDiscount(args: OrderEditRemoveLineItemDiscountArgs): Promise<OrderEditRemoveLineItemDiscountPayload> {
  const gql = `#graphql
    mutation orderEditRemoveLineItemDiscount($discountApplicationId: ID!, $id: ID!) {
      orderEditRemoveLineItemDiscount(discountApplicationId: $discountApplicationId, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditRemoveLineItemDiscount: OrderEditRemoveLineItemDiscountPayload }>(gql, args);
  return data.orderEditRemoveLineItemDiscount;
}

/**
 * Removes a shipping line from an existing order. For more information on how to use the GraphQL Admin API to edit an existing order, refer to Edit existing orders.
 * @scope write_order_edits
 */
export interface OrderEditRemoveShippingLineArgs {
  id: string;
  shippingLineId: string;
}

export async function orderEditRemoveShippingLine(args: OrderEditRemoveShippingLineArgs): Promise<OrderEditRemoveShippingLinePayload> {
  const gql = `#graphql
    mutation orderEditRemoveShippingLine($id: ID!, $shippingLineId: ID!) {
      orderEditRemoveShippingLine(id: $id, shippingLineId: $shippingLineId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditRemoveShippingLine: OrderEditRemoveShippingLinePayload }>(gql, args);
  return data.orderEditRemoveShippingLine;
}

/**
 * Sets the quantity of a line item on an order that's being edited. Use this mutation to increase, decrease, or remove items by adjusting their quantities.
 * @scope write_order_edits
 */
export interface OrderEditSetQuantityArgs {
  id: string;
  lineItemId: string;
  quantity: number;
  restock?: boolean;
  locationId?: string;
}

export async function orderEditSetQuantity(args: OrderEditSetQuantityArgs): Promise<OrderEditSetQuantityPayload> {
  const gql = `#graphql
    mutation orderEditSetQuantity($id: ID!, $lineItemId: ID!, $quantity: Int!, $restock: Boolean, $locationId: ID) {
      orderEditSetQuantity(id: $id, lineItemId: $lineItemId, quantity: $quantity, restock: $restock, locationId: $locationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditSetQuantity: OrderEditSetQuantityPayload }>(gql, args);
  return data.orderEditSetQuantity;
}

/**
 * Updates a manual line level discount on the current order edit. For more information on how to use the GraphQL Admin API to edit an existing order, refer to Edit existing orders.
 * @scope write_order_edits
 */
export interface OrderEditUpdateDiscountArgs {
  discount: OrderEditAppliedDiscountInput;
  discountApplicationId: string;
  id: string;
}

export async function orderEditUpdateDiscount(args: OrderEditUpdateDiscountArgs): Promise<OrderEditUpdateDiscountPayload> {
  const gql = `#graphql
    mutation orderEditUpdateDiscount($discount: OrderEditAppliedDiscountInput!, $discountApplicationId: ID!, $id: ID!) {
      orderEditUpdateDiscount(discount: $discount, discountApplicationId: $discountApplicationId, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditUpdateDiscount: OrderEditUpdateDiscountPayload }>(gql, args);
  return data.orderEditUpdateDiscount;
}

/**
 * Updates a shipping line on the current order edit. For more information on how to use the GraphQL Admin API to edit an existing order, refer to Edit existing orders.
 * @scope write_order_edits
 */
export interface OrderEditUpdateShippingLineArgs {
  id: string;
  shippingLine: OrderEditUpdateShippingLineInput;
  shippingLineId: string;
}

export async function orderEditUpdateShippingLine(args: OrderEditUpdateShippingLineArgs): Promise<OrderEditUpdateShippingLinePayload> {
  const gql = `#graphql
    mutation orderEditUpdateShippingLine($id: ID!, $shippingLine: OrderEditUpdateShippingLineInput!, $shippingLineId: ID!) {
      orderEditUpdateShippingLine(id: $id, shippingLine: $shippingLine, shippingLineId: $shippingLineId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderEditUpdateShippingLine: OrderEditUpdateShippingLinePayload }>(gql, args);
  return data.orderEditUpdateShippingLine;
}

/**
 * Sends an email invoice for an Order.
 * @scope write_orders
 */
export interface OrderInvoiceSendArgs {
  email?: EmailInput;
  id: string;
}

export async function orderInvoiceSend(args: OrderInvoiceSendArgs): Promise<OrderInvoiceSendPayload> {
  const gql = `#graphql
    mutation orderInvoiceSend($email: EmailInput, $id: ID!) {
      orderInvoiceSend(email: $email, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderInvoiceSend: OrderInvoiceSendPayload }>(gql, args);
  return data.orderInvoiceSend;
}

/**
 * Marks an order as paid by recording a payment transaction for the outstanding amount.
 * @scope write_orders
 */
export interface OrderMarkAsPaidArgs {
  input: OrderMarkAsPaidInput;
}

export async function orderMarkAsPaid(args: OrderMarkAsPaidArgs): Promise<OrderMarkAsPaidPayload> {
  const gql = `#graphql
    mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
      orderMarkAsPaid(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderMarkAsPaid: OrderMarkAsPaidPayload }>(gql, args);
  return data.orderMarkAsPaid;
}

/**
 * Opens a closed order.
 * @scope write_orders
 */
export interface OrderOpenArgs {
  input: OrderOpenInput;
}

export async function orderOpen(args: OrderOpenArgs): Promise<OrderOpenPayload> {
  const gql = `#graphql
    mutation orderOpen($input: OrderOpenInput!) {
      orderOpen(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderOpen: OrderOpenPayload }>(gql, args);
  return data.orderOpen;
}

/**
 * Creates a fraud risk assessment for a specific order, evaluating the likelihood that the order is fraudulent based on various risk signals. Use this to trigger risk analysis on orders that need manual review or to integrate custom risk scoring into order processing workflows.
 * @scope write_orders
 */
export interface OrderRiskAssessmentCreateArgs {
  orderRiskAssessmentInput: OrderRiskAssessmentCreateInput;
}

export async function orderRiskAssessmentCreate(args: OrderRiskAssessmentCreateArgs): Promise<OrderRiskAssessmentCreatePayload> {
  const gql = `#graphql
    mutation orderRiskAssessmentCreate($orderRiskAssessmentInput: OrderRiskAssessmentCreateInput!) {
      orderRiskAssessmentCreate(orderRiskAssessmentInput: $orderRiskAssessmentInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderRiskAssessmentCreate: OrderRiskAssessmentCreatePayload }>(gql, args);
  return data.orderRiskAssessmentCreate;
}

/**
 * Updates the attributes of an order, such as the customer's email, the shipping address for the order,
 * @scope write_orders
 */
export interface OrderUpdateArgs {
  input: OrderInput;
}

export async function orderUpdate(args: OrderUpdateArgs): Promise<OrderUpdatePayload> {
  const gql = `#graphql
    mutation orderUpdate($input: OrderInput!) {
      orderUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ orderUpdate: OrderUpdatePayload }>(gql, args);
  return data.orderUpdate;
}

/**
 * Sends an email payment reminder for a payment schedule.
 * @scope write_orders
 */
export interface PaymentReminderSendArgs {
  paymentScheduleId: string;
}

export async function paymentReminderSend(args: PaymentReminderSendArgs): Promise<PaymentReminderSendPayload> {
  const gql = `#graphql
    mutation paymentReminderSend($paymentScheduleId: ID!) {
      paymentReminderSend(paymentScheduleId: $paymentScheduleId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentReminderSend: PaymentReminderSendPayload }>(gql, args);
  return data.paymentReminderSend;
}

/**
 * Create payment terms on an order. To create payment terms on a draft order, use a draft order mutation and include the request with the DraftOrderInput.
 * @scope write_payment_terms
 */
export interface PaymentTermsCreateArgs {
  paymentTermsAttributes: PaymentTermsCreateInput;
  referenceId: string;
}

export async function paymentTermsCreate(args: PaymentTermsCreateArgs): Promise<PaymentTermsCreatePayload> {
  const gql = `#graphql
    mutation paymentTermsCreate($paymentTermsAttributes: PaymentTermsCreateInput!, $referenceId: ID!) {
      paymentTermsCreate(paymentTermsAttributes: $paymentTermsAttributes, referenceId: $referenceId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentTermsCreate: PaymentTermsCreatePayload }>(gql, args);
  return data.paymentTermsCreate;
}

/**
 * Delete payment terms for an order. To delete payment terms on a draft order, use a draft order mutation and include the request with the DraftOrderInput.
 * @scope write_payment_terms
 */
export interface PaymentTermsDeleteArgs {
  input: PaymentTermsDeleteInput;
}

export async function paymentTermsDelete(args: PaymentTermsDeleteArgs): Promise<PaymentTermsDeletePayload> {
  const gql = `#graphql
    mutation paymentTermsDelete($input: PaymentTermsDeleteInput!) {
      paymentTermsDelete(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentTermsDelete: PaymentTermsDeletePayload }>(gql, args);
  return data.paymentTermsDelete;
}

/**
 * Update payment terms on an order. To update payment terms on a draft order, use a draft order mutation and include the request with the DraftOrderInput.
 * @scope write_payment_terms
 */
export interface PaymentTermsUpdateArgs {
  input: PaymentTermsUpdateInput;
}

export async function paymentTermsUpdate(args: PaymentTermsUpdateArgs): Promise<PaymentTermsUpdatePayload> {
  const gql = `#graphql
    mutation paymentTermsUpdate($input: PaymentTermsUpdateInput!) {
      paymentTermsUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentTermsUpdate: PaymentTermsUpdatePayload }>(gql, args);
  return data.paymentTermsUpdate;
}

/**
 * Creates a refund for an order, allowing you to process returns and issue payments back to customers.
 * @scope orders
 */
export interface RefundCreateArgs {
  input: RefundInput;
}

export async function refundCreate(args: RefundCreateArgs): Promise<RefundCreatePayload> {
  const gql = `#graphql
    mutation refundCreate($input: RefundInput!) {
      refundCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ refundCreate: RefundCreatePayload }>(gql, args);
  return data.refundCreate;
}

/**
 * Removes return and/or exchange lines from a return.
 * @scope write_returns
 */
export interface RemoveFromReturnArgs {
  exchangeLineItems?: unknown;
  returnId: string;
  returnLineItems?: unknown;
}

export async function removeFromReturn(args: RemoveFromReturnArgs): Promise<RemoveFromReturnPayload> {
  const gql = `#graphql
    mutation removeFromReturn($exchangeLineItems: String, $returnId: ID!, $returnLineItems: String) {
      removeFromReturn(exchangeLineItems: $exchangeLineItems, returnId: $returnId, returnLineItems: $returnLineItems) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ removeFromReturn: RemoveFromReturnPayload }>(gql, args);
  return data.removeFromReturn;
}

/**
 * |-
 * @scope write_returns
 */
export interface ReturnApproveRequestArgs {
  input: ReturnApproveRequestInput;
}

export async function returnApproveRequest(args: ReturnApproveRequestArgs): Promise<ReturnApproveRequestPayload> {
  const gql = `#graphql
    mutation returnApproveRequest($input: ReturnApproveRequestInput!) {
      returnApproveRequest(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnApproveRequest: ReturnApproveRequestPayload }>(gql, args);
  return data.returnApproveRequest;
}

/**
 * |-
 * @scope write_returns
 */
export interface ReturnCancelArgs {
  id: string;
  notifyCustomer?: boolean;
}

export async function returnCancel(args: ReturnCancelArgs): Promise<ReturnCancelPayload> {
  const gql = `#graphql
    mutation returnCancel($id: ID!, $notifyCustomer: Boolean) {
      returnCancel(id: $id, notifyCustomer: $notifyCustomer) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnCancel: ReturnCancelPayload }>(gql, args);
  return data.returnCancel;
}

/**
 * Indicates a return is complete, either when a refund has been made and items restocked,
 * @scope write_returns
 */
export interface ReturnCloseArgs {
  id: string;
}

export async function returnClose(args: ReturnCloseArgs): Promise<ReturnClosePayload> {
  const gql = `#graphql
    mutation returnClose($id: ID!) {
      returnClose(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnClose: ReturnClosePayload }>(gql, args);
  return data.returnClose;
}

/**
 * Creates a return from an existing order that has at least one fulfilled
 * @scope write_returns
 */
export interface ReturnCreateArgs {
  returnInput: ReturnInput;
}

export async function returnCreate(args: ReturnCreateArgs): Promise<ReturnCreatePayload> {
  const gql = `#graphql
    mutation returnCreate($returnInput: ReturnInput!) {
      returnCreate(returnInput: $returnInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnCreate: ReturnCreatePayload }>(gql, args);
  return data.returnCreate;
}

/**
 * Declines a return on an order.
 * @scope write_returns
 */
export interface ReturnDeclineRequestArgs {
  input: ReturnDeclineRequestInput;
}

export async function returnDeclineRequest(args: ReturnDeclineRequestArgs): Promise<ReturnDeclineRequestPayload> {
  const gql = `#graphql
    mutation returnDeclineRequest($input: ReturnDeclineRequestInput!) {
      returnDeclineRequest(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnDeclineRequest: ReturnDeclineRequestPayload }>(gql, args);
  return data.returnDeclineRequest;
}

/**
 * Removes return lines from a return.
 * @scope write_returns
 */
export interface ReturnLineItemRemoveFromReturnArgs {
  returnId: string;
  returnLineItems: unknown;
}

export async function returnLineItemRemoveFromReturn(args: ReturnLineItemRemoveFromReturnArgs): Promise<ReturnLineItemRemoveFromReturnPayload> {
  const gql = `#graphql
    mutation returnLineItemRemoveFromReturn($returnId: ID!, $returnLineItems: String) {
      returnLineItemRemoveFromReturn(returnId: $returnId, returnLineItems: $returnLineItems) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnLineItemRemoveFromReturn: ReturnLineItemRemoveFromReturnPayload }>(gql, args);
  return data.returnLineItemRemoveFromReturn;
}

/**
 * Processes a return by confirming which items customers return and exchange, handling their disposition, and optionally issuing refunds. This mutation confirms the quantities for ReturnLineItem and ExchangeLineItem objects previously created on the Return.
 * @scope write_returns
 */
export interface ReturnProcessArgs {
  input: ReturnProcessInput;
}

export async function returnProcess(args: ReturnProcessArgs): Promise<ReturnProcessPayload> {
  const gql = `#graphql
    mutation returnProcess($input: ReturnProcessInput!) {
      returnProcess(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnProcess: ReturnProcessPayload }>(gql, args);
  return data.returnProcess;
}

/**
 * Creates a refund for items being returned when the return status is OPEN or CLOSED. This mutation processes the financial aspects of a return by refunding line items, shipping costs, and duties back to the customer.
 * @scope write_returns
 */
export interface ReturnRefundArgs {
  returnRefundInput: ReturnRefundInput;
}

export async function returnRefund(args: ReturnRefundArgs): Promise<ReturnRefundPayload> {
  const gql = `#graphql
    mutation returnRefund($returnRefundInput: ReturnRefundInput!) {
      returnRefund(returnRefundInput: $returnRefundInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnRefund: ReturnRefundPayload }>(gql, args);
  return data.returnRefund;
}

/**
 * Reopens a closed return.
 * @scope write_returns
 */
export interface ReturnReopenArgs {
  id: string;
}

export async function returnReopen(args: ReturnReopenArgs): Promise<ReturnReopenPayload> {
  const gql = `#graphql
    mutation returnReopen($id: ID!) {
      returnReopen(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnReopen: ReturnReopenPayload }>(gql, args);
  return data.returnReopen;
}

/**
 * Creates a return request that requires merchant approval before processing. The return has its status set to REQUESTED and the merchant must approve or decline it.
 * @scope write_returns
 */
export interface ReturnRequestArgs {
  input: ReturnRequestInput;
}

export async function returnRequest(args: ReturnRequestArgs): Promise<ReturnRequestPayload> {
  const gql = `#graphql
    mutation returnRequest($input: ReturnRequestInput!) {
      returnRequest(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ returnRequest: ReturnRequestPayload }>(gql, args);
  return data.returnRequest;
}

/**
 * Creates a new reverse delivery with associated external shipping information.
 * @scope write_returns
 */
export interface ReverseDeliveryCreateWithShippingArgs {
  labelInput?: ReverseDeliveryLabelInput;
  notifyCustomer?: boolean;
  reverseDeliveryLineItems: unknown;
  reverseFulfillmentOrderId: string;
  trackingInput?: ReverseDeliveryTrackingInput;
}

export async function reverseDeliveryCreateWithShipping(args: ReverseDeliveryCreateWithShippingArgs): Promise<ReverseDeliveryCreateWithShippingPayload> {
  const gql = `#graphql
    mutation reverseDeliveryCreateWithShipping($labelInput: ReverseDeliveryLabelInput, $notifyCustomer: Boolean, $reverseDeliveryLineItems: String, $reverseFulfillmentOrderId: ID!, $trackingInput: ReverseDeliveryTrackingInput) {
      reverseDeliveryCreateWithShipping(labelInput: $labelInput, notifyCustomer: $notifyCustomer, reverseDeliveryLineItems: $reverseDeliveryLineItems, reverseFulfillmentOrderId: $reverseFulfillmentOrderId, trackingInput: $trackingInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ reverseDeliveryCreateWithShipping: ReverseDeliveryCreateWithShippingPayload }>(gql, args);
  return data.reverseDeliveryCreateWithShipping;
}

/**
 * Updates a reverse delivery with associated external shipping information.
 * @scope write_returns
 */
export interface ReverseDeliveryShippingUpdateArgs {
  labelInput?: ReverseDeliveryLabelInput;
  notifyCustomer?: boolean;
  reverseDeliveryId: string;
  trackingInput?: ReverseDeliveryTrackingInput;
}

export async function reverseDeliveryShippingUpdate(args: ReverseDeliveryShippingUpdateArgs): Promise<ReverseDeliveryShippingUpdatePayload> {
  const gql = `#graphql
    mutation reverseDeliveryShippingUpdate($labelInput: ReverseDeliveryLabelInput, $notifyCustomer: Boolean, $reverseDeliveryId: ID!, $trackingInput: ReverseDeliveryTrackingInput) {
      reverseDeliveryShippingUpdate(labelInput: $labelInput, notifyCustomer: $notifyCustomer, reverseDeliveryId: $reverseDeliveryId, trackingInput: $trackingInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ reverseDeliveryShippingUpdate: ReverseDeliveryShippingUpdatePayload }>(gql, args);
  return data.reverseDeliveryShippingUpdate;
}

/**
 * Disposes reverse fulfillment order line items.
 * @scope write_returns
 */
export interface ReverseFulfillmentOrderDisposeArgs {
  dispositionInputs: unknown;
}

export async function reverseFulfillmentOrderDispose(args: ReverseFulfillmentOrderDisposeArgs): Promise<ReverseFulfillmentOrderDisposePayload> {
  const gql = `#graphql
    mutation reverseFulfillmentOrderDispose($dispositionInputs: String) {
      reverseFulfillmentOrderDispose(dispositionInputs: $dispositionInputs) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ reverseFulfillmentOrderDispose: ReverseFulfillmentOrderDisposePayload }>(gql, args);
  return data.reverseFulfillmentOrderDispose;
}

/**
 * Trigger the voiding of an uncaptured authorization transaction.
 * @scope write_orders
 */
export interface TransactionVoidArgs {
  parentTransactionId: string;
}

export async function transactionVoid(args: TransactionVoidArgs): Promise<TransactionVoidPayload> {
  const gql = `#graphql
    mutation transactionVoid($parentTransactionId: ID!) {
      transactionVoid(parentTransactionId: $parentTransactionId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ transactionVoid: TransactionVoidPayload }>(gql, args);
  return data.transactionVoid;
}










