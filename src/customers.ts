import { shopifyClient } from './client';
import type { CompaniesDeletePayload, Company, CompanyAddressDeletePayload, CompanyAddressInput, CompanyAssignCustomerAsContactPayload, CompanyAssignMainContactPayload, CompanyConnection, CompanyContact, CompanyContactAssignRolePayload, CompanyContactAssignRolesPayload, CompanyContactCreatePayload, CompanyContactDeletePayload, CompanyContactInput, CompanyContactRemoveFromCompanyPayload, CompanyContactRevokeRolePayload, CompanyContactRevokeRolesPayload, CompanyContactRole, CompanyContactsDeletePayload, CompanyContactUpdatePayload, CompanyCreateInput, CompanyCreatePayload, CompanyDeletePayload, CompanyInput, CompanyLocation, CompanyLocationAssignAddressPayload, CompanyLocationAssignRolesPayload, CompanyLocationAssignStaffMembersPayload, CompanyLocationAssignTaxExemptionsPayload, CompanyLocationConnection, CompanyLocationCreatePayload, CompanyLocationCreateTaxRegistrationPayload, CompanyLocationDeletePayload, CompanyLocationInput, CompanyLocationRemoveStaffMembersPayload, CompanyLocationRevokeRolesPayload, CompanyLocationRevokeTaxExemptionsPayload, CompanyLocationRevokeTaxRegistrationPayload, CompanyLocationsDeletePayload, CompanyLocationSortKeys, CompanyLocationTaxSettingsUpdatePayload, CompanyLocationUpdateInput, CompanyLocationUpdatePayload, CompanyRevokeMainContactPayload, CompanySortKeys, CompanyUpdatePayload, Count, Customer, CustomerAccountPage, CustomerAccountPageConnection, CustomerAddressCreatePayload, CustomerAddressDeletePayload, CustomerAddressUpdatePayload, CustomerAddTaxExemptionsPayload, CustomerCancelDataErasurePayload, CustomerConnection, CustomerCreatePayload, CustomerDeleteInput, CustomerDeletePayload, CustomerEmailMarketingConsentUpdateInput, CustomerEmailMarketingConsentUpdatePayload, CustomerGenerateAccountActivationUrlPayload, CustomerIdentifierInput, CustomerInput, CustomerMergeOverrideFields, CustomerMergePayload, CustomerMergePreview, CustomerMergeRequest, CustomerPaymentMethod, CustomerPaymentMethodCreditCardCreatePayload, CustomerPaymentMethodCreditCardUpdatePayload, CustomerPaymentMethodGetUpdateUrlPayload, CustomerPaymentMethodPaypalBillingAgreementCreatePayload, CustomerPaymentMethodPaypalBillingAgreementUpdatePayload, CustomerPaymentMethodRemoteCreatePayload, CustomerPaymentMethodRemoteInput, CustomerPaymentMethodRevokePayload, CustomerPaymentMethodSendUpdateEmailPayload, CustomerRemoveTaxExemptionsPayload, CustomerReplaceTaxExemptionsPayload, CustomerRequestDataErasurePayload, CustomerSavedSearchSortKeys, CustomerSegmentMemberConnection, CustomerSegmentMembersQuery, CustomerSegmentMembersQueryCreatePayload, CustomerSegmentMembersQueryInput, CustomerSendAccountInviteEmailPayload, CustomerSetIdentifiers, CustomerSetInput, CustomerSetPayload, CustomerSmsMarketingConsentUpdateInput, CustomerSmsMarketingConsentUpdatePayload, CustomerSortKeys, CustomerUpdateDefaultAddressPayload, CustomerUpdatePayload, EmailInput, MailingAddress, MailingAddressInput, Product, Return, SavedSearchConnection, Segment, SegmentConnection, SegmentCreatePayload, SegmentDeletePayload, SegmentFilterConnection, SegmentMembershipResponse, SegmentMigrationConnection, SegmentSortKeys, SegmentUpdatePayload, SegmentValueConnection, StoreCreditAccount, StoreCreditAccountCreditInput, StoreCreditAccountCreditPayload, StoreCreditAccountCreditTransaction, StoreCreditAccountDebitInput, StoreCreditAccountDebitPayload, StoreCreditConfiguration, SubscriptionBillingAttempt, SubscriptionBillingAttemptConnection, SubscriptionBillingAttemptCreatePayload, SubscriptionBillingAttemptInput, SubscriptionBillingAttemptInventoryPolicy, SubscriptionBillingAttemptPaymentProcessingPolicy, SubscriptionBillingAttemptsSortKeys, SubscriptionBillingCycle, SubscriptionBillingCycleBulkChargePayload, SubscriptionBillingCycleBulkFilters, SubscriptionBillingCycleBulkSearchPayload, SubscriptionBillingCycleChargePayload, SubscriptionBillingCycleConnection, SubscriptionBillingCycleContractDraftCommitPayload, SubscriptionBillingCycleContractDraftConcatenatePayload, SubscriptionBillingCycleContractEditPayload, SubscriptionBillingCycleEditDeletePayload, SubscriptionBillingCycleEditsDeletePayload, SubscriptionBillingCycleInput, SubscriptionBillingCycleScheduleEditInput, SubscriptionBillingCycleScheduleEditPayload, SubscriptionBillingCyclesDateRangeSelector, SubscriptionBillingCycleSelector, SubscriptionBillingCyclesIndexRangeSelector, SubscriptionBillingCycleSkipPayload, SubscriptionBillingCyclesSortKeys, SubscriptionBillingCyclesTargetSelection, SubscriptionBillingCycleUnskipPayload, SubscriptionContract, SubscriptionContractActivatePayload, SubscriptionContractAtomicCreateInput, SubscriptionContractAtomicCreatePayload, SubscriptionContractCancelPayload, SubscriptionContractConnection, SubscriptionContractCreateInput, SubscriptionContractCreatePayload, SubscriptionContractExpirePayload, SubscriptionContractFailPayload, SubscriptionContractPausePayload, SubscriptionContractProductChangeInput, SubscriptionContractProductChangePayload, SubscriptionContractSetNextBillingDatePayload, SubscriptionContractsSortKeys, SubscriptionContractUpdatePayload, SubscriptionDraft, SubscriptionDraftCommitPayload, SubscriptionDraftDiscountAddPayload, SubscriptionDraftDiscountCodeApplyPayload, SubscriptionDraftDiscountRemovePayload, SubscriptionDraftDiscountUpdatePayload, SubscriptionDraftFreeShippingDiscountAddPayload, SubscriptionDraftFreeShippingDiscountUpdatePayload, SubscriptionDraftInput, SubscriptionDraftLineAddPayload, SubscriptionDraftLineRemovePayload, SubscriptionDraftLineUpdatePayload, SubscriptionDraftUpdatePayload, SubscriptionFreeShippingDiscountInput, SubscriptionLineInput, SubscriptionLineUpdateInput, SubscriptionManualDiscountInput } from './types';

// ============================================================
// Customers
// 133 operations: 37 queries, 96 mutations
// ============================================================

// These are passed as plain objects. See Shopify docs for field shapes:

// ─── Queries ─────────────────────────────────────────────────────────

/**
 * A paginated list of companies in the shop. Company objects are business entities that purchase from the merchant.
 */
export interface CompaniesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: CompanySortKeys;
}

