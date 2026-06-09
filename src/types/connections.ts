// Auto-generated Shopify Admin GraphQL API 2026-04 - 182 connection types
// Do not edit manually - regenerate with parse_types.ps1

import type { CalculatedDiscountApplication, CashActivity, Catalog, CustomerAccountPage, CustomerMoment, DiscountApplication, Event, File, GiftCardTransaction, MarketRegion, Media, ReturnLineItemType, Sale, SalesAgreement, SegmentFilter, StoreCreditAccountTransaction } from './interfaces';
import type { AbandonedCheckout, AbandonedCheckoutEdge, AbandonedCheckoutLineItem, AbandonedCheckoutLineItemEdge, App, AppCredit, AppCreditEdge, AppDiscountType, AppDiscountTypeEdge, AppEdge, AppInstallation, AppInstallationEdge, AppPurchaseOneTime, AppPurchaseOneTimeEdge, AppRevenueAttributionRecord, AppRevenueAttributionRecordEdge, AppSubscription, AppSubscriptionEdge, AppUsageRecord, AppUsageRecordEdge, Article, ArticleAuthor, ArticleAuthorEdge, ArticleEdge, Blog, BlogEdge, BulkOperation, BulkOperationEdge, CalculatedDiscountApplicationEdge, CalculatedLineItem, CalculatedLineItemEdge, CartTransform, CartTransformEdge, CashActivityEdge, CashDrawer, CashDrawerEdge, CashManagementReasonCodeEdge, CashTrackingAdjustment, CashTrackingAdjustmentEdge, CashTrackingSession, CashTrackingSessionEdge, CatalogEdge, Channel, ChannelEdge, CheckoutAndAccountsConfiguration, CheckoutAndAccountsConfigurationEdge, CheckoutProfile, CheckoutProfileEdge, Collection, CollectionEdge, CollectionPublication, CollectionPublicationEdge, CombinedListingChild, CombinedListingChildEdge, Comment, CommentEdge, Company, CompanyContact, CompanyContactEdge, CompanyContactRole, CompanyContactRoleAssignment, CompanyContactRoleAssignmentEdge, CompanyContactRoleEdge, CompanyEdge, CompanyLocation, CompanyLocationEdge, CompanyLocationStaffMemberAssignment, CompanyLocationStaffMemberAssignmentEdge, CountryHarmonizedSystemCode, CountryHarmonizedSystemCodeEdge, CurrencySetting, CurrencySettingEdge, Customer, CustomerAccountPageEdge, CustomerEdge, CustomerMomentEdge, CustomerPaymentMethod, CustomerPaymentMethodEdge, CustomerSegmentMember, CustomerSegmentMemberEdge, CustomerVisitProductInfo, CustomerVisitProductInfoEdge, DeletionEvent, DeletionEventEdge, DeliveryCarrierService, DeliveryCarrierServiceEdge, DeliveryCustomization, DeliveryCustomizationEdge, DeliveryLocationGroupZone, DeliveryLocationGroupZoneEdge, DeliveryMethodDefinition, DeliveryMethodDefinitionEdge, DeliveryProfile, DeliveryProfileEdge, DeliveryProfileItem, DeliveryProfileItemEdge, DeliveryPromiseParticipant, DeliveryPromiseParticipantEdge, DiscountAllocation, DiscountAllocationEdge, DiscountApplicationEdge, DiscountAutomaticEdge, DiscountAutomaticNode, DiscountAutomaticNodeEdge, DiscountCodeNode, DiscountCodeNodeEdge, DiscountNode, DiscountNodeEdge, DiscountRedeemCode, DiscountRedeemCodeBulkCreationCode, DiscountRedeemCodeBulkCreationCodeEdge, DiscountRedeemCodeEdge, DraftOrder, DraftOrderEdge, DraftOrderLineItem, DraftOrderLineItemEdge, EventEdge, ExchangeLineItem, ExchangeLineItemEdge, FileEdge, Fulfillment, FulfillmentEdge, FulfillmentEvent, FulfillmentEventEdge, FulfillmentLineItem, FulfillmentLineItemEdge, FulfillmentOrder, FulfillmentOrderEdge, FulfillmentOrderLineItem, FulfillmentOrderLineItemEdge, FulfillmentOrderLocationForMove, FulfillmentOrderLocationForMoveEdge, FulfillmentOrderMerchantRequest, FulfillmentOrderMerchantRequestEdge, GiftCard, GiftCardEdge, GiftCardTransactionEdge, Image, ImageEdge, InventoryItem, InventoryItemEdge, InventoryLevel, InventoryLevelEdge, InventoryScheduledChange, InventoryScheduledChangeEdge, InventoryShipment, InventoryShipmentEdge, InventoryShipmentLineItem, InventoryShipmentLineItemEdge, InventoryTransfer, InventoryTransferEdge, InventoryTransferLineItem, InventoryTransferLineItemEdge, LineItem, LineItemEdge, LocalizationExtension, LocalizationExtensionEdge, LocalizedField, LocalizedFieldEdge, Location, LocationEdge, MailingAddress, MailingAddressEdge, Market, MarketCatalog, MarketCatalogEdge, MarketEdge, MarketingActivity, MarketingActivityEdge, MarketingEvent, MarketingEventEdge, MarketLocalizableResource, MarketLocalizableResourceEdge, MarketRegionEdge, MarketWebPresence, MarketWebPresenceEdge, MediaEdge, Menu, MenuEdge, Metafield, MetafieldDefinition, MetafieldDefinitionConstraintValue, MetafieldDefinitionConstraintValueEdge, MetafieldDefinitionEdge, MetafieldEdge, MetafieldReferenceEdge, MetafieldRelation, MetafieldRelationEdge, Metaobject, MetaobjectDefinition, MetaobjectDefinitionEdge, MetaobjectEdge, MobilePlatformApplicationEdge, OnlineStoreTheme, OnlineStoreThemeEdge, OnlineStoreThemeFile, OnlineStoreThemeFileEdge, Order, OrderAdjustment, OrderAdjustmentEdge, OrderEdge, OrderStagedChangeEdge, OrderTransaction, OrderTransactionEdge, Page, PageEdge, PageInfo, PaymentCustomization, PaymentCustomizationEdge, PaymentMandateResource, PaymentMandateResourceEdge, PaymentSchedule, PaymentScheduleEdge, PointOfSaleDevice, PointOfSaleDeviceEdge, PointOfSaleDevicePaymentSession, PointOfSaleDevicePaymentSessionEdge, PriceList, PriceListEdge, PriceListPrice, PriceListPriceEdge, PriceRuleDiscountCode, PriceRuleDiscountCodeEdge, Product, ProductBundleComponent, ProductBundleComponentEdge, ProductComponentType, ProductComponentTypeEdge, ProductEdge, ProductFeed, ProductFeedEdge, ProductPublication, ProductPublicationEdge, ProductVariant, ProductVariantComponent, ProductVariantComponentEdge, ProductVariantEdge, ProductVariantPricePair, ProductVariantPricePairEdge, Publication, PublicationEdge, QuantityPriceBreak, QuantityPriceBreakEdge, QuantityRule, QuantityRuleEdge, Refund, RefundEdge, RefundLineItem, RefundLineItemEdge, RefundShippingLine, RefundShippingLineEdge, ResourcePublication, ResourcePublicationEdge, ResourcePublicationV2, ResourcePublicationV2Edge, Return, ReturnableFulfillment, ReturnableFulfillmentEdge, ReturnableFulfillmentLineItem, ReturnableFulfillmentLineItemEdge, ReturnEdge, ReturnLineItemTypeEdge, ReturnReasonDefinition, ReturnReasonDefinitionEdge, ReverseDelivery, ReverseDeliveryEdge, ReverseDeliveryLineItem, ReverseDeliveryLineItemEdge, ReverseFulfillmentOrder, ReverseFulfillmentOrderEdge, ReverseFulfillmentOrderLineItem, ReverseFulfillmentOrderLineItemEdge, SaleEdge, SalesAgreementEdge, SavedSearch, SavedSearchEdge, ScriptTag, ScriptTagEdge, SearchResult, SearchResultEdge, Segment, SegmentEdge, SegmentFilterEdge, SegmentMigration, SegmentMigrationEdge, SegmentValue, SegmentValueEdge, SellingPlan, SellingPlanEdge, SellingPlanGroup, SellingPlanGroupEdge, ShippingLine, ShippingLineEdge, ShopifyFunction, ShopifyFunctionEdge, ShopifyPaymentsBalanceTransaction, ShopifyPaymentsBalanceTransactionEdge, ShopifyPaymentsBankAccount, ShopifyPaymentsBankAccountEdge, ShopifyPaymentsDispute, ShopifyPaymentsDisputeEdge, ShopifyPaymentsPayout, ShopifyPaymentsPayoutEdge, ShopPayPaymentRequestReceipt, ShopPayPaymentRequestReceiptEdge, StaffMember, StaffMemberEdge, StandardMetafieldDefinitionTemplate, StandardMetafieldDefinitionTemplateEdge, StoreCreditAccount, StoreCreditAccountEdge, StoreCreditAccountTransactionEdge, StorefrontAccessToken, StorefrontAccessTokenEdge, StringEdge, SubscriptionBillingAttempt, SubscriptionBillingAttemptEdge, SubscriptionBillingCycle, SubscriptionBillingCycleEdge, SubscriptionContract, SubscriptionContractEdge, SubscriptionDiscountEdge, SubscriptionLine, SubscriptionLineEdge, SubscriptionManualDiscount, SubscriptionManualDiscountEdge, TaxonomyCategory, TaxonomyCategoryAttributeEdge, TaxonomyCategoryEdge, TaxonomyValue, TaxonomyValueEdge, TenderTransaction, TenderTransactionEdge, TranslatableResource, TranslatableResourceEdge, UrlRedirect, UrlRedirectEdge, Validation, ValidationEdge, WebhookSubscription, WebhookSubscriptionEdge } from './objects';
import type { CashManagementReasonCode, DiscountAutomatic, MetafieldReference, MobilePlatformApplication, OrderStagedChange, SubscriptionDiscount, TaxonomyCategoryAttribute } from './unions';

