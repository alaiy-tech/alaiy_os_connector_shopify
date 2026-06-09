import { shopifyClient } from './client';
import type { App, BulkOperation, BulkOperationCancelPayload, BulkOperationConnection, BulkOperationRunMutationPayload, BulkOperationRunQueryPayload, BulkOperationsSortKeys, BulkOperationType, BulkProductResourceFeedbackCreatePayload, Channel, Count, DeletionEventConnection, DeletionEventSortKeys, DeletionEventSubjectType, Event, EventBridgeServerPixelUpdatePayload, EventBridgeWebhookSubscriptionCreatePayload, EventBridgeWebhookSubscriptionInput, EventBridgeWebhookSubscriptionUpdatePayload, EventConnection, EventSortKeys, FlowTriggerReceivePayload, ProductResourceFeedbackInput, PubSubServerPixelUpdatePayload, PubSubWebhookSubscriptionCreatePayload, PubSubWebhookSubscriptionInput, PubSubWebhookSubscriptionUpdatePayload, ServerPixelCreatePayload, ServerPixelDeletePayload, WebhookSubscription, WebhookSubscriptionConnection, WebhookSubscriptionCreatePayload, WebhookSubscriptionDeletePayload, WebhookSubscriptionFormat, WebhookSubscriptionInput, WebhookSubscriptionSortKeys, WebhookSubscriptionTopic, WebhookSubscriptionUpdatePayload, WebPixelCreatePayload, WebPixelDeletePayload, WebPixelInput, WebPixelUpdatePayload } from './types';

// ============================================================
// Webhooks, Events & Bulk Operations
// 31 operations
// ============================================================

/** Returns a webhook subscription by ID. */
export interface WebhookSubscriptionArgs {
  id: string;
}

export async function webhookSubscription(args: WebhookSubscriptionArgs): Promise<string | null> {
  const gql = `#graphql
    query webhookSubscription($id: ID!) {
      webhookSubscription(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webhookSubscription: string | null }>(gql, args);
  return data.webhookSubscription;
}

/** Retrieves a paginated list of webhook subscriptions created using the API for the current app and shop. */
export interface WebhookSubscriptionsArgs {
  after?: string;
  before?: string;
  first?: number;
  format?: WebhookSubscriptionFormat;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: WebhookSubscriptionSortKeys;
  topics?: WebhookSubscriptionTopic[];
  uri?: string;
  callbackUrl?: string;
}

export async function webhookSubscriptions(args?: WebhookSubscriptionsArgs): Promise<WebhookSubscriptionConnection> {
  const gql = `#graphql
    query webhookSubscriptions($after: String, $before: String, $first: Int, $format: WebhookSubscriptionFormat, $last: Int, $query: String, $reverse: Boolean, $sortKey: WebhookSubscriptionSortKeys, $topics: [WebhookSubscriptionTopic!]!, $uri: String, $callbackUrl: URL) {
      webhookSubscriptions(after: $after, before: $before, first: $first, format: $format, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey, topics: $topics, uri: $uri, callbackUrl: $callbackUrl) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webhookSubscriptions: WebhookSubscriptionConnection }>(gql, args);
  return data.webhookSubscriptions;
}

/** The count of webhook subscriptions. */
export interface WebhookSubscriptionsCountArgs {
  limit?: number;
  query?: string;
}

export async function webhookSubscriptionsCount(args?: WebhookSubscriptionsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query webhookSubscriptionsCount($limit: Int, $query: String) {
      webhookSubscriptionsCount(limit: $limit, query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webhookSubscriptionsCount: Count | null }>(gql, args);
  return data.webhookSubscriptionsCount;
}

/** Retrieves a single event by ID. Events chronicle activities in your store such as resource creation, updates, or staff comments. The query returns an [`Event`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Event) interface of type [`BasicEvent`](https://shopify.... */
export interface EventArgs {
  id: string;
}

export async function event(args: EventArgs): Promise<Event | null> {
  const gql = `#graphql
    query event($id: ID!) {
      event(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ event: Event | null }>(gql, args);
  return data.event;
}

/** A paginated list of events that chronicle activities in the store. [`Event`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Event) is an interface implemented by types such as [`BasicEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BasicEvent) an... */
export interface EventsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: EventSortKeys;
}

