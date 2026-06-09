// Auto-generated Shopify Admin GraphQL API 2026-04 - 56 union types
// Do not edit manually - regenerate with parse_types.ps1

import type { AddAllProductsOperation, AllDiscountItems, AndroidApplication, AppInstallation, AppleApplication, AppRecurringPricing, AppSubscriptionDiscountAmount, AppSubscriptionDiscountPercentage, AppUsagePricing, Article, BankAccount, Blog, CalculatedDraftOrderLineItem, CardPaymentDetails, CashManagementCustomReasonCode, CashManagementDefaultReasonCode, CashManagementSystemReasonCode, CatalogCsvOperation, CheckoutAndAccountsConfigurationBrandingCustomFontGroup, CheckoutAndAccountsConfigurationBrandingImage, CheckoutAndAccountsConfigurationBrandingShopifyFontGroup, Collection, CollectionRuleCategoryCondition, CollectionRuleMetafieldCondition, CollectionRuleProductCategoryCondition, CollectionRuleTextCondition, Company, CompanyLocation, Customer, CustomerCreditCard, CustomerPaypalBillingAgreement, CustomerShopPayAgreement, DeliveryCustomization, DeliveryParticipant, DeliveryRateDefinition, DepositPercentage, DiscountAmount, DiscountAutomaticApp, DiscountAutomaticBasic, DiscountAutomaticBxgy, DiscountAutomaticFreeShipping, DiscountAutomaticNode, DiscountBuyerSelectionAll, DiscountCodeApp, DiscountCodeBasic, DiscountCodeBxgy, DiscountCodeFreeShipping, DiscountCodeNode, DiscountCollections, DiscountCountries, DiscountCountryAll, DiscountCustomerAll, DiscountCustomers, DiscountCustomerSegments, DiscountMinimumQuantity, DiscountMinimumSubtotal, DiscountNode, DiscountOnQuantity, DiscountPercentage, DiscountProducts, DiscountPurchaseAmount, DiscountQuantity, DraftOrder, DraftOrderLineItem, FulfillmentOrder, GenericFile, InventoryTransfer, InvoiceReturnOutcome, LocalPaymentMethodsPaymentDetails, Location, Market, MediaImage, Metaobject, Model3d, MoneyV2, OnlineStoreThemeFileBodyBase64, OnlineStoreThemeFileBodyText, OnlineStoreThemeFileBodyUrl, Order, OrderStagedChangeAddCustomItem, OrderStagedChangeAddLineItemDiscount, OrderStagedChangeAddShippingLine, OrderStagedChangeAddVariant, OrderStagedChangeDecrementItem, OrderStagedChangeIncrementItem, OrderStagedChangeRemoveDiscount, OrderStagedChangeRemoveShippingLine, OrderTransaction, Page, PaymentCustomization, PaypalWalletPaymentDetails, PriceRuleFixedAmountValue, PriceRulePercentValue, PricingPercentageValue, Product, ProductVariant, PublicationResourceOperation, PurchasingCompany, RefundReturnOutcome, ReverseDeliveryShippingDeliverable, SellingPlanCheckoutChargePercentageValue, SellingPlanFixedBillingPolicy, SellingPlanFixedDeliveryPolicy, SellingPlanFixedPricingPolicy, SellingPlanPricingPolicyPercentageValue, SellingPlanRecurringBillingPolicy, SellingPlanRecurringDeliveryPolicy, SellingPlanRecurringPricingPolicy, ShippingLine, Shop, ShopPayInstallmentsPaymentDetails, SubscriptionAppliedCodeDiscount, SubscriptionBillingAttemptActionRequiredState, SubscriptionBillingAttemptFailedState, SubscriptionBillingAttemptGeneralError, SubscriptionBillingAttemptInventoryError, SubscriptionBillingAttemptPaymentChallenge, SubscriptionBillingAttemptPaymentError, SubscriptionBillingAttemptPendingState, SubscriptionBillingAttemptSuccessState, SubscriptionBillingAttemptUnexpectedError, SubscriptionDeliveryMethodLocalDelivery, SubscriptionDeliveryMethodPickup, SubscriptionDeliveryMethodShipping, SubscriptionDeliveryOptionResultFailure, SubscriptionDeliveryOptionResultSuccess, SubscriptionDiscountFixedAmountValue, SubscriptionDiscountPercentageValue, SubscriptionLocalDeliveryOption, SubscriptionManualDiscount, SubscriptionPickupOption, SubscriptionShippingOption, SubscriptionShippingOptionResultFailure, SubscriptionShippingOptionResultSuccess, TaxonomyAttribute, TaxonomyChoiceListAttribute, TaxonomyMeasurementAttribute, TaxonomyValue, TenderTransactionCreditCardDetails, VaultCreditCard, VaultPaypalBillingAgreement, Video, WebhookEventBridgeEndpoint, WebhookHttpEndpoint, WebhookPubSubEndpoint, Weight } from './objects';

