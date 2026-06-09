import { shopifyClient } from './client';
import type { CashDrawer, CashDrawerConnection, CashDrawerCreatePayload, CashDrawerFindOrCreatePayload, CashDrawerUpdateInput, CashDrawerUpdatePayload, CashManagementReasonCodeConnection, CashManagementReasonCodeCreatePayload, CashManagementReasonCodeDeletePayload, CashManagementSummary, CashTrackingSession, CashTrackingSessionConnection, CashTrackingSessionsSortKeys, CurrencyCode, MoneyInput, PaymentCustomization, PaymentCustomizationActivationPayload, PaymentCustomizationConnection, PaymentCustomizationCreatePayload, PaymentCustomizationDeletePayload, PaymentCustomizationInput, PaymentCustomizationUpdatePayload, PointOfSaleDevice, PointOfSaleDeviceAssignToCashDrawerPayload, PointOfSaleDevicePaymentSession, PointOfSaleDevicePaymentSessionAdjustPayload, PointOfSaleDevicePaymentSessionClosePayload, PointOfSaleDevicePaymentSessionConnection, PointOfSaleDevicePaymentSessionCountPayload, PointOfSaleDevicePaymentSessionOpenPayload, PointOfSaleDevicePaymentSessionSortKeys } from './types';

// ============================================================
// Retail
// 26 operations: 12 queries, 14 mutations
// ============================================================

// These are passed as plain objects. See Shopify docs for field shapes:

// ─── Queries ─────────────────────────────────────────────────────────

/**
 * Returns a CashDrawer resource by ID.
 * @scope read_cash_tracking
 */
export interface CashDrawerArgs {
  id: string;
}

