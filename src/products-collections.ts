import { shopifyClient } from './client';
import type { Catalog, CatalogConnection, CatalogContextInput, CatalogContextUpdatePayload, CatalogCreateInput, CatalogCreatePayload, CatalogDeletePayload, CatalogSortKeys, CatalogType, CatalogUpdateInput, CatalogUpdatePayload, Collection, CollectionAddProductsPayload, CollectionAddProductsV2Payload, CollectionConnection, CollectionCreatePayload, CollectionDeleteInput, CollectionDeletePayload, CollectionDuplicateInput, CollectionDuplicatePayload, CollectionIdentifierInput, CollectionInput, CollectionPublishInput, CollectionPublishPayload, CollectionRemoveProductsPayload, CollectionReorderProductsPayload, CollectionSortKeys, CollectionUnpublishInput, CollectionUnpublishPayload, CollectionUpdatePayload, CombinedListingUpdatePayload, Count, Job, Media, OptionUpdateInput, Product, ProductBundleCreateInput, ProductBundleCreatePayload, ProductBundleUpdateInput, ProductBundleUpdatePayload, ProductChangeStatusPayload, ProductConnection, ProductCreateInput, ProductCreateMediaPayload, ProductCreatePayload, ProductDeleteInput, ProductDeleteMediaPayload, ProductDeletePayload, ProductDuplicateJob, ProductDuplicatePayload, ProductFeed, ProductFeedConnection, ProductFeedCreatePayload, ProductFeedDeletePayload, ProductFeedInput, ProductFullSyncPayload, ProductIdentifierInput, ProductInput, ProductJoinSellingPlanGroupsPayload, ProductLeaveSellingPlanGroupsPayload, ProductOptionCreateVariantStrategy, ProductOptionDeleteStrategy, ProductOptionsCreatePayload, ProductOptionsDeletePayload, ProductOptionsReorderPayload, ProductOptionUpdatePayload, ProductOptionUpdateVariantStrategy, ProductPublishInput, ProductPublishPayload, ProductReorderMediaPayload, ProductResourceFeedback, ProductSetIdentifiers, ProductSetInput, ProductSetPayload, ProductSortKeys, ProductStatus, ProductUnpublishInput, ProductUnpublishPayload, ProductUpdateIdentifiers, ProductUpdateInput, ProductUpdateMediaPayload, ProductUpdatePayload, ProductVariant, ProductVariantAppendMediaPayload, ProductVariantConnection, ProductVariantDetachMediaPayload, ProductVariantIdentifierInput, ProductVariantJoinSellingPlanGroupsPayload, ProductVariantLeaveSellingPlanGroupsPayload, ProductVariantRelationshipBulkUpdatePayload, ProductVariantsBulkCreatePayload, ProductVariantsBulkCreateStrategy, ProductVariantsBulkDeletePayload, ProductVariantsBulkReorderPayload, ProductVariantsBulkUpdatePayload, ProductVariantSortKeys, Publication, Return, SavedSearchConnection, SellingPlanGroup, SellingPlanGroupAddProductsPayload, SellingPlanGroupAddProductVariantsPayload, SellingPlanGroupConnection, SellingPlanGroupCreatePayload, SellingPlanGroupDeletePayload, SellingPlanGroupInput, SellingPlanGroupRemoveProductsPayload, SellingPlanGroupRemoveProductVariantsPayload, SellingPlanGroupResourceInput, SellingPlanGroupSortKeys, SellingPlanGroupUpdatePayload, StringConnection, Taxonomy, UserError } from './types';

// ============================================================
// Products & Collections
// 87 operations: 33 queries, 54 mutations
// ============================================================

// These are passed as plain objects. See Shopify docs for field shapes:

// ─── Queries ─────────────────────────────────────────────────────────

/**
 * Retrieves a catalog by its ID.
 */
export interface CatalogArgs {
  id: string;
}

export async function catalog(args: CatalogArgs): Promise<Catalog | null> {
  const gql = `#graphql
    query catalog($id: ID!) {
      catalog(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ catalog: Catalog | null }>(gql, args);
  return data.catalog;
}

/**
 * Returns the most recent catalog operations for the shop.
 * @scope read_products
 */
export async function catalogOperations(): Promise<string> {
  const gql = `#graphql
    query catalogOperations {
      catalogOperations {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ catalogOperations: string }>(gql);
  return data.catalogOperations;
}

/**
 * Returns a paginated list of catalogs for the shop. Catalogs control which products are published and how they're priced in different contexts, such as international markets (Canada vs. United States), B2B company locations (different branches of the same business), or specific sales channels (such as online store vs. POS).
 */
export interface CatalogsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: CatalogSortKeys;
  type?: CatalogType;
}

