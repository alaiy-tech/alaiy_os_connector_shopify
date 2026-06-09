// Auto-generated Shopify Admin GraphQL API 2026-04 - 510 payload types
// Do not edit manually - regenerate with parse_types.ps1

import type { PrivacyFeaturesEnum } from './enums';
import type { Catalog, File, MarketRegion, Media, Node, Publishable } from './interfaces';
import type { Abandonment, AbandonmentEmailStateUpdateUserError, AbandonmentUpdateActivitiesDeliveryStatusesUserError, AccessScope, App, AppFeedback, AppPurchaseOneTime, AppRevokeAccessScopesAppRevokeScopeError, AppSubscription, AppSubscriptionTrialExtendUserError, AppUninstallAppUninstallError, AppUsageRecord, Article, ArticleCreateUserError, ArticleDeleteUserError, ArticleUpdateUserError, BillingAttemptUserError, Blog, BlogCreateUserError, BlogDeleteUserError, BlogUpdateUserError, BulkMutationUserError, BulkOperation, BulkOperationUserError, BulkProductResourceFeedbackCreateUserError, BusinessCustomerUserError, CalculatedDraftOrder, CalculatedLineItem, CalculatedOrder, CalculatedShippingLine, CarrierServiceCreateUserError, CarrierServiceDeleteUserError, CarrierServiceUpdateUserError, CartTransform, CartTransformCreateUserError, CartTransformDeleteUserError, CashDrawer, CashDrawerCreateUserError, CashDrawerFindOrCreateUserError, CashDrawerUpdateUserError, CashManagementCustomReasonCode, CashManagementReasonCodeCreateUserError, CashManagementReasonCodeDeleteUserError, CatalogUserError, Channel, ChannelCreateUserError, ChannelDeleteUserError, ChannelFullSyncUserError, ChannelUpdateUserError, CheckoutAndAccountsConfiguration, CheckoutAndAccountsConfigurationUserError, CheckoutBranding, CheckoutBrandingUpsertUserError, Collection, CollectionAddProductsV2UserError, CollectionDuplicateUserError, CollectionPublication, CollectionReorderProductsUserError, CombinedListingUpdateUserError, Comment, CommentApproveUserError, CommentDeleteUserError, CommentNotSpamUserError, CommentSpamUserError, Company, CompanyAddress, CompanyContact, CompanyContactRoleAssignment, CompanyLocation, CompanyLocationStaffMemberAssignment, ConsentPolicy, ConsentPolicyError, Customer, CustomerCancelDataErasureUserError, CustomerEmailMarketingConsentUpdateUserError, CustomerMergeUserError, CustomerPaymentMethod, CustomerPaymentMethodGetUpdateUrlUserError, CustomerPaymentMethodRemoteUserError, CustomerPaymentMethodUserError, CustomerRequestDataErasureUserError, CustomerSegmentMembersQuery, CustomerSegmentMembersQueryUserError, CustomerSendAccountInviteEmailUserError, CustomerSetUserError, CustomerSmsMarketingConsentError, DataSaleOptOutUserError, DelegateAccessToken, DelegateAccessTokenCreateUserError, DelegateAccessTokenDestroyUserError, DeliveryCarrierService, DeliveryCustomization, DeliveryCustomizationError, DeliveryLocalPickupSettings, DeliveryLocationLocalPickupSettingsError, DeliveryProfile, DeliveryPromiseParticipant, DeliveryPromiseProvider, DeliveryPromiseProviderUpsertUserError, DiscountAutomaticApp, DiscountAutomaticNode, DiscountCodeApp, DiscountCodeNode, DiscountRedeemCodeBulkCreation, DiscountUserError, DisputeEvidenceUpdateUserError, DraftOrder, ErrorsServerPixelUserError, ErrorsWebPixelUserError, FilesUserError, Fulfillment, FulfillmentConstraintRule, FulfillmentConstraintRuleCreateUserError, FulfillmentConstraintRuleDeleteUserError, FulfillmentConstraintRuleUpdateUserError, FulfillmentEvent, FulfillmentHold, FulfillmentOrder, FulfillmentOrderCancelError, FulfillmentOrderHoldUserError, FulfillmentOrderLineItemsPreparedForPickupUserError, FulfillmentOrderMergeResult, FulfillmentOrderMergeUserError, FulfillmentOrderMoveFulfillmentOrderMoveUserError, FulfillmentOrderReleaseHoldUserError, FulfillmentOrderReportProgressUserError, FulfillmentOrderRescheduleUserError, FulfillmentOrderSplitResult, FulfillmentOrderSplitUserError, FulfillmentOrdersRerouteUserError, FulfillmentOrdersSetFulfillmentDeadlineUserError, FulfillmentService, FullSyncTraceInfo, GiftCard, GiftCardCreditTransaction, GiftCardDeactivateUserError, GiftCardDebitTransaction, GiftCardSendNotificationToCustomerUserError, GiftCardSendNotificationToRecipientUserError, GiftCardTransactionUserError, GiftCardUserError, InventoryAdjustmentGroup, InventoryAdjustQuantitiesUserError, InventoryBulkToggleActivationUserError, InventoryItem, InventoryLevel, InventoryMoveQuantitiesUserError, InventoryScheduledChange, InventorySetOnHandQuantitiesUserError, InventorySetQuantitiesUserError, InventorySetScheduledChangesUserError, InventoryShipment, InventoryShipmentAddItemsUserError, InventoryShipmentCreateInTransitUserError, InventoryShipmentCreateUserError, InventoryShipmentDeleteUserError, InventoryShipmentLineItem, InventoryShipmentMarkInTransitUserError, InventoryShipmentReceiveUserError, InventoryShipmentRemoveItemsUserError, InventoryShipmentSetBarcodeUserError, InventoryShipmentSetTrackingUserError, InventoryShipmentUpdateItemQuantitiesUserError, InventoryTransfer, InventoryTransferCancelUserError, InventoryTransferCreateAsReadyToShipUserError, InventoryTransferCreateUserError, InventoryTransferDeleteUserError, InventoryTransferDuplicateUserError, InventoryTransferEditUserError, InventoryTransferLineItemUpdate, InventoryTransferMarkAsReadyToShipUserError, InventoryTransferRemoveItemsUserError, InventoryTransferSetItemsUserError, Job, Location, LocationActivateUserError, LocationAddUserError, LocationDeactivateUserError, LocationDeleteUserError, LocationEditUserError, MailingAddress, Market, MarketCurrencySettingsUserError, MarketingActivity, MarketingActivityUserError, MarketingEngagement, MarketLocalization, MarketUserError, MarketWebPresence, MediaUserError, Menu, MenuCreateUserError, MenuDeleteUserError, MenuUpdateUserError, Metafield, MetafieldDefinition, MetafieldDefinitionCreateUserError, MetafieldDefinitionDeleteUserError, MetafieldDefinitionIdentifier, MetafieldDefinitionPinUserError, MetafieldDefinitionUnpinUserError, MetafieldDefinitionUpdateUserError, MetafieldIdentifier, MetafieldsSetUserError, Metaobject, MetaobjectDefinition, MetaobjectUserError, MobilePlatformApplicationUserError, MutationsStagedUploadTargetGenerateUploadParameter, OnlineStoreTheme, OnlineStoreThemeFileOperationResult, OnlineStoreThemeFilesUserErrors, Order, OrderCancelUserError, OrderCreateMandatePaymentUserError, OrderCreateManualPaymentOrderCreateManualPaymentError, OrderCreateUserError, OrderCustomerRemoveUserError, OrderCustomerSetUserError, OrderDeleteUserError, OrderEditAddShippingLineUserError, OrderEditRemoveDiscountUserError, OrderEditRemoveShippingLineUserError, OrderEditSession, OrderEditUpdateDiscountUserError, OrderEditUpdateShippingLineUserError, OrderInvoiceSendUserError, OrderRiskAssessment, OrderRiskAssessmentCreateUserError, OrderStagedChangeAddLineItemDiscount, OrderTransaction, Page, PageCreateUserError, PageDeleteUserError, PageUpdateUserError, PaymentCustomization, PaymentCustomizationError, PaymentReminderSendUserError, PaymentTerms, PaymentTermsCreateUserError, PaymentTermsDeleteUserError, PaymentTermsUpdateUserError, PointOfSaleDevice, PointOfSaleDeviceAssignToCashDrawerUserError, PointOfSaleDevicePaymentSession, PointOfSaleDevicePaymentSessionCloseUserError, PointOfSaleDevicePaymentSessionCountUserError, PointOfSaleDevicePaymentSessionOpenUserError, PriceList, PriceListFixedPricesByProductBulkUpdateUserError, PriceListPrice, PriceListPriceUserError, PriceListUserError, PrivacyFeaturesDisableUserError, Product, ProductBundleOperation, ProductChangeStatusUserError, ProductDeleteOperation, ProductDuplicateOperation, ProductFeed, ProductFeedCreateUserError, ProductFeedDeleteUserError, ProductFullSyncUserError, ProductOptionsCreateUserError, ProductOptionsDeleteUserError, ProductOptionsReorderUserError, ProductOptionUpdateUserError, ProductPublication, ProductResourceFeedback, ProductSetOperation, ProductSetUserError, ProductVariant, ProductVariantRelationshipBulkUpdateUserError, ProductVariantsBulkCreateUserError, ProductVariantsBulkDeleteUserError, ProductVariantsBulkReorderUserError, ProductVariantsBulkUpdateUserError, Publication, PublicationUserError, PubSubWebhookSubscriptionCreateUserError, PubSubWebhookSubscriptionUpdateUserError, QuantityPricingByVariantUserError, QuantityRule, QuantityRuleUserError, Refund, Return, ReturnUserError, ReverseDelivery, ReverseFulfillmentOrderLineItem, SavedSearch, ScriptTag, Segment, SellingPlanGroup, SellingPlanGroupUserError, ServerPixel, Shop, ShopifyPaymentsDisputeEvidence, ShopifyPaymentsPayoutAlternateCurrencyCreateUserError, ShopifyPaymentsToolingProviderPayout, ShopLocale, ShopPolicy, ShopPolicyUserError, ShopResourceFeedbackCreateUserError, StagedMediaUploadTarget, StagedUploadTarget, StandardMetafieldDefinitionEnableUserError, StoreCreditAccountCreditTransaction, StoreCreditAccountCreditUserError, StoreCreditAccountDebitTransaction, StoreCreditAccountDebitUserError, StorefrontAccessToken, SubscriptionAppliedCodeDiscount, SubscriptionBillingAttempt, SubscriptionBillingCycle, SubscriptionBillingCycleBulkUserError, SubscriptionBillingCycleEditedContract, SubscriptionBillingCycleSkipUserError, SubscriptionBillingCycleUnskipUserError, SubscriptionBillingCycleUserError, SubscriptionContract, SubscriptionContractStatusUpdateUserError, SubscriptionContractUserError, SubscriptionDraft, SubscriptionDraftUserError, SubscriptionLine, SubscriptionManualDiscount, TaxAppConfiguration, TaxAppConfigureUserError, TaxSummaryCreateUserError, ThemeCreateUserError, ThemeDeleteUserError, ThemeDuplicateUserError, ThemePublishUserError, ThemeUpdateUserError, TransactionVoidUserError, Translation, TranslationUserError, UrlRedirect, UrlRedirectBulkDeleteByIdsUserError, UrlRedirectBulkDeleteBySavedSearchUserError, UrlRedirectBulkDeleteBySearchUserError, UrlRedirectImport, UrlRedirectImportUserError, UrlRedirectUserError, UserError, Validation, ValidationUserError, WebhookSubscription, WebPixel } from './objects';
import type { MobilePlatformApplication, SubscriptionDiscount } from './unions';

/** Return type for `abandonmentEmailStateUpdate` mutation. */
export interface AbandonmentEmailStateUpdatePayload {
  abandonment: Abandonment | null;
  userErrors: AbandonmentEmailStateUpdateUserError[];
}

/** Return type for `abandonmentUpdateActivitiesDeliveryStatuses` mutation. */
export interface AbandonmentUpdateActivitiesDeliveryStatusesPayload {
  abandonment: Abandonment | null;
  userErrors: AbandonmentUpdateActivitiesDeliveryStatusesUserError[];
}

/** Return type for `appPurchaseOneTimeCreate` mutation. */
export interface AppPurchaseOneTimeCreatePayload {
  appPurchaseOneTime: AppPurchaseOneTime | null;
  confirmationUrl: string | null;
  userErrors: UserError[];
}

/** Return type for `appRevokeAccessScopes` mutation. */
export interface AppRevokeAccessScopesPayload {
  revoked: AccessScope[];
  userErrors: AppRevokeAccessScopesAppRevokeScopeError[];
}

/** Return type for `appSubscriptionCancel` mutation. */
export interface AppSubscriptionCancelPayload {
  appSubscription: AppSubscription | null;
  userErrors: UserError[];
}

/** Return type for `appSubscriptionCreate` mutation. */
export interface AppSubscriptionCreatePayload {
  appSubscription: AppSubscription | null;
  confirmationUrl: string | null;
  userErrors: UserError[];
}

/** Return type for `appSubscriptionLineItemUpdate` mutation. */
export interface AppSubscriptionLineItemUpdatePayload {
  appSubscription: AppSubscription | null;
  confirmationUrl: string | null;
  userErrors: UserError[];
}

/** Return type for `appSubscriptionTrialExtend` mutation. */
export interface AppSubscriptionTrialExtendPayload {
  appSubscription: AppSubscription | null;
  userErrors: AppSubscriptionTrialExtendUserError[];
}

/** Return type for `appUninstall` mutation. */
export interface AppUninstallPayload {
  app: App | null;
  userErrors: AppUninstallAppUninstallError[];
}