export async function events(args?: EventsArgs): Promise<EventConnection | null> {
  const gql = `#graphql
    query events($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: EventSortKeys) {
      events(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ events: EventConnection | null }>(gql, args);
  return data.events;
}

/** Count of events. Limited to a maximum of 10000. */
export interface EventsCountArgs {
  query?: string;
}

export async function eventsCount(args?: EventsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query eventsCount($query: String) {
      eventsCount(query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ eventsCount: Count | null }>(gql, args);
  return data.eventsCount;
}

/** Returns a `BulkOperation` resource by ID. */
export interface BulkOperationArgs {
  id: string;
}

export async function bulkOperation(args: BulkOperationArgs): Promise<string> {
  const gql = `#graphql
    query bulkOperation($id: ID!) {
      bulkOperation(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ bulkOperation: string }>(gql, args);
  return data.bulkOperation;
}

/** Returns the app's bulk operations meeting the specified filters. Defaults to sorting by created\_at, with newest operations first. */
export interface BulkOperationsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: BulkOperationsSortKeys;
}

export async function bulkOperations(args?: BulkOperationsArgs): Promise<BulkOperationConnection> {
  const gql = `#graphql
    query bulkOperations($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: BulkOperationsSortKeys) {
      bulkOperations(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ bulkOperations: BulkOperationConnection }>(gql, args);
  return data.bulkOperations;
}

/** Deprecated. Use [bulkOperations](https://shopify.dev/docs/api/admin-graphql/latest/queries/bulkOperations) with status filter instead. */
export interface CurrentBulkOperationArgs {
  type?: BulkOperationType;
}

export async function currentBulkOperation(args?: CurrentBulkOperationArgs): Promise<string> {
  const gql = `#graphql
    query currentBulkOperation($type: BulkOperationType) {
      currentBulkOperation(type: $type) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ currentBulkOperation: string }>(gql, args);
  return data.currentBulkOperation;
}

/** The server pixel configured by the app. */
export async function serverPixel(): Promise<string> {
  const gql = `#graphql
    query serverPixel {
      serverPixel {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ serverPixel: string }>(gql);
  return data.serverPixel;
}

/** Returns a [web pixel](https://shopify.dev/docs/apps/build/marketing-analytics/build-web-pixels) by ID. */
export interface WebPixelArgs {
  id?: string;
}

export async function webPixel(args?: WebPixelArgs): Promise<string> {
  const gql = `#graphql
    query webPixel($id: ID) {
      webPixel(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webPixel: string }>(gql, args);
  return data.webPixel;
}

/** Deprecated. Use [events](https://shopify.dev/docs/api/admin-graphql/latest/queries/events) instead. */
export interface DeletionEventsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: DeletionEventSortKeys;
  subjectTypes?: DeletionEventSubjectType[];
}

export async function deletionEvents(args?: DeletionEventsArgs): Promise<DeletionEventConnection> {
  const gql = `#graphql
    query deletionEvents($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: DeletionEventSortKeys, $subjectTypes: [DeletionEventSubjectType!]!) {
      deletionEvents(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey, subjectTypes: $subjectTypes) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ deletionEvents: DeletionEventConnection }>(gql, args);
  return data.deletionEvents;
}

/** Creates a webhook subscription that notifies your [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) when specific events occur in a shop. Webhooks push event data to your endpoint immediately when changes happen, eliminating the need for polling. */
export interface WebhookSubscriptionCreateArgs {
  topic: WebhookSubscriptionTopic;
  webhookSubscription: WebhookSubscriptionInput;
}

export async function webhookSubscriptionCreate(args: WebhookSubscriptionCreateArgs): Promise<WebhookSubscriptionCreatePayload> {
  const gql = `#graphql
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webhookSubscriptionCreate: WebhookSubscriptionCreatePayload }>(gql, args);
  return data.webhookSubscriptionCreate;
}