/** The information about the price that's charged to a shop every plan period. The concrete type can be `AppRecurringPricing` for recurring billing or `AppUsagePricing` for usage-based billing. */
export type AppPricingDetails = AppRecurringPricing | AppUsagePricing;

/** The value of the discount. */
export type AppSubscriptionDiscountValue = AppSubscriptionDiscountAmount | AppSubscriptionDiscountPercentage;

export type CashManagementReasonCode = CashManagementCustomReasonCode | CashManagementDefaultReasonCode | CashManagementSystemReasonCode;

export type CheckoutAndAccountsConfigurationBrandingFontGroup = CheckoutAndAccountsConfigurationBrandingCustomFontGroup | CheckoutAndAccountsConfigurationBrandingShopifyFontGroup;

export type CheckoutAndAccountsConfigurationBrandingImageValue = CheckoutAndAccountsConfigurationBrandingImage;

export type CollectionRuleConditionObject = CollectionRuleCategoryCondition | CollectionRuleMetafieldCondition | CollectionRuleProductCategoryCondition | CollectionRuleTextCondition;

export type CollectionRuleConditionsRuleObject = CollectionRuleMetafieldCondition;

/** The main embed of a comment event. */
export type CommentEventEmbed = Customer | DraftOrder | InventoryTransfer | Order | Product | ProductVariant;

export type CustomerPaymentInstrument = BankAccount | CustomerCreditCard | CustomerPaypalBillingAgreement | CustomerShopPayAgreement;

export type DeliveryConditionCriteria = MoneyV2 | Weight;

export type DeliveryPromiseParticipantOwner = ProductVariant;

export type DeliveryRateProvider = DeliveryParticipant | DeliveryRateDefinition;

/** Configuration of the deposit. */
export type DepositConfiguration = DepositPercentage;

export type Discount = DiscountAutomaticApp | DiscountAutomaticBasic | DiscountAutomaticBxgy | DiscountAutomaticFreeShipping | DiscountCodeApp | DiscountCodeBasic | DiscountCodeBxgy | DiscountCodeFreeShipping;

export type DiscountAutomatic = DiscountAutomaticApp | DiscountAutomaticBasic | DiscountAutomaticBxgy | DiscountAutomaticFreeShipping;

export type DiscountCode = DiscountCodeApp | DiscountCodeBasic | DiscountCodeBxgy | DiscountCodeFreeShipping;

export type DiscountContext = DiscountBuyerSelectionAll | DiscountCustomerSegments | DiscountCustomers;

export type DiscountCustomerBuysValue = DiscountPurchaseAmount | DiscountQuantity;

export type DiscountCustomerGetsValue = DiscountAmount | DiscountOnQuantity | DiscountPercentage;

export type DiscountCustomerSelection = DiscountCustomerAll | DiscountCustomerSegments | DiscountCustomers;

export type DiscountEffect = DiscountAmount | DiscountPercentage;

export type DiscountItems = AllDiscountItems | DiscountCollections | DiscountProducts;

export type DiscountMinimumRequirement = DiscountMinimumQuantity | DiscountMinimumSubtotal;

export type DiscountShippingDestinationSelection = DiscountCountries | DiscountCountryAll;

export type DraftOrderPlatformDiscountAllocationTarget = CalculatedDraftOrderLineItem | DraftOrderLineItem | ShippingLine;

/** The resource referenced by the metafield value. */
export type MetafieldReference = Article | Collection | Company | Customer | GenericFile | MediaImage | Metaobject | Model3d | Order | Page | Product | ProductVariant | TaxonomyValue | Video;

/** Types of resources that may use metafields to reference other resources. */
export type MetafieldReferencer = AppInstallation | Article | Blog | Collection | Company | CompanyLocation | Customer | DeliveryCustomization | DiscountAutomaticNode | DiscountCodeNode | DiscountNode | DraftOrder | FulfillmentOrder | Location | Market | Metaobject | Order | Page | PaymentCustomization | Product | ProductVariant | Shop;