/** Return type for `appUsageRecordCreate` mutation. */
export interface AppUsageRecordCreatePayload {
  appUsageRecord: AppUsageRecord | null;
  userErrors: UserError[];
}

/** Return type for `articleCreate` mutation. */
export interface ArticleCreatePayload {
  article: Article | null;
  userErrors: ArticleCreateUserError[];
}

/** Return type for `articleDelete` mutation. */
export interface ArticleDeletePayload {
  deletedArticleId: string | null;
  userErrors: ArticleDeleteUserError[];
}

/** Return type for `articleUpdate` mutation. */
export interface ArticleUpdatePayload {
  article: Article | null;
  userErrors: ArticleUpdateUserError[];
}

/** Return type for `backupRegionUpdate` mutation. */
export interface BackupRegionUpdatePayload {
  backupRegion: MarketRegion | null;
  userErrors: MarketUserError[];
}

/** Return type for `blogCreate` mutation. */
export interface BlogCreatePayload {
  blog: Blog | null;
  userErrors: BlogCreateUserError[];
}

/** Return type for `blogDelete` mutation. */
export interface BlogDeletePayload {
  deletedBlogId: string | null;
  userErrors: BlogDeleteUserError[];
}

/** Return type for `blogUpdate` mutation. */
export interface BlogUpdatePayload {
  blog: Blog | null;
  userErrors: BlogUpdateUserError[];
}

/** Return type for `bulkOperationCancel` mutation. */
export interface BulkOperationCancelPayload {
  bulkOperation: BulkOperation | null;
  userErrors: UserError[];
}

/** Return type for `bulkOperationRunMutation` mutation. */
export interface BulkOperationRunMutationPayload {
  bulkOperation: BulkOperation | null;
  userErrors: BulkMutationUserError[];
}

/** Return type for `bulkOperationRunQuery` mutation. */
export interface BulkOperationRunQueryPayload {
  bulkOperation: BulkOperation | null;
  userErrors: BulkOperationUserError[];
}

/** Return type for `bulkProductResourceFeedbackCreate` mutation. */
export interface BulkProductResourceFeedbackCreatePayload {
  feedback: ProductResourceFeedback[];
  userErrors: BulkProductResourceFeedbackCreateUserError[];
}

/** Return type for `carrierServiceCreate` mutation. */
export interface CarrierServiceCreatePayload {
  carrierService: DeliveryCarrierService | null;
  userErrors: CarrierServiceCreateUserError[];
}

/** Return type for `carrierServiceDelete` mutation. */
export interface CarrierServiceDeletePayload {
  deletedId: string | null;
  userErrors: CarrierServiceDeleteUserError[];
}

/** Return type for `carrierServiceUpdate` mutation. */
export interface CarrierServiceUpdatePayload {
  carrierService: DeliveryCarrierService | null;
  userErrors: CarrierServiceUpdateUserError[];
}

/** Return type for `cartTransformCreate` mutation. */
export interface CartTransformCreatePayload {
  cartTransform: CartTransform | null;
  userErrors: CartTransformCreateUserError[];
}

/** Return type for `cartTransformDelete` mutation. */
export interface CartTransformDeletePayload {
  deletedId: string | null;
  userErrors: CartTransformDeleteUserError[];
}

/** Return type for `cashDrawerCreate` mutation. */
export interface CashDrawerCreatePayload {
  cashDrawer: CashDrawer | null;
  userErrors: CashDrawerCreateUserError[];
}

/** Return type for `cashDrawerFindOrCreate` mutation. */
export interface CashDrawerFindOrCreatePayload {
  cashDrawer: CashDrawer | null;
  userErrors: CashDrawerFindOrCreateUserError[];
}

/** Return type for `cashDrawerUpdate` mutation. */
export interface CashDrawerUpdatePayload {
  cashDrawer: CashDrawer | null;
  userErrors: CashDrawerUpdateUserError[];
}

/** Return type for `cashManagementReasonCodeCreate` mutation. */
export interface CashManagementReasonCodeCreatePayload {
  reasonCode: CashManagementCustomReasonCode | null;
  userErrors: CashManagementReasonCodeCreateUserError[];
}

/** Return type for `cashManagementReasonCodeDelete` mutation. */
export interface CashManagementReasonCodeDeletePayload {
  deletedId: string | null;
  userErrors: CashManagementReasonCodeDeleteUserError[];
}

/** Return type for `catalogContextUpdate` mutation. */
export interface CatalogContextUpdatePayload {
  catalog: Catalog | null;
  userErrors: CatalogUserError[];
}

/** Return type for `catalogCreate` mutation. */
export interface CatalogCreatePayload {
  catalog: Catalog | null;
  userErrors: CatalogUserError[];
}

/** Return type for `catalogDelete` mutation. */
export interface CatalogDeletePayload {
  deletedId: string | null;
  userErrors: CatalogUserError[];
}

/** Return type for `catalogUpdate` mutation. */
export interface CatalogUpdatePayload {
  catalog: Catalog | null;
  userErrors: CatalogUserError[];
}

/** Return type for `channelCreate` mutation. */
export interface ChannelCreatePayload {
  channel: Channel | null;
  userErrors: ChannelCreateUserError[];
}

/** Return type for `channelDelete` mutation. */
export interface ChannelDeletePayload {
  deletedId: string | null;
  userErrors: ChannelDeleteUserError[];
}

/** Return type for `channelFullSync` mutation. */
export interface ChannelFullSyncPayload {
  fullSyncTraceInfo: FullSyncTraceInfo[];
  userErrors: ChannelFullSyncUserError[];
}

/** Return type for `channelUpdate` mutation. */
export interface ChannelUpdatePayload {
  channel: Channel | null;
  userErrors: ChannelUpdateUserError[];
}

/** Return type for `checkoutAndAccountsConfigurationUpdate` mutation. */
export interface CheckoutAndAccountsConfigurationUpdatePayload {
  configuration: CheckoutAndAccountsConfiguration | null;
  userErrors: CheckoutAndAccountsConfigurationUserError[];
}

/** Return type for `checkoutBrandingUpsert` mutation. */
export interface CheckoutBrandingUpsertPayload {
  checkoutBranding: CheckoutBranding | null;
  userErrors: CheckoutBrandingUpsertUserError[];
}

/** Return type for `collectionAddProducts` mutation. */
export interface CollectionAddProductsPayload {
  collection: Collection | null;
  userErrors: UserError[];
}

/** Return type for `collectionAddProductsV2` mutation. */
export interface CollectionAddProductsV2Payload {
  job: Job | null;
  userErrors: CollectionAddProductsV2UserError[];
}

/** Return type for `collectionCreate` mutation. */
export interface CollectionCreatePayload {
  collection: Collection | null;
  userErrors: UserError[];
}

