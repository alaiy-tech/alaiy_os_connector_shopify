import { shopifyClient } from './client';
import type { Count, DeliveryLocationLocalPickupEnableInput, InventoryActivatePayload, InventoryAdjustQuantitiesInput, InventoryAdjustQuantitiesPayload, InventoryBulkToggleActivationPayload, InventoryDeactivatePayload, InventoryItem, InventoryItemConnection, InventoryItemInput, InventoryItemUpdatePayload, InventoryLevel, InventoryMoveQuantitiesInput, InventoryMoveQuantitiesPayload, InventoryProperties, InventorySetOnHandQuantitiesInput, InventorySetOnHandQuantitiesPayload, InventorySetQuantitiesInput, InventorySetQuantitiesPayload, InventorySetScheduledChangesInput, InventorySetScheduledChangesPayload, InventoryShipment, InventoryShipmentAddItemsPayload, InventoryShipmentConnection, InventoryShipmentCreateInput, InventoryShipmentCreateInTransitPayload, InventoryShipmentCreatePayload, InventoryShipmentDeletePayload, InventoryShipmentLineItem, InventoryShipmentMarkInTransitPayload, InventoryShipmentReceiveLineItemReason, InventoryShipmentReceivePayload, InventoryShipmentRemoveItemsPayload, InventoryShipmentSetBarcodePayload, InventoryShipmentSetTrackingPayload, InventoryShipmentSortKeys, InventoryShipmentStatus, InventoryShipmentTrackingInput, InventoryShipmentUpdateItemQuantitiesPayload, InventoryTransfer, InventoryTransferCancelPayload, InventoryTransferConnection, InventoryTransferCreateAsReadyToShipInput, InventoryTransferCreateAsReadyToShipPayload, InventoryTransferCreateInput, InventoryTransferCreatePayload, InventoryTransferDeletePayload, InventoryTransferDuplicatePayload, InventoryTransferEditInput, InventoryTransferEditPayload, InventoryTransferLineItem, InventoryTransferMarkAsReadyToShipPayload, InventoryTransferRemoveItemsInput, InventoryTransferRemoveItemsPayload, InventoryTransferSetItemsInput, InventoryTransferSetItemsPayload, InventoryTransferStatus, Location, LocationActivatePayload, LocationAddInput, LocationAddPayload, LocationConnection, LocationDeactivatePayload, LocationDeletePayload, LocationEditInput, LocationEditPayload, LocationIdentifierInput, LocationLocalPickupDisablePayload, LocationLocalPickupEnablePayload, LocationSortKeys, Order, Product, ProductVariant, Return, TransferSortKeys } from './types';

// ============================================================
// Inventory
// 47 operations: 12 queries, 35 mutations
// ============================================================

// These are passed as plain objects. See Shopify docs for field shapes:

// ─── Queries ─────────────────────────────────────────────────────────

/**
 * Returns an
 */
export interface InventoryItemArgs {
  id: string;
}

