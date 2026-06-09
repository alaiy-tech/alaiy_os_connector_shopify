import { shopifyClient } from './client';
import type { MetafieldAccess, MetafieldDefinition, MetafieldDefinitionConnection, MetafieldDefinitionConstraintStatus, MetafieldDefinitionConstraintSubtypeIdentifier, MetafieldDefinitionCreatePayload, MetafieldDefinitionDeletePayload, MetafieldDefinitionIdentifierInput, MetafieldDefinitionInput, MetafieldDefinitionPinnedStatus, MetafieldDefinitionPinPayload, MetafieldDefinitionSortKeys, MetafieldDefinitionUnpinPayload, MetafieldDefinitionUpdateInput, MetafieldDefinitionUpdatePayload, MetafieldIdentifierInput, MetafieldOwnerType, MetafieldsDeletePayload, MetafieldsSetInput, MetafieldsSetPayload, Metaobject, MetaobjectAccess, MetaobjectBulkDeletePayload, MetaobjectBulkDeleteWhereCondition, MetaobjectConnection, MetaobjectCreateInput, MetaobjectCreatePayload, MetaobjectDefinitionConnection, MetaobjectDefinitionCreateInput, MetaobjectDefinitionCreatePayload, MetaobjectDefinitionDeletePayload, MetaobjectDefinitionUpdateInput, MetaobjectDefinitionUpdatePayload, MetaobjectDeletePayload, MetaobjectHandleInput, MetaobjectUpdateInput, MetaobjectUpdatePayload, MetaobjectUpsertInput, MetaobjectUpsertPayload, StandardMetafieldDefinitionEnablePayload, StandardMetafieldDefinitionTemplateConnection, StandardMetaobjectDefinitionEnablePayload } from './types';

// ============================================================
// Metafields & Metaobjects
// 27 operations
// ============================================================

/** Requires API client to have access to the resource type associated with the metafield definition. */
export interface MetafieldDefinitionArgs {
  identifier?: MetafieldDefinitionIdentifierInput;
  id?: string;
}

