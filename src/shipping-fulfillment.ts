import { shopifyClient } from './client';
import type { CarrierServiceCreatePayload, CarrierServiceDeletePayload, CarrierServiceSortKeys, CarrierServiceUpdatePayload, CustomShippingPackageInput, DeliveryCarrierService, DeliveryCarrierServiceConnection, DeliveryCarrierServiceCreateInput, DeliveryCarrierServiceUpdateInput, DeliveryCustomization, DeliveryCustomizationActivationPayload, DeliveryCustomizationConnection, DeliveryCustomizationCreatePayload, DeliveryCustomizationDeletePayload, DeliveryCustomizationInput, DeliveryCustomizationUpdatePayload, DeliveryProfile, DeliveryProfileConnection, DeliveryProfileCreatePayload, DeliveryProfileInput, DeliveryProfileRemovePayload, DeliveryProfileUpdatePayload, DeliveryPromiseParticipantConnection, DeliveryPromiseParticipantsUpdatePayload, DeliveryPromiseProvider, DeliveryPromiseProviderUpsertPayload, DeliveryPromiseSetting, DeliverySettingUpdatePayload, DeliveryShippingOriginAssignPayload, DeliveryZone, Fulfillment, FulfillmentCancelPayload, FulfillmentConstraintRuleCreatePayload, FulfillmentConstraintRuleDeletePayload, FulfillmentConstraintRuleUpdatePayload, FulfillmentCreatePayload, FulfillmentCreateV2Payload, FulfillmentEvent, FulfillmentEventCreatePayload, FulfillmentEventInput, FulfillmentInput, FulfillmentOrder, FulfillmentOrderAcceptCancellationRequestPayload, FulfillmentOrderAcceptFulfillmentRequestPayload, FulfillmentOrderAssignmentStatus, FulfillmentOrderCancelPayload, FulfillmentOrderClosePayload, FulfillmentOrderConnection, FulfillmentOrderHoldInput, FulfillmentOrderHoldPayload, FulfillmentOrderLineItemsPreparedForPickupInput, FulfillmentOrderLineItemsPreparedForPickupPayload, FulfillmentOrderMergePayload, FulfillmentOrderMovePayload, FulfillmentOrderOpenPayload, FulfillmentOrderRejectCancellationRequestPayload, FulfillmentOrderRejectFulfillmentRequestPayload, FulfillmentOrderRejectionReason, FulfillmentOrderReleaseHoldPayload, FulfillmentOrderReportProgressInput, FulfillmentOrderReportProgressPayload, FulfillmentOrderReschedulePayload, FulfillmentOrderSortKeys, FulfillmentOrderSplitPayload, FulfillmentOrdersReroutePayload, FulfillmentOrdersSetFulfillmentDeadlinePayload, FulfillmentOrderSubmitCancellationRequestPayload, FulfillmentOrderSubmitFulfillmentRequestPayload, FulfillmentService, FulfillmentServiceCreatePayload, FulfillmentServiceDeleteInventoryAction, FulfillmentServiceDeletePayload, FulfillmentServiceUpdatePayload, FulfillmentTrackingInfoUpdatePayload, FulfillmentTrackingInfoUpdateV2Payload, FulfillmentTrackingInput, FulfillmentV2Input, LineItem, Location, LocationConnection, Order, Product, ProductVariant, ShippingPackageDeletePayload, ShippingPackageMakeDefaultPayload, ShippingPackageUpdatePayload, ShopifyFunction } from './types';

// ============================================================
// Shipping & Fulfillment
// 67 operations: 19 queries, 48 mutations
// ============================================================

// These are passed as plain objects. See Shopify docs for field shapes:

// ─── Queries ─────────────────────────────────────────────────────────

/**
 * The paginated list of fulfillment orders assigned to the shop locations owned by the app.
 * @scope read_assigned_fulfillment_orders
 */
export interface AssignedFulfillmentOrdersArgs {
  after?: string;
  assignmentStatus?: FulfillmentOrderAssignmentStatus;
  before?: string;
  first?: number;
  last?: number;
  locationIds?: unknown;
  reverse?: boolean;
  sortKey?: FulfillmentOrderSortKeys;
}

export async function assignedFulfillmentOrders(args?: AssignedFulfillmentOrdersArgs): Promise<FulfillmentOrderConnection> {
  const gql = `#graphql
    query assignedFulfillmentOrders($after: String, $assignmentStatus: FulfillmentOrderAssignmentStatus, $before: String, $first: Int, $last: Int, $locationIds: String, $reverse: Boolean, $sortKey: FulfillmentOrderSortKeys) {
      assignedFulfillmentOrders(after: $after, assignmentStatus: $assignmentStatus, before: $before, first: $first, last: $last, locationIds: $locationIds, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ assignedFulfillmentOrders: FulfillmentOrderConnection }>(gql, args);
  return data.assignedFulfillmentOrders;
}

/**
 * Returns a list of activated carrier services and associated shop locations that support them.
 */
export async function availableCarrierServices(): Promise<unknown> {
  const gql = `#graphql
    query availableCarrierServices {
      availableCarrierServices {
        # Specify the fields you need returned
      }
    }
  `;
  return shopifyClient.request(gql);
}

/**
 * Returns a DeliveryCarrierService resource by ID.
 */
export interface CarrierServiceArgs {
  id: string;
}

export async function carrierService(args: CarrierServiceArgs): Promise<DeliveryCarrierService | null> {
  const gql = `#graphql
    query carrierService($id: ID!) {
      carrierService(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ carrierService: DeliveryCarrierService | null }>(gql, args);
  return data.carrierService;
}

/**
 * A paginated list of carrier services configured for the shop. Carrier services provide real-time shipping rates from external providers like FedEx, UPS, or custom shipping solutions. Use the query parameter to filter results by attributes such as active status.
 * @scope read_shipping
 */
export interface CarrierServicesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: CarrierServiceSortKeys;
}

export async function carrierServices(args?: CarrierServicesArgs): Promise<DeliveryCarrierServiceConnection> {
  const gql = `#graphql
    query carrierServices($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CarrierServiceSortKeys) {
      carrierServices(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ carrierServices: DeliveryCarrierServiceConnection }>(gql, args);
  return data.carrierServices;
}

/**
 * The delivery customization.
 * @scope read_delivery_customizations
 */
export interface DeliveryCustomizationArgs {
  id: string;
}

export async function deliveryCustomization(args: DeliveryCustomizationArgs): Promise<DeliveryCustomization | null> {
  const gql = `#graphql
    query deliveryCustomization($id: ID!) {
      deliveryCustomization(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryCustomization: DeliveryCustomization | null }>(gql, args);
  return data.deliveryCustomization;
}

/**
 * The delivery customizations.
 * @scope read_delivery_customizations
 */
export interface DeliveryCustomizationsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
}