export async function inventoryItem(args: InventoryItemArgs): Promise<InventoryItem | null> {
  const gql = `#graphql
    query inventoryItem($id: ID!) {
      inventoryItem(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryItem: InventoryItem | null }>(gql, args);
  return data.inventoryItem;
}

/**
 * Returns a list of inventory items.
 */
export interface InventoryItemsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
}

export async function inventoryItems(args?: InventoryItemsArgs): Promise<InventoryItemConnection> {
  const gql = `#graphql
    query inventoryItems($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean) {
      inventoryItems(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryItems: InventoryItemConnection }>(gql, args);
  return data.inventoryItems;
}

/**
 * Returns an
 */
export interface InventoryLevelArgs {
  id: string;
}

export async function inventoryLevel(args: InventoryLevelArgs): Promise<InventoryLevel | null> {
  const gql = `#graphql
    query inventoryLevel($id: ID!) {
      inventoryLevel(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryLevel: InventoryLevel | null }>(gql, args);
  return data.inventoryLevel;
}

/**
 * Returns the shop's inventory configuration, including all inventory quantity names. Quantity names represent different inventory states that merchants use to track inventory.
 * @scope read_inventory
 */
export async function inventoryProperties(): Promise<InventoryProperties | null> {
  const gql = `#graphql
    query inventoryProperties {
      inventoryProperties {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryProperties: InventoryProperties | null }>(gql);
  return data.inventoryProperties;
}

/**
 * Retrieves an InventoryShipment by ID. Returns tracking details, InventoryShipmentLineItem objects with quantities, and the shipment's current InventoryShipmentStatus.
 * @scope read_inventory_shipments
 */
export interface InventoryShipmentArgs {
  id: string;
}

export async function inventoryShipment(args: InventoryShipmentArgs): Promise<InventoryShipment | null> {
  const gql = `#graphql
    query inventoryShipment($id: ID!) {
      inventoryShipment(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipment: InventoryShipment | null }>(gql, args);
  return data.inventoryShipment;
}

/**
 * Returns a paginated list of InventoryShipment objects.
 * @scope read_inventory_shipments
 */
export interface InventoryShipmentsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  sortKey?: InventoryShipmentSortKeys;
}

export async function inventoryShipments(args?: InventoryShipmentsArgs): Promise<InventoryShipmentConnection> {
  const gql = `#graphql
    query inventoryShipments($after: String, $before: String, $first: Int, $last: Int, $query: String, $sortKey: InventoryShipmentSortKeys) {
      inventoryShipments(after: $after, before: $before, first: $first, last: $last, query: $query, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipments: InventoryShipmentConnection }>(gql, args);
  return data.inventoryShipments;
}

/**
 * Returns an InventoryTransfer by ID. Inventory transfers track the movement of inventory between locations, including origin and destination details, InventoryTransferLineItem objects, quantities, and InventoryTransferStatus values.
 * @scope read_inventory_transfers
 */
export interface InventoryTransferArgs {
  id: string;
}

export async function inventoryTransfer(args: InventoryTransferArgs): Promise<InventoryTransfer | null> {
  const gql = `#graphql
    query inventoryTransfer($id: ID!) {
      inventoryTransfer(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransfer: InventoryTransfer | null }>(gql, args);
  return data.inventoryTransfer;
}

/**
 * Returns a paginated list of InventoryTransfer objects between locations. Transfers track the movement of InventoryItem objects between Location objects.
 * @scope read_inventory_transfers
 */
export interface InventoryTransfersArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: TransferSortKeys;
}

export async function inventoryTransfers(args?: InventoryTransfersArgs): Promise<InventoryTransferConnection> {
  const gql = `#graphql
    query inventoryTransfers($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: TransferSortKeys) {
      inventoryTransfers(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransfers: InventoryTransferConnection }>(gql, args);
  return data.inventoryTransfers;
}

/**
 * Retrieves a Location by its ID. Locations are physical places where merchants store inventory, such as warehouses, retail stores, or fulfillment centers.
 */
export interface LocationArgs {
  id?: string;
}

export async function location(args?: LocationArgs): Promise<Location | null> {
  const gql = `#graphql
    query location($id: ID) {
      location(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ location: Location | null }>(gql, args);
  return data.location;
}

/**
 * Return a location by an identifier.
 * @scope read_locations
 */
export interface LocationByIdentifierArgs {
  identifier: LocationIdentifierInput;
}

export async function locationByIdentifier(args: LocationByIdentifierArgs): Promise<Location | null> {
  const gql = `#graphql
    query locationByIdentifier($identifier: LocationIdentifierInput!) {
      locationByIdentifier(identifier: $identifier) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locationByIdentifier: Location | null }>(gql, args);
  return data.locationByIdentifier;
}

/**
 * A paginated list of inventory locations where merchants can stock Product items and fulfill Order items.
 */
export interface LocationsArgs {
  after?: string;
  before?: string;
  first?: number;
  includeInactive?: boolean;
  includeLegacy?: boolean;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: LocationSortKeys;
}

export async function locations(args?: LocationsArgs): Promise<LocationConnection> {
  const gql = `#graphql
    query locations($after: String, $before: String, $first: Int, $includeInactive: Boolean, $includeLegacy: Boolean, $last: Int, $query: String, $reverse: Boolean, $sortKey: LocationSortKeys) {
      locations(after: $after, before: $before, first: $first, includeInactive: $includeInactive, includeLegacy: $includeLegacy, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locations: LocationConnection }>(gql, args);
  return data.locations;
}

/**
 * Returns the count of locations for the given shop. Limited to a maximum of 10000 by default.
 */
export interface LocationsCountArgs {
  limit?: number;
  query?: string;
}

export async function locationsCount(args?: LocationsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query locationsCount($limit: Int, $query: String) {
      locationsCount(limit: $limit, query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locationsCount: Count | null }>(gql, args);
  return data.locationsCount;
}

// ─── Mutations ─────────────────────────────────────────────────────────

/**
 * Activates an inventory item at a Location by creating an InventoryLevel that tracks stock quantities. This enables you to manage inventory for a ProductVariant at the specified location.
 * @scope write_inventory
 */
export interface InventoryActivateArgs {
  available?: number;
  inventoryItemId: string;
  locationId: string;
  onHand?: number;
  stockAtLegacyLocation?: boolean;
}

export async function inventoryActivate(args: InventoryActivateArgs): Promise<InventoryActivatePayload> {
  const gql = `#graphql
    mutation inventoryActivate($available: Int, $inventoryItemId: ID!, $locationId: ID!, $onHand: Int, $stockAtLegacyLocation: Boolean) {
      inventoryActivate(available: $available, inventoryItemId: $inventoryItemId, locationId: $locationId, onHand: $onHand, stockAtLegacyLocation: $stockAtLegacyLocation) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryActivate: InventoryActivatePayload }>(gql, args);
  return data.inventoryActivate;
}

/**
 * Adjusts quantities for inventory items by applying incremental changes at specific locations. Each adjustment modifies the quantity by a delta value rather than setting an absolute amount.
 * @scope write_inventory
 */
export interface InventoryAdjustQuantitiesArgs {
  input: InventoryAdjustQuantitiesInput;
}

export async function inventoryAdjustQuantities(args: InventoryAdjustQuantitiesArgs): Promise<InventoryAdjustQuantitiesPayload> {
  const gql = `#graphql
    mutation inventoryAdjustQuantities($input: InventoryAdjustQuantitiesInput!) {
      inventoryAdjustQuantities(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryAdjustQuantities: InventoryAdjustQuantitiesPayload }>(gql, args);
  return data.inventoryAdjustQuantities;
}

/**
 * Activates or deactivates an inventory item at multiple locations. When you activate an InventoryItem at a Location, that location can stock and track quantities for that item. When you deactivate an inventory item at a location, the inventory item is no longer stocked at that location.
 * @scope write_inventory
 */
export interface InventoryBulkToggleActivationArgs {
  inventoryItemId: string;
  inventoryItemUpdates: unknown;
}

export async function inventoryBulkToggleActivation(args: InventoryBulkToggleActivationArgs): Promise<InventoryBulkToggleActivationPayload> {
  const gql = `#graphql
    mutation inventoryBulkToggleActivation($inventoryItemId: ID!, $inventoryItemUpdates: String) {
      inventoryBulkToggleActivation(inventoryItemId: $inventoryItemId, inventoryItemUpdates: $inventoryItemUpdates) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryBulkToggleActivation: InventoryBulkToggleActivationPayload }>(gql, args);
  return data.inventoryBulkToggleActivation;
}

/**
 * Removes an inventory item's quantities from a location, and turns off inventory at the location.
 * @scope write_inventory
 */
export interface InventoryDeactivateArgs {
  inventoryLevelId: string;
}

export async function inventoryDeactivate(args: InventoryDeactivateArgs): Promise<InventoryDeactivatePayload> {
  const gql = `#graphql
    mutation inventoryDeactivate($inventoryLevelId: ID!) {
      inventoryDeactivate(inventoryLevelId: $inventoryLevelId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryDeactivate: InventoryDeactivatePayload }>(gql, args);
  return data.inventoryDeactivate;
}

/**
 * Updates an InventoryItem's properties including whether inventory is tracked, cost, SKU, and whether shipping is required. Inventory items represent the goods available to be shipped to customers.
 * @scope write_inventory
 */
export interface InventoryItemUpdateArgs {
  id: string;
  input: InventoryItemInput;
}

export async function inventoryItemUpdate(args: InventoryItemUpdateArgs): Promise<InventoryItemUpdatePayload> {
  const gql = `#graphql
    mutation inventoryItemUpdate($id: ID!, $input: InventoryItemInput!) {
      inventoryItemUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryItemUpdate: InventoryItemUpdatePayload }>(gql, args);
  return data.inventoryItemUpdate;
}

/**
 * Moves inventory quantities for a single inventory item between different states at a single location. Use this mutation to reallocate inventory across quantity states without moving it between locations.
 * @scope write_inventory
 */
export interface InventoryMoveQuantitiesArgs {
  input: InventoryMoveQuantitiesInput;
}

export async function inventoryMoveQuantities(args: InventoryMoveQuantitiesArgs): Promise<InventoryMoveQuantitiesPayload> {
  const gql = `#graphql
    mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!) {
      inventoryMoveQuantities(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryMoveQuantities: InventoryMoveQuantitiesPayload }>(gql, args);
  return data.inventoryMoveQuantities;
}

/**
 * Sets an inventory item's on-hand quantities to specific absolute values at designated locations. The mutation takes a reason for tracking purposes and a reference document URI for audit trails.
 * @scope write_inventory
 */
export interface InventorySetOnHandQuantitiesArgs {
  input: InventorySetOnHandQuantitiesInput;
}

export async function inventorySetOnHandQuantities(args: InventorySetOnHandQuantitiesArgs): Promise<InventorySetOnHandQuantitiesPayload> {
  const gql = `#graphql
    mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!) {
      inventorySetOnHandQuantities(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventorySetOnHandQuantities: InventorySetOnHandQuantitiesPayload }>(gql, args);
  return data.inventorySetOnHandQuantities;
}

/**
 * Set quantities of specified name using absolute values. This mutation supports compare-and-set functionality to handle
 * @scope write_inventory
 */
export interface InventorySetQuantitiesArgs {
  input: InventorySetQuantitiesInput;
}

export async function inventorySetQuantities(args: InventorySetQuantitiesArgs): Promise<InventorySetQuantitiesPayload> {
  const gql = `#graphql
    mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventorySetQuantities: InventorySetQuantitiesPayload }>(gql, args);
  return data.inventorySetQuantities;
}

/**
 * Set up scheduled changes of inventory items.
 * @scope write_inventory
 */
export interface InventorySetScheduledChangesArgs {
  input: InventorySetScheduledChangesInput;
}

export async function inventorySetScheduledChanges(args: InventorySetScheduledChangesArgs): Promise<InventorySetScheduledChangesPayload> {
  const gql = `#graphql
    mutation inventorySetScheduledChanges($input: InventorySetScheduledChangesInput!) {
      inventorySetScheduledChanges(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventorySetScheduledChanges: InventorySetScheduledChangesPayload }>(gql, args);
  return data.inventorySetScheduledChanges;
}

/**
 * Adds items to an inventory shipment.
 * @scope write_inventory_shipments
 */
export interface InventoryShipmentAddItemsArgs {
  id: string;
  lineItems: unknown;
}

export async function inventoryShipmentAddItems(args: InventoryShipmentAddItemsArgs): Promise<InventoryShipmentAddItemsPayload> {
  const gql = `#graphql
    mutation inventoryShipmentAddItems($id: ID!, $lineItems: String) {
      inventoryShipmentAddItems(id: $id, lineItems: $lineItems) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipmentAddItems: InventoryShipmentAddItemsPayload }>(gql, args);
  return data.inventoryShipmentAddItems;
}

/**
 * Adds a draft shipment to an inventory transfer.
 * @scope write_inventory_shipments
 */
export interface InventoryShipmentCreateArgs {
  input: InventoryShipmentCreateInput;
}

export async function inventoryShipmentCreate(args: InventoryShipmentCreateArgs): Promise<InventoryShipmentCreatePayload> {
  const gql = `#graphql
    mutation inventoryShipmentCreate($input: InventoryShipmentCreateInput!) {
      inventoryShipmentCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipmentCreate: InventoryShipmentCreatePayload }>(gql, args);
  return data.inventoryShipmentCreate;
}

/**
 * Adds an in-transit shipment to an inventory transfer.
 * @scope write_inventory_shipments
 */
export interface InventoryShipmentCreateInTransitArgs {
  input: InventoryShipmentCreateInput;
}

export async function inventoryShipmentCreateInTransit(args: InventoryShipmentCreateInTransitArgs): Promise<InventoryShipmentCreateInTransitPayload> {
  const gql = `#graphql
    mutation inventoryShipmentCreateInTransit($input: InventoryShipmentCreateInput!) {
      inventoryShipmentCreateInTransit(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipmentCreateInTransit: InventoryShipmentCreateInTransitPayload }>(gql, args);
  return data.inventoryShipmentCreateInTransit;
}

/**
 * Deletes an inventory shipment. Only draft shipments can be deleted.
 * @scope write_inventory_shipments
 */
export interface InventoryShipmentDeleteArgs {
  id: string;
}

export async function inventoryShipmentDelete(args: InventoryShipmentDeleteArgs): Promise<InventoryShipmentDeletePayload> {
  const gql = `#graphql
    mutation inventoryShipmentDelete($id: ID!) {
      inventoryShipmentDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipmentDelete: InventoryShipmentDeletePayload }>(gql, args);
  return data.inventoryShipmentDelete;
}

/**
 * Marks a draft inventory shipment as in transit.
 * @scope write_inventory_shipments
 */
export interface InventoryShipmentMarkInTransitArgs {
  dateShipped?: string;
  id: string;
}

export async function inventoryShipmentMarkInTransit(args: InventoryShipmentMarkInTransitArgs): Promise<InventoryShipmentMarkInTransitPayload> {
  const gql = `#graphql
    mutation inventoryShipmentMarkInTransit($dateShipped: DateTime, $id: ID!) {
      inventoryShipmentMarkInTransit(dateShipped: $dateShipped, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipmentMarkInTransit: InventoryShipmentMarkInTransitPayload }>(gql, args);
  return data.inventoryShipmentMarkInTransit;
}

/**
 * Receive an inventory shipment.
 * @scope write_inventory_shipments_received_items
 */
export interface InventoryShipmentReceiveArgs {
  bulkReceiveAction?: InventoryShipmentReceiveLineItemReason;
  dateReceived?: string;
  id: string;
  lineItems?: unknown;
}

export async function inventoryShipmentReceive(args: InventoryShipmentReceiveArgs): Promise<InventoryShipmentReceivePayload> {
  const gql = `#graphql
    mutation inventoryShipmentReceive($bulkReceiveAction: InventoryShipmentReceiveLineItemReason, $dateReceived: DateTime, $id: ID!, $lineItems: String) {
      inventoryShipmentReceive(bulkReceiveAction: $bulkReceiveAction, dateReceived: $dateReceived, id: $id, lineItems: $lineItems) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipmentReceive: InventoryShipmentReceivePayload }>(gql, args);
  return data.inventoryShipmentReceive;
}

/**
 * Remove items from an inventory shipment.
 * @scope write_inventory_shipments
 */
export interface InventoryShipmentRemoveItemsArgs {
  id: string;
  lineItems: unknown;
}

export async function inventoryShipmentRemoveItems(args: InventoryShipmentRemoveItemsArgs): Promise<InventoryShipmentRemoveItemsPayload> {
  const gql = `#graphql
    mutation inventoryShipmentRemoveItems($id: ID!, $lineItems: String) {
      inventoryShipmentRemoveItems(id: $id, lineItems: $lineItems) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipmentRemoveItems: InventoryShipmentRemoveItemsPayload }>(gql, args);
  return data.inventoryShipmentRemoveItems;
}

/**
 * Sets the barcode on an inventory shipment.
 * @scope write_inventory_shipments
 */
export interface InventoryShipmentSetBarcodeArgs {
  barcode: string;
  id: string;
}

export async function inventoryShipmentSetBarcode(args: InventoryShipmentSetBarcodeArgs): Promise<InventoryShipmentSetBarcodePayload> {
  const gql = `#graphql
    mutation inventoryShipmentSetBarcode($barcode: String!, $id: ID!) {
      inventoryShipmentSetBarcode(barcode: $barcode, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipmentSetBarcode: InventoryShipmentSetBarcodePayload }>(gql, args);
  return data.inventoryShipmentSetBarcode;
}

/**
 * Edits the tracking info on an inventory shipment.
 * @scope write_inventory_shipments
 */
export interface InventoryShipmentSetTrackingArgs {
  id: string;
  tracking: InventoryShipmentTrackingInput;
}

export async function inventoryShipmentSetTracking(args: InventoryShipmentSetTrackingArgs): Promise<InventoryShipmentSetTrackingPayload> {
  const gql = `#graphql
    mutation inventoryShipmentSetTracking($id: ID!, $tracking: InventoryShipmentTrackingInput!) {
      inventoryShipmentSetTracking(id: $id, tracking: $tracking) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipmentSetTracking: InventoryShipmentSetTrackingPayload }>(gql, args);
  return data.inventoryShipmentSetTracking;
}

/**
 * Updates items on an inventory shipment.
 * @scope write_inventory_shipments
 */
export interface InventoryShipmentUpdateItemQuantitiesArgs {
  id: string;
  items?: unknown;
}

export async function inventoryShipmentUpdateItemQuantities(args: InventoryShipmentUpdateItemQuantitiesArgs): Promise<InventoryShipmentUpdateItemQuantitiesPayload> {
  const gql = `#graphql
    mutation inventoryShipmentUpdateItemQuantities($id: ID!, $items: String) {
      inventoryShipmentUpdateItemQuantities(id: $id, items: $items) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryShipmentUpdateItemQuantities: InventoryShipmentUpdateItemQuantitiesPayload }>(gql, args);
  return data.inventoryShipmentUpdateItemQuantities;
}

/**
 * Cancels an inventory transfer.
 * @scope write_inventory_transfers
 */
export interface InventoryTransferCancelArgs {
  id: string;
}

export async function inventoryTransferCancel(args: InventoryTransferCancelArgs): Promise<InventoryTransferCancelPayload> {
  const gql = `#graphql
    mutation inventoryTransferCancel($id: ID!) {
      inventoryTransferCancel(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransferCancel: InventoryTransferCancelPayload }>(gql, args);
  return data.inventoryTransferCancel;
}

/**
 * Creates a draft inventory transfer to move inventory items between Location objects in your store. The transfer tracks which items to move, their quantities, and the origin and destination locations.
 * @scope write_inventory_transfers
 */
export interface InventoryTransferCreateArgs {
  input: InventoryTransferCreateInput;
}

export async function inventoryTransferCreate(args: InventoryTransferCreateArgs): Promise<InventoryTransferCreatePayload> {
  const gql = `#graphql
    mutation inventoryTransferCreate($input: InventoryTransferCreateInput!) {
      inventoryTransferCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransferCreate: InventoryTransferCreatePayload }>(gql, args);
  return data.inventoryTransferCreate;
}

/**
 * Creates an inventory transfer in ready to ship.
 * @scope write_inventory_transfers
 */
export interface InventoryTransferCreateAsReadyToShipArgs {
  input: InventoryTransferCreateAsReadyToShipInput;
}

export async function inventoryTransferCreateAsReadyToShip(args: InventoryTransferCreateAsReadyToShipArgs): Promise<InventoryTransferCreateAsReadyToShipPayload> {
  const gql = `#graphql
    mutation inventoryTransferCreateAsReadyToShip($input: InventoryTransferCreateAsReadyToShipInput!) {
      inventoryTransferCreateAsReadyToShip(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransferCreateAsReadyToShip: InventoryTransferCreateAsReadyToShipPayload }>(gql, args);
  return data.inventoryTransferCreateAsReadyToShip;
}

/**
 * Deletes an inventory transfer.
 * @scope write_inventory_transfers
 */
export interface InventoryTransferDeleteArgs {
  id: string;
}

export async function inventoryTransferDelete(args: InventoryTransferDeleteArgs): Promise<InventoryTransferDeletePayload> {
  const gql = `#graphql
    mutation inventoryTransferDelete($id: ID!) {
      inventoryTransferDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransferDelete: InventoryTransferDeletePayload }>(gql, args);
  return data.inventoryTransferDelete;
}

/**
 * This mutation allows duplicating an existing inventory transfer. The duplicated transfer will have the same
 * @scope write_inventory_transfers
 */
export interface InventoryTransferDuplicateArgs {
  id: string;
}

export async function inventoryTransferDuplicate(args: InventoryTransferDuplicateArgs): Promise<InventoryTransferDuplicatePayload> {
  const gql = `#graphql
    mutation inventoryTransferDuplicate($id: ID!) {
      inventoryTransferDuplicate(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransferDuplicate: InventoryTransferDuplicatePayload }>(gql, args);
  return data.inventoryTransferDuplicate;
}

/**
 * Edits an inventory transfer.
 * @scope write_inventory_transfers
 */
export interface InventoryTransferEditArgs {
  id: string;
  input: InventoryTransferEditInput;
}

export async function inventoryTransferEdit(args: InventoryTransferEditArgs): Promise<InventoryTransferEditPayload> {
  const gql = `#graphql
    mutation inventoryTransferEdit($id: ID!, $input: InventoryTransferEditInput!) {
      inventoryTransferEdit(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransferEdit: InventoryTransferEditPayload }>(gql, args);
  return data.inventoryTransferEdit;
}

/**
 * Sets an inventory transfer to ready to ship.
 * @scope write_inventory_transfers
 */
export interface InventoryTransferMarkAsReadyToShipArgs {
  id: string;
}

export async function inventoryTransferMarkAsReadyToShip(args: InventoryTransferMarkAsReadyToShipArgs): Promise<InventoryTransferMarkAsReadyToShipPayload> {
  const gql = `#graphql
    mutation inventoryTransferMarkAsReadyToShip($id: ID!) {
      inventoryTransferMarkAsReadyToShip(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransferMarkAsReadyToShip: InventoryTransferMarkAsReadyToShipPayload }>(gql, args);
  return data.inventoryTransferMarkAsReadyToShip;
}

/**
 * This mutation removes InventoryTransferLineItems,
 * @scope write_inventory_transfers
 */
export interface InventoryTransferRemoveItemsArgs {
  input: InventoryTransferRemoveItemsInput;
}

export async function inventoryTransferRemoveItems(args: InventoryTransferRemoveItemsArgs): Promise<InventoryTransferRemoveItemsPayload> {
  const gql = `#graphql
    mutation inventoryTransferRemoveItems($input: InventoryTransferRemoveItemsInput!) {
      inventoryTransferRemoveItems(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransferRemoveItems: InventoryTransferRemoveItemsPayload }>(gql, args);
  return data.inventoryTransferRemoveItems;
}

/**
 * This mutation sets the quantity for one or more line items on a Transfer.
 * @scope write_inventory_transfers
 */
export interface InventoryTransferSetItemsArgs {
  input: InventoryTransferSetItemsInput;
}

export async function inventoryTransferSetItems(args: InventoryTransferSetItemsArgs): Promise<InventoryTransferSetItemsPayload> {
  const gql = `#graphql
    mutation inventoryTransferSetItems($input: InventoryTransferSetItemsInput!) {
      inventoryTransferSetItems(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ inventoryTransferSetItems: InventoryTransferSetItemsPayload }>(gql, args);
  return data.inventoryTransferSetItems;
}

/**
 * Activates a location so that you can stock inventory at the location. Refer to the
 * @scope write_locations
 */
export interface LocationActivateArgs {
  locationId: string;
}

export async function locationActivate(args: LocationActivateArgs): Promise<LocationActivatePayload> {
  const gql = `#graphql
    mutation locationActivate($locationId: ID!) {
      locationActivate(locationId: $locationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locationActivate: LocationActivatePayload }>(gql, args);
  return data.locationActivate;
}

/**
 * Adds a new Location where you can stock inventory and fulfill orders. Locations represent physical places like warehouses, retail stores, or fulfillment centers.
 * @scope write_locations
 */
export interface LocationAddArgs {
  input: LocationAddInput;
}

export async function locationAdd(args: LocationAddArgs): Promise<LocationAddPayload> {
  const gql = `#graphql
    mutation locationAdd($input: LocationAddInput!) {
      locationAdd(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locationAdd: LocationAddPayload }>(gql, args);
  return data.locationAdd;
}

/**
 * Deactivates a location and moves inventory, pending orders, and moving transfers " "to a destination location.
 * @scope write_locations
 */
export interface LocationDeactivateArgs {
  destinationLocationId?: string;
  locationId: string;
}

export async function locationDeactivate(args: LocationDeactivateArgs): Promise<LocationDeactivatePayload> {
  const gql = `#graphql
    mutation locationDeactivate($destinationLocationId: ID, $locationId: ID!) {
      locationDeactivate(destinationLocationId: $destinationLocationId, locationId: $locationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locationDeactivate: LocationDeactivatePayload }>(gql, args);
  return data.locationDeactivate;
}

/**
 * Deletes a location.
 * @scope write_locations
 */
export interface LocationDeleteArgs {
  locationId: string;
}

export async function locationDelete(args: LocationDeleteArgs): Promise<LocationDeletePayload> {
  const gql = `#graphql
    mutation locationDelete($locationId: ID!) {
      locationDelete(locationId: $locationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locationDelete: LocationDeletePayload }>(gql, args);
  return data.locationDelete;
}

/**
 * Updates the properties of an existing Location. You can modify the location's name, address, whether it fulfills online orders, and custom metafields.
 * @scope write_locations
 */
export interface LocationEditArgs {
  id: string;
  input: LocationEditInput;
}

export async function locationEdit(args: LocationEditArgs): Promise<LocationEditPayload> {
  const gql = `#graphql
    mutation locationEdit($id: ID!, $input: LocationEditInput!) {
      locationEdit(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locationEdit: LocationEditPayload }>(gql, args);
  return data.locationEdit;
}

/**
 * Disables local pickup for a location.
 */
export interface LocationLocalPickupDisableArgs {
  locationId: string;
}

export async function locationLocalPickupDisable(args: LocationLocalPickupDisableArgs): Promise<LocationLocalPickupDisablePayload> {
  const gql = `#graphql
    mutation locationLocalPickupDisable($locationId: ID!) {
      locationLocalPickupDisable(locationId: $locationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locationLocalPickupDisable: LocationLocalPickupDisablePayload }>(gql, args);
  return data.locationLocalPickupDisable;
}

/**
 * Enables local pickup for a location so customers can collect their orders in person. Configures the estimated pickup time that customers see at checkout and optional instructions for finding or accessing the pickup location.
 */
export interface LocationLocalPickupEnableArgs {
  localPickupSettings: DeliveryLocationLocalPickupEnableInput;
}

export async function locationLocalPickupEnable(args: LocationLocalPickupEnableArgs): Promise<LocationLocalPickupEnablePayload> {
  const gql = `#graphql
    mutation locationLocalPickupEnable($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
      locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ locationLocalPickupEnable: LocationLocalPickupEnablePayload }>(gql, args);
  return data.locationLocalPickupEnable;
}