export async function catalogs(args?: CatalogsArgs): Promise<CatalogConnection> {
  const gql = `#graphql
    query catalogs($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CatalogSortKeys, $type: CatalogType) {
      catalogs(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey, type: $type) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ catalogs: CatalogConnection }>(gql, args);
  return data.catalogs;
}

/**
 * The count of catalogs belonging to the shop. Limited to a maximum of 10000 by default.
 */
export interface CatalogsCountArgs {
  limit?: number;
  query?: string;
  type?: CatalogType;
}

export async function catalogsCount(args?: CatalogsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query catalogsCount($limit: Int, $query: String, $type: CatalogType) {
      catalogsCount(limit: $limit, query: $query, type: $type) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ catalogsCount: Count | null }>(gql, args);
  return data.catalogsCount;
}

/**
 * Retrieves a collection by its ID.
 */
export interface CollectionArgs {
  id: string;
}

export async function collection(args: CollectionArgs): Promise<Collection | null> {
  const gql = `#graphql
    query collection($id: ID!) {
      collection(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collection: Collection | null }>(gql, args);
  return data.collection;
}

/**
 * Retrieves a collection by its unique handle identifier. Handles provide a URL-friendly way to reference collections and are commonly used in storefront URLs and navigation.
 * @scope read_products
 */
export interface CollectionByHandleArgs {
  handle: string;
}

export async function collectionByHandle(args: CollectionByHandleArgs): Promise<Collection | null> {
  const gql = `#graphql
    query collectionByHandle($handle: String!) {
      collectionByHandle(handle: $handle) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionByHandle: Collection | null }>(gql, args);
  return data.collectionByHandle;
}

/**
 * Return a collection by an identifier.
 * @scope read_products
 */
export interface CollectionByIdentifierArgs {
  identifier: CollectionIdentifierInput;
}

export async function collectionByIdentifier(args: CollectionByIdentifierArgs): Promise<Collection | null> {
  const gql = `#graphql
    query collectionByIdentifier($identifier: CollectionIdentifierInput!) {
      collectionByIdentifier(identifier: $identifier) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionByIdentifier: Collection | null }>(gql, args);
  return data.collectionByIdentifier;
}

/**
 * Lists all rules that can be used to create smart collections.
 */
export async function collectionRulesConditions(): Promise<unknown> {
  const gql = `#graphql
    query collectionRulesConditions {
      collectionRulesConditions {
        # Specify the fields you need returned
      }
    }
  `;
  return shopifyClient.request(gql);
}

/**
 * Returns a list of the shop's collection saved searches.
 * @scope read_products
 */
export interface CollectionSavedSearchesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function collectionSavedSearches(args?: CollectionSavedSearchesArgs): Promise<SavedSearchConnection> {
  const gql = `#graphql
    query collectionSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      collectionSavedSearches(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionSavedSearches: SavedSearchConnection }>(gql, args);
  return data.collectionSavedSearches;
}

/**
 * Retrieves a list of collections
 */
export interface CollectionsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: CollectionSortKeys;
}

export async function collections(args?: CollectionsArgs): Promise<CollectionConnection> {
  const gql = `#graphql
    query collections($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: CollectionSortKeys) {
      collections(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collections: CollectionConnection }>(gql, args);
  return data.collections;
}

/**
 * Count of collections. Limited to a maximum of 10000 by default.
 * @scope read_products
 */
export interface CollectionsCountArgs {
  limit?: number;
  query?: string;
  savedSearchId?: string;
}

export async function collectionsCount(args?: CollectionsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query collectionsCount($limit: Int, $query: String, $savedSearchId: ID) {
      collectionsCount(limit: $limit, query: $query, savedSearchId: $savedSearchId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionsCount: Count | null }>(gql, args);
  return data.collectionsCount;
}

/**
 * Retrieves a product by its ID.
 */
export interface ProductArgs {
  id: string;
}

export async function product(args: ProductArgs): Promise<Product | null> {
  const gql = `#graphql
    query product($id: ID!) {
      product(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ product: Product | null }>(gql, args);
  return data.product;
}

/**
 * Retrieves a Product using its handle. A handle is a unique, URL-friendly string that Shopify automatically generates from the product's title.
 * @scope read_products
 */
export interface ProductByHandleArgs {
  handle: string;
}

export async function productByHandle(args: ProductByHandleArgs): Promise<Product | null> {
  const gql = `#graphql
    query productByHandle($handle: String!) {
      productByHandle(handle: $handle) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productByHandle: Product | null }>(gql, args);
  return data.productByHandle;
}

/**
 * Return a product by an identifier.
 * @scope read_products
 */
export interface ProductByIdentifierArgs {
  identifier: ProductIdentifierInput;
}

export async function productByIdentifier(args: ProductByIdentifierArgs): Promise<Product | null> {
  const gql = `#graphql
    query productByIdentifier($identifier: ProductIdentifierInput!) {
      productByIdentifier(identifier: $identifier) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productByIdentifier: Product | null }>(gql, args);
  return data.productByIdentifier;
}

/**
 * Returns the product duplicate job.
 */
export interface ProductDuplicateJobArgs {
  id: string;
}

export async function productDuplicateJob(args: ProductDuplicateJobArgs): Promise<ProductDuplicateJob | null> {
  const gql = `#graphql
    query productDuplicateJob($id: ID!) {
      productDuplicateJob(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productDuplicateJob: ProductDuplicateJob | null }>(gql, args);
  return data.productDuplicateJob;
}

/**
 * Returns a ProductFeed resource by ID.
 * @scope read_product_listings
 */
export interface ProductFeedArgs {
  id: string;
}

export async function productFeed(args: ProductFeedArgs): Promise<ProductFeed | null> {
  const gql = `#graphql
    query productFeed($id: ID!) {
      productFeed(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productFeed: ProductFeed | null }>(gql, args);
  return data.productFeed;
}

/**
 * The product feeds for the shop.
 * @scope read_product_listings
 */
export interface ProductFeedsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function productFeeds(args?: ProductFeedsArgs): Promise<ProductFeedConnection> {
  const gql = `#graphql
    query productFeeds($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      productFeeds(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productFeeds: ProductFeedConnection }>(gql, args);
  return data.productFeeds;
}

/**
 * Returns a ProductOperation resource by ID.
 */
export interface ProductOperationArgs {
  id: string;
}

export async function productOperation(args: ProductOperationArgs): Promise<unknown> {
  const gql = `#graphql
    query productOperation($id: ID!) {
      productOperation(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  return shopifyClient.request(gql, args);
}

/**
 * Retrieves product resource feedback for the currently authenticated app, providing insights into product data quality, completeness, and optimization opportunities. This feedback helps apps guide merchants toward better product listings and improved store performance.
 * @scope read_resource_feedbacks
 */
export interface ProductResourceFeedbackArgs {
  channelId?: string;
  id: string;
}

export async function productResourceFeedback(args: ProductResourceFeedbackArgs): Promise<ProductResourceFeedback | null> {
  const gql = `#graphql
    query productResourceFeedback($channelId: ID, $id: ID!) {
      productResourceFeedback(channelId: $channelId, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productResourceFeedback: ProductResourceFeedback | null }>(gql, args);
  return data.productResourceFeedback;
}

/**
 * Returns a list of the shop's product saved searches.
 * @scope read_products
 */
export interface ProductSavedSearchesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function productSavedSearches(args?: ProductSavedSearchesArgs): Promise<SavedSearchConnection> {
  const gql = `#graphql
    query productSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      productSavedSearches(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productSavedSearches: SavedSearchConnection }>(gql, args);
  return data.productSavedSearches;
}

/**
 * Returns tags added to Product objects in the shop. Provides a paginated list of tag strings.
 * @scope read_products
 */
export interface ProductTagsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function productTags(args?: ProductTagsArgs): Promise<StringConnection> {
  const gql = `#graphql
    query productTags($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      productTags(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productTags: StringConnection }>(gql, args);
  return data.productTags;
}

/**
 * Returns a paginated list of product types assigned to products in the store. The maximum page size is 1000.
 * @scope read_products
 */
export interface ProductTypesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function productTypes(args?: ProductTypesArgs): Promise<StringConnection> {
  const gql = `#graphql
    query productTypes($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      productTypes(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productTypes: StringConnection }>(gql, args);
  return data.productTypes;
}

/**
 * Retrieves a product variant by its ID.
 */
export interface ProductVariantArgs {
  id: string;
}

export async function productVariant(args: ProductVariantArgs): Promise<ProductVariant | null> {
  const gql = `#graphql
    query productVariant($id: ID!) {
      productVariant(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariant: ProductVariant | null }>(gql, args);
  return data.productVariant;
}

/**
 * Return a product variant by an identifier.
 * @scope read_products
 */
export interface ProductVariantByIdentifierArgs {
  identifier: ProductVariantIdentifierInput;
}

export async function productVariantByIdentifier(args: ProductVariantByIdentifierArgs): Promise<ProductVariant | null> {
  const gql = `#graphql
    query productVariantByIdentifier($identifier: ProductVariantIdentifierInput!) {
      productVariantByIdentifier(identifier: $identifier) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantByIdentifier: ProductVariant | null }>(gql, args);
  return data.productVariantByIdentifier;
}

/**
 * Retrieves a list of product variants
 */
export interface ProductVariantsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: ProductVariantSortKeys;
}

export async function productVariants(args?: ProductVariantsArgs): Promise<ProductVariantConnection> {
  const gql = `#graphql
    query productVariants($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: ProductVariantSortKeys) {
      productVariants(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariants: ProductVariantConnection }>(gql, args);
  return data.productVariants;
}

/**
 * Count of product variants. Limited to a maximum of 10000 by default.
 * @scope read_products
 */
export interface ProductVariantsCountArgs {
  limit?: number;
  query?: string;
}

export async function productVariantsCount(args?: ProductVariantsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query productVariantsCount($limit: Int, $query: String) {
      productVariantsCount(limit: $limit, query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantsCount: Count | null }>(gql, args);
  return data.productVariantsCount;
}

/**
 * |-
 * @scope read_products
 */
export interface ProductVendorsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function productVendors(args?: ProductVendorsArgs): Promise<StringConnection> {
  const gql = `#graphql
    query productVendors($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      productVendors(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVendors: StringConnection }>(gql, args);
  return data.productVendors;
}

/**
 * Retrieves a list of products
 */
export interface ProductsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: ProductSortKeys;
}

export async function products(args?: ProductsArgs): Promise<ProductConnection> {
  const gql = `#graphql
    query products($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: ProductSortKeys) {
      products(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ products: ProductConnection }>(gql, args);
  return data.products;
}

/**
 * Count of products. Limited to a maximum of 10000 by default.
 * @scope read_products
 */
export interface ProductsCountArgs {
  limit?: number;
  query?: string;
  savedSearchId?: string;
}

export async function productsCount(args?: ProductsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query productsCount($limit: Int, $query: String, $savedSearchId: ID) {
      productsCount(limit: $limit, query: $query, savedSearchId: $savedSearchId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productsCount: Count | null }>(gql, args);
  return data.productsCount;
}

/**
 * Returns a count of published products by publication ID. Limited to a maximum of 10000 by default.
 * @scope read_publications
 */
export interface PublishedProductsCountArgs {
  limit?: number;
  publicationId: string;
}

export async function publishedProductsCount(args: PublishedProductsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query publishedProductsCount($limit: Int, $publicationId: ID!) {
      publishedProductsCount(limit: $limit, publicationId: $publicationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ publishedProductsCount: Count | null }>(gql, args);
  return data.publishedProductsCount;
}

/**
 * Returns a SellingPlanGroup resource by ID.
 */
export interface SellingPlanGroupArgs {
  id: string;
}

export async function sellingPlanGroup(args: SellingPlanGroupArgs): Promise<SellingPlanGroup | null> {
  const gql = `#graphql
    query sellingPlanGroup($id: ID!) {
      sellingPlanGroup(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ sellingPlanGroup: SellingPlanGroup | null }>(gql, args);
  return data.sellingPlanGroup;
}

/**
 * Retrieves a paginated list of SellingPlanGroup objects that belong to the app making the API call. Selling plan groups are selling methods like subscriptions, preorders, or other purchase options that merchants offer to customers.
 */
export interface SellingPlanGroupsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: SellingPlanGroupSortKeys;
}

export async function sellingPlanGroups(args?: SellingPlanGroupsArgs): Promise<SellingPlanGroupConnection> {
  const gql = `#graphql
    query sellingPlanGroups($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: SellingPlanGroupSortKeys) {
      sellingPlanGroups(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ sellingPlanGroups: SellingPlanGroupConnection }>(gql, args);
  return data.sellingPlanGroups;
}

/**
 * Access to Shopify's standardized product taxonomy for categorizing products. The Taxonomy organizes products into a hierarchical tree structure with categories, attributes, and values.
 */
export async function taxonomy(): Promise<Taxonomy | null> {
  const gql = `#graphql
    query taxonomy {
      taxonomy {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ taxonomy: Taxonomy | null }>(gql);
  return data.taxonomy;
}

// ─── Mutations ─────────────────────────────────────────────────────────

/**
 * Modifies which contexts, like markets or B2B company locations, can access a Catalog. You can add or remove contexts to control where the catalog's products and prices are available.
 * @scope write_products
 */
export interface CatalogContextUpdateArgs {
  catalogId: string;
  contextsToAdd?: CatalogContextInput;
  contextsToRemove?: CatalogContextInput;
}

export async function catalogContextUpdate(args: CatalogContextUpdateArgs): Promise<CatalogContextUpdatePayload> {
  const gql = `#graphql
    mutation catalogContextUpdate($catalogId: ID!, $contextsToAdd: CatalogContextInput, $contextsToRemove: CatalogContextInput) {
      catalogContextUpdate(catalogId: $catalogId, contextsToAdd: $contextsToAdd, contextsToRemove: $contextsToRemove) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ catalogContextUpdate: CatalogContextUpdatePayload }>(gql, args);
  return data.catalogContextUpdate;
}

/**
 * Creates a Catalog that controls product availability and pricing for specific contexts like markets or B2B company locations.
 * @scope write_products
 */
export interface CatalogCreateArgs {
  input: CatalogCreateInput;
}

export async function catalogCreate(args: CatalogCreateArgs): Promise<CatalogCreatePayload> {
  const gql = `#graphql
    mutation catalogCreate($input: CatalogCreateInput!) {
      catalogCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ catalogCreate: CatalogCreatePayload }>(gql, args);
  return data.catalogCreate;
}

/**
 * Delete a catalog.
 * @scope write_products
 */
export interface CatalogDeleteArgs {
  deleteDependentResources?: boolean;
  id: string;
}

export async function catalogDelete(args: CatalogDeleteArgs): Promise<CatalogDeletePayload> {
  const gql = `#graphql
    mutation catalogDelete($deleteDependentResources: Boolean, $id: ID!) {
      catalogDelete(deleteDependentResources: $deleteDependentResources, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ catalogDelete: CatalogDeletePayload }>(gql, args);
  return data.catalogDelete;
}

/**
 * Updates an existing catalog's configuration. Catalogs control product publishing and pricing for specific contexts like markets or B2B company locations.
 * @scope write_products
 */
export interface CatalogUpdateArgs {
  id: string;
  input: CatalogUpdateInput;
}

export async function catalogUpdate(args: CatalogUpdateArgs): Promise<CatalogUpdatePayload> {
  const gql = `#graphql
    mutation catalogUpdate($id: ID!, $input: CatalogUpdateInput!) {
      catalogUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ catalogUpdate: CatalogUpdatePayload }>(gql, args);
  return data.catalogUpdate;
}

/**
 * Adds multiple products to an existing collection in a single operation. This mutation provides an efficient way to bulk-manage collection membership without individual product updates.
 * @scope write_products
 */
export interface CollectionAddProductsArgs {
  id: string;
  productIds: unknown;
}

export async function collectionAddProducts(args: CollectionAddProductsArgs): Promise<CollectionAddProductsPayload> {
  const gql = `#graphql
    mutation collectionAddProducts($id: ID!, $productIds: String) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionAddProducts: CollectionAddProductsPayload }>(gql, args);
  return data.collectionAddProducts;
}

/**
 * Adds products to a Collection asynchronously and returns a Job to track the operation's progress. This mutation handles large product sets efficiently by processing them in the background.
 * @scope write_products
 */
export interface CollectionAddProductsV2Args {
  id: string;
  productIds: unknown;
}

export async function collectionAddProductsV2(args: CollectionAddProductsV2Args): Promise<CollectionAddProductsV2Payload> {
  const gql = `#graphql
    mutation collectionAddProductsV2($id: ID!, $productIds: String) {
      collectionAddProductsV2(id: $id, productIds: $productIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionAddProductsV2: CollectionAddProductsV2Payload }>(gql, args);
  return data.collectionAddProductsV2;
}

/**
 * Creates a collection
 * @scope write_products
 */
export interface CollectionCreateArgs {
  input: CollectionInput;
}

export async function collectionCreate(args: CollectionCreateArgs): Promise<CollectionCreatePayload> {
  const gql = `#graphql
    mutation collectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionCreate: CollectionCreatePayload }>(gql, args);
  return data.collectionCreate;
}

/**
 * Deletes a collection and removes it permanently from the store. This operation cannot be undone and will remove the collection from all sales channels where it was published.
 * @scope write_products
 */
export interface CollectionDeleteArgs {
  input: CollectionDeleteInput;
}

export async function collectionDelete(args: CollectionDeleteArgs): Promise<CollectionDeletePayload> {
  const gql = `#graphql
    mutation collectionDelete($input: CollectionDeleteInput!) {
      collectionDelete(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionDelete: CollectionDeletePayload }>(gql, args);
  return data.collectionDelete;
}

/**
 * Duplicates a collection.
 * @scope write_products
 */
export interface CollectionDuplicateArgs {
  input: CollectionDuplicateInput;
}

export async function collectionDuplicate(args: CollectionDuplicateArgs): Promise<CollectionDuplicatePayload> {
  const gql = `#graphql
    mutation collectionDuplicate($input: CollectionDuplicateInput!) {
      collectionDuplicate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionDuplicate: CollectionDuplicatePayload }>(gql, args);
  return data.collectionDuplicate;
}

/**
 * Publishes a collection to a channel.
 * @scope write_publications
 */
export interface CollectionPublishArgs {
  input: CollectionPublishInput;
}

export async function collectionPublish(args: CollectionPublishArgs): Promise<CollectionPublishPayload> {
  const gql = `#graphql
    mutation collectionPublish($input: CollectionPublishInput!) {
      collectionPublish(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionPublish: CollectionPublishPayload }>(gql, args);
  return data.collectionPublish;
}

/**
 * Removes multiple products from a collection in a single operation. This mutation can process large product sets (up to 250 products) and may take significant time to complete for collections with many products.
 * @scope write_products
 */
export interface CollectionRemoveProductsArgs {
  id: string;
  productIds: unknown;
}

export async function collectionRemoveProducts(args: CollectionRemoveProductsArgs): Promise<CollectionRemoveProductsPayload> {
  const gql = `#graphql
    mutation collectionRemoveProducts($id: ID!, $productIds: String) {
      collectionRemoveProducts(id: $id, productIds: $productIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionRemoveProducts: CollectionRemoveProductsPayload }>(gql, args);
  return data.collectionRemoveProducts;
}

/**
 * Asynchronously reorders products within a specified collection. Instead of returning an updated collection, this mutation returns a job, which should be polled. The `Collection.sortOrder` must be MANUAL.
 * @scope write_products
 */
export interface CollectionReorderProductsArgs {
  id: string;
  moves: unknown;
}

export async function collectionReorderProducts(args: CollectionReorderProductsArgs): Promise<CollectionReorderProductsPayload> {
  const gql = `#graphql
    mutation collectionReorderProducts($id: ID!, $moves: String) {
      collectionReorderProducts(id: $id, moves: $moves) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionReorderProducts: CollectionReorderProductsPayload }>(gql, args);
  return data.collectionReorderProducts;
}

/**
 * Unpublishes a collection.
 * @scope write_publications
 */
export interface CollectionUnpublishArgs {
  input: CollectionUnpublishInput;
}

export async function collectionUnpublish(args: CollectionUnpublishArgs): Promise<CollectionUnpublishPayload> {
  const gql = `#graphql
    mutation collectionUnpublish($input: CollectionUnpublishInput!) {
      collectionUnpublish(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionUnpublish: CollectionUnpublishPayload }>(gql, args);
  return data.collectionUnpublish;
}

/**
 * Updates a collection,
 * @scope write_products
 */
export interface CollectionUpdateArgs {
  input: CollectionInput;
}

export async function collectionUpdate(args: CollectionUpdateArgs): Promise<CollectionUpdatePayload> {
  const gql = `#graphql
    mutation collectionUpdate($input: CollectionInput!) {
      collectionUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ collectionUpdate: CollectionUpdatePayload }>(gql, args);
  return data.collectionUpdate;
}

/**
 * Add, remove and update CombinedListings of a given Product.
 * @scope write_products
 */
export interface CombinedListingUpdateArgs {
  optionsAndValues?: unknown;
  parentProductId: string;
  productsAdded?: unknown;
  productsEdited?: unknown;
  productsRemovedIds?: unknown;
  title?: string;
}

export async function combinedListingUpdate(args: CombinedListingUpdateArgs): Promise<CombinedListingUpdatePayload> {
  const gql = `#graphql
    mutation combinedListingUpdate($optionsAndValues: String, $parentProductId: ID!, $productsAdded: String, $productsEdited: String, $productsRemovedIds: String, $title: String) {
      combinedListingUpdate(optionsAndValues: $optionsAndValues, parentProductId: $parentProductId, productsAdded: $productsAdded, productsEdited: $productsEdited, productsRemovedIds: $productsRemovedIds, title: $title) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ combinedListingUpdate: CombinedListingUpdatePayload }>(gql, args);
  return data.combinedListingUpdate;
}

/**
 * Creates a product bundle that groups multiple Product objects together as components. The bundle appears as a single product in the store, with its price determined by the parent product and inventory calculated from the component products.
 * @scope write_products
 */
export interface ProductBundleCreateArgs {
  input: ProductBundleCreateInput;
}

export async function productBundleCreate(args: ProductBundleCreateArgs): Promise<ProductBundleCreatePayload> {
  const gql = `#graphql
    mutation productBundleCreate($input: ProductBundleCreateInput!) {
      productBundleCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productBundleCreate: ProductBundleCreatePayload }>(gql, args);
  return data.productBundleCreate;
}

/**
 * Updates a product bundle or componentized product.
 * @scope write_products
 */
export interface ProductBundleUpdateArgs {
  input: ProductBundleUpdateInput;
}

export async function productBundleUpdate(args: ProductBundleUpdateArgs): Promise<ProductBundleUpdatePayload> {
  const gql = `#graphql
    mutation productBundleUpdate($input: ProductBundleUpdateInput!) {
      productBundleUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productBundleUpdate: ProductBundleUpdatePayload }>(gql, args);
  return data.productBundleUpdate;
}

/**
 * Changes the status of a product. This allows you to set the availability of the product across all channels.
 * @scope write_products
 */
export interface ProductChangeStatusArgs {
  productId: string;
  status: ProductStatus;
}

export async function productChangeStatus(args: ProductChangeStatusArgs): Promise<ProductChangeStatusPayload> {
  const gql = `#graphql
    mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
      productChangeStatus(productId: $productId, status: $status) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productChangeStatus: ProductChangeStatusPayload }>(gql, args);
  return data.productChangeStatus;
}

/**
 * Creates a product
 * @scope write_products
 */
export interface ProductCreateArgs {
  media?: unknown;
  product?: ProductCreateInput;
  input?: ProductInput;
}

export async function productCreate(args?: ProductCreateArgs): Promise<ProductCreatePayload> {
  const gql = `#graphql
    mutation productCreate($media: String, $product: ProductCreateInput, $input: ProductInput) {
      productCreate(media: $media, product: $product, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productCreate: ProductCreatePayload }>(gql, args);
  return data.productCreate;
}

/**
 * Adds media files to a Product, such as images, videos, or 3D models. Media files enhance product listings by providing visual representations that help customers understand the product.
 * @scope write_products
 */
export interface ProductCreateMediaArgs {
  media: unknown;
  productId: string;
}

export async function productCreateMedia(args: ProductCreateMediaArgs): Promise<ProductCreateMediaPayload> {
  const gql = `#graphql
    mutation productCreateMedia($media: String, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productCreateMedia: ProductCreateMediaPayload }>(gql, args);
  return data.productCreateMedia;
}

/**
 * Permanently deletes a product and all its associated data, including variants, media, publications, and inventory items.
 * @scope write_products
 */
export interface ProductDeleteArgs {
  input: ProductDeleteInput;
  synchronous?: boolean;
}

export async function productDelete(args: ProductDeleteArgs): Promise<ProductDeletePayload> {
  const gql = `#graphql
    mutation productDelete($input: ProductDeleteInput!, $synchronous: Boolean) {
      productDelete(input: $input, synchronous: $synchronous) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productDelete: ProductDeletePayload }>(gql, args);
  return data.productDelete;
}

/**
 * Deletes media from a Product, such as images, videos, and 3D models.
 * @scope write_products
 */
export interface ProductDeleteMediaArgs {
  mediaIds: unknown;
  productId: string;
}

export async function productDeleteMedia(args: ProductDeleteMediaArgs): Promise<ProductDeleteMediaPayload> {
  const gql = `#graphql
    mutation productDeleteMedia($mediaIds: String, $productId: ID!) {
      productDeleteMedia(mediaIds: $mediaIds, productId: $productId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productDeleteMedia: ProductDeleteMediaPayload }>(gql, args);
  return data.productDeleteMedia;
}

/**
 * Duplicates a product.
 * @scope write_products
 */
export interface ProductDuplicateArgs {
  includeImages?: boolean;
  includeTranslations?: boolean;
  newStatus?: ProductStatus;
  newTitle: string;
  productId: string;
  synchronous?: boolean;
}

export async function productDuplicate(args: ProductDuplicateArgs): Promise<ProductDuplicatePayload> {
  const gql = `#graphql
    mutation productDuplicate($includeImages: Boolean, $includeTranslations: Boolean, $newStatus: ProductStatus, $newTitle: String!, $productId: ID!, $synchronous: Boolean) {
      productDuplicate(includeImages: $includeImages, includeTranslations: $includeTranslations, newStatus: $newStatus, newTitle: $newTitle, productId: $productId, synchronous: $synchronous) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productDuplicate: ProductDuplicatePayload }>(gql, args);
  return data.productDuplicate;
}

/**
 * Creates a product feed for a specific publication.
 */
export interface ProductFeedCreateArgs {
  input?: ProductFeedInput;
}

export async function productFeedCreate(args?: ProductFeedCreateArgs): Promise<ProductFeedCreatePayload> {
  const gql = `#graphql
    mutation productFeedCreate($input: ProductFeedInput) {
      productFeedCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productFeedCreate: ProductFeedCreatePayload }>(gql, args);
  return data.productFeedCreate;
}

/**
 * Deletes a product feed for a specific publication.
 */
export interface ProductFeedDeleteArgs {
  id: string;
}

export async function productFeedDelete(args: ProductFeedDeleteArgs): Promise<ProductFeedDeletePayload> {
  const gql = `#graphql
    mutation productFeedDelete($id: ID!) {
      productFeedDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productFeedDelete: ProductFeedDeletePayload }>(gql, args);
  return data.productFeedDelete;
}

/**
 * Runs the full product sync for a given shop.
 */
export interface ProductFullSyncArgs {
  beforeUpdatedAt?: string;
  id: string;
  updatedAtSince?: string;
}

export async function productFullSync(args: ProductFullSyncArgs): Promise<ProductFullSyncPayload> {
  const gql = `#graphql
    mutation productFullSync($beforeUpdatedAt: DateTime, $id: ID!, $updatedAtSince: DateTime) {
      productFullSync(beforeUpdatedAt: $beforeUpdatedAt, id: $id, updatedAtSince: $updatedAtSince) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productFullSync: ProductFullSyncPayload }>(gql, args);
  return data.productFullSync;
}

/**
 * Adds multiple selling plan groups to a product.
 * @scope write_products
 */
export interface ProductJoinSellingPlanGroupsArgs {
  id: string;
  sellingPlanGroupIds: unknown;
}

export async function productJoinSellingPlanGroups(args: ProductJoinSellingPlanGroupsArgs): Promise<ProductJoinSellingPlanGroupsPayload> {
  const gql = `#graphql
    mutation productJoinSellingPlanGroups($id: ID!, $sellingPlanGroupIds: String) {
      productJoinSellingPlanGroups(id: $id, sellingPlanGroupIds: $sellingPlanGroupIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productJoinSellingPlanGroups: ProductJoinSellingPlanGroupsPayload }>(gql, args);
  return data.productJoinSellingPlanGroups;
}

/**
 * Removes multiple groups from a product.
 * @scope write_products
 */
export interface ProductLeaveSellingPlanGroupsArgs {
  id: string;
  sellingPlanGroupIds: unknown;
}

export async function productLeaveSellingPlanGroups(args: ProductLeaveSellingPlanGroupsArgs): Promise<ProductLeaveSellingPlanGroupsPayload> {
  const gql = `#graphql
    mutation productLeaveSellingPlanGroups($id: ID!, $sellingPlanGroupIds: String) {
      productLeaveSellingPlanGroups(id: $id, sellingPlanGroupIds: $sellingPlanGroupIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productLeaveSellingPlanGroups: ProductLeaveSellingPlanGroupsPayload }>(gql, args);
  return data.productLeaveSellingPlanGroups;
}

/**
 * Updates an option
 * @scope write_products
 */
export interface ProductOptionUpdateArgs {
  option: OptionUpdateInput;
  optionValuesToAdd?: unknown;
  optionValuesToDelete?: unknown;
  optionValuesToUpdate?: unknown;
  productId: string;
  variantStrategy?: ProductOptionUpdateVariantStrategy;
}

export async function productOptionUpdate(args: ProductOptionUpdateArgs): Promise<ProductOptionUpdatePayload> {
  const gql = `#graphql
    mutation productOptionUpdate($option: OptionUpdateInput!, $optionValuesToAdd: String, $optionValuesToDelete: String, $optionValuesToUpdate: String, $productId: ID!, $variantStrategy: ProductOptionUpdateVariantStrategy) {
      productOptionUpdate(option: $option, optionValuesToAdd: $optionValuesToAdd, optionValuesToDelete: $optionValuesToDelete, optionValuesToUpdate: $optionValuesToUpdate, productId: $productId, variantStrategy: $variantStrategy) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productOptionUpdate: ProductOptionUpdatePayload }>(gql, args);
  return data.productOptionUpdate;
}

/**
 * Creates one or more options
 * @scope write_products
 */
export interface ProductOptionsCreateArgs {
  options: unknown;
  productId: string;
  variantStrategy?: ProductOptionCreateVariantStrategy;
}

export async function productOptionsCreate(args: ProductOptionsCreateArgs): Promise<ProductOptionsCreatePayload> {
  const gql = `#graphql
    mutation productOptionsCreate($options: String, $productId: ID!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(options: $options, productId: $productId, variantStrategy: $variantStrategy) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productOptionsCreate: ProductOptionsCreatePayload }>(gql, args);
  return data.productOptionsCreate;
}

/**
 * Deletes one or more options
 * @scope write_products
 */
export interface ProductOptionsDeleteArgs {
  options: unknown;
  productId: string;
  strategy?: ProductOptionDeleteStrategy;
}

export async function productOptionsDelete(args: ProductOptionsDeleteArgs): Promise<ProductOptionsDeletePayload> {
  const gql = `#graphql
    mutation productOptionsDelete($options: String, $productId: ID!, $strategy: ProductOptionDeleteStrategy) {
      productOptionsDelete(options: $options, productId: $productId, strategy: $strategy) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productOptionsDelete: ProductOptionsDeletePayload }>(gql, args);
  return data.productOptionsDelete;
}

/**
 * Reorders the options and
 * @scope write_products
 */
export interface ProductOptionsReorderArgs {
  options: unknown;
  productId: string;
}

export async function productOptionsReorder(args: ProductOptionsReorderArgs): Promise<ProductOptionsReorderPayload> {
  const gql = `#graphql
    mutation productOptionsReorder($options: String, $productId: ID!) {
      productOptionsReorder(options: $options, productId: $productId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productOptionsReorder: ProductOptionsReorderPayload }>(gql, args);
  return data.productOptionsReorder;
}

/**
 * Publishes a Product to specified Publication objects.
 * @scope write_publications
 */
export interface ProductPublishArgs {
  input: ProductPublishInput;
}

export async function productPublish(args: ProductPublishArgs): Promise<ProductPublishPayload> {
  const gql = `#graphql
    mutation productPublish($input: ProductPublishInput!) {
      productPublish(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productPublish: ProductPublishPayload }>(gql, args);
  return data.productPublish;
}

/**
 * Reorders media attached to a product, changing their sequence in product displays. The operation processes asynchronously to handle products with large media collections.
 * @scope write_products
 */
export interface ProductReorderMediaArgs {
  id: string;
  moves: unknown;
}

export async function productReorderMedia(args: ProductReorderMediaArgs): Promise<ProductReorderMediaPayload> {
  const gql = `#graphql
    mutation productReorderMedia($id: ID!, $moves: String) {
      productReorderMedia(id: $id, moves: $moves) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productReorderMedia: ProductReorderMediaPayload }>(gql, args);
  return data.productReorderMedia;
}

/**
 * Performs multiple operations to create or update products in a single request.
 * @scope write_products
 */
export interface ProductSetArgs {
  identifier?: ProductSetIdentifiers;
  input: ProductSetInput;
  synchronous?: boolean;
}

export async function productSet(args: ProductSetArgs): Promise<ProductSetPayload> {
  const gql = `#graphql
    mutation productSet($identifier: ProductSetIdentifiers, $input: ProductSetInput!, $synchronous: Boolean) {
      productSet(identifier: $identifier, input: $input, synchronous: $synchronous) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productSet: ProductSetPayload }>(gql, args);
  return data.productSet;
}

/**
 * Unpublishes a product.
 * @scope write_publications
 */
export interface ProductUnpublishArgs {
  input: ProductUnpublishInput;
}

export async function productUnpublish(args: ProductUnpublishArgs): Promise<ProductUnpublishPayload> {
  const gql = `#graphql
    mutation productUnpublish($input: ProductUnpublishInput!) {
      productUnpublish(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productUnpublish: ProductUnpublishPayload }>(gql, args);
  return data.productUnpublish;
}

/**
 * Updates a product
 * @scope write_products
 */
export interface ProductUpdateArgs {
  identifier?: ProductUpdateIdentifiers;
  media?: unknown;
  product?: ProductUpdateInput;
  input?: ProductInput;
}

export async function productUpdate(args?: ProductUpdateArgs): Promise<ProductUpdatePayload> {
  const gql = `#graphql
    mutation productUpdate($identifier: ProductUpdateIdentifiers, $media: String, $product: ProductUpdateInput, $input: ProductInput) {
      productUpdate(identifier: $identifier, media: $media, product: $product, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productUpdate: ProductUpdatePayload }>(gql, args);
  return data.productUpdate;
}

/**
 * Updates properties of media attached to a Product. You can modify alt text for accessibility or change preview images for existing media items.
 * @scope write_products
 */
export interface ProductUpdateMediaArgs {
  media: unknown;
  productId: string;
}

export async function productUpdateMedia(args: ProductUpdateMediaArgs): Promise<ProductUpdateMediaPayload> {
  const gql = `#graphql
    mutation productUpdateMedia($media: String, $productId: ID!) {
      productUpdateMedia(media: $media, productId: $productId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productUpdateMedia: ProductUpdateMediaPayload }>(gql, args);
  return data.productUpdateMedia;
}

/**
 * Appends existing media from a product to specific variants of that product, creating associations between media files and particular product options. This allows different variants to showcase relevant images or videos.
 * @scope write_products
 */
export interface ProductVariantAppendMediaArgs {
  productId: string;
  variantMedia: unknown;
}

export async function productVariantAppendMedia(args: ProductVariantAppendMediaArgs): Promise<ProductVariantAppendMediaPayload> {
  const gql = `#graphql
    mutation productVariantAppendMedia($productId: ID!, $variantMedia: String) {
      productVariantAppendMedia(productId: $productId, variantMedia: $variantMedia) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantAppendMedia: ProductVariantAppendMediaPayload }>(gql, args);
  return data.productVariantAppendMedia;
}

/**
 * Detaches media from product variants.
 * @scope write_products
 */
export interface ProductVariantDetachMediaArgs {
  productId: string;
  variantMedia: unknown;
}

export async function productVariantDetachMedia(args: ProductVariantDetachMediaArgs): Promise<ProductVariantDetachMediaPayload> {
  const gql = `#graphql
    mutation productVariantDetachMedia($productId: ID!, $variantMedia: String) {
      productVariantDetachMedia(productId: $productId, variantMedia: $variantMedia) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantDetachMedia: ProductVariantDetachMediaPayload }>(gql, args);
  return data.productVariantDetachMedia;
}

/**
 * Adds multiple selling plan groups to a product variant.
 * @scope write_products
 */
export interface ProductVariantJoinSellingPlanGroupsArgs {
  id: string;
  sellingPlanGroupIds: unknown;
}

export async function productVariantJoinSellingPlanGroups(args: ProductVariantJoinSellingPlanGroupsArgs): Promise<ProductVariantJoinSellingPlanGroupsPayload> {
  const gql = `#graphql
    mutation productVariantJoinSellingPlanGroups($id: ID!, $sellingPlanGroupIds: String) {
      productVariantJoinSellingPlanGroups(id: $id, sellingPlanGroupIds: $sellingPlanGroupIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantJoinSellingPlanGroups: ProductVariantJoinSellingPlanGroupsPayload }>(gql, args);
  return data.productVariantJoinSellingPlanGroups;
}

/**
 * Remove multiple groups from a product variant.
 * @scope write_products
 */
export interface ProductVariantLeaveSellingPlanGroupsArgs {
  id: string;
  sellingPlanGroupIds: unknown;
}

export async function productVariantLeaveSellingPlanGroups(args: ProductVariantLeaveSellingPlanGroupsArgs): Promise<ProductVariantLeaveSellingPlanGroupsPayload> {
  const gql = `#graphql
    mutation productVariantLeaveSellingPlanGroups($id: ID!, $sellingPlanGroupIds: String) {
      productVariantLeaveSellingPlanGroups(id: $id, sellingPlanGroupIds: $sellingPlanGroupIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantLeaveSellingPlanGroups: ProductVariantLeaveSellingPlanGroupsPayload }>(gql, args);
  return data.productVariantLeaveSellingPlanGroups;
}

/**
 * Creates new bundles, updates component quantities in existing bundles, and removes bundle components for one or multiple ProductVariant objects.
 * @scope write_products
 */
export interface ProductVariantRelationshipBulkUpdateArgs {
  input: unknown;
}

export async function productVariantRelationshipBulkUpdate(args: ProductVariantRelationshipBulkUpdateArgs): Promise<ProductVariantRelationshipBulkUpdatePayload> {
  const gql = `#graphql
    mutation productVariantRelationshipBulkUpdate($input: String) {
      productVariantRelationshipBulkUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantRelationshipBulkUpdate: ProductVariantRelationshipBulkUpdatePayload }>(gql, args);
  return data.productVariantRelationshipBulkUpdate;
}

/**
 * Creates multiple product variants
 * @scope write_products
 */
export interface ProductVariantsBulkCreateArgs {
  media?: unknown;
  productId: string;
  strategy?: ProductVariantsBulkCreateStrategy;
  variants: unknown;
}

export async function productVariantsBulkCreate(args: ProductVariantsBulkCreateArgs): Promise<ProductVariantsBulkCreatePayload> {
  const gql = `#graphql
    mutation productVariantsBulkCreate($media: String, $productId: ID!, $strategy: ProductVariantsBulkCreateStrategy, $variants: String) {
      productVariantsBulkCreate(media: $media, productId: $productId, strategy: $strategy, variants: $variants) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantsBulkCreate: ProductVariantsBulkCreatePayload }>(gql, args);
  return data.productVariantsBulkCreate;
}

/**
 * Deletes multiple variants in a single Product. Specify the product ID and an array of variant IDs to remove variants in bulk. You can call this mutation directly or through the bulkOperationRunMutation mutation. Returns the updated product and any UserError objects.
 * @scope write_products
 */
export interface ProductVariantsBulkDeleteArgs {
  productId: string;
  variantsIds: unknown;
}

export async function productVariantsBulkDelete(args: ProductVariantsBulkDeleteArgs): Promise<ProductVariantsBulkDeletePayload> {
  const gql = `#graphql
    mutation productVariantsBulkDelete($productId: ID!, $variantsIds: String) {
      productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantsBulkDelete: ProductVariantsBulkDeletePayload }>(gql, args);
  return data.productVariantsBulkDelete;
}

/**
 * Reorders multiple variants in a single product. This mutation can be called directly or via the bulkOperation.
 * @scope write_products
 */
export interface ProductVariantsBulkReorderArgs {
  positions: unknown;
  productId: string;
}

export async function productVariantsBulkReorder(args: ProductVariantsBulkReorderArgs): Promise<ProductVariantsBulkReorderPayload> {
  const gql = `#graphql
    mutation productVariantsBulkReorder($positions: String, $productId: ID!) {
      productVariantsBulkReorder(positions: $positions, productId: $productId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantsBulkReorder: ProductVariantsBulkReorderPayload }>(gql, args);
  return data.productVariantsBulkReorder;
}

/**
 * Updates multiple product variants
 * @scope write_products
 */
export interface ProductVariantsBulkUpdateArgs {
  allowPartialUpdates?: boolean;
  media?: unknown;
  productId: string;
  variants: unknown;
}

export async function productVariantsBulkUpdate(args: ProductVariantsBulkUpdateArgs): Promise<ProductVariantsBulkUpdatePayload> {
  const gql = `#graphql
    mutation productVariantsBulkUpdate($allowPartialUpdates: Boolean, $media: String, $productId: ID!, $variants: String) {
      productVariantsBulkUpdate(allowPartialUpdates: $allowPartialUpdates, media: $media, productId: $productId, variants: $variants) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ productVariantsBulkUpdate: ProductVariantsBulkUpdatePayload }>(gql, args);
  return data.productVariantsBulkUpdate;
}

/**
 * Adds multiple product variants to a selling plan group.
 * @scope write_products
 */
export interface SellingPlanGroupAddProductVariantsArgs {
  id: string;
  productVariantIds: unknown;
}

export async function sellingPlanGroupAddProductVariants(args: SellingPlanGroupAddProductVariantsArgs): Promise<SellingPlanGroupAddProductVariantsPayload> {
  const gql = `#graphql
    mutation sellingPlanGroupAddProductVariants($id: ID!, $productVariantIds: String) {
      sellingPlanGroupAddProductVariants(id: $id, productVariantIds: $productVariantIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ sellingPlanGroupAddProductVariants: SellingPlanGroupAddProductVariantsPayload }>(gql, args);
  return data.sellingPlanGroupAddProductVariants;
}

/**
 * Adds multiple products to a selling plan group.
 * @scope write_products
 */
export interface SellingPlanGroupAddProductsArgs {
  id: string;
  productIds: unknown;
}

export async function sellingPlanGroupAddProducts(args: SellingPlanGroupAddProductsArgs): Promise<SellingPlanGroupAddProductsPayload> {
  const gql = `#graphql
    mutation sellingPlanGroupAddProducts($id: ID!, $productIds: String) {
      sellingPlanGroupAddProducts(id: $id, productIds: $productIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ sellingPlanGroupAddProducts: SellingPlanGroupAddProductsPayload }>(gql, args);
  return data.sellingPlanGroupAddProducts;
}

/**
 * Creates a selling plan group that defines how products can be sold and purchased. A selling plan group represents a selling method such as "Subscribe and save", "Pre-order", or "Try before you buy" and contains one or more selling plans with specific billing, delivery, and pricing policies.
 * @scope write_products
 */
export interface SellingPlanGroupCreateArgs {
  input: SellingPlanGroupInput;
  resources?: SellingPlanGroupResourceInput;
}

export async function sellingPlanGroupCreate(args: SellingPlanGroupCreateArgs): Promise<SellingPlanGroupCreatePayload> {
  const gql = `#graphql
    mutation sellingPlanGroupCreate($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
      sellingPlanGroupCreate(input: $input, resources: $resources) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ sellingPlanGroupCreate: SellingPlanGroupCreatePayload }>(gql, args);
  return data.sellingPlanGroupCreate;
}

/**
 * Delete a Selling Plan Group. This does not affect subscription contracts.
 * @scope write_products
 */
export interface SellingPlanGroupDeleteArgs {
  id: string;
}

export async function sellingPlanGroupDelete(args: SellingPlanGroupDeleteArgs): Promise<SellingPlanGroupDeletePayload> {
  const gql = `#graphql
    mutation sellingPlanGroupDelete($id: ID!) {
      sellingPlanGroupDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ sellingPlanGroupDelete: SellingPlanGroupDeletePayload }>(gql, args);
  return data.sellingPlanGroupDelete;
}

/**
 * Removes multiple product variants from a selling plan group.
 * @scope write_products
 */
export interface SellingPlanGroupRemoveProductVariantsArgs {
  id: string;
  productVariantIds: unknown;
}

export async function sellingPlanGroupRemoveProductVariants(args: SellingPlanGroupRemoveProductVariantsArgs): Promise<SellingPlanGroupRemoveProductVariantsPayload> {
  const gql = `#graphql
    mutation sellingPlanGroupRemoveProductVariants($id: ID!, $productVariantIds: String) {
      sellingPlanGroupRemoveProductVariants(id: $id, productVariantIds: $productVariantIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ sellingPlanGroupRemoveProductVariants: SellingPlanGroupRemoveProductVariantsPayload }>(gql, args);
  return data.sellingPlanGroupRemoveProductVariants;
}

/**
 * Removes multiple products from a selling plan group.
 * @scope write_products
 */
export interface SellingPlanGroupRemoveProductsArgs {
  id: string;
  productIds: unknown;
}

export async function sellingPlanGroupRemoveProducts(args: SellingPlanGroupRemoveProductsArgs): Promise<SellingPlanGroupRemoveProductsPayload> {
  const gql = `#graphql
    mutation sellingPlanGroupRemoveProducts($id: ID!, $productIds: String) {
      sellingPlanGroupRemoveProducts(id: $id, productIds: $productIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ sellingPlanGroupRemoveProducts: SellingPlanGroupRemoveProductsPayload }>(gql, args);
  return data.sellingPlanGroupRemoveProducts;
}

/**
 * Update a Selling Plan Group.
 * @scope write_products
 */
export interface SellingPlanGroupUpdateArgs {
  id: string;
  input: SellingPlanGroupInput;
}

export async function sellingPlanGroupUpdate(args: SellingPlanGroupUpdateArgs): Promise<SellingPlanGroupUpdatePayload> {
  const gql = `#graphql
    mutation sellingPlanGroupUpdate($id: ID!, $input: SellingPlanGroupInput!) {
      sellingPlanGroupUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ sellingPlanGroupUpdate: SellingPlanGroupUpdatePayload }>(gql, args);
  return data.sellingPlanGroupUpdate;
}










