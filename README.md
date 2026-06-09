# Shopify Admin API — Function Reference

**792 operations** across 18 sections. All functions return `Promise<T>`.

## Contents

1. [Customers](#customers)
2. [Discounts & Marketing](#discounts-marketing)
3. [Inventory](#inventory)
4. [Orders](#orders)
5. [Products & Collections](#products-collections)
6. [Retail / POS](#retail-pos)
7. [Shipping & Fulfillment](#shipping-fulfillment)
8. [App Management](#app-management)
9. [CMS (Articles, Blogs, Pages)](#cms-articles-blogs-pages)
10. [Channels & Publications](#channels-publications)
11. [Metafields & Metaobjects](#metafields-metaobjects)
12. [Shop Configuration](#shop-configuration)
13. [Themes & Online Store](#themes-online-store)
14. [Webhooks, Events & Bulk Ops](#webhooks-events-bulk-ops)
15. [Markets & Localization](#markets-localization)
16. [Files & Media](#files-media)
17. [URL Redirects](#url-redirects)
18. [Miscellaneous](#miscellaneous)

---

## Customers

### `companies`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: CompanySortKeys` |
| **Request** | `query companies($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CompanySortKeys)` |
| **Returns** | `CompanyConnection` |

### `companiesCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number` |
| **Request** | `query companiesCount($limit: Int)` |
| **Returns** | `Count | null` |

### `company`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query company($id: ID!)` |
| **Returns** | `Company | null` |

### `companyContact`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query companyContact($id: ID!)` |
| **Returns** | `CompanyContact | null` |

### `companyContactRole`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query companyContactRole($id: ID!)` |
| **Returns** | `CompanyContactRole | null` |

### `companyLocation`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query companyLocation($id: ID!)` |
| **Returns** | `CompanyLocation | null` |

### `companyLocations`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: CompanyLocationSortKeys` |
| **Request** | `query companyLocations($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CompanyLocationSortKeys)` |
| **Returns** | `CompanyLocationConnection` |

### `customer`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query customer($id: ID!)` |
| **Returns** | `Customer | null` |

### `customerAccountPage`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query customerAccountPage($id: ID!)` |
| **Returns** | `CustomerAccountPage | null` |

### `customerAccountPages`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query customerAccountPages($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `CustomerAccountPageConnection` |

### `customerByIdentifier`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `identifier: CustomerIdentifierInput` |
| **Request** | `query customerByIdentifier($identifier: CustomerIdentifierInput!)` |
| **Returns** | `Customer | null` |

### `customerMergeJobStatus`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `jobId: string` |
| **Request** | `query customerMergeJobStatus($jobId: ID!)` |
| **Returns** | `CustomerMergeRequest | null` |

### `customerMergePreview`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `customerOneId: string, customerTwoId: string, overrideFields?: CustomerMergeOverrideFields` |
| **Request** | `query customerMergePreview($customerOneId: ID!, $customerTwoId: ID!, $overrideFields: CustomerMergeOverrideFields)` |
| **Returns** | `CustomerMergePreview | null` |

### `customerPaymentMethod`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string, showRevoked?: boolean` |
| **Request** | `query customerPaymentMethod($id: ID!, $showRevoked: Boolean)` |
| **Returns** | `CustomerPaymentMethod | null` |

### `customerSavedSearches`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: CustomerSavedSearchSortKeys` |
| **Request** | `query customerSavedSearches($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CustomerSavedSearchSortKeys)` |
| **Returns** | `SavedSearchConnection` |

### `customerSegmentMembers`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, queryId?: string, reverse?: boolean, segmentId?: string, sortKey?: string, timezone?: string` |
| **Request** | `query customerSegmentMembers($after: String, $before: String, $first: Int, $last: Int, $query: String, $queryId: ID, $reverse: Boolean, $segmentId: ID, $sortKey: String, $timezone: String)` |
| **Returns** | `CustomerSegmentMemberConnection` |

### `customerSegmentMembersQuery`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query customerSegmentMembersQuery($id: ID!)` |
| **Returns** | `CustomerSegmentMembersQuery | null` |

### `customerSegmentMembership`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `customerId: string, segmentIds: unknown` |
| **Request** | `query customerSegmentMembership($customerId: ID!, $segmentIds: String)` |
| **Returns** | `SegmentMembershipResponse | null` |

### `customers`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: CustomerSortKeys` |
| **Request** | `query customers($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CustomerSortKeys)` |
| **Returns** | `CustomerConnection` |

### `customersCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string` |
| **Request** | `query customersCount($limit: Int, $query: String)` |
| **Returns** | `Count | null` |

### `segment`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query segment($id: ID!)` |
| **Returns** | `Segment | null` |

### `segmentFilterSuggestions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, first: number, search: string` |
| **Request** | `query segmentFilterSuggestions($after: String, $first: Int!, $search: String!)` |
| **Returns** | `SegmentFilterConnection` |

### `segmentFilters`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number` |
| **Request** | `query segmentFilters($after: String, $before: String, $first: Int, $last: Int)` |
| **Returns** | `SegmentFilterConnection` |

### `segmentMigrations`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, savedSearchId?: string` |
| **Request** | `query segmentMigrations($after: String, $before: String, $first: Int, $last: Int, $savedSearchId: ID)` |
| **Returns** | `SegmentMigrationConnection` |

### `segmentValueSuggestions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, filterQueryName?: string, first?: number, functionParameterQueryName?: string, last?: number, search: string` |
| **Request** | `query segmentValueSuggestions($after: String, $before: String, $filterQueryName: String, $first: Int, $functionParameterQueryName: String, $last: Int, $search: String!)` |
| **Returns** | `SegmentValueConnection` |

### `segments`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: SegmentSortKeys` |
| **Request** | `query segments($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: SegmentSortKeys)` |
| **Returns** | `SegmentConnection` |

### `segmentsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number` |
| **Request** | `query segmentsCount($limit: Int)` |
| **Returns** | `Count | null` |

### `storeCreditAccount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query storeCreditAccount($id: ID!)` |
| **Returns** | `StoreCreditAccount | null` |

### `storeCreditConfiguration`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query storeCreditConfiguration` |
| **Returns** | `StoreCreditConfiguration | null` |

### `subscriptionBillingAttempt`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query subscriptionBillingAttempt($id: ID!)` |
| **Returns** | `SubscriptionBillingAttempt | null` |

### `subscriptionBillingAttempts`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: SubscriptionBillingAttemptsSortKeys` |
| **Request** | `query subscriptionBillingAttempts($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: SubscriptionBillingAttemptsSortKeys)` |
| **Returns** | `SubscriptionBillingAttemptConnection` |

### `subscriptionBillingCycle`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `billingCycleInput: SubscriptionBillingCycleInput` |
| **Request** | `query subscriptionBillingCycle($billingCycleInput: SubscriptionBillingCycleInput!)` |
| **Returns** | `SubscriptionBillingCycle | null` |

### `subscriptionBillingCycleBulkResults`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, jobId: string, last?: number, reverse?: boolean` |
| **Request** | `query subscriptionBillingCycleBulkResults($after: String, $before: String, $first: Int, $jobId: ID!, $last: Int, $reverse: Boolean)` |
| **Returns** | `SubscriptionBillingCycleConnection` |

### `subscriptionBillingCycles`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, billingCyclesDateRangeSelector?: SubscriptionBillingCyclesDateRangeSelector, billingCyclesIndexRangeSelector?: SubscriptionBillingCyclesIndexRangeSelector, contractId: string, first?: number, last?: number, reverse?: boolean, sortKey?: SubscriptionBillingCyclesSortKeys` |
| **Request** | `query subscriptionBillingCycles($after: String, $before: String, $billingCyclesDateRangeSelector: SubscriptionBillingCyclesDateRangeSelector, $billingCyclesIndexRangeSelector: SubscriptionBillingCyclesIndexRangeSelector, $contractId: ID!, $first: Int, $last: Int, $reverse: Boolean, $sortKey: SubscriptionBillingCyclesSortKeys)` |
| **Returns** | `SubscriptionBillingCycleConnection` |

### `subscriptionContract`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query subscriptionContract($id: ID!)` |
| **Returns** | `SubscriptionContract | null` |

### `subscriptionContracts`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: SubscriptionContractsSortKeys` |
| **Request** | `query subscriptionContracts($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: SubscriptionContractsSortKeys)` |
| **Returns** | `SubscriptionContractConnection` |

### `subscriptionDraft`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query subscriptionDraft($id: ID!)` |
| **Returns** | `SubscriptionDraft | null` |

### `companiesDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyIds: unknown` |
| **Request** | `mutation companiesDelete($companyIds: String)` |
| **Returns** | `CompaniesDeletePayload` |

### `companyAddressDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `addressId: string` |
| **Request** | `mutation companyAddressDelete($addressId: ID!)` |
| **Returns** | `CompanyAddressDeletePayload` |

### `companyAssignCustomerAsContact`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyId: string, customerId: string` |
| **Request** | `mutation companyAssignCustomerAsContact($companyId: ID!, $customerId: ID!)` |
| **Returns** | `CompanyAssignCustomerAsContactPayload` |

### `companyAssignMainContact`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyContactId: string, companyId: string` |
| **Request** | `mutation companyAssignMainContact($companyContactId: ID!, $companyId: ID!)` |
| **Returns** | `CompanyAssignMainContactPayload` |

### `companyContactAssignRole`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyContactId: string, companyContactRoleId: string, companyLocationId: string` |
| **Request** | `mutation companyContactAssignRole($companyContactId: ID!, $companyContactRoleId: ID!, $companyLocationId: ID!)` |
| **Returns** | `CompanyContactAssignRolePayload` |

### `companyContactAssignRoles`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyContactId: string, rolesToAssign: unknown` |
| **Request** | `mutation companyContactAssignRoles($companyContactId: ID!, $rolesToAssign: String)` |
| **Returns** | `CompanyContactAssignRolesPayload` |

### `companyContactCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyId: string, input: CompanyContactInput` |
| **Request** | `mutation companyContactCreate($companyId: ID!, $input: CompanyContactInput!)` |
| **Returns** | `CompanyContactCreatePayload` |

### `companyContactDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyContactId: string` |
| **Request** | `mutation companyContactDelete($companyContactId: ID!)` |
| **Returns** | `CompanyContactDeletePayload` |

### `companyContactRemoveFromCompany`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyContactId: string` |
| **Request** | `mutation companyContactRemoveFromCompany($companyContactId: ID!)` |
| **Returns** | `CompanyContactRemoveFromCompanyPayload` |

### `companyContactRevokeRole`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyContactId: string, companyContactRoleAssignmentId: string` |
| **Request** | `mutation companyContactRevokeRole($companyContactId: ID!, $companyContactRoleAssignmentId: ID!)` |
| **Returns** | `CompanyContactRevokeRolePayload` |

### `companyContactRevokeRoles`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyContactId: string, revokeAll?: boolean, roleAssignmentIds?: unknown` |
| **Request** | `mutation companyContactRevokeRoles($companyContactId: ID!, $revokeAll: Boolean, $roleAssignmentIds: String)` |
| **Returns** | `CompanyContactRevokeRolesPayload` |

### `companyContactUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyContactId: string, input: CompanyContactInput` |
| **Request** | `mutation companyContactUpdate($companyContactId: ID!, $input: CompanyContactInput!)` |
| **Returns** | `CompanyContactUpdatePayload` |

### `companyContactsDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyContactIds: unknown` |
| **Request** | `mutation companyContactsDelete($companyContactIds: String)` |
| **Returns** | `CompanyContactsDeletePayload` |

### `companyCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CompanyCreateInput` |
| **Request** | `mutation companyCreate($input: CompanyCreateInput!)` |
| **Returns** | `CompanyCreatePayload` |

### `companyDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation companyDelete($id: ID!)` |
| **Returns** | `CompanyDeletePayload` |

### `companyLocationAssignAddress`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `address: CompanyAddressInput, addressTypes: unknown, locationId: string` |
| **Request** | `mutation companyLocationAssignAddress($address: CompanyAddressInput!, $addressTypes: String, $locationId: ID!)` |
| **Returns** | `CompanyLocationAssignAddressPayload` |

### `companyLocationAssignRoles`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationId: string, rolesToAssign: unknown` |
| **Request** | `mutation companyLocationAssignRoles($companyLocationId: ID!, $rolesToAssign: String)` |
| **Returns** | `CompanyLocationAssignRolesPayload` |

### `companyLocationAssignStaffMembers`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationId: string, staffMemberIds: unknown` |
| **Request** | `mutation companyLocationAssignStaffMembers($companyLocationId: ID!, $staffMemberIds: String)` |
| **Returns** | `CompanyLocationAssignStaffMembersPayload` |

### `companyLocationAssignTaxExemptions`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationId: string, taxExemptions: unknown` |
| **Request** | `mutation companyLocationAssignTaxExemptions($companyLocationId: ID!, $taxExemptions: String)` |
| **Returns** | `CompanyLocationAssignTaxExemptionsPayload` |

### `companyLocationCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyId: string, input: CompanyLocationInput` |
| **Request** | `mutation companyLocationCreate($companyId: ID!, $input: CompanyLocationInput!)` |
| **Returns** | `CompanyLocationCreatePayload` |

### `companyLocationCreateTaxRegistration`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locationId: string, taxId: string` |
| **Request** | `mutation companyLocationCreateTaxRegistration($locationId: ID!, $taxId: String!)` |
| **Returns** | `CompanyLocationCreateTaxRegistrationPayload` |

### `companyLocationDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationId: string` |
| **Request** | `mutation companyLocationDelete($companyLocationId: ID!)` |
| **Returns** | `CompanyLocationDeletePayload` |

### `companyLocationRemoveStaffMembers`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationStaffMemberAssignmentIds: unknown` |
| **Request** | `mutation companyLocationRemoveStaffMembers($companyLocationStaffMemberAssignmentIds: String)` |
| **Returns** | `CompanyLocationRemoveStaffMembersPayload` |

### `companyLocationRevokeRoles`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationId: string, rolesToRevoke: unknown` |
| **Request** | `mutation companyLocationRevokeRoles($companyLocationId: ID!, $rolesToRevoke: String)` |
| **Returns** | `CompanyLocationRevokeRolesPayload` |

### `companyLocationRevokeTaxExemptions`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationId: string, taxExemptions: unknown` |
| **Request** | `mutation companyLocationRevokeTaxExemptions($companyLocationId: ID!, $taxExemptions: String)` |
| **Returns** | `CompanyLocationRevokeTaxExemptionsPayload` |

### `companyLocationRevokeTaxRegistration`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationId: string` |
| **Request** | `mutation companyLocationRevokeTaxRegistration($companyLocationId: ID!)` |
| **Returns** | `CompanyLocationRevokeTaxRegistrationPayload` |

### `companyLocationTaxSettingsUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationId: string, exemptionsToAssign?: unknown, exemptionsToRemove?: unknown, taxExempt?: boolean, taxRegistrationId?: string` |
| **Request** | `mutation companyLocationTaxSettingsUpdate($companyLocationId: ID!, $exemptionsToAssign: String, $exemptionsToRemove: String, $taxExempt: Boolean, $taxRegistrationId: String)` |
| **Returns** | `CompanyLocationTaxSettingsUpdatePayload` |

### `companyLocationUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationId: string, input: CompanyLocationUpdateInput` |
| **Request** | `mutation companyLocationUpdate($companyLocationId: ID!, $input: CompanyLocationUpdateInput!)` |
| **Returns** | `CompanyLocationUpdatePayload` |

### `companyLocationsDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyLocationIds: unknown` |
| **Request** | `mutation companyLocationsDelete($companyLocationIds: String)` |
| **Returns** | `CompanyLocationsDeletePayload` |

### `companyRevokeMainContact`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyId: string` |
| **Request** | `mutation companyRevokeMainContact($companyId: ID!)` |
| **Returns** | `CompanyRevokeMainContactPayload` |

### `companyUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `companyId: string, input: CompanyInput` |
| **Request** | `mutation companyUpdate($companyId: ID!, $input: CompanyInput!)` |
| **Returns** | `CompanyUpdatePayload` |

### `customerAddTaxExemptions`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerId: string, taxExemptions: unknown` |
| **Request** | `mutation customerAddTaxExemptions($customerId: ID!, $taxExemptions: String)` |
| **Returns** | `CustomerAddTaxExemptionsPayload` |

### `customerAddressCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `address: MailingAddressInput, customerId: string, setAsDefault?: boolean` |
| **Request** | `mutation customerAddressCreate($address: MailingAddressInput!, $customerId: ID!, $setAsDefault: Boolean)` |
| **Returns** | `CustomerAddressCreatePayload` |

### `customerAddressDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `addressId: string, customerId: string` |
| **Request** | `mutation customerAddressDelete($addressId: ID!, $customerId: ID!)` |
| **Returns** | `CustomerAddressDeletePayload` |

### `customerAddressUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `address: MailingAddressInput, addressId: string, customerId: string, setAsDefault?: boolean` |
| **Request** | `mutation customerAddressUpdate($address: MailingAddressInput!, $addressId: ID!, $customerId: ID!, $setAsDefault: Boolean)` |
| **Returns** | `CustomerAddressUpdatePayload` |

### `customerCancelDataErasure`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerId: string` |
| **Request** | `mutation customerCancelDataErasure($customerId: ID!)` |
| **Returns** | `CustomerCancelDataErasurePayload` |

### `customerCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CustomerInput` |
| **Request** | `mutation customerCreate($input: CustomerInput!)` |
| **Returns** | `CustomerCreatePayload` |

### `customerDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CustomerDeleteInput` |
| **Request** | `mutation customerDelete($input: CustomerDeleteInput!)` |
| **Returns** | `CustomerDeletePayload` |

### `customerEmailMarketingConsentUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CustomerEmailMarketingConsentUpdateInput` |
| **Request** | `mutation customerEmailMarketingConsentUpdate($input: CustomerEmailMarketingConsentUpdateInput!)` |
| **Returns** | `CustomerEmailMarketingConsentUpdatePayload` |

### `customerGenerateAccountActivationUrl`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerId: string` |
| **Request** | `mutation customerGenerateAccountActivationUrl($customerId: ID!)` |
| **Returns** | `CustomerGenerateAccountActivationUrlPayload` |

### `customerMerge`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerOneId: string, customerTwoId: string, overrideFields?: CustomerMergeOverrideFields` |
| **Request** | `mutation customerMerge($customerOneId: ID!, $customerTwoId: ID!, $overrideFields: CustomerMergeOverrideFields)` |
| **Returns** | `CustomerMergePayload` |

### `customerPaymentMethodCreditCardCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingAddress: MailingAddressInput, customerId: string, sessionId: string` |
| **Request** | `mutation customerPaymentMethodCreditCardCreate($billingAddress: MailingAddressInput!, $customerId: ID!, $sessionId: String!)` |
| **Returns** | `CustomerPaymentMethodCreditCardCreatePayload` |

### `customerPaymentMethodCreditCardUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingAddress: MailingAddressInput, id: string, sessionId: string` |
| **Request** | `mutation customerPaymentMethodCreditCardUpdate($billingAddress: MailingAddressInput!, $id: ID!, $sessionId: String!)` |
| **Returns** | `CustomerPaymentMethodCreditCardUpdatePayload` |

### `customerPaymentMethodGetUpdateUrl`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerPaymentMethodId: string` |
| **Request** | `mutation customerPaymentMethodGetUpdateUrl($customerPaymentMethodId: ID!)` |
| **Returns** | `CustomerPaymentMethodGetUpdateUrlPayload` |

### `customerPaymentMethodPaypalBillingAgreementCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingAddress?: MailingAddressInput, billingAgreementId: string, customerId: string, inactive?: boolean` |
| **Request** | `mutation customerPaymentMethodPaypalBillingAgreementCreate($billingAddress: MailingAddressInput, $billingAgreementId: String!, $customerId: ID!, $inactive: Boolean)` |
| **Returns** | `CustomerPaymentMethodPaypalBillingAgreementCreatePayload` |

### `customerPaymentMethodPaypalBillingAgreementUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingAddress: MailingAddressInput, id: string` |
| **Request** | `mutation customerPaymentMethodPaypalBillingAgreementUpdate($billingAddress: MailingAddressInput!, $id: ID!)` |
| **Returns** | `CustomerPaymentMethodPaypalBillingAgreementUpdatePayload` |

### `customerPaymentMethodRemoteCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerId: string, remoteReference: CustomerPaymentMethodRemoteInput` |
| **Request** | `mutation customerPaymentMethodRemoteCreate($customerId: ID!, $remoteReference: CustomerPaymentMethodRemoteInput!)` |
| **Returns** | `CustomerPaymentMethodRemoteCreatePayload` |

### `customerPaymentMethodRevoke`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerPaymentMethodId: string` |
| **Request** | `mutation customerPaymentMethodRevoke($customerPaymentMethodId: ID!)` |
| **Returns** | `CustomerPaymentMethodRevokePayload` |

### `customerPaymentMethodSendUpdateEmail`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerPaymentMethodId: string, email?: EmailInput` |
| **Request** | `mutation customerPaymentMethodSendUpdateEmail($customerPaymentMethodId: ID!, $email: EmailInput)` |
| **Returns** | `CustomerPaymentMethodSendUpdateEmailPayload` |

### `customerRemoveTaxExemptions`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerId: string, taxExemptions: unknown` |
| **Request** | `mutation customerRemoveTaxExemptions($customerId: ID!, $taxExemptions: String)` |
| **Returns** | `CustomerRemoveTaxExemptionsPayload` |

### `customerReplaceTaxExemptions`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerId: string, taxExemptions: unknown` |
| **Request** | `mutation customerReplaceTaxExemptions($customerId: ID!, $taxExemptions: String)` |
| **Returns** | `CustomerReplaceTaxExemptionsPayload` |

### `customerRequestDataErasure`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerId: string` |
| **Request** | `mutation customerRequestDataErasure($customerId: ID!)` |
| **Returns** | `CustomerRequestDataErasurePayload` |

### `customerSegmentMembersQueryCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CustomerSegmentMembersQueryInput` |
| **Request** | `mutation customerSegmentMembersQueryCreate($input: CustomerSegmentMembersQueryInput!)` |
| **Returns** | `CustomerSegmentMembersQueryCreatePayload` |

### `customerSendAccountInviteEmail`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerId: string, email?: EmailInput` |
| **Request** | `mutation customerSendAccountInviteEmail($customerId: ID!, $email: EmailInput)` |
| **Returns** | `CustomerSendAccountInviteEmailPayload` |

### `customerSet`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `identifier?: CustomerSetIdentifiers, input: CustomerSetInput` |
| **Request** | `mutation customerSet($identifier: CustomerSetIdentifiers, $input: CustomerSetInput!)` |
| **Returns** | `CustomerSetPayload` |

### `customerSmsMarketingConsentUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CustomerSmsMarketingConsentUpdateInput` |
| **Request** | `mutation customerSmsMarketingConsentUpdate($input: CustomerSmsMarketingConsentUpdateInput!)` |
| **Returns** | `CustomerSmsMarketingConsentUpdatePayload` |

### `customerUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CustomerInput` |
| **Request** | `mutation customerUpdate($input: CustomerInput!)` |
| **Returns** | `CustomerUpdatePayload` |

### `customerUpdateDefaultAddress`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `addressId: string, customerId: string` |
| **Request** | `mutation customerUpdateDefaultAddress($addressId: ID!, $customerId: ID!)` |
| **Returns** | `CustomerUpdateDefaultAddressPayload` |

### `segmentCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `name: string, query: string` |
| **Request** | `mutation segmentCreate($name: String!, $query: String!)` |
| **Returns** | `SegmentCreatePayload` |

### `segmentDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation segmentDelete($id: ID!)` |
| **Returns** | `SegmentDeletePayload` |

### `segmentUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, name?: string, query?: string` |
| **Request** | `mutation segmentUpdate($id: ID!, $name: String, $query: String)` |
| **Returns** | `SegmentUpdatePayload` |

### `storeCreditAccountCredit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `creditInput: StoreCreditAccountCreditInput, id: string` |
| **Request** | `mutation storeCreditAccountCredit($creditInput: StoreCreditAccountCreditInput!, $id: ID!)` |
| **Returns** | `StoreCreditAccountCreditPayload` |

### `storeCreditAccountDebit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `debitInput: StoreCreditAccountDebitInput, id: string` |
| **Request** | `mutation storeCreditAccountDebit($debitInput: StoreCreditAccountDebitInput!, $id: ID!)` |
| **Returns** | `StoreCreditAccountDebitPayload` |

### `subscriptionBillingAttemptCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `subscriptionBillingAttemptInput: SubscriptionBillingAttemptInput, subscriptionContractId: string` |
| **Request** | `mutation subscriptionBillingAttemptCreate($subscriptionBillingAttemptInput: SubscriptionBillingAttemptInput!, $subscriptionContractId: ID!)` |
| **Returns** | `SubscriptionBillingAttemptCreatePayload` |

### `subscriptionBillingCycleBulkCharge`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingAttemptExpectedDateRange: SubscriptionBillingCyclesDateRangeSelector, filters?: SubscriptionBillingCycleBulkFilters, inventoryPolicy?: SubscriptionBillingAttemptInventoryPolicy, paymentProcessingPolicy?: SubscriptionBillingAttemptPaymentProcessingPolicy` |
| **Request** | `mutation subscriptionBillingCycleBulkCharge($billingAttemptExpectedDateRange: SubscriptionBillingCyclesDateRangeSelector!, $filters: SubscriptionBillingCycleBulkFilters, $inventoryPolicy: SubscriptionBillingAttemptInventoryPolicy, $paymentProcessingPolicy: SubscriptionBillingAttemptPaymentProcessingPolicy)` |
| **Returns** | `SubscriptionBillingCycleBulkChargePayload` |

### `subscriptionBillingCycleBulkSearch`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingAttemptExpectedDateRange: SubscriptionBillingCyclesDateRangeSelector, filters?: SubscriptionBillingCycleBulkFilters` |
| **Request** | `mutation subscriptionBillingCycleBulkSearch($billingAttemptExpectedDateRange: SubscriptionBillingCyclesDateRangeSelector!, $filters: SubscriptionBillingCycleBulkFilters)` |
| **Returns** | `SubscriptionBillingCycleBulkSearchPayload` |

### `subscriptionBillingCycleCharge`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingCycleSelector: SubscriptionBillingCycleSelector, inventoryPolicy?: SubscriptionBillingAttemptInventoryPolicy, paymentProcessingPolicy?: SubscriptionBillingAttemptPaymentProcessingPolicy, subscriptionContractId: string` |
| **Request** | `mutation subscriptionBillingCycleCharge($billingCycleSelector: SubscriptionBillingCycleSelector!, $inventoryPolicy: SubscriptionBillingAttemptInventoryPolicy, $paymentProcessingPolicy: SubscriptionBillingAttemptPaymentProcessingPolicy, $subscriptionContractId: ID!)` |
| **Returns** | `SubscriptionBillingCycleChargePayload` |

### `subscriptionBillingCycleContractDraftCommit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `draftId: string` |
| **Request** | `mutation subscriptionBillingCycleContractDraftCommit($draftId: ID!)` |
| **Returns** | `SubscriptionBillingCycleContractDraftCommitPayload` |

### `subscriptionBillingCycleContractDraftConcatenate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `concatenatedBillingCycleContracts: unknown, draftId: string` |
| **Request** | `mutation subscriptionBillingCycleContractDraftConcatenate($concatenatedBillingCycleContracts: String, $draftId: ID!)` |
| **Returns** | `SubscriptionBillingCycleContractDraftConcatenatePayload` |

### `subscriptionBillingCycleContractEdit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingCycleInput: SubscriptionBillingCycleInput` |
| **Request** | `mutation subscriptionBillingCycleContractEdit($billingCycleInput: SubscriptionBillingCycleInput!)` |
| **Returns** | `SubscriptionBillingCycleContractEditPayload` |

### `subscriptionBillingCycleEditDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingCycleInput: SubscriptionBillingCycleInput` |
| **Request** | `mutation subscriptionBillingCycleEditDelete($billingCycleInput: SubscriptionBillingCycleInput!)` |
| **Returns** | `SubscriptionBillingCycleEditDeletePayload` |

### `subscriptionBillingCycleEditsDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `contractId: string, targetSelection: SubscriptionBillingCyclesTargetSelection` |
| **Request** | `mutation subscriptionBillingCycleEditsDelete($contractId: ID!, $targetSelection: SubscriptionBillingCyclesTargetSelection!)` |
| **Returns** | `SubscriptionBillingCycleEditsDeletePayload` |

### `subscriptionBillingCycleScheduleEdit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingCycleInput: SubscriptionBillingCycleInput, input: SubscriptionBillingCycleScheduleEditInput` |
| **Request** | `mutation subscriptionBillingCycleScheduleEdit($billingCycleInput: SubscriptionBillingCycleInput!, $input: SubscriptionBillingCycleScheduleEditInput!)` |
| **Returns** | `SubscriptionBillingCycleScheduleEditPayload` |

### `subscriptionBillingCycleSkip`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingCycleInput: SubscriptionBillingCycleInput` |
| **Request** | `mutation subscriptionBillingCycleSkip($billingCycleInput: SubscriptionBillingCycleInput!)` |
| **Returns** | `SubscriptionBillingCycleSkipPayload` |

### `subscriptionBillingCycleUnskip`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `billingCycleInput: SubscriptionBillingCycleInput` |
| **Request** | `mutation subscriptionBillingCycleUnskip($billingCycleInput: SubscriptionBillingCycleInput!)` |
| **Returns** | `SubscriptionBillingCycleUnskipPayload` |

### `subscriptionContractActivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `subscriptionContractId: string` |
| **Request** | `mutation subscriptionContractActivate($subscriptionContractId: ID!)` |
| **Returns** | `SubscriptionContractActivatePayload` |

### `subscriptionContractAtomicCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: SubscriptionContractAtomicCreateInput` |
| **Request** | `mutation subscriptionContractAtomicCreate($input: SubscriptionContractAtomicCreateInput!)` |
| **Returns** | `SubscriptionContractAtomicCreatePayload` |

### `subscriptionContractCancel`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `subscriptionContractId: string` |
| **Request** | `mutation subscriptionContractCancel($subscriptionContractId: ID!)` |
| **Returns** | `SubscriptionContractCancelPayload` |

### `subscriptionContractCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: SubscriptionContractCreateInput` |
| **Request** | `mutation subscriptionContractCreate($input: SubscriptionContractCreateInput!)` |
| **Returns** | `SubscriptionContractCreatePayload` |

### `subscriptionContractExpire`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `subscriptionContractId: string` |
| **Request** | `mutation subscriptionContractExpire($subscriptionContractId: ID!)` |
| **Returns** | `SubscriptionContractExpirePayload` |

### `subscriptionContractFail`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `subscriptionContractId: string` |
| **Request** | `mutation subscriptionContractFail($subscriptionContractId: ID!)` |
| **Returns** | `SubscriptionContractFailPayload` |

### `subscriptionContractPause`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `subscriptionContractId: string` |
| **Request** | `mutation subscriptionContractPause($subscriptionContractId: ID!)` |
| **Returns** | `SubscriptionContractPausePayload` |

### `subscriptionContractProductChange`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: SubscriptionContractProductChangeInput, lineId: string, subscriptionContractId: string` |
| **Request** | `mutation subscriptionContractProductChange($input: SubscriptionContractProductChangeInput!, $lineId: ID!, $subscriptionContractId: ID!)` |
| **Returns** | `SubscriptionContractProductChangePayload` |

### `subscriptionContractSetNextBillingDate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `contractId: string, date: string` |
| **Request** | `mutation subscriptionContractSetNextBillingDate($contractId: ID!, $date: DateTime!)` |
| **Returns** | `SubscriptionContractSetNextBillingDatePayload` |

### `subscriptionContractUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `contractId: string` |
| **Request** | `mutation subscriptionContractUpdate($contractId: ID!)` |
| **Returns** | `SubscriptionContractUpdatePayload` |

### `subscriptionDraftCommit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `draftId: string` |
| **Request** | `mutation subscriptionDraftCommit($draftId: ID!)` |
| **Returns** | `SubscriptionDraftCommitPayload` |

### `subscriptionDraftDiscountAdd`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `draftId: string, input: SubscriptionManualDiscountInput` |
| **Request** | `mutation subscriptionDraftDiscountAdd($draftId: ID!, $input: SubscriptionManualDiscountInput!)` |
| **Returns** | `SubscriptionDraftDiscountAddPayload` |

### `subscriptionDraftDiscountCodeApply`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `draftId: string, redeemCode: string` |
| **Request** | `mutation subscriptionDraftDiscountCodeApply($draftId: ID!, $redeemCode: String!)` |
| **Returns** | `SubscriptionDraftDiscountCodeApplyPayload` |

### `subscriptionDraftDiscountRemove`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `discountId: string, draftId: string` |
| **Request** | `mutation subscriptionDraftDiscountRemove($discountId: ID!, $draftId: ID!)` |
| **Returns** | `SubscriptionDraftDiscountRemovePayload` |

### `subscriptionDraftDiscountUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `discountId: string, draftId: string, input: SubscriptionManualDiscountInput` |
| **Request** | `mutation subscriptionDraftDiscountUpdate($discountId: ID!, $draftId: ID!, $input: SubscriptionManualDiscountInput!)` |
| **Returns** | `SubscriptionDraftDiscountUpdatePayload` |

### `subscriptionDraftFreeShippingDiscountAdd`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `draftId: string, input: SubscriptionFreeShippingDiscountInput` |
| **Request** | `mutation subscriptionDraftFreeShippingDiscountAdd($draftId: ID!, $input: SubscriptionFreeShippingDiscountInput!)` |
| **Returns** | `SubscriptionDraftFreeShippingDiscountAddPayload` |

### `subscriptionDraftFreeShippingDiscountUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `discountId: string, draftId: string, input: SubscriptionFreeShippingDiscountInput` |
| **Request** | `mutation subscriptionDraftFreeShippingDiscountUpdate($discountId: ID!, $draftId: ID!, $input: SubscriptionFreeShippingDiscountInput!)` |
| **Returns** | `SubscriptionDraftFreeShippingDiscountUpdatePayload` |

### `subscriptionDraftLineAdd`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `draftId: string, input: SubscriptionLineInput` |
| **Request** | `mutation subscriptionDraftLineAdd($draftId: ID!, $input: SubscriptionLineInput!)` |
| **Returns** | `SubscriptionDraftLineAddPayload` |

### `subscriptionDraftLineRemove`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `draftId: string, lineId: string` |
| **Request** | `mutation subscriptionDraftLineRemove($draftId: ID!, $lineId: ID!)` |
| **Returns** | `SubscriptionDraftLineRemovePayload` |

### `subscriptionDraftLineUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `draftId: string, input: SubscriptionLineUpdateInput, lineId: string` |
| **Request** | `mutation subscriptionDraftLineUpdate($draftId: ID!, $input: SubscriptionLineUpdateInput!, $lineId: ID!)` |
| **Returns** | `SubscriptionDraftLineUpdatePayload` |

### `subscriptionDraftUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `draftId: string, input: SubscriptionDraftInput` |
| **Request** | `mutation subscriptionDraftUpdate($draftId: ID!, $input: SubscriptionDraftInput!)` |
| **Returns** | `SubscriptionDraftUpdatePayload` |

---

## Discounts & Marketing

### `abandonedCheckouts`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: AbandonedCheckoutSortKeys` |
| **Request** | `query abandonedCheckouts($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: AbandonedCheckoutSortKeys)` |
| **Returns** | `AbandonedCheckoutConnection` |

### `abandonedCheckoutsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string, savedSearchId?: string` |
| **Request** | `query abandonedCheckoutsCount($limit: Int, $query: String, $savedSearchId: ID)` |
| **Returns** | `Count | null` |

### `abandonment`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query abandonment($id: ID!)` |
| **Returns** | `Abandonment | null` |

### `abandonmentByAbandonedCheckoutId`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `abandonedCheckoutId: string` |
| **Request** | `query abandonmentByAbandonedCheckoutId($abandonedCheckoutId: ID!)` |
| **Returns** | `Abandonment | null` |

### `automaticDiscount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query automaticDiscount($id: ID!)` |
| **Returns** | `DiscountAutomatic | null` |

### `automaticDiscountNode`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query automaticDiscountNode($id: ID!)` |
| **Returns** | `DiscountAutomaticNode | null` |

### `automaticDiscountNodes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: AutomaticDiscountSortKeys` |
| **Request** | `query automaticDiscountNodes($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: AutomaticDiscountSortKeys)` |
| **Returns** | `DiscountAutomaticNodeConnection` |

### `automaticDiscountSavedSearches`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query automaticDiscountSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `SavedSearchConnection` |

### `automaticDiscounts`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: AutomaticDiscountSortKeys` |
| **Request** | `query automaticDiscounts($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: AutomaticDiscountSortKeys)` |
| **Returns** | `DiscountAutomaticConnection` |

### `codeDiscountNode`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query codeDiscountNode($id: ID!)` |
| **Returns** | `DiscountCodeNode | null` |

### `codeDiscountNodeByCode`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `code: string` |
| **Request** | `query codeDiscountNodeByCode($code: String!)` |
| **Returns** | `DiscountCodeNode | null` |

### `codeDiscountNodes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: CodeDiscountSortKeys` |
| **Request** | `query codeDiscountNodes($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: CodeDiscountSortKeys)` |
| **Returns** | `DiscountCodeNodeConnection` |

### `codeDiscountSavedSearches`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query codeDiscountSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `SavedSearchConnection` |

### `discountCodesCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string` |
| **Request** | `query discountCodesCount($limit: Int, $query: String)` |
| **Returns** | `Count | null` |

### `discountNode`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query discountNode($id: ID!)` |
| **Returns** | `DiscountNode | null` |

### `discountNodes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: DiscountSortKeys` |
| **Request** | `query discountNodes($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: DiscountSortKeys)` |
| **Returns** | `DiscountNodeConnection` |

### `discountNodesCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string, savedSearchId?: string` |
| **Request** | `query discountNodesCount($limit: Int, $query: String, $savedSearchId: ID)` |
| **Returns** | `Count | null` |

### `discountRedeemCodeBulkCreation`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query discountRedeemCodeBulkCreation($id: ID!)` |
| **Returns** | `DiscountRedeemCodeBulkCreation | null` |

### `discountRedeemCodeSavedSearches`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: DiscountCodeSortKeys` |
| **Request** | `query discountRedeemCodeSavedSearches($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: DiscountCodeSortKeys)` |
| **Returns** | `SavedSearchConnection` |

### `discountTags`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: DiscountTagSortKeys` |
| **Request** | `query discountTags($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: DiscountTagSortKeys)` |
| **Returns** | `StringConnection` |

### `marketingActivities`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, marketingActivityIds?: unknown, query?: string, remoteIds?: unknown, reverse?: boolean, savedSearchId?: string, sortKey?: MarketingActivitySortKeys, utm?: UTMInput` |
| **Request** | `query marketingActivities($after: String, $before: String, $first: Int, $last: Int, $marketingActivityIds: String, $query: String, $remoteIds: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: MarketingActivitySortKeys, $utm: UTMInput)` |
| **Returns** | `MarketingActivityConnection` |

### `marketingActivity`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query marketingActivity($id: ID!)` |
| **Returns** | `MarketingActivity | null` |

### `marketingEvent`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query marketingEvent($id: ID!)` |
| **Returns** | `MarketingEvent | null` |

### `marketingEvents`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: MarketingEventSortKeys` |
| **Request** | `query marketingEvents($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: MarketingEventSortKeys)` |
| **Returns** | `MarketingEventConnection` |

### `priceList`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query priceList($id: ID!)` |
| **Returns** | `PriceList | null` |

### `priceLists`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean, sortKey?: PriceListSortKeys` |
| **Request** | `query priceLists($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean, $sortKey: PriceListSortKeys)` |
| **Returns** | `PriceListConnection` |

### `abandonmentEmailStateUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `emailSentAt?: string, emailState: AbandonmentEmailState, emailStateChangeReason?: string, id: string` |
| **Request** | `mutation abandonmentEmailStateUpdate($emailSentAt: DateTime, $emailState: AbandonmentEmailState!, $emailStateChangeReason: String, $id: ID!)` |
| **Returns** | `AbandonmentEmailStateUpdatePayload` |

### `abandonmentUpdateActivitiesDeliveryStatuses`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `abandonmentId: string, deliveredAt?: string, deliveryStatus: AbandonmentDeliveryState, deliveryStatusChangeReason?: string, marketingActivityId: string` |
| **Request** | `mutation abandonmentUpdateActivitiesDeliveryStatuses($abandonmentId: ID!, $deliveredAt: DateTime, $deliveryStatus: AbandonmentDeliveryState!, $deliveryStatusChangeReason: String, $marketingActivityId: ID!)` |
| **Returns** | `AbandonmentUpdateActivitiesDeliveryStatusesPayload` |

### `discountAutomaticActivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation discountAutomaticActivate($id: ID!)` |
| **Returns** | `DiscountAutomaticActivatePayload` |

### `discountAutomaticAppCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `automaticAppDiscount: DiscountAutomaticAppInput` |
| **Request** | `mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!)` |
| **Returns** | `DiscountAutomaticAppCreatePayload` |

### `discountAutomaticAppUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `automaticAppDiscount: DiscountAutomaticAppInput, id: string` |
| **Request** | `mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!)` |
| **Returns** | `DiscountAutomaticAppUpdatePayload` |

### `discountAutomaticBasicCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `automaticBasicDiscount: DiscountAutomaticBasicInput` |
| **Request** | `mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!)` |
| **Returns** | `DiscountAutomaticBasicCreatePayload` |

### `discountAutomaticBasicUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `automaticBasicDiscount: DiscountAutomaticBasicInput, id: string` |
| **Request** | `mutation discountAutomaticBasicUpdate($automaticBasicDiscount: DiscountAutomaticBasicInput!, $id: ID!)` |
| **Returns** | `DiscountAutomaticBasicUpdatePayload` |

### `discountAutomaticBulkDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids?: unknown, savedSearchId?: string, search?: string` |
| **Request** | `mutation discountAutomaticBulkDelete($ids: String, $savedSearchId: ID, $search: String)` |
| **Returns** | `DiscountAutomaticBulkDeletePayload` |

### `discountAutomaticBxgyCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `automaticBxgyDiscount: DiscountAutomaticBxgyInput` |
| **Request** | `mutation discountAutomaticBxgyCreate($automaticBxgyDiscount: DiscountAutomaticBxgyInput!)` |
| **Returns** | `DiscountAutomaticBxgyCreatePayload` |

### `discountAutomaticBxgyUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `automaticBxgyDiscount: DiscountAutomaticBxgyInput, id: string` |
| **Request** | `mutation discountAutomaticBxgyUpdate($automaticBxgyDiscount: DiscountAutomaticBxgyInput!, $id: ID!)` |
| **Returns** | `DiscountAutomaticBxgyUpdatePayload` |

### `discountAutomaticDeactivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation discountAutomaticDeactivate($id: ID!)` |
| **Returns** | `DiscountAutomaticDeactivatePayload` |

### `discountAutomaticDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation discountAutomaticDelete($id: ID!)` |
| **Returns** | `DiscountAutomaticDeletePayload` |

### `discountAutomaticFreeShippingCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput` |
| **Request** | `mutation discountAutomaticFreeShippingCreate($freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput!)` |
| **Returns** | `DiscountAutomaticFreeShippingCreatePayload` |

### `discountAutomaticFreeShippingUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput, id: string` |
| **Request** | `mutation discountAutomaticFreeShippingUpdate($freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput!, $id: ID!)` |
| **Returns** | `DiscountAutomaticFreeShippingUpdatePayload` |

### `discountBulkTagsAdd`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids?: unknown, savedSearchId?: string, search?: string, tags: unknown` |
| **Request** | `mutation discountBulkTagsAdd($ids: String, $savedSearchId: ID, $search: String, $tags: String)` |
| **Returns** | `DiscountBulkTagsAddPayload` |

### `discountBulkTagsRemove`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids?: unknown, savedSearchId?: string, search?: string, tags: unknown` |
| **Request** | `mutation discountBulkTagsRemove($ids: String, $savedSearchId: ID, $search: String, $tags: String)` |
| **Returns** | `DiscountBulkTagsRemovePayload` |

### `discountCodeActivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation discountCodeActivate($id: ID!)` |
| **Returns** | `DiscountCodeActivatePayload` |

### `discountCodeAppCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `codeAppDiscount: DiscountCodeAppInput` |
| **Request** | `mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!)` |
| **Returns** | `DiscountCodeAppCreatePayload` |

### `discountCodeAppUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `codeAppDiscount: DiscountCodeAppInput, id: string` |
| **Request** | `mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!)` |
| **Returns** | `DiscountCodeAppUpdatePayload` |

### `discountCodeBasicCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `basicCodeDiscount: DiscountCodeBasicInput` |
| **Request** | `mutation discountCodeBasicCreate($basicCodeDiscount: DiscountCodeBasicInput!)` |
| **Returns** | `DiscountCodeBasicCreatePayload` |

### `discountCodeBasicUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `basicCodeDiscount: DiscountCodeBasicInput, id: string` |
| **Request** | `mutation discountCodeBasicUpdate($basicCodeDiscount: DiscountCodeBasicInput!, $id: ID!)` |
| **Returns** | `DiscountCodeBasicUpdatePayload` |

### `discountCodeBulkActivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids?: unknown, savedSearchId?: string, search?: string` |
| **Request** | `mutation discountCodeBulkActivate($ids: String, $savedSearchId: ID, $search: String)` |
| **Returns** | `DiscountCodeBulkActivatePayload` |

### `discountCodeBulkDeactivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids?: unknown, savedSearchId?: string, search?: string` |
| **Request** | `mutation discountCodeBulkDeactivate($ids: String, $savedSearchId: ID, $search: String)` |
| **Returns** | `DiscountCodeBulkDeactivatePayload` |

### `discountCodeBulkDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids?: unknown, savedSearchId?: string, search?: string` |
| **Request** | `mutation discountCodeBulkDelete($ids: String, $savedSearchId: ID, $search: String)` |
| **Returns** | `DiscountCodeBulkDeletePayload` |

### `discountCodeBxgyCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `bxgyCodeDiscount: DiscountCodeBxgyInput` |
| **Request** | `mutation discountCodeBxgyCreate($bxgyCodeDiscount: DiscountCodeBxgyInput!)` |
| **Returns** | `DiscountCodeBxgyCreatePayload` |

### `discountCodeBxgyUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `bxgyCodeDiscount: DiscountCodeBxgyInput, id: string` |
| **Request** | `mutation discountCodeBxgyUpdate($bxgyCodeDiscount: DiscountCodeBxgyInput!, $id: ID!)` |
| **Returns** | `DiscountCodeBxgyUpdatePayload` |

### `discountCodeDeactivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation discountCodeDeactivate($id: ID!)` |
| **Returns** | `DiscountCodeDeactivatePayload` |

### `discountCodeDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation discountCodeDelete($id: ID!)` |
| **Returns** | `DiscountCodeDeletePayload` |

### `discountCodeFreeShippingCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `freeShippingCodeDiscount: DiscountCodeFreeShippingInput` |
| **Request** | `mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!)` |
| **Returns** | `DiscountCodeFreeShippingCreatePayload` |

### `discountCodeFreeShippingUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `freeShippingCodeDiscount: DiscountCodeFreeShippingInput, id: string` |
| **Request** | `mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!)` |
| **Returns** | `DiscountCodeFreeShippingUpdatePayload` |

### `discountCodeRedeemCodeBulkDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `discountId: string, ids?: DiscountRedeemCode, savedSearchId?: string, search?: string` |
| **Request** | `mutation discountCodeRedeemCodeBulkDelete($discountId: ID!, $ids: DiscountRedeemCode, $savedSearchId: ID, $search: String)` |
| **Returns** | `DiscountCodeRedeemCodeBulkDeletePayload` |

### `discountRedeemCodeBulkAdd`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `codes: unknown, discountId: string` |
| **Request** | `mutation discountRedeemCodeBulkAdd($codes: String, $discountId: ID!)` |
| **Returns** | `DiscountRedeemCodeBulkAddPayload` |

### `marketingActivitiesDeleteAllExternal`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | _(none)_ |
| **Request** | `mutation marketingActivitiesDeleteAllExternal` |
| **Returns** | `MarketingActivitiesDeleteAllExternalPayload` |

### `marketingActivityCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: MarketingActivityCreateInput` |
| **Request** | `mutation marketingActivityCreate($input: MarketingActivityCreateInput!)` |
| **Returns** | `MarketingActivityCreatePayload` |

### `marketingActivityCreateExternal`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: MarketingActivityCreateExternalInput` |
| **Request** | `mutation marketingActivityCreateExternal($input: MarketingActivityCreateExternalInput!)` |
| **Returns** | `MarketingActivityCreateExternalPayload` |

### `marketingActivityDeleteExternal`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `marketingActivityId?: string, remoteId?: string` |
| **Request** | `mutation marketingActivityDeleteExternal($marketingActivityId: ID, $remoteId: String)` |
| **Returns** | `MarketingActivityDeleteExternalPayload` |

### `marketingActivityUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: MarketingActivityUpdateInput` |
| **Request** | `mutation marketingActivityUpdate($input: MarketingActivityUpdateInput!)` |
| **Returns** | `MarketingActivityUpdatePayload` |

### `marketingActivityUpdateExternal`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: MarketingActivityUpdateExternalInput, marketingActivityId?: string, remoteId?: string, utm?: UTMInput` |
| **Request** | `mutation marketingActivityUpdateExternal($input: MarketingActivityUpdateExternalInput!, $marketingActivityId: ID, $remoteId: String, $utm: UTMInput)` |
| **Returns** | `MarketingActivityUpdateExternalPayload` |

### `marketingActivityUpsertExternal`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: MarketingActivityUpsertExternalInput` |
| **Request** | `mutation marketingActivityUpsertExternal($input: MarketingActivityUpsertExternalInput!)` |
| **Returns** | `MarketingActivityUpsertExternalPayload` |

### `marketingEngagementCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `channelHandle?: string, marketingActivityId?: string, marketingEngagement: MarketingEngagementInput, remoteId?: string` |
| **Request** | `mutation marketingEngagementCreate($channelHandle: String, $marketingActivityId: ID, $marketingEngagement: MarketingEngagementInput!, $remoteId: String)` |
| **Returns** | `MarketingEngagementCreatePayload` |

### `marketingEngagementsDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `channelHandle?: string, deleteEngagementsForAllChannels?: boolean` |
| **Request** | `mutation marketingEngagementsDelete($channelHandle: String, $deleteEngagementsForAllChannels: Boolean)` |
| **Returns** | `MarketingEngagementsDeletePayload` |

### `priceListCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: PriceListCreateInput` |
| **Request** | `mutation priceListCreate($input: PriceListCreateInput!)` |
| **Returns** | `PriceListCreatePayload` |

### `priceListDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation priceListDelete($id: ID!)` |
| **Returns** | `PriceListDeletePayload` |

### `priceListFixedPricesAdd`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `priceListId: string, prices: unknown` |
| **Request** | `mutation priceListFixedPricesAdd($priceListId: ID!, $prices: String)` |
| **Returns** | `PriceListFixedPricesAddPayload` |

### `priceListFixedPricesByProductUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `priceListId: string, pricesToAdd?: unknown, pricesToDeleteByProductIds?: unknown` |
| **Request** | `mutation priceListFixedPricesByProductUpdate($priceListId: ID!, $pricesToAdd: String, $pricesToDeleteByProductIds: String)` |
| **Returns** | `PriceListFixedPricesByProductUpdatePayload` |

### `priceListFixedPricesDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `priceListId: string, variantIds: unknown` |
| **Request** | `mutation priceListFixedPricesDelete($priceListId: ID!, $variantIds: String)` |
| **Returns** | `PriceListFixedPricesDeletePayload` |

### `priceListFixedPricesUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `priceListId: string, pricesToAdd: unknown, variantIdsToDelete: unknown` |
| **Request** | `mutation priceListFixedPricesUpdate($priceListId: ID!, $pricesToAdd: String, $variantIdsToDelete: String)` |
| **Returns** | `PriceListFixedPricesUpdatePayload` |

### `priceListUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: PriceListUpdateInput` |
| **Request** | `mutation priceListUpdate($id: ID!, $input: PriceListUpdateInput!)` |
| **Returns** | `PriceListUpdatePayload` |

### `quantityPricingByVariantUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: QuantityPricingByVariantUpdateInput, priceListId: string` |
| **Request** | `mutation quantityPricingByVariantUpdate($input: QuantityPricingByVariantUpdateInput!, $priceListId: ID!)` |
| **Returns** | `QuantityPricingByVariantUpdatePayload` |

### `quantityRulesAdd`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `priceListId: string, quantityRules: unknown` |
| **Request** | `mutation quantityRulesAdd($priceListId: ID!, $quantityRules: String)` |
| **Returns** | `QuantityRulesAddPayload` |

### `quantityRulesDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `priceListId: string, variantIds: unknown` |
| **Request** | `mutation quantityRulesDelete($priceListId: ID!, $variantIds: String)` |
| **Returns** | `QuantityRulesDeletePayload` |

---

## Inventory

### `inventoryItem`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query inventoryItem($id: ID!)` |
| **Returns** | `InventoryItem | null` |

### `inventoryItems`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean` |
| **Request** | `query inventoryItems($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean)` |
| **Returns** | `InventoryItemConnection` |

### `inventoryLevel`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query inventoryLevel($id: ID!)` |
| **Returns** | `InventoryLevel | null` |

### `inventoryProperties`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query inventoryProperties` |
| **Returns** | `InventoryProperties | null` |

### `inventoryShipment`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query inventoryShipment($id: ID!)` |
| **Returns** | `InventoryShipment | null` |

### `inventoryShipments`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, sortKey?: InventoryShipmentSortKeys` |
| **Request** | `query inventoryShipments($after: String, $before: String, $first: Int, $last: Int, $query: String, $sortKey: InventoryShipmentSortKeys)` |
| **Returns** | `InventoryShipmentConnection` |

### `inventoryTransfer`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query inventoryTransfer($id: ID!)` |
| **Returns** | `InventoryTransfer | null` |

### `inventoryTransfers`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: TransferSortKeys` |
| **Request** | `query inventoryTransfers($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: TransferSortKeys)` |
| **Returns** | `InventoryTransferConnection` |

### `location`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id?: string` |
| **Request** | `query location($id: ID)` |
| **Returns** | `Location | null` |

### `locationByIdentifier`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `identifier: LocationIdentifierInput` |
| **Request** | `query locationByIdentifier($identifier: LocationIdentifierInput!)` |
| **Returns** | `Location | null` |

### `locations`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, includeInactive?: boolean, includeLegacy?: boolean, last?: number, query?: string, reverse?: boolean, sortKey?: LocationSortKeys` |
| **Request** | `query locations($after: String, $before: String, $first: Int, $includeInactive: Boolean, $includeLegacy: Boolean, $last: Int, $query: String, $reverse: Boolean, $sortKey: LocationSortKeys)` |
| **Returns** | `LocationConnection` |

### `locationsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string` |
| **Request** | `query locationsCount($limit: Int, $query: String)` |
| **Returns** | `Count | null` |

### `inventoryActivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `available?: number, inventoryItemId: string, locationId: string, onHand?: number, stockAtLegacyLocation?: boolean` |
| **Request** | `mutation inventoryActivate($available: Int, $inventoryItemId: ID!, $locationId: ID!, $onHand: Int, $stockAtLegacyLocation: Boolean)` |
| **Returns** | `InventoryActivatePayload` |

### `inventoryAdjustQuantities`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventoryAdjustQuantitiesInput` |
| **Request** | `mutation inventoryAdjustQuantities($input: InventoryAdjustQuantitiesInput!)` |
| **Returns** | `InventoryAdjustQuantitiesPayload` |

### `inventoryBulkToggleActivation`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `inventoryItemId: string, inventoryItemUpdates: unknown` |
| **Request** | `mutation inventoryBulkToggleActivation($inventoryItemId: ID!, $inventoryItemUpdates: String)` |
| **Returns** | `InventoryBulkToggleActivationPayload` |

### `inventoryDeactivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `inventoryLevelId: string` |
| **Request** | `mutation inventoryDeactivate($inventoryLevelId: ID!)` |
| **Returns** | `InventoryDeactivatePayload` |

### `inventoryItemUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: InventoryItemInput` |
| **Request** | `mutation inventoryItemUpdate($id: ID!, $input: InventoryItemInput!)` |
| **Returns** | `InventoryItemUpdatePayload` |

### `inventoryMoveQuantities`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventoryMoveQuantitiesInput` |
| **Request** | `mutation inventoryMoveQuantities($input: InventoryMoveQuantitiesInput!)` |
| **Returns** | `InventoryMoveQuantitiesPayload` |

### `inventorySetOnHandQuantities`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventorySetOnHandQuantitiesInput` |
| **Request** | `mutation inventorySetOnHandQuantities($input: InventorySetOnHandQuantitiesInput!)` |
| **Returns** | `InventorySetOnHandQuantitiesPayload` |

### `inventorySetQuantities`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventorySetQuantitiesInput` |
| **Request** | `mutation inventorySetQuantities($input: InventorySetQuantitiesInput!)` |
| **Returns** | `InventorySetQuantitiesPayload` |

### `inventorySetScheduledChanges`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventorySetScheduledChangesInput` |
| **Request** | `mutation inventorySetScheduledChanges($input: InventorySetScheduledChangesInput!)` |
| **Returns** | `InventorySetScheduledChangesPayload` |

### `inventoryShipmentAddItems`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, lineItems: unknown` |
| **Request** | `mutation inventoryShipmentAddItems($id: ID!, $lineItems: String)` |
| **Returns** | `InventoryShipmentAddItemsPayload` |

### `inventoryShipmentCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventoryShipmentCreateInput` |
| **Request** | `mutation inventoryShipmentCreate($input: InventoryShipmentCreateInput!)` |
| **Returns** | `InventoryShipmentCreatePayload` |

### `inventoryShipmentCreateInTransit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventoryShipmentCreateInput` |
| **Request** | `mutation inventoryShipmentCreateInTransit($input: InventoryShipmentCreateInput!)` |
| **Returns** | `InventoryShipmentCreateInTransitPayload` |

### `inventoryShipmentDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation inventoryShipmentDelete($id: ID!)` |
| **Returns** | `InventoryShipmentDeletePayload` |

### `inventoryShipmentMarkInTransit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `dateShipped?: string, id: string` |
| **Request** | `mutation inventoryShipmentMarkInTransit($dateShipped: DateTime, $id: ID!)` |
| **Returns** | `InventoryShipmentMarkInTransitPayload` |

### `inventoryShipmentReceive`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `bulkReceiveAction?: InventoryShipmentReceiveLineItemReason, dateReceived?: string, id: string, lineItems?: unknown` |
| **Request** | `mutation inventoryShipmentReceive($bulkReceiveAction: InventoryShipmentReceiveLineItemReason, $dateReceived: DateTime, $id: ID!, $lineItems: String)` |
| **Returns** | `InventoryShipmentReceivePayload` |

### `inventoryShipmentRemoveItems`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, lineItems: unknown` |
| **Request** | `mutation inventoryShipmentRemoveItems($id: ID!, $lineItems: String)` |
| **Returns** | `InventoryShipmentRemoveItemsPayload` |

### `inventoryShipmentSetBarcode`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `barcode: string, id: string` |
| **Request** | `mutation inventoryShipmentSetBarcode($barcode: String!, $id: ID!)` |
| **Returns** | `InventoryShipmentSetBarcodePayload` |

### `inventoryShipmentSetTracking`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, tracking: InventoryShipmentTrackingInput` |
| **Request** | `mutation inventoryShipmentSetTracking($id: ID!, $tracking: InventoryShipmentTrackingInput!)` |
| **Returns** | `InventoryShipmentSetTrackingPayload` |

### `inventoryShipmentUpdateItemQuantities`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, items?: unknown` |
| **Request** | `mutation inventoryShipmentUpdateItemQuantities($id: ID!, $items: String)` |
| **Returns** | `InventoryShipmentUpdateItemQuantitiesPayload` |

### `inventoryTransferCancel`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation inventoryTransferCancel($id: ID!)` |
| **Returns** | `InventoryTransferCancelPayload` |

### `inventoryTransferCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventoryTransferCreateInput` |
| **Request** | `mutation inventoryTransferCreate($input: InventoryTransferCreateInput!)` |
| **Returns** | `InventoryTransferCreatePayload` |

### `inventoryTransferCreateAsReadyToShip`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventoryTransferCreateAsReadyToShipInput` |
| **Request** | `mutation inventoryTransferCreateAsReadyToShip($input: InventoryTransferCreateAsReadyToShipInput!)` |
| **Returns** | `InventoryTransferCreateAsReadyToShipPayload` |

### `inventoryTransferDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation inventoryTransferDelete($id: ID!)` |
| **Returns** | `InventoryTransferDeletePayload` |

### `inventoryTransferDuplicate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation inventoryTransferDuplicate($id: ID!)` |
| **Returns** | `InventoryTransferDuplicatePayload` |

### `inventoryTransferEdit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: InventoryTransferEditInput` |
| **Request** | `mutation inventoryTransferEdit($id: ID!, $input: InventoryTransferEditInput!)` |
| **Returns** | `InventoryTransferEditPayload` |

### `inventoryTransferMarkAsReadyToShip`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation inventoryTransferMarkAsReadyToShip($id: ID!)` |
| **Returns** | `InventoryTransferMarkAsReadyToShipPayload` |

### `inventoryTransferRemoveItems`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventoryTransferRemoveItemsInput` |
| **Request** | `mutation inventoryTransferRemoveItems($input: InventoryTransferRemoveItemsInput!)` |
| **Returns** | `InventoryTransferRemoveItemsPayload` |

### `inventoryTransferSetItems`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: InventoryTransferSetItemsInput` |
| **Request** | `mutation inventoryTransferSetItems($input: InventoryTransferSetItemsInput!)` |
| **Returns** | `InventoryTransferSetItemsPayload` |

### `locationActivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locationId: string` |
| **Request** | `mutation locationActivate($locationId: ID!)` |
| **Returns** | `LocationActivatePayload` |

### `locationAdd`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: LocationAddInput` |
| **Request** | `mutation locationAdd($input: LocationAddInput!)` |
| **Returns** | `LocationAddPayload` |

### `locationDeactivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `destinationLocationId?: string, locationId: string` |
| **Request** | `mutation locationDeactivate($destinationLocationId: ID, $locationId: ID!)` |
| **Returns** | `LocationDeactivatePayload` |

### `locationDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locationId: string` |
| **Request** | `mutation locationDelete($locationId: ID!)` |
| **Returns** | `LocationDeletePayload` |

### `locationEdit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: LocationEditInput` |
| **Request** | `mutation locationEdit($id: ID!, $input: LocationEditInput!)` |
| **Returns** | `LocationEditPayload` |

### `locationLocalPickupDisable`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locationId: string` |
| **Request** | `mutation locationLocalPickupDisable($locationId: ID!)` |
| **Returns** | `LocationLocalPickupDisablePayload` |

### `locationLocalPickupEnable`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `localPickupSettings: DeliveryLocationLocalPickupEnableInput` |
| **Request** | `mutation locationLocalPickupEnable($localPickupSettings: DeliveryLocationLocalPickupEnableInput!)` |
| **Returns** | `LocationLocalPickupEnablePayload` |

---

## Orders

### `dispute`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query dispute($id: ID!)` |
| **Returns** | `ShopifyPaymentsDispute | null` |

### `disputeEvidence`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query disputeEvidence($id: ID!)` |
| **Returns** | `ShopifyPaymentsDisputeEvidence | null` |

### `disputes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean` |
| **Request** | `query disputes($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean)` |
| **Returns** | `ShopifyPaymentsDisputeConnection` |

### `draftOrder`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query draftOrder($id: ID!)` |
| **Returns** | `DraftOrder | null` |

### `draftOrderAvailableDeliveryOptions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `input: DraftOrderAvailableDeliveryOptionsInput, localPickupCount?: number, localPickupFrom?: number, search?: string, sessionToken?: string` |
| **Request** | `query draftOrderAvailableDeliveryOptions($input: DraftOrderAvailableDeliveryOptionsInput!, $localPickupCount: Int, $localPickupFrom: Int, $search: String, $sessionToken: String)` |
| **Returns** | `DraftOrderAvailableDeliveryOptions | null` |

### `draftOrderSavedSearches`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query draftOrderSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `SavedSearchConnection` |

### `draftOrderTag`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query draftOrderTag($id: ID!)` |
| **Returns** | `DraftOrderTag | null` |

### `draftOrders`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: DraftOrderSortKeys` |
| **Request** | `query draftOrders($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: DraftOrderSortKeys)` |
| **Returns** | `DraftOrderConnection` |

### `draftOrdersCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string, savedSearchId?: string` |
| **Request** | `query draftOrdersCount($limit: Int, $query: String, $savedSearchId: ID)` |
| **Returns** | `Count | null` |

### `giftCard`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query giftCard($id: ID!)` |
| **Returns** | `GiftCard | null` |

### `giftCardConfiguration`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query giftCardConfiguration` |
| **Returns** | `GiftCardConfiguration | null` |

### `giftCards`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: GiftCardSortKeys` |
| **Request** | `query giftCards($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: GiftCardSortKeys)` |
| **Returns** | `GiftCardConnection` |

### `giftCardsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string, savedSearchId?: string` |
| **Request** | `query giftCardsCount($limit: Int, $query: String, $savedSearchId: ID)` |
| **Returns** | `Count | null` |

### `order`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query order($id: ID!)` |
| **Returns** | `Order | null` |

### `orderByIdentifier`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `identifier: OrderIdentifierInput` |
| **Request** | `query orderByIdentifier($identifier: OrderIdentifierInput!)` |
| **Returns** | `Order | null` |

### `orderEditSession`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query orderEditSession($id: ID!)` |
| **Returns** | `OrderEditSession | null` |

### `orderPaymentStatus`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `orderId: string, paymentReferenceId: string` |
| **Request** | `query orderPaymentStatus($orderId: ID!, $paymentReferenceId: String!)` |
| **Returns** | `OrderPaymentStatus | null` |

### `orderSavedSearches`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query orderSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `SavedSearchConnection` |

### `orders`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: OrderSortKeys` |
| **Request** | `query orders($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: OrderSortKeys)` |
| **Returns** | `OrderConnection` |

### `ordersCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string, savedSearchId?: string` |
| **Request** | `query ordersCount($limit: Int, $query: String, $savedSearchId: ID)` |
| **Returns** | `Count | null` |

### `paymentTermsTemplates`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `paymentTermsType?: PaymentTermsType` |
| **Request** | `query paymentTermsTemplates($paymentTermsType: PaymentTermsType)` |
| **Returns** | `string` |

### `pendingOrdersCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query pendingOrdersCount` |
| **Returns** | `Count | null` |

### `refund`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query refund($id: ID!)` |
| **Returns** | `Refund | null` |

### `getReturn`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query getReturn($id: ID!)` |
| **Returns** | `Return | null` |

### `returnCalculate`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `input: CalculateReturnInput` |
| **Request** | `query returnCalculate($input: CalculateReturnInput!)` |
| **Returns** | `CalculatedReturn | null` |

### `returnReasonDefinitions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, handles?: unknown, ids?: unknown, last?: number, query?: string, reverse?: boolean, sortKey?: ReturnReasonDefinitionSortKeys` |
| **Request** | `query returnReasonDefinitions($after: String, $before: String, $first: Int, $handles: String, $ids: String, $last: Int, $query: String, $reverse: Boolean, $sortKey: ReturnReasonDefinitionSortKeys)` |
| **Returns** | `ReturnReasonDefinitionConnection` |

### `returnableFulfillment`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query returnableFulfillment($id: ID!)` |
| **Returns** | `ReturnableFulfillment | null` |

### `returnableFulfillments`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, orderId: string, reverse?: boolean` |
| **Request** | `query returnableFulfillments($after: String, $before: String, $first: Int, $last: Int, $orderId: ID!, $reverse: Boolean)` |
| **Returns** | `ReturnableFulfillmentConnection` |

### `reverseDelivery`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query reverseDelivery($id: ID!)` |
| **Returns** | `ReverseDelivery | null` |

### `reverseFulfillmentOrder`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query reverseFulfillmentOrder($id: ID!)` |
| **Returns** | `ReverseFulfillmentOrder | null` |

### `tenderTransactions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean` |
| **Request** | `query tenderTransactions($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean)` |
| **Returns** | `TenderTransactionConnection` |

### `disputeEvidenceUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: ShopifyPaymentsDisputeEvidenceUpdateInput` |
| **Request** | `mutation disputeEvidenceUpdate($id: ID!, $input: ShopifyPaymentsDisputeEvidenceUpdateInput!)` |
| **Returns** | `DisputeEvidenceUpdatePayload` |

### `draftOrderBulkAddTags`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids?: unknown, savedSearchId?: string, search?: string, tags: unknown` |
| **Request** | `mutation draftOrderBulkAddTags($ids: String, $savedSearchId: ID, $search: String, $tags: String)` |
| **Returns** | `DraftOrderBulkAddTagsPayload` |

### `draftOrderBulkDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids?: unknown, savedSearchId?: string, search?: string` |
| **Request** | `mutation draftOrderBulkDelete($ids: String, $savedSearchId: ID, $search: String)` |
| **Returns** | `DraftOrderBulkDeletePayload` |

### `draftOrderBulkRemoveTags`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids?: unknown, savedSearchId?: string, search?: string, tags: unknown` |
| **Request** | `mutation draftOrderBulkRemoveTags($ids: String, $savedSearchId: ID, $search: String, $tags: String)` |
| **Returns** | `DraftOrderBulkRemoveTagsPayload` |

### `draftOrderCalculate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: DraftOrderInput` |
| **Request** | `mutation draftOrderCalculate($input: DraftOrderInput!)` |
| **Returns** | `DraftOrderCalculatePayload` |

### `draftOrderComplete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, paymentGatewayId?: string, sourceName?: string, paymentPending?: boolean` |
| **Request** | `mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID, $sourceName: String, $paymentPending: Boolean)` |
| **Returns** | `DraftOrderCompletePayload` |

### `draftOrderCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: DraftOrderInput` |
| **Request** | `mutation draftOrderCreate($input: DraftOrderInput!)` |
| **Returns** | `DraftOrderCreatePayload` |

### `draftOrderCreateFromOrder`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `orderId: string` |
| **Request** | `mutation draftOrderCreateFromOrder($orderId: ID!)` |
| **Returns** | `DraftOrderCreateFromOrderPayload` |

### `draftOrderDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: DraftOrderDeleteInput` |
| **Request** | `mutation draftOrderDelete($input: DraftOrderDeleteInput!)` |
| **Returns** | `DraftOrderDeletePayload` |

### `draftOrderDuplicate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id?: string, draftOrderId?: string` |
| **Request** | `mutation draftOrderDuplicate($id: ID, $draftOrderId: ID)` |
| **Returns** | `DraftOrderDuplicatePayload` |

### `draftOrderInvoicePreview`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `email?: EmailInput, id: string` |
| **Request** | `mutation draftOrderInvoicePreview($email: EmailInput, $id: ID!)` |
| **Returns** | `DraftOrderInvoicePreviewPayload` |

### `draftOrderInvoiceSend`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `email?: EmailInput, id: string` |
| **Request** | `mutation draftOrderInvoiceSend($email: EmailInput, $id: ID!)` |
| **Returns** | `DraftOrderInvoiceSendPayload` |

### `draftOrderUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: DraftOrderInput` |
| **Request** | `mutation draftOrderUpdate($id: ID!, $input: DraftOrderInput!)` |
| **Returns** | `DraftOrderUpdatePayload` |

### `giftCardCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: GiftCardCreateInput` |
| **Request** | `mutation giftCardCreate($input: GiftCardCreateInput!)` |
| **Returns** | `GiftCardCreatePayload` |

### `giftCardCredit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `creditInput: GiftCardCreditInput, id: string` |
| **Request** | `mutation giftCardCredit($creditInput: GiftCardCreditInput!, $id: ID!)` |
| **Returns** | `GiftCardCreditPayload` |

### `giftCardDeactivate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation giftCardDeactivate($id: ID!)` |
| **Returns** | `GiftCardDeactivatePayload` |

### `giftCardDebit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `debitInput: GiftCardDebitInput, id: string` |
| **Request** | `mutation giftCardDebit($debitInput: GiftCardDebitInput!, $id: ID!)` |
| **Returns** | `GiftCardDebitPayload` |

### `giftCardSendNotificationToCustomer`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation giftCardSendNotificationToCustomer($id: ID!)` |
| **Returns** | `GiftCardSendNotificationToCustomerPayload` |

### `giftCardSendNotificationToRecipient`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation giftCardSendNotificationToRecipient($id: ID!)` |
| **Returns** | `GiftCardSendNotificationToRecipientPayload` |

### `giftCardUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: GiftCardUpdateInput` |
| **Request** | `mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!)` |
| **Returns** | `GiftCardUpdatePayload` |

### `orderCancel`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `notifyCustomer?: boolean, orderId: string, reason: OrderCancelReason, refundMethod?: OrderCancelRefundMethodInput, restock: boolean, staffNote?: string, refund?: boolean` |
| **Request** | `mutation orderCancel($notifyCustomer: Boolean, $orderId: ID!, $reason: OrderCancelReason!, $refundMethod: OrderCancelRefundMethodInput, $restock: Boolean!, $staffNote: String, $refund: Boolean)` |
| **Returns** | `OrderCancelPayload` |

### `orderCapture`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: OrderCaptureInput` |
| **Request** | `mutation orderCapture($input: OrderCaptureInput!)` |
| **Returns** | `OrderCapturePayload` |

### `orderClose`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: OrderCloseInput` |
| **Request** | `mutation orderClose($input: OrderCloseInput!)` |
| **Returns** | `OrderClosePayload` |

### `orderCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `options?: OrderCreateOptionsInput, order: OrderCreateOrderInput` |
| **Request** | `mutation orderCreate($options: OrderCreateOptionsInput, $order: OrderCreateOrderInput!)` |
| **Returns** | `OrderCreatePayload` |

### `orderCreateMandatePayment`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `amount?: MoneyInput, autoCapture?: boolean, id: string, idempotencyKey: string, mandateId: string, paymentScheduleId?: string` |
| **Request** | `mutation orderCreateMandatePayment($amount: MoneyInput, $autoCapture: Boolean, $id: ID!, $idempotencyKey: String!, $mandateId: ID!, $paymentScheduleId: ID)` |
| **Returns** | `OrderCreateMandatePaymentPayload` |

### `orderCreateManualPayment`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `amount?: MoneyInput, id: string, paymentMethodName?: string, processedAt?: string` |
| **Request** | `mutation orderCreateManualPayment($amount: MoneyInput, $id: ID!, $paymentMethodName: String, $processedAt: DateTime)` |
| **Returns** | `OrderCreateManualPaymentPayload` |

### `orderCustomerRemove`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `orderId: string` |
| **Request** | `mutation orderCustomerRemove($orderId: ID!)` |
| **Returns** | `OrderCustomerRemovePayload` |

### `orderCustomerSet`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `customerId: string, orderId: string` |
| **Request** | `mutation orderCustomerSet($customerId: ID!, $orderId: ID!)` |
| **Returns** | `OrderCustomerSetPayload` |

### `orderDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `orderId: string` |
| **Request** | `mutation orderDelete($orderId: ID!)` |
| **Returns** | `OrderDeletePayload` |

### `orderEditAddCustomItem`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, locationId?: string, price: MoneyInput, quantity: number, requiresShipping?: boolean, taxable?: boolean, title: string` |
| **Request** | `mutation orderEditAddCustomItem($id: ID!, $locationId: ID, $price: MoneyInput!, $quantity: Int!, $requiresShipping: Boolean, $taxable: Boolean, $title: String!)` |
| **Returns** | `OrderEditAddCustomItemPayload` |

### `orderEditAddLineItemDiscount`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `discount: OrderEditAppliedDiscountInput, id: string, lineItemId: string` |
| **Request** | `mutation orderEditAddLineItemDiscount($discount: OrderEditAppliedDiscountInput!, $id: ID!, $lineItemId: ID!)` |
| **Returns** | `OrderEditAddLineItemDiscountPayload` |

### `orderEditAddShippingLine`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, shippingLine: OrderEditAddShippingLineInput` |
| **Request** | `mutation orderEditAddShippingLine($id: ID!, $shippingLine: OrderEditAddShippingLineInput!)` |
| **Returns** | `OrderEditAddShippingLinePayload` |

### `orderEditAddVariant`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `allowDuplicates?: boolean, id: string, locationId?: string, quantity: number, variantId: string` |
| **Request** | `mutation orderEditAddVariant($allowDuplicates: Boolean, $id: ID!, $locationId: ID, $quantity: Int!, $variantId: ID!)` |
| **Returns** | `OrderEditAddVariantPayload` |

### `orderEditBegin`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation orderEditBegin($id: ID!)` |
| **Returns** | `OrderEditBeginPayload` |

### `orderEditCommit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, notifyCustomer?: boolean, staffNote?: string` |
| **Request** | `mutation orderEditCommit($id: ID!, $notifyCustomer: Boolean, $staffNote: String)` |
| **Returns** | `OrderEditCommitPayload` |

### `orderEditRemoveDiscount`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `discountApplicationId: string, id: string` |
| **Request** | `mutation orderEditRemoveDiscount($discountApplicationId: ID!, $id: ID!)` |
| **Returns** | `OrderEditRemoveDiscountPayload` |

### `orderEditRemoveLineItemDiscount`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `discountApplicationId: string, id: string` |
| **Request** | `mutation orderEditRemoveLineItemDiscount($discountApplicationId: ID!, $id: ID!)` |
| **Returns** | `OrderEditRemoveLineItemDiscountPayload` |

### `orderEditRemoveShippingLine`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, shippingLineId: string` |
| **Request** | `mutation orderEditRemoveShippingLine($id: ID!, $shippingLineId: ID!)` |
| **Returns** | `OrderEditRemoveShippingLinePayload` |

### `orderEditSetQuantity`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, lineItemId: string, quantity: number, restock?: boolean, locationId?: string` |
| **Request** | `mutation orderEditSetQuantity($id: ID!, $lineItemId: ID!, $quantity: Int!, $restock: Boolean, $locationId: ID)` |
| **Returns** | `OrderEditSetQuantityPayload` |

### `orderEditUpdateDiscount`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `discount: OrderEditAppliedDiscountInput, discountApplicationId: string, id: string` |
| **Request** | `mutation orderEditUpdateDiscount($discount: OrderEditAppliedDiscountInput!, $discountApplicationId: ID!, $id: ID!)` |
| **Returns** | `OrderEditUpdateDiscountPayload` |

### `orderEditUpdateShippingLine`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, shippingLine: OrderEditUpdateShippingLineInput, shippingLineId: string` |
| **Request** | `mutation orderEditUpdateShippingLine($id: ID!, $shippingLine: OrderEditUpdateShippingLineInput!, $shippingLineId: ID!)` |
| **Returns** | `OrderEditUpdateShippingLinePayload` |

### `orderInvoiceSend`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `email?: EmailInput, id: string` |
| **Request** | `mutation orderInvoiceSend($email: EmailInput, $id: ID!)` |
| **Returns** | `OrderInvoiceSendPayload` |

### `orderMarkAsPaid`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: OrderMarkAsPaidInput` |
| **Request** | `mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!)` |
| **Returns** | `OrderMarkAsPaidPayload` |

### `orderOpen`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: OrderOpenInput` |
| **Request** | `mutation orderOpen($input: OrderOpenInput!)` |
| **Returns** | `OrderOpenPayload` |

### `orderRiskAssessmentCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `orderRiskAssessmentInput: OrderRiskAssessmentCreateInput` |
| **Request** | `mutation orderRiskAssessmentCreate($orderRiskAssessmentInput: OrderRiskAssessmentCreateInput!)` |
| **Returns** | `OrderRiskAssessmentCreatePayload` |

### `orderUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: OrderInput` |
| **Request** | `mutation orderUpdate($input: OrderInput!)` |
| **Returns** | `OrderUpdatePayload` |

### `paymentReminderSend`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `paymentScheduleId: string` |
| **Request** | `mutation paymentReminderSend($paymentScheduleId: ID!)` |
| **Returns** | `PaymentReminderSendPayload` |

### `paymentTermsCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `paymentTermsAttributes: PaymentTermsCreateInput, referenceId: string` |
| **Request** | `mutation paymentTermsCreate($paymentTermsAttributes: PaymentTermsCreateInput!, $referenceId: ID!)` |
| **Returns** | `PaymentTermsCreatePayload` |

### `paymentTermsDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: PaymentTermsDeleteInput` |
| **Request** | `mutation paymentTermsDelete($input: PaymentTermsDeleteInput!)` |
| **Returns** | `PaymentTermsDeletePayload` |

### `paymentTermsUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: PaymentTermsUpdateInput` |
| **Request** | `mutation paymentTermsUpdate($input: PaymentTermsUpdateInput!)` |
| **Returns** | `PaymentTermsUpdatePayload` |

### `refundCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: RefundInput` |
| **Request** | `mutation refundCreate($input: RefundInput!)` |
| **Returns** | `RefundCreatePayload` |

### `removeFromReturn`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `exchangeLineItems?: unknown, returnId: string, returnLineItems?: unknown` |
| **Request** | `mutation removeFromReturn($exchangeLineItems: String, $returnId: ID!, $returnLineItems: String)` |
| **Returns** | `RemoveFromReturnPayload` |

### `returnApproveRequest`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ReturnApproveRequestInput` |
| **Request** | `mutation returnApproveRequest($input: ReturnApproveRequestInput!)` |
| **Returns** | `ReturnApproveRequestPayload` |

### `returnCancel`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, notifyCustomer?: boolean` |
| **Request** | `mutation returnCancel($id: ID!, $notifyCustomer: Boolean)` |
| **Returns** | `ReturnCancelPayload` |

### `returnClose`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation returnClose($id: ID!)` |
| **Returns** | `ReturnClosePayload` |

### `returnCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `returnInput: ReturnInput` |
| **Request** | `mutation returnCreate($returnInput: ReturnInput!)` |
| **Returns** | `ReturnCreatePayload` |

### `returnDeclineRequest`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ReturnDeclineRequestInput` |
| **Request** | `mutation returnDeclineRequest($input: ReturnDeclineRequestInput!)` |
| **Returns** | `ReturnDeclineRequestPayload` |

### `returnLineItemRemoveFromReturn`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `returnId: string, returnLineItems: unknown` |
| **Request** | `mutation returnLineItemRemoveFromReturn($returnId: ID!, $returnLineItems: String)` |
| **Returns** | `ReturnLineItemRemoveFromReturnPayload` |

### `returnProcess`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ReturnProcessInput` |
| **Request** | `mutation returnProcess($input: ReturnProcessInput!)` |
| **Returns** | `ReturnProcessPayload` |

### `returnRefund`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `returnRefundInput: ReturnRefundInput` |
| **Request** | `mutation returnRefund($returnRefundInput: ReturnRefundInput!)` |
| **Returns** | `ReturnRefundPayload` |

### `returnReopen`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation returnReopen($id: ID!)` |
| **Returns** | `ReturnReopenPayload` |

### `returnRequest`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ReturnRequestInput` |
| **Request** | `mutation returnRequest($input: ReturnRequestInput!)` |
| **Returns** | `ReturnRequestPayload` |

### `reverseDeliveryCreateWithShipping`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `labelInput?: ReverseDeliveryLabelInput, notifyCustomer?: boolean, reverseDeliveryLineItems: unknown, reverseFulfillmentOrderId: string, trackingInput?: ReverseDeliveryTrackingInput` |
| **Request** | `mutation reverseDeliveryCreateWithShipping($labelInput: ReverseDeliveryLabelInput, $notifyCustomer: Boolean, $reverseDeliveryLineItems: String, $reverseFulfillmentOrderId: ID!, $trackingInput: ReverseDeliveryTrackingInput)` |
| **Returns** | `ReverseDeliveryCreateWithShippingPayload` |

### `reverseDeliveryShippingUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `labelInput?: ReverseDeliveryLabelInput, notifyCustomer?: boolean, reverseDeliveryId: string, trackingInput?: ReverseDeliveryTrackingInput` |
| **Request** | `mutation reverseDeliveryShippingUpdate($labelInput: ReverseDeliveryLabelInput, $notifyCustomer: Boolean, $reverseDeliveryId: ID!, $trackingInput: ReverseDeliveryTrackingInput)` |
| **Returns** | `ReverseDeliveryShippingUpdatePayload` |

### `reverseFulfillmentOrderDispose`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `dispositionInputs: unknown` |
| **Request** | `mutation reverseFulfillmentOrderDispose($dispositionInputs: String)` |
| **Returns** | `ReverseFulfillmentOrderDisposePayload` |

### `transactionVoid`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `parentTransactionId: string` |
| **Request** | `mutation transactionVoid($parentTransactionId: ID!)` |
| **Returns** | `TransactionVoidPayload` |

---

## Products & Collections

### `catalog`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query catalog($id: ID!)` |
| **Returns** | `Catalog | null` |

### `catalogOperations`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query catalogOperations` |
| **Returns** | `string` |

### `catalogs`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: CatalogSortKeys, type?: CatalogType` |
| **Request** | `query catalogs($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CatalogSortKeys, $type: CatalogType)` |
| **Returns** | `CatalogConnection` |

### `catalogsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string, type?: CatalogType` |
| **Request** | `query catalogsCount($limit: Int, $query: String, $type: CatalogType)` |
| **Returns** | `Count | null` |

### `collection`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query collection($id: ID!)` |
| **Returns** | `Collection | null` |

### `collectionByHandle`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `handle: string` |
| **Request** | `query collectionByHandle($handle: String!)` |
| **Returns** | `Collection | null` |

### `collectionByIdentifier`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `identifier: CollectionIdentifierInput` |
| **Request** | `query collectionByIdentifier($identifier: CollectionIdentifierInput!)` |
| **Returns** | `Collection | null` |

### `collectionRulesConditions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query collectionRulesConditions` |
| **Returns** | `unknown` |

### `collectionSavedSearches`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query collectionSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `SavedSearchConnection` |

### `collections`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: CollectionSortKeys` |
| **Request** | `query collections($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: CollectionSortKeys)` |
| **Returns** | `CollectionConnection` |

### `collectionsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string, savedSearchId?: string` |
| **Request** | `query collectionsCount($limit: Int, $query: String, $savedSearchId: ID)` |
| **Returns** | `Count | null` |

### `product`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query product($id: ID!)` |
| **Returns** | `Product | null` |

### `productByHandle`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `handle: string` |
| **Request** | `query productByHandle($handle: String!)` |
| **Returns** | `Product | null` |

### `productByIdentifier`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `identifier: ProductIdentifierInput` |
| **Request** | `query productByIdentifier($identifier: ProductIdentifierInput!)` |
| **Returns** | `Product | null` |

### `productDuplicateJob`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query productDuplicateJob($id: ID!)` |
| **Returns** | `ProductDuplicateJob | null` |

### `productFeed`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query productFeed($id: ID!)` |
| **Returns** | `ProductFeed | null` |

### `productFeeds`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query productFeeds($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `ProductFeedConnection` |

### `productOperation`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query productOperation($id: ID!)` |
| **Returns** | `unknown` |

### `productResourceFeedback`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `channelId?: string, id: string` |
| **Request** | `query productResourceFeedback($channelId: ID, $id: ID!)` |
| **Returns** | `ProductResourceFeedback | null` |

### `productSavedSearches`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query productSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `SavedSearchConnection` |

### `productTags`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query productTags($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `StringConnection` |

### `productTypes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query productTypes($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `StringConnection` |

### `productVariant`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query productVariant($id: ID!)` |
| **Returns** | `ProductVariant | null` |

### `productVariantByIdentifier`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `identifier: ProductVariantIdentifierInput` |
| **Request** | `query productVariantByIdentifier($identifier: ProductVariantIdentifierInput!)` |
| **Returns** | `ProductVariant | null` |

### `productVariants`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: ProductVariantSortKeys` |
| **Request** | `query productVariants($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: ProductVariantSortKeys)` |
| **Returns** | `ProductVariantConnection` |

### `productVariantsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string` |
| **Request** | `query productVariantsCount($limit: Int, $query: String)` |
| **Returns** | `Count | null` |

### `productVendors`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query productVendors($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `StringConnection` |

### `products`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: ProductSortKeys` |
| **Request** | `query products($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: ProductSortKeys)` |
| **Returns** | `ProductConnection` |

### `productsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string, savedSearchId?: string` |
| **Request** | `query productsCount($limit: Int, $query: String, $savedSearchId: ID)` |
| **Returns** | `Count | null` |

### `publishedProductsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, publicationId: string` |
| **Request** | `query publishedProductsCount($limit: Int, $publicationId: ID!)` |
| **Returns** | `Count | null` |

### `sellingPlanGroup`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query sellingPlanGroup($id: ID!)` |
| **Returns** | `SellingPlanGroup | null` |

### `sellingPlanGroups`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: SellingPlanGroupSortKeys` |
| **Request** | `query sellingPlanGroups($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: SellingPlanGroupSortKeys)` |
| **Returns** | `SellingPlanGroupConnection` |

### `taxonomy`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query taxonomy` |
| **Returns** | `Taxonomy | null` |

### `catalogContextUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `catalogId: string, contextsToAdd?: CatalogContextInput, contextsToRemove?: CatalogContextInput` |
| **Request** | `mutation catalogContextUpdate($catalogId: ID!, $contextsToAdd: CatalogContextInput, $contextsToRemove: CatalogContextInput)` |
| **Returns** | `CatalogContextUpdatePayload` |

### `catalogCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CatalogCreateInput` |
| **Request** | `mutation catalogCreate($input: CatalogCreateInput!)` |
| **Returns** | `CatalogCreatePayload` |

### `catalogDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `deleteDependentResources?: boolean, id: string` |
| **Request** | `mutation catalogDelete($deleteDependentResources: Boolean, $id: ID!)` |
| **Returns** | `CatalogDeletePayload` |

### `catalogUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: CatalogUpdateInput` |
| **Request** | `mutation catalogUpdate($id: ID!, $input: CatalogUpdateInput!)` |
| **Returns** | `CatalogUpdatePayload` |

### `collectionAddProducts`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, productIds: unknown` |
| **Request** | `mutation collectionAddProducts($id: ID!, $productIds: String)` |
| **Returns** | `CollectionAddProductsPayload` |

### `collectionAddProductsV2`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, productIds: unknown` |
| **Request** | `mutation collectionAddProductsV2($id: ID!, $productIds: String)` |
| **Returns** | `CollectionAddProductsV2Payload` |

### `collectionCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CollectionInput` |
| **Request** | `mutation collectionCreate($input: CollectionInput!)` |
| **Returns** | `CollectionCreatePayload` |

### `collectionDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CollectionDeleteInput` |
| **Request** | `mutation collectionDelete($input: CollectionDeleteInput!)` |
| **Returns** | `CollectionDeletePayload` |

### `collectionDuplicate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CollectionDuplicateInput` |
| **Request** | `mutation collectionDuplicate($input: CollectionDuplicateInput!)` |
| **Returns** | `CollectionDuplicatePayload` |

### `collectionPublish`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CollectionPublishInput` |
| **Request** | `mutation collectionPublish($input: CollectionPublishInput!)` |
| **Returns** | `CollectionPublishPayload` |

### `collectionRemoveProducts`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, productIds: unknown` |
| **Request** | `mutation collectionRemoveProducts($id: ID!, $productIds: String)` |
| **Returns** | `CollectionRemoveProductsPayload` |

### `collectionReorderProducts`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, moves: unknown` |
| **Request** | `mutation collectionReorderProducts($id: ID!, $moves: String)` |
| **Returns** | `CollectionReorderProductsPayload` |

### `collectionUnpublish`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CollectionUnpublishInput` |
| **Request** | `mutation collectionUnpublish($input: CollectionUnpublishInput!)` |
| **Returns** | `CollectionUnpublishPayload` |

### `collectionUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: CollectionInput` |
| **Request** | `mutation collectionUpdate($input: CollectionInput!)` |
| **Returns** | `CollectionUpdatePayload` |

### `combinedListingUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `optionsAndValues?: unknown, parentProductId: string, productsAdded?: unknown, productsEdited?: unknown, productsRemovedIds?: unknown, title?: string` |
| **Request** | `mutation combinedListingUpdate($optionsAndValues: String, $parentProductId: ID!, $productsAdded: String, $productsEdited: String, $productsRemovedIds: String, $title: String)` |
| **Returns** | `CombinedListingUpdatePayload` |

### `productBundleCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ProductBundleCreateInput` |
| **Request** | `mutation productBundleCreate($input: ProductBundleCreateInput!)` |
| **Returns** | `ProductBundleCreatePayload` |

### `productBundleUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ProductBundleUpdateInput` |
| **Request** | `mutation productBundleUpdate($input: ProductBundleUpdateInput!)` |
| **Returns** | `ProductBundleUpdatePayload` |

### `productChangeStatus`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `productId: string, status: ProductStatus` |
| **Request** | `mutation productChangeStatus($productId: ID!, $status: ProductStatus!)` |
| **Returns** | `ProductChangeStatusPayload` |

### `productCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `media?: unknown, product?: ProductCreateInput, input?: ProductInput` |
| **Request** | `mutation productCreate($media: String, $product: ProductCreateInput, $input: ProductInput)` |
| **Returns** | `ProductCreatePayload` |

### `productCreateMedia`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `media: unknown, productId: string` |
| **Request** | `mutation productCreateMedia($media: String, $productId: ID!)` |
| **Returns** | `ProductCreateMediaPayload` |

### `productDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ProductDeleteInput, synchronous?: boolean` |
| **Request** | `mutation productDelete($input: ProductDeleteInput!, $synchronous: Boolean)` |
| **Returns** | `ProductDeletePayload` |

### `productDeleteMedia`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `mediaIds: unknown, productId: string` |
| **Request** | `mutation productDeleteMedia($mediaIds: String, $productId: ID!)` |
| **Returns** | `ProductDeleteMediaPayload` |

### `productDuplicate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `includeImages?: boolean, includeTranslations?: boolean, newStatus?: ProductStatus, newTitle: string, productId: string, synchronous?: boolean` |
| **Request** | `mutation productDuplicate($includeImages: Boolean, $includeTranslations: Boolean, $newStatus: ProductStatus, $newTitle: String!, $productId: ID!, $synchronous: Boolean)` |
| **Returns** | `ProductDuplicatePayload` |

### `productFeedCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input?: ProductFeedInput` |
| **Request** | `mutation productFeedCreate($input: ProductFeedInput)` |
| **Returns** | `ProductFeedCreatePayload` |

### `productFeedDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation productFeedDelete($id: ID!)` |
| **Returns** | `ProductFeedDeletePayload` |

### `productFullSync`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `beforeUpdatedAt?: string, id: string, updatedAtSince?: string` |
| **Request** | `mutation productFullSync($beforeUpdatedAt: DateTime, $id: ID!, $updatedAtSince: DateTime)` |
| **Returns** | `ProductFullSyncPayload` |

### `productJoinSellingPlanGroups`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, sellingPlanGroupIds: unknown` |
| **Request** | `mutation productJoinSellingPlanGroups($id: ID!, $sellingPlanGroupIds: String)` |
| **Returns** | `ProductJoinSellingPlanGroupsPayload` |

### `productLeaveSellingPlanGroups`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, sellingPlanGroupIds: unknown` |
| **Request** | `mutation productLeaveSellingPlanGroups($id: ID!, $sellingPlanGroupIds: String)` |
| **Returns** | `ProductLeaveSellingPlanGroupsPayload` |

### `productOptionUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `option: OptionUpdateInput, optionValuesToAdd?: unknown, optionValuesToDelete?: unknown, optionValuesToUpdate?: unknown, productId: string, variantStrategy?: ProductOptionUpdateVariantStrategy` |
| **Request** | `mutation productOptionUpdate($option: OptionUpdateInput!, $optionValuesToAdd: String, $optionValuesToDelete: String, $optionValuesToUpdate: String, $productId: ID!, $variantStrategy: ProductOptionUpdateVariantStrategy)` |
| **Returns** | `ProductOptionUpdatePayload` |

### `productOptionsCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `options: unknown, productId: string, variantStrategy?: ProductOptionCreateVariantStrategy` |
| **Request** | `mutation productOptionsCreate($options: String, $productId: ID!, $variantStrategy: ProductOptionCreateVariantStrategy)` |
| **Returns** | `ProductOptionsCreatePayload` |

### `productOptionsDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `options: unknown, productId: string, strategy?: ProductOptionDeleteStrategy` |
| **Request** | `mutation productOptionsDelete($options: String, $productId: ID!, $strategy: ProductOptionDeleteStrategy)` |
| **Returns** | `ProductOptionsDeletePayload` |

### `productOptionsReorder`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `options: unknown, productId: string` |
| **Request** | `mutation productOptionsReorder($options: String, $productId: ID!)` |
| **Returns** | `ProductOptionsReorderPayload` |

### `productPublish`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ProductPublishInput` |
| **Request** | `mutation productPublish($input: ProductPublishInput!)` |
| **Returns** | `ProductPublishPayload` |

### `productReorderMedia`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, moves: unknown` |
| **Request** | `mutation productReorderMedia($id: ID!, $moves: String)` |
| **Returns** | `ProductReorderMediaPayload` |

### `productSet`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `identifier?: ProductSetIdentifiers, input: ProductSetInput, synchronous?: boolean` |
| **Request** | `mutation productSet($identifier: ProductSetIdentifiers, $input: ProductSetInput!, $synchronous: Boolean)` |
| **Returns** | `ProductSetPayload` |

### `productUnpublish`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ProductUnpublishInput` |
| **Request** | `mutation productUnpublish($input: ProductUnpublishInput!)` |
| **Returns** | `ProductUnpublishPayload` |

### `productUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `identifier?: ProductUpdateIdentifiers, media?: unknown, product?: ProductUpdateInput, input?: ProductInput` |
| **Request** | `mutation productUpdate($identifier: ProductUpdateIdentifiers, $media: String, $product: ProductUpdateInput, $input: ProductInput)` |
| **Returns** | `ProductUpdatePayload` |

### `productUpdateMedia`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `media: unknown, productId: string` |
| **Request** | `mutation productUpdateMedia($media: String, $productId: ID!)` |
| **Returns** | `ProductUpdateMediaPayload` |

### `productVariantAppendMedia`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `productId: string, variantMedia: unknown` |
| **Request** | `mutation productVariantAppendMedia($productId: ID!, $variantMedia: String)` |
| **Returns** | `ProductVariantAppendMediaPayload` |

### `productVariantDetachMedia`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `productId: string, variantMedia: unknown` |
| **Request** | `mutation productVariantDetachMedia($productId: ID!, $variantMedia: String)` |
| **Returns** | `ProductVariantDetachMediaPayload` |

### `productVariantJoinSellingPlanGroups`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, sellingPlanGroupIds: unknown` |
| **Request** | `mutation productVariantJoinSellingPlanGroups($id: ID!, $sellingPlanGroupIds: String)` |
| **Returns** | `ProductVariantJoinSellingPlanGroupsPayload` |

### `productVariantLeaveSellingPlanGroups`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, sellingPlanGroupIds: unknown` |
| **Request** | `mutation productVariantLeaveSellingPlanGroups($id: ID!, $sellingPlanGroupIds: String)` |
| **Returns** | `ProductVariantLeaveSellingPlanGroupsPayload` |

### `productVariantRelationshipBulkUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: unknown` |
| **Request** | `mutation productVariantRelationshipBulkUpdate($input: String)` |
| **Returns** | `ProductVariantRelationshipBulkUpdatePayload` |

### `productVariantsBulkCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `media?: unknown, productId: string, strategy?: ProductVariantsBulkCreateStrategy, variants: unknown` |
| **Request** | `mutation productVariantsBulkCreate($media: String, $productId: ID!, $strategy: ProductVariantsBulkCreateStrategy, $variants: String)` |
| **Returns** | `ProductVariantsBulkCreatePayload` |

### `productVariantsBulkDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `productId: string, variantsIds: unknown` |
| **Request** | `mutation productVariantsBulkDelete($productId: ID!, $variantsIds: String)` |
| **Returns** | `ProductVariantsBulkDeletePayload` |

### `productVariantsBulkReorder`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `positions: unknown, productId: string` |
| **Request** | `mutation productVariantsBulkReorder($positions: String, $productId: ID!)` |
| **Returns** | `ProductVariantsBulkReorderPayload` |

### `productVariantsBulkUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `allowPartialUpdates?: boolean, media?: unknown, productId: string, variants: unknown` |
| **Request** | `mutation productVariantsBulkUpdate($allowPartialUpdates: Boolean, $media: String, $productId: ID!, $variants: String)` |
| **Returns** | `ProductVariantsBulkUpdatePayload` |

### `sellingPlanGroupAddProductVariants`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, productVariantIds: unknown` |
| **Request** | `mutation sellingPlanGroupAddProductVariants($id: ID!, $productVariantIds: String)` |
| **Returns** | `SellingPlanGroupAddProductVariantsPayload` |

### `sellingPlanGroupAddProducts`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, productIds: unknown` |
| **Request** | `mutation sellingPlanGroupAddProducts($id: ID!, $productIds: String)` |
| **Returns** | `SellingPlanGroupAddProductsPayload` |

### `sellingPlanGroupCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: SellingPlanGroupInput, resources?: SellingPlanGroupResourceInput` |
| **Request** | `mutation sellingPlanGroupCreate($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput)` |
| **Returns** | `SellingPlanGroupCreatePayload` |

### `sellingPlanGroupDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation sellingPlanGroupDelete($id: ID!)` |
| **Returns** | `SellingPlanGroupDeletePayload` |

### `sellingPlanGroupRemoveProductVariants`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, productVariantIds: unknown` |
| **Request** | `mutation sellingPlanGroupRemoveProductVariants($id: ID!, $productVariantIds: String)` |
| **Returns** | `SellingPlanGroupRemoveProductVariantsPayload` |

### `sellingPlanGroupRemoveProducts`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, productIds: unknown` |
| **Request** | `mutation sellingPlanGroupRemoveProducts($id: ID!, $productIds: String)` |
| **Returns** | `SellingPlanGroupRemoveProductsPayload` |

### `sellingPlanGroupUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: SellingPlanGroupInput` |
| **Request** | `mutation sellingPlanGroupUpdate($id: ID!, $input: SellingPlanGroupInput!)` |
| **Returns** | `SellingPlanGroupUpdatePayload` |

---

## Retail / POS

### `cashDrawer`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query cashDrawer($id: ID!)` |
| **Returns** | `CashDrawer | null` |

### `cashDrawers`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string` |
| **Request** | `query cashDrawers($after: String, $before: String, $first: Int, $last: Int, $query: String)` |
| **Returns** | `CashDrawerConnection` |

### `cashManagementLocationSummary`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `endDate: string, locationId: string, startDate: string` |
| **Request** | `query cashManagementLocationSummary($endDate: Date!, $locationId: ID!, $startDate: Date!)` |
| **Returns** | `CashManagementSummary | null` |

### `cashManagementReasonCodes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query cashManagementReasonCodes($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `CashManagementReasonCodeConnection` |

### `cashManagementShopSummary`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `currencyCode: CurrencyCode, endDate: string, startDate: string` |
| **Request** | `query cashManagementShopSummary($currencyCode: CurrencyCode!, $endDate: Date!, $startDate: Date!)` |
| **Returns** | `CashManagementSummary | null` |

### `cashTrackingSession`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query cashTrackingSession($id: ID!)` |
| **Returns** | `CashTrackingSession | null` |

### `cashTrackingSessions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: CashTrackingSessionsSortKeys` |
| **Request** | `query cashTrackingSessions($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CashTrackingSessionsSortKeys)` |
| **Returns** | `CashTrackingSessionConnection` |

### `paymentCustomization`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query paymentCustomization($id: ID!)` |
| **Returns** | `PaymentCustomization | null` |

### `paymentCustomizations`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean` |
| **Request** | `query paymentCustomizations($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean)` |
| **Returns** | `PaymentCustomizationConnection` |

### `pointOfSaleDevice`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query pointOfSaleDevice($id: ID!)` |
| **Returns** | `PointOfSaleDevice | null` |

### `pointOfSaleDevicePaymentSession`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query pointOfSaleDevicePaymentSession($id: ID!)` |
| **Returns** | `PointOfSaleDevicePaymentSession | null` |

### `pointOfSaleDevicePaymentSessions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: PointOfSaleDevicePaymentSessionSortKeys` |
| **Request** | `query pointOfSaleDevicePaymentSessions($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: PointOfSaleDevicePaymentSessionSortKeys)` |
| **Returns** | `PointOfSaleDevicePaymentSessionConnection` |

### `cashDrawerCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locationId: string, name: string` |
| **Request** | `mutation cashDrawerCreate($locationId: ID!, $name: String!)` |
| **Returns** | `CashDrawerCreatePayload` |

### `cashDrawerFindOrCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locationId: string, name: string, pointOfSaleDeviceId: string` |
| **Request** | `mutation cashDrawerFindOrCreate($locationId: ID!, $name: String!, $pointOfSaleDeviceId: ID!)` |
| **Returns** | `CashDrawerFindOrCreatePayload` |

### `cashDrawerUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: CashDrawerUpdateInput` |
| **Request** | `mutation cashDrawerUpdate($id: ID!, $input: CashDrawerUpdateInput!)` |
| **Returns** | `CashDrawerUpdatePayload` |

### `cashManagementReasonCodeCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `code: string` |
| **Request** | `mutation cashManagementReasonCodeCreate($code: String!)` |
| **Returns** | `CashManagementReasonCodeCreatePayload` |

### `cashManagementReasonCodeDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation cashManagementReasonCodeDelete($id: ID!)` |
| **Returns** | `CashManagementReasonCodeDeletePayload` |

### `paymentCustomizationActivation`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `enabled: boolean, ids: unknown` |
| **Request** | `mutation paymentCustomizationActivation($enabled: Boolean!, $ids: String)` |
| **Returns** | `PaymentCustomizationActivationPayload` |

### `paymentCustomizationCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `paymentCustomization: PaymentCustomizationInput` |
| **Request** | `mutation paymentCustomizationCreate($paymentCustomization: PaymentCustomizationInput!)` |
| **Returns** | `PaymentCustomizationCreatePayload` |

### `paymentCustomizationDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation paymentCustomizationDelete($id: ID!)` |
| **Returns** | `PaymentCustomizationDeletePayload` |

### `paymentCustomizationUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, paymentCustomization: PaymentCustomizationInput` |
| **Request** | `mutation paymentCustomizationUpdate($id: ID!, $paymentCustomization: PaymentCustomizationInput!)` |
| **Returns** | `PaymentCustomizationUpdatePayload` |

### `pointOfSaleDeviceAssignToCashDrawer`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `cashDrawerId: string, pointOfSaleDeviceId: string` |
| **Request** | `mutation pointOfSaleDeviceAssignToCashDrawer($cashDrawerId: ID!, $pointOfSaleDeviceId: ID!)` |
| **Returns** | `PointOfSaleDeviceAssignToCashDrawerPayload` |

### `pointOfSaleDevicePaymentSessionAdjust`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `cash: MoneyInput, note?: string, pointOfSaleDevicePaymentSessionId: string, reasonCodeId?: string, staffMemberId: string, time?: string` |
| **Request** | `mutation pointOfSaleDevicePaymentSessionAdjust($cash: MoneyInput!, $note: String, $pointOfSaleDevicePaymentSessionId: ID!, $reasonCodeId: ID, $staffMemberId: ID!, $time: DateTime)` |
| **Returns** | `PointOfSaleDevicePaymentSessionAdjustPayload` |

### `pointOfSaleDevicePaymentSessionClose`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `balance: MoneyInput, note?: string, pointOfSaleDevicePaymentSessionId: string, reasonCodeId?: string, staffMemberId: string, time?: string` |
| **Request** | `mutation pointOfSaleDevicePaymentSessionClose($balance: MoneyInput!, $note: String, $pointOfSaleDevicePaymentSessionId: ID!, $reasonCodeId: ID, $staffMemberId: ID!, $time: DateTime)` |
| **Returns** | `PointOfSaleDevicePaymentSessionClosePayload` |

### `pointOfSaleDevicePaymentSessionCount`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `balance: MoneyInput, note?: string, pointOfSaleDevicePaymentSessionId: string, reasonCodeId?: string, staffMemberId: string, time?: string` |
| **Request** | `mutation pointOfSaleDevicePaymentSessionCount($balance: MoneyInput!, $note: String, $pointOfSaleDevicePaymentSessionId: ID!, $reasonCodeId: ID, $staffMemberId: ID!, $time: DateTime)` |
| **Returns** | `PointOfSaleDevicePaymentSessionCountPayload` |

### `pointOfSaleDevicePaymentSessionOpen`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `balance?: MoneyInput, note?: string, pointOfSaleDeviceId: string, reasonCodeId?: string, staffMemberId: string, time?: string` |
| **Request** | `mutation pointOfSaleDevicePaymentSessionOpen($balance: MoneyInput, $note: String, $pointOfSaleDeviceId: ID!, $reasonCodeId: ID, $staffMemberId: ID!, $time: DateTime)` |
| **Returns** | `PointOfSaleDevicePaymentSessionOpenPayload` |

---

## Shipping & Fulfillment

### `assignedFulfillmentOrders`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, assignmentStatus?: FulfillmentOrderAssignmentStatus, before?: string, first?: number, last?: number, locationIds?: unknown, reverse?: boolean, sortKey?: FulfillmentOrderSortKeys` |
| **Request** | `query assignedFulfillmentOrders($after: String, $assignmentStatus: FulfillmentOrderAssignmentStatus, $before: String, $first: Int, $last: Int, $locationIds: String, $reverse: Boolean, $sortKey: FulfillmentOrderSortKeys)` |
| **Returns** | `FulfillmentOrderConnection` |

### `availableCarrierServices`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query availableCarrierServices` |
| **Returns** | `unknown` |

### `carrierService`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query carrierService($id: ID!)` |
| **Returns** | `DeliveryCarrierService | null` |

### `carrierServices`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: CarrierServiceSortKeys` |
| **Request** | `query carrierServices($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CarrierServiceSortKeys)` |
| **Returns** | `DeliveryCarrierServiceConnection` |

### `deliveryCustomization`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query deliveryCustomization($id: ID!)` |
| **Returns** | `DeliveryCustomization | null` |

### `deliveryCustomizations`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean` |
| **Request** | `query deliveryCustomizations($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean)` |
| **Returns** | `DeliveryCustomizationConnection` |

### `deliveryProfile`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query deliveryProfile($id: ID!)` |
| **Returns** | `DeliveryProfile | null` |

### `deliveryProfiles`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, merchantOwnedOnly?: boolean, reverse?: boolean` |
| **Request** | `query deliveryProfiles($after: String, $before: String, $first: Int, $last: Int, $merchantOwnedOnly: Boolean, $reverse: Boolean)` |
| **Returns** | `DeliveryProfileConnection` |

### `deliveryPromiseParticipants`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, brandedPromiseHandle: string, first?: number, last?: number, ownerIds?: unknown, reverse?: boolean` |
| **Request** | `query deliveryPromiseParticipants($after: String, $before: String, $brandedPromiseHandle: String!, $first: Int, $last: Int, $ownerIds: String, $reverse: Boolean)` |
| **Returns** | `DeliveryPromiseParticipantConnection` |

### `deliveryPromiseProvider`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `locationId: string` |
| **Request** | `query deliveryPromiseProvider($locationId: ID!)` |
| **Returns** | `DeliveryPromiseProvider | null` |

### `deliveryPromiseSettings`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query deliveryPromiseSettings` |
| **Returns** | `DeliveryPromiseSetting | null` |

### `fulfillment`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query fulfillment($id: ID!)` |
| **Returns** | `Fulfillment | null` |

### `fulfillmentConstraintRules`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query fulfillmentConstraintRules` |
| **Returns** | `ShopifyFunction | null` |

### `fulfillmentOrder`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query fulfillmentOrder($id: ID!)` |
| **Returns** | `FulfillmentOrder | null` |

### `fulfillmentOrders`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, includeClosed?: boolean, last?: number, query?: string, reverse?: boolean, sortKey?: FulfillmentOrderSortKeys` |
| **Request** | `query fulfillmentOrders($after: String, $before: String, $first: Int, $includeClosed: Boolean, $last: Int, $query: String, $reverse: Boolean, $sortKey: FulfillmentOrderSortKeys)` |
| **Returns** | `FulfillmentOrderConnection` |

### `fulfillmentService`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query fulfillmentService($id: ID!)` |
| **Returns** | `FulfillmentService | null` |

### `locationsAvailableForDeliveryProfiles`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query locationsAvailableForDeliveryProfiles` |
| **Returns** | `unknown` |

### `locationsAvailableForDeliveryProfilesConnection`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query locationsAvailableForDeliveryProfilesConnection($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `LocationConnection` |

### `manualHoldsFulfillmentOrders`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean` |
| **Request** | `query manualHoldsFulfillmentOrders($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean)` |
| **Returns** | `FulfillmentOrderConnection` |

### `carrierServiceCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: DeliveryCarrierServiceCreateInput` |
| **Request** | `mutation carrierServiceCreate($input: DeliveryCarrierServiceCreateInput!)` |
| **Returns** | `CarrierServiceCreatePayload` |

### `carrierServiceDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation carrierServiceDelete($id: ID!)` |
| **Returns** | `CarrierServiceDeletePayload` |

### `carrierServiceUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: DeliveryCarrierServiceUpdateInput` |
| **Request** | `mutation carrierServiceUpdate($input: DeliveryCarrierServiceUpdateInput!)` |
| **Returns** | `CarrierServiceUpdatePayload` |

### `deliveryCustomizationActivation`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `enabled: boolean, ids: unknown` |
| **Request** | `mutation deliveryCustomizationActivation($enabled: Boolean!, $ids: String)` |
| **Returns** | `DeliveryCustomizationActivationPayload` |

### `deliveryCustomizationCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `deliveryCustomization: DeliveryCustomizationInput` |
| **Request** | `mutation deliveryCustomizationCreate($deliveryCustomization: DeliveryCustomizationInput!)` |
| **Returns** | `DeliveryCustomizationCreatePayload` |

### `deliveryCustomizationDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation deliveryCustomizationDelete($id: ID!)` |
| **Returns** | `DeliveryCustomizationDeletePayload` |

### `deliveryCustomizationUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `deliveryCustomization: DeliveryCustomizationInput, id: string` |
| **Request** | `mutation deliveryCustomizationUpdate($deliveryCustomization: DeliveryCustomizationInput!, $id: ID!)` |
| **Returns** | `DeliveryCustomizationUpdatePayload` |

### `deliveryProfileCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `profile: DeliveryProfileInput` |
| **Request** | `mutation deliveryProfileCreate($profile: DeliveryProfileInput!)` |
| **Returns** | `DeliveryProfileCreatePayload` |

### `deliveryProfileRemove`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation deliveryProfileRemove($id: ID!)` |
| **Returns** | `DeliveryProfileRemovePayload` |

### `deliveryProfileUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, profile: DeliveryProfileInput` |
| **Request** | `mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!)` |
| **Returns** | `DeliveryProfileUpdatePayload` |

### `deliveryPromiseParticipantsUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `brandedPromiseHandle: string, ownersToAdd?: unknown, ownersToRemove?: unknown` |
| **Request** | `mutation deliveryPromiseParticipantsUpdate($brandedPromiseHandle: String!, $ownersToAdd: String, $ownersToRemove: String)` |
| **Returns** | `DeliveryPromiseParticipantsUpdatePayload` |

### `deliveryPromiseProviderUpsert`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `active?: boolean, fulfillmentDelay?: number, locationId: string, timeZone?: string` |
| **Request** | `mutation deliveryPromiseProviderUpsert($active: Boolean, $fulfillmentDelay: Int, $locationId: ID!, $timeZone: String)` |
| **Returns** | `DeliveryPromiseProviderUpsertPayload` |

### `deliverySettingUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | _(none)_ |
| **Request** | `mutation deliverySettingUpdate` |
| **Returns** | `DeliverySettingUpdatePayload` |

### `deliveryShippingOriginAssign`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locationId: string` |
| **Request** | `mutation deliveryShippingOriginAssign($locationId: ID!)` |
| **Returns** | `DeliveryShippingOriginAssignPayload` |

### `fulfillmentCancel`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation fulfillmentCancel($id: ID!)` |
| **Returns** | `FulfillmentCancelPayload` |

### `fulfillmentConstraintRuleCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `deliveryMethodTypes: unknown, functionHandle?: string, metafields?: unknown, functionId?: string` |
| **Request** | `mutation fulfillmentConstraintRuleCreate($deliveryMethodTypes: String, $functionHandle: String, $metafields: String, $functionId: String)` |
| **Returns** | `FulfillmentConstraintRuleCreatePayload` |

### `fulfillmentConstraintRuleDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation fulfillmentConstraintRuleDelete($id: ID!)` |
| **Returns** | `FulfillmentConstraintRuleDeletePayload` |

### `fulfillmentConstraintRuleUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `deliveryMethodTypes: unknown, id: string` |
| **Request** | `mutation fulfillmentConstraintRuleUpdate($deliveryMethodTypes: String, $id: ID!)` |
| **Returns** | `FulfillmentConstraintRuleUpdatePayload` |

### `fulfillmentCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillment: FulfillmentInput, message?: string` |
| **Request** | `mutation fulfillmentCreate($fulfillment: FulfillmentInput!, $message: String)` |
| **Returns** | `FulfillmentCreatePayload` |

### `fulfillmentCreateV2`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillment: FulfillmentV2Input, message?: string` |
| **Request** | `mutation fulfillmentCreateV2($fulfillment: FulfillmentV2Input!, $message: String)` |
| **Returns** | `FulfillmentCreateV2Payload` |

### `fulfillmentEventCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillmentEvent: FulfillmentEventInput` |
| **Request** | `mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!)` |
| **Returns** | `FulfillmentEventCreatePayload` |

### `fulfillmentOrderAcceptCancellationRequest`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, message?: string` |
| **Request** | `mutation fulfillmentOrderAcceptCancellationRequest($id: ID!, $message: String)` |
| **Returns** | `FulfillmentOrderAcceptCancellationRequestPayload` |

### `fulfillmentOrderAcceptFulfillmentRequest`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `estimatedShippedAt?: string, id: string, message?: string` |
| **Request** | `mutation fulfillmentOrderAcceptFulfillmentRequest($estimatedShippedAt: DateTime, $id: ID!, $message: String)` |
| **Returns** | `FulfillmentOrderAcceptFulfillmentRequestPayload` |

### `fulfillmentOrderCancel`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation fulfillmentOrderCancel($id: ID!)` |
| **Returns** | `FulfillmentOrderCancelPayload` |

### `fulfillmentOrderClose`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, message?: string` |
| **Request** | `mutation fulfillmentOrderClose($id: ID!, $message: String)` |
| **Returns** | `FulfillmentOrderClosePayload` |

### `fulfillmentOrderHold`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillmentHold: FulfillmentOrderHoldInput, id: string` |
| **Request** | `mutation fulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!)` |
| **Returns** | `FulfillmentOrderHoldPayload` |

### `fulfillmentOrderLineItemsPreparedForPickup`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: FulfillmentOrderLineItemsPreparedForPickupInput` |
| **Request** | `mutation fulfillmentOrderLineItemsPreparedForPickup($input: FulfillmentOrderLineItemsPreparedForPickupInput!)` |
| **Returns** | `FulfillmentOrderLineItemsPreparedForPickupPayload` |

### `fulfillmentOrderMerge`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillmentOrderMergeInputs: unknown` |
| **Request** | `mutation fulfillmentOrderMerge($fulfillmentOrderMergeInputs: String)` |
| **Returns** | `FulfillmentOrderMergePayload` |

### `fulfillmentOrderMove`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillmentOrderLineItems?: unknown, id: string, newLocationId: string` |
| **Request** | `mutation fulfillmentOrderMove($fulfillmentOrderLineItems: String, $id: ID!, $newLocationId: ID!)` |
| **Returns** | `FulfillmentOrderMovePayload` |

### `fulfillmentOrderOpen`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation fulfillmentOrderOpen($id: ID!)` |
| **Returns** | `FulfillmentOrderOpenPayload` |

### `fulfillmentOrderRejectCancellationRequest`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, message?: string` |
| **Request** | `mutation fulfillmentOrderRejectCancellationRequest($id: ID!, $message: String)` |
| **Returns** | `FulfillmentOrderRejectCancellationRequestPayload` |

### `fulfillmentOrderRejectFulfillmentRequest`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, lineItems?: unknown, message?: string, reason?: FulfillmentOrderRejectionReason` |
| **Request** | `mutation fulfillmentOrderRejectFulfillmentRequest($id: ID!, $lineItems: String, $message: String, $reason: FulfillmentOrderRejectionReason)` |
| **Returns** | `FulfillmentOrderRejectFulfillmentRequestPayload` |

### `fulfillmentOrderReleaseHold`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `externalId?: string, holdIds?: unknown, id: string` |
| **Request** | `mutation fulfillmentOrderReleaseHold($externalId: String, $holdIds: String, $id: ID!)` |
| **Returns** | `FulfillmentOrderReleaseHoldPayload` |

### `fulfillmentOrderReportProgress`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, progressReport?: FulfillmentOrderReportProgressInput` |
| **Request** | `mutation fulfillmentOrderReportProgress($id: ID!, $progressReport: FulfillmentOrderReportProgressInput)` |
| **Returns** | `FulfillmentOrderReportProgressPayload` |

### `fulfillmentOrderReschedule`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillAt: string, id: string` |
| **Request** | `mutation fulfillmentOrderReschedule($fulfillAt: DateTime!, $id: ID!)` |
| **Returns** | `FulfillmentOrderReschedulePayload` |

### `fulfillmentOrderSplit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillmentOrderSplits: unknown` |
| **Request** | `mutation fulfillmentOrderSplit($fulfillmentOrderSplits: String)` |
| **Returns** | `FulfillmentOrderSplitPayload` |

### `fulfillmentOrderSubmitCancellationRequest`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, message?: string` |
| **Request** | `mutation fulfillmentOrderSubmitCancellationRequest($id: ID!, $message: String)` |
| **Returns** | `FulfillmentOrderSubmitCancellationRequestPayload` |

### `fulfillmentOrderSubmitFulfillmentRequest`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillmentOrderLineItems?: unknown, id: string, message?: string, notifyCustomer?: boolean` |
| **Request** | `mutation fulfillmentOrderSubmitFulfillmentRequest($fulfillmentOrderLineItems: String, $id: ID!, $message: String, $notifyCustomer: Boolean)` |
| **Returns** | `FulfillmentOrderSubmitFulfillmentRequestPayload` |

### `fulfillmentOrdersReroute`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `excludedLocationIds?: unknown, fulfillmentOrderIds: unknown, includedLocationIds?: unknown` |
| **Request** | `mutation fulfillmentOrdersReroute($excludedLocationIds: String, $fulfillmentOrderIds: String, $includedLocationIds: String)` |
| **Returns** | `FulfillmentOrdersReroutePayload` |

### `fulfillmentOrdersSetFulfillmentDeadline`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillmentDeadline: string, fulfillmentOrderIds: unknown` |
| **Request** | `mutation fulfillmentOrdersSetFulfillmentDeadline($fulfillmentDeadline: DateTime!, $fulfillmentOrderIds: String)` |
| **Returns** | `FulfillmentOrdersSetFulfillmentDeadlinePayload` |

### `fulfillmentServiceCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `callbackUrl?: string, inventoryManagement?: boolean, name: string, requiresShippingMethod?: boolean, trackingSupport?: boolean, fulfillmentOrdersOptIn?: boolean` |
| **Request** | `mutation fulfillmentServiceCreate($callbackUrl: URL, $inventoryManagement: Boolean, $name: String!, $requiresShippingMethod: Boolean, $trackingSupport: Boolean, $fulfillmentOrdersOptIn: Boolean)` |
| **Returns** | `FulfillmentServiceCreatePayload` |

### `fulfillmentServiceDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `destinationLocationId?: string, id: string, inventoryAction?: FulfillmentServiceDeleteInventoryAction` |
| **Request** | `mutation fulfillmentServiceDelete($destinationLocationId: ID, $id: ID!, $inventoryAction: FulfillmentServiceDeleteInventoryAction)` |
| **Returns** | `FulfillmentServiceDeletePayload` |

### `fulfillmentServiceUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `callbackUrl?: string, id: string, inventoryManagement?: boolean, name?: string, requiresShippingMethod?: boolean, trackingSupport?: boolean, fulfillmentOrdersOptIn?: boolean` |
| **Request** | `mutation fulfillmentServiceUpdate($callbackUrl: URL, $id: ID!, $inventoryManagement: Boolean, $name: String, $requiresShippingMethod: Boolean, $trackingSupport: Boolean, $fulfillmentOrdersOptIn: Boolean)` |
| **Returns** | `FulfillmentServiceUpdatePayload` |

### `fulfillmentTrackingInfoUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillmentId: string, notifyCustomer?: boolean, trackingInfoInput: FulfillmentTrackingInput` |
| **Request** | `mutation fulfillmentTrackingInfoUpdate($fulfillmentId: ID!, $notifyCustomer: Boolean, $trackingInfoInput: FulfillmentTrackingInput!)` |
| **Returns** | `FulfillmentTrackingInfoUpdatePayload` |

### `fulfillmentTrackingInfoUpdateV2`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fulfillmentId: string, notifyCustomer?: boolean, trackingInfoInput: FulfillmentTrackingInput` |
| **Request** | `mutation fulfillmentTrackingInfoUpdateV2($fulfillmentId: ID!, $notifyCustomer: Boolean, $trackingInfoInput: FulfillmentTrackingInput!)` |
| **Returns** | `FulfillmentTrackingInfoUpdateV2Payload` |

### `shippingPackageDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation shippingPackageDelete($id: ID!)` |
| **Returns** | `ShippingPackageDeletePayload` |

### `shippingPackageMakeDefault`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation shippingPackageMakeDefault($id: ID!)` |
| **Returns** | `ShippingPackageMakeDefaultPayload` |

### `shippingPackageUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, shippingPackage: CustomShippingPackageInput` |
| **Request** | `mutation shippingPackageUpdate($id: ID!, $shippingPackage: CustomShippingPackageInput!)` |
| **Returns** | `ShippingPackageUpdatePayload` |

---

## App Management

### `app`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id?: string` |
| **Request** | `query app($id: ID)` |
| **Returns** | `App | null` |

### `appByHandle`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `handle: string` |
| **Request** | `query appByHandle($handle: String!)` |
| **Returns** | `App | null` |

### `appByKey`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `apiKey: string` |
| **Request** | `query appByKey($apiKey: String!)` |
| **Returns** | `App | null` |

### `appDiscountType`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `functionId: string` |
| **Request** | `query appDiscountType($functionId: String!)` |
| **Returns** | `App` |

### `appDiscountTypes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query appDiscountTypes` |
| **Returns** | `App` |

### `appDiscountTypesNodes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query appDiscountTypesNodes($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `AppDiscountTypeConnection` |

### `appInstallation`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id?: string` |
| **Request** | `query appInstallation($id: ID)` |
| **Returns** | `number | null` |

### `appInstallations`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, category?: AppInstallationCategory, first?: number, last?: number, privacy?: AppInstallationPrivacy, reverse?: boolean, sortKey?: AppInstallationSortKeys` |
| **Request** | `query appInstallations($after: String, $before: String, $category: AppInstallationCategory, $first: Int, $last: Int, $privacy: AppInstallationPrivacy, $reverse: Boolean, $sortKey: AppInstallationSortKeys)` |
| **Returns** | `AppInstallationConnection` |

### `currentAppInstallation`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query currentAppInstallation` |
| **Returns** | `number | null` |

### `appPurchaseOneTimeCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `name: string, price: MoneyInput, returnUrl: string, test?: boolean` |
| **Request** | `mutation appPurchaseOneTimeCreate($name: String!, $price: MoneyInput!, $returnUrl: URL!, $test: Boolean)` |
| **Returns** | `AppPurchaseOneTimeCreatePayload` |

### `appRevokeAccessScopes`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `scopes: string[]` |
| **Request** | `mutation appRevokeAccessScopes($scopes: [String!]!)` |
| **Returns** | `AppRevokeAccessScopesPayload` |

### `appSubscriptionCancel`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, prorate?: boolean` |
| **Request** | `mutation appSubscriptionCancel($id: ID!, $prorate: Boolean)` |
| **Returns** | `AppSubscriptionCancelPayload` |

### `appSubscriptionCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `lineItems: AppSubscriptionLineItemInput[], name: string, replacementBehavior?: AppSubscriptionReplacementBehavior, returnUrl: string, test?: boolean, trialDays?: number` |
| **Request** | `mutation appSubscriptionCreate($lineItems: [AppSubscriptionLineItemInput!]!, $name: String!, $replacementBehavior: AppSubscriptionReplacementBehavior, $returnUrl: URL!, $test: Boolean, $trialDays: Int)` |
| **Returns** | `AppSubscriptionCreatePayload` |

### `appSubscriptionLineItemUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `cappedAmount: MoneyInput, id: string` |
| **Request** | `mutation appSubscriptionLineItemUpdate($cappedAmount: MoneyInput!, $id: ID!)` |
| **Returns** | `AppSubscriptionLineItemUpdatePayload` |

### `appSubscriptionTrialExtend`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `days: number, id: string` |
| **Request** | `mutation appSubscriptionTrialExtend($days: Int!, $id: ID!)` |
| **Returns** | `AppSubscriptionTrialExtendPayload` |

### `appUninstall`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | _(none)_ |
| **Request** | `mutation appUninstall` |
| **Returns** | `AppUninstallPayload` |

### `appUsageRecordCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `description: string, idempotencyKey?: string, price: MoneyInput, subscriptionLineItemId: string` |
| **Request** | `mutation appUsageRecordCreate($description: String!, $idempotencyKey: String, $price: MoneyInput!, $subscriptionLineItemId: ID!)` |
| **Returns** | `AppUsageRecordCreatePayload` |

---

## CMS (Articles, Blogs, Pages)

### `article`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query article($id: ID!)` |
| **Returns** | `Article | null` |

### `articleAuthors`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query articleAuthors($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `ArticleAuthorConnection` |

### `articles`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: ArticleSortKeys` |
| **Request** | `query articles($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: ArticleSortKeys)` |
| **Returns** | `ArticleConnection` |

### `articleTags`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit: number, sort?: ArticleTagSort` |
| **Request** | `query articleTags($limit: Int!, $sort: ArticleTagSort)` |
| **Returns** | `string[]` |

### `blog`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query blog($id: ID!)` |
| **Returns** | `Blog | null` |

### `blogs`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: BlogSortKeys` |
| **Request** | `query blogs($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: BlogSortKeys)` |
| **Returns** | `BlogConnection` |

### `blogsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string` |
| **Request** | `query blogsCount($limit: Int, $query: String)` |
| **Returns** | `Count | null` |

### `comment`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query comment($id: ID!)` |
| **Returns** | `Comment | null` |

### `comments`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: CommentSortKeys` |
| **Request** | `query comments($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CommentSortKeys)` |
| **Returns** | `CommentConnection` |

### `menu`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query menu($id: ID!)` |
| **Returns** | `Menu | null` |

### `menus`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: MenuSortKeys` |
| **Request** | `query menus($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: MenuSortKeys)` |
| **Returns** | `MenuConnection` |

### `page`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query page($id: ID!)` |
| **Returns** | `Page | null` |

### `pages`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: PageSortKeys` |
| **Request** | `query pages($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: PageSortKeys)` |
| **Returns** | `PageConnection` |

### `pagesCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number` |
| **Request** | `query pagesCount($limit: Int)` |
| **Returns** | `Count | null` |

### `scriptTag`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query scriptTag($id: ID!)` |
| **Returns** | `boolean` |

### `scriptTags`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, src?: string` |
| **Request** | `query scriptTags($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $src: URL)` |
| **Returns** | `ScriptTagConnection` |

### `articleCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `article: ArticleCreateInput, blog?: ArticleBlogInput` |
| **Request** | `mutation articleCreate($article: ArticleCreateInput!, $blog: ArticleBlogInput)` |
| **Returns** | `ArticleCreatePayload` |

### `articleDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation articleDelete($id: ID!)` |
| **Returns** | `ArticleDeletePayload` |

### `articleUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `article: ArticleUpdateInput, blog?: ArticleBlogInput, id: string` |
| **Request** | `mutation articleUpdate($article: ArticleUpdateInput!, $blog: ArticleBlogInput, $id: ID!)` |
| **Returns** | `ArticleUpdatePayload` |

### `blogCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `blog: BlogCreateInput` |
| **Request** | `mutation blogCreate($blog: BlogCreateInput!)` |
| **Returns** | `BlogCreatePayload` |

### `blogDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation blogDelete($id: ID!)` |
| **Returns** | `BlogDeletePayload` |

### `blogUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `blog: BlogUpdateInput, id: string` |
| **Request** | `mutation blogUpdate($blog: BlogUpdateInput!, $id: ID!)` |
| **Returns** | `BlogUpdatePayload` |

### `commentApprove`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation commentApprove($id: ID!)` |
| **Returns** | `CommentApprovePayload` |

### `commentDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation commentDelete($id: ID!)` |
| **Returns** | `CommentDeletePayload` |

### `commentNotSpam`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation commentNotSpam($id: ID!)` |
| **Returns** | `CommentNotSpamPayload` |

### `commentSpam`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation commentSpam($id: ID!)` |
| **Returns** | `CommentSpamPayload` |

### `menuCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `handle: string, items: MenuItemCreateInput[], title: string` |
| **Request** | `mutation menuCreate($handle: String!, $items: [MenuItemCreateInput!]!, $title: String!)` |
| **Returns** | `MenuCreatePayload` |

### `menuDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation menuDelete($id: ID!)` |
| **Returns** | `MenuDeletePayload` |

### `menuUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `handle?: string, id: string, items: MenuItemUpdateInput[], title: string` |
| **Request** | `mutation menuUpdate($handle: String, $id: ID!, $items: [MenuItemUpdateInput!]!, $title: String!)` |
| **Returns** | `MenuUpdatePayload` |

### `pageCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `page: PageCreateInput` |
| **Request** | `mutation pageCreate($page: PageCreateInput!)` |
| **Returns** | `PageCreatePayload` |

### `pageDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation pageDelete($id: ID!)` |
| **Returns** | `PageDeletePayload` |

### `pageUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, page: PageUpdateInput` |
| **Request** | `mutation pageUpdate($id: ID!, $page: PageUpdateInput!)` |
| **Returns** | `PageUpdatePayload` |

### `savedSearchCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: SavedSearchCreateInput` |
| **Request** | `mutation savedSearchCreate($input: SavedSearchCreateInput!)` |
| **Returns** | `SavedSearchCreatePayload` |

### `savedSearchDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: SavedSearchDeleteInput` |
| **Request** | `mutation savedSearchDelete($input: SavedSearchDeleteInput!)` |
| **Returns** | `SavedSearchDeletePayload` |

### `savedSearchUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: SavedSearchUpdateInput` |
| **Request** | `mutation savedSearchUpdate($input: SavedSearchUpdateInput!)` |
| **Returns** | `SavedSearchUpdatePayload` |

### `scriptTagCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ScriptTagInput` |
| **Request** | `mutation scriptTagCreate($input: ScriptTagInput!)` |
| **Returns** | `ScriptTagCreatePayload` |

### `scriptTagDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation scriptTagDelete($id: ID!)` |
| **Returns** | `ScriptTagDeletePayload` |

### `scriptTagUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: ScriptTagInput` |
| **Request** | `mutation scriptTagUpdate($id: ID!, $input: ScriptTagInput!)` |
| **Returns** | `ScriptTagUpdatePayload` |

---

## Channels & Publications

### `channel`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query channel($id: ID!)` |
| **Returns** | `Channel | null` |

### `channelByHandle`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `handle: string` |
| **Request** | `query channelByHandle($handle: String!)` |
| **Returns** | `Channel | null` |

### `channels`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query channels($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `ChannelConnection` |

### `checkoutAndAccountsConfiguration`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query checkoutAndAccountsConfiguration($id: ID!)` |
| **Returns** | `CheckoutAndAccountsConfigurationBranding | null` |

### `checkoutAndAccountsConfigurations`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: CheckoutAndAccountsConfigurationsGraphQLSortKeys` |
| **Request** | `query checkoutAndAccountsConfigurations($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CheckoutAndAccountsConfigurationsGraphQLSortKeys)` |
| **Returns** | `CheckoutAndAccountsConfigurationConnection | null` |

### `checkoutBranding`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `checkoutProfileId: string` |
| **Request** | `query checkoutBranding($checkoutProfileId: ID!)` |
| **Returns** | `CheckoutBrandingCustomizations | null` |

### `checkoutProfile`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query checkoutProfile($id: ID!)` |
| **Returns** | `string` |

### `checkoutProfiles`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: CheckoutProfileSortKeys` |
| **Request** | `query checkoutProfiles($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CheckoutProfileSortKeys)` |
| **Returns** | `CheckoutProfileConnection` |

### `consentPolicy`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `consentRequired?: boolean, countryCode?: PrivacyCountryCode, dataSaleOptOutRequired?: boolean, id?: string, regionCode?: string` |
| **Request** | `query consentPolicy($consentRequired: Boolean, $countryCode: PrivacyCountryCode, $dataSaleOptOutRequired: Boolean, $id: ID, $regionCode: String)` |
| **Returns** | `string` |

### `consentPolicyRegions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query consentPolicyRegions` |
| **Returns** | `unknown` |

### `publication`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query publication($id: ID!)` |
| **Returns** | `Publication | null` |

### `publications`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, catalogType?: CatalogType, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query publications($after: String, $before: String, $catalogType: CatalogType, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `PublicationConnection` |

### `publicationsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `catalogType?: CatalogType, limit?: number` |
| **Request** | `query publicationsCount($catalogType: CatalogType, $limit: Int)` |
| **Returns** | `Count | null` |

### `channelCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ChannelCreateInput` |
| **Request** | `mutation channelCreate($input: ChannelCreateInput!)` |
| **Returns** | `ChannelCreatePayload` |

### `channelDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation channelDelete($id: ID!)` |
| **Returns** | `ChannelDeletePayload` |

### `channelFullSync`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `beforeUpdatedAt?: string, channelId: string, country?: CountryCode, language?: LanguageCode, updatedAtSince?: string` |
| **Request** | `mutation channelFullSync($beforeUpdatedAt: DateTime, $channelId: ID!, $country: CountryCode, $language: LanguageCode, $updatedAtSince: DateTime)` |
| **Returns** | `ChannelFullSyncPayload` |

### `channelUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: ChannelUpdateInput` |
| **Request** | `mutation channelUpdate($id: ID!, $input: ChannelUpdateInput!)` |
| **Returns** | `ChannelUpdatePayload` |

### `checkoutAndAccountsConfigurationUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `configuration: CheckoutAndAccountsConfigurationInput, id: string` |
| **Request** | `mutation checkoutAndAccountsConfigurationUpdate($configuration: CheckoutAndAccountsConfigurationInput!, $id: ID!)` |
| **Returns** | `CheckoutAndAccountsConfigurationUpdatePayload` |

### `checkoutBrandingUpsert`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `checkoutBrandingInput?: CheckoutBrandingInput, checkoutProfileId: string` |
| **Request** | `mutation checkoutBrandingUpsert($checkoutBrandingInput: CheckoutBrandingInput, $checkoutProfileId: ID!)` |
| **Returns** | `CheckoutBrandingUpsertPayload` |

### `consentPolicyUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `consentPolicies: ConsentPolicyInput[]` |
| **Request** | `mutation consentPolicyUpdate($consentPolicies: [ConsentPolicyInput!]!)` |
| **Returns** | `ConsentPolicyUpdatePayload` |

### `publicationCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: PublicationCreateInput` |
| **Request** | `mutation publicationCreate($input: PublicationCreateInput!)` |
| **Returns** | `PublicationCreatePayload` |

### `publicationDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation publicationDelete($id: ID!)` |
| **Returns** | `PublicationDeletePayload` |

### `publicationUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: PublicationUpdateInput` |
| **Request** | `mutation publicationUpdate($id: ID!, $input: PublicationUpdateInput!)` |
| **Returns** | `PublicationUpdatePayload` |

### `publishablePublish`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: PublicationInput[]` |
| **Request** | `mutation publishablePublish($id: ID!, $input: [PublicationInput!]!)` |
| **Returns** | `PublishablePublishPayload` |

### `publishablePublishToCurrentChannel`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation publishablePublishToCurrentChannel($id: ID!)` |
| **Returns** | `PublishablePublishToCurrentChannelPayload` |

### `publishableUnpublish`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: PublicationInput[]` |
| **Request** | `mutation publishableUnpublish($id: ID!, $input: [PublicationInput!]!)` |
| **Returns** | `PublishableUnpublishPayload` |

### `publishableUnpublishToCurrentChannel`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation publishableUnpublishToCurrentChannel($id: ID!)` |
| **Returns** | `PublishableUnpublishToCurrentChannelPayload` |

---

## Metafields & Metaobjects

### `metafieldDefinition`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `identifier?: MetafieldDefinitionIdentifierInput, id?: string` |
| **Request** | `query metafieldDefinition($identifier: MetafieldDefinitionIdentifierInput, $id: ID)` |
| **Returns** | `MetafieldAccess` |

### `metafieldDefinitions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, constraintStatus?: MetafieldDefinitionConstraintStatus, constraintSubtype?: MetafieldDefinitionConstraintSubtypeIdentifier, first?: number, key?: string, last?: number, namespace?: string, ownerType: MetafieldOwnerType, pinnedStatus?: MetafieldDefinitionPinnedStatus, query?: string, reverse?: boolean, sortKey?: MetafieldDefinitionSortKeys` |
| **Request** | `query metafieldDefinitions($after: String, $before: String, $constraintStatus: MetafieldDefinitionConstraintStatus, $constraintSubtype: MetafieldDefinitionConstraintSubtypeIdentifier, $first: Int, $key: String, $last: Int, $namespace: String, $ownerType: MetafieldOwnerType!, $pinnedStatus: MetafieldDefinitionPinnedStatus, $query: String, $reverse: Boolean, $sortKey: MetafieldDefinitionSortKeys)` |
| **Returns** | `MetafieldDefinitionConnection` |

### `metafieldDefinitionTypes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query metafieldDefinitionTypes` |
| **Returns** | `string` |

### `metaobject`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query metaobject($id: ID!)` |
| **Returns** | `Metaobject | null` |

### `metaobjectByHandle`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `handle: MetaobjectHandleInput` |
| **Request** | `query metaobjectByHandle($handle: MetaobjectHandleInput!)` |
| **Returns** | `Metaobject | null` |

### `metaobjects`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: string, type: string` |
| **Request** | `query metaobjects($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: String, $type: String!)` |
| **Returns** | `MetaobjectConnection` |

### `metaobjectDefinition`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query metaobjectDefinition($id: ID!)` |
| **Returns** | `MetaobjectAccess` |

### `metaobjectDefinitionByType`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `type: string` |
| **Request** | `query metaobjectDefinitionByType($type: String!)` |
| **Returns** | `MetaobjectAccess` |

### `metaobjectDefinitions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query metaobjectDefinitions($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `MetaobjectDefinitionConnection` |

### `standardMetafieldDefinitionTemplates`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, constraintStatus?: MetafieldDefinitionConstraintStatus, constraintSubtype?: MetafieldDefinitionConstraintSubtypeIdentifier, excludeActivated?: boolean, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query standardMetafieldDefinitionTemplates($after: String, $before: String, $constraintStatus: MetafieldDefinitionConstraintStatus, $constraintSubtype: MetafieldDefinitionConstraintSubtypeIdentifier, $excludeActivated: Boolean, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `StandardMetafieldDefinitionTemplateConnection` |

### `metafieldDefinitionCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `definition: MetafieldDefinitionInput` |
| **Request** | `mutation metafieldDefinitionCreate($definition: MetafieldDefinitionInput!)` |
| **Returns** | `MetafieldDefinitionCreatePayload` |

### `metafieldDefinitionDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `deleteAllAssociatedMetafields?: boolean, id?: string, identifier?: MetafieldDefinitionIdentifierInput` |
| **Request** | `mutation metafieldDefinitionDelete($deleteAllAssociatedMetafields: Boolean, $id: ID, $identifier: MetafieldDefinitionIdentifierInput)` |
| **Returns** | `MetafieldDefinitionDeletePayload` |

### `metafieldDefinitionPin`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `definitionId?: string, identifier?: MetafieldDefinitionIdentifierInput` |
| **Request** | `mutation metafieldDefinitionPin($definitionId: ID, $identifier: MetafieldDefinitionIdentifierInput)` |
| **Returns** | `MetafieldDefinitionPinPayload` |

### `metafieldDefinitionUnpin`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `definitionId?: string, identifier?: MetafieldDefinitionIdentifierInput` |
| **Request** | `mutation metafieldDefinitionUnpin($definitionId: ID, $identifier: MetafieldDefinitionIdentifierInput)` |
| **Returns** | `MetafieldDefinitionUnpinPayload` |

### `metafieldDefinitionUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `definition: MetafieldDefinitionUpdateInput` |
| **Request** | `mutation metafieldDefinitionUpdate($definition: MetafieldDefinitionUpdateInput!)` |
| **Returns** | `MetafieldDefinitionUpdatePayload` |

### `metafieldsDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `metafields: MetafieldIdentifierInput[]` |
| **Request** | `mutation metafieldsDelete($metafields: [MetafieldIdentifierInput!]!)` |
| **Returns** | `MetafieldsDeletePayload` |

### `metafieldsSet`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `metafields: MetafieldsSetInput[]` |
| **Request** | `mutation metafieldsSet($metafields: [MetafieldsSetInput!]!)` |
| **Returns** | `MetafieldsSetPayload` |

### `metaobjectBulkDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `where: MetaobjectBulkDeleteWhereCondition` |
| **Request** | `mutation metaobjectBulkDelete($where: MetaobjectBulkDeleteWhereCondition!)` |
| **Returns** | `MetaobjectBulkDeletePayload` |

### `metaobjectCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `metaobject: MetaobjectCreateInput` |
| **Request** | `mutation metaobjectCreate($metaobject: MetaobjectCreateInput!)` |
| **Returns** | `MetaobjectCreatePayload` |

### `metaobjectDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation metaobjectDelete($id: ID!)` |
| **Returns** | `MetaobjectDeletePayload` |

### `metaobjectUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, metaobject: MetaobjectUpdateInput` |
| **Request** | `mutation metaobjectUpdate($id: ID!, $metaobject: MetaobjectUpdateInput!)` |
| **Returns** | `MetaobjectUpdatePayload` |

### `metaobjectUpsert`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `handle: MetaobjectHandleInput, metaobject: MetaobjectUpsertInput` |
| **Request** | `mutation metaobjectUpsert($handle: MetaobjectHandleInput!, $metaobject: MetaobjectUpsertInput!)` |
| **Returns** | `MetaobjectUpsertPayload` |

### `metaobjectDefinitionCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `definition: MetaobjectDefinitionCreateInput` |
| **Request** | `mutation metaobjectDefinitionCreate($definition: MetaobjectDefinitionCreateInput!)` |
| **Returns** | `MetaobjectDefinitionCreatePayload` |

### `metaobjectDefinitionDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation metaobjectDefinitionDelete($id: ID!)` |
| **Returns** | `MetaobjectDefinitionDeletePayload` |

### `metaobjectDefinitionUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `definition: MetaobjectDefinitionUpdateInput, id: string` |
| **Request** | `mutation metaobjectDefinitionUpdate($definition: MetaobjectDefinitionUpdateInput!, $id: ID!)` |
| **Returns** | `MetaobjectDefinitionUpdatePayload` |

### `standardMetafieldDefinitionEnable`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `useAsCollectionCondition?: boolean, visibleToStorefrontApi?: boolean` |
| **Request** | `mutation standardMetafieldDefinitionEnable($useAsCollectionCondition: Boolean, $visibleToStorefrontApi: Boolean)` |
| **Returns** | `StandardMetafieldDefinitionEnablePayload` |

### `standardMetaobjectDefinitionEnable`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `type: string` |
| **Request** | `mutation standardMetaobjectDefinitionEnable($type: String!)` |
| **Returns** | `StandardMetaobjectDefinitionEnablePayload` |

---

## Shop Configuration

### `shop`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query shop` |
| **Returns** | `Shop` |

### `shopBillingPreferences`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query shopBillingPreferences` |
| **Returns** | `CurrencyCode` |

### `shopLocales`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `published?: boolean` |
| **Request** | `query shopLocales($published: Boolean)` |
| **Returns** | `string` |

### `shopifyFunction`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query shopifyFunction($id: String!)` |
| **Returns** | `App` |

### `shopifyFunctions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, apiType?: string, before?: string, first?: number, last?: number, reverse?: boolean, useCreationUi?: boolean` |
| **Request** | `query shopifyFunctions($after: String, $apiType: String, $before: String, $first: Int, $last: Int, $reverse: Boolean, $useCreationUi: Boolean)` |
| **Returns** | `ShopifyFunctionConnection` |

### `shopifyqlQuery`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `query: string` |
| **Request** | `query shopifyqlQuery($query: String!)` |
| **Returns** | `unknown` |

### `shopifyPaymentsAccount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query shopifyPaymentsAccount` |
| **Returns** | `boolean` |

### `staffMember`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id?: string` |
| **Request** | `query staffMember($id: ID)` |
| **Returns** | `boolean` |

### `staffMembers`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: StaffMembersSortKeys` |
| **Request** | `query staffMembers($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: StaffMembersSortKeys)` |
| **Returns** | `StaffMemberConnection | null` |

### `currentStaffMember`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query currentStaffMember` |
| **Returns** | `boolean` |

### `privacySettings`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query privacySettings` |
| **Returns** | `CookieBanner | null` |

### `publicApiVersions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query publicApiVersions` |
| **Returns** | `string` |

### `shopLocaleDisable`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locale: string` |
| **Request** | `mutation shopLocaleDisable($locale: String!)` |
| **Returns** | `ShopLocaleDisablePayload` |

### `shopLocaleEnable`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locale: string, marketWebPresenceIds?: string[]` |
| **Request** | `mutation shopLocaleEnable($locale: String!, $marketWebPresenceIds: [ID!]!)` |
| **Returns** | `ShopLocaleEnablePayload` |

### `shopLocaleUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locale: string, shopLocale: ShopLocaleInput` |
| **Request** | `mutation shopLocaleUpdate($locale: String!, $shopLocale: ShopLocaleInput!)` |
| **Returns** | `ShopLocaleUpdatePayload` |

### `shopPolicyUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `shopPolicy: ShopPolicyInput` |
| **Request** | `mutation shopPolicyUpdate($shopPolicy: ShopPolicyInput!)` |
| **Returns** | `ShopPolicyUpdatePayload` |

### `shopResourceFeedbackCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: ResourceFeedbackCreateInput` |
| **Request** | `mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!)` |
| **Returns** | `ShopResourceFeedbackCreatePayload` |

### `shopifyPaymentsPayoutAlternateCurrencyCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `accountId?: string, currency: CurrencyCode` |
| **Request** | `mutation shopifyPaymentsPayoutAlternateCurrencyCreate($accountId: ID, $currency: CurrencyCode!)` |
| **Returns** | `ShopifyPaymentsPayoutAlternateCurrencyCreatePayload` |

### `stagedUploadsCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: StagedUploadInput[]` |
| **Request** | `mutation stagedUploadsCreate($input: [StagedUploadInput!]!)` |
| **Returns** | `StagedUploadsCreatePayload` |

### `stagedUploadTargetGenerate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: StagedUploadTargetGenerateInput` |
| **Request** | `mutation stagedUploadTargetGenerate($input: StagedUploadTargetGenerateInput!)` |
| **Returns** | `StagedUploadTargetGeneratePayload` |

### `stagedUploadTargetsGenerate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: StageImageInput[]` |
| **Request** | `mutation stagedUploadTargetsGenerate($input: [StageImageInput!]!)` |
| **Returns** | `StagedUploadTargetsGeneratePayload` |

### `tagsAdd`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, tags: string[]` |
| **Request** | `mutation tagsAdd($id: ID!, $tags: [String!]!)` |
| **Returns** | `TagsAddPayload` |

### `tagsRemove`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, tags: string[]` |
| **Request** | `mutation tagsRemove($id: ID!, $tags: [String!]!)` |
| **Returns** | `TagsRemovePayload` |

### `delegateAccessTokenCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: DelegateAccessTokenInput` |
| **Request** | `mutation delegateAccessTokenCreate($input: DelegateAccessTokenInput!)` |
| **Returns** | `DelegateAccessTokenCreatePayload` |

### `delegateAccessTokenDestroy`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `accessToken: string` |
| **Request** | `mutation delegateAccessTokenDestroy($accessToken: String!)` |
| **Returns** | `DelegateAccessTokenDestroyPayload` |

### `dataSaleOptOut`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `email: string` |
| **Request** | `mutation dataSaleOptOut($email: String!)` |
| **Returns** | `DataSaleOptOutPayload` |

### `taxAppConfigure`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ready: boolean` |
| **Request** | `mutation taxAppConfigure($ready: Boolean!)` |
| **Returns** | `TaxAppConfigurePayload` |

### `taxSummaryCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `endTime?: string, orderId?: string, startTime?: string` |
| **Request** | `mutation taxSummaryCreate($endTime: DateTime, $orderId: ID, $startTime: DateTime)` |
| **Returns** | `TaxSummaryCreatePayload` |

### `privacyFeaturesDisable`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `featuresToDisable: PrivacyFeaturesEnum[]` |
| **Request** | `mutation privacyFeaturesDisable($featuresToDisable: [PrivacyFeaturesEnum!]!)` |
| **Returns** | `PrivacyFeaturesDisablePayload` |

### `financeAppAccessPolicy`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query financeAppAccessPolicy` |
| **Returns** | `BankingFinanceAppAccess[]` |

### `financeKycInformation`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query financeKycInformation` |
| **Returns** | `ShopifyPaymentsMerchantCategoryCode | null` |

---

## Themes & Online Store

### `theme`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query theme($id: ID!)` |
| **Returns** | `OnlineStoreThemeFileConnection | null` |

### `themes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, names?: string[], reverse?: boolean, roles?: ThemeRole[]` |
| **Request** | `query themes($after: String, $before: String, $first: Int, $last: Int, $names: [String!]!, $reverse: Boolean, $roles: [ThemeRole!]!)` |
| **Returns** | `OnlineStoreThemeConnection | null` |

### `onlineStore`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query onlineStore` |
| **Returns** | `unknown` |

### `availableBackupRegions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query availableBackupRegions` |
| **Returns** | `string` |

### `backupRegion`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query backupRegion` |
| **Returns** | `string` |

### `themeCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `name?: string, role?: ThemeRole, source: string` |
| **Request** | `mutation themeCreate($name: String, $role: ThemeRole, $source: URL!)` |
| **Returns** | `ThemeCreatePayload` |

### `themeDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation themeDelete($id: ID!)` |
| **Returns** | `ThemeDeletePayload` |

### `themeDuplicate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, name?: string` |
| **Request** | `mutation themeDuplicate($id: ID!, $name: String)` |
| **Returns** | `ThemeDuplicatePayload` |

### `themeFilesCopy`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `files: ThemeFilesCopyFileInput[], themeId: string` |
| **Request** | `mutation themeFilesCopy($files: [ThemeFilesCopyFileInput!]!, $themeId: ID!)` |
| **Returns** | `ThemeFilesCopyPayload` |

### `themeFilesDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `files: string[], themeId: string` |
| **Request** | `mutation themeFilesDelete($files: [String!]!, $themeId: ID!)` |
| **Returns** | `ThemeFilesDeletePayload` |

### `themeFilesUpsert`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `files: OnlineStoreThemeFilesUpsertFileInput[], themeId: string` |
| **Request** | `mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!)` |
| **Returns** | `ThemeFilesUpsertPayload` |

### `themePublish`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation themePublish($id: ID!)` |
| **Returns** | `ThemePublishPayload` |

### `themeUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: OnlineStoreThemeInput` |
| **Request** | `mutation themeUpdate($id: ID!, $input: OnlineStoreThemeInput!)` |
| **Returns** | `ThemeUpdatePayload` |

### `backupRegionUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `region?: BackupRegionUpdateInput` |
| **Request** | `mutation backupRegionUpdate($region: BackupRegionUpdateInput)` |
| **Returns** | `BackupRegionUpdatePayload` |

---

## Webhooks, Events & Bulk Ops

### `webhookSubscription`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query webhookSubscription($id: ID!)` |
| **Returns** | `string | null` |

### `webhookSubscriptions`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, format?: WebhookSubscriptionFormat, last?: number, query?: string, reverse?: boolean, sortKey?: WebhookSubscriptionSortKeys, topics?: WebhookSubscriptionTopic[], uri?: string, callbackUrl?: string` |
| **Request** | `query webhookSubscriptions($after: String, $before: String, $first: Int, $format: WebhookSubscriptionFormat, $last: Int, $query: String, $reverse: Boolean, $sortKey: WebhookSubscriptionSortKeys, $topics: [WebhookSubscriptionTopic!]!, $uri: String, $callbackUrl: URL)` |
| **Returns** | `WebhookSubscriptionConnection` |

### `webhookSubscriptionsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string` |
| **Request** | `query webhookSubscriptionsCount($limit: Int, $query: String)` |
| **Returns** | `Count | null` |

### `event`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query event($id: ID!)` |
| **Returns** | `Event | null` |

### `events`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: EventSortKeys` |
| **Request** | `query events($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: EventSortKeys)` |
| **Returns** | `EventConnection | null` |

### `eventsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `query?: string` |
| **Request** | `query eventsCount($query: String)` |
| **Returns** | `Count | null` |

### `bulkOperation`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query bulkOperation($id: ID!)` |
| **Returns** | `string` |

### `bulkOperations`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: BulkOperationsSortKeys` |
| **Request** | `query bulkOperations($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: BulkOperationsSortKeys)` |
| **Returns** | `BulkOperationConnection` |

### `currentBulkOperation`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `type?: BulkOperationType` |
| **Request** | `query currentBulkOperation($type: BulkOperationType)` |
| **Returns** | `string` |

### `serverPixel`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query serverPixel` |
| **Returns** | `string` |

### `webPixel`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id?: string` |
| **Request** | `query webPixel($id: ID)` |
| **Returns** | `string` |

### `deletionEvents`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: DeletionEventSortKeys, subjectTypes?: DeletionEventSubjectType[]` |
| **Request** | `query deletionEvents($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: DeletionEventSortKeys, $subjectTypes: [DeletionEventSubjectType!]!)` |
| **Returns** | `DeletionEventConnection` |

### `webhookSubscriptionCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `topic: WebhookSubscriptionTopic, webhookSubscription: WebhookSubscriptionInput` |
| **Request** | `mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!)` |
| **Returns** | `WebhookSubscriptionCreatePayload` |

### `webhookSubscriptionDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation webhookSubscriptionDelete($id: ID!)` |
| **Returns** | `WebhookSubscriptionDeletePayload` |

### `webhookSubscriptionUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, webhookSubscription: WebhookSubscriptionInput` |
| **Request** | `mutation webhookSubscriptionUpdate($id: ID!, $webhookSubscription: WebhookSubscriptionInput!)` |
| **Returns** | `WebhookSubscriptionUpdatePayload` |

### `eventBridgeWebhookSubscriptionCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `topic: WebhookSubscriptionTopic, webhookSubscription: EventBridgeWebhookSubscriptionInput` |
| **Request** | `mutation eventBridgeWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: EventBridgeWebhookSubscriptionInput!)` |
| **Returns** | `EventBridgeWebhookSubscriptionCreatePayload` |

### `eventBridgeWebhookSubscriptionUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, webhookSubscription: EventBridgeWebhookSubscriptionInput` |
| **Request** | `mutation eventBridgeWebhookSubscriptionUpdate($id: ID!, $webhookSubscription: EventBridgeWebhookSubscriptionInput!)` |
| **Returns** | `EventBridgeWebhookSubscriptionUpdatePayload` |

### `pubSubWebhookSubscriptionCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `topic: WebhookSubscriptionTopic, webhookSubscription: PubSubWebhookSubscriptionInput` |
| **Request** | `mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!)` |
| **Returns** | `PubSubWebhookSubscriptionCreatePayload` |

### `pubSubWebhookSubscriptionUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, webhookSubscription: PubSubWebhookSubscriptionInput` |
| **Request** | `mutation pubSubWebhookSubscriptionUpdate($id: ID!, $webhookSubscription: PubSubWebhookSubscriptionInput!)` |
| **Returns** | `PubSubWebhookSubscriptionUpdatePayload` |

### `bulkOperationCancel`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation bulkOperationCancel($id: ID!)` |
| **Returns** | `BulkOperationCancelPayload` |

### `bulkOperationRunMutation`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `clientIdentifier?: string, mutation: string, stagedUploadPath: string, groupObjects?: boolean` |
| **Request** | `mutation bulkOperationRunMutation($clientIdentifier: String, $mutation: String!, $stagedUploadPath: String!, $groupObjects: Boolean)` |
| **Returns** | `BulkOperationRunMutationPayload` |

### `bulkOperationRunQuery`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `groupObjects?: boolean, query: string` |
| **Request** | `mutation bulkOperationRunQuery($groupObjects: Boolean!, $query: String!)` |
| **Returns** | `BulkOperationRunQueryPayload` |

### `bulkProductResourceFeedbackCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `feedbackInput: ProductResourceFeedbackInput[]` |
| **Request** | `mutation bulkProductResourceFeedbackCreate($feedbackInput: [ProductResourceFeedbackInput!]!)` |
| **Returns** | `BulkProductResourceFeedbackCreatePayload` |

### `flowTriggerReceive`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `handle?: string, payload?: unknown, body?: string` |
| **Request** | `mutation flowTriggerReceive($handle: String, $payload: JSON, $body: String)` |
| **Returns** | `FlowTriggerReceivePayload` |

### `serverPixelCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | _(none)_ |
| **Request** | `mutation serverPixelCreate` |
| **Returns** | `ServerPixelCreatePayload` |

### `serverPixelDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | _(none)_ |
| **Request** | `mutation serverPixelDelete` |
| **Returns** | `ServerPixelDeletePayload` |

### `eventBridgeServerPixelUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `arn: string` |
| **Request** | `mutation eventBridgeServerPixelUpdate($arn: ARN!)` |
| **Returns** | `EventBridgeServerPixelUpdatePayload` |

### `pubSubServerPixelUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `pubSubProject: string, pubSubTopic: string` |
| **Request** | `mutation pubSubServerPixelUpdate($pubSubProject: String!, $pubSubTopic: String!)` |
| **Returns** | `PubSubServerPixelUpdatePayload` |

### `webPixelCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `webPixel: WebPixelInput` |
| **Request** | `mutation webPixelCreate($webPixel: WebPixelInput!)` |
| **Returns** | `WebPixelCreatePayload` |

### `webPixelDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation webPixelDelete($id: ID!)` |
| **Returns** | `WebPixelDeletePayload` |

### `webPixelUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, webPixel: WebPixelInput` |
| **Request** | `mutation webPixelUpdate($id: ID!, $webPixel: WebPixelInput!)` |
| **Returns** | `WebPixelUpdatePayload` |

---

## Markets & Localization

### `market`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query market($id: ID!)` |
| **Returns** | `Market | null` |

### `marketByGeography`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `countryCode: CountryCode` |
| **Request** | `query marketByGeography($countryCode: CountryCode!)` |
| **Returns** | `Market | null` |

### `markets`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: MarketsSortKeys, type?: MarketType` |
| **Request** | `query markets($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: MarketsSortKeys, $type: MarketType)` |
| **Returns** | `MarketConnection` |

### `marketsResolvedValues`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `buyerSignal: BuyerSignalInput` |
| **Request** | `query marketsResolvedValues($buyerSignal: BuyerSignalInput!)` |
| **Returns** | `MarketCatalogConnection` |

### `primaryMarket`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query primaryMarket` |
| **Returns** | `Market` |

### `availableLocales`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query availableLocales` |
| **Returns** | `Locale[]` |

### `translatableResource`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `resourceId: string` |
| **Request** | `query translatableResource($resourceId: ID!)` |
| **Returns** | `number | null` |

### `translatableResources`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, resourceType: TranslatableResourceType, reverse?: boolean` |
| **Request** | `query translatableResources($after: String, $before: String, $first: Int, $last: Int, $resourceType: TranslatableResourceType!, $reverse: Boolean)` |
| **Returns** | `TranslatableResourceConnection` |

### `translatableResourcesByIds`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, resourceIds: string[], reverse?: boolean` |
| **Request** | `query translatableResourcesByIds($after: String, $before: String, $first: Int, $last: Int, $resourceIds: [ID!]!, $reverse: Boolean)` |
| **Returns** | `TranslatableResourceConnection` |

### `marketLocalizableResource`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `resourceId: string` |
| **Request** | `query marketLocalizableResource($resourceId: ID!)` |
| **Returns** | `unknown` |

### `marketLocalizableResources`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, resourceType: MarketLocalizableResourceType, reverse?: boolean` |
| **Request** | `query marketLocalizableResources($after: String, $before: String, $first: Int, $last: Int, $resourceType: MarketLocalizableResourceType!, $reverse: Boolean)` |
| **Returns** | `MarketLocalizableResourceConnection` |

### `marketLocalizableResourcesByIds`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, resourceIds: string[], reverse?: boolean` |
| **Request** | `query marketLocalizableResourcesByIds($after: String, $before: String, $first: Int, $last: Int, $resourceIds: [ID!]!, $reverse: Boolean)` |
| **Returns** | `MarketLocalizableResourceConnection` |

### `marketCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: MarketCreateInput` |
| **Request** | `mutation marketCreate($input: MarketCreateInput!)` |
| **Returns** | `MarketCreatePayload` |

### `marketCurrencySettingsUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: MarketCurrencySettingsUpdateInput, marketId: string` |
| **Request** | `mutation marketCurrencySettingsUpdate($input: MarketCurrencySettingsUpdateInput!, $marketId: ID!)` |
| **Returns** | `MarketCurrencySettingsUpdatePayload` |

### `marketDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation marketDelete($id: ID!)` |
| **Returns** | `MarketDeletePayload` |

### `marketLocalizationsRegister`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `marketLocalizations: MarketLocalizationRegisterInput[], resourceId: string` |
| **Request** | `mutation marketLocalizationsRegister($marketLocalizations: [MarketLocalizationRegisterInput!]!, $resourceId: ID!)` |
| **Returns** | `MarketLocalizationsRegisterPayload` |

### `marketLocalizationsRemove`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `marketIds: string[], marketLocalizationKeys: string[], resourceId: string` |
| **Request** | `mutation marketLocalizationsRemove($marketIds: [ID!]!, $marketLocalizationKeys: [String!]!, $resourceId: ID!)` |
| **Returns** | `MarketLocalizationsRemovePayload` |

### `marketRegionDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation marketRegionDelete($id: ID!)` |
| **Returns** | `MarketRegionDeletePayload` |

### `marketRegionsCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `marketId: string, regions: MarketRegionCreateInput[]` |
| **Request** | `mutation marketRegionsCreate($marketId: ID!, $regions: [MarketRegionCreateInput!]!)` |
| **Returns** | `MarketRegionsCreatePayload` |

### `marketRegionsDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids: string[]` |
| **Request** | `mutation marketRegionsDelete($ids: [ID!]!)` |
| **Returns** | `MarketRegionsDeletePayload` |

### `marketUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: MarketUpdateInput` |
| **Request** | `mutation marketUpdate($id: ID!, $input: MarketUpdateInput!)` |
| **Returns** | `MarketUpdatePayload` |

### `marketWebPresenceCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `marketId: string, webPresence: MarketWebPresenceCreateInput` |
| **Request** | `mutation marketWebPresenceCreate($marketId: ID!, $webPresence: MarketWebPresenceCreateInput!)` |
| **Returns** | `MarketWebPresenceCreatePayload` |

### `marketWebPresenceDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `webPresenceId: string` |
| **Request** | `mutation marketWebPresenceDelete($webPresenceId: ID!)` |
| **Returns** | `MarketWebPresenceDeletePayload` |

### `marketWebPresenceUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `webPresence: MarketWebPresenceUpdateInput, webPresenceId: string` |
| **Request** | `mutation marketWebPresenceUpdate($webPresence: MarketWebPresenceUpdateInput!, $webPresenceId: ID!)` |
| **Returns** | `MarketWebPresenceUpdatePayload` |

### `translationsRegister`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `resourceId: string, translations: TranslationInput[]` |
| **Request** | `mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!)` |
| **Returns** | `TranslationsRegisterPayload` |

### `translationsRemove`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `locales: string[], marketIds?: string[], resourceId: string, translationKeys: string[]` |
| **Request** | `mutation translationsRemove($locales: [String!]!, $marketIds: [ID!]!, $resourceId: ID!, $translationKeys: [String!]!)` |
| **Returns** | `TranslationsRemovePayload` |

### `webPresenceCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: WebPresenceCreateInput` |
| **Request** | `mutation webPresenceCreate($input: WebPresenceCreateInput!)` |
| **Returns** | `WebPresenceCreatePayload` |

### `webPresenceDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation webPresenceDelete($id: ID!)` |
| **Returns** | `WebPresenceDeletePayload` |

### `webPresenceUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: WebPresenceUpdateInput` |
| **Request** | `mutation webPresenceUpdate($id: ID!, $input: WebPresenceUpdateInput!)` |
| **Returns** | `WebPresenceUpdatePayload` |

### `webPresences`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query webPresences($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `MarketWebPresenceConnection | null` |

---

## Files & Media

### `fileAcknowledgeUpdateFailed`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fileIds: string[]` |
| **Request** | `mutation fileAcknowledgeUpdateFailed($fileIds: [ID!]!)` |
| **Returns** | `FileAcknowledgeUpdateFailedPayload` |

### `fileCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `files: FileCreateInput[]` |
| **Request** | `mutation fileCreate($files: [FileCreateInput!]!)` |
| **Returns** | `FileCreatePayload` |

### `fileDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `fileIds: string[]` |
| **Request** | `mutation fileDelete($fileIds: [ID!]!)` |
| **Returns** | `FileDeletePayload` |

### `files`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: FileSortKeys` |
| **Request** | `query files($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: FileSortKeys)` |
| **Returns** | `FileConnection` |

### `fileSavedSearches`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query fileSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `SavedSearchConnection` |

### `fileUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `files: FileUpdateInput[]` |
| **Request** | `mutation fileUpdate($files: [FileUpdateInput!]!)` |
| **Returns** | `FileUpdatePayload` |

---

## URL Redirects

### `urlRedirect`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query urlRedirect($id: ID!)` |
| **Returns** | `string` |

### `urlRedirects`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, savedSearchId?: string, sortKey?: UrlRedirectSortKeys` |
| **Request** | `query urlRedirects($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: UrlRedirectSortKeys)` |
| **Returns** | `UrlRedirectConnection` |

### `urlRedirectSavedSearches`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query urlRedirectSavedSearches($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `SavedSearchConnection` |

### `urlRedirectsCount`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `limit?: number, query?: string, savedSearchId?: string` |
| **Request** | `query urlRedirectsCount($limit: Int, $query: String, $savedSearchId: ID)` |
| **Returns** | `Count | null` |

### `urlRedirectBulkDeleteAll`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | _(none)_ |
| **Request** | `mutation urlRedirectBulkDeleteAll` |
| **Returns** | `UrlRedirectBulkDeleteAllPayload` |

### `urlRedirectBulkDeleteByIds`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `ids: string[]` |
| **Request** | `mutation urlRedirectBulkDeleteByIds($ids: [ID!]!)` |
| **Returns** | `UrlRedirectBulkDeleteByIdsPayload` |

### `urlRedirectBulkDeleteBySavedSearch`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `savedSearchId: string` |
| **Request** | `mutation urlRedirectBulkDeleteBySavedSearch($savedSearchId: ID!)` |
| **Returns** | `UrlRedirectBulkDeleteBySavedSearchPayload` |

### `urlRedirectBulkDeleteBySearch`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `search: string` |
| **Request** | `mutation urlRedirectBulkDeleteBySearch($search: String!)` |
| **Returns** | `UrlRedirectBulkDeleteBySearchPayload` |

### `urlRedirectCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `urlRedirect: UrlRedirectInput` |
| **Request** | `mutation urlRedirectCreate($urlRedirect: UrlRedirectInput!)` |
| **Returns** | `UrlRedirectCreatePayload` |

### `urlRedirectDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation urlRedirectDelete($id: ID!)` |
| **Returns** | `UrlRedirectDeletePayload` |

### `urlRedirectImport`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query urlRedirectImport($id: ID!)` |
| **Returns** | `number | null` |

### `urlRedirectImportCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `url: string` |
| **Request** | `mutation urlRedirectImportCreate($url: URL!)` |
| **Returns** | `UrlRedirectImportCreatePayload` |

### `urlRedirectImportSubmit`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation urlRedirectImportSubmit($id: ID!)` |
| **Returns** | `UrlRedirectImportSubmitPayload` |

### `urlRedirectUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, urlRedirect: UrlRedirectInput` |
| **Request** | `mutation urlRedirectUpdate($id: ID!, $urlRedirect: UrlRedirectInput!)` |
| **Returns** | `UrlRedirectUpdatePayload` |

---

## Miscellaneous

### `node`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query node($id: ID!)` |
| **Returns** | `Node | null` |

### `nodes`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `ids: string[]` |
| **Request** | `query nodes($ids: [ID!]!)` |
| **Returns** | `Node | null[]` |

### `job`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query job($id: ID!)` |
| **Returns** | `Job | null` |

### `domain`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query domain($id: ID!)` |
| **Returns** | `Domain | null` |

### `mobilePlatformApplication`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query mobilePlatformApplication($id: ID!)` |
| **Returns** | `string` |

### `mobilePlatformApplications`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query mobilePlatformApplications($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `MobilePlatformApplicationConnection` |

### `mobilePlatformApplicationCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: MobilePlatformApplicationCreateInput` |
| **Request** | `mutation mobilePlatformApplicationCreate($input: MobilePlatformApplicationCreateInput!)` |
| **Returns** | `MobilePlatformApplicationCreatePayload` |

### `mobilePlatformApplicationDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation mobilePlatformApplicationDelete($id: ID!)` |
| **Returns** | `MobilePlatformApplicationDeletePayload` |

### `mobilePlatformApplicationUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, input: MobilePlatformApplicationUpdateInput` |
| **Request** | `mutation mobilePlatformApplicationUpdate($id: ID!, $input: MobilePlatformApplicationUpdateInput!)` |
| **Returns** | `MobilePlatformApplicationUpdatePayload` |

### `cartTransformCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `blockOnFailure?: boolean, functionHandle?: string, metafields?: MetafieldInput[], functionId?: string` |
| **Request** | `mutation cartTransformCreate($blockOnFailure: Boolean, $functionHandle: String, $metafields: [MetafieldInput!]!, $functionId: String)` |
| **Returns** | `CartTransformCreatePayload` |

### `cartTransformDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation cartTransformDelete($id: ID!)` |
| **Returns** | `CartTransformDeletePayload` |

### `cartTransforms`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean` |
| **Request** | `query cartTransforms($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean)` |
| **Returns** | `CartTransformConnection` |

### `storefrontAccessTokenCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: StorefrontAccessTokenInput` |
| **Request** | `mutation storefrontAccessTokenCreate($input: StorefrontAccessTokenInput!)` |
| **Returns** | `StorefrontAccessTokenCreatePayload` |

### `storefrontAccessTokenDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `input: StorefrontAccessTokenDeleteInput` |
| **Request** | `mutation storefrontAccessTokenDelete($input: StorefrontAccessTokenDeleteInput!)` |
| **Returns** | `StorefrontAccessTokenDeletePayload` |

### `shopPayPaymentRequestReceipt`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `token: string` |
| **Request** | `query shopPayPaymentRequestReceipt($token: String!)` |
| **Returns** | `Order | null` |

### `shopPayPaymentRequestReceipts`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, query?: string, reverse?: boolean, sortKey?: ShopPayPaymentRequestReceiptsSortKeys` |
| **Request** | `query shopPayPaymentRequestReceipts($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: ShopPayPaymentRequestReceiptsSortKeys)` |
| **Returns** | `ShopPayPaymentRequestReceiptConnection | null` |

### `validation`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id: string` |
| **Request** | `query validation($id: ID!)` |
| **Returns** | `Validation | null` |

### `validations`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `after?: string, before?: string, first?: number, last?: number, reverse?: boolean, sortKey?: ValidationSortKeys` |
| **Request** | `query validations($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean, $sortKey: ValidationSortKeys)` |
| **Returns** | `ValidationConnection` |

### `validationCreate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `validation: ValidationCreateInput` |
| **Request** | `mutation validationCreate($validation: ValidationCreateInput!)` |
| **Returns** | `ValidationCreatePayload` |

### `validationDelete`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string` |
| **Request** | `mutation validationDelete($id: ID!)` |
| **Returns** | `ValidationDeletePayload` |

### `validationUpdate`
| | |
|---|---|
| **Type** | `mutation` |
| **Args** | `id: string, validation: ValidationUpdateInput` |
| **Request** | `mutation validationUpdate($id: ID!, $validation: ValidationUpdateInput!)` |
| **Returns** | `ValidationUpdatePayload` |

### `businessEntities`
| | |
|---|---|
| **Type** | `query` |
| **Args** | _(none)_ |
| **Request** | `query businessEntities` |
| **Returns** | `BusinessEntityAddress` |

### `businessEntity`
| | |
|---|---|
| **Type** | `query` |
| **Args** | `id?: string` |
| **Request** | `query businessEntity($id: ID)` |
| **Returns** | `BusinessEntityAddress` |

---