/** Return type for `collectionDelete` mutation. */
export interface CollectionDeletePayload {
  deletedCollectionId: string | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `collectionDuplicate` mutation. */
export interface CollectionDuplicatePayload {
  collection: Collection | null;
  job: Job | null;
  userErrors: CollectionDuplicateUserError[];
}

/** Return type for `collectionPublish` mutation. */
export interface CollectionPublishPayload {
  collection: Collection | null;
  collectionPublications: CollectionPublication[];
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `collectionRemoveProducts` mutation. */
export interface CollectionRemoveProductsPayload {
  job: Job | null;
  userErrors: UserError[];
}

/** Return type for `collectionReorderProducts` mutation. */
export interface CollectionReorderProductsPayload {
  job: Job | null;
  userErrors: CollectionReorderProductsUserError[];
}

/** Return type for `collectionUnpublish` mutation. */
export interface CollectionUnpublishPayload {
  collection: Collection | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `collectionUpdate` mutation. */
export interface CollectionUpdatePayload {
  collection: Collection | null;
  job: Job | null;
  userErrors: UserError[];
}

/** Return type for `combinedListingUpdate` mutation. */
export interface CombinedListingUpdatePayload {
  product: Product | null;
  userErrors: CombinedListingUpdateUserError[];
}

/** Return type for `commentApprove` mutation. */
export interface CommentApprovePayload {
  comment: Comment | null;
  userErrors: CommentApproveUserError[];
}

/** Return type for `commentDelete` mutation. */
export interface CommentDeletePayload {
  deletedCommentId: string | null;
  userErrors: CommentDeleteUserError[];
}

/** Return type for `commentNotSpam` mutation. */
export interface CommentNotSpamPayload {
  comment: Comment | null;
  userErrors: CommentNotSpamUserError[];
}

/** Return type for `commentSpam` mutation. */
export interface CommentSpamPayload {
  comment: Comment | null;
  userErrors: CommentSpamUserError[];
}

/** Return type for `companiesDelete` mutation. */
export interface CompaniesDeletePayload {
  deletedCompanyIds: string[];
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyAddressDelete` mutation. */
export interface CompanyAddressDeletePayload {
  deletedAddressId: string | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyAssignCustomerAsContact` mutation. */
export interface CompanyAssignCustomerAsContactPayload {
  companyContact: CompanyContact | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyAssignMainContact` mutation. */
export interface CompanyAssignMainContactPayload {
  company: Company | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyContactAssignRole` mutation. */
export interface CompanyContactAssignRolePayload {
  companyContactRoleAssignment: CompanyContactRoleAssignment | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyContactAssignRoles` mutation. */
export interface CompanyContactAssignRolesPayload {
  roleAssignments: CompanyContactRoleAssignment[];
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyContactCreate` mutation. */
export interface CompanyContactCreatePayload {
  companyContact: CompanyContact | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyContactDelete` mutation. */
export interface CompanyContactDeletePayload {
  deletedCompanyContactId: string | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyContactRemoveFromCompany` mutation. */
export interface CompanyContactRemoveFromCompanyPayload {
  removedCompanyContactId: string | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyContactRevokeRole` mutation. */
export interface CompanyContactRevokeRolePayload {
  revokedCompanyContactRoleAssignmentId: string | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyContactRevokeRoles` mutation. */
export interface CompanyContactRevokeRolesPayload {
  revokedRoleAssignmentIds: string[];
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyContactsDelete` mutation. */
export interface CompanyContactsDeletePayload {
  deletedCompanyContactIds: string[];
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyContactUpdate` mutation. */
export interface CompanyContactUpdatePayload {
  companyContact: CompanyContact | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyCreate` mutation. */
export interface CompanyCreatePayload {
  company: Company | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyDelete` mutation. */
export interface CompanyDeletePayload {
  deletedCompanyId: string | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationAssignAddress` mutation. */
export interface CompanyLocationAssignAddressPayload {
  addresses: CompanyAddress[];
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationAssignRoles` mutation. */
export interface CompanyLocationAssignRolesPayload {
  roleAssignments: CompanyContactRoleAssignment[];
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationAssignStaffMembers` mutation. */
export interface CompanyLocationAssignStaffMembersPayload {
  companyLocationStaffMemberAssignments: CompanyLocationStaffMemberAssignment[];
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationAssignTaxExemptions` mutation. */
export interface CompanyLocationAssignTaxExemptionsPayload {
  companyLocation: CompanyLocation | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationCreate` mutation. */
export interface CompanyLocationCreatePayload {
  companyLocation: CompanyLocation | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationCreateTaxRegistration` mutation. */
export interface CompanyLocationCreateTaxRegistrationPayload {
  companyLocation: CompanyLocation | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationDelete` mutation. */
export interface CompanyLocationDeletePayload {
  deletedCompanyLocationId: string | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationRemoveStaffMembers` mutation. */
export interface CompanyLocationRemoveStaffMembersPayload {
  deletedCompanyLocationStaffMemberAssignmentIds: string[];
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationRevokeRoles` mutation. */
export interface CompanyLocationRevokeRolesPayload {
  revokedRoleAssignmentIds: string[];
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationRevokeTaxExemptions` mutation. */
export interface CompanyLocationRevokeTaxExemptionsPayload {
  companyLocation: CompanyLocation | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationRevokeTaxRegistration` mutation. */
export interface CompanyLocationRevokeTaxRegistrationPayload {
  companyLocation: CompanyLocation | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationsDelete` mutation. */
export interface CompanyLocationsDeletePayload {
  deletedCompanyLocationIds: string[];
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationTaxSettingsUpdate` mutation. */
export interface CompanyLocationTaxSettingsUpdatePayload {
  companyLocation: CompanyLocation | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyLocationUpdate` mutation. */
export interface CompanyLocationUpdatePayload {
  companyLocation: CompanyLocation | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyRevokeMainContact` mutation. */
export interface CompanyRevokeMainContactPayload {
  company: Company | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `companyUpdate` mutation. */
export interface CompanyUpdatePayload {
  company: Company | null;
  userErrors: BusinessCustomerUserError[];
}

/** Return type for `consentPolicyUpdate` mutation. */
export interface ConsentPolicyUpdatePayload {
  updatedPolicies: ConsentPolicy[];
  userErrors: ConsentPolicyError[];
}

/** Return type for `customerAddressCreate` mutation. */
export interface CustomerAddressCreatePayload {
  address: MailingAddress | null;
  userErrors: UserError[];
}

/** Return type for `customerAddressDelete` mutation. */
export interface CustomerAddressDeletePayload {
  deletedAddressId: string | null;
  userErrors: UserError[];
}

/** Return type for `customerAddressUpdate` mutation. */
export interface CustomerAddressUpdatePayload {
  address: MailingAddress | null;
  userErrors: UserError[];
}

/** Return type for `customerAddTaxExemptions` mutation. */
export interface CustomerAddTaxExemptionsPayload {
  customer: Customer | null;
  userErrors: UserError[];
}

/** Return type for `customerCancelDataErasure` mutation. */
export interface CustomerCancelDataErasurePayload {
  customerId: string | null;
  userErrors: CustomerCancelDataErasureUserError[];
}

/** Return type for `customerCreate` mutation. */
export interface CustomerCreatePayload {
  customer: Customer | null;
  userErrors: UserError[];
}

/** Return type for `customerDelete` mutation. */
export interface CustomerDeletePayload {
  deletedCustomerId: string | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `customerEmailMarketingConsentUpdate` mutation. */
export interface CustomerEmailMarketingConsentUpdatePayload {
  customer: Customer | null;
  userErrors: CustomerEmailMarketingConsentUpdateUserError[];
}

/** Return type for `customerGenerateAccountActivationUrl` mutation. */
export interface CustomerGenerateAccountActivationUrlPayload {
  accountActivationUrl: string | null;
  userErrors: UserError[];
}

/** Return type for `customerMerge` mutation. */
export interface CustomerMergePayload {
  job: Job | null;
  resultingCustomerId: string | null;
  userErrors: CustomerMergeUserError[];
}

/** Return type for `customerPaymentMethodCreditCardCreate` mutation. */
export interface CustomerPaymentMethodCreditCardCreatePayload {
  customerPaymentMethod: CustomerPaymentMethod | null;
  processing: boolean | null;
  userErrors: UserError[];
}

/** Return type for `customerPaymentMethodCreditCardUpdate` mutation. */
export interface CustomerPaymentMethodCreditCardUpdatePayload {
  customerPaymentMethod: CustomerPaymentMethod | null;
  processing: boolean | null;
  userErrors: UserError[];
}

/** Return type for `customerPaymentMethodGetUpdateUrl` mutation. */
export interface CustomerPaymentMethodGetUpdateUrlPayload {
  updatePaymentMethodUrl: string | null;
  userErrors: CustomerPaymentMethodGetUpdateUrlUserError[];
}

/** Return type for `customerPaymentMethodPaypalBillingAgreementCreate` mutation. */
export interface CustomerPaymentMethodPaypalBillingAgreementCreatePayload {
  customerPaymentMethod: CustomerPaymentMethod | null;
  userErrors: CustomerPaymentMethodUserError[];
}

/** Return type for `customerPaymentMethodPaypalBillingAgreementUpdate` mutation. */
export interface CustomerPaymentMethodPaypalBillingAgreementUpdatePayload {
  customerPaymentMethod: CustomerPaymentMethod | null;
  userErrors: CustomerPaymentMethodUserError[];
}

/** Return type for `customerPaymentMethodRemoteCreate` mutation. */
export interface CustomerPaymentMethodRemoteCreatePayload {
  customerPaymentMethod: CustomerPaymentMethod | null;
  userErrors: CustomerPaymentMethodRemoteUserError[];
}

/** Return type for `customerPaymentMethodRevoke` mutation. */
export interface CustomerPaymentMethodRevokePayload {
  revokedCustomerPaymentMethodId: string | null;
  userErrors: UserError[];
}

/** Return type for `customerPaymentMethodSendUpdateEmail` mutation. */
export interface CustomerPaymentMethodSendUpdateEmailPayload {
  customer: Customer | null;
  userErrors: UserError[];
}

/** Return type for `customerRemoveTaxExemptions` mutation. */
export interface CustomerRemoveTaxExemptionsPayload {
  customer: Customer | null;
  userErrors: UserError[];
}

/** Return type for `customerReplaceTaxExemptions` mutation. */
export interface CustomerReplaceTaxExemptionsPayload {
  customer: Customer | null;
  userErrors: UserError[];
}

/** Return type for `customerRequestDataErasure` mutation. */
export interface CustomerRequestDataErasurePayload {
  customerId: string | null;
  userErrors: CustomerRequestDataErasureUserError[];
}

/** Return type for `customerSegmentMembersQueryCreate` mutation. */
export interface CustomerSegmentMembersQueryCreatePayload {
  customerSegmentMembersQuery: CustomerSegmentMembersQuery | null;
  userErrors: CustomerSegmentMembersQueryUserError[];
}

/** Return type for `customerSendAccountInviteEmail` mutation. */
export interface CustomerSendAccountInviteEmailPayload {
  customer: Customer | null;
  userErrors: CustomerSendAccountInviteEmailUserError[];
}

/** Return type for `customerSet` mutation. */
export interface CustomerSetPayload {
  customer: Customer | null;
  userErrors: CustomerSetUserError[];
}

/** Return type for `customerSmsMarketingConsentUpdate` mutation. */
export interface CustomerSmsMarketingConsentUpdatePayload {
  customer: Customer | null;
  userErrors: CustomerSmsMarketingConsentError[];
}

/** Return type for `customerUpdateDefaultAddress` mutation. */
export interface CustomerUpdateDefaultAddressPayload {
  customer: Customer | null;
  userErrors: UserError[];
}

/** Return type for `customerUpdate` mutation. */
export interface CustomerUpdatePayload {
  customer: Customer | null;
  userErrors: UserError[];
}

/** Return type for `dataSaleOptOut` mutation. */
export interface DataSaleOptOutPayload {
  customerId: string | null;
  userErrors: DataSaleOptOutUserError[];
}

/** Return type for `delegateAccessTokenCreate` mutation. */
export interface DelegateAccessTokenCreatePayload {
  delegateAccessToken: DelegateAccessToken | null;
  shop: Shop;
  userErrors: DelegateAccessTokenCreateUserError[];
}

/** Return type for `delegateAccessTokenDestroy` mutation. */
export interface DelegateAccessTokenDestroyPayload {
  shop: Shop;
  status: boolean | null;
  userErrors: DelegateAccessTokenDestroyUserError[];
}

/** Return type for `deliveryCustomizationActivation` mutation. */
export interface DeliveryCustomizationActivationPayload {
  ids: string[];
  userErrors: DeliveryCustomizationError[];
}

/** Return type for `deliveryCustomizationCreate` mutation. */
export interface DeliveryCustomizationCreatePayload {
  deliveryCustomization: DeliveryCustomization | null;
  userErrors: DeliveryCustomizationError[];
}

/** Return type for `deliveryCustomizationDelete` mutation. */
export interface DeliveryCustomizationDeletePayload {
  deletedId: string | null;
  userErrors: DeliveryCustomizationError[];
}

/** Return type for `deliveryCustomizationUpdate` mutation. */
export interface DeliveryCustomizationUpdatePayload {
  deliveryCustomization: DeliveryCustomization | null;
  userErrors: DeliveryCustomizationError[];
}

/** Return type for `deliveryProfileCreate` mutation. */
export interface DeliveryProfileCreatePayload {
  profile: DeliveryProfile | null;
  userErrors: UserError[];
}

/** Return type for `deliveryProfileRemove` mutation. */
export interface DeliveryProfileRemovePayload {
  job: Job | null;
  userErrors: UserError[];
}

/** Return type for `deliveryProfileUpdate` mutation. */
export interface DeliveryProfileUpdatePayload {
  profile: DeliveryProfile | null;
  userErrors: UserError[];
}

/** Return type for `deliveryPromiseParticipantsUpdate` mutation. */
export interface DeliveryPromiseParticipantsUpdatePayload {
  promiseParticipants: DeliveryPromiseParticipant[];
  userErrors: UserError[];
}

/** Return type for `deliveryPromiseProviderUpsert` mutation. */
export interface DeliveryPromiseProviderUpsertPayload {
  deliveryPromiseProvider: DeliveryPromiseProvider | null;
  userErrors: DeliveryPromiseProviderUpsertUserError[];
}

/** Return type for `deliverySettingUpdate` mutation. */
export interface DeliverySettingUpdatePayload {
  userErrors: UserError[];
}

/** Return type for `deliveryShippingOriginAssign` mutation. */
export interface DeliveryShippingOriginAssignPayload {
  userErrors: UserError[];
}

/** Return type for `discountAutomaticActivate` mutation. */
export interface DiscountAutomaticActivatePayload {
  automaticDiscountNode: DiscountAutomaticNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticAppCreate` mutation. */
export interface DiscountAutomaticAppCreatePayload {
  automaticAppDiscount: DiscountAutomaticApp | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticAppUpdate` mutation. */
export interface DiscountAutomaticAppUpdatePayload {
  automaticAppDiscount: DiscountAutomaticApp | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticBasicCreate` mutation. */
export interface DiscountAutomaticBasicCreatePayload {
  automaticDiscountNode: DiscountAutomaticNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticBasicUpdate` mutation. */
export interface DiscountAutomaticBasicUpdatePayload {
  automaticDiscountNode: DiscountAutomaticNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticBulkDelete` mutation. */
export interface DiscountAutomaticBulkDeletePayload {
  job: Job | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticBxgyCreate` mutation. */
export interface DiscountAutomaticBxgyCreatePayload {
  automaticDiscountNode: DiscountAutomaticNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticBxgyUpdate` mutation. */
export interface DiscountAutomaticBxgyUpdatePayload {
  automaticDiscountNode: DiscountAutomaticNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticDeactivate` mutation. */
export interface DiscountAutomaticDeactivatePayload {
  automaticDiscountNode: DiscountAutomaticNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticDelete` mutation. */
export interface DiscountAutomaticDeletePayload {
  deletedAutomaticDiscountId: string | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticFreeShippingCreate` mutation. */
export interface DiscountAutomaticFreeShippingCreatePayload {
  automaticDiscountNode: DiscountAutomaticNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountAutomaticFreeShippingUpdate` mutation. */
export interface DiscountAutomaticFreeShippingUpdatePayload {
  automaticDiscountNode: DiscountAutomaticNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountBulkTagsAdd` mutation. */
export interface DiscountBulkTagsAddPayload {
  job: Job | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountBulkTagsRemove` mutation. */
export interface DiscountBulkTagsRemovePayload {
  job: Job | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeActivate` mutation. */
export interface DiscountCodeActivatePayload {
  codeDiscountNode: DiscountCodeNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeAppCreate` mutation. */
export interface DiscountCodeAppCreatePayload {
  codeAppDiscount: DiscountCodeApp | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeAppUpdate` mutation. */
export interface DiscountCodeAppUpdatePayload {
  codeAppDiscount: DiscountCodeApp | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeBasicCreate` mutation. */
export interface DiscountCodeBasicCreatePayload {
  codeDiscountNode: DiscountCodeNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeBasicUpdate` mutation. */
export interface DiscountCodeBasicUpdatePayload {
  codeDiscountNode: DiscountCodeNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeBulkActivate` mutation. */
export interface DiscountCodeBulkActivatePayload {
  job: Job | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeBulkDeactivate` mutation. */
export interface DiscountCodeBulkDeactivatePayload {
  job: Job | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeBulkDelete` mutation. */
export interface DiscountCodeBulkDeletePayload {
  job: Job | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeBxgyCreate` mutation. */
export interface DiscountCodeBxgyCreatePayload {
  codeDiscountNode: DiscountCodeNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeBxgyUpdate` mutation. */
export interface DiscountCodeBxgyUpdatePayload {
  codeDiscountNode: DiscountCodeNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeDeactivate` mutation. */
export interface DiscountCodeDeactivatePayload {
  codeDiscountNode: DiscountCodeNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeDelete` mutation. */
export interface DiscountCodeDeletePayload {
  deletedCodeDiscountId: string | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeFreeShippingCreate` mutation. */
export interface DiscountCodeFreeShippingCreatePayload {
  codeDiscountNode: DiscountCodeNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeFreeShippingUpdate` mutation. */
export interface DiscountCodeFreeShippingUpdatePayload {
  codeDiscountNode: DiscountCodeNode | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountCodeRedeemCodeBulkDelete` mutation. */
export interface DiscountCodeRedeemCodeBulkDeletePayload {
  job: Job | null;
  userErrors: DiscountUserError[];
}

/** Return type for `discountRedeemCodeBulkAdd` mutation. */
export interface DiscountRedeemCodeBulkAddPayload {
  bulkCreation: DiscountRedeemCodeBulkCreation | null;
  userErrors: DiscountUserError[];
}

/** Return type for `disputeEvidenceUpdate` mutation. */
export interface DisputeEvidenceUpdatePayload {
  disputeEvidence: ShopifyPaymentsDisputeEvidence | null;
  userErrors: DisputeEvidenceUpdateUserError[];
}

/** Return type for `draftOrderBulkAddTags` mutation. */
export interface DraftOrderBulkAddTagsPayload {
  job: Job | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderBulkDelete` mutation. */
export interface DraftOrderBulkDeletePayload {
  job: Job | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderBulkRemoveTags` mutation. */
export interface DraftOrderBulkRemoveTagsPayload {
  job: Job | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderCalculate` mutation. */
export interface DraftOrderCalculatePayload {
  calculatedDraftOrder: CalculatedDraftOrder | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderComplete` mutation. */
export interface DraftOrderCompletePayload {
  draftOrder: DraftOrder | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderCreateFromOrder` mutation. */
export interface DraftOrderCreateFromOrderPayload {
  draftOrder: DraftOrder | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderCreate` mutation. */
export interface DraftOrderCreatePayload {
  draftOrder: DraftOrder | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderDelete` mutation. */
export interface DraftOrderDeletePayload {
  deletedId: string | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderDuplicate` mutation. */
export interface DraftOrderDuplicatePayload {
  draftOrder: DraftOrder | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderInvoicePreview` mutation. */
export interface DraftOrderInvoicePreviewPayload {
  previewHtml: string | null;
  previewSubject: string | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderInvoiceSend` mutation. */
export interface DraftOrderInvoiceSendPayload {
  draftOrder: DraftOrder | null;
  userErrors: UserError[];
}

/** Return type for `draftOrderUpdate` mutation. */
export interface DraftOrderUpdatePayload {
  draftOrder: DraftOrder | null;
  userErrors: UserError[];
}

/** Return type for `eventBridgeServerPixelUpdate` mutation. */
export interface EventBridgeServerPixelUpdatePayload {
  serverPixel: ServerPixel | null;
  userErrors: ErrorsServerPixelUserError[];
}

/** Return type for `eventBridgeWebhookSubscriptionCreate` mutation. */
export interface EventBridgeWebhookSubscriptionCreatePayload {
  userErrors: UserError[];
  webhookSubscription: WebhookSubscription | null;
}

/** Return type for `eventBridgeWebhookSubscriptionUpdate` mutation. */
export interface EventBridgeWebhookSubscriptionUpdatePayload {
  userErrors: UserError[];
  webhookSubscription: WebhookSubscription | null;
}

/** Return type for `fileAcknowledgeUpdateFailed` mutation. */
export interface FileAcknowledgeUpdateFailedPayload {
  files: File[];
  userErrors: FilesUserError[];
}

/** Return type for `fileCreate` mutation. */
export interface FileCreatePayload {
  files: File[];
  userErrors: FilesUserError[];
}

/** Return type for `fileDelete` mutation. */
export interface FileDeletePayload {
  deletedFileIds: string[];
  userErrors: FilesUserError[];
}

/** Return type for `fileUpdate` mutation. */
export interface FileUpdatePayload {
  files: File[];
  userErrors: FilesUserError[];
}

/** Return type for `flowTriggerReceive` mutation. */
export interface FlowTriggerReceivePayload {
  userErrors: UserError[];
}

/** Return type for `fulfillmentCancel` mutation. */
export interface FulfillmentCancelPayload {
  fulfillment: Fulfillment | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentConstraintRuleCreate` mutation. */
export interface FulfillmentConstraintRuleCreatePayload {
  fulfillmentConstraintRule: FulfillmentConstraintRule | null;
  userErrors: FulfillmentConstraintRuleCreateUserError[];
}

/** Return type for `fulfillmentConstraintRuleDelete` mutation. */
export interface FulfillmentConstraintRuleDeletePayload {
  success: boolean | null;
  userErrors: FulfillmentConstraintRuleDeleteUserError[];
}

/** Return type for `fulfillmentConstraintRuleUpdate` mutation. */
export interface FulfillmentConstraintRuleUpdatePayload {
  fulfillmentConstraintRule: FulfillmentConstraintRule | null;
  userErrors: FulfillmentConstraintRuleUpdateUserError[];
}

/** Return type for `fulfillmentCreate` mutation. */
export interface FulfillmentCreatePayload {
  fulfillment: Fulfillment | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentCreateV2` mutation. */
export interface FulfillmentCreateV2Payload {
  fulfillment: Fulfillment | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentEventCreate` mutation. */
export interface FulfillmentEventCreatePayload {
  fulfillmentEvent: FulfillmentEvent | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentOrderAcceptCancellationRequest` mutation. */
export interface FulfillmentOrderAcceptCancellationRequestPayload {
  fulfillmentOrder: FulfillmentOrder | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentOrderAcceptFulfillmentRequest` mutation. */
export interface FulfillmentOrderAcceptFulfillmentRequestPayload {
  fulfillmentOrder: FulfillmentOrder | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentOrderCancel` mutation. */
export interface FulfillmentOrderCancelPayload {
  fulfillmentOrder: FulfillmentOrder | null;
  replacementFulfillmentOrder: FulfillmentOrder | null;
  userErrors: FulfillmentOrderCancelError[];
}

/** Return type for `fulfillmentOrderClose` mutation. */
export interface FulfillmentOrderClosePayload {
  fulfillmentOrder: FulfillmentOrder | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentOrderHold` mutation. */
export interface FulfillmentOrderHoldPayload {
  fulfillmentHold: FulfillmentHold | null;
  fulfillmentOrder: FulfillmentOrder | null;
  remainingFulfillmentOrder: FulfillmentOrder | null;
  userErrors: FulfillmentOrderHoldUserError[];
}

/** Return type for `fulfillmentOrderLineItemsPreparedForPickup` mutation. */
export interface FulfillmentOrderLineItemsPreparedForPickupPayload {
  userErrors: FulfillmentOrderLineItemsPreparedForPickupUserError[];
}

/** Return type for `fulfillmentOrderMerge` mutation. */
export interface FulfillmentOrderMergePayload {
  fulfillmentOrderMerges: FulfillmentOrderMergeResult[];
  userErrors: FulfillmentOrderMergeUserError[];
}

/** Return type for `fulfillmentOrderMove` mutation. */
export interface FulfillmentOrderMovePayload {
  movedFulfillmentOrder: FulfillmentOrder | null;
  originalFulfillmentOrder: FulfillmentOrder | null;
  remainingFulfillmentOrder: FulfillmentOrder | null;
  userErrors: FulfillmentOrderMoveFulfillmentOrderMoveUserError[];
}

/** Return type for `fulfillmentOrderOpen` mutation. */
export interface FulfillmentOrderOpenPayload {
  fulfillmentOrder: FulfillmentOrder | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentOrderRejectCancellationRequest` mutation. */
export interface FulfillmentOrderRejectCancellationRequestPayload {
  fulfillmentOrder: FulfillmentOrder | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentOrderRejectFulfillmentRequest` mutation. */
export interface FulfillmentOrderRejectFulfillmentRequestPayload {
  fulfillmentOrder: FulfillmentOrder | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentOrderReleaseHold` mutation. */
export interface FulfillmentOrderReleaseHoldPayload {
  fulfillmentOrder: FulfillmentOrder | null;
  userErrors: FulfillmentOrderReleaseHoldUserError[];
}

/** Return type for `fulfillmentOrderReportProgress` mutation. */
export interface FulfillmentOrderReportProgressPayload {
  fulfillmentOrder: FulfillmentOrder | null;
  userErrors: FulfillmentOrderReportProgressUserError[];
}

/** Return type for `fulfillmentOrderReschedule` mutation. */
export interface FulfillmentOrderReschedulePayload {
  fulfillmentOrder: FulfillmentOrder | null;
  userErrors: FulfillmentOrderRescheduleUserError[];
}

/** Return type for `fulfillmentOrderSplit` mutation. */
export interface FulfillmentOrderSplitPayload {
  fulfillmentOrderSplits: FulfillmentOrderSplitResult[];
  userErrors: FulfillmentOrderSplitUserError[];
}

/** Return type for `fulfillmentOrdersReroute` mutation. */
export interface FulfillmentOrdersReroutePayload {
  movedFulfillmentOrders: FulfillmentOrder[];
  userErrors: FulfillmentOrdersRerouteUserError[];
}

/** Return type for `fulfillmentOrdersSetFulfillmentDeadline` mutation. */
export interface FulfillmentOrdersSetFulfillmentDeadlinePayload {
  success: boolean | null;
  userErrors: FulfillmentOrdersSetFulfillmentDeadlineUserError[];
}

/** Return type for `fulfillmentOrderSubmitCancellationRequest` mutation. */
export interface FulfillmentOrderSubmitCancellationRequestPayload {
  fulfillmentOrder: FulfillmentOrder | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentOrderSubmitFulfillmentRequest` mutation. */
export interface FulfillmentOrderSubmitFulfillmentRequestPayload {
  originalFulfillmentOrder: FulfillmentOrder | null;
  submittedFulfillmentOrder: FulfillmentOrder | null;
  unsubmittedFulfillmentOrder: FulfillmentOrder | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentServiceCreate` mutation. */
export interface FulfillmentServiceCreatePayload {
  fulfillmentService: FulfillmentService | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentServiceDelete` mutation. */
export interface FulfillmentServiceDeletePayload {
  deletedId: string | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentServiceUpdate` mutation. */
export interface FulfillmentServiceUpdatePayload {
  fulfillmentService: FulfillmentService | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentTrackingInfoUpdate` mutation. */
export interface FulfillmentTrackingInfoUpdatePayload {
  fulfillment: Fulfillment | null;
  userErrors: UserError[];
}

/** Return type for `fulfillmentTrackingInfoUpdateV2` mutation. */
export interface FulfillmentTrackingInfoUpdateV2Payload {
  fulfillment: Fulfillment | null;
  userErrors: UserError[];
}

/** Return type for `giftCardCreate` mutation. */
export interface GiftCardCreatePayload {
  giftCard: GiftCard | null;
  giftCardCode: string | null;
  userErrors: GiftCardUserError[];
}

/** Return type for `giftCardCredit` mutation. */
export interface GiftCardCreditPayload {
  giftCardCreditTransaction: GiftCardCreditTransaction | null;
  userErrors: GiftCardTransactionUserError[];
}

/** Return type for `giftCardDeactivate` mutation. */
export interface GiftCardDeactivatePayload {
  giftCard: GiftCard | null;
  userErrors: GiftCardDeactivateUserError[];
}

/** Return type for `giftCardDebit` mutation. */
export interface GiftCardDebitPayload {
  giftCardDebitTransaction: GiftCardDebitTransaction | null;
  userErrors: GiftCardTransactionUserError[];
}

/** Return type for `giftCardSendNotificationToCustomer` mutation. */
export interface GiftCardSendNotificationToCustomerPayload {
  giftCard: GiftCard | null;
  userErrors: GiftCardSendNotificationToCustomerUserError[];
}

/** Return type for `giftCardSendNotificationToRecipient` mutation. */
export interface GiftCardSendNotificationToRecipientPayload {
  giftCard: GiftCard | null;
  userErrors: GiftCardSendNotificationToRecipientUserError[];
}

/** Return type for `giftCardUpdate` mutation. */
export interface GiftCardUpdatePayload {
  giftCard: GiftCard | null;
  userErrors: UserError[];
}

/** Return type for `inventoryActivate` mutation. */
export interface InventoryActivatePayload {
  inventoryLevel: InventoryLevel | null;
  userErrors: UserError[];
}

/** Return type for `inventoryAdjustQuantities` mutation. */
export interface InventoryAdjustQuantitiesPayload {
  inventoryAdjustmentGroup: InventoryAdjustmentGroup | null;
  userErrors: InventoryAdjustQuantitiesUserError[];
}

/** Return type for `inventoryBulkToggleActivation` mutation. */
export interface InventoryBulkToggleActivationPayload {
  inventoryItem: InventoryItem | null;
  inventoryLevels: InventoryLevel[];
  userErrors: InventoryBulkToggleActivationUserError[];
}

/** Return type for `inventoryDeactivate` mutation. */
export interface InventoryDeactivatePayload {
  userErrors: UserError[];
}

/** Return type for `inventoryItemUpdate` mutation. */
export interface InventoryItemUpdatePayload {
  inventoryItem: InventoryItem | null;
  userErrors: UserError[];
}

/** Return type for `inventoryMoveQuantities` mutation. */
export interface InventoryMoveQuantitiesPayload {
  inventoryAdjustmentGroup: InventoryAdjustmentGroup | null;
  userErrors: InventoryMoveQuantitiesUserError[];
}

/** Return type for `inventorySetOnHandQuantities` mutation. */
export interface InventorySetOnHandQuantitiesPayload {
  inventoryAdjustmentGroup: InventoryAdjustmentGroup | null;
  userErrors: InventorySetOnHandQuantitiesUserError[];
}

/** Return type for `inventorySetQuantities` mutation. */
export interface InventorySetQuantitiesPayload {
  inventoryAdjustmentGroup: InventoryAdjustmentGroup | null;
  userErrors: InventorySetQuantitiesUserError[];
}

/** Return type for `inventorySetScheduledChanges` mutation. */
export interface InventorySetScheduledChangesPayload {
  scheduledChanges: InventoryScheduledChange[];
  userErrors: InventorySetScheduledChangesUserError[];
}

/** Return type for `inventoryShipmentAddItems` mutation. */
export interface InventoryShipmentAddItemsPayload {
  addedItems: InventoryShipmentLineItem[];
  inventoryShipment: InventoryShipment | null;
  userErrors: InventoryShipmentAddItemsUserError[];
}

/** Return type for `inventoryShipmentCreateInTransit` mutation. */
export interface InventoryShipmentCreateInTransitPayload {
  inventoryShipment: InventoryShipment | null;
  userErrors: InventoryShipmentCreateInTransitUserError[];
}

/** Return type for `inventoryShipmentCreate` mutation. */
export interface InventoryShipmentCreatePayload {
  inventoryShipment: InventoryShipment | null;
  userErrors: InventoryShipmentCreateUserError[];
}

/** Return type for `inventoryShipmentDelete` mutation. */
export interface InventoryShipmentDeletePayload {
  id: string | null;
  userErrors: InventoryShipmentDeleteUserError[];
}

/** Return type for `inventoryShipmentMarkInTransit` mutation. */
export interface InventoryShipmentMarkInTransitPayload {
  inventoryShipment: InventoryShipment | null;
  userErrors: InventoryShipmentMarkInTransitUserError[];
}

/** Return type for `inventoryShipmentReceive` mutation. */
export interface InventoryShipmentReceivePayload {
  inventoryShipment: InventoryShipment | null;
  userErrors: InventoryShipmentReceiveUserError[];
}

/** Return type for `inventoryShipmentRemoveItems` mutation. */
export interface InventoryShipmentRemoveItemsPayload {
  inventoryShipment: InventoryShipment | null;
  userErrors: InventoryShipmentRemoveItemsUserError[];
}

/** Return type for `inventoryShipmentSetBarcode` mutation. */
export interface InventoryShipmentSetBarcodePayload {
  inventoryShipment: InventoryShipment | null;
  userErrors: InventoryShipmentSetBarcodeUserError[];
}

/** Return type for `inventoryShipmentSetTracking` mutation. */
export interface InventoryShipmentSetTrackingPayload {
  inventoryShipment: InventoryShipment | null;
  userErrors: InventoryShipmentSetTrackingUserError[];
}

/** Return type for `inventoryShipmentUpdateItemQuantities` mutation. */
export interface InventoryShipmentUpdateItemQuantitiesPayload {
  shipment: InventoryShipment | null;
  updatedLineItems: InventoryShipmentLineItem[];
  userErrors: InventoryShipmentUpdateItemQuantitiesUserError[];
}

/** Return type for `inventoryTransferCancel` mutation. */
export interface InventoryTransferCancelPayload {
  inventoryTransfer: InventoryTransfer | null;
  userErrors: InventoryTransferCancelUserError[];
}

/** Return type for `inventoryTransferCreateAsReadyToShip` mutation. */
export interface InventoryTransferCreateAsReadyToShipPayload {
  inventoryTransfer: InventoryTransfer | null;
  userErrors: InventoryTransferCreateAsReadyToShipUserError[];
}

/** Return type for `inventoryTransferCreate` mutation. */
export interface InventoryTransferCreatePayload {
  inventoryTransfer: InventoryTransfer | null;
  userErrors: InventoryTransferCreateUserError[];
}

/** Return type for `inventoryTransferDelete` mutation. */
export interface InventoryTransferDeletePayload {
  deletedId: string | null;
  userErrors: InventoryTransferDeleteUserError[];
}

/** Return type for `inventoryTransferDuplicate` mutation. */
export interface InventoryTransferDuplicatePayload {
  inventoryTransfer: InventoryTransfer | null;
  userErrors: InventoryTransferDuplicateUserError[];
}

/** Return type for `inventoryTransferEdit` mutation. */
export interface InventoryTransferEditPayload {
  inventoryTransfer: InventoryTransfer | null;
  userErrors: InventoryTransferEditUserError[];
}

/** Return type for `inventoryTransferMarkAsReadyToShip` mutation. */
export interface InventoryTransferMarkAsReadyToShipPayload {
  inventoryTransfer: InventoryTransfer | null;
  userErrors: InventoryTransferMarkAsReadyToShipUserError[];
}

/** Return type for `inventoryTransferRemoveItems` mutation. */
export interface InventoryTransferRemoveItemsPayload {
  inventoryTransfer: InventoryTransfer | null;
  removedQuantities: InventoryTransferLineItemUpdate[];
  userErrors: InventoryTransferRemoveItemsUserError[];
}

/** Return type for `inventoryTransferSetItems` mutation. */
export interface InventoryTransferSetItemsPayload {
  inventoryTransfer: InventoryTransfer | null;
  updatedLineItems: InventoryTransferLineItemUpdate[];
  userErrors: InventoryTransferSetItemsUserError[];
}

/** Return type for `locationActivate` mutation. */
export interface LocationActivatePayload {
  location: Location | null;
  locationActivateUserErrors: LocationActivateUserError[];
}

/** Return type for `locationAdd` mutation. */
export interface LocationAddPayload {
  location: Location | null;
  userErrors: LocationAddUserError[];
}

/** Return type for `locationDeactivate` mutation. */
export interface LocationDeactivatePayload {
  location: Location | null;
  locationDeactivateUserErrors: LocationDeactivateUserError[];
}

/** Return type for `locationDelete` mutation. */
export interface LocationDeletePayload {
  deletedLocationId: string | null;
  locationDeleteUserErrors: LocationDeleteUserError[];
}

/** Return type for `locationEdit` mutation. */
export interface LocationEditPayload {
  location: Location | null;
  userErrors: LocationEditUserError[];
}

/** Return type for `locationLocalPickupDisable` mutation. */
export interface LocationLocalPickupDisablePayload {
  locationId: string | null;
  userErrors: DeliveryLocationLocalPickupSettingsError[];
}

/** Return type for `locationLocalPickupEnable` mutation. */
export interface LocationLocalPickupEnablePayload {
  localPickupSettings: DeliveryLocalPickupSettings | null;
  userErrors: DeliveryLocationLocalPickupSettingsError[];
}

/** Return type for `marketCreate` mutation. */
export interface MarketCreatePayload {
  market: Market | null;
  userErrors: MarketUserError[];
}

/** Return type for `marketCurrencySettingsUpdate` mutation. */
export interface MarketCurrencySettingsUpdatePayload {
  userErrors: MarketCurrencySettingsUserError[];
  market: Market | null;
}

/** Return type for `marketDelete` mutation. */
export interface MarketDeletePayload {
  deletedId: string | null;
  userErrors: MarketUserError[];
}

/** Return type for `marketingActivitiesDeleteAllExternal` mutation. */
export interface MarketingActivitiesDeleteAllExternalPayload {
  job: Job | null;
  userErrors: MarketingActivityUserError[];
}

/** Return type for `marketingActivityCreateExternal` mutation. */
export interface MarketingActivityCreateExternalPayload {
  marketingActivity: MarketingActivity | null;
  userErrors: MarketingActivityUserError[];
}

/** Return type for `marketingActivityCreate` mutation. */
export interface MarketingActivityCreatePayload {
  userErrors: UserError[];
  marketingActivity: MarketingActivity | null;
  redirectPath: string | null;
}

/** Return type for `marketingActivityDeleteExternal` mutation. */
export interface MarketingActivityDeleteExternalPayload {
  deletedMarketingActivityId: string | null;
  userErrors: MarketingActivityUserError[];
}

/** Return type for `marketingActivityUpdateExternal` mutation. */
export interface MarketingActivityUpdateExternalPayload {
  marketingActivity: MarketingActivity | null;
  userErrors: MarketingActivityUserError[];
}

/** Return type for `marketingActivityUpdate` mutation. */
export interface MarketingActivityUpdatePayload {
  marketingActivity: MarketingActivity | null;
  redirectPath: string | null;
  userErrors: UserError[];
}

/** Return type for `marketingActivityUpsertExternal` mutation. */
export interface MarketingActivityUpsertExternalPayload {
  marketingActivity: MarketingActivity | null;
  userErrors: MarketingActivityUserError[];
}

/** Return type for `marketingEngagementCreate` mutation. */
export interface MarketingEngagementCreatePayload {
  marketingEngagement: MarketingEngagement | null;
  userErrors: MarketingActivityUserError[];
}

/** Return type for `marketingEngagementsDelete` mutation. */
export interface MarketingEngagementsDeletePayload {
  result: string | null;
  userErrors: MarketingActivityUserError[];
}

/** Return type for `marketLocalizationsRegister` mutation. */
export interface MarketLocalizationsRegisterPayload {
  marketLocalizations: MarketLocalization[];
  userErrors: TranslationUserError[];
}

/** Return type for `marketLocalizationsRemove` mutation. */
export interface MarketLocalizationsRemovePayload {
  marketLocalizations: MarketLocalization[];
  userErrors: TranslationUserError[];
}

/** Return type for `marketRegionDelete` mutation. */
export interface MarketRegionDeletePayload {
  deletedId: string | null;
  market: Market | null;
  userErrors: MarketUserError[];
}

/** Return type for `marketRegionsCreate` mutation. */
export interface MarketRegionsCreatePayload {
  market: Market | null;
  userErrors: MarketUserError[];
}

/** Return type for `marketRegionsDelete` mutation. */
export interface MarketRegionsDeletePayload {
  deletedIds: string[];
  userErrors: MarketUserError[];
}

/** Return type for `marketUpdate` mutation. */
export interface MarketUpdatePayload {
  market: Market | null;
  userErrors: MarketUserError[];
}

/** Return type for `marketWebPresenceCreate` mutation. */
export interface MarketWebPresenceCreatePayload {
  market: Market | null;
  userErrors: MarketUserError[];
}

/** Return type for `marketWebPresenceDelete` mutation. */
export interface MarketWebPresenceDeletePayload {
  deletedId: string | null;
  market: Market | null;
  userErrors: MarketUserError[];
}

/** Return type for `marketWebPresenceUpdate` mutation. */
export interface MarketWebPresenceUpdatePayload {
  market: Market | null;
  userErrors: MarketUserError[];
}

/** Return type for `menuCreate` mutation. */
export interface MenuCreatePayload {
  menu: Menu | null;
  userErrors: MenuCreateUserError[];
}

/** Return type for `menuDelete` mutation. */
export interface MenuDeletePayload {
  deletedMenuId: string | null;
  userErrors: MenuDeleteUserError[];
}

/** Return type for `menuUpdate` mutation. */
export interface MenuUpdatePayload {
  menu: Menu | null;
  userErrors: MenuUpdateUserError[];
}

/** Return type for `metafieldDefinitionCreate` mutation. */
export interface MetafieldDefinitionCreatePayload {
  createdDefinition: MetafieldDefinition | null;
  userErrors: MetafieldDefinitionCreateUserError[];
}

/** Return type for `metafieldDefinitionDelete` mutation. */
export interface MetafieldDefinitionDeletePayload {
  deletedDefinition: MetafieldDefinitionIdentifier | null;
  deletedDefinitionId: string | null;
  userErrors: MetafieldDefinitionDeleteUserError[];
}

/** Return type for `metafieldDefinitionPin` mutation. */
export interface MetafieldDefinitionPinPayload {
  pinnedDefinition: MetafieldDefinition | null;
  userErrors: MetafieldDefinitionPinUserError[];
}

/** Return type for `metafieldDefinitionUnpin` mutation. */
export interface MetafieldDefinitionUnpinPayload {
  unpinnedDefinition: MetafieldDefinition | null;
  userErrors: MetafieldDefinitionUnpinUserError[];
}

/** Return type for `metafieldDefinitionUpdate` mutation. */
export interface MetafieldDefinitionUpdatePayload {
  updatedDefinition: MetafieldDefinition | null;
  userErrors: MetafieldDefinitionUpdateUserError[];
  validationJob: Job | null;
}

/** Return type for `metafieldsDelete` mutation. */
export interface MetafieldsDeletePayload {
  deletedMetafields: MetafieldIdentifier | null[] | null;
  userErrors: UserError[];
}

/** Return type for `metafieldsSet` mutation. */
export interface MetafieldsSetPayload {
  metafields: Metafield[];
  userErrors: MetafieldsSetUserError[];
}

/** Return type for `metaobjectBulkDelete` mutation. */
export interface MetaobjectBulkDeletePayload {
  job: Job | null;
  userErrors: MetaobjectUserError[];
}

/** Return type for `metaobjectCreate` mutation. */
export interface MetaobjectCreatePayload {
  metaobject: Metaobject | null;
  userErrors: MetaobjectUserError[];
}

/** Return type for `metaobjectDefinitionCreate` mutation. */
export interface MetaobjectDefinitionCreatePayload {
  metaobjectDefinition: MetaobjectDefinition | null;
  userErrors: MetaobjectUserError[];
}

/** Return type for `metaobjectDefinitionDelete` mutation. */
export interface MetaobjectDefinitionDeletePayload {
  deletedId: string | null;
  userErrors: MetaobjectUserError[];
}

/** Return type for `metaobjectDefinitionUpdate` mutation. */
export interface MetaobjectDefinitionUpdatePayload {
  metaobjectDefinition: MetaobjectDefinition | null;
  userErrors: MetaobjectUserError[];
}

/** Return type for `metaobjectDelete` mutation. */
export interface MetaobjectDeletePayload {
  deletedId: string | null;
  userErrors: MetaobjectUserError[];
}

/** Return type for `metaobjectUpdate` mutation. */
export interface MetaobjectUpdatePayload {
  metaobject: Metaobject | null;
  userErrors: MetaobjectUserError[];
}

/** Return type for `metaobjectUpsert` mutation. */
export interface MetaobjectUpsertPayload {
  metaobject: Metaobject | null;
  userErrors: MetaobjectUserError[];
}

/** Return type for `mobilePlatformApplicationCreate` mutation. */
export interface MobilePlatformApplicationCreatePayload {
  mobilePlatformApplication: MobilePlatformApplication | null;
  userErrors: MobilePlatformApplicationUserError[];
}

/** Return type for `mobilePlatformApplicationDelete` mutation. */
export interface MobilePlatformApplicationDeletePayload {
  deletedMobilePlatformApplicationId: string | null;
  userErrors: MobilePlatformApplicationUserError[];
}

/** Return type for `mobilePlatformApplicationUpdate` mutation. */
export interface MobilePlatformApplicationUpdatePayload {
  mobilePlatformApplication: MobilePlatformApplication | null;
  userErrors: MobilePlatformApplicationUserError[];
}

/** Return type for `orderCancel` mutation. */
export interface OrderCancelPayload {
  job: Job | null;
  orderCancelUserErrors: OrderCancelUserError[];
  userErrors: UserError[];
}

/** Return type for `orderCapture` mutation. */
export interface OrderCapturePayload {
  transaction: OrderTransaction | null;
  userErrors: UserError[];
}

/** Return type for `orderClose` mutation. */
export interface OrderClosePayload {
  order: Order | null;
  userErrors: UserError[];
}

/** Return type for `orderCreateMandatePayment` mutation. */
export interface OrderCreateMandatePaymentPayload {
  job: Job | null;
  paymentReferenceId: string | null;
  userErrors: OrderCreateMandatePaymentUserError[];
}

/** Return type for `orderCreateManualPayment` mutation. */
export interface OrderCreateManualPaymentPayload {
  order: Order | null;
  userErrors: OrderCreateManualPaymentOrderCreateManualPaymentError[];
}

/** Return type for `orderCreate` mutation. */
export interface OrderCreatePayload {
  order: Order | null;
  userErrors: OrderCreateUserError[];
}

/** Return type for `orderCustomerRemove` mutation. */
export interface OrderCustomerRemovePayload {
  order: Order | null;
  userErrors: OrderCustomerRemoveUserError[];
}

/** Return type for `orderCustomerSet` mutation. */
export interface OrderCustomerSetPayload {
  order: Order | null;
  userErrors: OrderCustomerSetUserError[];
}

/** Return type for `orderDelete` mutation. */
export interface OrderDeletePayload {
  deletedId: string | null;
  userErrors: OrderDeleteUserError[];
}

/** Return type for `orderEditAddCustomItem` mutation. */
export interface OrderEditAddCustomItemPayload {
  calculatedLineItem: CalculatedLineItem | null;
  calculatedOrder: CalculatedOrder | null;
  orderEditSession: OrderEditSession | null;
  userErrors: UserError[];
}

/** Return type for `orderEditAddLineItemDiscount` mutation. */
export interface OrderEditAddLineItemDiscountPayload {
  addedDiscountStagedChange: OrderStagedChangeAddLineItemDiscount | null;
  calculatedLineItem: CalculatedLineItem | null;
  calculatedOrder: CalculatedOrder | null;
  orderEditSession: OrderEditSession | null;
  userErrors: UserError[];
}

/** Return type for `orderEditAddShippingLine` mutation. */
export interface OrderEditAddShippingLinePayload {
  calculatedOrder: CalculatedOrder | null;
  calculatedShippingLine: CalculatedShippingLine | null;
  orderEditSession: OrderEditSession | null;
  userErrors: OrderEditAddShippingLineUserError[];
}

/** Return type for `orderEditAddVariant` mutation. */
export interface OrderEditAddVariantPayload {
  calculatedLineItem: CalculatedLineItem | null;
  calculatedOrder: CalculatedOrder | null;
  orderEditSession: OrderEditSession | null;
  userErrors: UserError[];
}

/** Return type for `orderEditBegin` mutation. */
export interface OrderEditBeginPayload {
  calculatedOrder: CalculatedOrder | null;
  orderEditSession: OrderEditSession | null;
  userErrors: UserError[];
}

/** Return type for `orderEditCommit` mutation. */
export interface OrderEditCommitPayload {
  order: Order | null;
  successMessages: string[];
  userErrors: UserError[];
}

/** Return type for `orderEditRemoveDiscount` mutation. */
export interface OrderEditRemoveDiscountPayload {
  calculatedOrder: CalculatedOrder | null;
  orderEditSession: OrderEditSession | null;
  userErrors: OrderEditRemoveDiscountUserError[];
}

/** Return type for `orderEditRemoveLineItemDiscount` mutation. */
export interface OrderEditRemoveLineItemDiscountPayload {
  calculatedLineItem: CalculatedLineItem | null;
  calculatedOrder: CalculatedOrder | null;
  orderEditSession: OrderEditSession | null;
  userErrors: UserError[];
}

/** Return type for `orderEditRemoveShippingLine` mutation. */
export interface OrderEditRemoveShippingLinePayload {
  calculatedOrder: CalculatedOrder | null;
  orderEditSession: OrderEditSession | null;
  userErrors: OrderEditRemoveShippingLineUserError[];
}

/** Return type for `orderEditSetQuantity` mutation. */
export interface OrderEditSetQuantityPayload {
  calculatedLineItem: CalculatedLineItem | null;
  calculatedOrder: CalculatedOrder | null;
  orderEditSession: OrderEditSession | null;
  userErrors: UserError[];
}

/** Return type for `orderEditUpdateDiscount` mutation. */
export interface OrderEditUpdateDiscountPayload {
  calculatedOrder: CalculatedOrder | null;
  orderEditSession: OrderEditSession | null;
  userErrors: OrderEditUpdateDiscountUserError[];
}

/** Return type for `orderEditUpdateShippingLine` mutation. */
export interface OrderEditUpdateShippingLinePayload {
  calculatedOrder: CalculatedOrder | null;
  orderEditSession: OrderEditSession | null;
  userErrors: OrderEditUpdateShippingLineUserError[];
}

/** Return type for `orderInvoiceSend` mutation. */
export interface OrderInvoiceSendPayload {
  order: Order | null;
  userErrors: OrderInvoiceSendUserError[];
}

/** Return type for `orderMarkAsPaid` mutation. */
export interface OrderMarkAsPaidPayload {
  order: Order | null;
  userErrors: UserError[];
}

/** Return type for `orderOpen` mutation. */
export interface OrderOpenPayload {
  order: Order | null;
  userErrors: UserError[];
}

/** Return type for `orderRiskAssessmentCreate` mutation. */
export interface OrderRiskAssessmentCreatePayload {
  orderRiskAssessment: OrderRiskAssessment | null;
  userErrors: OrderRiskAssessmentCreateUserError[];
}

/** Return type for `orderUpdate` mutation. */
export interface OrderUpdatePayload {
  order: Order | null;
  userErrors: UserError[];
}

/** Return type for `pageCreate` mutation. */
export interface PageCreatePayload {
  page: Page | null;
  userErrors: PageCreateUserError[];
}

/** Return type for `pageDelete` mutation. */
export interface PageDeletePayload {
  deletedPageId: string | null;
  userErrors: PageDeleteUserError[];
}

/** Return type for `pageUpdate` mutation. */
export interface PageUpdatePayload {
  page: Page | null;
  userErrors: PageUpdateUserError[];
}

/** Return type for `paymentCustomizationActivation` mutation. */
export interface PaymentCustomizationActivationPayload {
  ids: string[];
  userErrors: PaymentCustomizationError[];
}

/** Return type for `paymentCustomizationCreate` mutation. */
export interface PaymentCustomizationCreatePayload {
  paymentCustomization: PaymentCustomization | null;
  userErrors: PaymentCustomizationError[];
}

/** Return type for `paymentCustomizationDelete` mutation. */
export interface PaymentCustomizationDeletePayload {
  deletedId: string | null;
  userErrors: PaymentCustomizationError[];
}

/** Return type for `paymentCustomizationUpdate` mutation. */
export interface PaymentCustomizationUpdatePayload {
  paymentCustomization: PaymentCustomization | null;
  userErrors: PaymentCustomizationError[];
}

/** Return type for `paymentReminderSend` mutation. */
export interface PaymentReminderSendPayload {
  success: boolean | null;
  userErrors: PaymentReminderSendUserError[];
}

/** Return type for `paymentTermsCreate` mutation. */
export interface PaymentTermsCreatePayload {
  paymentTerms: PaymentTerms | null;
  userErrors: PaymentTermsCreateUserError[];
}

/** Return type for `paymentTermsDelete` mutation. */
export interface PaymentTermsDeletePayload {
  deletedId: string | null;
  userErrors: PaymentTermsDeleteUserError[];
}

/** Return type for `paymentTermsUpdate` mutation. */
export interface PaymentTermsUpdatePayload {
  paymentTerms: PaymentTerms | null;
  userErrors: PaymentTermsUpdateUserError[];
}

/** Return type for `pointOfSaleDeviceAssignToCashDrawer` mutation. */
export interface PointOfSaleDeviceAssignToCashDrawerPayload {
  pointOfSaleDevice: PointOfSaleDevice | null;
  userErrors: PointOfSaleDeviceAssignToCashDrawerUserError[];
}

/** Return type for `pointOfSaleDevicePaymentSessionAdjust` mutation. */
export interface PointOfSaleDevicePaymentSessionAdjustPayload {
  pointOfSaleDevicePaymentSession: PointOfSaleDevicePaymentSession | null;
  userErrors: UserError[];
}

/** Return type for `pointOfSaleDevicePaymentSessionClose` mutation. */
export interface PointOfSaleDevicePaymentSessionClosePayload {
  pointOfSaleDevicePaymentSession: PointOfSaleDevicePaymentSession | null;
  userErrors: PointOfSaleDevicePaymentSessionCloseUserError[];
}

/** Return type for `pointOfSaleDevicePaymentSessionCount` mutation. */
export interface PointOfSaleDevicePaymentSessionCountPayload {
  pointOfSaleDevicePaymentSession: PointOfSaleDevicePaymentSession | null;
  userErrors: PointOfSaleDevicePaymentSessionCountUserError[];
}

/** Return type for `pointOfSaleDevicePaymentSessionOpen` mutation. */
export interface PointOfSaleDevicePaymentSessionOpenPayload {
  pointOfSaleDevicePaymentSession: PointOfSaleDevicePaymentSession | null;
  userErrors: PointOfSaleDevicePaymentSessionOpenUserError[];
}

/** Return type for `priceListCreate` mutation. */
export interface PriceListCreatePayload {
  priceList: PriceList | null;
  userErrors: PriceListUserError[];
}

/** Return type for `priceListDelete` mutation. */
export interface PriceListDeletePayload {
  deletedId: string | null;
  userErrors: PriceListUserError[];
}

/** Return type for `priceListFixedPricesAdd` mutation. */
export interface PriceListFixedPricesAddPayload {
  prices: PriceListPrice[];
  userErrors: PriceListPriceUserError[];
}

/** Return type for `priceListFixedPricesByProductUpdate` mutation. */
export interface PriceListFixedPricesByProductUpdatePayload {
  priceList: PriceList | null;
  pricesToAddProducts: Product[];
  pricesToDeleteProducts: Product[];
  userErrors: PriceListFixedPricesByProductBulkUpdateUserError[];
}

/** Return type for `priceListFixedPricesDelete` mutation. */
export interface PriceListFixedPricesDeletePayload {
  deletedFixedPriceVariantIds: string[];
  userErrors: PriceListPriceUserError[];
}

/** Return type for `priceListFixedPricesUpdate` mutation. */
export interface PriceListFixedPricesUpdatePayload {
  deletedFixedPriceVariantIds: string[];
  priceList: PriceList | null;
  pricesAdded: PriceListPrice[];
  userErrors: PriceListPriceUserError[];
}

/** Return type for `priceListUpdate` mutation. */
export interface PriceListUpdatePayload {
  priceList: PriceList | null;
  userErrors: PriceListUserError[];
}

/** Return type for `privacyFeaturesDisable` mutation. */
export interface PrivacyFeaturesDisablePayload {
  featuresDisabled: PrivacyFeaturesEnum[];
  userErrors: PrivacyFeaturesDisableUserError[];
}

/** Return type for `productBundleCreate` mutation. */
export interface ProductBundleCreatePayload {
  productBundleOperation: ProductBundleOperation | null;
  userErrors: UserError[];
}

/** Return type for `productBundleUpdate` mutation. */
export interface ProductBundleUpdatePayload {
  productBundleOperation: ProductBundleOperation | null;
  userErrors: UserError[];
}

/** Return type for `productChangeStatus` mutation. */
export interface ProductChangeStatusPayload {
  product: Product | null;
  userErrors: ProductChangeStatusUserError[];
}

/** Return type for `productCreateMedia` mutation. */
export interface ProductCreateMediaPayload {
  media: Media[];
  mediaUserErrors: MediaUserError[];
  product: Product | null;
  userErrors: UserError[];
}

/** Return type for `productCreate` mutation. */
export interface ProductCreatePayload {
  product: Product | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `productDeleteMedia` mutation. */
export interface ProductDeleteMediaPayload {
  deletedMediaIds: string[];
  deletedProductImageIds: string[];
  mediaUserErrors: MediaUserError[];
  product: Product | null;
  userErrors: UserError[];
}

/** Return type for `productDelete` mutation. */
export interface ProductDeletePayload {
  deletedProductId: string | null;
  productDeleteOperation: ProductDeleteOperation | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `productDuplicate` mutation. */
export interface ProductDuplicatePayload {
  imageJob: Job | null;
  newProduct: Product | null;
  productDuplicateOperation: ProductDuplicateOperation | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `productFeedCreate` mutation. */
export interface ProductFeedCreatePayload {
  productFeed: ProductFeed | null;
  userErrors: ProductFeedCreateUserError[];
}

/** Return type for `productFeedDelete` mutation. */
export interface ProductFeedDeletePayload {
  deletedId: string | null;
  userErrors: ProductFeedDeleteUserError[];
}

/** Return type for `productFullSync` mutation. */
export interface ProductFullSyncPayload {
  id: string | null;
  userErrors: ProductFullSyncUserError[];
}

/** Return type for `productJoinSellingPlanGroups` mutation. */
export interface ProductJoinSellingPlanGroupsPayload {
  product: Product | null;
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `productLeaveSellingPlanGroups` mutation. */
export interface ProductLeaveSellingPlanGroupsPayload {
  product: Product | null;
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `productOptionsCreate` mutation. */
export interface ProductOptionsCreatePayload {
  product: Product | null;
  userErrors: ProductOptionsCreateUserError[];
}

/** Return type for `productOptionsDelete` mutation. */
export interface ProductOptionsDeletePayload {
  deletedOptionsIds: string[];
  product: Product | null;
  userErrors: ProductOptionsDeleteUserError[];
}

/** Return type for `productOptionsReorder` mutation. */
export interface ProductOptionsReorderPayload {
  product: Product | null;
  userErrors: ProductOptionsReorderUserError[];
}

/** Return type for `productOptionUpdate` mutation. */
export interface ProductOptionUpdatePayload {
  product: Product | null;
  userErrors: ProductOptionUpdateUserError[];
}

/** Return type for `productPublish` mutation. */
export interface ProductPublishPayload {
  product: Product | null;
  shop: Shop;
  userErrors: UserError[];
  productPublications: ProductPublication[];
}

/** Return type for `productReorderMedia` mutation. */
export interface ProductReorderMediaPayload {
  job: Job | null;
  mediaUserErrors: MediaUserError[];
  userErrors: UserError[];
}

/** Return type for `productSet` mutation. */
export interface ProductSetPayload {
  product: Product | null;
  productSetOperation: ProductSetOperation | null;
  userErrors: ProductSetUserError[];
}

/** Return type for `productUnpublish` mutation. */
export interface ProductUnpublishPayload {
  product: Product | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `productUpdateMedia` mutation. */
export interface ProductUpdateMediaPayload {
  media: Media[];
  mediaUserErrors: MediaUserError[];
  product: Product | null;
  userErrors: UserError[];
}

/** Return type for `productUpdate` mutation. */
export interface ProductUpdatePayload {
  product: Product | null;
  userErrors: UserError[];
}

/** Return type for `productVariantAppendMedia` mutation. */
export interface ProductVariantAppendMediaPayload {
  product: Product | null;
  productVariants: ProductVariant[];
  userErrors: MediaUserError[];
}

/** Return type for `productVariantDetachMedia` mutation. */
export interface ProductVariantDetachMediaPayload {
  product: Product | null;
  productVariants: ProductVariant[];
  userErrors: MediaUserError[];
}

/** Return type for `productVariantJoinSellingPlanGroups` mutation. */
export interface ProductVariantJoinSellingPlanGroupsPayload {
  productVariant: ProductVariant | null;
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `productVariantLeaveSellingPlanGroups` mutation. */
export interface ProductVariantLeaveSellingPlanGroupsPayload {
  productVariant: ProductVariant | null;
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `productVariantRelationshipBulkUpdate` mutation. */
export interface ProductVariantRelationshipBulkUpdatePayload {
  parentProductVariants: ProductVariant[];
  userErrors: ProductVariantRelationshipBulkUpdateUserError[];
}

/** Return type for `productVariantsBulkCreate` mutation. */
export interface ProductVariantsBulkCreatePayload {
  product: Product | null;
  productVariants: ProductVariant[];
  userErrors: ProductVariantsBulkCreateUserError[];
}

/** Return type for `productVariantsBulkDelete` mutation. */
export interface ProductVariantsBulkDeletePayload {
  product: Product | null;
  userErrors: ProductVariantsBulkDeleteUserError[];
}

/** Return type for `productVariantsBulkReorder` mutation. */
export interface ProductVariantsBulkReorderPayload {
  product: Product | null;
  userErrors: ProductVariantsBulkReorderUserError[];
}

/** Return type for `productVariantsBulkUpdate` mutation. */
export interface ProductVariantsBulkUpdatePayload {
  product: Product | null;
  productVariants: ProductVariant[];
  userErrors: ProductVariantsBulkUpdateUserError[];
}

/** Return type for `publicationCreate` mutation. */
export interface PublicationCreatePayload {
  publication: Publication | null;
  userErrors: PublicationUserError[];
}

/** Return type for `publicationDelete` mutation. */
export interface PublicationDeletePayload {
  deletedId: string | null;
  userErrors: PublicationUserError[];
}

/** Return type for `publicationUpdate` mutation. */
export interface PublicationUpdatePayload {
  publication: Publication | null;
  userErrors: PublicationUserError[];
}

/** Return type for `publishablePublish` mutation. */
export interface PublishablePublishPayload {
  publishable: Publishable | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `publishablePublishToCurrentChannel` mutation. */
export interface PublishablePublishToCurrentChannelPayload {
  publishable: Publishable | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `publishableUnpublish` mutation. */
export interface PublishableUnpublishPayload {
  publishable: Publishable | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `publishableUnpublishToCurrentChannel` mutation. */
export interface PublishableUnpublishToCurrentChannelPayload {
  publishable: Publishable | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `pubSubServerPixelUpdate` mutation. */
export interface PubSubServerPixelUpdatePayload {
  serverPixel: ServerPixel | null;
  userErrors: ErrorsServerPixelUserError[];
}

/** Return type for `pubSubWebhookSubscriptionCreate` mutation. */
export interface PubSubWebhookSubscriptionCreatePayload {
  userErrors: PubSubWebhookSubscriptionCreateUserError[];
  webhookSubscription: WebhookSubscription | null;
}

/** Return type for `pubSubWebhookSubscriptionUpdate` mutation. */
export interface PubSubWebhookSubscriptionUpdatePayload {
  userErrors: PubSubWebhookSubscriptionUpdateUserError[];
  webhookSubscription: WebhookSubscription | null;
}

/** Return type for `quantityPricingByVariantUpdate` mutation. */
export interface QuantityPricingByVariantUpdatePayload {
  productVariants: ProductVariant[];
  userErrors: QuantityPricingByVariantUserError[];
}

/** Return type for `quantityRulesAdd` mutation. */
export interface QuantityRulesAddPayload {
  quantityRules: QuantityRule[];
  userErrors: QuantityRuleUserError[];
}

/** Return type for `quantityRulesDelete` mutation. */
export interface QuantityRulesDeletePayload {
  deletedQuantityRulesVariantIds: string[];
  userErrors: QuantityRuleUserError[];
}

/** Return type for `refundCreate` mutation. */
export interface RefundCreatePayload {
  order: Order | null;
  refund: Refund | null;
  userErrors: UserError[];
}

/** Return type for `removeFromReturn` mutation. */
export interface RemoveFromReturnPayload {
  return: Return | null;
  userErrors: ReturnUserError[];
}

/** Return type for `returnApproveRequest` mutation. */
export interface ReturnApproveRequestPayload {
  return: Return | null;
  userErrors: ReturnUserError[];
}

/** Return type for `returnCancel` mutation. */
export interface ReturnCancelPayload {
  return: Return | null;
  userErrors: ReturnUserError[];
}

/** Return type for `returnClose` mutation. */
export interface ReturnClosePayload {
  return: Return | null;
  userErrors: ReturnUserError[];
}

/** Return type for `returnCreate` mutation. */
export interface ReturnCreatePayload {
  return: Return | null;
  userErrors: ReturnUserError[];
}

/** Return type for `returnDeclineRequest` mutation. */
export interface ReturnDeclineRequestPayload {
  return: Return | null;
  userErrors: ReturnUserError[];
}

/** Return type for `returnLineItemRemoveFromReturn` mutation. */
export interface ReturnLineItemRemoveFromReturnPayload {
  return: Return | null;
  userErrors: ReturnUserError[];
}

/** Return type for `returnProcess` mutation. */
export interface ReturnProcessPayload {
  return: Return | null;
  userErrors: ReturnUserError[];
}

/** Return type for `returnRefund` mutation. */
export interface ReturnRefundPayload {
  refund: Refund | null;
  userErrors: ReturnUserError[];
}

/** Return type for `returnReopen` mutation. */
export interface ReturnReopenPayload {
  return: Return | null;
  userErrors: ReturnUserError[];
}

/** Return type for `returnRequest` mutation. */
export interface ReturnRequestPayload {
  return: Return | null;
  userErrors: ReturnUserError[];
}

/** Return type for `reverseDeliveryCreateWithShipping` mutation. */
export interface ReverseDeliveryCreateWithShippingPayload {
  reverseDelivery: ReverseDelivery | null;
  userErrors: ReturnUserError[];
}

/** Return type for `reverseDeliveryShippingUpdate` mutation. */
export interface ReverseDeliveryShippingUpdatePayload {
  reverseDelivery: ReverseDelivery | null;
  userErrors: ReturnUserError[];
}

/** Return type for `reverseFulfillmentOrderDispose` mutation. */
export interface ReverseFulfillmentOrderDisposePayload {
  reverseFulfillmentOrderLineItems: ReverseFulfillmentOrderLineItem[];
  userErrors: ReturnUserError[];
}

/** Return type for `savedSearchCreate` mutation. */
export interface SavedSearchCreatePayload {
  savedSearch: SavedSearch | null;
  userErrors: UserError[];
}

/** Return type for `savedSearchDelete` mutation. */
export interface SavedSearchDeletePayload {
  deletedSavedSearchId: string | null;
  shop: Shop;
  userErrors: UserError[];
}

/** Return type for `savedSearchUpdate` mutation. */
export interface SavedSearchUpdatePayload {
  savedSearch: SavedSearch | null;
  userErrors: UserError[];
}

/** Return type for `scriptTagCreate` mutation. */
export interface ScriptTagCreatePayload {
  scriptTag: ScriptTag | null;
  userErrors: UserError[];
}

/** Return type for `scriptTagDelete` mutation. */
export interface ScriptTagDeletePayload {
  deletedScriptTagId: string | null;
  userErrors: UserError[];
}

/** Return type for `scriptTagUpdate` mutation. */
export interface ScriptTagUpdatePayload {
  scriptTag: ScriptTag | null;
  userErrors: UserError[];
}

/** Return type for `segmentCreate` mutation. */
export interface SegmentCreatePayload {
  segment: Segment | null;
  userErrors: UserError[];
}

/** Return type for `segmentDelete` mutation. */
export interface SegmentDeletePayload {
  deletedSegmentId: string | null;
  userErrors: UserError[];
}

/** Return type for `segmentUpdate` mutation. */
export interface SegmentUpdatePayload {
  segment: Segment | null;
  userErrors: UserError[];
}

/** Return type for `sellingPlanGroupAddProducts` mutation. */
export interface SellingPlanGroupAddProductsPayload {
  sellingPlanGroup: SellingPlanGroup | null;
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `sellingPlanGroupAddProductVariants` mutation. */
export interface SellingPlanGroupAddProductVariantsPayload {
  sellingPlanGroup: SellingPlanGroup | null;
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `sellingPlanGroupCreate` mutation. */
export interface SellingPlanGroupCreatePayload {
  sellingPlanGroup: SellingPlanGroup | null;
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `sellingPlanGroupDelete` mutation. */
export interface SellingPlanGroupDeletePayload {
  deletedSellingPlanGroupId: string | null;
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `sellingPlanGroupRemoveProducts` mutation. */
export interface SellingPlanGroupRemoveProductsPayload {
  removedProductIds: string[];
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `sellingPlanGroupRemoveProductVariants` mutation. */
export interface SellingPlanGroupRemoveProductVariantsPayload {
  removedProductVariantIds: string[];
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `sellingPlanGroupUpdate` mutation. */
export interface SellingPlanGroupUpdatePayload {
  deletedSellingPlanIds: string[];
  sellingPlanGroup: SellingPlanGroup | null;
  userErrors: SellingPlanGroupUserError[];
}

/** Return type for `serverPixelCreate` mutation. */
export interface ServerPixelCreatePayload {
  serverPixel: ServerPixel | null;
  userErrors: ErrorsServerPixelUserError[];
}

/** Return type for `serverPixelDelete` mutation. */
export interface ServerPixelDeletePayload {
  deletedServerPixelId: string | null;
  userErrors: ErrorsServerPixelUserError[];
}

/** Return type for `shippingPackageDelete` mutation. */
export interface ShippingPackageDeletePayload {
  deletedId: string | null;
  userErrors: UserError[];
}

/** Return type for `shippingPackageMakeDefault` mutation. */
export interface ShippingPackageMakeDefaultPayload {
  userErrors: UserError[];
}

/** Return type for `shippingPackageUpdate` mutation. */
export interface ShippingPackageUpdatePayload {
  userErrors: UserError[];
}

/** Return type for `shopifyPaymentsPayoutAlternateCurrencyCreate` mutation. */
export interface ShopifyPaymentsPayoutAlternateCurrencyCreatePayload {
  payout: ShopifyPaymentsToolingProviderPayout | null;
  success: boolean | null;
  userErrors: ShopifyPaymentsPayoutAlternateCurrencyCreateUserError[];
}

/** Return type for `shopLocaleDisable` mutation. */
export interface ShopLocaleDisablePayload {
  locale: string | null;
  userErrors: UserError[];
}

/** Return type for `shopLocaleEnable` mutation. */
export interface ShopLocaleEnablePayload {
  shopLocale: ShopLocale | null;
  userErrors: UserError[];
}

/** Return type for `shopLocaleUpdate` mutation. */
export interface ShopLocaleUpdatePayload {
  shopLocale: ShopLocale | null;
  userErrors: UserError[];
}

/** Return type for `shopPolicyUpdate` mutation. */
export interface ShopPolicyUpdatePayload {
  shopPolicy: ShopPolicy | null;
  userErrors: ShopPolicyUserError[];
}

/** Return type for `shopResourceFeedbackCreate` mutation. */
export interface ShopResourceFeedbackCreatePayload {
  feedback: AppFeedback | null;
  userErrors: ShopResourceFeedbackCreateUserError[];
}

/** Return type for `stagedUploadsCreate` mutation. */
export interface StagedUploadsCreatePayload {
  stagedTargets: StagedMediaUploadTarget[];
  userErrors: UserError[];
}

/** Return type for `stagedUploadTargetGenerate` mutation. */
export interface StagedUploadTargetGeneratePayload {
  parameters: MutationsStagedUploadTargetGenerateUploadParameter[];
  url: string;
  userErrors: UserError[];
}

/** Return type for `stagedUploadTargetsGenerate` mutation. */
export interface StagedUploadTargetsGeneratePayload {
  urls: StagedUploadTarget[];
  userErrors: UserError[];
}

/** Return type for `standardMetafieldDefinitionEnable` mutation. */
export interface StandardMetafieldDefinitionEnablePayload {
  createdDefinition: MetafieldDefinition | null;
  userErrors: StandardMetafieldDefinitionEnableUserError[];
}

/** Return type for `standardMetaobjectDefinitionEnable` mutation. */
export interface StandardMetaobjectDefinitionEnablePayload {
  metaobjectDefinition: MetaobjectDefinition | null;
  userErrors: MetaobjectUserError[];
}

/** Return type for `storeCreditAccountCredit` mutation. */
export interface StoreCreditAccountCreditPayload {
  storeCreditAccountTransaction: StoreCreditAccountCreditTransaction | null;
  userErrors: StoreCreditAccountCreditUserError[];
}

/** Return type for `storeCreditAccountDebit` mutation. */
export interface StoreCreditAccountDebitPayload {
  storeCreditAccountTransaction: StoreCreditAccountDebitTransaction | null;
  userErrors: StoreCreditAccountDebitUserError[];
}

/** Return type for `storefrontAccessTokenCreate` mutation. */
export interface StorefrontAccessTokenCreatePayload {
  shop: Shop;
  storefrontAccessToken: StorefrontAccessToken | null;
  userErrors: UserError[];
}

/** Return type for `storefrontAccessTokenDelete` mutation. */
export interface StorefrontAccessTokenDeletePayload {
  deletedStorefrontAccessTokenId: string | null;
  userErrors: UserError[];
}

/** Return type for `subscriptionBillingAttemptCreate` mutation. */
export interface SubscriptionBillingAttemptCreatePayload {
  subscriptionBillingAttempt: SubscriptionBillingAttempt | null;
  userErrors: BillingAttemptUserError[];
}

/** Return type for `subscriptionBillingCycleBulkCharge` mutation. */
export interface SubscriptionBillingCycleBulkChargePayload {
  job: Job | null;
  userErrors: SubscriptionBillingCycleBulkUserError[];
}

/** Return type for `subscriptionBillingCycleBulkSearch` mutation. */
export interface SubscriptionBillingCycleBulkSearchPayload {
  job: Job | null;
  userErrors: SubscriptionBillingCycleBulkUserError[];
}

/** Return type for `subscriptionBillingCycleCharge` mutation. */
export interface SubscriptionBillingCycleChargePayload {
  subscriptionBillingAttempt: SubscriptionBillingAttempt | null;
  userErrors: BillingAttemptUserError[];
}

/** Return type for `subscriptionBillingCycleContractDraftCommit` mutation. */
export interface SubscriptionBillingCycleContractDraftCommitPayload {
  contract: SubscriptionBillingCycleEditedContract | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionBillingCycleContractDraftConcatenate` mutation. */
export interface SubscriptionBillingCycleContractDraftConcatenatePayload {
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionBillingCycleContractEdit` mutation. */
export interface SubscriptionBillingCycleContractEditPayload {
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionBillingCycleEditDelete` mutation. */
export interface SubscriptionBillingCycleEditDeletePayload {
  billingCycles: SubscriptionBillingCycle[];
  userErrors: SubscriptionBillingCycleUserError[];
}

/** Return type for `subscriptionBillingCycleEditsDelete` mutation. */
export interface SubscriptionBillingCycleEditsDeletePayload {
  billingCycles: SubscriptionBillingCycle[];
  userErrors: SubscriptionBillingCycleUserError[];
}

/** Return type for `subscriptionBillingCycleScheduleEdit` mutation. */
export interface SubscriptionBillingCycleScheduleEditPayload {
  billingCycle: SubscriptionBillingCycle | null;
  userErrors: SubscriptionBillingCycleUserError[];
}

/** Return type for `subscriptionBillingCycleSkip` mutation. */
export interface SubscriptionBillingCycleSkipPayload {
  billingCycle: SubscriptionBillingCycle | null;
  userErrors: SubscriptionBillingCycleSkipUserError[];
}

/** Return type for `subscriptionBillingCycleUnskip` mutation. */
export interface SubscriptionBillingCycleUnskipPayload {
  billingCycle: SubscriptionBillingCycle | null;
  userErrors: SubscriptionBillingCycleUnskipUserError[];
}

/** Return type for `subscriptionContractActivate` mutation. */
export interface SubscriptionContractActivatePayload {
  contract: SubscriptionContract | null;
  userErrors: SubscriptionContractStatusUpdateUserError[];
}

/** Return type for `subscriptionContractAtomicCreate` mutation. */
export interface SubscriptionContractAtomicCreatePayload {
  contract: SubscriptionContract | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionContractCancel` mutation. */
export interface SubscriptionContractCancelPayload {
  contract: SubscriptionContract | null;
  userErrors: SubscriptionContractStatusUpdateUserError[];
}

/** Return type for `subscriptionContractCreate` mutation. */
export interface SubscriptionContractCreatePayload {
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionContractExpire` mutation. */
export interface SubscriptionContractExpirePayload {
  contract: SubscriptionContract | null;
  userErrors: SubscriptionContractStatusUpdateUserError[];
}

/** Return type for `subscriptionContractFail` mutation. */
export interface SubscriptionContractFailPayload {
  contract: SubscriptionContract | null;
  userErrors: SubscriptionContractStatusUpdateUserError[];
}

/** Return type for `subscriptionContractPause` mutation. */
export interface SubscriptionContractPausePayload {
  contract: SubscriptionContract | null;
  userErrors: SubscriptionContractStatusUpdateUserError[];
}

/** Return type for `subscriptionContractProductChange` mutation. */
export interface SubscriptionContractProductChangePayload {
  contract: SubscriptionContract | null;
  lineUpdated: SubscriptionLine | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionContractSetNextBillingDate` mutation. */
export interface SubscriptionContractSetNextBillingDatePayload {
  contract: SubscriptionContract | null;
  userErrors: SubscriptionContractUserError[];
}

/** Return type for `subscriptionContractUpdate` mutation. */
export interface SubscriptionContractUpdatePayload {
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftCommit` mutation. */
export interface SubscriptionDraftCommitPayload {
  contract: SubscriptionContract | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftDiscountAdd` mutation. */
export interface SubscriptionDraftDiscountAddPayload {
  discountAdded: SubscriptionManualDiscount | null;
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftDiscountCodeApply` mutation. */
export interface SubscriptionDraftDiscountCodeApplyPayload {
  appliedDiscount: SubscriptionAppliedCodeDiscount | null;
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftDiscountRemove` mutation. */
export interface SubscriptionDraftDiscountRemovePayload {
  discountRemoved: SubscriptionDiscount | null;
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftDiscountUpdate` mutation. */
export interface SubscriptionDraftDiscountUpdatePayload {
  discountUpdated: SubscriptionManualDiscount | null;
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftFreeShippingDiscountAdd` mutation. */
export interface SubscriptionDraftFreeShippingDiscountAddPayload {
  discountAdded: SubscriptionManualDiscount | null;
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftFreeShippingDiscountUpdate` mutation. */
export interface SubscriptionDraftFreeShippingDiscountUpdatePayload {
  discountUpdated: SubscriptionManualDiscount | null;
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftLineAdd` mutation. */
export interface SubscriptionDraftLineAddPayload {
  draft: SubscriptionDraft | null;
  lineAdded: SubscriptionLine | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftLineRemove` mutation. */
export interface SubscriptionDraftLineRemovePayload {
  discountsUpdated: SubscriptionManualDiscount[];
  draft: SubscriptionDraft | null;
  lineRemoved: SubscriptionLine | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftLineUpdate` mutation. */
export interface SubscriptionDraftLineUpdatePayload {
  draft: SubscriptionDraft | null;
  lineUpdated: SubscriptionLine | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `subscriptionDraftUpdate` mutation. */
export interface SubscriptionDraftUpdatePayload {
  draft: SubscriptionDraft | null;
  userErrors: SubscriptionDraftUserError[];
}

/** Return type for `tagsAdd` mutation. */
export interface TagsAddPayload {
  node: Node | null;
  userErrors: UserError[];
}

/** Return type for `tagsRemove` mutation. */
export interface TagsRemovePayload {
  node: Node | null;
  userErrors: UserError[];
}

/** Return type for `taxAppConfigure` mutation. */
export interface TaxAppConfigurePayload {
  taxAppConfiguration: TaxAppConfiguration | null;
  userErrors: TaxAppConfigureUserError[];
}

/** Return type for `taxSummaryCreate` mutation. */
export interface TaxSummaryCreatePayload {
  enqueuedOrders: Order[];
  userErrors: TaxSummaryCreateUserError[];
}

/** Return type for `themeCreate` mutation. */
export interface ThemeCreatePayload {
  theme: OnlineStoreTheme | null;
  userErrors: ThemeCreateUserError[];
}

/** Return type for `themeDelete` mutation. */
export interface ThemeDeletePayload {
  deletedThemeId: string | null;
  userErrors: ThemeDeleteUserError[];
}

/** Return type for `themeDuplicate` mutation. */
export interface ThemeDuplicatePayload {
  newTheme: OnlineStoreTheme | null;
  userErrors: ThemeDuplicateUserError[];
}

/** Return type for `themeFilesCopy` mutation. */
export interface ThemeFilesCopyPayload {
  copiedThemeFiles: OnlineStoreThemeFileOperationResult[];
  userErrors: OnlineStoreThemeFilesUserErrors[];
}

/** Return type for `themeFilesDelete` mutation. */
export interface ThemeFilesDeletePayload {
  deletedThemeFiles: OnlineStoreThemeFileOperationResult[];
  userErrors: OnlineStoreThemeFilesUserErrors[];
}

/** Return type for `themeFilesUpsert` mutation. */
export interface ThemeFilesUpsertPayload {
  job: Job | null;
  upsertedThemeFiles: OnlineStoreThemeFileOperationResult[];
  userErrors: OnlineStoreThemeFilesUserErrors[];
}

/** Return type for `themePublish` mutation. */
export interface ThemePublishPayload {
  theme: OnlineStoreTheme | null;
  userErrors: ThemePublishUserError[];
}

/** Return type for `themeUpdate` mutation. */
export interface ThemeUpdatePayload {
  theme: OnlineStoreTheme | null;
  userErrors: ThemeUpdateUserError[];
}

/** Return type for `transactionVoid` mutation. */
export interface TransactionVoidPayload {
  transaction: OrderTransaction | null;
  userErrors: TransactionVoidUserError[];
}

/** Return type for `translationsRegister` mutation. */
export interface TranslationsRegisterPayload {
  translations: Translation[];
  userErrors: TranslationUserError[];
}

/** Return type for `translationsRemove` mutation. */
export interface TranslationsRemovePayload {
  translations: Translation[];
  userErrors: TranslationUserError[];
}

/** Return type for `urlRedirectBulkDeleteAll` mutation. */
export interface UrlRedirectBulkDeleteAllPayload {
  job: Job | null;
  userErrors: UserError[];
}

/** Return type for `urlRedirectBulkDeleteByIds` mutation. */
export interface UrlRedirectBulkDeleteByIdsPayload {
  job: Job | null;
  userErrors: UrlRedirectBulkDeleteByIdsUserError[];
}

/** Return type for `urlRedirectBulkDeleteBySavedSearch` mutation. */
export interface UrlRedirectBulkDeleteBySavedSearchPayload {
  job: Job | null;
  userErrors: UrlRedirectBulkDeleteBySavedSearchUserError[];
}

/** Return type for `urlRedirectBulkDeleteBySearch` mutation. */
export interface UrlRedirectBulkDeleteBySearchPayload {
  job: Job | null;
  userErrors: UrlRedirectBulkDeleteBySearchUserError[];
}

/** Return type for `urlRedirectCreate` mutation. */
export interface UrlRedirectCreatePayload {
  urlRedirect: UrlRedirect | null;
  userErrors: UrlRedirectUserError[];
}

/** Return type for `urlRedirectDelete` mutation. */
export interface UrlRedirectDeletePayload {
  deletedUrlRedirectId: string | null;
  userErrors: UrlRedirectUserError[];
}

/** Return type for `urlRedirectImportCreate` mutation. */
export interface UrlRedirectImportCreatePayload {
  urlRedirectImport: UrlRedirectImport | null;
  userErrors: UrlRedirectImportUserError[];
}

/** Return type for `urlRedirectImportSubmit` mutation. */
export interface UrlRedirectImportSubmitPayload {
  job: Job | null;
  userErrors: UrlRedirectImportUserError[];
}

/** Return type for `urlRedirectUpdate` mutation. */
export interface UrlRedirectUpdatePayload {
  urlRedirect: UrlRedirect | null;
  userErrors: UrlRedirectUserError[];
}

/** Return type for `validationCreate` mutation. */
export interface ValidationCreatePayload {
  userErrors: ValidationUserError[];
  validation: Validation | null;
}

/** Return type for `validationDelete` mutation. */
export interface ValidationDeletePayload {
  deletedId: string | null;
  userErrors: ValidationUserError[];
}

/** Return type for `validationUpdate` mutation. */
export interface ValidationUpdatePayload {
  userErrors: ValidationUserError[];
  validation: Validation | null;
}

/** Return type for `webhookSubscriptionCreate` mutation. */
export interface WebhookSubscriptionCreatePayload {
  userErrors: UserError[];
  webhookSubscription: WebhookSubscription | null;
}

/** Return type for `webhookSubscriptionDelete` mutation. */
export interface WebhookSubscriptionDeletePayload {
  deletedWebhookSubscriptionId: string | null;
  userErrors: UserError[];
}

/** Return type for `webhookSubscriptionUpdate` mutation. */
export interface WebhookSubscriptionUpdatePayload {
  userErrors: UserError[];
  webhookSubscription: WebhookSubscription | null;
}

/** Return type for `webPixelCreate` mutation. */
export interface WebPixelCreatePayload {
  userErrors: ErrorsWebPixelUserError[];
  webPixel: WebPixel | null;
}

/** Return type for `webPixelDelete` mutation. */
export interface WebPixelDeletePayload {
  deletedWebPixelId: string | null;
  userErrors: ErrorsWebPixelUserError[];
}

/** Return type for `webPixelUpdate` mutation. */
export interface WebPixelUpdatePayload {
  userErrors: ErrorsWebPixelUserError[];
  webPixel: WebPixel | null;
}

/** Return type for `webPresenceCreate` mutation. */
export interface WebPresenceCreatePayload {
  userErrors: MarketUserError[];
  webPresence: MarketWebPresence | null;
}

/** Return type for `webPresenceDelete` mutation. */
export interface WebPresenceDeletePayload {
  deletedId: string | null;
  userErrors: MarketUserError[];
}

/** Return type for `webPresenceUpdate` mutation. */
export interface WebPresenceUpdatePayload {
  userErrors: MarketUserError[];
  webPresence: MarketWebPresence | null;
}