/** An auto-generated type for paginating through multiple AbandonedCheckouts. */
export interface AbandonedCheckoutConnection {
  edges: AbandonedCheckoutEdge[];
  nodes: AbandonedCheckout[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple AbandonedCheckoutLineItems. */
export interface AbandonedCheckoutLineItemConnection {
  edges: AbandonedCheckoutLineItemEdge[];
  nodes: AbandonedCheckoutLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Apps. */
export interface AppConnection {
  edges: AppEdge[];
  nodes: App[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple AppCredits. */
export interface AppCreditConnection {
  edges: AppCreditEdge[];
  nodes: AppCredit[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple AppDiscountTypes. */
export interface AppDiscountTypeConnection {
  edges: AppDiscountTypeEdge[];
  nodes: AppDiscountType[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple AppInstallations. */
export interface AppInstallationConnection {
  edges: AppInstallationEdge[];
  nodes: AppInstallation[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple AppPurchaseOneTimes. */
export interface AppPurchaseOneTimeConnection {
  edges: AppPurchaseOneTimeEdge[];
  nodes: AppPurchaseOneTime[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple AppRevenueAttributionRecords. */
export interface AppRevenueAttributionRecordConnection {
  edges: AppRevenueAttributionRecordEdge[];
  nodes: AppRevenueAttributionRecord[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple AppSubscriptions. */
export interface AppSubscriptionConnection {
  edges: AppSubscriptionEdge[];
  nodes: AppSubscription[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple AppUsageRecords. */
export interface AppUsageRecordConnection {
  edges: AppUsageRecordEdge[];
  nodes: AppUsageRecord[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ArticleAuthors. */
export interface ArticleAuthorConnection {
  edges: ArticleAuthorEdge[];
  nodes: ArticleAuthor[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Articles. */
export interface ArticleConnection {
  edges: ArticleEdge[];
  nodes: Article[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Blogs. */
export interface BlogConnection {
  edges: BlogEdge[];
  nodes: Blog[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple BulkOperations. */
export interface BulkOperationConnection {
  edges: BulkOperationEdge[];
  nodes: BulkOperation[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CalculatedDiscountApplications. */
export interface CalculatedDiscountApplicationConnection {
  edges: CalculatedDiscountApplicationEdge[];
  nodes: CalculatedDiscountApplication[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CalculatedLineItems. */
export interface CalculatedLineItemConnection {
  edges: CalculatedLineItemEdge[];
  nodes: CalculatedLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CartTransforms. */
export interface CartTransformConnection {
  edges: CartTransformEdge[];
  nodes: CartTransform[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CashActivities. */
export interface CashActivityConnection {
  edges: CashActivityEdge[];
  nodes: CashActivity[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CashDrawers. */
export interface CashDrawerConnection {
  edges: CashDrawerEdge[];
  nodes: CashDrawer[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CashManagementReasonCodes. */
export interface CashManagementReasonCodeConnection {
  edges: CashManagementReasonCodeEdge[];
  nodes: CashManagementReasonCode[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CashTrackingAdjustments. */
export interface CashTrackingAdjustmentConnection {
  edges: CashTrackingAdjustmentEdge[];
  nodes: CashTrackingAdjustment[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CashTrackingSessions. */
export interface CashTrackingSessionConnection {
  edges: CashTrackingSessionEdge[];
  nodes: CashTrackingSession[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Catalogs. */
export interface CatalogConnection {
  edges: CatalogEdge[];
  nodes: Catalog[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Channels. */
export interface ChannelConnection {
  edges: ChannelEdge[];
  nodes: Channel[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CheckoutAndAccountsConfigurations. */
export interface CheckoutAndAccountsConfigurationConnection {
  edges: CheckoutAndAccountsConfigurationEdge[];
  nodes: CheckoutAndAccountsConfiguration[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CheckoutProfiles. */
export interface CheckoutProfileConnection {
  edges: CheckoutProfileEdge[];
  nodes: CheckoutProfile[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Collections. */
export interface CollectionConnection {
  edges: CollectionEdge[];
  nodes: Collection[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CollectionPublications. */
export interface CollectionPublicationConnection {
  edges: CollectionPublicationEdge[];
  nodes: CollectionPublication[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CombinedListingChildren. */
export interface CombinedListingChildConnection {
  edges: CombinedListingChildEdge[];
  nodes: CombinedListingChild[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Comments. */
export interface CommentConnection {
  edges: CommentEdge[];
  nodes: Comment[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Companies. */
export interface CompanyConnection {
  edges: CompanyEdge[];
  nodes: Company[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CompanyContacts. */
export interface CompanyContactConnection {
  edges: CompanyContactEdge[];
  nodes: CompanyContact[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CompanyContactRoleAssignments. */
export interface CompanyContactRoleAssignmentConnection {
  edges: CompanyContactRoleAssignmentEdge[];
  nodes: CompanyContactRoleAssignment[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CompanyContactRoles. */
export interface CompanyContactRoleConnection {
  edges: CompanyContactRoleEdge[];
  nodes: CompanyContactRole[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CompanyLocations. */
export interface CompanyLocationConnection {
  edges: CompanyLocationEdge[];
  nodes: CompanyLocation[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CompanyLocationStaffMemberAssignments. */
export interface CompanyLocationStaffMemberAssignmentConnection {
  edges: CompanyLocationStaffMemberAssignmentEdge[];
  nodes: CompanyLocationStaffMemberAssignment[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CountryHarmonizedSystemCodes. */
export interface CountryHarmonizedSystemCodeConnection {
  edges: CountryHarmonizedSystemCodeEdge[];
  nodes: CountryHarmonizedSystemCode[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CurrencySettings. */
export interface CurrencySettingConnection {
  edges: CurrencySettingEdge[];
  nodes: CurrencySetting[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CustomerAccountPages. */
export interface CustomerAccountPageConnection {
  edges: CustomerAccountPageEdge[];
  nodes: CustomerAccountPage[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Customers. */
export interface CustomerConnection {
  edges: CustomerEdge[];
  nodes: Customer[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CustomerMoments. */
export interface CustomerMomentConnection {
  edges: CustomerMomentEdge[];
  nodes: CustomerMoment[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CustomerPaymentMethods. */
export interface CustomerPaymentMethodConnection {
  edges: CustomerPaymentMethodEdge[];
  nodes: CustomerPaymentMethod[];
  pageInfo: PageInfo;
}

/** The connection type for the `CustomerSegmentMembers` object. */
export interface CustomerSegmentMemberConnection {
  edges: CustomerSegmentMemberEdge[];
  nodes: CustomerSegmentMember[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple CustomerVisitProductInfos. */
export interface CustomerVisitProductInfoConnection {
  edges: CustomerVisitProductInfoEdge[];
  nodes: CustomerVisitProductInfo[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DeletionEvents. */
export interface DeletionEventConnection {
  edges: DeletionEventEdge[];
  nodes: DeletionEvent[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DeliveryCarrierServices. */
export interface DeliveryCarrierServiceConnection {
  edges: DeliveryCarrierServiceEdge[];
  nodes: DeliveryCarrierService[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DeliveryCustomizations. */
export interface DeliveryCustomizationConnection {
  edges: DeliveryCustomizationEdge[];
  nodes: DeliveryCustomization[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DeliveryLocationGroupZones. */
export interface DeliveryLocationGroupZoneConnection {
  edges: DeliveryLocationGroupZoneEdge[];
  nodes: DeliveryLocationGroupZone[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DeliveryMethodDefinitions. */
export interface DeliveryMethodDefinitionConnection {
  edges: DeliveryMethodDefinitionEdge[];
  nodes: DeliveryMethodDefinition[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DeliveryProfiles. */
export interface DeliveryProfileConnection {
  edges: DeliveryProfileEdge[];
  nodes: DeliveryProfile[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DeliveryProfileItems. */
export interface DeliveryProfileItemConnection {
  edges: DeliveryProfileItemEdge[];
  nodes: DeliveryProfileItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DeliveryPromiseParticipants. */
export interface DeliveryPromiseParticipantConnection {
  edges: DeliveryPromiseParticipantEdge[];
  nodes: DeliveryPromiseParticipant[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DiscountAllocations. */
export interface DiscountAllocationConnection {
  edges: DiscountAllocationEdge[];
  nodes: DiscountAllocation[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DiscountApplications. */
export interface DiscountApplicationConnection {
  edges: DiscountApplicationEdge[];
  nodes: DiscountApplication[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DiscountAutomatics. */
export interface DiscountAutomaticConnection {
  edges: DiscountAutomaticEdge[];
  nodes: DiscountAutomatic[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DiscountAutomaticNodes. */
export interface DiscountAutomaticNodeConnection {
  edges: DiscountAutomaticNodeEdge[];
  nodes: DiscountAutomaticNode[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DiscountCodeNodes. */
export interface DiscountCodeNodeConnection {
  edges: DiscountCodeNodeEdge[];
  nodes: DiscountCodeNode[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DiscountNodes. */
export interface DiscountNodeConnection {
  edges: DiscountNodeEdge[];
  nodes: DiscountNode[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DiscountRedeemCodeBulkCreationCodes. */
export interface DiscountRedeemCodeBulkCreationCodeConnection {
  edges: DiscountRedeemCodeBulkCreationCodeEdge[];
  nodes: DiscountRedeemCodeBulkCreationCode[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DiscountRedeemCodes. */
export interface DiscountRedeemCodeConnection {
  edges: DiscountRedeemCodeEdge[];
  nodes: DiscountRedeemCode[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DraftOrders. */
export interface DraftOrderConnection {
  edges: DraftOrderEdge[];
  nodes: DraftOrder[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple DraftOrderLineItems. */
export interface DraftOrderLineItemConnection {
  edges: DraftOrderLineItemEdge[];
  nodes: DraftOrderLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Events. */
export interface EventConnection {
  edges: EventEdge[];
  nodes: Event[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ExchangeLineItems. */
export interface ExchangeLineItemConnection {
  edges: ExchangeLineItemEdge[];
  nodes: ExchangeLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Files. */
export interface FileConnection {
  edges: FileEdge[];
  nodes: File[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Fulfillments. */
export interface FulfillmentConnection {
  edges: FulfillmentEdge[];
  nodes: Fulfillment[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple FulfillmentEvents. */
export interface FulfillmentEventConnection {
  edges: FulfillmentEventEdge[];
  nodes: FulfillmentEvent[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple FulfillmentLineItems. */
export interface FulfillmentLineItemConnection {
  edges: FulfillmentLineItemEdge[];
  nodes: FulfillmentLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple FulfillmentOrders. */
export interface FulfillmentOrderConnection {
  edges: FulfillmentOrderEdge[];
  nodes: FulfillmentOrder[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple FulfillmentOrderLineItems. */
export interface FulfillmentOrderLineItemConnection {
  edges: FulfillmentOrderLineItemEdge[];
  nodes: FulfillmentOrderLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple FulfillmentOrderLocationForMoves. */
export interface FulfillmentOrderLocationForMoveConnection {
  edges: FulfillmentOrderLocationForMoveEdge[];
  nodes: FulfillmentOrderLocationForMove[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple FulfillmentOrderMerchantRequests. */
export interface FulfillmentOrderMerchantRequestConnection {
  edges: FulfillmentOrderMerchantRequestEdge[];
  nodes: FulfillmentOrderMerchantRequest[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple GiftCards. */
export interface GiftCardConnection {
  edges: GiftCardEdge[];
  nodes: GiftCard[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple GiftCardTransactions. */
export interface GiftCardTransactionConnection {
  edges: GiftCardTransactionEdge[];
  nodes: GiftCardTransaction[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Images. */
export interface ImageConnection {
  edges: ImageEdge[];
  nodes: Image[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple InventoryItems. */
export interface InventoryItemConnection {
  edges: InventoryItemEdge[];
  nodes: InventoryItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple InventoryLevels. */
export interface InventoryLevelConnection {
  edges: InventoryLevelEdge[];
  nodes: InventoryLevel[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple InventoryScheduledChanges. */
export interface InventoryScheduledChangeConnection {
  edges: InventoryScheduledChangeEdge[];
  nodes: InventoryScheduledChange[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple InventoryShipments. */
export interface InventoryShipmentConnection {
  edges: InventoryShipmentEdge[];
  nodes: InventoryShipment[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple InventoryShipmentLineItems. */
export interface InventoryShipmentLineItemConnection {
  edges: InventoryShipmentLineItemEdge[];
  nodes: InventoryShipmentLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple InventoryTransfers. */
export interface InventoryTransferConnection {
  edges: InventoryTransferEdge[];
  nodes: InventoryTransfer[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple InventoryTransferLineItems. */
export interface InventoryTransferLineItemConnection {
  edges: InventoryTransferLineItemEdge[];
  nodes: InventoryTransferLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple LineItems. */
export interface LineItemConnection {
  edges: LineItemEdge[];
  nodes: LineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple LocalizationExtensions. */
export interface LocalizationExtensionConnection {
  edges: LocalizationExtensionEdge[];
  nodes: LocalizationExtension[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple LocalizedFields. */
export interface LocalizedFieldConnection {
  edges: LocalizedFieldEdge[];
  nodes: LocalizedField[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Locations. */
export interface LocationConnection {
  edges: LocationEdge[];
  nodes: Location[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MailingAddresses. */
export interface MailingAddressConnection {
  edges: MailingAddressEdge[];
  nodes: MailingAddress[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MarketCatalogs. */
export interface MarketCatalogConnection {
  edges: MarketCatalogEdge[];
  nodes: MarketCatalog[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Markets. */
export interface MarketConnection {
  edges: MarketEdge[];
  nodes: Market[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MarketingActivities. */
export interface MarketingActivityConnection {
  edges: MarketingActivityEdge[];
  nodes: MarketingActivity[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MarketingEvents. */
export interface MarketingEventConnection {
  edges: MarketingEventEdge[];
  nodes: MarketingEvent[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MarketLocalizableResources. */
export interface MarketLocalizableResourceConnection {
  edges: MarketLocalizableResourceEdge[];
  nodes: MarketLocalizableResource[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MarketRegions. */
export interface MarketRegionConnection {
  edges: MarketRegionEdge[];
  nodes: MarketRegion[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MarketWebPresences. */
export interface MarketWebPresenceConnection {
  edges: MarketWebPresenceEdge[];
  nodes: MarketWebPresence[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Media. */
export interface MediaConnection {
  edges: MediaEdge[];
  nodes: Media[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Menus. */
export interface MenuConnection {
  edges: MenuEdge[];
  nodes: Menu[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Metafields. */
export interface MetafieldConnection {
  edges: MetafieldEdge[];
  nodes: Metafield[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MetafieldDefinitions. */
export interface MetafieldDefinitionConnection {
  edges: MetafieldDefinitionEdge[];
  nodes: MetafieldDefinition[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MetafieldDefinitionConstraintValues. */
export interface MetafieldDefinitionConstraintValueConnection {
  edges: MetafieldDefinitionConstraintValueEdge[];
  nodes: MetafieldDefinitionConstraintValue[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MetafieldReferences. */
export interface MetafieldReferenceConnection {
  edges: MetafieldReferenceEdge[];
  nodes: MetafieldReference[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MetafieldRelations. */
export interface MetafieldRelationConnection {
  edges: MetafieldRelationEdge[];
  nodes: MetafieldRelation[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Metaobjects. */
export interface MetaobjectConnection {
  edges: MetaobjectEdge[];
  nodes: Metaobject[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MetaobjectDefinitions. */
export interface MetaobjectDefinitionConnection {
  edges: MetaobjectDefinitionEdge[];
  nodes: MetaobjectDefinition[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple MobilePlatformApplications. */
export interface MobilePlatformApplicationConnection {
  edges: MobilePlatformApplicationEdge[];
  nodes: MobilePlatformApplication[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple OnlineStoreThemes. */
export interface OnlineStoreThemeConnection {
  edges: OnlineStoreThemeEdge[];
  nodes: OnlineStoreTheme[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple OnlineStoreThemeFiles. */
export interface OnlineStoreThemeFileConnection {
  edges: OnlineStoreThemeFileEdge[];
  nodes: OnlineStoreThemeFile[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple OrderAdjustments. */
export interface OrderAdjustmentConnection {
  edges: OrderAdjustmentEdge[];
  nodes: OrderAdjustment[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Orders. */
export interface OrderConnection {
  edges: OrderEdge[];
  nodes: Order[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple OrderStagedChanges. */
export interface OrderStagedChangeConnection {
  edges: OrderStagedChangeEdge[];
  nodes: OrderStagedChange[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple OrderTransactions. */
export interface OrderTransactionConnection {
  edges: OrderTransactionEdge[];
  nodes: OrderTransaction[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Pages. */
export interface PageConnection {
  edges: PageEdge[];
  nodes: Page[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple PaymentCustomizations. */
export interface PaymentCustomizationConnection {
  edges: PaymentCustomizationEdge[];
  nodes: PaymentCustomization[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple PaymentMandateResources. */
export interface PaymentMandateResourceConnection {
  edges: PaymentMandateResourceEdge[];
  nodes: PaymentMandateResource[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple PaymentSchedules. */
export interface PaymentScheduleConnection {
  edges: PaymentScheduleEdge[];
  nodes: PaymentSchedule[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple PointOfSaleDevices. */
export interface PointOfSaleDeviceConnection {
  edges: PointOfSaleDeviceEdge[];
  nodes: PointOfSaleDevice[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple PointOfSaleDevicePaymentSessions. */
export interface PointOfSaleDevicePaymentSessionConnection {
  edges: PointOfSaleDevicePaymentSessionEdge[];
  nodes: PointOfSaleDevicePaymentSession[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple PriceLists. */
export interface PriceListConnection {
  edges: PriceListEdge[];
  nodes: PriceList[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple PriceListPrices. */
export interface PriceListPriceConnection {
  edges: PriceListPriceEdge[];
  nodes: PriceListPrice[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple PriceRuleDiscountCodes. */
export interface PriceRuleDiscountCodeConnection {
  edges: PriceRuleDiscountCodeEdge[];
  nodes: PriceRuleDiscountCode[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ProductBundleComponents. */
export interface ProductBundleComponentConnection {
  edges: ProductBundleComponentEdge[];
  nodes: ProductBundleComponent[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ProductComponentTypes. */
export interface ProductComponentTypeConnection {
  edges: ProductComponentTypeEdge[];
  nodes: ProductComponentType[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Products. */
export interface ProductConnection {
  edges: ProductEdge[];
  nodes: Product[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ProductFeeds. */
export interface ProductFeedConnection {
  edges: ProductFeedEdge[];
  nodes: ProductFeed[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ProductPublications. */
export interface ProductPublicationConnection {
  edges: ProductPublicationEdge[];
  nodes: ProductPublication[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ProductVariantComponents. */
export interface ProductVariantComponentConnection {
  edges: ProductVariantComponentEdge[];
  nodes: ProductVariantComponent[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ProductVariants. */
export interface ProductVariantConnection {
  edges: ProductVariantEdge[];
  nodes: ProductVariant[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ProductVariantPricePairs. */
export interface ProductVariantPricePairConnection {
  edges: ProductVariantPricePairEdge[];
  nodes: ProductVariantPricePair[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Publications. */
export interface PublicationConnection {
  edges: PublicationEdge[];
  nodes: Publication[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple QuantityPriceBreaks. */
export interface QuantityPriceBreakConnection {
  edges: QuantityPriceBreakEdge[];
  nodes: QuantityPriceBreak[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple QuantityRules. */
export interface QuantityRuleConnection {
  edges: QuantityRuleEdge[];
  nodes: QuantityRule[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Refunds. */
export interface RefundConnection {
  edges: RefundEdge[];
  nodes: Refund[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple RefundLineItems. */
export interface RefundLineItemConnection {
  edges: RefundLineItemEdge[];
  nodes: RefundLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple RefundShippingLines. */
export interface RefundShippingLineConnection {
  edges: RefundShippingLineEdge[];
  nodes: RefundShippingLine[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ResourcePublications. */
export interface ResourcePublicationConnection {
  edges: ResourcePublicationEdge[];
  nodes: ResourcePublication[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ResourcePublicationV2s. */
export interface ResourcePublicationV2Connection {
  edges: ResourcePublicationV2Edge[];
  nodes: ResourcePublicationV2[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ReturnableFulfillments. */
export interface ReturnableFulfillmentConnection {
  edges: ReturnableFulfillmentEdge[];
  nodes: ReturnableFulfillment[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ReturnableFulfillmentLineItems. */
export interface ReturnableFulfillmentLineItemConnection {
  edges: ReturnableFulfillmentLineItemEdge[];
  nodes: ReturnableFulfillmentLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Returns. */
export interface ReturnConnection {
  edges: ReturnEdge[];
  nodes: Return[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ReturnLineItemTypes. */
export interface ReturnLineItemTypeConnection {
  edges: ReturnLineItemTypeEdge[];
  nodes: ReturnLineItemType[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ReturnReasonDefinitions. */
export interface ReturnReasonDefinitionConnection {
  edges: ReturnReasonDefinitionEdge[];
  nodes: ReturnReasonDefinition[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ReverseDeliveries. */
export interface ReverseDeliveryConnection {
  edges: ReverseDeliveryEdge[];
  nodes: ReverseDelivery[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ReverseDeliveryLineItems. */
export interface ReverseDeliveryLineItemConnection {
  edges: ReverseDeliveryLineItemEdge[];
  nodes: ReverseDeliveryLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ReverseFulfillmentOrders. */
export interface ReverseFulfillmentOrderConnection {
  edges: ReverseFulfillmentOrderEdge[];
  nodes: ReverseFulfillmentOrder[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ReverseFulfillmentOrderLineItems. */
export interface ReverseFulfillmentOrderLineItemConnection {
  edges: ReverseFulfillmentOrderLineItemEdge[];
  nodes: ReverseFulfillmentOrderLineItem[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Sales. */
export interface SaleConnection {
  edges: SaleEdge[];
  nodes: Sale[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SalesAgreements. */
export interface SalesAgreementConnection {
  edges: SalesAgreementEdge[];
  nodes: SalesAgreement[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SavedSearches. */
export interface SavedSearchConnection {
  edges: SavedSearchEdge[];
  nodes: SavedSearch[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ScriptTags. */
export interface ScriptTagConnection {
  edges: ScriptTagEdge[];
  nodes: ScriptTag[];
  pageInfo: PageInfo;
}

/** The connection type for SearchResult. */
export interface SearchResultConnection {
  edges: SearchResultEdge[];
  nodes: SearchResult[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Segments. */
export interface SegmentConnection {
  edges: SegmentEdge[];
  nodes: Segment[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SegmentFilters. */
export interface SegmentFilterConnection {
  edges: SegmentFilterEdge[];
  nodes: SegmentFilter[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SegmentMigrations. */
export interface SegmentMigrationConnection {
  edges: SegmentMigrationEdge[];
  nodes: SegmentMigration[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SegmentValues. */
export interface SegmentValueConnection {
  edges: SegmentValueEdge[];
  nodes: SegmentValue[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SellingPlans. */
export interface SellingPlanConnection {
  edges: SellingPlanEdge[];
  nodes: SellingPlan[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SellingPlanGroups. */
export interface SellingPlanGroupConnection {
  edges: SellingPlanGroupEdge[];
  nodes: SellingPlanGroup[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ShippingLines. */
export interface ShippingLineConnection {
  edges: ShippingLineEdge[];
  nodes: ShippingLine[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ShopifyFunctions. */
export interface ShopifyFunctionConnection {
  edges: ShopifyFunctionEdge[];
  nodes: ShopifyFunction[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ShopifyPaymentsBalanceTransactions. */
export interface ShopifyPaymentsBalanceTransactionConnection {
  edges: ShopifyPaymentsBalanceTransactionEdge[];
  nodes: ShopifyPaymentsBalanceTransaction[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ShopifyPaymentsBankAccounts. */
export interface ShopifyPaymentsBankAccountConnection {
  edges: ShopifyPaymentsBankAccountEdge[];
  nodes: ShopifyPaymentsBankAccount[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ShopifyPaymentsDisputes. */
export interface ShopifyPaymentsDisputeConnection {
  edges: ShopifyPaymentsDisputeEdge[];
  nodes: ShopifyPaymentsDispute[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ShopifyPaymentsPayouts. */
export interface ShopifyPaymentsPayoutConnection {
  edges: ShopifyPaymentsPayoutEdge[];
  nodes: ShopifyPaymentsPayout[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple ShopPayPaymentRequestReceipts. */
export interface ShopPayPaymentRequestReceiptConnection {
  edges: ShopPayPaymentRequestReceiptEdge[];
  nodes: ShopPayPaymentRequestReceipt[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple StaffMembers. */
export interface StaffMemberConnection {
  edges: StaffMemberEdge[];
  nodes: StaffMember[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple StandardMetafieldDefinitionTemplates. */
export interface StandardMetafieldDefinitionTemplateConnection {
  edges: StandardMetafieldDefinitionTemplateEdge[];
  nodes: StandardMetafieldDefinitionTemplate[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple StoreCreditAccounts. */
export interface StoreCreditAccountConnection {
  edges: StoreCreditAccountEdge[];
  nodes: StoreCreditAccount[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple StoreCreditAccountTransactions. */
export interface StoreCreditAccountTransactionConnection {
  edges: StoreCreditAccountTransactionEdge[];
  nodes: StoreCreditAccountTransaction[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple StorefrontAccessTokens. */
export interface StorefrontAccessTokenConnection {
  edges: StorefrontAccessTokenEdge[];
  nodes: StorefrontAccessToken[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Strings. */
export interface StringConnection {
  edges: StringEdge[];
  nodes: String[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SubscriptionBillingAttempts. */
export interface SubscriptionBillingAttemptConnection {
  edges: SubscriptionBillingAttemptEdge[];
  nodes: SubscriptionBillingAttempt[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SubscriptionBillingCycles. */
export interface SubscriptionBillingCycleConnection {
  edges: SubscriptionBillingCycleEdge[];
  nodes: SubscriptionBillingCycle[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SubscriptionContracts. */
export interface SubscriptionContractConnection {
  edges: SubscriptionContractEdge[];
  nodes: SubscriptionContract[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SubscriptionDiscounts. */
export interface SubscriptionDiscountConnection {
  edges: SubscriptionDiscountEdge[];
  nodes: SubscriptionDiscount[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SubscriptionLines. */
export interface SubscriptionLineConnection {
  edges: SubscriptionLineEdge[];
  nodes: SubscriptionLine[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple SubscriptionManualDiscounts. */
export interface SubscriptionManualDiscountConnection {
  edges: SubscriptionManualDiscountEdge[];
  nodes: SubscriptionManualDiscount[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple TaxonomyCategoryAttributes. */
export interface TaxonomyCategoryAttributeConnection {
  edges: TaxonomyCategoryAttributeEdge[];
  nodes: TaxonomyCategoryAttribute[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple TaxonomyCategories. */
export interface TaxonomyCategoryConnection {
  edges: TaxonomyCategoryEdge[];
  nodes: TaxonomyCategory[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple TaxonomyValues. */
export interface TaxonomyValueConnection {
  edges: TaxonomyValueEdge[];
  nodes: TaxonomyValue[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple TenderTransactions. */
export interface TenderTransactionConnection {
  edges: TenderTransactionEdge[];
  nodes: TenderTransaction[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple TranslatableResources. */
export interface TranslatableResourceConnection {
  edges: TranslatableResourceEdge[];
  nodes: TranslatableResource[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple UrlRedirects. */
export interface UrlRedirectConnection {
  edges: UrlRedirectEdge[];
  nodes: UrlRedirect[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple Validations. */
export interface ValidationConnection {
  edges: ValidationEdge[];
  nodes: Validation[];
  pageInfo: PageInfo;
}

/** An auto-generated type for paginating through multiple WebhookSubscriptions. */
export interface WebhookSubscriptionConnection {
  edges: WebhookSubscriptionEdge[];
  nodes: WebhookSubscription[];
  pageInfo: PageInfo;
}