export async function deliveryCustomizations(args?: DeliveryCustomizationsArgs): Promise<DeliveryCustomizationConnection> {
  const gql = `#graphql
    query deliveryCustomizations($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean) {
      deliveryCustomizations(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryCustomizations: DeliveryCustomizationConnection }>(gql, args);
  return data.deliveryCustomizations;
}

/**
 * Retrieves a DeliveryProfile by ID. Delivery profiles group shipping settings for specific Product objects that ship from selected Location objects to [delivery zones](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryZone with defined rates.
 */
export interface DeliveryProfileArgs {
  id: string;
}

export async function deliveryProfile(args: DeliveryProfileArgs): Promise<DeliveryProfile | null> {
  const gql = `#graphql
    query deliveryProfile($id: ID!) {
      deliveryProfile(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryProfile: DeliveryProfile | null }>(gql, args);
  return data.deliveryProfile;
}

/**
 * Returns a paginated list of DeliveryProfile objects for the shop. Delivery profiles group Product and ProductVariant objects that share shipping rates and zones.
 */
export interface DeliveryProfilesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  merchantOwnedOnly?: boolean;
  reverse?: boolean;
}

export async function deliveryProfiles(args?: DeliveryProfilesArgs): Promise<DeliveryProfileConnection> {
  const gql = `#graphql
    query deliveryProfiles($after: String, $before: String, $first: Int, $last: Int, $merchantOwnedOnly: Boolean, $reverse: Boolean) {
      deliveryProfiles(after: $after, before: $before, first: $first, last: $last, merchantOwnedOnly: $merchantOwnedOnly, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryProfiles: DeliveryProfileConnection }>(gql, args);
  return data.deliveryProfiles;
}

/**
 * Returns delivery promise participants.
 * @scope read_delivery_promises
 */
export interface DeliveryPromiseParticipantsArgs {
  after?: string;
  before?: string;
  brandedPromiseHandle: string;
  first?: number;
  last?: number;
  ownerIds?: unknown;
  reverse?: boolean;
}

export async function deliveryPromiseParticipants(args: DeliveryPromiseParticipantsArgs): Promise<DeliveryPromiseParticipantConnection> {
  const gql = `#graphql
    query deliveryPromiseParticipants($after: String, $before: String, $brandedPromiseHandle: String!, $first: Int, $last: Int, $ownerIds: String, $reverse: Boolean) {
      deliveryPromiseParticipants(after: $after, before: $before, brandedPromiseHandle: $brandedPromiseHandle, first: $first, last: $last, ownerIds: $ownerIds, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryPromiseParticipants: DeliveryPromiseParticipantConnection }>(gql, args);
  return data.deliveryPromiseParticipants;
}

/**
 * Lookup a delivery promise provider.
 * @scope read_delivery_promises
 */
export interface DeliveryPromiseProviderArgs {
  locationId: string;
}

export async function deliveryPromiseProvider(args: DeliveryPromiseProviderArgs): Promise<DeliveryPromiseProvider | null> {
  const gql = `#graphql
    query deliveryPromiseProvider($locationId: ID!) {
      deliveryPromiseProvider(locationId: $locationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryPromiseProvider: DeliveryPromiseProvider | null }>(gql, args);
  return data.deliveryPromiseProvider;
}

/**
 * Represents the delivery promise settings for a shop.
 * @scope read_shipping
 */
export async function deliveryPromiseSettings(): Promise<DeliveryPromiseSetting | null> {
  const gql = `#graphql
    query deliveryPromiseSettings {
      deliveryPromiseSettings {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryPromiseSettings: DeliveryPromiseSetting | null }>(gql);
  return data.deliveryPromiseSettings;
}

/**
 * Retrieves a Fulfillment by its ID. A fulfillment is a record that the merchant has completed their work required for one or more line items in an Order. It includes tracking information, LineItem objects, and the status of the fulfillment.
 * @scope read_orders
 */
export interface FulfillmentArgs {
  id: string;
}

export async function fulfillment(args: FulfillmentArgs): Promise<Fulfillment | null> {
  const gql = `#graphql
    query fulfillment($id: ID!) {
      fulfillment(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillment: Fulfillment | null }>(gql, args);
  return data.fulfillment;
}

/**
 * The fulfillment constraint rules that belong to a shop.
 * @scope read_fulfillment_constraint_rules
 */
export async function fulfillmentConstraintRules(): Promise<ShopifyFunction | null> {
  const gql = `#graphql
    query fulfillmentConstraintRules {
      fulfillmentConstraintRules {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentConstraintRules: ShopifyFunction | null }>(gql);
  return data.fulfillmentConstraintRules;
}

/**
 * Returns a FulfillmentOrder resource by ID.
 */
export interface FulfillmentOrderArgs {
  id: string;
}

export async function fulfillmentOrder(args: FulfillmentOrderArgs): Promise<FulfillmentOrder | null> {
  const gql = `#graphql
    query fulfillmentOrder($id: ID!) {
      fulfillmentOrder(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrder: FulfillmentOrder | null }>(gql, args);
  return data.fulfillmentOrder;
}

/**
 * The paginated list of all fulfillment orders.
 * @scope read_assigned_fulfillment_orders
 */
export interface FulfillmentOrdersArgs {
  after?: string;
  before?: string;
  first?: number;
  includeClosed?: boolean;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: FulfillmentOrderSortKeys;
}

export async function fulfillmentOrders(args?: FulfillmentOrdersArgs): Promise<FulfillmentOrderConnection> {
  const gql = `#graphql
    query fulfillmentOrders($after: String, $before: String, $first: Int, $includeClosed: Boolean, $last: Int, $query: String, $reverse: Boolean, $sortKey: FulfillmentOrderSortKeys) {
      fulfillmentOrders(after: $after, before: $before, first: $first, includeClosed: $includeClosed, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrders: FulfillmentOrderConnection }>(gql, args);
  return data.fulfillmentOrders;
}

/**
 * Returns a FulfillmentService by its ID. The service can manage inventory, process fulfillment requests, and provide tracking details through callback endpoints or directly calling Shopify's APIs.
 */
export interface FulfillmentServiceArgs {
  id: string;
}

export async function fulfillmentService(args: FulfillmentServiceArgs): Promise<FulfillmentService | null> {
  const gql = `#graphql
    query fulfillmentService($id: ID!) {
      fulfillmentService(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentService: FulfillmentService | null }>(gql, args);
  return data.fulfillmentService;
}

/**
 * Returns a list of all origin locations available for a delivery profile.
 */
export async function locationsAvailableForDeliveryProfiles(): Promise<unknown> {
  const gql = `#graphql
    query locationsAvailableForDeliveryProfiles {
      locationsAvailableForDeliveryProfiles {
        # Specify the fields you need returned
      }
    }
  `;
  return shopifyClient.request(gql);
}

/**
 * Returns a list of all origin locations available for a delivery profile.
 */
export interface LocationsAvailableForDeliveryProfilesConnectionArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function locationsAvailableForDeliveryProfilesConnection(args?: LocationsAvailableForDeliveryProfilesConnectionArgs): Promise<LocationConnection> {
  const gql = `#graphql
    query locationsAvailableForDeliveryProfilesConnection($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      locationsAvailableForDeliveryProfilesConnection(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locationsAvailableForDeliveryProfilesConnection: LocationConnection }>(gql, args);
  return data.locationsAvailableForDeliveryProfilesConnection;
}

/**
 * Returns a list of fulfillment orders that are on hold.
 * @scope read_orders
 */
export interface ManualHoldsFulfillmentOrdersArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
}

export async function manualHoldsFulfillmentOrders(args?: ManualHoldsFulfillmentOrdersArgs): Promise<FulfillmentOrderConnection> {
  const gql = `#graphql
    query manualHoldsFulfillmentOrders($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean) {
      manualHoldsFulfillmentOrders(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ manualHoldsFulfillmentOrders: FulfillmentOrderConnection }>(gql, args);
  return data.manualHoldsFulfillmentOrders;
}

// ─── Mutations ─────────────────────────────────────────────────────────

/**
 * Creates a carrier service that provides real-time shipping rates to Shopify. Carrier services provide real-time shipping rates from external providers like FedEx, UPS, or custom shipping solutions. The carrier service connects to your external shipping rate calculation system through a callback URL.
 * @scope write_shipping
 */
export interface CarrierServiceCreateArgs {
  input: DeliveryCarrierServiceCreateInput;
}

export async function carrierServiceCreate(args: CarrierServiceCreateArgs): Promise<CarrierServiceCreatePayload> {
  const gql = `#graphql
    mutation carrierServiceCreate($input: DeliveryCarrierServiceCreateInput!) {
      carrierServiceCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ carrierServiceCreate: CarrierServiceCreatePayload }>(gql, args);
  return data.carrierServiceCreate;
}

/**
 * Removes an existing carrier service.
 * @scope write_shipping
 */
export interface CarrierServiceDeleteArgs {
  id: string;
}

export async function carrierServiceDelete(args: CarrierServiceDeleteArgs): Promise<CarrierServiceDeletePayload> {
  const gql = `#graphql
    mutation carrierServiceDelete($id: ID!) {
      carrierServiceDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ carrierServiceDelete: CarrierServiceDeletePayload }>(gql, args);
  return data.carrierServiceDelete;
}

/**
 * Updates a carrier service. Only the app that creates a carrier service can update it.
 * @scope write_shipping
 */
export interface CarrierServiceUpdateArgs {
  input: DeliveryCarrierServiceUpdateInput;
}

export async function carrierServiceUpdate(args: CarrierServiceUpdateArgs): Promise<CarrierServiceUpdatePayload> {
  const gql = `#graphql
    mutation carrierServiceUpdate($input: DeliveryCarrierServiceUpdateInput!) {
      carrierServiceUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ carrierServiceUpdate: CarrierServiceUpdatePayload }>(gql, args);
  return data.carrierServiceUpdate;
}

/**
 * Activates and deactivates delivery customizations.
 * @scope write_delivery_customizations
 */
export interface DeliveryCustomizationActivationArgs {
  enabled: boolean;
  ids: unknown;
}

export async function deliveryCustomizationActivation(args: DeliveryCustomizationActivationArgs): Promise<DeliveryCustomizationActivationPayload> {
  const gql = `#graphql
    mutation deliveryCustomizationActivation($enabled: Boolean!, $ids: String) {
      deliveryCustomizationActivation(enabled: $enabled, ids: $ids) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryCustomizationActivation: DeliveryCustomizationActivationPayload }>(gql, args);
  return data.deliveryCustomizationActivation;
}

/**
 * Creates a delivery customization.
 * @scope write_delivery_customizations
 */
export interface DeliveryCustomizationCreateArgs {
  deliveryCustomization: DeliveryCustomizationInput;
}

export async function deliveryCustomizationCreate(args: DeliveryCustomizationCreateArgs): Promise<DeliveryCustomizationCreatePayload> {
  const gql = `#graphql
    mutation deliveryCustomizationCreate($deliveryCustomization: DeliveryCustomizationInput!) {
      deliveryCustomizationCreate(deliveryCustomization: $deliveryCustomization) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryCustomizationCreate: DeliveryCustomizationCreatePayload }>(gql, args);
  return data.deliveryCustomizationCreate;
}

/**
 * Creates a delivery customization.
 * @scope write_delivery_customizations
 */
export interface DeliveryCustomizationDeleteArgs {
  id: string;
}

export async function deliveryCustomizationDelete(args: DeliveryCustomizationDeleteArgs): Promise<DeliveryCustomizationDeletePayload> {
  const gql = `#graphql
    mutation deliveryCustomizationDelete($id: ID!) {
      deliveryCustomizationDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryCustomizationDelete: DeliveryCustomizationDeletePayload }>(gql, args);
  return data.deliveryCustomizationDelete;
}

/**
 * Updates a delivery customization.
 * @scope write_delivery_customizations
 */
export interface DeliveryCustomizationUpdateArgs {
  deliveryCustomization: DeliveryCustomizationInput;
  id: string;
}

export async function deliveryCustomizationUpdate(args: DeliveryCustomizationUpdateArgs): Promise<DeliveryCustomizationUpdatePayload> {
  const gql = `#graphql
    mutation deliveryCustomizationUpdate($deliveryCustomization: DeliveryCustomizationInput!, $id: ID!) {
      deliveryCustomizationUpdate(deliveryCustomization: $deliveryCustomization, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryCustomizationUpdate: DeliveryCustomizationUpdatePayload }>(gql, args);
  return data.deliveryCustomizationUpdate;
}

/**
 * Creates a DeliveryProfile that defines shipping rates for specific products and locations.
 */
export interface DeliveryProfileCreateArgs {
  profile: DeliveryProfileInput;
}

export async function deliveryProfileCreate(args: DeliveryProfileCreateArgs): Promise<DeliveryProfileCreatePayload> {
  const gql = `#graphql
    mutation deliveryProfileCreate($profile: DeliveryProfileInput!) {
      deliveryProfileCreate(profile: $profile) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryProfileCreate: DeliveryProfileCreatePayload }>(gql, args);
  return data.deliveryProfileCreate;
}

/**
 * Enqueue the removal of a delivery profile.
 */
export interface DeliveryProfileRemoveArgs {
  id: string;
}

export async function deliveryProfileRemove(args: DeliveryProfileRemoveArgs): Promise<DeliveryProfileRemovePayload> {
  const gql = `#graphql
    mutation deliveryProfileRemove($id: ID!) {
      deliveryProfileRemove(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryProfileRemove: DeliveryProfileRemovePayload }>(gql, args);
  return data.deliveryProfileRemove;
}

/**
 * Updates a DeliveryProfile's configuration, including its shipping zones, rates, and associated products.
 */
export interface DeliveryProfileUpdateArgs {
  id: string;
  profile: DeliveryProfileInput;
}

export async function deliveryProfileUpdate(args: DeliveryProfileUpdateArgs): Promise<DeliveryProfileUpdatePayload> {
  const gql = `#graphql
    mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
      deliveryProfileUpdate(id: $id, profile: $profile) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryProfileUpdate: DeliveryProfileUpdatePayload }>(gql, args);
  return data.deliveryProfileUpdate;
}

/**
 * Updates the delivery promise participants by adding or removing owners based on a branded promise handle.
 * @scope write_delivery_promises
 */
export interface DeliveryPromiseParticipantsUpdateArgs {
  brandedPromiseHandle: string;
  ownersToAdd?: unknown;
  ownersToRemove?: unknown;
}

export async function deliveryPromiseParticipantsUpdate(args: DeliveryPromiseParticipantsUpdateArgs): Promise<DeliveryPromiseParticipantsUpdatePayload> {
  const gql = `#graphql
    mutation deliveryPromiseParticipantsUpdate($brandedPromiseHandle: String!, $ownersToAdd: String, $ownersToRemove: String) {
      deliveryPromiseParticipantsUpdate(brandedPromiseHandle: $brandedPromiseHandle, ownersToAdd: $ownersToAdd, ownersToRemove: $ownersToRemove) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryPromiseParticipantsUpdate: DeliveryPromiseParticipantsUpdatePayload }>(gql, args);
  return data.deliveryPromiseParticipantsUpdate;
}

/**
 * Creates or updates a delivery promise provider. Currently restricted to select approved delivery promise partners.
 * @scope write_delivery_promises
 */
export interface DeliveryPromiseProviderUpsertArgs {
  active?: boolean;
  fulfillmentDelay?: number;
  locationId: string;
  timeZone?: string;
}

export async function deliveryPromiseProviderUpsert(args: DeliveryPromiseProviderUpsertArgs): Promise<DeliveryPromiseProviderUpsertPayload> {
  const gql = `#graphql
    mutation deliveryPromiseProviderUpsert($active: Boolean, $fulfillmentDelay: Int, $locationId: ID!, $timeZone: String) {
      deliveryPromiseProviderUpsert(active: $active, fulfillmentDelay: $fulfillmentDelay, locationId: $locationId, timeZone: $timeZone) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryPromiseProviderUpsert: DeliveryPromiseProviderUpsertPayload }>(gql, args);
  return data.deliveryPromiseProviderUpsert;
}

/**
 * Set the delivery settings for a shop.
 */
export async function deliverySettingUpdate(): Promise<DeliverySettingUpdatePayload> {
  const gql = `#graphql
    mutation deliverySettingUpdate {
      deliverySettingUpdate {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliverySettingUpdate: DeliverySettingUpdatePayload }>(gql);
  return data.deliverySettingUpdate;
}

/**
 * Assigns a location as the shipping origin while using legacy compatibility mode for multi-location delivery profiles.
 */
export interface DeliveryShippingOriginAssignArgs {
  locationId: string;
}

export async function deliveryShippingOriginAssign(args: DeliveryShippingOriginAssignArgs): Promise<DeliveryShippingOriginAssignPayload> {
  const gql = `#graphql
    mutation deliveryShippingOriginAssign($locationId: ID!) {
      deliveryShippingOriginAssign(locationId: $locationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deliveryShippingOriginAssign: DeliveryShippingOriginAssignPayload }>(gql, args);
  return data.deliveryShippingOriginAssign;
}

/**
 * Cancels an existing Fulfillment and reverses its effects on associated FulfillmentOrder objects. When you cancel a fulfillment, the system creates new fulfillment orders for the cancelled items so they can be fulfilled again.
 */
export interface FulfillmentCancelArgs {
  id: string;
}

export async function fulfillmentCancel(args: FulfillmentCancelArgs): Promise<FulfillmentCancelPayload> {
  const gql = `#graphql
    mutation fulfillmentCancel($id: ID!) {
      fulfillmentCancel(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentCancel: FulfillmentCancelPayload }>(gql, args);
  return data.fulfillmentCancel;
}

/**
 * Creates a fulfillment constraint rule and its metafield.
 * @scope write_fulfillment_constraint_rules
 */
export interface FulfillmentConstraintRuleCreateArgs {
  deliveryMethodTypes: unknown;
  functionHandle?: string;
  metafields?: unknown;
  functionId?: string;
}

export async function fulfillmentConstraintRuleCreate(args: FulfillmentConstraintRuleCreateArgs): Promise<FulfillmentConstraintRuleCreatePayload> {
  const gql = `#graphql
    mutation fulfillmentConstraintRuleCreate($deliveryMethodTypes: String, $functionHandle: String, $metafields: String, $functionId: String) {
      fulfillmentConstraintRuleCreate(deliveryMethodTypes: $deliveryMethodTypes, functionHandle: $functionHandle, metafields: $metafields, functionId: $functionId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentConstraintRuleCreate: FulfillmentConstraintRuleCreatePayload }>(gql, args);
  return data.fulfillmentConstraintRuleCreate;
}

/**
 * Deletes a fulfillment constraint rule and its metafields.
 * @scope write_fulfillment_constraint_rules
 */
export interface FulfillmentConstraintRuleDeleteArgs {
  id: string;
}

export async function fulfillmentConstraintRuleDelete(args: FulfillmentConstraintRuleDeleteArgs): Promise<FulfillmentConstraintRuleDeletePayload> {
  const gql = `#graphql
    mutation fulfillmentConstraintRuleDelete($id: ID!) {
      fulfillmentConstraintRuleDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentConstraintRuleDelete: FulfillmentConstraintRuleDeletePayload }>(gql, args);
  return data.fulfillmentConstraintRuleDelete;
}

/**
 * Update a fulfillment constraint rule.
 * @scope write_fulfillment_constraint_rules
 */
export interface FulfillmentConstraintRuleUpdateArgs {
  deliveryMethodTypes: unknown;
  id: string;
}

export async function fulfillmentConstraintRuleUpdate(args: FulfillmentConstraintRuleUpdateArgs): Promise<FulfillmentConstraintRuleUpdatePayload> {
  const gql = `#graphql
    mutation fulfillmentConstraintRuleUpdate($deliveryMethodTypes: String, $id: ID!) {
      fulfillmentConstraintRuleUpdate(deliveryMethodTypes: $deliveryMethodTypes, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentConstraintRuleUpdate: FulfillmentConstraintRuleUpdatePayload }>(gql, args);
  return data.fulfillmentConstraintRuleUpdate;
}

/**
 * Creates a fulfillment for one or more FulfillmentOrder objects. The fulfillment orders are associated with the same Order and are assigned to the same Location.
 * @scope write_assigned_fulfillment_orders
 */
export interface FulfillmentCreateArgs {
  fulfillment: FulfillmentInput;
  message?: string;
}

export async function fulfillmentCreate(args: FulfillmentCreateArgs): Promise<FulfillmentCreatePayload> {
  const gql = `#graphql
    mutation fulfillmentCreate($fulfillment: FulfillmentInput!, $message: String) {
      fulfillmentCreate(fulfillment: $fulfillment, message: $message) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentCreate: FulfillmentCreatePayload }>(gql, args);
  return data.fulfillmentCreate;
}

/**
 * Creates a fulfillment for one or many fulfillment orders.
 * @scope write_assigned_fulfillment_orders
 */
export interface FulfillmentCreateV2Args {
  fulfillment: FulfillmentV2Input;
  message?: string;
}

export async function fulfillmentCreateV2(args: FulfillmentCreateV2Args): Promise<FulfillmentCreateV2Payload> {
  const gql = `#graphql
    mutation fulfillmentCreateV2($fulfillment: FulfillmentV2Input!, $message: String) {
      fulfillmentCreateV2(fulfillment: $fulfillment, message: $message) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentCreateV2: FulfillmentCreateV2Payload }>(gql, args);
  return data.fulfillmentCreateV2;
}

/**
 * Creates a FulfillmentEvent to track the shipment status and location of items that have shipped. Events capture status updates like carrier pickup, in transit, out for delivery, or delivered.
 * @scope write_fulfillments
 */
export interface FulfillmentEventCreateArgs {
  fulfillmentEvent: FulfillmentEventInput;
}

export async function fulfillmentEventCreate(args: FulfillmentEventCreateArgs): Promise<FulfillmentEventCreatePayload> {
  const gql = `#graphql
    mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
      fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentEventCreate: FulfillmentEventCreatePayload }>(gql, args);
  return data.fulfillmentEventCreate;
}

/**
 * Accept a cancellation request sent to a fulfillment service for a fulfillment order.
 * @scope write_assigned_fulfillment_orders
 */
export interface FulfillmentOrderAcceptCancellationRequestArgs {
  id: string;
  message?: string;
}

export async function fulfillmentOrderAcceptCancellationRequest(args: FulfillmentOrderAcceptCancellationRequestArgs): Promise<FulfillmentOrderAcceptCancellationRequestPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderAcceptCancellationRequest($id: ID!, $message: String) {
      fulfillmentOrderAcceptCancellationRequest(id: $id, message: $message) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderAcceptCancellationRequest: FulfillmentOrderAcceptCancellationRequestPayload }>(gql, args);
  return data.fulfillmentOrderAcceptCancellationRequest;
}

/**
 * Accepts a fulfillment request that the fulfillment service has received for a FulfillmentOrder which signals that the fulfillment service will process and fulfill the order. The fulfillment service can optionally provide a message to the merchant and an estimated shipped date when accepting the request.
 * @scope write_assigned_fulfillment_orders
 */
export interface FulfillmentOrderAcceptFulfillmentRequestArgs {
  estimatedShippedAt?: string;
  id: string;
  message?: string;
}

export async function fulfillmentOrderAcceptFulfillmentRequest(args: FulfillmentOrderAcceptFulfillmentRequestArgs): Promise<FulfillmentOrderAcceptFulfillmentRequestPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderAcceptFulfillmentRequest($estimatedShippedAt: DateTime, $id: ID!, $message: String) {
      fulfillmentOrderAcceptFulfillmentRequest(estimatedShippedAt: $estimatedShippedAt, id: $id, message: $message) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderAcceptFulfillmentRequest: FulfillmentOrderAcceptFulfillmentRequestPayload }>(gql, args);
  return data.fulfillmentOrderAcceptFulfillmentRequest;
}

/**
 * Cancels a FulfillmentOrder and creates a replacement fulfillment order to represent the work left to be done. The original fulfillment order will be marked as closed.
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrderCancelArgs {
  id: string;
}

export async function fulfillmentOrderCancel(args: FulfillmentOrderCancelArgs): Promise<FulfillmentOrderCancelPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderCancel($id: ID!) {
      fulfillmentOrderCancel(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderCancel: FulfillmentOrderCancelPayload }>(gql, args);
  return data.fulfillmentOrderCancel;
}

/**
 * Marks an in-progress fulfillment order as incomplete,
 * @scope write_assigned_fulfillment_orders
 */
export interface FulfillmentOrderCloseArgs {
  id: string;
  message?: string;
}

export async function fulfillmentOrderClose(args: FulfillmentOrderCloseArgs): Promise<FulfillmentOrderClosePayload> {
  const gql = `#graphql
    mutation fulfillmentOrderClose($id: ID!, $message: String) {
      fulfillmentOrderClose(id: $id, message: $message) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderClose: FulfillmentOrderClosePayload }>(gql, args);
  return data.fulfillmentOrderClose;
}

/**
 * Applies a fulfillment hold on a fulfillment order.
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrderHoldArgs {
  fulfillmentHold: FulfillmentOrderHoldInput;
  id: string;
}

export async function fulfillmentOrderHold(args: FulfillmentOrderHoldArgs): Promise<FulfillmentOrderHoldPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
      fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderHold: FulfillmentOrderHoldPayload }>(gql, args);
  return data.fulfillmentOrderHold;
}

/**
 * Marks fulfillment order line items as ready for customer pickup. When executed, this mutation automatically sends a "Ready For Pickup" notification to the customer.
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrderLineItemsPreparedForPickupArgs {
  input: FulfillmentOrderLineItemsPreparedForPickupInput;
}

export async function fulfillmentOrderLineItemsPreparedForPickup(args: FulfillmentOrderLineItemsPreparedForPickupArgs): Promise<FulfillmentOrderLineItemsPreparedForPickupPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderLineItemsPreparedForPickup($input: FulfillmentOrderLineItemsPreparedForPickupInput!) {
      fulfillmentOrderLineItemsPreparedForPickup(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderLineItemsPreparedForPickup: FulfillmentOrderLineItemsPreparedForPickupPayload }>(gql, args);
  return data.fulfillmentOrderLineItemsPreparedForPickup;
}

/**
 * |-
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrderMergeArgs {
  fulfillmentOrderMergeInputs: unknown;
}

export async function fulfillmentOrderMerge(args: FulfillmentOrderMergeArgs): Promise<FulfillmentOrderMergePayload> {
  const gql = `#graphql
    mutation fulfillmentOrderMerge($fulfillmentOrderMergeInputs: String) {
      fulfillmentOrderMerge(fulfillmentOrderMergeInputs: $fulfillmentOrderMergeInputs) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderMerge: FulfillmentOrderMergePayload }>(gql, args);
  return data.fulfillmentOrderMerge;
}

/**
 * Changes the location which is assigned to fulfill a number of unfulfilled fulfillment order line items.
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrderMoveArgs {
  fulfillmentOrderLineItems?: unknown;
  id: string;
  newLocationId: string;
}

export async function fulfillmentOrderMove(args: FulfillmentOrderMoveArgs): Promise<FulfillmentOrderMovePayload> {
  const gql = `#graphql
    mutation fulfillmentOrderMove($fulfillmentOrderLineItems: String, $id: ID!, $newLocationId: ID!) {
      fulfillmentOrderMove(fulfillmentOrderLineItems: $fulfillmentOrderLineItems, id: $id, newLocationId: $newLocationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderMove: FulfillmentOrderMovePayload }>(gql, args);
  return data.fulfillmentOrderMove;
}

/**
 * Marks a scheduled fulfillment order as open.
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrderOpenArgs {
  id: string;
}

export async function fulfillmentOrderOpen(args: FulfillmentOrderOpenArgs): Promise<FulfillmentOrderOpenPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderOpen($id: ID!) {
      fulfillmentOrderOpen(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderOpen: FulfillmentOrderOpenPayload }>(gql, args);
  return data.fulfillmentOrderOpen;
}

/**
 * Rejects a cancellation request sent to a fulfillment service for a fulfillment order.
 * @scope write_assigned_fulfillment_orders
 */
export interface FulfillmentOrderRejectCancellationRequestArgs {
  id: string;
  message?: string;
}

export async function fulfillmentOrderRejectCancellationRequest(args: FulfillmentOrderRejectCancellationRequestArgs): Promise<FulfillmentOrderRejectCancellationRequestPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderRejectCancellationRequest($id: ID!, $message: String) {
      fulfillmentOrderRejectCancellationRequest(id: $id, message: $message) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderRejectCancellationRequest: FulfillmentOrderRejectCancellationRequestPayload }>(gql, args);
  return data.fulfillmentOrderRejectCancellationRequest;
}

/**
 * Rejects a fulfillment request sent to a fulfillment service for a fulfillment order.
 * @scope write_assigned_fulfillment_orders
 */
export interface FulfillmentOrderRejectFulfillmentRequestArgs {
  id: string;
  lineItems?: unknown;
  message?: string;
  reason?: FulfillmentOrderRejectionReason;
}

export async function fulfillmentOrderRejectFulfillmentRequest(args: FulfillmentOrderRejectFulfillmentRequestArgs): Promise<FulfillmentOrderRejectFulfillmentRequestPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderRejectFulfillmentRequest($id: ID!, $lineItems: String, $message: String, $reason: FulfillmentOrderRejectionReason) {
      fulfillmentOrderRejectFulfillmentRequest(id: $id, lineItems: $lineItems, message: $message, reason: $reason) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderRejectFulfillmentRequest: FulfillmentOrderRejectFulfillmentRequestPayload }>(gql, args);
  return data.fulfillmentOrderRejectFulfillmentRequest;
}

/**
 * Releases the fulfillment hold on a fulfillment order.
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrderReleaseHoldArgs {
  externalId?: string;
  holdIds?: unknown;
  id: string;
}

export async function fulfillmentOrderReleaseHold(args: FulfillmentOrderReleaseHoldArgs): Promise<FulfillmentOrderReleaseHoldPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderReleaseHold($externalId: String, $holdIds: String, $id: ID!) {
      fulfillmentOrderReleaseHold(externalId: $externalId, holdIds: $holdIds, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderReleaseHold: FulfillmentOrderReleaseHoldPayload }>(gql, args);
  return data.fulfillmentOrderReleaseHold;
}

/**
 * Reports the progress of an open or in-progress fulfillment order.
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrderReportProgressArgs {
  id: string;
  progressReport?: FulfillmentOrderReportProgressInput;
}

export async function fulfillmentOrderReportProgress(args: FulfillmentOrderReportProgressArgs): Promise<FulfillmentOrderReportProgressPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderReportProgress($id: ID!, $progressReport: FulfillmentOrderReportProgressInput) {
      fulfillmentOrderReportProgress(id: $id, progressReport: $progressReport) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderReportProgress: FulfillmentOrderReportProgressPayload }>(gql, args);
  return data.fulfillmentOrderReportProgress;
}

/**
 * Reschedules a scheduled fulfillment order.
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrderRescheduleArgs {
  fulfillAt: string;
  id: string;
}

export async function fulfillmentOrderReschedule(args: FulfillmentOrderRescheduleArgs): Promise<FulfillmentOrderReschedulePayload> {
  const gql = `#graphql
    mutation fulfillmentOrderReschedule($fulfillAt: DateTime!, $id: ID!) {
      fulfillmentOrderReschedule(fulfillAt: $fulfillAt, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderReschedule: FulfillmentOrderReschedulePayload }>(gql, args);
  return data.fulfillmentOrderReschedule;
}

/**
 * Splits FulfillmentOrder objects by moving the specified LineItem objects and quantities into a new fulfillment order.
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrderSplitArgs {
  fulfillmentOrderSplits: unknown;
}

export async function fulfillmentOrderSplit(args: FulfillmentOrderSplitArgs): Promise<FulfillmentOrderSplitPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderSplit($fulfillmentOrderSplits: String) {
      fulfillmentOrderSplit(fulfillmentOrderSplits: $fulfillmentOrderSplits) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderSplit: FulfillmentOrderSplitPayload }>(gql, args);
  return data.fulfillmentOrderSplit;
}

/**
 * Sends a cancellation request to the fulfillment service of a fulfillment order.
 * @scope write_third_party_fulfillment_orders
 */
export interface FulfillmentOrderSubmitCancellationRequestArgs {
  id: string;
  message?: string;
}

export async function fulfillmentOrderSubmitCancellationRequest(args: FulfillmentOrderSubmitCancellationRequestArgs): Promise<FulfillmentOrderSubmitCancellationRequestPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderSubmitCancellationRequest($id: ID!, $message: String) {
      fulfillmentOrderSubmitCancellationRequest(id: $id, message: $message) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderSubmitCancellationRequest: FulfillmentOrderSubmitCancellationRequestPayload }>(gql, args);
  return data.fulfillmentOrderSubmitCancellationRequest;
}

/**
 * Sends a fulfillment request to the fulfillment service assigned to a FulfillmentOrder. The fulfillment service must then accept or reject the request before processing can begin.
 * @scope write_third_party_fulfillment_orders
 */
export interface FulfillmentOrderSubmitFulfillmentRequestArgs {
  fulfillmentOrderLineItems?: unknown;
  id: string;
  message?: string;
  notifyCustomer?: boolean;
}

export async function fulfillmentOrderSubmitFulfillmentRequest(args: FulfillmentOrderSubmitFulfillmentRequestArgs): Promise<FulfillmentOrderSubmitFulfillmentRequestPayload> {
  const gql = `#graphql
    mutation fulfillmentOrderSubmitFulfillmentRequest($fulfillmentOrderLineItems: String, $id: ID!, $message: String, $notifyCustomer: Boolean) {
      fulfillmentOrderSubmitFulfillmentRequest(fulfillmentOrderLineItems: $fulfillmentOrderLineItems, id: $id, message: $message, notifyCustomer: $notifyCustomer) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrderSubmitFulfillmentRequest: FulfillmentOrderSubmitFulfillmentRequestPayload }>(gql, args);
  return data.fulfillmentOrderSubmitFulfillmentRequest;
}

/**
 * Route the fulfillment orders to an alternative location, according to the shop's order routing settings. This involves:
 * @scope write_assigned_fulfillment_orders
 */
export interface FulfillmentOrdersRerouteArgs {
  excludedLocationIds?: unknown;
  fulfillmentOrderIds: unknown;
  includedLocationIds?: unknown;
}

export async function fulfillmentOrdersReroute(args: FulfillmentOrdersRerouteArgs): Promise<FulfillmentOrdersReroutePayload> {
  const gql = `#graphql
    mutation fulfillmentOrdersReroute($excludedLocationIds: String, $fulfillmentOrderIds: String, $includedLocationIds: String) {
      fulfillmentOrdersReroute(excludedLocationIds: $excludedLocationIds, fulfillmentOrderIds: $fulfillmentOrderIds, includedLocationIds: $includedLocationIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrdersReroute: FulfillmentOrdersReroutePayload }>(gql, args);
  return data.fulfillmentOrdersReroute;
}

/**
 * Sets the latest date and time by which the fulfillment orders need to be fulfilled.
 * @scope write_merchant_managed_fulfillment_orders
 */
export interface FulfillmentOrdersSetFulfillmentDeadlineArgs {
  fulfillmentDeadline: string;
  fulfillmentOrderIds: unknown;
}

export async function fulfillmentOrdersSetFulfillmentDeadline(args: FulfillmentOrdersSetFulfillmentDeadlineArgs): Promise<FulfillmentOrdersSetFulfillmentDeadlinePayload> {
  const gql = `#graphql
    mutation fulfillmentOrdersSetFulfillmentDeadline($fulfillmentDeadline: DateTime!, $fulfillmentOrderIds: String) {
      fulfillmentOrdersSetFulfillmentDeadline(fulfillmentDeadline: $fulfillmentDeadline, fulfillmentOrderIds: $fulfillmentOrderIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentOrdersSetFulfillmentDeadline: FulfillmentOrdersSetFulfillmentDeadlinePayload }>(gql, args);
  return data.fulfillmentOrdersSetFulfillmentDeadline;
}

/**
 * Creates a fulfillment service.
 * @scope write_fulfillments
 */
export interface FulfillmentServiceCreateArgs {
  callbackUrl?: string;
  inventoryManagement?: boolean;
  name: string;
  requiresShippingMethod?: boolean;
  trackingSupport?: boolean;
  fulfillmentOrdersOptIn?: boolean;
}

export async function fulfillmentServiceCreate(args: FulfillmentServiceCreateArgs): Promise<FulfillmentServiceCreatePayload> {
  const gql = `#graphql
    mutation fulfillmentServiceCreate($callbackUrl: URL, $inventoryManagement: Boolean, $name: String!, $requiresShippingMethod: Boolean, $trackingSupport: Boolean, $fulfillmentOrdersOptIn: Boolean) {
      fulfillmentServiceCreate(callbackUrl: $callbackUrl, inventoryManagement: $inventoryManagement, name: $name, requiresShippingMethod: $requiresShippingMethod, trackingSupport: $trackingSupport, fulfillmentOrdersOptIn: $fulfillmentOrdersOptIn) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentServiceCreate: FulfillmentServiceCreatePayload }>(gql, args);
  return data.fulfillmentServiceCreate;
}

/**
 * Deletes a fulfillment service.
 * @scope write_fulfillments
 */
export interface FulfillmentServiceDeleteArgs {
  destinationLocationId?: string;
  id: string;
  inventoryAction?: FulfillmentServiceDeleteInventoryAction;
}

export async function fulfillmentServiceDelete(args: FulfillmentServiceDeleteArgs): Promise<FulfillmentServiceDeletePayload> {
  const gql = `#graphql
    mutation fulfillmentServiceDelete($destinationLocationId: ID, $id: ID!, $inventoryAction: FulfillmentServiceDeleteInventoryAction) {
      fulfillmentServiceDelete(destinationLocationId: $destinationLocationId, id: $id, inventoryAction: $inventoryAction) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentServiceDelete: FulfillmentServiceDeletePayload }>(gql, args);
  return data.fulfillmentServiceDelete;
}

/**
 * Updates the FulfillmentService configuration, including its name, callback URL, and operational settings.
 * @scope write_fulfillments
 */
export interface FulfillmentServiceUpdateArgs {
  callbackUrl?: string;
  id: string;
  inventoryManagement?: boolean;
  name?: string;
  requiresShippingMethod?: boolean;
  trackingSupport?: boolean;
  fulfillmentOrdersOptIn?: boolean;
}

export async function fulfillmentServiceUpdate(args: FulfillmentServiceUpdateArgs): Promise<FulfillmentServiceUpdatePayload> {
  const gql = `#graphql
    mutation fulfillmentServiceUpdate($callbackUrl: URL, $id: ID!, $inventoryManagement: Boolean, $name: String, $requiresShippingMethod: Boolean, $trackingSupport: Boolean, $fulfillmentOrdersOptIn: Boolean) {
      fulfillmentServiceUpdate(callbackUrl: $callbackUrl, id: $id, inventoryManagement: $inventoryManagement, name: $name, requiresShippingMethod: $requiresShippingMethod, trackingSupport: $trackingSupport, fulfillmentOrdersOptIn: $fulfillmentOrdersOptIn) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentServiceUpdate: FulfillmentServiceUpdatePayload }>(gql, args);
  return data.fulfillmentServiceUpdate;
}

/**
 * Updates tracking information for a fulfillment, including the carrier name, tracking numbers, and tracking URLs. You can provide either single or multiple tracking numbers for shipments with multiple packages.
 * @scope write_assigned_fulfillment_orders
 */
export interface FulfillmentTrackingInfoUpdateArgs {
  fulfillmentId: string;
  notifyCustomer?: boolean;
  trackingInfoInput: FulfillmentTrackingInput;
}

export async function fulfillmentTrackingInfoUpdate(args: FulfillmentTrackingInfoUpdateArgs): Promise<FulfillmentTrackingInfoUpdatePayload> {
  const gql = `#graphql
    mutation fulfillmentTrackingInfoUpdate($fulfillmentId: ID!, $notifyCustomer: Boolean, $trackingInfoInput: FulfillmentTrackingInput!) {
      fulfillmentTrackingInfoUpdate(fulfillmentId: $fulfillmentId, notifyCustomer: $notifyCustomer, trackingInfoInput: $trackingInfoInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentTrackingInfoUpdate: FulfillmentTrackingInfoUpdatePayload }>(gql, args);
  return data.fulfillmentTrackingInfoUpdate;
}

/**
 * Updates tracking information for a fulfillment.
 * @scope write_assigned_fulfillment_orders
 */
export interface FulfillmentTrackingInfoUpdateV2Args {
  fulfillmentId: string;
  notifyCustomer?: boolean;
  trackingInfoInput: FulfillmentTrackingInput;
}

export async function fulfillmentTrackingInfoUpdateV2(args: FulfillmentTrackingInfoUpdateV2Args): Promise<FulfillmentTrackingInfoUpdateV2Payload> {
  const gql = `#graphql
    mutation fulfillmentTrackingInfoUpdateV2($fulfillmentId: ID!, $notifyCustomer: Boolean, $trackingInfoInput: FulfillmentTrackingInput!) {
      fulfillmentTrackingInfoUpdateV2(fulfillmentId: $fulfillmentId, notifyCustomer: $notifyCustomer, trackingInfoInput: $trackingInfoInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ fulfillmentTrackingInfoUpdateV2: FulfillmentTrackingInfoUpdateV2Payload }>(gql, args);
  return data.fulfillmentTrackingInfoUpdateV2;
}

/**
 * Deletes a shipping package.
 */
export interface ShippingPackageDeleteArgs {
  id: string;
}

export async function shippingPackageDelete(args: ShippingPackageDeleteArgs): Promise<ShippingPackageDeletePayload> {
  const gql = `#graphql
    mutation shippingPackageDelete($id: ID!) {
      shippingPackageDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shippingPackageDelete: ShippingPackageDeletePayload }>(gql, args);
  return data.shippingPackageDelete;
}

/**
 * Set a shipping package as the default.
 */
export interface ShippingPackageMakeDefaultArgs {
  id: string;
}

export async function shippingPackageMakeDefault(args: ShippingPackageMakeDefaultArgs): Promise<ShippingPackageMakeDefaultPayload> {
  const gql = `#graphql
    mutation shippingPackageMakeDefault($id: ID!) {
      shippingPackageMakeDefault(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shippingPackageMakeDefault: ShippingPackageMakeDefaultPayload }>(gql, args);
  return data.shippingPackageMakeDefault;
}

/**
 * Updates a shipping package.
 */
export interface ShippingPackageUpdateArgs {
  id: string;
  shippingPackage: CustomShippingPackageInput;
}

export async function shippingPackageUpdate(args: ShippingPackageUpdateArgs): Promise<ShippingPackageUpdatePayload> {
  const gql = `#graphql
    mutation shippingPackageUpdate($id: ID!, $shippingPackage: CustomShippingPackageInput!) {
      shippingPackageUpdate(id: $id, shippingPackage: $shippingPackage) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ shippingPackageUpdate: ShippingPackageUpdatePayload }>(gql, args);
  return data.shippingPackageUpdate;
}