export async function metafieldDefinition(args?: MetafieldDefinitionArgs): Promise<MetafieldAccess> {
  const gql = `#graphql
    query metafieldDefinition($identifier: MetafieldDefinitionIdentifierInput, $id: ID) {
      metafieldDefinition(identifier: $identifier, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metafieldDefinition: MetafieldAccess }>(gql, args);
  return data.metafieldDefinition;
}

/** Returns a list of metafield definitions. */
export interface MetafieldDefinitionsArgs {
  after?: string;
  before?: string;
  constraintStatus?: MetafieldDefinitionConstraintStatus;
  constraintSubtype?: MetafieldDefinitionConstraintSubtypeIdentifier;
  first?: number;
  key?: string;
  last?: number;
  namespace?: string;
  ownerType: MetafieldOwnerType;
  pinnedStatus?: MetafieldDefinitionPinnedStatus;
  query?: string;
  reverse?: boolean;
  sortKey?: MetafieldDefinitionSortKeys;
}

export async function metafieldDefinitions(args: MetafieldDefinitionsArgs): Promise<MetafieldDefinitionConnection> {
  const gql = `#graphql
    query metafieldDefinitions($after: String, $before: String, $constraintStatus: MetafieldDefinitionConstraintStatus, $constraintSubtype: MetafieldDefinitionConstraintSubtypeIdentifier, $first: Int, $key: String, $last: Int, $namespace: String, $ownerType: MetafieldOwnerType!, $pinnedStatus: MetafieldDefinitionPinnedStatus, $query: String, $reverse: Boolean, $sortKey: MetafieldDefinitionSortKeys) {
      metafieldDefinitions(after: $after, before: $before, constraintStatus: $constraintStatus, constraintSubtype: $constraintSubtype, first: $first, key: $key, last: $last, namespace: $namespace, ownerType: $ownerType, pinnedStatus: $pinnedStatus, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metafieldDefinitions: MetafieldDefinitionConnection }>(gql, args);
  return data.metafieldDefinitions;
}

/** The available metafield types that you can use when creating [`MetafieldDefinition`](https://shopify.dev/docs/api/admin-graphql/2026-04/objects/MetafieldDefinition) objects. Each type specifies what kind of data it stores (such as boolean, color, date, or references), its cate... */
export async function metafieldDefinitionTypes(): Promise<string> {
  const gql = `#graphql
    query metafieldDefinitionTypes {
      metafieldDefinitionTypes {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metafieldDefinitionTypes: string }>(gql);
  return data.metafieldDefinitionTypes;
}

/** Requires `read_metaobjects` access scope. */
export interface MetaobjectArgs {
  id: string;
}

export async function metaobject(args: MetaobjectArgs): Promise<Metaobject | null> {
  const gql = `#graphql
    query metaobject($id: ID!) {
      metaobject(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobject: Metaobject | null }>(gql, args);
  return data.metaobject;
}

/** Requires `read_metaobjects` access scope. */
export interface MetaobjectByHandleArgs {
  handle: MetaobjectHandleInput;
}

export async function metaobjectByHandle(args: MetaobjectByHandleArgs): Promise<Metaobject | null> {
  const gql = `#graphql
    query metaobjectByHandle($handle: MetaobjectHandleInput!) {
      metaobjectByHandle(handle: $handle) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectByHandle: Metaobject | null }>(gql, args);
  return data.metaobjectByHandle;
}

/** Requires `read_metaobjects` access scope. */
export interface MetaobjectsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: string;
  type: string;
}

export async function metaobjects(args: MetaobjectsArgs): Promise<MetaobjectConnection> {
  const gql = `#graphql
    query metaobjects($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: String, $type: String!) {
      metaobjects(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey, type: $type) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjects: MetaobjectConnection }>(gql, args);
  return data.metaobjects;
}

/** Requires `read_metaobject_definitions` access scope. */
export interface MetaobjectDefinitionArgs {
  id: string;
}

export async function metaobjectDefinition(args: MetaobjectDefinitionArgs): Promise<MetaobjectAccess> {
  const gql = `#graphql
    query metaobjectDefinition($id: ID!) {
      metaobjectDefinition(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectDefinition: MetaobjectAccess }>(gql, args);
  return data.metaobjectDefinition;
}

/** Requires `read_metaobject_definitions` access scope. */
export interface MetaobjectDefinitionByTypeArgs {
  type: string;
}

export async function metaobjectDefinitionByType(args: MetaobjectDefinitionByTypeArgs): Promise<MetaobjectAccess> {
  const gql = `#graphql
    query metaobjectDefinitionByType($type: String!) {
      metaobjectDefinitionByType(type: $type) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectDefinitionByType: MetaobjectAccess }>(gql, args);
  return data.metaobjectDefinitionByType;
}

/** Requires `read_metaobject_definitions` access scope. */
export interface MetaobjectDefinitionsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function metaobjectDefinitions(args?: MetaobjectDefinitionsArgs): Promise<MetaobjectDefinitionConnection> {
  const gql = `#graphql
    query metaobjectDefinitions($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      metaobjectDefinitions(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectDefinitions: MetaobjectDefinitionConnection }>(gql, args);
  return data.metaobjectDefinitions;
}

/** Retrieves preset metafield definition templates for common use cases. Each template provides a reserved namespace and key combination for specific purposes like product subtitles, care guides, or ISBN numbers. Use these templates to create standardized metafields across your s... */
export interface StandardMetafieldDefinitionTemplatesArgs {
  after?: string;
  before?: string;
  constraintStatus?: MetafieldDefinitionConstraintStatus;
  constraintSubtype?: MetafieldDefinitionConstraintSubtypeIdentifier;
  excludeActivated?: boolean;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function standardMetafieldDefinitionTemplates(args?: StandardMetafieldDefinitionTemplatesArgs): Promise<StandardMetafieldDefinitionTemplateConnection> {
  const gql = `#graphql
    query standardMetafieldDefinitionTemplates($after: String, $before: String, $constraintStatus: MetafieldDefinitionConstraintStatus, $constraintSubtype: MetafieldDefinitionConstraintSubtypeIdentifier, $excludeActivated: Boolean, $first: Int, $last: Int, $reverse: Boolean) {
      standardMetafieldDefinitionTemplates(after: $after, before: $before, constraintStatus: $constraintStatus, constraintSubtype: $constraintSubtype, excludeActivated: $excludeActivated, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ standardMetafieldDefinitionTemplates: StandardMetafieldDefinitionTemplateConnection }>(gql, args);
  return data.standardMetafieldDefinitionTemplates;
}

/** Requires API client to have access to the namespace and the resource type associated with the metafield definition. */
export interface MetafieldDefinitionCreateArgs {
  definition: MetafieldDefinitionInput;
}

export async function metafieldDefinitionCreate(args: MetafieldDefinitionCreateArgs): Promise<MetafieldDefinitionCreatePayload> {
  const gql = `#graphql
    mutation metafieldDefinitionCreate($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metafieldDefinitionCreate: MetafieldDefinitionCreatePayload }>(gql, args);
  return data.metafieldDefinitionCreate;
}

/** Requires API client to have access to the resource type associated with the metafield definition. */
export interface MetafieldDefinitionDeleteArgs {
  deleteAllAssociatedMetafields?: boolean;
  id?: string;
  identifier?: MetafieldDefinitionIdentifierInput;
}

export async function metafieldDefinitionDelete(args?: MetafieldDefinitionDeleteArgs): Promise<MetafieldDefinitionDeletePayload> {
  const gql = `#graphql
    mutation metafieldDefinitionDelete($deleteAllAssociatedMetafields: Boolean, $id: ID, $identifier: MetafieldDefinitionIdentifierInput) {
      metafieldDefinitionDelete(deleteAllAssociatedMetafields: $deleteAllAssociatedMetafields, id: $id, identifier: $identifier) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metafieldDefinitionDelete: MetafieldDefinitionDeletePayload }>(gql, args);
  return data.metafieldDefinitionDelete;
}

/** Requires API client to have access to the namespace and the resource type associated with the metafield definition. */
export interface MetafieldDefinitionPinArgs {
  definitionId?: string;
  identifier?: MetafieldDefinitionIdentifierInput;
}

export async function metafieldDefinitionPin(args?: MetafieldDefinitionPinArgs): Promise<MetafieldDefinitionPinPayload> {
  const gql = `#graphql
    mutation metafieldDefinitionPin($definitionId: ID, $identifier: MetafieldDefinitionIdentifierInput) {
      metafieldDefinitionPin(definitionId: $definitionId, identifier: $identifier) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metafieldDefinitionPin: MetafieldDefinitionPinPayload }>(gql, args);
  return data.metafieldDefinitionPin;
}

/** Requires API client to have access to the namespace and the resource type associated with the metafield definition. */
export interface MetafieldDefinitionUnpinArgs {
  definitionId?: string;
  identifier?: MetafieldDefinitionIdentifierInput;
}

export async function metafieldDefinitionUnpin(args?: MetafieldDefinitionUnpinArgs): Promise<MetafieldDefinitionUnpinPayload> {
  const gql = `#graphql
    mutation metafieldDefinitionUnpin($definitionId: ID, $identifier: MetafieldDefinitionIdentifierInput) {
      metafieldDefinitionUnpin(definitionId: $definitionId, identifier: $identifier) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metafieldDefinitionUnpin: MetafieldDefinitionUnpinPayload }>(gql, args);
  return data.metafieldDefinitionUnpin;
}

/** Requires API client to have access to the namespace and the resource type associated with the metafield definition. */
export interface MetafieldDefinitionUpdateArgs {
  definition: MetafieldDefinitionUpdateInput;
}

export async function metafieldDefinitionUpdate(args: MetafieldDefinitionUpdateArgs): Promise<MetafieldDefinitionUpdatePayload> {
  const gql = `#graphql
    mutation metafieldDefinitionUpdate($definition: MetafieldDefinitionUpdateInput!) {
      metafieldDefinitionUpdate(definition: $definition) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metafieldDefinitionUpdate: MetafieldDefinitionUpdatePayload }>(gql, args);
  return data.metafieldDefinitionUpdate;
}

/** Requires access defined by each metafield input `ownerId` scalar's type in a `MetafieldsSetInput` field. For example, setting a metafield on a `PRODUCT` requires the same access as mutating a `PRODUCT`. */
export interface MetafieldsDeleteArgs {
  metafields: MetafieldIdentifierInput[];
}

export async function metafieldsDelete(args: MetafieldsDeleteArgs): Promise<MetafieldsDeletePayload> {
  const gql = `#graphql
    mutation metafieldsDelete($metafields: [MetafieldIdentifierInput!]!) {
      metafieldsDelete(metafields: $metafields) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metafieldsDelete: MetafieldsDeletePayload }>(gql, args);
  return data.metafieldsDelete;
}

/** Requires the same access level needed to mutate the owner resource. For instance, if you want to set a metafield on a product, you need the same permissions as you would need to mutate a product. */
export interface MetafieldsSetArgs {
  metafields: MetafieldsSetInput[];
}

export async function metafieldsSet(args: MetafieldsSetArgs): Promise<MetafieldsSetPayload> {
  const gql = `#graphql
    mutation metafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metafieldsSet: MetafieldsSetPayload }>(gql, args);
  return data.metafieldsSet;
}

/** Requires `write_metaobjects` access scope. */
export interface MetaobjectBulkDeleteArgs {
  where: MetaobjectBulkDeleteWhereCondition;
}

export async function metaobjectBulkDelete(args: MetaobjectBulkDeleteArgs): Promise<MetaobjectBulkDeletePayload> {
  const gql = `#graphql
    mutation metaobjectBulkDelete($where: MetaobjectBulkDeleteWhereCondition!) {
      metaobjectBulkDelete(where: $where) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectBulkDelete: MetaobjectBulkDeletePayload }>(gql, args);
  return data.metaobjectBulkDelete;
}

/** Requires `write_metaobjects` access scope. */
export interface MetaobjectCreateArgs {
  metaobject: MetaobjectCreateInput;
}

export async function metaobjectCreate(args: MetaobjectCreateArgs): Promise<MetaobjectCreatePayload> {
  const gql = `#graphql
    mutation metaobjectCreate($metaobject: MetaobjectCreateInput!) {
      metaobjectCreate(metaobject: $metaobject) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectCreate: MetaobjectCreatePayload }>(gql, args);
  return data.metaobjectCreate;
}

/** Requires `write_metaobjects` access scope. */
export interface MetaobjectDeleteArgs {
  id: string;
}

export async function metaobjectDelete(args: MetaobjectDeleteArgs): Promise<MetaobjectDeletePayload> {
  const gql = `#graphql
    mutation metaobjectDelete($id: ID!) {
      metaobjectDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectDelete: MetaobjectDeletePayload }>(gql, args);
  return data.metaobjectDelete;
}

/** Requires `write_metaobjects` access scope. */
export interface MetaobjectUpdateArgs {
  id: string;
  metaobject: MetaobjectUpdateInput;
}

export async function metaobjectUpdate(args: MetaobjectUpdateArgs): Promise<MetaobjectUpdatePayload> {
  const gql = `#graphql
    mutation metaobjectUpdate($id: ID!, $metaobject: MetaobjectUpdateInput!) {
      metaobjectUpdate(id: $id, metaobject: $metaobject) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectUpdate: MetaobjectUpdatePayload }>(gql, args);
  return data.metaobjectUpdate;
}

/** Requires `write_metaobjects` access scope. */
export interface MetaobjectUpsertArgs {
  handle: MetaobjectHandleInput;
  metaobject: MetaobjectUpsertInput;
}

export async function metaobjectUpsert(args: MetaobjectUpsertArgs): Promise<MetaobjectUpsertPayload> {
  const gql = `#graphql
    mutation metaobjectUpsert($handle: MetaobjectHandleInput!, $metaobject: MetaobjectUpsertInput!) {
      metaobjectUpsert(handle: $handle, metaobject: $metaobject) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectUpsert: MetaobjectUpsertPayload }>(gql, args);
  return data.metaobjectUpsert;
}

/** Requires `write_metaobject_definitions` access scope. */
export interface MetaobjectDefinitionCreateArgs {
  definition: MetaobjectDefinitionCreateInput;
}

export async function metaobjectDefinitionCreate(args: MetaobjectDefinitionCreateArgs): Promise<MetaobjectDefinitionCreatePayload> {
  const gql = `#graphql
    mutation metaobjectDefinitionCreate($definition: MetaobjectDefinitionCreateInput!) {
      metaobjectDefinitionCreate(definition: $definition) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectDefinitionCreate: MetaobjectDefinitionCreatePayload }>(gql, args);
  return data.metaobjectDefinitionCreate;
}

/** Requires `write_metaobject_definitions` access scope. */
export interface MetaobjectDefinitionDeleteArgs {
  id: string;
}

export async function metaobjectDefinitionDelete(args: MetaobjectDefinitionDeleteArgs): Promise<MetaobjectDefinitionDeletePayload> {
  const gql = `#graphql
    mutation metaobjectDefinitionDelete($id: ID!) {
      metaobjectDefinitionDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectDefinitionDelete: MetaobjectDefinitionDeletePayload }>(gql, args);
  return data.metaobjectDefinitionDelete;
}

/** Requires `write_metaobject_definitions` access scope. */
export interface MetaobjectDefinitionUpdateArgs {
  definition: MetaobjectDefinitionUpdateInput;
  id: string;
}

export async function metaobjectDefinitionUpdate(args: MetaobjectDefinitionUpdateArgs): Promise<MetaobjectDefinitionUpdatePayload> {
  const gql = `#graphql
    mutation metaobjectDefinitionUpdate($definition: MetaobjectDefinitionUpdateInput!, $id: ID!) {
      metaobjectDefinitionUpdate(definition: $definition, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ metaobjectDefinitionUpdate: MetaobjectDefinitionUpdatePayload }>(gql, args);
  return data.metaobjectDefinitionUpdate;
}

/** Requires API client to have access to the resource type associated with the metafield definition owner type. */
export interface StandardMetafieldDefinitionEnableArgs {
  useAsCollectionCondition?: boolean;
  visibleToStorefrontApi?: boolean;
}

export async function standardMetafieldDefinitionEnable(args?: StandardMetafieldDefinitionEnableArgs): Promise<StandardMetafieldDefinitionEnablePayload> {
  const gql = `#graphql
    mutation standardMetafieldDefinitionEnable($useAsCollectionCondition: Boolean, $visibleToStorefrontApi: Boolean) {
      standardMetafieldDefinitionEnable(useAsCollectionCondition: $useAsCollectionCondition, visibleToStorefrontApi: $visibleToStorefrontApi) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ standardMetafieldDefinitionEnable: StandardMetafieldDefinitionEnablePayload }>(gql, args);
  return data.standardMetafieldDefinitionEnable;
}

/** Requires `write_metaobject_definitions` access scope. */
export interface StandardMetaobjectDefinitionEnableArgs {
  type: string;
}

export async function standardMetaobjectDefinitionEnable(args: StandardMetaobjectDefinitionEnableArgs): Promise<StandardMetaobjectDefinitionEnablePayload> {
  const gql = `#graphql
    mutation standardMetaobjectDefinitionEnable($type: String!) {
      standardMetaobjectDefinitionEnable(type: $type) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ standardMetaobjectDefinitionEnable: StandardMetaobjectDefinitionEnablePayload }>(gql, args);
  return data.standardMetaobjectDefinitionEnable;
}