/** Deletes a [`WebhookSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscription) and stops all future webhooks to its endpoint. Returns the deleted subscription's ID for confirmation. */
export interface WebhookSubscriptionDeleteArgs {
  id: string;
}

export async function webhookSubscriptionDelete(args: WebhookSubscriptionDeleteArgs): Promise<WebhookSubscriptionDeletePayload> {
  const gql = `#graphql
    mutation webhookSubscriptionDelete($id: ID!) {
      webhookSubscriptionDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webhookSubscriptionDelete: WebhookSubscriptionDeletePayload }>(gql, args);
  return data.webhookSubscriptionDelete;
}

/** Updates a webhook subscription's configuration. Modify the endpoint URL, event filters, included fields, or metafield namespaces without recreating the subscription. */
export interface WebhookSubscriptionUpdateArgs {
  id: string;
  webhookSubscription: WebhookSubscriptionInput;
}

export async function webhookSubscriptionUpdate(args: WebhookSubscriptionUpdateArgs): Promise<WebhookSubscriptionUpdatePayload> {
  const gql = `#graphql
    mutation webhookSubscriptionUpdate($id: ID!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webhookSubscriptionUpdate: WebhookSubscriptionUpdatePayload }>(gql, args);
  return data.webhookSubscriptionUpdate;
}

/** Deprecated. Use [webhookSubscriptionCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionCreate) instead. */
export interface EventBridgeWebhookSubscriptionCreateArgs {
  topic: WebhookSubscriptionTopic;
  webhookSubscription: EventBridgeWebhookSubscriptionInput;
}

export async function eventBridgeWebhookSubscriptionCreate(args: EventBridgeWebhookSubscriptionCreateArgs): Promise<EventBridgeWebhookSubscriptionCreatePayload> {
  const gql = `#graphql
    mutation eventBridgeWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: EventBridgeWebhookSubscriptionInput!) {
      eventBridgeWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ eventBridgeWebhookSubscriptionCreate: EventBridgeWebhookSubscriptionCreatePayload }>(gql, args);
  return data.eventBridgeWebhookSubscriptionCreate;
}

/** Deprecated. Use [webhookSubscriptionUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionUpdate) instead. */
export interface EventBridgeWebhookSubscriptionUpdateArgs {
  id: string;
  webhookSubscription: EventBridgeWebhookSubscriptionInput;
}

export async function eventBridgeWebhookSubscriptionUpdate(args: EventBridgeWebhookSubscriptionUpdateArgs): Promise<EventBridgeWebhookSubscriptionUpdatePayload> {
  const gql = `#graphql
    mutation eventBridgeWebhookSubscriptionUpdate($id: ID!, $webhookSubscription: EventBridgeWebhookSubscriptionInput!) {
      eventBridgeWebhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ eventBridgeWebhookSubscriptionUpdate: EventBridgeWebhookSubscriptionUpdatePayload }>(gql, args);
  return data.eventBridgeWebhookSubscriptionUpdate;
}

/** Deprecated. Use [webhookSubscriptionCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionCreate) instead. */
export interface PubSubWebhookSubscriptionCreateArgs {
  topic: WebhookSubscriptionTopic;
  webhookSubscription: PubSubWebhookSubscriptionInput;
}

export async function pubSubWebhookSubscriptionCreate(args: PubSubWebhookSubscriptionCreateArgs): Promise<PubSubWebhookSubscriptionCreatePayload> {
  const gql = `#graphql
    mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
      pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pubSubWebhookSubscriptionCreate: PubSubWebhookSubscriptionCreatePayload }>(gql, args);
  return data.pubSubWebhookSubscriptionCreate;
}

/** Deprecated. Use [webhookSubscriptionUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionUpdate) instead. */
export interface PubSubWebhookSubscriptionUpdateArgs {
  id: string;
  webhookSubscription: PubSubWebhookSubscriptionInput;
}

export async function pubSubWebhookSubscriptionUpdate(args: PubSubWebhookSubscriptionUpdateArgs): Promise<PubSubWebhookSubscriptionUpdatePayload> {
  const gql = `#graphql
    mutation pubSubWebhookSubscriptionUpdate($id: ID!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
      pubSubWebhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pubSubWebhookSubscriptionUpdate: PubSubWebhookSubscriptionUpdatePayload }>(gql, args);
  return data.pubSubWebhookSubscriptionUpdate;
}