export async function companies(args?: CompaniesArgs): Promise<CompanyConnection> {
  const gql = `#graphql
    query companies($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CompanySortKeys) {
      companies(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companies: CompanyConnection }>(gql, args);
  return data.companies;
}

/**
 * The number of companies for a shop. Limited to a maximum of 10000 by default.
 * @scope read_customers
 */
export interface CompaniesCountArgs {
  limit?: number;
}

export async function companiesCount(args?: CompaniesCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query companiesCount($limit: Int) {
      companiesCount(limit: $limit) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companiesCount: Count | null }>(gql, args);
  return data.companiesCount;
}

/**
 * Returns a Company resource by ID.
 */
export interface CompanyArgs {
  id: string;
}

export async function company(args: CompanyArgs): Promise<Company | null> {
  const gql = `#graphql
    query company($id: ID!) {
      company(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ company: Company | null }>(gql, args);
  return data.company;
}

/**
 * Returns a CompanyContact resource by ID.
 */
export interface CompanyContactArgs {
  id: string;
}

export async function companyContact(args: CompanyContactArgs): Promise<CompanyContact | null> {
  const gql = `#graphql
    query companyContact($id: ID!) {
      companyContact(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContact: CompanyContact | null }>(gql, args);
  return data.companyContact;
}

/**
 * Returns a CompanyContactRole resource by ID.
 */
export interface CompanyContactRoleArgs {
  id: string;
}

export async function companyContactRole(args: CompanyContactRoleArgs): Promise<CompanyContactRole | null> {
  const gql = `#graphql
    query companyContactRole($id: ID!) {
      companyContactRole(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContactRole: CompanyContactRole | null }>(gql, args);
  return data.companyContactRole;
}

/**
 * Returns a CompanyLocation resource by ID.
 */
export interface CompanyLocationArgs {
  id: string;
}

export async function companyLocation(args: CompanyLocationArgs): Promise<CompanyLocation | null> {
  const gql = `#graphql
    query companyLocation($id: ID!) {
      companyLocation(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocation: CompanyLocation | null }>(gql, args);
  return data.companyLocation;
}

/**
 * A paginated list of CompanyLocation objects for B2B customers. Company locations represent individual branches or offices of a Company where B2B orders can be placed.
 */
export interface CompanyLocationsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: CompanyLocationSortKeys;
}

export async function companyLocations(args?: CompanyLocationsArgs): Promise<CompanyLocationConnection> {
  const gql = `#graphql
    query companyLocations($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CompanyLocationSortKeys) {
      companyLocations(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocations: CompanyLocationConnection }>(gql, args);
  return data.companyLocations;
}

/**
 * Returns a Customer resource by ID.
 */
export interface CustomerArgs {
  id: string;
}

export async function customer(args: CustomerArgs): Promise<Customer | null> {
  const gql = `#graphql
    query customer($id: ID!) {
      customer(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customer: Customer | null }>(gql, args);
  return data.customer;
}

/**
 * Returns a CustomerAccountPage resource by ID.
 */
export interface CustomerAccountPageArgs {
  id: string;
}

export async function customerAccountPage(args: CustomerAccountPageArgs): Promise<CustomerAccountPage | null> {
  const gql = `#graphql
    query customerAccountPage($id: ID!) {
      customerAccountPage(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerAccountPage: CustomerAccountPage | null }>(gql, args);
  return data.customerAccountPage;
}

/**
 * List of the shop's customer account pages.
 */
export interface CustomerAccountPagesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function customerAccountPages(args?: CustomerAccountPagesArgs): Promise<CustomerAccountPageConnection> {
  const gql = `#graphql
    query customerAccountPages($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      customerAccountPages(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerAccountPages: CustomerAccountPageConnection }>(gql, args);
  return data.customerAccountPages;
}

/**
 * Return a customer by an identifier.
 * @scope read_customers
 */
export interface CustomerByIdentifierArgs {
  identifier: CustomerIdentifierInput;
}

export async function customerByIdentifier(args: CustomerByIdentifierArgs): Promise<Customer | null> {
  const gql = `#graphql
    query customerByIdentifier($identifier: CustomerIdentifierInput!) {
      customerByIdentifier(identifier: $identifier) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerByIdentifier: Customer | null }>(gql, args);
  return data.customerByIdentifier;
}

/**
 * Returns the status of a customer merge request job.
 * @scope read_customer_merge
 */
export interface CustomerMergeJobStatusArgs {
  jobId: string;
}

export async function customerMergeJobStatus(args: CustomerMergeJobStatusArgs): Promise<CustomerMergeRequest | null> {
  const gql = `#graphql
    query customerMergeJobStatus($jobId: ID!) {
      customerMergeJobStatus(jobId: $jobId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerMergeJobStatus: CustomerMergeRequest | null }>(gql, args);
  return data.customerMergeJobStatus;
}

/**
 * Returns a preview of a customer merge request.
 * @scope read_customer_merge
 */
export interface CustomerMergePreviewArgs {
  customerOneId: string;
  customerTwoId: string;
  overrideFields?: CustomerMergeOverrideFields;
}

export async function customerMergePreview(args: CustomerMergePreviewArgs): Promise<CustomerMergePreview | null> {
  const gql = `#graphql
    query customerMergePreview($customerOneId: ID!, $customerTwoId: ID!, $overrideFields: CustomerMergeOverrideFields) {
      customerMergePreview(customerOneId: $customerOneId, customerTwoId: $customerTwoId, overrideFields: $overrideFields) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerMergePreview: CustomerMergePreview | null }>(gql, args);
  return data.customerMergePreview;
}

/**
 * Returns a vaulted customer payment method by its ID, including the instrument type (credit card, PayPal, etc.), billing address, and current status. Optionally includes revoked payment methods. Use this to look up a specific saved payment method for a customer â€” for example, to check whether a subscription's payment method is still valid or to display stored payment details.
 */
export interface CustomerPaymentMethodArgs {
  id: string;
  showRevoked?: boolean;
}

export async function customerPaymentMethod(args: CustomerPaymentMethodArgs): Promise<CustomerPaymentMethod | null> {
  const gql = `#graphql
    query customerPaymentMethod($id: ID!, $showRevoked: Boolean) {
      customerPaymentMethod(id: $id, showRevoked: $showRevoked) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerPaymentMethod: CustomerPaymentMethod | null }>(gql, args);
  return data.customerPaymentMethod;
}

/**
 * List of the shop's customer saved searches.
 */
export interface CustomerSavedSearchesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: CustomerSavedSearchSortKeys;
}

export async function customerSavedSearches(args?: CustomerSavedSearchesArgs): Promise<SavedSearchConnection> {
  const gql = `#graphql
    query customerSavedSearches($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CustomerSavedSearchSortKeys) {
      customerSavedSearches(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerSavedSearches: SavedSearchConnection }>(gql, args);
  return data.customerSavedSearches;
}

/**
 * A paginated list of customers that belong to an individual Segment. Segments group customers based on criteria defined through ShopifyQL queries. Access segment members with their profile information and purchase summary data. The connection includes statistics for analyzing segment attributes (such as average and sum calculations) and a total count of all members.
 */
export interface CustomerSegmentMembersArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  queryId?: string;
  reverse?: boolean;
  segmentId?: string;
  sortKey?: string;
  timezone?: string;
}

export async function customerSegmentMembers(args?: CustomerSegmentMembersArgs): Promise<CustomerSegmentMemberConnection> {
  const gql = `#graphql
    query customerSegmentMembers($after: String, $before: String, $first: Int, $last: Int, $query: String, $queryId: ID, $reverse: Boolean, $segmentId: ID, $sortKey: String, $timezone: String) {
      customerSegmentMembers(after: $after, before: $before, first: $first, last: $last, query: $query, queryId: $queryId, reverse: $reverse, segmentId: $segmentId, sortKey: $sortKey, timezone: $timezone) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerSegmentMembers: CustomerSegmentMemberConnection }>(gql, args);
  return data.customerSegmentMembers;
}

/**
 * Returns a CustomerSegmentMembersQuery resource by ID.
 */
export interface CustomerSegmentMembersQueryArgs {
  id: string;
}

export async function customerSegmentMembersQuery(args: CustomerSegmentMembersQueryArgs): Promise<CustomerSegmentMembersQuery | null> {
  const gql = `#graphql
    query customerSegmentMembersQuery($id: ID!) {
      customerSegmentMembersQuery(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerSegmentMembersQuery: CustomerSegmentMembersQuery | null }>(gql, args);
  return data.customerSegmentMembersQuery;
}

/**
 * Whether a member, which is a customer, belongs to a segment.
 */
export interface CustomerSegmentMembershipArgs {
  customerId: string;
  segmentIds: unknown;
}

export async function customerSegmentMembership(args: CustomerSegmentMembershipArgs): Promise<SegmentMembershipResponse | null> {
  const gql = `#graphql
    query customerSegmentMembership($customerId: ID!, $segmentIds: String) {
      customerSegmentMembership(customerId: $customerId, segmentIds: $segmentIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerSegmentMembership: SegmentMembershipResponse | null }>(gql, args);
  return data.customerSegmentMembership;
}

/**
 * Returns a list of customers in your Shopify store, including key information such as name, email, location, and purchase history.
 */
export interface CustomersArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: CustomerSortKeys;
}

export async function customers(args?: CustomersArgs): Promise<CustomerConnection> {
  const gql = `#graphql
    query customers($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CustomerSortKeys) {
      customers(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customers: CustomerConnection }>(gql, args);
  return data.customers;
}

/**
 * The number of customers. Limited to a maximum of 10000 by default.
 * @scope read_customers
 */
export interface CustomersCountArgs {
  limit?: number;
  query?: string;
}

export async function customersCount(args?: CustomersCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query customersCount($limit: Int, $query: String) {
      customersCount(limit: $limit, query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customersCount: Count | null }>(gql, args);
  return data.customersCount;
}

/**
 * Retrieves a customer Segment by ID. Segments are dynamic groups of customers that meet specific criteria defined through ShopifyQL queries.
 */
export interface SegmentArgs {
  id: string;
}

export async function segment(args: SegmentArgs): Promise<Segment | null> {
  const gql = `#graphql
    query segment($id: ID!) {
      segment(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ segment: Segment | null }>(gql, args);
  return data.segment;
}

/**
 * A list of filter suggestions associated with a segment. A segment is a group of members (commonly customers) that meet specific criteria.
 */
export interface SegmentFilterSuggestionsArgs {
  after?: string;
  first: number;
  search: string;
}

export async function segmentFilterSuggestions(args: SegmentFilterSuggestionsArgs): Promise<SegmentFilterConnection> {
  const gql = `#graphql
    query segmentFilterSuggestions($after: String, $first: Int!, $search: String!) {
      segmentFilterSuggestions(after: $after, first: $first, search: $search) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ segmentFilterSuggestions: SegmentFilterConnection }>(gql, args);
  return data.segmentFilterSuggestions;
}

/**
 * A list of filters.
 */
export interface SegmentFiltersArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
}

export async function segmentFilters(args?: SegmentFiltersArgs): Promise<SegmentFilterConnection> {
  const gql = `#graphql
    query segmentFilters($after: String, $before: String, $first: Int, $last: Int) {
      segmentFilters(after: $after, before: $before, first: $first, last: $last) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ segmentFilters: SegmentFilterConnection }>(gql, args);
  return data.segmentFilters;
}

/**
 * A list of a shop's segment migrations.
 */
export interface SegmentMigrationsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  savedSearchId?: string;
}

export async function segmentMigrations(args?: SegmentMigrationsArgs): Promise<SegmentMigrationConnection> {
  const gql = `#graphql
    query segmentMigrations($after: String, $before: String, $first: Int, $last: Int, $savedSearchId: ID) {
      segmentMigrations(after: $after, before: $before, first: $first, last: $last, savedSearchId: $savedSearchId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ segmentMigrations: SegmentMigrationConnection }>(gql, args);
  return data.segmentMigrations;
}

/**
 * The list of suggested values corresponding to a particular filter for a segment. A segment is a group of members, such as customers, that meet specific criteria.
 */
export interface SegmentValueSuggestionsArgs {
  after?: string;
  before?: string;
  filterQueryName?: string;
  first?: number;
  functionParameterQueryName?: string;
  last?: number;
  search: string;
}

export async function segmentValueSuggestions(args: SegmentValueSuggestionsArgs): Promise<SegmentValueConnection> {
  const gql = `#graphql
    query segmentValueSuggestions($after: String, $before: String, $filterQueryName: String, $first: Int, $functionParameterQueryName: String, $last: Int, $search: String!) {
      segmentValueSuggestions(after: $after, before: $before, filterQueryName: $filterQueryName, first: $first, functionParameterQueryName: $functionParameterQueryName, last: $last, search: $search) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ segmentValueSuggestions: SegmentValueConnection }>(gql, args);
  return data.segmentValueSuggestions;
}

/**
 * Returns a paginated list of Segment objects for the shop. Segments are dynamic groups of customers that meet specific criteria defined through ShopifyQL queries. You can filter segments by search query and sort them by creation date or other criteria.
 */
export interface SegmentsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: SegmentSortKeys;
}

export async function segments(args?: SegmentsArgs): Promise<SegmentConnection> {
  const gql = `#graphql
    query segments($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: SegmentSortKeys) {
      segments(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ segments: SegmentConnection }>(gql, args);
  return data.segments;
}

/**
 * The number of segments for a shop. Limited to a maximum of 10000 by default.
 */
export interface SegmentsCountArgs {
  limit?: number;
}

export async function segmentsCount(args?: SegmentsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query segmentsCount($limit: Int) {
      segmentsCount(limit: $limit) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ segmentsCount: Count | null }>(gql, args);
  return data.segmentsCount;
}

/**
 * Retrieves a StoreCreditAccount by ID. Store credit accounts hold monetary balances that account owners can use at checkout. The owner is either a Customer or a CompanyLocation.
 */
export interface StoreCreditAccountArgs {
  id: string;
}

export async function storeCreditAccount(args: StoreCreditAccountArgs): Promise<StoreCreditAccount | null> {
  const gql = `#graphql
    query storeCreditAccount($id: ID!) {
      storeCreditAccount(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ storeCreditAccount: StoreCreditAccount | null }>(gql, args);
  return data.storeCreditAccount;
}

/**
 * Returns the store credit configuration for a shop, including whether store credit is enabled for customers at checkout. Use this to display the current state of a merchant's store credit program or check eligibility before issuing store credit to customers.
 */
export async function storeCreditConfiguration(): Promise<StoreCreditConfiguration | null> {
  const gql = `#graphql
    query storeCreditConfiguration {
      storeCreditConfiguration {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ storeCreditConfiguration: StoreCreditConfiguration | null }>(gql);
  return data.storeCreditConfiguration;
}

/**
 * Returns a SubscriptionBillingAttempt resource by ID.
 */
export interface SubscriptionBillingAttemptArgs {
  id: string;
}

export async function subscriptionBillingAttempt(args: SubscriptionBillingAttemptArgs): Promise<SubscriptionBillingAttempt | null> {
  const gql = `#graphql
    query subscriptionBillingAttempt($id: ID!) {
      subscriptionBillingAttempt(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingAttempt: SubscriptionBillingAttempt | null }>(gql, args);
  return data.subscriptionBillingAttempt;
}

/**
 * Returns subscription billing attempts on a store.
 */
export interface SubscriptionBillingAttemptsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: SubscriptionBillingAttemptsSortKeys;
}

export async function subscriptionBillingAttempts(args?: SubscriptionBillingAttemptsArgs): Promise<SubscriptionBillingAttemptConnection> {
  const gql = `#graphql
    query subscriptionBillingAttempts($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: SubscriptionBillingAttemptsSortKeys) {
      subscriptionBillingAttempts(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingAttempts: SubscriptionBillingAttemptConnection }>(gql, args);
  return data.subscriptionBillingAttempts;
}

/**
 * Returns a subscription billing cycle found either by cycle index or date.
 */
export interface SubscriptionBillingCycleArgs {
  billingCycleInput: SubscriptionBillingCycleInput;
}

export async function subscriptionBillingCycle(args: SubscriptionBillingCycleArgs): Promise<SubscriptionBillingCycle | null> {
  const gql = `#graphql
    query subscriptionBillingCycle($billingCycleInput: SubscriptionBillingCycleInput!) {
      subscriptionBillingCycle(billingCycleInput: $billingCycleInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycle: SubscriptionBillingCycle | null }>(gql, args);
  return data.subscriptionBillingCycle;
}

/**
 * Retrieves the results of the asynchronous job for the subscription billing cycle bulk action based on the specified job ID.
 */
export interface SubscriptionBillingCycleBulkResultsArgs {
  after?: string;
  before?: string;
  first?: number;
  jobId: string;
  last?: number;
  reverse?: boolean;
}

export async function subscriptionBillingCycleBulkResults(args: SubscriptionBillingCycleBulkResultsArgs): Promise<SubscriptionBillingCycleConnection> {
  const gql = `#graphql
    query subscriptionBillingCycleBulkResults($after: String, $before: String, $first: Int, $jobId: ID!, $last: Int, $reverse: Boolean) {
      subscriptionBillingCycleBulkResults(after: $after, before: $before, first: $first, jobId: $jobId, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleBulkResults: SubscriptionBillingCycleConnection }>(gql, args);
  return data.subscriptionBillingCycleBulkResults;
}

/**
 * Returns subscription billing cycles for a contract ID.
 */
export interface SubscriptionBillingCyclesArgs {
  after?: string;
  before?: string;
  billingCyclesDateRangeSelector?: SubscriptionBillingCyclesDateRangeSelector;
  billingCyclesIndexRangeSelector?: SubscriptionBillingCyclesIndexRangeSelector;
  contractId: string;
  first?: number;
  last?: number;
  reverse?: boolean;
  sortKey?: SubscriptionBillingCyclesSortKeys;
}

export async function subscriptionBillingCycles(args: SubscriptionBillingCyclesArgs): Promise<SubscriptionBillingCycleConnection> {
  const gql = `#graphql
    query subscriptionBillingCycles($after: String, $before: String, $billingCyclesDateRangeSelector: SubscriptionBillingCyclesDateRangeSelector, $billingCyclesIndexRangeSelector: SubscriptionBillingCyclesIndexRangeSelector, $contractId: ID!, $first: Int, $last: Int, $reverse: Boolean, $sortKey: SubscriptionBillingCyclesSortKeys) {
      subscriptionBillingCycles(after: $after, before: $before, billingCyclesDateRangeSelector: $billingCyclesDateRangeSelector, billingCyclesIndexRangeSelector: $billingCyclesIndexRangeSelector, contractId: $contractId, first: $first, last: $last, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycles: SubscriptionBillingCycleConnection }>(gql, args);
  return data.subscriptionBillingCycles;
}

/**
 * Retrieves a SubscriptionContract by ID.
 */
export interface SubscriptionContractArgs {
  id: string;
}

export async function subscriptionContract(args: SubscriptionContractArgs): Promise<SubscriptionContract | null> {
  const gql = `#graphql
    query subscriptionContract($id: ID!) {
      subscriptionContract(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContract: SubscriptionContract | null }>(gql, args);
  return data.subscriptionContract;
}

/**
 * Returns a SubscriptionContractConnection containing subscription contracts. Subscription contracts are agreements between customers and merchants for recurring purchases with defined billing and delivery schedules.
 */
export interface SubscriptionContractsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: SubscriptionContractsSortKeys;
}

export async function subscriptionContracts(args?: SubscriptionContractsArgs): Promise<SubscriptionContractConnection> {
  const gql = `#graphql
    query subscriptionContracts($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: SubscriptionContractsSortKeys) {
      subscriptionContracts(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContracts: SubscriptionContractConnection }>(gql, args);
  return data.subscriptionContracts;
}

/**
 * Returns a Subscription Draft resource by ID.
 */
export interface SubscriptionDraftArgs {
  id: string;
}

export async function subscriptionDraft(args: SubscriptionDraftArgs): Promise<SubscriptionDraft | null> {
  const gql = `#graphql
    query subscriptionDraft($id: ID!) {
      subscriptionDraft(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraft: SubscriptionDraft | null }>(gql, args);
  return data.subscriptionDraft;
}

// ─── Mutations ─────────────────────────────────────────────────────────

/**
 * Deletes a list of companies.
 * @scope write_customers
 */
export interface CompaniesDeleteArgs {
  companyIds: unknown;
}

export async function companiesDelete(args: CompaniesDeleteArgs): Promise<CompaniesDeletePayload> {
  const gql = `#graphql
    mutation companiesDelete($companyIds: String) {
      companiesDelete(companyIds: $companyIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companiesDelete: CompaniesDeletePayload }>(gql, args);
  return data.companiesDelete;
}

/**
 * Deletes a company address.
 * @scope write_customers
 */
export interface CompanyAddressDeleteArgs {
  addressId: string;
}

export async function companyAddressDelete(args: CompanyAddressDeleteArgs): Promise<CompanyAddressDeletePayload> {
  const gql = `#graphql
    mutation companyAddressDelete($addressId: ID!) {
      companyAddressDelete(addressId: $addressId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyAddressDelete: CompanyAddressDeletePayload }>(gql, args);
  return data.companyAddressDelete;
}

/**
 * Adds an existing Customer as a contact to a Company.  Companies are business entities that make purchases from the merchant's store. Use this mutation when you have a customer who needs to be associated with a B2B company to make purchases on behalf of that company.
 * @scope write_customers
 */
export interface CompanyAssignCustomerAsContactArgs {
  companyId: string;
  customerId: string;
}

export async function companyAssignCustomerAsContact(args: CompanyAssignCustomerAsContactArgs): Promise<CompanyAssignCustomerAsContactPayload> {
  const gql = `#graphql
    mutation companyAssignCustomerAsContact($companyId: ID!, $customerId: ID!) {
      companyAssignCustomerAsContact(companyId: $companyId, customerId: $customerId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyAssignCustomerAsContact: CompanyAssignCustomerAsContactPayload }>(gql, args);
  return data.companyAssignCustomerAsContact;
}

/**
 * Assigns the main contact for the company.
 * @scope write_customers
 */
export interface CompanyAssignMainContactArgs {
  companyContactId: string;
  companyId: string;
}

export async function companyAssignMainContact(args: CompanyAssignMainContactArgs): Promise<CompanyAssignMainContactPayload> {
  const gql = `#graphql
    mutation companyAssignMainContact($companyContactId: ID!, $companyId: ID!) {
      companyAssignMainContact(companyContactId: $companyContactId, companyId: $companyId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyAssignMainContact: CompanyAssignMainContactPayload }>(gql, args);
  return data.companyAssignMainContact;
}

/**
 * Assigns a role to a contact for a location.
 * @scope write_customers
 */
export interface CompanyContactAssignRoleArgs {
  companyContactId: string;
  companyContactRoleId: string;
  companyLocationId: string;
}

export async function companyContactAssignRole(args: CompanyContactAssignRoleArgs): Promise<CompanyContactAssignRolePayload> {
  const gql = `#graphql
    mutation companyContactAssignRole($companyContactId: ID!, $companyContactRoleId: ID!, $companyLocationId: ID!) {
      companyContactAssignRole(companyContactId: $companyContactId, companyContactRoleId: $companyContactRoleId, companyLocationId: $companyLocationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContactAssignRole: CompanyContactAssignRolePayload }>(gql, args);
  return data.companyContactAssignRole;
}

/**
 * Assigns roles on a company contact.
 * @scope write_customers
 */
export interface CompanyContactAssignRolesArgs {
  companyContactId: string;
  rolesToAssign: unknown;
}

export async function companyContactAssignRoles(args: CompanyContactAssignRolesArgs): Promise<CompanyContactAssignRolesPayload> {
  const gql = `#graphql
    mutation companyContactAssignRoles($companyContactId: ID!, $rolesToAssign: String) {
      companyContactAssignRoles(companyContactId: $companyContactId, rolesToAssign: $rolesToAssign) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContactAssignRoles: CompanyContactAssignRolesPayload }>(gql, args);
  return data.companyContactAssignRoles;
}

/**
 * Creates a company contact and the associated customer.
 * @scope write_customers
 */
export interface CompanyContactCreateArgs {
  companyId: string;
  input: CompanyContactInput;
}

export async function companyContactCreate(args: CompanyContactCreateArgs): Promise<CompanyContactCreatePayload> {
  const gql = `#graphql
    mutation companyContactCreate($companyId: ID!, $input: CompanyContactInput!) {
      companyContactCreate(companyId: $companyId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContactCreate: CompanyContactCreatePayload }>(gql, args);
  return data.companyContactCreate;
}

/**
 * Deletes a company contact.
 * @scope write_customers
 */
export interface CompanyContactDeleteArgs {
  companyContactId: string;
}

export async function companyContactDelete(args: CompanyContactDeleteArgs): Promise<CompanyContactDeletePayload> {
  const gql = `#graphql
    mutation companyContactDelete($companyContactId: ID!) {
      companyContactDelete(companyContactId: $companyContactId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContactDelete: CompanyContactDeletePayload }>(gql, args);
  return data.companyContactDelete;
}

/**
 * Removes a company contact from a Company.
 * @scope write_customers
 */
export interface CompanyContactRemoveFromCompanyArgs {
  companyContactId: string;
}

export async function companyContactRemoveFromCompany(args: CompanyContactRemoveFromCompanyArgs): Promise<CompanyContactRemoveFromCompanyPayload> {
  const gql = `#graphql
    mutation companyContactRemoveFromCompany($companyContactId: ID!) {
      companyContactRemoveFromCompany(companyContactId: $companyContactId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContactRemoveFromCompany: CompanyContactRemoveFromCompanyPayload }>(gql, args);
  return data.companyContactRemoveFromCompany;
}

/**
 * Revokes a role on a company contact.
 * @scope write_customers
 */
export interface CompanyContactRevokeRoleArgs {
  companyContactId: string;
  companyContactRoleAssignmentId: string;
}

export async function companyContactRevokeRole(args: CompanyContactRevokeRoleArgs): Promise<CompanyContactRevokeRolePayload> {
  const gql = `#graphql
    mutation companyContactRevokeRole($companyContactId: ID!, $companyContactRoleAssignmentId: ID!) {
      companyContactRevokeRole(companyContactId: $companyContactId, companyContactRoleAssignmentId: $companyContactRoleAssignmentId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContactRevokeRole: CompanyContactRevokeRolePayload }>(gql, args);
  return data.companyContactRevokeRole;
}

/**
 * Revokes roles on a company contact.
 * @scope write_customers
 */
export interface CompanyContactRevokeRolesArgs {
  companyContactId: string;
  revokeAll?: boolean;
  roleAssignmentIds?: unknown;
}

export async function companyContactRevokeRoles(args: CompanyContactRevokeRolesArgs): Promise<CompanyContactRevokeRolesPayload> {
  const gql = `#graphql
    mutation companyContactRevokeRoles($companyContactId: ID!, $revokeAll: Boolean, $roleAssignmentIds: String) {
      companyContactRevokeRoles(companyContactId: $companyContactId, revokeAll: $revokeAll, roleAssignmentIds: $roleAssignmentIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContactRevokeRoles: CompanyContactRevokeRolesPayload }>(gql, args);
  return data.companyContactRevokeRoles;
}

/**
 * Updates a company contact.
 * @scope write_customers
 */
export interface CompanyContactUpdateArgs {
  companyContactId: string;
  input: CompanyContactInput;
}

export async function companyContactUpdate(args: CompanyContactUpdateArgs): Promise<CompanyContactUpdatePayload> {
  const gql = `#graphql
    mutation companyContactUpdate($companyContactId: ID!, $input: CompanyContactInput!) {
      companyContactUpdate(companyContactId: $companyContactId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContactUpdate: CompanyContactUpdatePayload }>(gql, args);
  return data.companyContactUpdate;
}

/**
 * Deletes one or more company contacts.
 * @scope write_customers
 */
export interface CompanyContactsDeleteArgs {
  companyContactIds: unknown;
}

export async function companyContactsDelete(args: CompanyContactsDeleteArgs): Promise<CompanyContactsDeletePayload> {
  const gql = `#graphql
    mutation companyContactsDelete($companyContactIds: String) {
      companyContactsDelete(companyContactIds: $companyContactIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyContactsDelete: CompanyContactsDeletePayload }>(gql, args);
  return data.companyContactsDelete;
}

/**
 * Creates a Company for B2B commerce. This mutation creates the company and can optionally create an initial CompanyContact and CompanyLocation in a single operation. Company contacts are people who place orders on behalf of the company. Company locations are branches or offices with their own billing and shipping addresses.
 * @scope write_customers
 */
export interface CompanyCreateArgs {
  input: CompanyCreateInput;
}

export async function companyCreate(args: CompanyCreateArgs): Promise<CompanyCreatePayload> {
  const gql = `#graphql
    mutation companyCreate($input: CompanyCreateInput!) {
      companyCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyCreate: CompanyCreatePayload }>(gql, args);
  return data.companyCreate;
}

/**
 * Deletes a company.
 * @scope write_customers
 */
export interface CompanyDeleteArgs {
  id: string;
}

export async function companyDelete(args: CompanyDeleteArgs): Promise<CompanyDeletePayload> {
  const gql = `#graphql
    mutation companyDelete($id: ID!) {
      companyDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyDelete: CompanyDeletePayload }>(gql, args);
  return data.companyDelete;
}

/**
 * Updates an address on a company location.
 * @scope write_customers
 */
export interface CompanyLocationAssignAddressArgs {
  address: CompanyAddressInput;
  addressTypes: unknown;
  locationId: string;
}

export async function companyLocationAssignAddress(args: CompanyLocationAssignAddressArgs): Promise<CompanyLocationAssignAddressPayload> {
  const gql = `#graphql
    mutation companyLocationAssignAddress($address: CompanyAddressInput!, $addressTypes: String, $locationId: ID!) {
      companyLocationAssignAddress(address: $address, addressTypes: $addressTypes, locationId: $locationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationAssignAddress: CompanyLocationAssignAddressPayload }>(gql, args);
  return data.companyLocationAssignAddress;
}

/**
 * Assigns roles on a company location.
 * @scope write_customers
 */
export interface CompanyLocationAssignRolesArgs {
  companyLocationId: string;
  rolesToAssign: unknown;
}

export async function companyLocationAssignRoles(args: CompanyLocationAssignRolesArgs): Promise<CompanyLocationAssignRolesPayload> {
  const gql = `#graphql
    mutation companyLocationAssignRoles($companyLocationId: ID!, $rolesToAssign: String) {
      companyLocationAssignRoles(companyLocationId: $companyLocationId, rolesToAssign: $rolesToAssign) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationAssignRoles: CompanyLocationAssignRolesPayload }>(gql, args);
  return data.companyLocationAssignRoles;
}

/**
 * Creates one or more mappings between a staff member at a shop and a company location.
 * @scope write_customers
 */
export interface CompanyLocationAssignStaffMembersArgs {
  companyLocationId: string;
  staffMemberIds: unknown;
}

export async function companyLocationAssignStaffMembers(args: CompanyLocationAssignStaffMembersArgs): Promise<CompanyLocationAssignStaffMembersPayload> {
  const gql = `#graphql
    mutation companyLocationAssignStaffMembers($companyLocationId: ID!, $staffMemberIds: String) {
      companyLocationAssignStaffMembers(companyLocationId: $companyLocationId, staffMemberIds: $staffMemberIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationAssignStaffMembers: CompanyLocationAssignStaffMembersPayload }>(gql, args);
  return data.companyLocationAssignStaffMembers;
}

/**
 * Assigns tax exemptions to the company location.
 * @scope write_customers
 */
export interface CompanyLocationAssignTaxExemptionsArgs {
  companyLocationId: string;
  taxExemptions: unknown;
}

export async function companyLocationAssignTaxExemptions(args: CompanyLocationAssignTaxExemptionsArgs): Promise<CompanyLocationAssignTaxExemptionsPayload> {
  const gql = `#graphql
    mutation companyLocationAssignTaxExemptions($companyLocationId: ID!, $taxExemptions: String) {
      companyLocationAssignTaxExemptions(companyLocationId: $companyLocationId, taxExemptions: $taxExemptions) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationAssignTaxExemptions: CompanyLocationAssignTaxExemptionsPayload }>(gql, args);
  return data.companyLocationAssignTaxExemptions;
}

/**
 * Creates a new location for a Company. Company locations are branches or offices where B2B customers can place orders with specific pricing, catalogs, and payment terms.
 * @scope write_customers
 */
export interface CompanyLocationCreateArgs {
  companyId: string;
  input: CompanyLocationInput;
}

export async function companyLocationCreate(args: CompanyLocationCreateArgs): Promise<CompanyLocationCreatePayload> {
  const gql = `#graphql
    mutation companyLocationCreate($companyId: ID!, $input: CompanyLocationInput!) {
      companyLocationCreate(companyId: $companyId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationCreate: CompanyLocationCreatePayload }>(gql, args);
  return data.companyLocationCreate;
}

/**
 * Creates a tax registration for a company location.
 * @scope write_customers
 */
export interface CompanyLocationCreateTaxRegistrationArgs {
  locationId: string;
  taxId: string;
}

export async function companyLocationCreateTaxRegistration(args: CompanyLocationCreateTaxRegistrationArgs): Promise<CompanyLocationCreateTaxRegistrationPayload> {
  const gql = `#graphql
    mutation companyLocationCreateTaxRegistration($locationId: ID!, $taxId: String!) {
      companyLocationCreateTaxRegistration(locationId: $locationId, taxId: $taxId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationCreateTaxRegistration: CompanyLocationCreateTaxRegistrationPayload }>(gql, args);
  return data.companyLocationCreateTaxRegistration;
}

/**
 * Deletes a company location.
 * @scope write_customers
 */
export interface CompanyLocationDeleteArgs {
  companyLocationId: string;
}

export async function companyLocationDelete(args: CompanyLocationDeleteArgs): Promise<CompanyLocationDeletePayload> {
  const gql = `#graphql
    mutation companyLocationDelete($companyLocationId: ID!) {
      companyLocationDelete(companyLocationId: $companyLocationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationDelete: CompanyLocationDeletePayload }>(gql, args);
  return data.companyLocationDelete;
}

/**
 * Deletes one or more existing mappings between a staff member at a shop and a company location.
 * @scope write_customers
 */
export interface CompanyLocationRemoveStaffMembersArgs {
  companyLocationStaffMemberAssignmentIds: unknown;
}

export async function companyLocationRemoveStaffMembers(args: CompanyLocationRemoveStaffMembersArgs): Promise<CompanyLocationRemoveStaffMembersPayload> {
  const gql = `#graphql
    mutation companyLocationRemoveStaffMembers($companyLocationStaffMemberAssignmentIds: String) {
      companyLocationRemoveStaffMembers(companyLocationStaffMemberAssignmentIds: $companyLocationStaffMemberAssignmentIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationRemoveStaffMembers: CompanyLocationRemoveStaffMembersPayload }>(gql, args);
  return data.companyLocationRemoveStaffMembers;
}

/**
 * Revokes roles on a company location.
 * @scope write_customers
 */
export interface CompanyLocationRevokeRolesArgs {
  companyLocationId: string;
  rolesToRevoke: unknown;
}

export async function companyLocationRevokeRoles(args: CompanyLocationRevokeRolesArgs): Promise<CompanyLocationRevokeRolesPayload> {
  const gql = `#graphql
    mutation companyLocationRevokeRoles($companyLocationId: ID!, $rolesToRevoke: String) {
      companyLocationRevokeRoles(companyLocationId: $companyLocationId, rolesToRevoke: $rolesToRevoke) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationRevokeRoles: CompanyLocationRevokeRolesPayload }>(gql, args);
  return data.companyLocationRevokeRoles;
}

/**
 * Revokes tax exemptions from the company location.
 * @scope write_customers
 */
export interface CompanyLocationRevokeTaxExemptionsArgs {
  companyLocationId: string;
  taxExemptions: unknown;
}

export async function companyLocationRevokeTaxExemptions(args: CompanyLocationRevokeTaxExemptionsArgs): Promise<CompanyLocationRevokeTaxExemptionsPayload> {
  const gql = `#graphql
    mutation companyLocationRevokeTaxExemptions($companyLocationId: ID!, $taxExemptions: String) {
      companyLocationRevokeTaxExemptions(companyLocationId: $companyLocationId, taxExemptions: $taxExemptions) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationRevokeTaxExemptions: CompanyLocationRevokeTaxExemptionsPayload }>(gql, args);
  return data.companyLocationRevokeTaxExemptions;
}

/**
 * Revokes tax registration on a company location.
 * @scope write_customers
 */
export interface CompanyLocationRevokeTaxRegistrationArgs {
  companyLocationId: string;
}

export async function companyLocationRevokeTaxRegistration(args: CompanyLocationRevokeTaxRegistrationArgs): Promise<CompanyLocationRevokeTaxRegistrationPayload> {
  const gql = `#graphql
    mutation companyLocationRevokeTaxRegistration($companyLocationId: ID!) {
      companyLocationRevokeTaxRegistration(companyLocationId: $companyLocationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationRevokeTaxRegistration: CompanyLocationRevokeTaxRegistrationPayload }>(gql, args);
  return data.companyLocationRevokeTaxRegistration;
}

/**
 * Sets the tax settings for a company location.
 * @scope write_customers
 */
export interface CompanyLocationTaxSettingsUpdateArgs {
  companyLocationId: string;
  exemptionsToAssign?: unknown;
  exemptionsToRemove?: unknown;
  taxExempt?: boolean;
  taxRegistrationId?: string;
}

export async function companyLocationTaxSettingsUpdate(args: CompanyLocationTaxSettingsUpdateArgs): Promise<CompanyLocationTaxSettingsUpdatePayload> {
  const gql = `#graphql
    mutation companyLocationTaxSettingsUpdate($companyLocationId: ID!, $exemptionsToAssign: String, $exemptionsToRemove: String, $taxExempt: Boolean, $taxRegistrationId: String) {
      companyLocationTaxSettingsUpdate(companyLocationId: $companyLocationId, exemptionsToAssign: $exemptionsToAssign, exemptionsToRemove: $exemptionsToRemove, taxExempt: $taxExempt, taxRegistrationId: $taxRegistrationId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationTaxSettingsUpdate: CompanyLocationTaxSettingsUpdatePayload }>(gql, args);
  return data.companyLocationTaxSettingsUpdate;
}

/**
 * Updates a company location's information and B2B checkout settings. Company locations are branches or offices where CompanyContact members place orders on behalf of the company. Contacts must be assigned to a location through roleAssignments to place orders.
 * @scope write_customers
 */
export interface CompanyLocationUpdateArgs {
  companyLocationId: string;
  input: CompanyLocationUpdateInput;
}

export async function companyLocationUpdate(args: CompanyLocationUpdateArgs): Promise<CompanyLocationUpdatePayload> {
  const gql = `#graphql
    mutation companyLocationUpdate($companyLocationId: ID!, $input: CompanyLocationUpdateInput!) {
      companyLocationUpdate(companyLocationId: $companyLocationId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationUpdate: CompanyLocationUpdatePayload }>(gql, args);
  return data.companyLocationUpdate;
}

/**
 * Deletes a list of company locations.
 * @scope write_customers
 */
export interface CompanyLocationsDeleteArgs {
  companyLocationIds: unknown;
}

export async function companyLocationsDelete(args: CompanyLocationsDeleteArgs): Promise<CompanyLocationsDeletePayload> {
  const gql = `#graphql
    mutation companyLocationsDelete($companyLocationIds: String) {
      companyLocationsDelete(companyLocationIds: $companyLocationIds) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyLocationsDelete: CompanyLocationsDeletePayload }>(gql, args);
  return data.companyLocationsDelete;
}

/**
 * Revokes the main contact from the company.
 * @scope write_customers
 */
export interface CompanyRevokeMainContactArgs {
  companyId: string;
}

export async function companyRevokeMainContact(args: CompanyRevokeMainContactArgs): Promise<CompanyRevokeMainContactPayload> {
  const gql = `#graphql
    mutation companyRevokeMainContact($companyId: ID!) {
      companyRevokeMainContact(companyId: $companyId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyRevokeMainContact: CompanyRevokeMainContactPayload }>(gql, args);
  return data.companyRevokeMainContact;
}

/**
 * Updates a Company with new information. Companies represent business customers that can have multiple contacts and locations with specific pricing, payment terms, and checkout settings.
 * @scope write_customers
 */
export interface CompanyUpdateArgs {
  companyId: string;
  input: CompanyInput;
}

export async function companyUpdate(args: CompanyUpdateArgs): Promise<CompanyUpdatePayload> {
  const gql = `#graphql
    mutation companyUpdate($companyId: ID!, $input: CompanyInput!) {
      companyUpdate(companyId: $companyId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ companyUpdate: CompanyUpdatePayload }>(gql, args);
  return data.companyUpdate;
}

/**
 * Add tax exemptions for the customer.
 * @scope write_customers
 */
export interface CustomerAddTaxExemptionsArgs {
  customerId: string;
  taxExemptions: unknown;
}

export async function customerAddTaxExemptions(args: CustomerAddTaxExemptionsArgs): Promise<CustomerAddTaxExemptionsPayload> {
  const gql = `#graphql
    mutation customerAddTaxExemptions($customerId: ID!, $taxExemptions: String) {
      customerAddTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerAddTaxExemptions: CustomerAddTaxExemptionsPayload }>(gql, args);
  return data.customerAddTaxExemptions;
}

/**
 * Creates a new MailingAddress for a Customer. You can optionally set the address as the customer's default address.
 * @scope write_customers
 */
export interface CustomerAddressCreateArgs {
  address: MailingAddressInput;
  customerId: string;
  setAsDefault?: boolean;
}

export async function customerAddressCreate(args: CustomerAddressCreateArgs): Promise<CustomerAddressCreatePayload> {
  const gql = `#graphql
    mutation customerAddressCreate($address: MailingAddressInput!, $customerId: ID!, $setAsDefault: Boolean) {
      customerAddressCreate(address: $address, customerId: $customerId, setAsDefault: $setAsDefault) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerAddressCreate: CustomerAddressCreatePayload }>(gql, args);
  return data.customerAddressCreate;
}

/**
 * Deletes a customer's address.
 * @scope write_customers
 */
export interface CustomerAddressDeleteArgs {
  addressId: string;
  customerId: string;
}

export async function customerAddressDelete(args: CustomerAddressDeleteArgs): Promise<CustomerAddressDeletePayload> {
  const gql = `#graphql
    mutation customerAddressDelete($addressId: ID!, $customerId: ID!) {
      customerAddressDelete(addressId: $addressId, customerId: $customerId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerAddressDelete: CustomerAddressDeletePayload }>(gql, args);
  return data.customerAddressDelete;
}

/**
 * Updates a Customer's MailingAddress. You can modify any field of the address and optionally set it as the customer's default address.
 * @scope write_customers
 */
export interface CustomerAddressUpdateArgs {
  address: MailingAddressInput;
  addressId: string;
  customerId: string;
  setAsDefault?: boolean;
}

export async function customerAddressUpdate(args: CustomerAddressUpdateArgs): Promise<CustomerAddressUpdatePayload> {
  const gql = `#graphql
    mutation customerAddressUpdate($address: MailingAddressInput!, $addressId: ID!, $customerId: ID!, $setAsDefault: Boolean) {
      customerAddressUpdate(address: $address, addressId: $addressId, customerId: $customerId, setAsDefault: $setAsDefault) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerAddressUpdate: CustomerAddressUpdatePayload }>(gql, args);
  return data.customerAddressUpdate;
}

/**
 * Cancels a pending erasure of a customer's data. Read more here.
 * @scope write_customer_data_erasure
 */
export interface CustomerCancelDataErasureArgs {
  customerId: string;
}

export async function customerCancelDataErasure(args: CustomerCancelDataErasureArgs): Promise<CustomerCancelDataErasurePayload> {
  const gql = `#graphql
    mutation customerCancelDataErasure($customerId: ID!) {
      customerCancelDataErasure(customerId: $customerId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerCancelDataErasure: CustomerCancelDataErasurePayload }>(gql, args);
  return data.customerCancelDataErasure;
}

/**
 * Creates a new Customer in the store.
 * @scope write_customers
 */
export interface CustomerCreateArgs {
  input: CustomerInput;
}

export async function customerCreate(args: CustomerCreateArgs): Promise<CustomerCreatePayload> {
  const gql = `#graphql
    mutation customerCreate($input: CustomerInput!) {
      customerCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerCreate: CustomerCreatePayload }>(gql, args);
  return data.customerCreate;
}

/**
 * Deletes a Customer from the store. You can only delete customers who haven't placed any orders.
 * @scope write_customers
 */
export interface CustomerDeleteArgs {
  input: CustomerDeleteInput;
}

export async function customerDelete(args: CustomerDeleteArgs): Promise<CustomerDeletePayload> {
  const gql = `#graphql
    mutation customerDelete($input: CustomerDeleteInput!) {
      customerDelete(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerDelete: CustomerDeletePayload }>(gql, args);
  return data.customerDelete;
}

/**
 * Updates a Customer's email marketing consent information. The customer must have an email address to update their consent. Records the marketing state (such as subscribed, pending, unsubscribed), opt-in level, and when and where the customer gave or withdrew consent.
 * @scope write_customers
 */
export interface CustomerEmailMarketingConsentUpdateArgs {
  input: CustomerEmailMarketingConsentUpdateInput;
}

export async function customerEmailMarketingConsentUpdate(args: CustomerEmailMarketingConsentUpdateArgs): Promise<CustomerEmailMarketingConsentUpdatePayload> {
  const gql = `#graphql
    mutation customerEmailMarketingConsentUpdate($input: CustomerEmailMarketingConsentUpdateInput!) {
      customerEmailMarketingConsentUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerEmailMarketingConsentUpdate: CustomerEmailMarketingConsentUpdatePayload }>(gql, args);
  return data.customerEmailMarketingConsentUpdate;
}

/**
 * Generates a one-time activation URL for a Customer whose legacy customer account isn't yet enabled. Use this after importing customers or creating accounts that need activation.
 * @scope write_customers
 */
export interface CustomerGenerateAccountActivationUrlArgs {
  customerId: string;
}

export async function customerGenerateAccountActivationUrl(args: CustomerGenerateAccountActivationUrlArgs): Promise<CustomerGenerateAccountActivationUrlPayload> {
  const gql = `#graphql
    mutation customerGenerateAccountActivationUrl($customerId: ID!) {
      customerGenerateAccountActivationUrl(customerId: $customerId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerGenerateAccountActivationUrl: CustomerGenerateAccountActivationUrlPayload }>(gql, args);
  return data.customerGenerateAccountActivationUrl;
}

/**
 * Merges two customers.
 * @scope write_customer_merge
 */
export interface CustomerMergeArgs {
  customerOneId: string;
  customerTwoId: string;
  overrideFields?: CustomerMergeOverrideFields;
}

export async function customerMerge(args: CustomerMergeArgs): Promise<CustomerMergePayload> {
  const gql = `#graphql
    mutation customerMerge($customerOneId: ID!, $customerTwoId: ID!, $overrideFields: CustomerMergeOverrideFields) {
      customerMerge(customerOneId: $customerOneId, customerTwoId: $customerTwoId, overrideFields: $overrideFields) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerMerge: CustomerMergePayload }>(gql, args);
  return data.customerMerge;
}

/**
 * Creates a credit card payment method for a customer using a session id.
 * @scope write_customers
 */
export interface CustomerPaymentMethodCreditCardCreateArgs {
  billingAddress: MailingAddressInput;
  customerId: string;
  sessionId: string;
}

export async function customerPaymentMethodCreditCardCreate(args: CustomerPaymentMethodCreditCardCreateArgs): Promise<CustomerPaymentMethodCreditCardCreatePayload> {
  const gql = `#graphql
    mutation customerPaymentMethodCreditCardCreate($billingAddress: MailingAddressInput!, $customerId: ID!, $sessionId: String!) {
      customerPaymentMethodCreditCardCreate(billingAddress: $billingAddress, customerId: $customerId, sessionId: $sessionId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerPaymentMethodCreditCardCreate: CustomerPaymentMethodCreditCardCreatePayload }>(gql, args);
  return data.customerPaymentMethodCreditCardCreate;
}

/**
 * Updates an existing vaulted credit card payment method for a customer, including billing address and card details. Requires a valid cardserver session from a PCI-compliant environment. Use this when a customer's card details have changed (e.g., new expiration date or replacement card) and ongoing subscriptions or saved payment methods need to be updated.
 * @scope write_customers
 */
export interface CustomerPaymentMethodCreditCardUpdateArgs {
  billingAddress: MailingAddressInput;
  id: string;
  sessionId: string;
}

export async function customerPaymentMethodCreditCardUpdate(args: CustomerPaymentMethodCreditCardUpdateArgs): Promise<CustomerPaymentMethodCreditCardUpdatePayload> {
  const gql = `#graphql
    mutation customerPaymentMethodCreditCardUpdate($billingAddress: MailingAddressInput!, $id: ID!, $sessionId: String!) {
      customerPaymentMethodCreditCardUpdate(billingAddress: $billingAddress, id: $id, sessionId: $sessionId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerPaymentMethodCreditCardUpdate: CustomerPaymentMethodCreditCardUpdatePayload }>(gql, args);
  return data.customerPaymentMethodCreditCardUpdate;
}

/**
 * |-
 * @scope write_customers
 */
export interface CustomerPaymentMethodGetUpdateUrlArgs {
  customerPaymentMethodId: string;
}

export async function customerPaymentMethodGetUpdateUrl(args: CustomerPaymentMethodGetUpdateUrlArgs): Promise<CustomerPaymentMethodGetUpdateUrlPayload> {
  const gql = `#graphql
    mutation customerPaymentMethodGetUpdateUrl($customerPaymentMethodId: ID!) {
      customerPaymentMethodGetUpdateUrl(customerPaymentMethodId: $customerPaymentMethodId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerPaymentMethodGetUpdateUrl: CustomerPaymentMethodGetUpdateUrlPayload }>(gql, args);
  return data.customerPaymentMethodGetUpdateUrl;
}

/**
 * Creates a vaulted PayPal billing agreement for a customer, enabling recurring charges through PayPal. The billing agreement ID (starting with 'B-') must be obtained from PayPal. Once created, this payment method can be used for subscription billing or future order payments without requiring the customer to re-authenticate with PayPal.
 * @scope write_customers
 */
export interface CustomerPaymentMethodPaypalBillingAgreementCreateArgs {
  billingAddress?: MailingAddressInput;
  billingAgreementId: string;
  customerId: string;
  inactive?: boolean;
}

export async function customerPaymentMethodPaypalBillingAgreementCreate(args: CustomerPaymentMethodPaypalBillingAgreementCreateArgs): Promise<CustomerPaymentMethodPaypalBillingAgreementCreatePayload> {
  const gql = `#graphql
    mutation customerPaymentMethodPaypalBillingAgreementCreate($billingAddress: MailingAddressInput, $billingAgreementId: String!, $customerId: ID!, $inactive: Boolean) {
      customerPaymentMethodPaypalBillingAgreementCreate(billingAddress: $billingAddress, billingAgreementId: $billingAgreementId, customerId: $customerId, inactive: $inactive) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerPaymentMethodPaypalBillingAgreementCreate: CustomerPaymentMethodPaypalBillingAgreementCreatePayload }>(gql, args);
  return data.customerPaymentMethodPaypalBillingAgreementCreate;
}

/**
 * Updates the billing address associated with a customer's vaulted PayPal billing agreement. Use this when a customer's billing information has changed and their PayPal payment method record in Shopify needs to be updated accordingly.
 * @scope write_customers
 */
export interface CustomerPaymentMethodPaypalBillingAgreementUpdateArgs {
  billingAddress: MailingAddressInput;
  id: string;
}

export async function customerPaymentMethodPaypalBillingAgreementUpdate(args: CustomerPaymentMethodPaypalBillingAgreementUpdateArgs): Promise<CustomerPaymentMethodPaypalBillingAgreementUpdatePayload> {
  const gql = `#graphql
    mutation customerPaymentMethodPaypalBillingAgreementUpdate($billingAddress: MailingAddressInput!, $id: ID!) {
      customerPaymentMethodPaypalBillingAgreementUpdate(billingAddress: $billingAddress, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerPaymentMethodPaypalBillingAgreementUpdate: CustomerPaymentMethodPaypalBillingAgreementUpdatePayload }>(gql, args);
  return data.customerPaymentMethodPaypalBillingAgreementUpdate;
}

/**
 * Creates a customer payment method using identifiers from remote payment gateways like Stripe, Authorize.Net, or Braintree. Imports existing payment methods from external gateways and associates them with Customer objects in Shopify.
 * @scope write_customers
 */
export interface CustomerPaymentMethodRemoteCreateArgs {
  customerId: string;
  remoteReference: CustomerPaymentMethodRemoteInput;
}

export async function customerPaymentMethodRemoteCreate(args: CustomerPaymentMethodRemoteCreateArgs): Promise<CustomerPaymentMethodRemoteCreatePayload> {
  const gql = `#graphql
    mutation customerPaymentMethodRemoteCreate($customerId: ID!, $remoteReference: CustomerPaymentMethodRemoteInput!) {
      customerPaymentMethodRemoteCreate(customerId: $customerId, remoteReference: $remoteReference) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerPaymentMethodRemoteCreate: CustomerPaymentMethodRemoteCreatePayload }>(gql, args);
  return data.customerPaymentMethodRemoteCreate;
}

/**
 * Revokes a customer's vaulted payment method, preventing it from being used for future charges such as subscriptions, draft orders, or other payments. Revocation will fail if the payment method has active subscription contracts. Use this when a customer requests removal of their stored payment information or when a payment method is no longer valid.
 * @scope write_customers
 */
export interface CustomerPaymentMethodRevokeArgs {
  customerPaymentMethodId: string;
}

export async function customerPaymentMethodRevoke(args: CustomerPaymentMethodRevokeArgs): Promise<CustomerPaymentMethodRevokePayload> {
  const gql = `#graphql
    mutation customerPaymentMethodRevoke($customerPaymentMethodId: ID!) {
      customerPaymentMethodRevoke(customerPaymentMethodId: $customerPaymentMethodId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerPaymentMethodRevoke: CustomerPaymentMethodRevokePayload }>(gql, args);
  return data.customerPaymentMethodRevoke;
}

/**
 * Sends an email to a customer containing a secure link to update a specific vaulted payment method. This is commonly used when a customer's credit card is expiring or has been declined, and they need to provide updated payment details for ongoing subscriptions. The email can be customized with sender and BCC fields.
 * @scope write_customers
 */
export interface CustomerPaymentMethodSendUpdateEmailArgs {
  customerPaymentMethodId: string;
  email?: EmailInput;
}

export async function customerPaymentMethodSendUpdateEmail(args: CustomerPaymentMethodSendUpdateEmailArgs): Promise<CustomerPaymentMethodSendUpdateEmailPayload> {
  const gql = `#graphql
    mutation customerPaymentMethodSendUpdateEmail($customerPaymentMethodId: ID!, $email: EmailInput) {
      customerPaymentMethodSendUpdateEmail(customerPaymentMethodId: $customerPaymentMethodId, email: $email) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerPaymentMethodSendUpdateEmail: CustomerPaymentMethodSendUpdateEmailPayload }>(gql, args);
  return data.customerPaymentMethodSendUpdateEmail;
}

/**
 * Remove tax exemptions from a customer.
 * @scope write_customers
 */
export interface CustomerRemoveTaxExemptionsArgs {
  customerId: string;
  taxExemptions: unknown;
}

export async function customerRemoveTaxExemptions(args: CustomerRemoveTaxExemptionsArgs): Promise<CustomerRemoveTaxExemptionsPayload> {
  const gql = `#graphql
    mutation customerRemoveTaxExemptions($customerId: ID!, $taxExemptions: String) {
      customerRemoveTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerRemoveTaxExemptions: CustomerRemoveTaxExemptionsPayload }>(gql, args);
  return data.customerRemoveTaxExemptions;
}

/**
 * Replace tax exemptions for a customer.
 * @scope write_customers
 */
export interface CustomerReplaceTaxExemptionsArgs {
  customerId: string;
  taxExemptions: unknown;
}

export async function customerReplaceTaxExemptions(args: CustomerReplaceTaxExemptionsArgs): Promise<CustomerReplaceTaxExemptionsPayload> {
  const gql = `#graphql
    mutation customerReplaceTaxExemptions($customerId: ID!, $taxExemptions: String) {
      customerReplaceTaxExemptions(customerId: $customerId, taxExemptions: $taxExemptions) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerReplaceTaxExemptions: CustomerReplaceTaxExemptionsPayload }>(gql, args);
  return data.customerReplaceTaxExemptions;
}

/**
 * Enqueues a request to erase customer's data. Read more here.
 * @scope write_customer_data_erasure
 */
export interface CustomerRequestDataErasureArgs {
  customerId: string;
}

export async function customerRequestDataErasure(args: CustomerRequestDataErasureArgs): Promise<CustomerRequestDataErasurePayload> {
  const gql = `#graphql
    mutation customerRequestDataErasure($customerId: ID!) {
      customerRequestDataErasure(customerId: $customerId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerRequestDataErasure: CustomerRequestDataErasurePayload }>(gql, args);
  return data.customerRequestDataErasure;
}

/**
 * Creates a customer segment members query.
 * @scope write_customers
 */
export interface CustomerSegmentMembersQueryCreateArgs {
  input: CustomerSegmentMembersQueryInput;
}

export async function customerSegmentMembersQueryCreate(args: CustomerSegmentMembersQueryCreateArgs): Promise<CustomerSegmentMembersQueryCreatePayload> {
  const gql = `#graphql
    mutation customerSegmentMembersQueryCreate($input: CustomerSegmentMembersQueryInput!) {
      customerSegmentMembersQueryCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerSegmentMembersQueryCreate: CustomerSegmentMembersQueryCreatePayload }>(gql, args);
  return data.customerSegmentMembersQueryCreate;
}

/**
 * Sends an email invitation for a customer to create a legacy customer account. The invitation lets customers set up their password and activate their account in the online store.
 * @scope write_customers
 */
export interface CustomerSendAccountInviteEmailArgs {
  customerId: string;
  email?: EmailInput;
}

export async function customerSendAccountInviteEmail(args: CustomerSendAccountInviteEmailArgs): Promise<CustomerSendAccountInviteEmailPayload> {
  const gql = `#graphql
    mutation customerSendAccountInviteEmail($customerId: ID!, $email: EmailInput) {
      customerSendAccountInviteEmail(customerId: $customerId, email: $email) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerSendAccountInviteEmail: CustomerSendAccountInviteEmailPayload }>(gql, args);
  return data.customerSendAccountInviteEmail;
}

/**
 * Creates or updates a customer in a single mutation.
 * @scope write_customers
 */
export interface CustomerSetArgs {
  identifier?: CustomerSetIdentifiers;
  input: CustomerSetInput;
}

export async function customerSet(args: CustomerSetArgs): Promise<CustomerSetPayload> {
  const gql = `#graphql
    mutation customerSet($identifier: CustomerSetIdentifiers, $input: CustomerSetInput!) {
      customerSet(identifier: $identifier, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerSet: CustomerSetPayload }>(gql, args);
  return data.customerSet;
}

/**
 * Updates a customer's SMS marketing consent information. The customer must have a phone number on their account to receive SMS marketing.
 * @scope write_customers
 */
export interface CustomerSmsMarketingConsentUpdateArgs {
  input: CustomerSmsMarketingConsentUpdateInput;
}

export async function customerSmsMarketingConsentUpdate(args: CustomerSmsMarketingConsentUpdateArgs): Promise<CustomerSmsMarketingConsentUpdatePayload> {
  const gql = `#graphql
    mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!) {
      customerSmsMarketingConsentUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerSmsMarketingConsentUpdate: CustomerSmsMarketingConsentUpdatePayload }>(gql, args);
  return data.customerSmsMarketingConsentUpdate;
}

/**
 * Updates a Customer's attributes including personal information and `tax exemptions`.
 * @scope write_customers
 */
export interface CustomerUpdateArgs {
  input: CustomerInput;
}

export async function customerUpdate(args: CustomerUpdateArgs): Promise<CustomerUpdatePayload> {
  const gql = `#graphql
    mutation customerUpdate($input: CustomerInput!) {
      customerUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerUpdate: CustomerUpdatePayload }>(gql, args);
  return data.customerUpdate;
}

/**
 * Updates a customer's default address.
 * @scope write_customers
 */
export interface CustomerUpdateDefaultAddressArgs {
  addressId: string;
  customerId: string;
}

export async function customerUpdateDefaultAddress(args: CustomerUpdateDefaultAddressArgs): Promise<CustomerUpdateDefaultAddressPayload> {
  const gql = `#graphql
    mutation customerUpdateDefaultAddress($addressId: ID!, $customerId: ID!) {
      customerUpdateDefaultAddress(addressId: $addressId, customerId: $customerId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ customerUpdateDefaultAddress: CustomerUpdateDefaultAddressPayload }>(gql, args);
  return data.customerUpdateDefaultAddress;
}

/**
 * Creates a segment.
 * @scope write_customers
 */
export interface SegmentCreateArgs {
  name: string;
  query: string;
}

export async function segmentCreate(args: SegmentCreateArgs): Promise<SegmentCreatePayload> {
  const gql = `#graphql
    mutation segmentCreate($name: String!, $query: String!) {
      segmentCreate(name: $name, query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ segmentCreate: SegmentCreatePayload }>(gql, args);
  return data.segmentCreate;
}

/**
 * Deletes a segment.
 * @scope write_customers
 */
export interface SegmentDeleteArgs {
  id: string;
}

export async function segmentDelete(args: SegmentDeleteArgs): Promise<SegmentDeletePayload> {
  const gql = `#graphql
    mutation segmentDelete($id: ID!) {
      segmentDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ segmentDelete: SegmentDeletePayload }>(gql, args);
  return data.segmentDelete;
}

/**
 * Updates a segment.
 * @scope write_customers
 */
export interface SegmentUpdateArgs {
  id: string;
  name?: string;
  query?: string;
}

export async function segmentUpdate(args: SegmentUpdateArgs): Promise<SegmentUpdatePayload> {
  const gql = `#graphql
    mutation segmentUpdate($id: ID!, $name: String, $query: String) {
      segmentUpdate(id: $id, name: $name, query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ segmentUpdate: SegmentUpdatePayload }>(gql, args);
  return data.segmentUpdate;
}

/**
 * Adds funds to a StoreCreditAccount by creating a StoreCreditAccountCreditTransaction. The mutation accepts either a store credit account ID, a Customer ID, or a CompanyLocation ID. When you provide a customer or company location ID, it automatically creates an account if one doesn't exist for the specified currency.
 * @scope write_store_credit_account_transactions
 */
export interface StoreCreditAccountCreditArgs {
  creditInput: StoreCreditAccountCreditInput;
  id: string;
}

export async function storeCreditAccountCredit(args: StoreCreditAccountCreditArgs): Promise<StoreCreditAccountCreditPayload> {
  const gql = `#graphql
    mutation storeCreditAccountCredit($creditInput: StoreCreditAccountCreditInput!, $id: ID!) {
      storeCreditAccountCredit(creditInput: $creditInput, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ storeCreditAccountCredit: StoreCreditAccountCreditPayload }>(gql, args);
  return data.storeCreditAccountCredit;
}

/**
 * Creates a debit transaction that decreases the store credit account balance by the given amount.
 * @scope write_store_credit_account_transactions
 */
export interface StoreCreditAccountDebitArgs {
  debitInput: StoreCreditAccountDebitInput;
  id: string;
}

export async function storeCreditAccountDebit(args: StoreCreditAccountDebitArgs): Promise<StoreCreditAccountDebitPayload> {
  const gql = `#graphql
    mutation storeCreditAccountDebit($debitInput: StoreCreditAccountDebitInput!, $id: ID!) {
      storeCreditAccountDebit(debitInput: $debitInput, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ storeCreditAccountDebit: StoreCreditAccountDebitPayload }>(gql, args);
  return data.storeCreditAccountDebit;
}

/**
 * Creates a billing attempt to charge for a SubscriptionContract. The mutation processes either the payment for the current billing cycle or for a specific cycle, if selected.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingAttemptCreateArgs {
  subscriptionBillingAttemptInput: SubscriptionBillingAttemptInput;
  subscriptionContractId: string;
}

export async function subscriptionBillingAttemptCreate(args: SubscriptionBillingAttemptCreateArgs): Promise<SubscriptionBillingAttemptCreatePayload> {
  const gql = `#graphql
    mutation subscriptionBillingAttemptCreate($subscriptionBillingAttemptInput: SubscriptionBillingAttemptInput!, $subscriptionContractId: ID!) {
      subscriptionBillingAttemptCreate(subscriptionBillingAttemptInput: $subscriptionBillingAttemptInput, subscriptionContractId: $subscriptionContractId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingAttemptCreate: SubscriptionBillingAttemptCreatePayload }>(gql, args);
  return data.subscriptionBillingAttemptCreate;
}

/**
 * Asynchronously queries and charges all subscription billing cycles whose billingAttemptExpectedDate values fall within a specified date range and meet additional filtering criteria. The results of this action can be retrieved using the subscriptionBillingCycleBulkResults query.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleBulkChargeArgs {
  billingAttemptExpectedDateRange: SubscriptionBillingCyclesDateRangeSelector;
  filters?: SubscriptionBillingCycleBulkFilters;
  inventoryPolicy?: SubscriptionBillingAttemptInventoryPolicy;
  paymentProcessingPolicy?: SubscriptionBillingAttemptPaymentProcessingPolicy;
}

export async function subscriptionBillingCycleBulkCharge(args: SubscriptionBillingCycleBulkChargeArgs): Promise<SubscriptionBillingCycleBulkChargePayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleBulkCharge($billingAttemptExpectedDateRange: SubscriptionBillingCyclesDateRangeSelector!, $filters: SubscriptionBillingCycleBulkFilters, $inventoryPolicy: SubscriptionBillingAttemptInventoryPolicy, $paymentProcessingPolicy: SubscriptionBillingAttemptPaymentProcessingPolicy) {
      subscriptionBillingCycleBulkCharge(billingAttemptExpectedDateRange: $billingAttemptExpectedDateRange, filters: $filters, inventoryPolicy: $inventoryPolicy, paymentProcessingPolicy: $paymentProcessingPolicy) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleBulkCharge: SubscriptionBillingCycleBulkChargePayload }>(gql, args);
  return data.subscriptionBillingCycleBulkCharge;
}

/**
 * Asynchronously queries all subscription billing cycles whose billingAttemptExpectedDate values fall within a specified date range and meet additional filtering criteria. The results of this action can be retrieved using the subscriptionBillingCycleBulkResults query.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleBulkSearchArgs {
  billingAttemptExpectedDateRange: SubscriptionBillingCyclesDateRangeSelector;
  filters?: SubscriptionBillingCycleBulkFilters;
}

export async function subscriptionBillingCycleBulkSearch(args: SubscriptionBillingCycleBulkSearchArgs): Promise<SubscriptionBillingCycleBulkSearchPayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleBulkSearch($billingAttemptExpectedDateRange: SubscriptionBillingCyclesDateRangeSelector!, $filters: SubscriptionBillingCycleBulkFilters) {
      subscriptionBillingCycleBulkSearch(billingAttemptExpectedDateRange: $billingAttemptExpectedDateRange, filters: $filters) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleBulkSearch: SubscriptionBillingCycleBulkSearchPayload }>(gql, args);
  return data.subscriptionBillingCycleBulkSearch;
}

/**
 * Creates a new subscription billing attempt for a specified billing cycle. This is the alternative mutation for subscriptionBillingAttemptCreate. For more information, refer to Create a subscription contract.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleChargeArgs {
  billingCycleSelector: SubscriptionBillingCycleSelector;
  inventoryPolicy?: SubscriptionBillingAttemptInventoryPolicy;
  paymentProcessingPolicy?: SubscriptionBillingAttemptPaymentProcessingPolicy;
  subscriptionContractId: string;
}

export async function subscriptionBillingCycleCharge(args: SubscriptionBillingCycleChargeArgs): Promise<SubscriptionBillingCycleChargePayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleCharge($billingCycleSelector: SubscriptionBillingCycleSelector!, $inventoryPolicy: SubscriptionBillingAttemptInventoryPolicy, $paymentProcessingPolicy: SubscriptionBillingAttemptPaymentProcessingPolicy, $subscriptionContractId: ID!) {
      subscriptionBillingCycleCharge(billingCycleSelector: $billingCycleSelector, inventoryPolicy: $inventoryPolicy, paymentProcessingPolicy: $paymentProcessingPolicy, subscriptionContractId: $subscriptionContractId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleCharge: SubscriptionBillingCycleChargePayload }>(gql, args);
  return data.subscriptionBillingCycleCharge;
}

/**
 * Commits the updates of a Subscription Billing Cycle Contract draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleContractDraftCommitArgs {
  draftId: string;
}

export async function subscriptionBillingCycleContractDraftCommit(args: SubscriptionBillingCycleContractDraftCommitArgs): Promise<SubscriptionBillingCycleContractDraftCommitPayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleContractDraftCommit($draftId: ID!) {
      subscriptionBillingCycleContractDraftCommit(draftId: $draftId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleContractDraftCommit: SubscriptionBillingCycleContractDraftCommitPayload }>(gql, args);
  return data.subscriptionBillingCycleContractDraftCommit;
}

/**
 * Concatenates a contract to a Subscription Draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleContractDraftConcatenateArgs {
  concatenatedBillingCycleContracts: unknown;
  draftId: string;
}

export async function subscriptionBillingCycleContractDraftConcatenate(args: SubscriptionBillingCycleContractDraftConcatenateArgs): Promise<SubscriptionBillingCycleContractDraftConcatenatePayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleContractDraftConcatenate($concatenatedBillingCycleContracts: String, $draftId: ID!) {
      subscriptionBillingCycleContractDraftConcatenate(concatenatedBillingCycleContracts: $concatenatedBillingCycleContracts, draftId: $draftId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleContractDraftConcatenate: SubscriptionBillingCycleContractDraftConcatenatePayload }>(gql, args);
  return data.subscriptionBillingCycleContractDraftConcatenate;
}

/**
 * Edit the contents of a subscription contract for the specified billing cycle.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleContractEditArgs {
  billingCycleInput: SubscriptionBillingCycleInput;
}

export async function subscriptionBillingCycleContractEdit(args: SubscriptionBillingCycleContractEditArgs): Promise<SubscriptionBillingCycleContractEditPayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleContractEdit($billingCycleInput: SubscriptionBillingCycleInput!) {
      subscriptionBillingCycleContractEdit(billingCycleInput: $billingCycleInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleContractEdit: SubscriptionBillingCycleContractEditPayload }>(gql, args);
  return data.subscriptionBillingCycleContractEdit;
}

/**
 * Delete the schedule and contract edits of the selected subscription billing cycle.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleEditDeleteArgs {
  billingCycleInput: SubscriptionBillingCycleInput;
}

export async function subscriptionBillingCycleEditDelete(args: SubscriptionBillingCycleEditDeleteArgs): Promise<SubscriptionBillingCycleEditDeletePayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleEditDelete($billingCycleInput: SubscriptionBillingCycleInput!) {
      subscriptionBillingCycleEditDelete(billingCycleInput: $billingCycleInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleEditDelete: SubscriptionBillingCycleEditDeletePayload }>(gql, args);
  return data.subscriptionBillingCycleEditDelete;
}

/**
 * Delete the current and future schedule and contract edits of a list of subscription billing cycles.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleEditsDeleteArgs {
  contractId: string;
  targetSelection: SubscriptionBillingCyclesTargetSelection;
}

export async function subscriptionBillingCycleEditsDelete(args: SubscriptionBillingCycleEditsDeleteArgs): Promise<SubscriptionBillingCycleEditsDeletePayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleEditsDelete($contractId: ID!, $targetSelection: SubscriptionBillingCyclesTargetSelection!) {
      subscriptionBillingCycleEditsDelete(contractId: $contractId, targetSelection: $targetSelection) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleEditsDelete: SubscriptionBillingCycleEditsDeletePayload }>(gql, args);
  return data.subscriptionBillingCycleEditsDelete;
}

/**
 * Modify the schedule of a specific billing cycle.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleScheduleEditArgs {
  billingCycleInput: SubscriptionBillingCycleInput;
  input: SubscriptionBillingCycleScheduleEditInput;
}

export async function subscriptionBillingCycleScheduleEdit(args: SubscriptionBillingCycleScheduleEditArgs): Promise<SubscriptionBillingCycleScheduleEditPayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleScheduleEdit($billingCycleInput: SubscriptionBillingCycleInput!, $input: SubscriptionBillingCycleScheduleEditInput!) {
      subscriptionBillingCycleScheduleEdit(billingCycleInput: $billingCycleInput, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleScheduleEdit: SubscriptionBillingCycleScheduleEditPayload }>(gql, args);
  return data.subscriptionBillingCycleScheduleEdit;
}

/**
 * Skips a Subscription Billing Cycle.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleSkipArgs {
  billingCycleInput: SubscriptionBillingCycleInput;
}

export async function subscriptionBillingCycleSkip(args: SubscriptionBillingCycleSkipArgs): Promise<SubscriptionBillingCycleSkipPayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleSkip($billingCycleInput: SubscriptionBillingCycleInput!) {
      subscriptionBillingCycleSkip(billingCycleInput: $billingCycleInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleSkip: SubscriptionBillingCycleSkipPayload }>(gql, args);
  return data.subscriptionBillingCycleSkip;
}

/**
 * Unskips a Subscription Billing Cycle.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionBillingCycleUnskipArgs {
  billingCycleInput: SubscriptionBillingCycleInput;
}

export async function subscriptionBillingCycleUnskip(args: SubscriptionBillingCycleUnskipArgs): Promise<SubscriptionBillingCycleUnskipPayload> {
  const gql = `#graphql
    mutation subscriptionBillingCycleUnskip($billingCycleInput: SubscriptionBillingCycleInput!) {
      subscriptionBillingCycleUnskip(billingCycleInput: $billingCycleInput) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionBillingCycleUnskip: SubscriptionBillingCycleUnskipPayload }>(gql, args);
  return data.subscriptionBillingCycleUnskip;
}

/**
 * Activates a Subscription Contract. Contract status must be either active, paused, or failed.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionContractActivateArgs {
  subscriptionContractId: string;
}

export async function subscriptionContractActivate(args: SubscriptionContractActivateArgs): Promise<SubscriptionContractActivatePayload> {
  const gql = `#graphql
    mutation subscriptionContractActivate($subscriptionContractId: ID!) {
      subscriptionContractActivate(subscriptionContractId: $subscriptionContractId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContractActivate: SubscriptionContractActivatePayload }>(gql, args);
  return data.subscriptionContractActivate;
}

/**
 * Creates a Subscription Contract.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionContractAtomicCreateArgs {
  input: SubscriptionContractAtomicCreateInput;
}

export async function subscriptionContractAtomicCreate(args: SubscriptionContractAtomicCreateArgs): Promise<SubscriptionContractAtomicCreatePayload> {
  const gql = `#graphql
    mutation subscriptionContractAtomicCreate($input: SubscriptionContractAtomicCreateInput!) {
      subscriptionContractAtomicCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContractAtomicCreate: SubscriptionContractAtomicCreatePayload }>(gql, args);
  return data.subscriptionContractAtomicCreate;
}

/**
 * Cancels a Subscription Contract.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionContractCancelArgs {
  subscriptionContractId: string;
}

export async function subscriptionContractCancel(args: SubscriptionContractCancelArgs): Promise<SubscriptionContractCancelPayload> {
  const gql = `#graphql
    mutation subscriptionContractCancel($subscriptionContractId: ID!) {
      subscriptionContractCancel(subscriptionContractId: $subscriptionContractId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContractCancel: SubscriptionContractCancelPayload }>(gql, args);
  return data.subscriptionContractCancel;
}

/**
 * Creates a subscription contract draft, which is an intention to create a new subscription. The draft lets you incrementally build and modify subscription details before committing them to create the actual SubscriptionContract.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionContractCreateArgs {
  input: SubscriptionContractCreateInput;
}

export async function subscriptionContractCreate(args: SubscriptionContractCreateArgs): Promise<SubscriptionContractCreatePayload> {
  const gql = `#graphql
    mutation subscriptionContractCreate($input: SubscriptionContractCreateInput!) {
      subscriptionContractCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContractCreate: SubscriptionContractCreatePayload }>(gql, args);
  return data.subscriptionContractCreate;
}

/**
 * Expires a Subscription Contract.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionContractExpireArgs {
  subscriptionContractId: string;
}

export async function subscriptionContractExpire(args: SubscriptionContractExpireArgs): Promise<SubscriptionContractExpirePayload> {
  const gql = `#graphql
    mutation subscriptionContractExpire($subscriptionContractId: ID!) {
      subscriptionContractExpire(subscriptionContractId: $subscriptionContractId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContractExpire: SubscriptionContractExpirePayload }>(gql, args);
  return data.subscriptionContractExpire;
}

/**
 * Fails a Subscription Contract.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionContractFailArgs {
  subscriptionContractId: string;
}

export async function subscriptionContractFail(args: SubscriptionContractFailArgs): Promise<SubscriptionContractFailPayload> {
  const gql = `#graphql
    mutation subscriptionContractFail($subscriptionContractId: ID!) {
      subscriptionContractFail(subscriptionContractId: $subscriptionContractId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContractFail: SubscriptionContractFailPayload }>(gql, args);
  return data.subscriptionContractFail;
}

/**
 * Pauses a Subscription Contract.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionContractPauseArgs {
  subscriptionContractId: string;
}

export async function subscriptionContractPause(args: SubscriptionContractPauseArgs): Promise<SubscriptionContractPausePayload> {
  const gql = `#graphql
    mutation subscriptionContractPause($subscriptionContractId: ID!) {
      subscriptionContractPause(subscriptionContractId: $subscriptionContractId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContractPause: SubscriptionContractPausePayload }>(gql, args);
  return data.subscriptionContractPause;
}

/**
 * Allows for the easy change of a Product in a Contract or a Product price change.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionContractProductChangeArgs {
  input: SubscriptionContractProductChangeInput;
  lineId: string;
  subscriptionContractId: string;
}

export async function subscriptionContractProductChange(args: SubscriptionContractProductChangeArgs): Promise<SubscriptionContractProductChangePayload> {
  const gql = `#graphql
    mutation subscriptionContractProductChange($input: SubscriptionContractProductChangeInput!, $lineId: ID!, $subscriptionContractId: ID!) {
      subscriptionContractProductChange(input: $input, lineId: $lineId, subscriptionContractId: $subscriptionContractId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContractProductChange: SubscriptionContractProductChangePayload }>(gql, args);
  return data.subscriptionContractProductChange;
}

/**
 * Sets the next billing date of a Subscription Contract. This field is managed by the apps. Alternatively you can utilize our Billing Cycles APIs, which provide auto-computed billing dates and additional functionalities.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionContractSetNextBillingDateArgs {
  contractId: string;
  date: string;
}

export async function subscriptionContractSetNextBillingDate(args: SubscriptionContractSetNextBillingDateArgs): Promise<SubscriptionContractSetNextBillingDatePayload> {
  const gql = `#graphql
    mutation subscriptionContractSetNextBillingDate($contractId: ID!, $date: DateTime!) {
      subscriptionContractSetNextBillingDate(contractId: $contractId, date: $date) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContractSetNextBillingDate: SubscriptionContractSetNextBillingDatePayload }>(gql, args);
  return data.subscriptionContractSetNextBillingDate;
}

/**
 * Creates a draft of an existing SubscriptionContract. The draft captures the current state of the contract and allows incremental modifications through draft mutations such as subscriptionDraftLineAdd, subscriptionDraftDiscountAdd, and subscriptionDraftUpdate.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionContractUpdateArgs {
  contractId: string;
}

export async function subscriptionContractUpdate(args: SubscriptionContractUpdateArgs): Promise<SubscriptionContractUpdatePayload> {
  const gql = `#graphql
    mutation subscriptionContractUpdate($contractId: ID!) {
      subscriptionContractUpdate(contractId: $contractId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionContractUpdate: SubscriptionContractUpdatePayload }>(gql, args);
  return data.subscriptionContractUpdate;
}

/**
 * Commits the updates of a Subscription Contract draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftCommitArgs {
  draftId: string;
}

export async function subscriptionDraftCommit(args: SubscriptionDraftCommitArgs): Promise<SubscriptionDraftCommitPayload> {
  const gql = `#graphql
    mutation subscriptionDraftCommit($draftId: ID!) {
      subscriptionDraftCommit(draftId: $draftId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftCommit: SubscriptionDraftCommitPayload }>(gql, args);
  return data.subscriptionDraftCommit;
}

/**
 * Adds a subscription discount to a subscription draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftDiscountAddArgs {
  draftId: string;
  input: SubscriptionManualDiscountInput;
}

export async function subscriptionDraftDiscountAdd(args: SubscriptionDraftDiscountAddArgs): Promise<SubscriptionDraftDiscountAddPayload> {
  const gql = `#graphql
    mutation subscriptionDraftDiscountAdd($draftId: ID!, $input: SubscriptionManualDiscountInput!) {
      subscriptionDraftDiscountAdd(draftId: $draftId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftDiscountAdd: SubscriptionDraftDiscountAddPayload }>(gql, args);
  return data.subscriptionDraftDiscountAdd;
}

/**
 * Applies a code discount on the subscription draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftDiscountCodeApplyArgs {
  draftId: string;
  redeemCode: string;
}

export async function subscriptionDraftDiscountCodeApply(args: SubscriptionDraftDiscountCodeApplyArgs): Promise<SubscriptionDraftDiscountCodeApplyPayload> {
  const gql = `#graphql
    mutation subscriptionDraftDiscountCodeApply($draftId: ID!, $redeemCode: String!) {
      subscriptionDraftDiscountCodeApply(draftId: $draftId, redeemCode: $redeemCode) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftDiscountCodeApply: SubscriptionDraftDiscountCodeApplyPayload }>(gql, args);
  return data.subscriptionDraftDiscountCodeApply;
}

/**
 * Removes a subscription discount from a subscription draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftDiscountRemoveArgs {
  discountId: string;
  draftId: string;
}

export async function subscriptionDraftDiscountRemove(args: SubscriptionDraftDiscountRemoveArgs): Promise<SubscriptionDraftDiscountRemovePayload> {
  const gql = `#graphql
    mutation subscriptionDraftDiscountRemove($discountId: ID!, $draftId: ID!) {
      subscriptionDraftDiscountRemove(discountId: $discountId, draftId: $draftId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftDiscountRemove: SubscriptionDraftDiscountRemovePayload }>(gql, args);
  return data.subscriptionDraftDiscountRemove;
}

/**
 * Updates a subscription discount on a subscription draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftDiscountUpdateArgs {
  discountId: string;
  draftId: string;
  input: SubscriptionManualDiscountInput;
}

export async function subscriptionDraftDiscountUpdate(args: SubscriptionDraftDiscountUpdateArgs): Promise<SubscriptionDraftDiscountUpdatePayload> {
  const gql = `#graphql
    mutation subscriptionDraftDiscountUpdate($discountId: ID!, $draftId: ID!, $input: SubscriptionManualDiscountInput!) {
      subscriptionDraftDiscountUpdate(discountId: $discountId, draftId: $draftId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftDiscountUpdate: SubscriptionDraftDiscountUpdatePayload }>(gql, args);
  return data.subscriptionDraftDiscountUpdate;
}

/**
 * Adds a subscription free shipping discount to a subscription draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftFreeShippingDiscountAddArgs {
  draftId: string;
  input: SubscriptionFreeShippingDiscountInput;
}

export async function subscriptionDraftFreeShippingDiscountAdd(args: SubscriptionDraftFreeShippingDiscountAddArgs): Promise<SubscriptionDraftFreeShippingDiscountAddPayload> {
  const gql = `#graphql
    mutation subscriptionDraftFreeShippingDiscountAdd($draftId: ID!, $input: SubscriptionFreeShippingDiscountInput!) {
      subscriptionDraftFreeShippingDiscountAdd(draftId: $draftId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftFreeShippingDiscountAdd: SubscriptionDraftFreeShippingDiscountAddPayload }>(gql, args);
  return data.subscriptionDraftFreeShippingDiscountAdd;
}

/**
 * Updates a subscription free shipping discount on a subscription draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftFreeShippingDiscountUpdateArgs {
  discountId: string;
  draftId: string;
  input: SubscriptionFreeShippingDiscountInput;
}

export async function subscriptionDraftFreeShippingDiscountUpdate(args: SubscriptionDraftFreeShippingDiscountUpdateArgs): Promise<SubscriptionDraftFreeShippingDiscountUpdatePayload> {
  const gql = `#graphql
    mutation subscriptionDraftFreeShippingDiscountUpdate($discountId: ID!, $draftId: ID!, $input: SubscriptionFreeShippingDiscountInput!) {
      subscriptionDraftFreeShippingDiscountUpdate(discountId: $discountId, draftId: $draftId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftFreeShippingDiscountUpdate: SubscriptionDraftFreeShippingDiscountUpdatePayload }>(gql, args);
  return data.subscriptionDraftFreeShippingDiscountUpdate;
}

/**
 * Adds a subscription line to a subscription draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftLineAddArgs {
  draftId: string;
  input: SubscriptionLineInput;
}

export async function subscriptionDraftLineAdd(args: SubscriptionDraftLineAddArgs): Promise<SubscriptionDraftLineAddPayload> {
  const gql = `#graphql
    mutation subscriptionDraftLineAdd($draftId: ID!, $input: SubscriptionLineInput!) {
      subscriptionDraftLineAdd(draftId: $draftId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftLineAdd: SubscriptionDraftLineAddPayload }>(gql, args);
  return data.subscriptionDraftLineAdd;
}

/**
 * Removes a subscription line from a subscription draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftLineRemoveArgs {
  draftId: string;
  lineId: string;
}

export async function subscriptionDraftLineRemove(args: SubscriptionDraftLineRemoveArgs): Promise<SubscriptionDraftLineRemovePayload> {
  const gql = `#graphql
    mutation subscriptionDraftLineRemove($draftId: ID!, $lineId: ID!) {
      subscriptionDraftLineRemove(draftId: $draftId, lineId: $lineId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftLineRemove: SubscriptionDraftLineRemovePayload }>(gql, args);
  return data.subscriptionDraftLineRemove;
}

/**
 * Updates a subscription line on a subscription draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftLineUpdateArgs {
  draftId: string;
  input: SubscriptionLineUpdateInput;
  lineId: string;
}

export async function subscriptionDraftLineUpdate(args: SubscriptionDraftLineUpdateArgs): Promise<SubscriptionDraftLineUpdatePayload> {
  const gql = `#graphql
    mutation subscriptionDraftLineUpdate($draftId: ID!, $input: SubscriptionLineUpdateInput!, $lineId: ID!) {
      subscriptionDraftLineUpdate(draftId: $draftId, input: $input, lineId: $lineId) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftLineUpdate: SubscriptionDraftLineUpdatePayload }>(gql, args);
  return data.subscriptionDraftLineUpdate;
}

/**
 * Updates a Subscription Draft.
 * @scope write_own_subscription_contracts
 */
export interface SubscriptionDraftUpdateArgs {
  draftId: string;
  input: SubscriptionDraftInput;
}

export async function subscriptionDraftUpdate(args: SubscriptionDraftUpdateArgs): Promise<SubscriptionDraftUpdatePayload> {
  const gql = `#graphql
    mutation subscriptionDraftUpdate($draftId: ID!, $input: SubscriptionDraftInput!) {
      subscriptionDraftUpdate(draftId: $draftId, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ subscriptionDraftUpdate: SubscriptionDraftUpdatePayload }>(gql, args);
  return data.subscriptionDraftUpdate;
}