export async function cashDrawer(args: CashDrawerArgs): Promise<CashDrawer | null> {
  const gql = `#graphql
    query cashDrawer($id: ID!) {
      cashDrawer(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashDrawer: CashDrawer | null }>(gql, args);
  return data.cashDrawer;
}

/**
 * A list of cash drawers in the shop.
 * @scope read_cash_tracking
 */
export interface CashDrawersArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
}

export async function cashDrawers(args?: CashDrawersArgs): Promise<CashDrawerConnection> {
  const gql = `#graphql
    query cashDrawers($after: String, $before: String, $first: Int, $last: Int, $query: String) {
      cashDrawers(after: $after, before: $before, first: $first, last: $last, query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashDrawers: CashDrawerConnection }>(gql, args);
  return data.cashDrawers;
}

/**
 * Summary of cash management data for a location.
 * @scope read_cash_tracking
 */
export interface CashManagementLocationSummaryArgs {
  endDate: string;
  locationId: string;
  startDate: string;
}

export async function cashManagementLocationSummary(args: CashManagementLocationSummaryArgs): Promise<CashManagementSummary | null> {
  const gql = `#graphql
    query cashManagementLocationSummary($endDate: Date!, $locationId: ID!, $startDate: Date!) {
      cashManagementLocationSummary(endDate: $endDate, locationId: $locationId, startDate: $startDate) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashManagementLocationSummary: CashManagementSummary | null }>(gql, args);
  return data.cashManagementLocationSummary;
}

/**
 * Returns the cash management reason codes for the shop.
 * @scope read_cash_tracking
 */
export interface CashManagementReasonCodesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function cashManagementReasonCodes(args?: CashManagementReasonCodesArgs): Promise<CashManagementReasonCodeConnection> {
  const gql = `#graphql
    query cashManagementReasonCodes($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      cashManagementReasonCodes(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashManagementReasonCodes: CashManagementReasonCodeConnection }>(gql, args);
  return data.cashManagementReasonCodes;
}

/**
 * Summary of cash management data across all locations with a POS Pro subscription for a shop, filtered by currency.
 * @scope read_cash_tracking
 */
export interface CashManagementShopSummaryArgs {
  currencyCode: CurrencyCode;
  endDate: string;
  startDate: string;
}

export async function cashManagementShopSummary(args: CashManagementShopSummaryArgs): Promise<CashManagementSummary | null> {
  const gql = `#graphql
    query cashManagementShopSummary($currencyCode: CurrencyCode!, $endDate: Date!, $startDate: Date!) {
      cashManagementShopSummary(currencyCode: $currencyCode, endDate: $endDate, startDate: $startDate) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashManagementShopSummary: CashManagementSummary | null }>(gql, args);
  return data.cashManagementShopSummary;
}

/**
 * Returns a CashTrackingSession resource by ID.
 */
export interface CashTrackingSessionArgs {
  id: string;
}

export async function cashTrackingSession(args: CashTrackingSessionArgs): Promise<CashTrackingSession | null> {
  const gql = `#graphql
    query cashTrackingSession($id: ID!) {
      cashTrackingSession(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashTrackingSession: CashTrackingSession | null }>(gql, args);
  return data.cashTrackingSession;
}

/**
 * Returns a shop's cash tracking sessions for locations with a POS Pro subscription.
 */
export interface CashTrackingSessionsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: CashTrackingSessionsSortKeys;
}

export async function cashTrackingSessions(args?: CashTrackingSessionsArgs): Promise<CashTrackingSessionConnection> {
  const gql = `#graphql
    query cashTrackingSessions($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CashTrackingSessionsSortKeys) {
      cashTrackingSessions(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashTrackingSessions: CashTrackingSessionConnection }>(gql, args);
  return data.cashTrackingSessions;
}

/**
 * The payment customization.
 * @scope read_payment_customizations
 */
export interface PaymentCustomizationArgs {
  id: string;
}

export async function paymentCustomization(args: PaymentCustomizationArgs): Promise<PaymentCustomization | null> {
  const gql = `#graphql
    query paymentCustomization($id: ID!) {
      paymentCustomization(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentCustomization: PaymentCustomization | null }>(gql, args);
  return data.paymentCustomization;
}

/**
 * The payment customizations.
 * @scope read_payment_customizations
 */
export interface PaymentCustomizationsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
}

export async function paymentCustomizations(args?: PaymentCustomizationsArgs): Promise<PaymentCustomizationConnection> {
  const gql = `#graphql
    query paymentCustomizations($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean) {
      paymentCustomizations(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentCustomizations: PaymentCustomizationConnection }>(gql, args);
  return data.paymentCustomizations;
}

/**
 * Returns a PointOfSaleDevice resource by ID.
 */
export interface PointOfSaleDeviceArgs {
  id: string;
}

export async function pointOfSaleDevice(args: PointOfSaleDeviceArgs): Promise<PointOfSaleDevice | null> {
  const gql = `#graphql
    query pointOfSaleDevice($id: ID!) {
      pointOfSaleDevice(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pointOfSaleDevice: PointOfSaleDevice | null }>(gql, args);
  return data.pointOfSaleDevice;
}

/**
 * Lookup a point of sale device payment session by ID.
 */
export interface PointOfSaleDevicePaymentSessionArgs {
  id: string;
}

export async function pointOfSaleDevicePaymentSession(args: PointOfSaleDevicePaymentSessionArgs): Promise<PointOfSaleDevicePaymentSession | null> {
  const gql = `#graphql
    query pointOfSaleDevicePaymentSession($id: ID!) {
      pointOfSaleDevicePaymentSession(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pointOfSaleDevicePaymentSession: PointOfSaleDevicePaymentSession | null }>(gql, args);
  return data.pointOfSaleDevicePaymentSession;
}

/**
 * A list of point of sale device payment sessions in the shop.
 * @scope read_cash_tracking
 */
export interface PointOfSaleDevicePaymentSessionsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: PointOfSaleDevicePaymentSessionSortKeys;
}

export async function pointOfSaleDevicePaymentSessions(args?: PointOfSaleDevicePaymentSessionsArgs): Promise<PointOfSaleDevicePaymentSessionConnection> {
  const gql = `#graphql
    query pointOfSaleDevicePaymentSessions($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: PointOfSaleDevicePaymentSessionSortKeys) {
      pointOfSaleDevicePaymentSessions(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pointOfSaleDevicePaymentSessions: PointOfSaleDevicePaymentSessionConnection }>(gql, args);
  return data.pointOfSaleDevicePaymentSessions;
}

// ─── Mutations ─────────────────────────────────────────────────────────

/**
 * Creates a cash drawer in a provided location.
 * @scope write_cash_tracking
 */
export interface CashDrawerCreateArgs {
  locationId: string;
  name: string;
}

export async function cashDrawerCreate(args: CashDrawerCreateArgs): Promise<CashDrawerCreatePayload> {
  const gql = `#graphql
    mutation cashDrawerCreate($locationId: ID!, $name: String!) {
      cashDrawerCreate(locationId: $locationId, name: $name) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashDrawerCreate: CashDrawerCreatePayload }>(gql, args);
  return data.cashDrawerCreate;
}

/**
 * Finds or creates a cash drawer for cash management. Also ensures the provided device is assigned to the drawer.
 * @scope write_cash_tracking
 */
export interface CashDrawerFindOrCreateArgs {
  locationId: string;
  name: string;
  pointOfSaleDeviceId: string;
}

export async function cashDrawerFindOrCreate(args: CashDrawerFindOrCreateArgs): Promise<CashDrawerFindOrCreatePayload> {
  const gql = `#graphql
    mutation cashDrawerFindOrCreate($locationId: ID!, $name: String!, $pointOfSaleDeviceId: ID!) {
      cashDrawerFindOrCreate(locationId: $locationId, name: $name, pointOfSaleDeviceId: $pointOfSaleDeviceId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashDrawerFindOrCreate: CashDrawerFindOrCreatePayload }>(gql, args);
  return data.cashDrawerFindOrCreate;
}

/**
 * Updates a cash drawer.
 * @scope write_cash_tracking
 */
export interface CashDrawerUpdateArgs {
  id: string;
  input: CashDrawerUpdateInput;
}

export async function cashDrawerUpdate(args: CashDrawerUpdateArgs): Promise<CashDrawerUpdatePayload> {
  const gql = `#graphql
    mutation cashDrawerUpdate($id: ID!, $input: CashDrawerUpdateInput!) {
      cashDrawerUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashDrawerUpdate: CashDrawerUpdatePayload }>(gql, args);
  return data.cashDrawerUpdate;
}

/**
 * Create a cash management reason code.
 * @scope write_cash_tracking
 */
export interface CashManagementReasonCodeCreateArgs {
  code: string;
}

export async function cashManagementReasonCodeCreate(args: CashManagementReasonCodeCreateArgs): Promise<CashManagementReasonCodeCreatePayload> {
  const gql = `#graphql
    mutation cashManagementReasonCodeCreate($code: String!) {
      cashManagementReasonCodeCreate(code: $code) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashManagementReasonCodeCreate: CashManagementReasonCodeCreatePayload }>(gql, args);
  return data.cashManagementReasonCodeCreate;
}

/**
 * Deletes a cash management reason code.
 * @scope write_cash_tracking
 */
export interface CashManagementReasonCodeDeleteArgs {
  id: string;
}

export async function cashManagementReasonCodeDelete(args: CashManagementReasonCodeDeleteArgs): Promise<CashManagementReasonCodeDeletePayload> {
  const gql = `#graphql
    mutation cashManagementReasonCodeDelete($id: ID!) {
      cashManagementReasonCodeDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ cashManagementReasonCodeDelete: CashManagementReasonCodeDeletePayload }>(gql, args);
  return data.cashManagementReasonCodeDelete;
}

/**
 * Activates or deactivates payment customizations for the shop. Payment customizations allow apps to hide, reorder, or rename payment methods at checkout based on cart contents, customer attributes, or other conditions. Use this to toggle customizations on or off without deleting them.
 * @scope write_payment_customizations
 */
export interface PaymentCustomizationActivationArgs {
  enabled: boolean;
  ids: unknown;
}

export async function paymentCustomizationActivation(args: PaymentCustomizationActivationArgs): Promise<PaymentCustomizationActivationPayload> {
  const gql = `#graphql
    mutation paymentCustomizationActivation($enabled: Boolean!, $ids: String) {
      paymentCustomizationActivation(enabled: $enabled, ids: $ids) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentCustomizationActivation: PaymentCustomizationActivationPayload }>(gql, args);
  return data.paymentCustomizationActivation;
}

/**
 * Creates a new payment customization for the shop. Payment customizations let apps modify the payment methods shown at checkout â€” hiding, reordering, or renaming options based on cart contents, customer attributes, or other business logic.
 * @scope write_payment_customizations
 */
export interface PaymentCustomizationCreateArgs {
  paymentCustomization: PaymentCustomizationInput;
}

export async function paymentCustomizationCreate(args: PaymentCustomizationCreateArgs): Promise<PaymentCustomizationCreatePayload> {
  const gql = `#graphql
    mutation paymentCustomizationCreate($paymentCustomization: PaymentCustomizationInput!) {
      paymentCustomizationCreate(paymentCustomization: $paymentCustomization) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentCustomizationCreate: PaymentCustomizationCreatePayload }>(gql, args);
  return data.paymentCustomizationCreate;
}

/**
 * Permanently deletes a payment customization. Once deleted, the customization will no longer affect which payment methods appear at checkout.
 * @scope write_payment_customizations
 */
export interface PaymentCustomizationDeleteArgs {
  id: string;
}

export async function paymentCustomizationDelete(args: PaymentCustomizationDeleteArgs): Promise<PaymentCustomizationDeletePayload> {
  const gql = `#graphql
    mutation paymentCustomizationDelete($id: ID!) {
      paymentCustomizationDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentCustomizationDelete: PaymentCustomizationDeletePayload }>(gql, args);
  return data.paymentCustomizationDelete;
}

/**
 * Updates an existing payment customization, modifying its configuration for how payment methods are displayed at checkout. Use this to change the customization's title or enabled state. The customization's function can't be changed once set; create a new payment customization to use a different function.
 * @scope write_payment_customizations
 */
export interface PaymentCustomizationUpdateArgs {
  id: string;
  paymentCustomization: PaymentCustomizationInput;
}

export async function paymentCustomizationUpdate(args: PaymentCustomizationUpdateArgs): Promise<PaymentCustomizationUpdatePayload> {
  const gql = `#graphql
    mutation paymentCustomizationUpdate($id: ID!, $paymentCustomization: PaymentCustomizationInput!) {
      paymentCustomizationUpdate(id: $id, paymentCustomization: $paymentCustomization) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ paymentCustomizationUpdate: PaymentCustomizationUpdatePayload }>(gql, args);
  return data.paymentCustomizationUpdate;
}

/**
 * Assigns a point of sale device to a cash drawer, removing any prior assignment.
 * @scope write_cash_tracking
 */
export interface PointOfSaleDeviceAssignToCashDrawerArgs {
  cashDrawerId: string;
  pointOfSaleDeviceId: string;
}

export async function pointOfSaleDeviceAssignToCashDrawer(args: PointOfSaleDeviceAssignToCashDrawerArgs): Promise<PointOfSaleDeviceAssignToCashDrawerPayload> {
  const gql = `#graphql
    mutation pointOfSaleDeviceAssignToCashDrawer($cashDrawerId: ID!, $pointOfSaleDeviceId: ID!) {
      pointOfSaleDeviceAssignToCashDrawer(cashDrawerId: $cashDrawerId, pointOfSaleDeviceId: $pointOfSaleDeviceId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pointOfSaleDeviceAssignToCashDrawer: PointOfSaleDeviceAssignToCashDrawerPayload }>(gql, args);
  return data.pointOfSaleDeviceAssignToCashDrawer;
}

/**
 * Adds an adjustment to a point of sale device payment session.
 * @scope write_cash_tracking
 */
export interface PointOfSaleDevicePaymentSessionAdjustArgs {
  cash: MoneyInput;
  note?: string;
  pointOfSaleDevicePaymentSessionId: string;
  reasonCodeId?: string;
  staffMemberId: string;
  time?: string;
}

export async function pointOfSaleDevicePaymentSessionAdjust(args: PointOfSaleDevicePaymentSessionAdjustArgs): Promise<PointOfSaleDevicePaymentSessionAdjustPayload> {
  const gql = `#graphql
    mutation pointOfSaleDevicePaymentSessionAdjust($cash: MoneyInput!, $note: String, $pointOfSaleDevicePaymentSessionId: ID!, $reasonCodeId: ID, $staffMemberId: ID!, $time: DateTime) {
      pointOfSaleDevicePaymentSessionAdjust(cash: $cash, note: $note, pointOfSaleDevicePaymentSessionId: $pointOfSaleDevicePaymentSessionId, reasonCodeId: $reasonCodeId, staffMemberId: $staffMemberId, time: $time) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pointOfSaleDevicePaymentSessionAdjust: PointOfSaleDevicePaymentSessionAdjustPayload }>(gql, args);
  return data.pointOfSaleDevicePaymentSessionAdjust;
}

/**
 * Closes a point of sale device payment session.
 * @scope write_cash_tracking
 */
export interface PointOfSaleDevicePaymentSessionCloseArgs {
  balance: MoneyInput;
  note?: string;
  pointOfSaleDevicePaymentSessionId: string;
  reasonCodeId?: string;
  staffMemberId: string;
  time?: string;
}

export async function pointOfSaleDevicePaymentSessionClose(args: PointOfSaleDevicePaymentSessionCloseArgs): Promise<PointOfSaleDevicePaymentSessionClosePayload> {
  const gql = `#graphql
    mutation pointOfSaleDevicePaymentSessionClose($balance: MoneyInput!, $note: String, $pointOfSaleDevicePaymentSessionId: ID!, $reasonCodeId: ID, $staffMemberId: ID!, $time: DateTime) {
      pointOfSaleDevicePaymentSessionClose(balance: $balance, note: $note, pointOfSaleDevicePaymentSessionId: $pointOfSaleDevicePaymentSessionId, reasonCodeId: $reasonCodeId, staffMemberId: $staffMemberId, time: $time) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pointOfSaleDevicePaymentSessionClose: PointOfSaleDevicePaymentSessionClosePayload }>(gql, args);
  return data.pointOfSaleDevicePaymentSessionClose;
}

/**
 * Records a mid-session cash count for a point of sale device payment session.
 * @scope write_cash_tracking
 */
export interface PointOfSaleDevicePaymentSessionCountArgs {
  balance: MoneyInput;
  note?: string;
  pointOfSaleDevicePaymentSessionId: string;
  reasonCodeId?: string;
  staffMemberId: string;
  time?: string;
}

export async function pointOfSaleDevicePaymentSessionCount(args: PointOfSaleDevicePaymentSessionCountArgs): Promise<PointOfSaleDevicePaymentSessionCountPayload> {
  const gql = `#graphql
    mutation pointOfSaleDevicePaymentSessionCount($balance: MoneyInput!, $note: String, $pointOfSaleDevicePaymentSessionId: ID!, $reasonCodeId: ID, $staffMemberId: ID!, $time: DateTime) {
      pointOfSaleDevicePaymentSessionCount(balance: $balance, note: $note, pointOfSaleDevicePaymentSessionId: $pointOfSaleDevicePaymentSessionId, reasonCodeId: $reasonCodeId, staffMemberId: $staffMemberId, time: $time) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pointOfSaleDevicePaymentSessionCount: PointOfSaleDevicePaymentSessionCountPayload }>(gql, args);
  return data.pointOfSaleDevicePaymentSessionCount;
}

/**
 * Opens a point of sale device payment session.
 * @scope write_cash_tracking
 */
export interface PointOfSaleDevicePaymentSessionOpenArgs {
  balance?: MoneyInput;
  note?: string;
  pointOfSaleDeviceId: string;
  reasonCodeId?: string;
  staffMemberId: string;
  time?: string;
}

export async function pointOfSaleDevicePaymentSessionOpen(args: PointOfSaleDevicePaymentSessionOpenArgs): Promise<PointOfSaleDevicePaymentSessionOpenPayload> {
  const gql = `#graphql
    mutation pointOfSaleDevicePaymentSessionOpen($balance: MoneyInput, $note: String, $pointOfSaleDeviceId: ID!, $reasonCodeId: ID, $staffMemberId: ID!, $time: DateTime) {
      pointOfSaleDevicePaymentSessionOpen(balance: $balance, note: $note, pointOfSaleDeviceId: $pointOfSaleDeviceId, reasonCodeId: $reasonCodeId, staffMemberId: $staffMemberId, time: $time) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pointOfSaleDevicePaymentSessionOpen: PointOfSaleDevicePaymentSessionOpenPayload }>(gql, args);
  return data.pointOfSaleDevicePaymentSessionOpen;
}