/** Starts the cancelation process of a running bulk operation. */
export interface BulkOperationCancelArgs {
  id: string;
}

export async function bulkOperationCancel(args: BulkOperationCancelArgs): Promise<BulkOperationCancelPayload> {
  const gql = `#graphql
    mutation bulkOperationCancel($id: ID!) {
      bulkOperationCancel(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ bulkOperationCancel: BulkOperationCancelPayload }>(gql, args);
  return data.bulkOperationCancel;
}

/** Requires Only accessible by supported access tokens: <https://shopify.dev/docs/api/usage/bulk-operations/queries#access-token-considerations>. */
export interface BulkOperationRunMutationArgs {
  clientIdentifier?: string;
  mutation: string;
  stagedUploadPath: string;
  groupObjects?: boolean;
}

export async function bulkOperationRunMutation(args: BulkOperationRunMutationArgs): Promise<BulkOperationRunMutationPayload> {
  const gql = `#graphql
    mutation bulkOperationRunMutation($clientIdentifier: String, $mutation: String!, $stagedUploadPath: String!, $groupObjects: Boolean) {
      bulkOperationRunMutation(clientIdentifier: $clientIdentifier, mutation: $mutation, stagedUploadPath: $stagedUploadPath, groupObjects: $groupObjects) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ bulkOperationRunMutation: BulkOperationRunMutationPayload }>(gql, args);
  return data.bulkOperationRunMutation;
}

/** Requires Only accessible by supported access tokens: <https://shopify.dev/docs/api/usage/bulk-operations/queries#access-token-considerations>. */
export interface BulkOperationRunQueryArgs {
  groupObjects?: boolean;
  query: string;
}

export async function bulkOperationRunQuery(args: BulkOperationRunQueryArgs): Promise<BulkOperationRunQueryPayload> {
  const gql = `#graphql
    mutation bulkOperationRunQuery($groupObjects: Boolean!, $query: String!) {
      bulkOperationRunQuery(groupObjects: $groupObjects, query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ bulkOperationRunQuery: BulkOperationRunQueryPayload }>(gql, args);
  return data.bulkOperationRunQuery;
}

/** Requires `write_resource_feedbacks` access scope. Also: App must be configured to use the Storefront API or as a Sales Channel. */
export interface BulkProductResourceFeedbackCreateArgs {
  feedbackInput: ProductResourceFeedbackInput[];
}

export async function bulkProductResourceFeedbackCreate(args: BulkProductResourceFeedbackCreateArgs): Promise<BulkProductResourceFeedbackCreatePayload> {
  const gql = `#graphql
    mutation bulkProductResourceFeedbackCreate($feedbackInput: [ProductResourceFeedbackInput!]!) {
      bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ bulkProductResourceFeedbackCreate: BulkProductResourceFeedbackCreatePayload }>(gql, args);
  return data.bulkProductResourceFeedbackCreate;
}

/** Triggers any workflows that begin with the trigger specified in the request body. To learn more, refer to [*Create Shopify Flow triggers*](https://shopify.dev/apps/flow/triggers). */
export interface FlowTriggerReceiveArgs {
  handle?: string;
  payload?: unknown;
  body?: string;
}