export type MobilePlatformApplication = AndroidApplication | AppleApplication;

export type OnlineStoreThemeFileBody = OnlineStoreThemeFileBodyBase64 | OnlineStoreThemeFileBodyText | OnlineStoreThemeFileBodyUrl;

export type OrderStagedChange = OrderStagedChangeAddCustomItem | OrderStagedChangeAddLineItemDiscount | OrderStagedChangeAddShippingLine | OrderStagedChangeAddVariant | OrderStagedChangeDecrementItem | OrderStagedChangeIncrementItem | OrderStagedChangeRemoveDiscount | OrderStagedChangeRemoveShippingLine;

export type PaymentDetails = CardPaymentDetails | LocalPaymentMethodsPaymentDetails | PaypalWalletPaymentDetails | ShopPayInstallmentsPaymentDetails;

export type PaymentInstrument = BankAccount | VaultCreditCard | VaultPaypalBillingAgreement;

export type PriceRuleValue = PriceRuleFixedAmountValue | PriceRulePercentValue;

/** The type of value given to a customer when a discount is applied to an order. For example, the application of the discount might give the customer a percentage off a specified item. Alternatively, the application of the discount might give the customer a monetary value in a gi... */
export type PricingValue = MoneyV2 | PricingPercentageValue;

export type PublicationOperation = AddAllProductsOperation | CatalogCsvOperation | PublicationResourceOperation;

export type PurchasingEntity = Customer | PurchasingCompany;

export type ReturnOutcomeFinancialTransfer = InvoiceReturnOutcome | RefundReturnOutcome;

export type ReverseDeliveryDeliverable = ReverseDeliveryShippingDeliverable;

export type SellingPlanBillingPolicy = SellingPlanFixedBillingPolicy | SellingPlanRecurringBillingPolicy;

export type SellingPlanCheckoutChargeValue = MoneyV2 | SellingPlanCheckoutChargePercentageValue;

export type SellingPlanDeliveryPolicy = SellingPlanFixedDeliveryPolicy | SellingPlanRecurringDeliveryPolicy;

export type SellingPlanPricingPolicy = SellingPlanFixedPricingPolicy | SellingPlanRecurringPricingPolicy;

export type SellingPlanPricingPolicyAdjustmentValue = MoneyV2 | SellingPlanPricingPolicyPercentageValue;

/** The origin of a store credit account transaction. */
export type StoreCreditAccountTransactionOrigin = OrderTransaction;

export type SubscriptionBillingAttemptAction = SubscriptionBillingAttemptPaymentChallenge;

export type SubscriptionBillingAttemptError = SubscriptionBillingAttemptGeneralError | SubscriptionBillingAttemptInventoryError | SubscriptionBillingAttemptPaymentError | SubscriptionBillingAttemptUnexpectedError;

export type SubscriptionBillingAttemptState = SubscriptionBillingAttemptActionRequiredState | SubscriptionBillingAttemptFailedState | SubscriptionBillingAttemptPendingState | SubscriptionBillingAttemptSuccessState;

export type SubscriptionDeliveryMethod = SubscriptionDeliveryMethodLocalDelivery | SubscriptionDeliveryMethodPickup | SubscriptionDeliveryMethodShipping;

export type SubscriptionDeliveryOption = SubscriptionLocalDeliveryOption | SubscriptionPickupOption | SubscriptionShippingOption;

export type SubscriptionDeliveryOptionResult = SubscriptionDeliveryOptionResultFailure | SubscriptionDeliveryOptionResultSuccess;

export type SubscriptionDiscount = SubscriptionAppliedCodeDiscount | SubscriptionManualDiscount;

export type SubscriptionDiscountValue = SubscriptionDiscountFixedAmountValue | SubscriptionDiscountPercentageValue;

export type SubscriptionShippingOptionResult = SubscriptionShippingOptionResultFailure | SubscriptionShippingOptionResultSuccess;

/** A product taxonomy attribute interface. */
export type TaxonomyCategoryAttribute = TaxonomyAttribute | TaxonomyChoiceListAttribute | TaxonomyMeasurementAttribute;

export type TenderTransactionDetails = TenderTransactionCreditCardDetails;

/** An endpoint to which webhook subscriptions send webhooks events. */
export type WebhookSubscriptionEndpoint = WebhookEventBridgeEndpoint | WebhookHttpEndpoint | WebhookPubSubEndpoint;