export async function flowTriggerReceive(args?: FlowTriggerReceiveArgs): Promise<FlowTriggerReceivePayload> {
  const gql = `#graphql
    mutation flowTriggerReceive($handle: String, $payload: JSON, $body: String) {
      flowTriggerReceive(handle: $handle, payload: $payload, body: $body) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ flowTriggerReceive: FlowTriggerReceivePayload }>(gql, args);
  return data.flowTriggerReceive;
}

/** Requires `write_pixels` access scope. Also: The app must have the read\_customer\_events access scope, write\_server\_pixels access scope, and user access permission. */
export async function serverPixelCreate(): Promise<ServerPixelCreatePayload> {
  const gql = `#graphql
    mutation serverPixelCreate {
      serverPixelCreate {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ serverPixelCreate: ServerPixelCreatePayload }>(gql);
  return data.serverPixelCreate;
}

/** Requires `write_pixels` access scope. Also: The app must have the write\_server\_pixels access scope, and user access permission. */
export async function serverPixelDelete(): Promise<ServerPixelDeletePayload> {
  const gql = `#graphql
    mutation serverPixelDelete {
      serverPixelDelete {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ serverPixelDelete: ServerPixelDeletePayload }>(gql);
  return data.serverPixelDelete;
}

/** Requires `write_pixels` access scope. Also: The app must have the read\_customer\_events and write\_server\_pixels access scopes. */
export interface EventBridgeServerPixelUpdateArgs {
  arn: string;
}

export async function eventBridgeServerPixelUpdate(args: EventBridgeServerPixelUpdateArgs): Promise<EventBridgeServerPixelUpdatePayload> {
  const gql = `#graphql
    mutation eventBridgeServerPixelUpdate($arn: ARN!) {
      eventBridgeServerPixelUpdate(arn: $arn) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ eventBridgeServerPixelUpdate: EventBridgeServerPixelUpdatePayload }>(gql, args);
  return data.eventBridgeServerPixelUpdate;
}

/** Requires `write_pixels` access scope. Also: The app must have the read\_customer\_events and write\_server\_pixels access scopes. */
export interface PubSubServerPixelUpdateArgs {
  pubSubProject: string;
  pubSubTopic: string;
}

export async function pubSubServerPixelUpdate(args: PubSubServerPixelUpdateArgs): Promise<PubSubServerPixelUpdatePayload> {
  const gql = `#graphql
    mutation pubSubServerPixelUpdate($pubSubProject: String!, $pubSubTopic: String!) {
      pubSubServerPixelUpdate(pubSubProject: $pubSubProject, pubSubTopic: $pubSubTopic) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pubSubServerPixelUpdate: PubSubServerPixelUpdatePayload }>(gql, args);
  return data.pubSubServerPixelUpdate;
}

/** Requires `write_pixels` access scope. Also: The app requires read\_customer\_events access scope and user access permission. */
export interface WebPixelCreateArgs {
  webPixel: WebPixelInput;
}

export async function webPixelCreate(args: WebPixelCreateArgs): Promise<WebPixelCreatePayload> {
  const gql = `#graphql
    mutation webPixelCreate($webPixel: WebPixelInput!) {
      webPixelCreate(webPixel: $webPixel) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webPixelCreate: WebPixelCreatePayload }>(gql, args);
  return data.webPixelCreate;
}

/** Requires `write_pixels` access scope. Also: The app requires user access permission. */
export interface WebPixelDeleteArgs {
  id: string;
}

export async function webPixelDelete(args: WebPixelDeleteArgs): Promise<WebPixelDeletePayload> {
  const gql = `#graphql
    mutation webPixelDelete($id: ID!) {
      webPixelDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webPixelDelete: WebPixelDeletePayload }>(gql, args);
  return data.webPixelDelete;
}

/** Requires `write_pixels` access scope. Also: The app requires read\_customer\_events access scope and user access permission. */
export interface WebPixelUpdateArgs {
  id: string;
  webPixel: WebPixelInput;
}

export async function webPixelUpdate(args: WebPixelUpdateArgs): Promise<WebPixelUpdatePayload> {
  const gql = `#graphql
    mutation webPixelUpdate($id: ID!, $webPixel: WebPixelInput!) {
      webPixelUpdate(id: $id, webPixel: $webPixel) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ webPixelUpdate: WebPixelUpdatePayload }>(gql, args);
  return data.webPixelUpdate;
}

