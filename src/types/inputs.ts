// Auto-generated Shopify Admin GraphQL API 2026-04 - 601 input types
// Do not edit manually - regenerate with parse_types.ps1

import type { AppPricingInterval, CatalogStatus, CheckoutAndAccountsConfigurationBrandingBackground, CheckoutAndAccountsConfigurationBrandingBorder, CheckoutAndAccountsConfigurationBrandingBorderStyle, CheckoutAndAccountsConfigurationBrandingBorderWidth, CheckoutAndAccountsConfigurationBrandingCartLinkContentType, CheckoutAndAccountsConfigurationBrandingCornerRadius, CheckoutAndAccountsConfigurationBrandingFontLoadingStrategy, CheckoutAndAccountsConfigurationBrandingFooterAlignment, CheckoutAndAccountsConfigurationBrandingFooterPosition, CheckoutAndAccountsConfigurationBrandingHeaderAlignment, CheckoutAndAccountsConfigurationBrandingHeaderPosition, CheckoutAndAccountsConfigurationBrandingLabelPosition, CheckoutAndAccountsConfigurationBrandingMerchandiseThumbnailBadgeBackground, CheckoutAndAccountsConfigurationBrandingObjectFit, CheckoutAndAccountsConfigurationBrandingShadow, CheckoutAndAccountsConfigurationBrandingSharedCornerRadius, CheckoutAndAccountsConfigurationBrandingSimpleBorder, CheckoutAndAccountsConfigurationBrandingSpacing, CheckoutAndAccountsConfigurationBrandingSpacingKeyword, CheckoutAndAccountsConfigurationBrandingTypographyFont, CheckoutAndAccountsConfigurationBrandingTypographyKerning, CheckoutAndAccountsConfigurationBrandingTypographyLetterCase, CheckoutAndAccountsConfigurationBrandingTypographySize, CheckoutAndAccountsConfigurationBrandingTypographyWeight, CheckoutAndAccountsConfigurationBrandingVisibility, CheckoutBrandingBackground, CheckoutBrandingBackgroundStyle, CheckoutBrandingBorder, CheckoutBrandingBorderStyle, CheckoutBrandingBorderWidth, CheckoutBrandingCartLinkContentType, CheckoutBrandingColorSchemeSelection, CheckoutBrandingColorSelection, CheckoutBrandingCornerRadius, CheckoutBrandingFontLoadingStrategy, CheckoutBrandingFooterAlignment, CheckoutBrandingFooterPosition, CheckoutBrandingGlobalCornerRadius, CheckoutBrandingHeaderAlignment, CheckoutBrandingHeaderPosition, CheckoutBrandingLabelPosition, CheckoutBrandingMerchandiseThumbnailBadgeBackground, CheckoutBrandingObjectFit, CheckoutBrandingShadow, CheckoutBrandingSimpleBorder, CheckoutBrandingSpacing, CheckoutBrandingSpacingKeyword, CheckoutBrandingTypographyFont, CheckoutBrandingTypographyKerning, CheckoutBrandingTypographyLetterCase, CheckoutBrandingTypographySize, CheckoutBrandingTypographyWeight, CheckoutBrandingVisibility, CollectionRuleColumn, CollectionRuleRelation, CollectionSortOrder, CombinedListingsRole, CommentPolicy, CountryCode, CropRegion, CurrencyCode, CustomerEmailMarketingState, CustomerMarketingOptInLevel, CustomerSmsMarketingState, DeliveryConditionField, DeliveryConditionOperator, DeliveryLocalPickupTime, DiscountBuyerSelection, DiscountClass, DraftOrderAppliedDiscountType, FileContentType, FileCreateInputDuplicateResolutionMode, FulfillmentEventStatus, FulfillmentHoldReason, ImageContentType, InclusiveDutiesPricingStrategy, InclusiveTaxPricingStrategy, InventoryShipmentReceiveLineItemReason, LanguageCode, LengthUnit, LocalizationExtensionKey, LocalizedFieldKey, MarketConditionApplicationType, MarketingActivityExternalStatus, MarketingActivityHierarchyLevel, MarketingActivityStatus, MarketingBudgetBudgetType, MarketingChannel, MarketingTactic, MarketStatus, MediaContentType, MenuItemType, MetafieldAdminAccessInput, MetafieldCustomerAccountAccessInput, MetafieldOwnerType, MetafieldStorefrontAccessInput, MetaobjectAdminAccessInput, MetaobjectCustomerAccountAccess, MetaobjectStatus, MetaobjectStorefrontAccess, OnlineStoreThemeFileBodyInputType, OrderAdjustmentInputDiscrepancyReason, OrderCreateFinancialStatus, OrderCreateFulfillmentStatus, OrderCreateInputsInventoryBehavior, OrderTransactionKind, OrderTransactionStatus, PriceCalculationType, PriceListAdjustmentType, PriceListCompareAtMode, PrivacyCountryCode, ProductStatus, ProductVariantInventoryPolicy, PublicationCreateInputPublicationDefaultState, RefundDutyRefundType, RefundLineItemRestockType, ResourceFeedbackState, ReturnDeclineReason, ReturnReason, ReverseFulfillmentOrderDispositionType, RiskAssessmentResult, RiskFactSentiment, ScriptTagDisplayScope, SearchResultType, SellingPlanAnchorType, SellingPlanCategory, SellingPlanCheckoutChargeType, SellingPlanFixedDeliveryPolicyIntent, SellingPlanFixedDeliveryPolicyPreAnchorBehavior, SellingPlanFulfillmentTrigger, SellingPlanInterval, SellingPlanPricingPolicyAdjustmentType, SellingPlanRecurringDeliveryPolicyIntent, SellingPlanRecurringDeliveryPolicyPreAnchorBehavior, SellingPlanRemainingBalanceChargeTrigger, SellingPlanReserve, ShippingPackageType, ShopPolicyType, StagedUploadHttpMethodType, StagedUploadTargetGenerateUploadResource, SubscriptionBillingAttemptInventoryPolicy, SubscriptionBillingAttemptPaymentProcessingPolicy, SubscriptionBillingCycleBillingAttemptStatus, SubscriptionBillingCycleBillingCycleStatus, SubscriptionBillingCycleScheduleEditInputScheduleEditReason, SubscriptionContractSubscriptionStatus, TaxExemption, UnitPriceMeasurementMeasuredUnit, WebhookSubscriptionFormat, WeightUnit } from './enums';

/** The pricing model for the app subscription. The pricing model input can be either `appRecurringPricingDetails` or `appUsagePricingDetails`. */
export interface AppPlanInput {
  appRecurringPricingDetails?: AppRecurringPricingInput;
  appUsagePricingDetails?: AppUsagePricingInput;
}

/** Instructs the app subscription to generate a fixed charge on a recurring basis. The frequency is specified by the billing interval. */
export interface AppRecurringPricingInput {
  discount?: AppSubscriptionDiscountInput;
  interval?: AppPricingInterval;
  price: MoneyInput;
}

/** The input fields to specify a discount to the recurring pricing portion of a subscription over a number of billing intervals. */
export interface AppSubscriptionDiscountInput {
  durationLimitInIntervals?: number;
  value?: AppSubscriptionDiscountValueInput;
}

/** The input fields to specify the value discounted every billing interval. */
export interface AppSubscriptionDiscountValueInput {
  amount?: string;
  percentage?: number;
}

/** The input fields to add more than one pricing plan to an app subscription. */
export interface AppSubscriptionLineItemInput {
  plan: AppPlanInput;
}

/** The input fields to issue arbitrary charges for app usage associated with a subscription. */
export interface AppUsagePricingInput {
  cappedAmount: MoneyInput;
  terms: string;
}

/** The input fields of a blog when an article is created or updated. */
export interface ArticleBlogInput {
  title: string;
}

/** The input fields to create an article. */
export interface ArticleCreateInput {
  author: AuthorInput;
  blogId?: string;
  body?: string;
  handle?: string;
  image?: ArticleImageInput;
  isPublished?: boolean;
  metafields?: MetafieldInput[];
  publishDate?: string;
  summary?: string;
  tags?: string[];
  templateSuffix?: string;
  title: string;
}

/** The input fields for an image associated with an article. */
export interface ArticleImageInput {
  altText?: string;
  url?: string;
}

/** The input fields to update an article. */
export interface ArticleUpdateInput {
  author?: AuthorInput;
  blogId?: string;
  body?: string;
  handle?: string;
  image?: ArticleImageInput;
  isPublished?: boolean;
  metafields?: MetafieldInput[];
  publishDate?: string;
  redirectNewHandle?: boolean;
  summary?: string;
  tags?: string[];
  templateSuffix?: string;
  title?: string;
}

/** The input fields for an attribute. */
export interface AttributeInput {
  key: string;
  value: string;
}

/** The input fields for an author. Either the `name` or `user_id` fields can be supplied, but never both. */
export interface AuthorInput {
  name?: string;
  userId?: string;
}

/** The input fields for updating a backup region with exactly one required option. */
export interface BackupRegionUpdateInput {
  countryCode: CountryCode;
}

/** The input fields to create a blog. */
export interface BlogCreateInput {
  commentPolicy?: CommentPolicy;
  handle?: string;
  metafields?: MetafieldInput[];
  templateSuffix?: string;
  title: string;
}

/** The input fields to update a blog. */
export interface BlogUpdateInput {
  commentPolicy?: CommentPolicy;
  handle?: string;
  metafields?: MetafieldInput[];
  redirectArticles?: boolean;
  redirectNewHandle?: boolean;
  templateSuffix?: string;
  title?: string;
}

/** The input fields representing the components of a bundle line item. */
export interface BundlesDraftOrderBundleLineItemComponentInput {
  quantity: number;
  uuid?: string;
  variantId?: string;
}

/** The input fields specifying the behavior of checkout for a B2B buyer. */
export interface BuyerExperienceConfigurationInput {
  checkoutToDraft?: boolean;
  deposit?: DepositInput;
  editableShippingAddress?: boolean;
  paymentTermsTemplateId?: string;
}

/** The input fields for a buyer signal. */
export interface BuyerSignalInput {
  countryCode: CountryCode;
}

/** The input fields for exchange line items on a calculated return. */
export interface CalculateExchangeLineItemInput {
  appliedDiscount?: ExchangeLineItemAppliedDiscountInput;
  quantity: number;
  variantId?: string;
}

/** The input fields to calculate return amounts associated with an order. */
export interface CalculateReturnInput {
  exchangeLineItems?: CalculateExchangeLineItemInput[];
  orderId: string;
  returnLineItems?: CalculateReturnLineItemInput[];
  returnShippingFee?: ReturnShippingFeeInput;
}

/** The input fields for return line items on a calculated return. */
export interface CalculateReturnLineItemInput {
  fulfillmentLineItemId: string;
  quantity: number;
  restockingFee?: RestockingFeeInput;
}

/** The input fields for date and time range filter. */
export interface CashDrawerDateRangeInput {
  from: string;
  to: string;
}

/** The input fields for updating a cash drawer. */
export interface CashDrawerUpdateInput {
  name: string;
}

/** The input fields for the context in which the catalog's publishing and pricing rules apply. */
export interface CatalogContextInput {
  companyLocationIds?: string[];
  marketIds?: string[];
}

/** The input fields required to create a catalog. */
export interface CatalogCreateInput {
  context: CatalogContextInput;
  priceListId?: string;
  publicationId?: string;
  status: CatalogStatus;
  title: string;
}

/** The input fields used to update a catalog. */
export interface CatalogUpdateInput {
  context?: CatalogContextInput;
  priceListId?: string;
  publicationId?: string;
  status?: CatalogStatus;
  title?: string;
}

/** The input fields for creating a [`Channel`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel). */
export interface ChannelCreateInput {
  accountId: string;
  accountName: string;
  handle?: string;
  specificationHandle: string;
}

/** The input fields for updating a [`Channel`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel). */
export interface ChannelUpdateInput {
  accountId?: string;
  accountName?: string;
  handle?: string;
  specificationHandle?: string;
}

/** The input fields for customizing a base group of colors. */
export interface CheckoutAndAccountsConfigurationBrandingBaseColorRolesInput {
  accent?: string;
  background?: string;
  border?: string;
  decorative?: string;
  icon?: string;
  text?: string;
}

/** The input fields for customizing the buttons. */
export interface CheckoutAndAccountsConfigurationBrandingButtonInput {
  blockPadding?: CheckoutAndAccountsConfigurationBrandingSpacing;
  border?: CheckoutAndAccountsConfigurationBrandingSimpleBorder;
  cornerRadius?: CheckoutAndAccountsConfigurationBrandingCornerRadius;
  inlinePadding?: CheckoutAndAccountsConfigurationBrandingSpacing;
  typography?: CheckoutAndAccountsConfigurationBrandingTypographyStyleInput;
}

/** The input fields for updating breadcrumb customizations, which represent the buyer's journey to checkout. */
export interface CheckoutAndAccountsConfigurationBrandingBuyerJourneyInput {
  visibility?: CheckoutAndAccountsConfigurationBrandingVisibility;
}

/** The input fields for customizing the cart link at Checkout. */
export interface CheckoutAndAccountsConfigurationBrandingCartLinkInput {
  visibility?: CheckoutAndAccountsConfigurationBrandingVisibility;
}

/** The input fields for customizing the checkboxes. */
export interface CheckoutAndAccountsConfigurationBrandingCheckboxInput {
  cornerRadius?: CheckoutAndAccountsConfigurationBrandingCornerRadius;
}

/** The input fields for customizing the Checkout components. */
export interface CheckoutAndAccountsConfigurationBrandingCheckoutComponentsInput {
  buyerJourney?: CheckoutAndAccountsConfigurationBrandingBuyerJourneyInput;
  cartLink?: CheckoutAndAccountsConfigurationBrandingCartLinkInput;
  content?: CheckoutAndAccountsConfigurationBrandingContentInput;
  expressCheckout?: CheckoutAndAccountsConfigurationBrandingExpressCheckoutInput;
  footer?: CheckoutAndAccountsConfigurationBrandingCheckoutFooterInput;
  header?: CheckoutAndAccountsConfigurationBrandingCheckoutHeaderInput;
  main?: CheckoutAndAccountsConfigurationBrandingMainInput;
  orderSummary?: CheckoutAndAccountsConfigurationBrandingOrderSummaryInput;
}

/** The input fields for customizing the checkout footer. */
export interface CheckoutAndAccountsConfigurationBrandingCheckoutFooterInput {
  alignment?: CheckoutAndAccountsConfigurationBrandingFooterAlignment;
  background?: CheckoutAndAccountsConfigurationBrandingBackground;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  content?: CheckoutAndAccountsConfigurationBrandingFooterContentInput;
  divided?: boolean;
  padding?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
  position?: CheckoutAndAccountsConfigurationBrandingFooterPosition;
}

/** The input fields for customizing the checkout header. */
export interface CheckoutAndAccountsConfigurationBrandingCheckoutHeaderInput {
  alignment?: CheckoutAndAccountsConfigurationBrandingHeaderAlignment;
  background?: CheckoutAndAccountsConfigurationBrandingBackground;
  cartLink?: CheckoutAndAccountsConfigurationBrandingHeaderCartLinkInput;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  divided?: boolean;
  logo?: CheckoutAndAccountsConfigurationBrandingLogoInput;
  padding?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
  position?: CheckoutAndAccountsConfigurationBrandingHeaderPosition;
}

/** The input fields for customizing the Checkout surface. */
export interface CheckoutAndAccountsConfigurationBrandingCheckoutSurfaceInput {
  components?: CheckoutAndAccountsConfigurationBrandingCheckoutComponentsInput;
}

/** The input fields for customizing the 'group' variant of ChoiceList. */
export interface CheckoutAndAccountsConfigurationBrandingChoiceListGroupInput {
  spacing?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
}

/** The input fields for customizing the choice list. */
export interface CheckoutAndAccountsConfigurationBrandingChoiceListInput {
  group?: CheckoutAndAccountsConfigurationBrandingChoiceListGroupInput;
}

/** The input fields for customizing a group of colors used together on a surface. */
export interface CheckoutAndAccountsConfigurationBrandingColorRolesInput {
  accent?: string;
  background?: string;
  border?: string;
  decorative?: string;
  icon?: string;
  text?: string;
}

/** The input fields for customizing a base set of colors, from which every component pulls its colors. */
export interface CheckoutAndAccountsConfigurationBrandingColorsInput {
  base?: CheckoutAndAccountsConfigurationBrandingBaseColorRolesInput;
  control?: CheckoutAndAccountsConfigurationBrandingControlColorRolesInput;
  primaryButton?: CheckoutAndAccountsConfigurationBrandingPrimaryButtonColorRolesInput;
  secondaryButton?: CheckoutAndAccountsConfigurationBrandingSecondaryButtonColorRolesInput;
}

/** The input fields for customizing the components. */
export interface CheckoutAndAccountsConfigurationBrandingComponentsInput {
  checkbox?: CheckoutAndAccountsConfigurationBrandingCheckboxInput;
  choiceList?: CheckoutAndAccountsConfigurationBrandingChoiceListInput;
  control?: CheckoutAndAccountsConfigurationBrandingControlInput;
  divider?: CheckoutAndAccountsConfigurationBrandingDividerStyleInput;
  favicon?: CheckoutAndAccountsConfigurationBrandingImageInput;
  footer?: CheckoutAndAccountsConfigurationBrandingFooterInput;
  header?: CheckoutAndAccountsConfigurationBrandingHeaderInput;
  headingLevel1?: CheckoutAndAccountsConfigurationBrandingHeadingLevelInput;
  headingLevel2?: CheckoutAndAccountsConfigurationBrandingHeadingLevelInput;
  headingLevel3?: CheckoutAndAccountsConfigurationBrandingHeadingLevelInput;
  main?: CheckoutAndAccountsConfigurationBrandingMainInput;
  merchandiseThumbnail?: CheckoutAndAccountsConfigurationBrandingMerchandiseThumbnailInput;
  primaryButton?: CheckoutAndAccountsConfigurationBrandingButtonInput;
  secondaryButton?: CheckoutAndAccountsConfigurationBrandingButtonInput;
  select?: CheckoutAndAccountsConfigurationBrandingSelectInput;
  shared?: CheckoutAndAccountsConfigurationBrandingSharedInput;
  textField?: CheckoutAndAccountsConfigurationBrandingTextFieldInput;
}

/** The input fields for customizing a container's divider. */
export interface CheckoutAndAccountsConfigurationBrandingContainerDividerInput {
  borderStyle?: CheckoutAndAccountsConfigurationBrandingBorderStyle;
  borderWidth?: CheckoutAndAccountsConfigurationBrandingBorderWidth;
  visibility?: CheckoutAndAccountsConfigurationBrandingVisibility;
}

/** The input fields for customizing the content container. */
export interface CheckoutAndAccountsConfigurationBrandingContentInput {
  divider?: CheckoutAndAccountsConfigurationBrandingContainerDividerInput;
}

/** The input fields for customizing colors for form controls. */
export interface CheckoutAndAccountsConfigurationBrandingControlColorRolesInput {
  accent?: string;
  background?: string;
  border?: string;
  decorative?: string;
  icon?: string;
  selected?: CheckoutAndAccountsConfigurationBrandingColorRolesInput;
  text?: string;
}

/** The input fields for customizing the form controls. */
export interface CheckoutAndAccountsConfigurationBrandingControlInput {
  border?: CheckoutAndAccountsConfigurationBrandingSimpleBorder;
  cornerRadius?: CheckoutAndAccountsConfigurationBrandingCornerRadius;
  labelPosition?: CheckoutAndAccountsConfigurationBrandingLabelPosition;
}

/** The input fields for customizing the corner radius variables. */
export interface CheckoutAndAccountsConfigurationBrandingCornerRadiusVariablesInput {
  base?: number;
  large?: number;
  small?: number;
}

/** The input fields for customizing the Customer Accounts components. */
export interface CheckoutAndAccountsConfigurationBrandingCustomerAccountsComponentsInput {
  footer?: CheckoutAndAccountsConfigurationBrandingCustomerAccountsFooterInput;
  header?: CheckoutAndAccountsConfigurationBrandingCustomerAccountsHeaderInput;
  main?: CheckoutAndAccountsConfigurationBrandingCustomerAccountsMainInput;
}

/** The input fields for customizing the customer accounts footer. */
export interface CheckoutAndAccountsConfigurationBrandingCustomerAccountsFooterInput {
  alignment?: CheckoutAndAccountsConfigurationBrandingFooterAlignment;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  padding?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
}

/** The input fields for customizing the customer accounts header. */
export interface CheckoutAndAccountsConfigurationBrandingCustomerAccountsHeaderInput {
  alignment?: CheckoutAndAccountsConfigurationBrandingHeaderAlignment;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  logo?: CheckoutAndAccountsConfigurationBrandingCustomerAccountsLogoInput;
  padding?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
}

/** The input fields for customizing the logo. */
export interface CheckoutAndAccountsConfigurationBrandingCustomerAccountsLogoInput {
  image?: CheckoutAndAccountsConfigurationBrandingImageInput;
  maxWidth?: number;
}

/** The input fields for customizing the main container. */
export interface CheckoutAndAccountsConfigurationBrandingCustomerAccountsMainInput {
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  section?: CheckoutAndAccountsConfigurationBrandingCustomerAccountsMainSectionInput;
}

/** The input fields for customizing the customer accounts branding section. */
export interface CheckoutAndAccountsConfigurationBrandingCustomerAccountsMainSectionInput {
  background?: CheckoutAndAccountsConfigurationBrandingBackground;
  border?: CheckoutAndAccountsConfigurationBrandingSimpleBorder;
  borderStyle?: CheckoutAndAccountsConfigurationBrandingBorderStyle;
  borderWidth?: CheckoutAndAccountsConfigurationBrandingBorderWidth;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  cornerRadius?: CheckoutAndAccountsConfigurationBrandingCornerRadius;
  padding?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
  shadow?: CheckoutAndAccountsConfigurationBrandingShadow;
}

/** The input fields for customizing the Customer Accounts surface. */
export interface CheckoutAndAccountsConfigurationBrandingCustomerAccountsSurfaceInput {
  components?: CheckoutAndAccountsConfigurationBrandingCustomerAccountsComponentsInput;
}

/** The input fields for customizing a custom font group. */
export interface CheckoutAndAccountsConfigurationBrandingCustomFontGroupInput {
  base: CheckoutAndAccountsConfigurationBrandingCustomFontInput;
  bold: CheckoutAndAccountsConfigurationBrandingCustomFontInput;
  loadingStrategy?: CheckoutAndAccountsConfigurationBrandingFontLoadingStrategy;
}

/** The input fields for customizing a custom font. */
export interface CheckoutAndAccountsConfigurationBrandingCustomFontInput {
  genericFileId: string;
  weight: number;
}

/** The input fields for customizing the colors. */
export interface CheckoutAndAccountsConfigurationBrandingDesignTokensColorsInput {
  palette?: CheckoutAndAccountsConfigurationBrandingPaletteInput;
}

/** The input fields for customizing the design tokens. */
export interface CheckoutAndAccountsConfigurationBrandingDesignTokensInput {
  colors?: CheckoutAndAccountsConfigurationBrandingDesignTokensColorsInput;
  cornerRadius?: CheckoutAndAccountsConfigurationBrandingCornerRadiusVariablesInput;
  typography?: CheckoutAndAccountsConfigurationBrandingTypographyInput;
}

/** The input fields for customizing the global divider. */
export interface CheckoutAndAccountsConfigurationBrandingDividerStyleInput {
  borderStyle?: CheckoutAndAccountsConfigurationBrandingBorderStyle;
  borderWidth?: CheckoutAndAccountsConfigurationBrandingBorderWidth;
}

/** The input fields for customizing the express checkout button. */
export interface CheckoutAndAccountsConfigurationBrandingExpressCheckoutButtonInput {
  cornerRadius?: CheckoutAndAccountsConfigurationBrandingCornerRadius;
}

/** The input fields for customizing the Express Checkout. */
export interface CheckoutAndAccountsConfigurationBrandingExpressCheckoutInput {
  button?: CheckoutAndAccountsConfigurationBrandingExpressCheckoutButtonInput;
}

/** The input fields used to update a font group. */
export interface CheckoutAndAccountsConfigurationBrandingFontGroupInput {
  customFontGroup?: CheckoutAndAccountsConfigurationBrandingCustomFontGroupInput;
  shopifyFontGroup?: CheckoutAndAccountsConfigurationBrandingShopifyFontGroupInput;
}

/** The input fields for customizing the font size. */
export interface CheckoutAndAccountsConfigurationBrandingFontSizeInput {
  base?: number;
  ratio?: number;
}

/** The input fields for customizing the footer content. */
export interface CheckoutAndAccountsConfigurationBrandingFooterContentInput {
  visibility?: CheckoutAndAccountsConfigurationBrandingVisibility;
}

/** The input fields for customizing the checkout footer. */
export interface CheckoutAndAccountsConfigurationBrandingFooterInput {
  alignment?: CheckoutAndAccountsConfigurationBrandingFooterAlignment;
  background?: CheckoutAndAccountsConfigurationBrandingBackground;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  content?: CheckoutAndAccountsConfigurationBrandingFooterContentInput;
  divided?: boolean;
  padding?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
}

/** The input fields for customizing the cart link for 1-page checkout. This field allows to customize the cart icon that renders by default on 1-page checkout. */
export interface CheckoutAndAccountsConfigurationBrandingHeaderCartLinkInput {
  contentType?: CheckoutAndAccountsConfigurationBrandingCartLinkContentType;
  image?: CheckoutAndAccountsConfigurationBrandingImageInput;
}

/** The input fields for customizing the header. */
export interface CheckoutAndAccountsConfigurationBrandingHeaderInput {
  alignment?: CheckoutAndAccountsConfigurationBrandingHeaderAlignment;
  background?: CheckoutAndAccountsConfigurationBrandingBackground;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  divided?: boolean;
  logo?: CheckoutAndAccountsConfigurationBrandingLogoInput;
  padding?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
}

/** The input fields for customizing the heading level. */
export interface CheckoutAndAccountsConfigurationBrandingHeadingLevelInput {
  typography?: CheckoutAndAccountsConfigurationBrandingTypographyStyleInput;
}

/** The input fields for customizing the image. */
export interface CheckoutAndAccountsConfigurationBrandingImageInput {
  mediaImageId?: string;
}

/** The input fields for customizing Checkout and Customer Accounts branding. */
export interface CheckoutAndAccountsConfigurationBrandingInput {
  components?: CheckoutAndAccountsConfigurationBrandingComponentsInput;
  designTokens?: CheckoutAndAccountsConfigurationBrandingDesignTokensInput;
  surfaces?: CheckoutAndAccountsConfigurationBrandingSurfacesInput;
}

/** The input fields for customizing the logo. */
export interface CheckoutAndAccountsConfigurationBrandingLogoInput {
  image?: CheckoutAndAccountsConfigurationBrandingImageInput;
  maxWidth?: number;
  visibility?: CheckoutAndAccountsConfigurationBrandingVisibility;
}

/** The input fields for customizing the main container. */
export interface CheckoutAndAccountsConfigurationBrandingMainInput {
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  divider?: CheckoutAndAccountsConfigurationBrandingContainerDividerInput;
  section?: CheckoutAndAccountsConfigurationBrandingMainSectionInput;
}

/** The input fields for customizing the main sections. */
export interface CheckoutAndAccountsConfigurationBrandingMainSectionInput {
  background?: CheckoutAndAccountsConfigurationBrandingBackground;
  border?: CheckoutAndAccountsConfigurationBrandingSimpleBorder;
  borderStyle?: CheckoutAndAccountsConfigurationBrandingBorderStyle;
  borderWidth?: CheckoutAndAccountsConfigurationBrandingBorderWidth;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  cornerRadius?: CheckoutAndAccountsConfigurationBrandingCornerRadius;
  padding?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
  shadow?: CheckoutAndAccountsConfigurationBrandingShadow;
}

/** The input fields for customizing the merchandise thumbnail badges. */
export interface CheckoutAndAccountsConfigurationBrandingMerchandiseThumbnailBadgeInput {
  background?: CheckoutAndAccountsConfigurationBrandingMerchandiseThumbnailBadgeBackground;
}

/** The input fields for customizing the merchandise thumbnails. */
export interface CheckoutAndAccountsConfigurationBrandingMerchandiseThumbnailInput {
  aspectRatio?: number;
  badge?: CheckoutAndAccountsConfigurationBrandingMerchandiseThumbnailBadgeInput;
  border?: CheckoutAndAccountsConfigurationBrandingSimpleBorder;
  cornerRadius?: CheckoutAndAccountsConfigurationBrandingCornerRadius;
  fit?: CheckoutAndAccountsConfigurationBrandingObjectFit;
}

/** The input fields for customizing the order summary container. */
export interface CheckoutAndAccountsConfigurationBrandingOrderSummaryInput {
  backgroundImage?: CheckoutAndAccountsConfigurationBrandingImageInput;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  divider?: CheckoutAndAccountsConfigurationBrandingContainerDividerInput;
  section?: CheckoutAndAccountsConfigurationBrandingOrderSummarySectionInput;
}

/** The input fields for customizing the order summary sections. */
export interface CheckoutAndAccountsConfigurationBrandingOrderSummarySectionInput {
  background?: CheckoutAndAccountsConfigurationBrandingBackground;
  border?: CheckoutAndAccountsConfigurationBrandingSimpleBorder;
  borderStyle?: CheckoutAndAccountsConfigurationBrandingBorderStyle;
  borderWidth?: CheckoutAndAccountsConfigurationBrandingBorderWidth;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  cornerRadius?: CheckoutAndAccountsConfigurationBrandingCornerRadius;
  padding?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
  shadow?: CheckoutAndAccountsConfigurationBrandingShadow;
}

/** The input fields to update the color palette. */
export interface CheckoutAndAccountsConfigurationBrandingPaletteInput {
  color1?: string;
  color10?: string;
  color11?: string;
  color12?: string;
  color13?: string;
  color14?: string;
  color15?: string;
  color16?: string;
  color17?: string;
  color18?: string;
  color19?: string;
  color2?: string;
  color20?: string;
  color3?: string;
  color4?: string;
  color5?: string;
  color6?: string;
  color7?: string;
  color8?: string;
  color9?: string;
}

/** The input fields for customizing colors for primary buttons. */
export interface CheckoutAndAccountsConfigurationBrandingPrimaryButtonColorRolesInput {
  accent?: string;
  background?: string;
  border?: string;
  decorative?: string;
  hover?: CheckoutAndAccountsConfigurationBrandingColorRolesInput;
  icon?: string;
  text?: string;
}

/** The input fields for customizing colors for secondary buttons. */
export interface CheckoutAndAccountsConfigurationBrandingSecondaryButtonColorRolesInput {
  accent?: string;
  background?: string;
  border?: string;
  decorative?: string;
  hover?: CheckoutAndAccountsConfigurationBrandingColorRolesInput;
  icon?: string;
  text?: string;
}

/** The input fields for customizing the selects. */
export interface CheckoutAndAccountsConfigurationBrandingSelectInput {
  border?: CheckoutAndAccountsConfigurationBrandingBorder;
  typography?: CheckoutAndAccountsConfigurationBrandingTypographyStyleInput;
}

/** The input fields for customizing shared colors. */
export interface CheckoutAndAccountsConfigurationBrandingSharedColorsInput {
  accent?: string;
  button?: string;
  control?: string;
  critical?: string;
  decorative?: string;
  info?: string;
  success?: string;
  warning?: string;
}

/** The input fields for customizing the shared settings. */
export interface CheckoutAndAccountsConfigurationBrandingSharedInput {
  colors?: CheckoutAndAccountsConfigurationBrandingSharedColorsInput;
  cornerRadius?: CheckoutAndAccountsConfigurationBrandingSharedCornerRadius;
  typography?: CheckoutAndAccountsConfigurationBrandingSharedTypographyStyleInput;
}

/** The input fields for customizing the shared typography. */
export interface CheckoutAndAccountsConfigurationBrandingSharedTypographyStyleInput {
  kerning?: CheckoutAndAccountsConfigurationBrandingTypographyKerning;
  letterCase?: CheckoutAndAccountsConfigurationBrandingTypographyLetterCase;
}

/** The input fields for customizing a Shopify font group. */
export interface CheckoutAndAccountsConfigurationBrandingShopifyFontGroupInput {
  baseFontHandle: string;
  boldFontHandle: string;
  loadingStrategy?: CheckoutAndAccountsConfigurationBrandingFontLoadingStrategy;
}

/** The input fields for customizing the sign-in components. */
export interface CheckoutAndAccountsConfigurationBrandingSignInComponentsInput {
  header?: CheckoutAndAccountsConfigurationBrandingSignInHeaderInput;
  main?: CheckoutAndAccountsConfigurationBrandingSignInMainInput;
}

/** The input fields for customizing the sign-in header. */
export interface CheckoutAndAccountsConfigurationBrandingSignInHeaderInput {
  logo?: CheckoutAndAccountsConfigurationBrandingSignInLogoInput;
  padding?: CheckoutAndAccountsConfigurationBrandingSpacingKeyword;
}

/** The input fields for customizing the sign-in logo. */
export interface CheckoutAndAccountsConfigurationBrandingSignInLogoInput {
  image?: CheckoutAndAccountsConfigurationBrandingImageInput;
  maxWidth?: number;
}

/** The input fields for customizing the sign-in main container. */
export interface CheckoutAndAccountsConfigurationBrandingSignInMainInput {
  backgroundImage?: CheckoutAndAccountsConfigurationBrandingImageInput;
  colors?: CheckoutAndAccountsConfigurationBrandingColorsInput;
  section?: CheckoutAndAccountsConfigurationBrandingMainSectionInput;
}

/** The input fields for customizing the sign-in surface. */
export interface CheckoutAndAccountsConfigurationBrandingSignInSurfaceInput {
  components?: CheckoutAndAccountsConfigurationBrandingSignInComponentsInput;
}

/** The input fields for customizing surfaces branding. */
export interface CheckoutAndAccountsConfigurationBrandingSurfacesInput {
  checkout?: CheckoutAndAccountsConfigurationBrandingCheckoutSurfaceInput;
  customerAccounts?: CheckoutAndAccountsConfigurationBrandingCustomerAccountsSurfaceInput;
  signIn?: CheckoutAndAccountsConfigurationBrandingSignInSurfaceInput;
}

/** The input fields for customizing the text fields. */
export interface CheckoutAndAccountsConfigurationBrandingTextFieldInput {
  border?: CheckoutAndAccountsConfigurationBrandingBorder;
  typography?: CheckoutAndAccountsConfigurationBrandingTypographyStyleInput;
}

/** The input fields for customizing the typography. */
export interface CheckoutAndAccountsConfigurationBrandingTypographyInput {
  primary?: CheckoutAndAccountsConfigurationBrandingFontGroupInput;
  secondary?: CheckoutAndAccountsConfigurationBrandingFontGroupInput;
  size?: CheckoutAndAccountsConfigurationBrandingFontSizeInput;
}

/** The input fields for customizing the typography. */
export interface CheckoutAndAccountsConfigurationBrandingTypographyStyleInput {
  font?: CheckoutAndAccountsConfigurationBrandingTypographyFont;
  kerning?: CheckoutAndAccountsConfigurationBrandingTypographyKerning;
  letterCase?: CheckoutAndAccountsConfigurationBrandingTypographyLetterCase;
  size?: CheckoutAndAccountsConfigurationBrandingTypographySize;
  weight?: CheckoutAndAccountsConfigurationBrandingTypographyWeight;
}

/** The input fields for checkout and account configurations. */
export interface CheckoutAndAccountsConfigurationInput {
  branding?: CheckoutAndAccountsConfigurationBrandingInput;
  overrides?: CheckoutAndAccountsConfigurationOverrideInput[];
}

/** The input fields for checkout and account configuration overrides. */
export interface CheckoutAndAccountsConfigurationOverrideInput {
  branding?: CheckoutAndAccountsConfigurationBrandingInput;
  id?: string;
}

/** The input fields to set colors for buttons. */
export interface CheckoutBrandingButtonColorRolesInput {
  accent?: string;
  background?: string;
  border?: string;
  decorative?: string;
  hover?: CheckoutBrandingColorRolesInput;
  icon?: string;
  text?: string;
}

/** The input fields used to update the buttons customizations. */
export interface CheckoutBrandingButtonInput {
  background?: CheckoutBrandingBackgroundStyle;
  blockPadding?: CheckoutBrandingSpacing;
  border?: CheckoutBrandingSimpleBorder;
  cornerRadius?: CheckoutBrandingCornerRadius;
  inlinePadding?: CheckoutBrandingSpacing;
  typography?: CheckoutBrandingTypographyStyleInput;
}

/** The input fields for updating breadcrumb customizations, which represent the buyer's journey to checkout. */
export interface CheckoutBrandingBuyerJourneyInput {
  visibility?: CheckoutBrandingVisibility;
}

/** The input fields for updating the cart link customizations at checkout. */
export interface CheckoutBrandingCartLinkInput {
  visibility?: CheckoutBrandingVisibility;
}

/** The input fields used to update the checkboxes customizations. */
export interface CheckoutBrandingCheckboxInput {
  cornerRadius?: CheckoutBrandingCornerRadius;
}

/** The input fields to update the settings that apply to the 'group' variant of ChoiceList. */
export interface CheckoutBrandingChoiceListGroupInput {
  spacing?: CheckoutBrandingSpacingKeyword;
}

/** The input fields to use to update the choice list customizations. */
export interface CheckoutBrandingChoiceListInput {
  group?: CheckoutBrandingChoiceListGroupInput;
}

/** The input fields to customize the overall look and feel of the checkout. */
export interface CheckoutBrandingColorGlobalInput {
  accent?: string;
  brand?: string;
  critical?: string;
  decorative?: string;
  info?: string;
  success?: string;
  warning?: string;
}

/** The input fields for a group of colors used together on a surface. */
export interface CheckoutBrandingColorRolesInput {
  accent?: string;
  background?: string;
  border?: string;
  decorative?: string;
  icon?: string;
  text?: string;
}

/** The input fields for a base set of color customizations that's applied to an area of Checkout, from which every component pulls its colors. */
export interface CheckoutBrandingColorSchemeInput {
  base?: CheckoutBrandingColorRolesInput;
  control?: CheckoutBrandingControlColorRolesInput;
  primaryButton?: CheckoutBrandingButtonColorRolesInput;
  secondaryButton?: CheckoutBrandingButtonColorRolesInput;
}

/** The input fields for the color schemes. */
export interface CheckoutBrandingColorSchemesInput {
  scheme1?: CheckoutBrandingColorSchemeInput;
  scheme2?: CheckoutBrandingColorSchemeInput;
  scheme3?: CheckoutBrandingColorSchemeInput;
  scheme4?: CheckoutBrandingColorSchemeInput;
  scheme5?: CheckoutBrandingColorSchemeInput;
  scheme6?: CheckoutBrandingColorSchemeInput;
}

/** The input fields used to update the color settings for global colors and color schemes. */
export interface CheckoutBrandingColorsInput {
  global?: CheckoutBrandingColorGlobalInput;
  schemes?: CheckoutBrandingColorSchemesInput;
}

/** The input fields used to update a container's divider customizations. */
export interface CheckoutBrandingContainerDividerInput {
  borderStyle?: CheckoutBrandingBorderStyle;
  borderWidth?: CheckoutBrandingBorderWidth;
  visibility?: CheckoutBrandingVisibility;
}

/** The input fields used to update the content container customizations. */
export interface CheckoutBrandingContentInput {
  divider?: CheckoutBrandingContainerDividerInput;
}

/** The input fields to define colors for form controls. */
export interface CheckoutBrandingControlColorRolesInput {
  accent?: string;
  background?: string;
  border?: string;
  decorative?: string;
  icon?: string;
  selected?: CheckoutBrandingColorRolesInput;
  text?: string;
}

/** The input fields used to update the form controls customizations. */
export interface CheckoutBrandingControlInput {
  border?: CheckoutBrandingSimpleBorder;
  color?: CheckoutBrandingColorSelection;
  cornerRadius?: CheckoutBrandingCornerRadius;
  labelPosition?: CheckoutBrandingLabelPosition;
}

/** The input fields used to update the corner radius variables. */
export interface CheckoutBrandingCornerRadiusVariablesInput {
  base?: number;
  large?: number;
  small?: number;
}

/** The input fields required to update a custom font group. */
export interface CheckoutBrandingCustomFontGroupInput {
  base: CheckoutBrandingCustomFontInput;
  bold: CheckoutBrandingCustomFontInput;
  loadingStrategy?: CheckoutBrandingFontLoadingStrategy;
}

/** The input fields required to update a font. */
export interface CheckoutBrandingCustomFontInput {
  genericFileId: string;
  weight: number;
}

/** The input fields used to update the components customizations. */
export interface CheckoutBrandingCustomizationsInput {
  buyerJourney?: CheckoutBrandingBuyerJourneyInput;
  cartLink?: CheckoutBrandingCartLinkInput;
  checkbox?: CheckoutBrandingCheckboxInput;
  choiceList?: CheckoutBrandingChoiceListInput;
  content?: CheckoutBrandingContentInput;
  control?: CheckoutBrandingControlInput;
  divider?: CheckoutBrandingDividerStyleInput;
  expressCheckout?: CheckoutBrandingExpressCheckoutInput;
  favicon?: CheckoutBrandingImageInput;
  footer?: CheckoutBrandingFooterInput;
  global?: CheckoutBrandingGlobalInput;
  header?: CheckoutBrandingHeaderInput;
  headingLevel1?: CheckoutBrandingHeadingLevelInput;
  headingLevel2?: CheckoutBrandingHeadingLevelInput;
  headingLevel3?: CheckoutBrandingHeadingLevelInput;
  main?: CheckoutBrandingMainInput;
  merchandiseThumbnail?: CheckoutBrandingMerchandiseThumbnailInput;
  orderSummary?: CheckoutBrandingOrderSummaryInput;
  primaryButton?: CheckoutBrandingButtonInput;
  secondaryButton?: CheckoutBrandingButtonInput;
  select?: CheckoutBrandingSelectInput;
  textField?: CheckoutBrandingTextFieldInput;
}

/** The input fields used to update the design system. */
export interface CheckoutBrandingDesignSystemInput {
  colors?: CheckoutBrandingColorsInput;
  cornerRadius?: CheckoutBrandingCornerRadiusVariablesInput;
  typography?: CheckoutBrandingTypographyInput;
}

/** The input fields used to update the page, content, main and order summary dividers customizations. */
export interface CheckoutBrandingDividerStyleInput {
  borderStyle?: CheckoutBrandingBorderStyle;
  borderWidth?: CheckoutBrandingBorderWidth;
}

/** The input fields to use to update the express checkout customizations. */
export interface CheckoutBrandingExpressCheckoutButtonInput {
  cornerRadius?: CheckoutBrandingCornerRadius;
}

/** The input fields to use to update the Express Checkout customizations. */
export interface CheckoutBrandingExpressCheckoutInput {
  button?: CheckoutBrandingExpressCheckoutButtonInput;
}

/** The input fields used to update a font group. To learn more about updating fonts, refer to the [checkoutBrandingUpsert](https://shopify.dev/api/admin-graphql/unstable/mutations/checkoutBrandingUpsert) mutation and the checkout branding [tutorial](https://shopify.dev/docs/apps/... */
export interface CheckoutBrandingFontGroupInput {
  customFontGroup?: CheckoutBrandingCustomFontGroupInput;
  shopifyFontGroup?: CheckoutBrandingShopifyFontGroupInput;
}

/** The input fields used to update the font size. */
export interface CheckoutBrandingFontSizeInput {
  base?: number;
  ratio?: number;
}

/** The input fields for footer content customizations. */
export interface CheckoutBrandingFooterContentInput {
  visibility?: CheckoutBrandingVisibility;
}

/** The input fields when mutating the checkout footer settings. */
export interface CheckoutBrandingFooterInput {
  alignment?: CheckoutBrandingFooterAlignment;
  colorScheme?: CheckoutBrandingColorSchemeSelection;
  content?: CheckoutBrandingFooterContentInput;
  divided?: boolean;
  padding?: CheckoutBrandingSpacingKeyword;
  position?: CheckoutBrandingFooterPosition;
}

/** The input fields used to update the global customizations. */
export interface CheckoutBrandingGlobalInput {
  cornerRadius?: CheckoutBrandingGlobalCornerRadius;
  typography?: CheckoutBrandingTypographyStyleGlobalInput;
}

/** The input fields for header cart link customizations. */
export interface CheckoutBrandingHeaderCartLinkInput {
  contentType?: CheckoutBrandingCartLinkContentType;
  image?: CheckoutBrandingImageInput;
}

/** The input fields used to update the header customizations. */
export interface CheckoutBrandingHeaderInput {
  alignment?: CheckoutBrandingHeaderAlignment;
  banner?: CheckoutBrandingImageInput;
  cartLink?: CheckoutBrandingHeaderCartLinkInput;
  colorScheme?: CheckoutBrandingColorSchemeSelection;
  divided?: boolean;
  logo?: CheckoutBrandingLogoInput;
  padding?: CheckoutBrandingSpacingKeyword;
  position?: CheckoutBrandingHeaderPosition;
}

/** The input fields for heading level customizations. */
export interface CheckoutBrandingHeadingLevelInput {
  typography?: CheckoutBrandingTypographyStyleInput;
}

/** The input fields used to update a checkout branding image uploaded via the Files API. */
export interface CheckoutBrandingImageInput {
  mediaImageId?: string;
}

/** The input fields used to upsert the checkout branding settings. */
export interface CheckoutBrandingInput {
  customizations?: CheckoutBrandingCustomizationsInput;
  designSystem?: CheckoutBrandingDesignSystemInput;
}

/** The input fields used to update the logo customizations. */
export interface CheckoutBrandingLogoInput {
  image?: CheckoutBrandingImageInput;
  maxWidth?: number;
  visibility?: CheckoutBrandingVisibility;
}

/** The input fields used to update the main container customizations. */
export interface CheckoutBrandingMainInput {
  backgroundImage?: CheckoutBrandingImageInput;
  colorScheme?: CheckoutBrandingColorSchemeSelection;
  divider?: CheckoutBrandingContainerDividerInput;
  section?: CheckoutBrandingMainSectionInput;
}

/** The input fields used to update the main sections customizations. */
export interface CheckoutBrandingMainSectionInput {
  background?: CheckoutBrandingBackground;
  border?: CheckoutBrandingSimpleBorder;
  borderStyle?: CheckoutBrandingBorderStyle;
  borderWidth?: CheckoutBrandingBorderWidth;
  colorScheme?: CheckoutBrandingColorSchemeSelection;
  cornerRadius?: CheckoutBrandingCornerRadius;
  padding?: CheckoutBrandingSpacingKeyword;
  shadow?: CheckoutBrandingShadow;
}

/** The input fields used to update the merchandise thumbnail badges customizations. */
export interface CheckoutBrandingMerchandiseThumbnailBadgeInput {
  background?: CheckoutBrandingMerchandiseThumbnailBadgeBackground;
}

/** The input fields used to update the merchandise thumbnails customizations. */
export interface CheckoutBrandingMerchandiseThumbnailInput {
  badge?: CheckoutBrandingMerchandiseThumbnailBadgeInput;
  border?: CheckoutBrandingSimpleBorder;
  cornerRadius?: CheckoutBrandingCornerRadius;
  fit?: CheckoutBrandingObjectFit;
}

/** The input fields used to update the order summary container customizations. */
export interface CheckoutBrandingOrderSummaryInput {
  backgroundImage?: CheckoutBrandingImageInput;
  colorScheme?: CheckoutBrandingColorSchemeSelection;
  divider?: CheckoutBrandingContainerDividerInput;
  section?: CheckoutBrandingOrderSummarySectionInput;
}

/** The input fields used to update the order summary sections customizations. */
export interface CheckoutBrandingOrderSummarySectionInput {
  background?: CheckoutBrandingBackground;
  border?: CheckoutBrandingSimpleBorder;
  borderStyle?: CheckoutBrandingBorderStyle;
  borderWidth?: CheckoutBrandingBorderWidth;
  colorScheme?: CheckoutBrandingColorSchemeSelection;
  cornerRadius?: CheckoutBrandingCornerRadius;
  padding?: CheckoutBrandingSpacingKeyword;
  shadow?: CheckoutBrandingShadow;
}

/** The input fields used to update the selects customizations. */
export interface CheckoutBrandingSelectInput {
  border?: CheckoutBrandingBorder;
  typography?: CheckoutBrandingTypographyStyleInput;
}

/** The input fields used to update a Shopify font group. */
export interface CheckoutBrandingShopifyFontGroupInput {
  baseWeight?: number;
  boldWeight?: number;
  loadingStrategy?: CheckoutBrandingFontLoadingStrategy;
  name: string;
}

/** The input fields used to update the text fields customizations. */
export interface CheckoutBrandingTextFieldInput {
  border?: CheckoutBrandingBorder;
  typography?: CheckoutBrandingTypographyStyleInput;
}

/** The input fields used to update the typography. Refer to the [typography tutorial](https://shopify.dev/docs/apps/checkout/styling/customize-typography) for more information on how to set these fields. */
export interface CheckoutBrandingTypographyInput {
  primary?: CheckoutBrandingFontGroupInput;
  secondary?: CheckoutBrandingFontGroupInput;
  size?: CheckoutBrandingFontSizeInput;
}

/** The input fields used to update the global typography customizations. */
export interface CheckoutBrandingTypographyStyleGlobalInput {
  kerning?: CheckoutBrandingTypographyKerning;
  letterCase?: CheckoutBrandingTypographyLetterCase;
}

/** The input fields used to update the typography customizations. */
export interface CheckoutBrandingTypographyStyleInput {
  font?: CheckoutBrandingTypographyFont;
  kerning?: CheckoutBrandingTypographyKerning;
  letterCase?: CheckoutBrandingTypographyLetterCase;
  size?: CheckoutBrandingTypographySize;
  weight?: CheckoutBrandingTypographyWeight;
}

/** The input fields for adding products to the Combined Listing. */
export interface ChildProductRelationInput {
  childProductId: string;
  selectedParentOptionValues: SelectedVariantOptionInput[];
}

/** The input fields for specifying the collection to delete. */
export interface CollectionDeleteInput {
  id: string;
}

/** The input fields for duplicating a collection. */
export interface CollectionDuplicateInput {
  collectionId: string;
  copyPublications?: boolean;
  newTitle: string;
}

/** The input fields for identifying a collection. */
export interface CollectionIdentifierInput {
  customId?: UniqueMetafieldValueInput;
  handle?: string;
  id?: string;
}

/** The input fields required to create a collection. */
export interface CollectionInput {
  descriptionHtml?: string;
  handle?: string;
  id?: string;
  image?: ImageInput;
  metafields?: MetafieldInput[];
  products?: string[];
  redirectNewHandle?: boolean;
  ruleSet?: CollectionRuleSetInput;
  seo?: SEOInput;
  sortOrder?: CollectionSortOrder;
  templateSuffix?: string;
  title?: string;
  publications?: CollectionPublicationInput[];
}

/** The input fields for publications to which a collection will be published. */
export interface CollectionPublicationInput {
  publicationId?: string;
  channelHandle?: string;
  channelId?: string;
}

/** The input fields for specifying a collection to publish and the sales channels to publish it to. */
export interface CollectionPublishInput {
  collectionPublications: CollectionPublicationInput[];
  id: string;
}

/** The input fields for a rule to associate with a collection. */
export interface CollectionRuleInput {
  column: CollectionRuleColumn;
  condition: string;
  conditionObjectId?: string;
  relation: CollectionRuleRelation;
}

/** The input fields for a rule set of the collection. */
export interface CollectionRuleSetInput {
  appliedDisjunctively: boolean;
  rules?: CollectionRuleInput[];
}

/** The input fields for specifying the collection to unpublish and the sales channels to remove it from. */
export interface CollectionUnpublishInput {
  collectionPublications: CollectionPublicationInput[];
  id: string;
}

/** The input fields to create or update the address of a company location. */
export interface CompanyAddressInput {
  address1?: string;
  address2?: string;
  city?: string;
  countryCode?: CountryCode;
  firstName?: string;
  lastName?: string;
  phone?: string;
  recipient?: string;
  zip?: string;
  zoneCode?: string;
}

/** The input fields for company contact attributes when creating or updating a company contact. */
export interface CompanyContactInput {
  email?: string;
  firstName?: string;
  lastName?: string;
  locale?: string;
  phone?: string;
  title?: string;
}

/** The input fields for the role and location to assign to a company contact. */
export interface CompanyContactRoleAssign {
  companyContactRoleId: string;
  companyLocationId: string;
}

/** The input fields and values for creating a company and its associated resources. */
export interface CompanyCreateInput {
  company: CompanyInput;
  companyContact?: CompanyContactInput;
  companyLocation?: CompanyLocationInput;
}

/** The input fields for company attributes when creating or updating a company. */
export interface CompanyInput {
  customerSince?: string;
  externalId?: string;
  name?: string;
  note?: string;
}

/** The input fields for company location when creating or updating a company location. */
export interface CompanyLocationInput {
  billingAddress?: CompanyAddressInput;
  billingSameAsShipping?: boolean;
  buyerExperienceConfiguration?: BuyerExperienceConfigurationInput;
  externalId?: string;
  locale?: string;
  name?: string;
  note?: string;
  phone?: string;
  shippingAddress?: CompanyAddressInput;
  taxExempt?: boolean;
  taxExemptions?: TaxExemption[];
  taxRegistrationId?: string;
}

/** The input fields for the role and contact to assign on a location. */
export interface CompanyLocationRoleAssign {
  companyContactId: string;
  companyContactRoleId: string;
}

/** The input fields for company location when creating or updating a company location. */
export interface CompanyLocationUpdateInput {
  buyerExperienceConfiguration?: BuyerExperienceConfigurationInput;
  externalId?: string;
  locale?: string;
  name?: string;
  note?: string;
  phone?: string;
}

/** The input fields for a consent policy to be updated or created. */
export interface ConsentPolicyInput {
  consentRequired?: boolean;
  countryCode?: PrivacyCountryCode;
  dataSaleOptOutRequired?: boolean;
  regionCode?: string;
}

/** The input fields for the context data that determines the pricing of a variant. Refer to [Product](https://shopify.dev/docs/api/admin-graphql/latest/queries/product?example=Get+the+price+range+for+a+product+for+buyers+from+Canada)for more information on how to use this input o... */
export interface ContextualPricingContext {
  companyLocationId?: string;
  country?: CountryCode;
  locationId?: string;
}

/** The context data that determines the publication status of a product. */
export interface ContextualPublicationContext {
  companyLocationId?: string;
  country?: CountryCode;
  locationId?: string;
}

/** The input fields required to specify a harmonized system code. */
export interface CountryHarmonizedSystemCodeInput {
  countryCode?: CountryCode;
  harmonizedSystemCode: string;
}

/** The input fields required to create a media object. */
export interface CreateMediaInput {
  alt?: string;
  mediaContentType: MediaContentType;
  originalSource: string;
}

/** The input fields to delete a customer. */
export interface CustomerDeleteInput {
  id: string;
}

/** Information that describes when a customer consented to receiving marketing material by email. */
export interface CustomerEmailMarketingConsentInput {
  consentUpdatedAt?: string;
  marketingOptInLevel?: CustomerMarketingOptInLevel;
  marketingState: CustomerEmailMarketingState;
  sourceLocationId?: string;
}

/** The input fields for the email consent information to update for a given customer ID. */
export interface CustomerEmailMarketingConsentUpdateInput {
  customerId: string;
  emailMarketingConsent: CustomerEmailMarketingConsentInput;
}

/** The input fields for identifying a customer. */
export interface CustomerIdentifierInput {
  customId?: UniqueMetafieldValueInput;
  emailAddress?: string;
  id?: string;
  phoneNumber?: string;
}

/** The input fields and values to use when creating or updating a customer. */
export interface CustomerInput {
  email?: string;
  emailMarketingConsent?: CustomerEmailMarketingConsentInput;
  firstName?: string;
  id?: string;
  lastName?: string;
  locale?: string;
  metafields?: MetafieldInput[];
  multipassIdentifier?: string;
  note?: string;
  phone?: string;
  smsMarketingConsent?: CustomerSmsMarketingConsentInput;
  tags?: string[];
  taxExempt?: boolean;
  taxExemptions?: TaxExemption[];
  addresses?: MailingAddressInput[];
}

/** The input fields to override default customer merge rules. */
export interface CustomerMergeOverrideFields {
  customerIdOfDefaultAddressToKeep?: string;
  customerIdOfEmailToKeep?: string;
  customerIdOfFirstNameToKeep?: string;
  customerIdOfLastNameToKeep?: string;
  customerIdOfPhoneNumberToKeep?: string;
  note?: string;
  tags?: string[];
}

/** The input fields for a remote gateway payment method, only one remote reference permitted. */
export interface CustomerPaymentMethodRemoteInput {
  authorizeNetCustomerPaymentProfile?: RemoteAuthorizeNetCustomerPaymentProfileInput;
  braintreePaymentMethod?: RemoteBraintreePaymentMethodInput;
  stripePaymentMethod?: RemoteStripePaymentMethodInput;
}

/** The input fields and values for creating a customer segment members query. */
export interface CustomerSegmentMembersQueryInput {
  query?: string;
  reverse?: boolean;
  segmentId?: string;
  sortKey?: string;
}

/** The input fields required to identify a customer. */
export interface CustomerSetIdentifiers {
  customId?: UniqueMetafieldValueInput;
  email?: string;
  id?: string;
  phone?: string;
}

/** The input fields and values to use when creating or updating a customer. */
export interface CustomerSetInput {
  addresses?: MailingAddressInput[];
  email?: string;
  firstName?: string;
  lastName?: string;
  locale?: string;
  note?: string;
  phone?: string;
  tags?: string[];
  taxExempt?: boolean;
  taxExemptions?: TaxExemption[];
  id?: string;
}

/** The marketing consent information when the customer consented to receiving marketing material by SMS. */
export interface CustomerSmsMarketingConsentInput {
  consentUpdatedAt?: string;
  marketingOptInLevel?: CustomerMarketingOptInLevel;
  marketingState: CustomerSmsMarketingState;
  sourceLocationId?: string;
}

/** The input fields for updating SMS marketing consent information for a given customer ID. */
export interface CustomerSmsMarketingConsentUpdateInput {
  customerId: string;
  smsMarketingConsent: CustomerSmsMarketingConsentInput;
}

/** The input fields for a custom shipping package used to pack shipment. */
export interface CustomShippingPackageInput {
  default?: boolean;
  dimensions?: ObjectDimensionsInput;
  name?: string;
  type?: ShippingPackageType;
  weight?: WeightInput;
}

/** The input fields for a delegate access token. */
export interface DelegateAccessTokenInput {
  delegateAccessScope: string[];
  expiresIn?: number;
}

/** The input fields required to create a carrier service. */
export interface DeliveryCarrierServiceCreateInput {
  active: boolean;
  callbackUrl: string;
  name: string;
  supportsServiceDiscovery: boolean;
}

/** The input fields used to update a carrier service. */
export interface DeliveryCarrierServiceUpdateInput {
  active?: boolean;
  callbackUrl?: string;
  id: string;
  name?: string;
  supportsServiceDiscovery?: boolean;
}

/** The input fields to specify a country. */
export interface DeliveryCountryInput {
  code?: CountryCode;
  includeAllProvinces?: boolean;
  provinces?: DeliveryProvinceInput[];
  restOfWorld?: boolean;
}

/** The input fields to create and update a delivery customization. */
export interface DeliveryCustomizationInput {
  enabled?: boolean;
  functionHandle?: string;
  metafields?: MetafieldInput[];
  title?: string;
  functionId?: string;
}

/** The input fields for a delivery zone associated to a location group and profile. */
export interface DeliveryLocationGroupZoneInput {
  countries?: DeliveryCountryInput[];
  id?: string;
  methodDefinitionsToCreate?: DeliveryMethodDefinitionInput[];
  methodDefinitionsToUpdate?: DeliveryMethodDefinitionInput[];
  name?: string;
}

/** The input fields for a local pickup setting associated with a location. */
export interface DeliveryLocationLocalPickupEnableInput {
  instructions?: string;
  locationId: string;
  pickupTime: DeliveryLocalPickupTime;
}

/** The input fields for a method definition. */
export interface DeliveryMethodDefinitionInput {
  active?: boolean;
  conditionsToUpdate?: DeliveryUpdateConditionInput[];
  description?: string;
  id?: string;
  name?: string;
  participant?: DeliveryParticipantInput;
  priceConditionsToCreate?: DeliveryPriceConditionInput[];
  rateDefinition?: DeliveryRateDefinitionInput;
  weightConditionsToCreate?: DeliveryWeightConditionInput[];
}

/** The input fields for a participant. */
export interface DeliveryParticipantInput {
  adaptToNewServices?: boolean;
  carrierServiceId?: string;
  fixedFee?: MoneyInput;
  id?: string;
  participantServices?: DeliveryParticipantServiceInput[];
  percentageOfRateFee?: number;
}

/** The input fields for a shipping service provided by a participant. */
export interface DeliveryParticipantServiceInput {
  active: boolean;
  name: string;
}

/** The input fields for a price-based condition of a delivery method definition. */
export interface DeliveryPriceConditionInput {
  criteria?: MoneyInput;
  operator?: DeliveryConditionOperator;
}

/** The input fields for a delivery profile. */
export interface DeliveryProfileInput {
  conditionsToDelete?: string[];
  locationGroupsToCreate?: DeliveryProfileLocationGroupInput[];
  locationGroupsToDelete?: string[];
  locationGroupsToUpdate?: DeliveryProfileLocationGroupInput[];
  methodDefinitionsToDelete?: string[];
  name?: string;
  profileLocationGroups?: DeliveryProfileLocationGroupInput[];
  sellingPlanGroupsToAssociate?: string[];
  sellingPlanGroupsToDissociate?: string[];
  variantsToAssociate?: string[];
  variantsToDissociate?: string[];
  zonesToDelete?: string[];
}

/** The input fields for a location group associated to a delivery profile. */
export interface DeliveryProfileLocationGroupInput {
  id?: string;
  locations?: string[];
  locationsToAdd?: string[];
  locationsToRemove?: string[];
  zonesToCreate?: DeliveryLocationGroupZoneInput[];
  zonesToUpdate?: DeliveryLocationGroupZoneInput[];
}

/** The input fields to specify a region. */
export interface DeliveryProvinceInput {
  code: string;
}

/** The input fields for a rate definition. */
export interface DeliveryRateDefinitionInput {
  id?: string;
  price: MoneyInput;
}

/** The input fields for updating the condition of a delivery method definition. */
export interface DeliveryUpdateConditionInput {
  criteria?: number;
  criteriaUnit?: string;
  field?: DeliveryConditionField;
  id: string;
  operator?: DeliveryConditionOperator;
}

/** The input fields for a weight-based condition of a delivery method definition. */
export interface DeliveryWeightConditionInput {
  criteria?: WeightInput;
  operator?: DeliveryConditionOperator;
}

/** The input fields configuring the deposit for a B2B buyer. */
export interface DepositInput {
  percentage: number;
}

/** The input fields for the value of the discount and how it is applied. */
export interface DiscountAmountInput {
  amount?: string;
  appliesOnEachItem?: boolean;
}

/** The input fields for creating or updating an automatic discount that's managed by an app. */
export interface DiscountAutomaticAppInput {
  appliesOnOneTimePurchase?: boolean;
  appliesOnSubscription?: boolean;
  combinesWith?: DiscountCombinesWithInput;
  context?: DiscountContextInput;
  discountClasses?: DiscountClass[];
  endsAt?: string;
  functionHandle?: string;
  metafields?: MetafieldInput[];
  recurringCycleLimit?: number;
  startsAt?: string;
  tags?: string[];
  title?: string;
  functionId?: string;
}

/** The input fields for creating or updating an [amount off discount](https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's automatically applied on a cart and at checkout. */
export interface DiscountAutomaticBasicInput {
  combinesWith?: DiscountCombinesWithInput;
  context?: DiscountContextInput;
  customerGets?: DiscountCustomerGetsInput;
  endsAt?: string;
  minimumRequirement?: DiscountMinimumRequirementInput;
  recurringCycleLimit?: number;
  startsAt?: string;
  tags?: string[];
  title?: string;
}

/** The input fields for creating or updating a [buy X get Y discount (BXGY)](https://help.shopify.com/manual/discounts/discount-types/buy-x-get-y) that's automatically applied on a cart and at checkout. */
export interface DiscountAutomaticBxgyInput {
  combinesWith?: DiscountCombinesWithInput;
  context?: DiscountContextInput;
  customerBuys?: DiscountCustomerBuysInput;
  customerGets?: DiscountCustomerGetsInput;
  endsAt?: string;
  startsAt?: string;
  tags?: string[];
  title?: string;
  usesPerOrderLimit?: string;
}

/** The input fields for creating or updating a [free shipping discount](https://help.shopify.com/manual/discounts/discount-types/free-shipping) that's automatically applied on a cart and at checkout. */
export interface DiscountAutomaticFreeShippingInput {
  appliesOnOneTimePurchase?: boolean;
  appliesOnSubscription?: boolean;
  combinesWith?: DiscountCombinesWithInput;
  context?: DiscountContextInput;
  destination?: DiscountShippingDestinationSelectionInput;
  endsAt?: string;
  maximumShippingPrice?: string;
  minimumRequirement?: DiscountMinimumRequirementInput;
  recurringCycleLimit?: number;
  startsAt?: string;
  tags?: string[];
  title?: string;
}

/** The input fields for creating or updating a code discount, where the discount type is provided by an app extension that uses [Shopify Functions](https://shopify.dev/docs/apps/build/functions). */
export interface DiscountCodeAppInput {
  appliesOncePerCustomer?: boolean;
  appliesOnOneTimePurchase?: boolean;
  appliesOnSubscription?: boolean;
  code?: string;
  combinesWith?: DiscountCombinesWithInput;
  context?: DiscountContextInput;
  discountClasses?: DiscountClass[];
  endsAt?: string;
  functionHandle?: string;
  metafields?: MetafieldInput[];
  recurringCycleLimit?: number;
  startsAt?: string;
  tags?: string[];
  title?: string;
  usageLimit?: number;
  customerSelection?: DiscountCustomerSelectionInput;
  functionId?: string;
}

/** The input fields for creating or updating an [amount off discount](https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when a customer enters a code. Amount off discounts can be a percentage off or a fixed ... */
export interface DiscountCodeBasicInput {
  appliesOncePerCustomer?: boolean;
  code?: string;
  combinesWith?: DiscountCombinesWithInput;
  context?: DiscountContextInput;
  customerGets?: DiscountCustomerGetsInput;
  endsAt?: string;
  minimumRequirement?: DiscountMinimumRequirementInput;
  recurringCycleLimit?: number;
  startsAt?: string;
  tags?: string[];
  title?: string;
  usageLimit?: number;
  customerSelection?: DiscountCustomerSelectionInput;
}

/** The input fields for creating or updating a [buy X get Y discount (BXGY)](https://help.shopify.com/manual/discounts/discount-types/buy-x-get-y) that's applied on a cart and at checkout when a customer enters a code. */
export interface DiscountCodeBxgyInput {
  appliesOncePerCustomer?: boolean;
  code?: string;
  combinesWith?: DiscountCombinesWithInput;
  context?: DiscountContextInput;
  customerBuys?: DiscountCustomerBuysInput;
  customerGets?: DiscountCustomerGetsInput;
  endsAt?: string;
  startsAt?: string;
  tags?: string[];
  title?: string;
  usageLimit?: number;
  usesPerOrderLimit?: number;
  customerSelection?: DiscountCustomerSelectionInput;
}

/** The input fields for creating or updating a [free shipping discount](https://help.shopify.com/manual/discounts/discount-types/free-shipping) that's applied on a cart and at checkout when a customer enters a code. */
export interface DiscountCodeFreeShippingInput {
  appliesOncePerCustomer?: boolean;
  appliesOnOneTimePurchase?: boolean;
  appliesOnSubscription?: boolean;
  code?: string;
  combinesWith?: DiscountCombinesWithInput;
  context?: DiscountContextInput;
  destination?: DiscountShippingDestinationSelectionInput;
  endsAt?: string;
  maximumShippingPrice?: string;
  minimumRequirement?: DiscountMinimumRequirementInput;
  recurringCycleLimit?: number;
  startsAt?: string;
  tags?: string[];
  title?: string;
  usageLimit?: number;
  customerSelection?: DiscountCustomerSelectionInput;
}

/** The input fields for collections attached to a discount. */
export interface DiscountCollectionsInput {
  add?: string[];
  remove?: string[];
}

/** The input fields to determine which discount classes the discount can combine with. */
export interface DiscountCombinesWithInput {
  orderDiscounts?: boolean;
  productDiscounts?: boolean;
  productDiscountsWithTagsOnSameCartLine?: ProductDiscountsWithTagsOnSameCartLineInput;
  shippingDiscounts?: boolean;
}

/** The input fields for the buyers who can use this discount. */
export interface DiscountContextInput {
  all?: DiscountBuyerSelection;
  customers?: DiscountCustomersInput;
  customerSegments?: DiscountCustomerSegmentsInput;
}

/** The input fields for a list of countries to add or remove from the free shipping discount. */
export interface DiscountCountriesInput {
  add?: CountryCode[];
  includeRestOfWorld?: boolean;
  remove?: CountryCode[];
}

/** The input fields for prerequisite items and quantity for the discount. */
export interface DiscountCustomerBuysInput {
  isOneTimePurchase?: boolean;
  isSubscription?: boolean;
  items?: DiscountItemsInput;
  value?: DiscountCustomerBuysValueInput;
}

/** The input fields for prerequisite quantity or minimum purchase amount required for the discount. */
export interface DiscountCustomerBuysValueInput {
  amount?: string;
  quantity?: string;
}

/** Specifies the items that will be discounted, the quantity of items that will be discounted, and the value of discount. */
export interface DiscountCustomerGetsInput {
  appliesOnOneTimePurchase?: boolean;
  appliesOnSubscription?: boolean;
  items?: DiscountItemsInput;
  value?: DiscountCustomerGetsValueInput;
}

/** The input fields for the quantity of items discounted and the discount value. */
export interface DiscountCustomerGetsValueInput {
  discountAmount?: DiscountAmountInput;
  discountOnQuantity?: DiscountOnQuantityInput;
  percentage?: number;
}

/** The input fields for which customer segments to add to or remove from the discount. */
export interface DiscountCustomerSegmentsInput {
  add?: string[];
  remove?: string[];
}

/** The input fields for the customers who can use this discount. */
export interface DiscountCustomerSelectionInput {
  all?: boolean;
  customers?: DiscountCustomersInput;
  customerSegments?: DiscountCustomerSegmentsInput;
}

/** The input fields for which customers to add to or remove from the discount. */
export interface DiscountCustomersInput {
  add?: string[];
  remove?: string[];
}

/** The input fields for how the discount will be applied. Currently, only percentage off is supported. */
export interface DiscountEffectInput {
  amount?: string;
  percentage?: number;
}

/** The input fields for the items attached to a discount. You can specify the discount items by product ID or collection ID. */
export interface DiscountItemsInput {
  all?: boolean;
  collections?: DiscountCollectionsInput;
  products?: DiscountProductsInput;
}

/** The input fields for the minimum quantity required for the discount. */
export interface DiscountMinimumQuantityInput {
  greaterThanOrEqualToQuantity?: string;
}

/** The input fields for the minimum quantity or subtotal required for a discount. */
export interface DiscountMinimumRequirementInput {
  quantity?: DiscountMinimumQuantityInput;
  subtotal?: DiscountMinimumSubtotalInput;
}

/** The input fields for the minimum subtotal required for a discount. */
export interface DiscountMinimumSubtotalInput {
  greaterThanOrEqualToSubtotal?: string;
}

/** The input fields for the quantity of items discounted and the discount value. */
export interface DiscountOnQuantityInput {
  effect?: DiscountEffectInput;
  quantity?: string;
}

/** The input fields for adding and removing [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) and [product variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/productvariant) as prerequisites or as eligible items for a discount. */
export interface DiscountProductsInput {
  productsToAdd?: string[];
  productsToRemove?: string[];
  productVariantsToAdd?: string[];
  productVariantsToRemove?: string[];
}

/** The input fields for the redeem code to attach to a discount. */
export interface DiscountRedeemCodeInput {
  code: string;
}

/** The input fields for the destinations where the free shipping discount will be applied. */
export interface DiscountShippingDestinationSelectionInput {
  all?: boolean;
  countries?: DiscountCountriesInput;
}

/** The input fields for applying an order-level discount to a draft order. */
export interface DraftOrderAppliedDiscountInput {
  amountWithCurrency?: MoneyInput;
  description?: string;
  title?: string;
  value: number;
  valueType: DraftOrderAppliedDiscountType;
  amount?: string;
}

/** The input fields used to determine available delivery options for a draft order. */
export interface DraftOrderAvailableDeliveryOptionsInput {
  acceptAutomaticDiscounts?: boolean;
  appliedDiscount?: DraftOrderAppliedDiscountInput;
  discountCodes?: string[];
  lineItems?: DraftOrderLineItemInput[];
  marketRegionCountryCode?: CountryCode;
  purchasingEntity?: PurchasingEntityInput;
  shippingAddress?: MailingAddressInput;
}

/** The input fields to specify the draft order to delete by its ID. */
export interface DraftOrderDeleteInput {
  id: string;
}

/** The input fields used to create or update a draft order. */
export interface DraftOrderInput {
  acceptAutomaticDiscounts?: boolean;
  allowDiscountCodesInCheckout?: boolean;
  appliedDiscount?: DraftOrderAppliedDiscountInput;
  billingAddress?: MailingAddressInput;
  customAttributes?: AttributeInput[];
  discountCodes?: string[];
  email?: string;
  lineItems?: DraftOrderLineItemInput[];
  localizedFields?: LocalizedFieldInput[];
  metafields?: MetafieldInput[];
  note?: string;
  paymentTerms?: PaymentTermsInput;
  phone?: string;
  poNumber?: string;
  presentmentCurrencyCode?: CurrencyCode;
  purchasingEntity?: PurchasingEntityInput;
  reserveInventoryUntil?: string;
  sessionToken?: string;
  shippingAddress?: MailingAddressInput;
  shippingLine?: ShippingLineInput;
  sourceName?: string;
  tags?: string[];
  taxExempt?: boolean;
  transformerFingerprint?: string;
  useCustomerDefaultAddress?: boolean;
  visibleToCustomer?: boolean;
  customerId?: string;
  localizationExtensions?: LocalizationExtensionInput[];
  marketRegionCountryCode?: CountryCode;
}

/** The input fields representing the components of a line item. */
export interface DraftOrderLineItemComponentInput {
  quantity: number;
  uuid?: string;
  variantId?: string;
}

/** The input fields for a line item included in a draft order. */
export interface DraftOrderLineItemInput {
  appliedDiscount?: DraftOrderAppliedDiscountInput;
  components?: DraftOrderLineItemComponentInput[];
  customAttributes?: AttributeInput[];
  generatePriceOverride?: boolean;
  originalUnitPriceWithCurrency?: MoneyInput;
  priceOverride?: MoneyInput;
  quantity: number;
  requiresShipping?: boolean;
  sku?: string;
  taxable?: boolean;
  title?: string;
  uuid?: string;
  variantId?: string;
  weight?: WeightInput;
  bundleComponents?: BundlesDraftOrderBundleLineItemComponentInput[];
  grams?: number;
  originalUnitPrice?: string;
}

/** The input fields for an email. */
export interface EmailInput {
  bcc?: string[];
  body?: string;
  customMessage?: string;
  from?: string;
  subject?: string;
  to?: string;
}

/** The input fields for an EventBridge webhook subscription. */
export interface EventBridgeWebhookSubscriptionInput {
  arn?: string;
  filter?: string;
  format?: WebhookSubscriptionFormat;
  includeFields?: string[];
  metafieldNamespaces?: string[];
  metafields?: HasMetafieldsMetafieldIdentifierInput[];
  name?: string;
}

/** The input fields for an applied discount on a calculated exchange line item. */
export interface ExchangeLineItemAppliedDiscountInput {
  description?: string;
  value: ExchangeLineItemAppliedDiscountValueInput;
}

/** The input value for an applied discount on a calculated exchange line item. Can either specify the value as a fixed amount or a percentage. */
export interface ExchangeLineItemAppliedDiscountValueInput {
  amount?: MoneyInput;
  percentage?: number;
}

/** The input fields for new line items to be added to the order as part of an exchange. */
export interface ExchangeLineItemInput {
  appliedDiscount?: ExchangeLineItemAppliedDiscountInput;
  giftCardCodes?: string[];
  quantity: number;
  variantId?: string;
}

/** The input fields for removing an exchange line item from a return. */
export interface ExchangeLineItemRemoveFromReturnInput {
  exchangeLineItemId: string;
  quantity: number;
}

/** The input fields that are required to create a file object. */
export interface FileCreateInput {
  alt?: string;
  contentType?: FileContentType;
  duplicateResolutionMode?: FileCreateInputDuplicateResolutionMode;
  filename?: string;
  originalSource: string;
}

/** The input fields required to create or update a file object. */
export interface FileSetInput {
  alt?: string;
  contentType?: FileContentType;
  duplicateResolutionMode?: FileCreateInputDuplicateResolutionMode;
  filename?: string;
  id?: string;
  originalSource?: string;
}

/** The input fields that are required to update a file object. */
export interface FileUpdateInput {
  alt?: string;
  filename?: string;
  id: string;
  originalSource?: string;
  previewImageSource?: string;
  referencesToAdd?: string[];
  referencesToRemove?: string[];
}

/** The input fields used to create a fulfillment event. */
export interface FulfillmentEventInput {
  address1?: string;
  city?: string;
  country?: string;
  estimatedDeliveryAt?: string;
  fulfillmentId: string;
  happenedAt?: string;
  latitude?: number;
  longitude?: number;
  message?: string;
  province?: string;
  status: FulfillmentEventStatus;
  zip?: string;
}

/** The input fields used to create a fulfillment from fulfillment orders. */
export interface FulfillmentInput {
  lineItemsByFulfillmentOrder: FulfillmentOrderLineItemsInput[];
  notifyCustomer?: boolean;
  originAddress?: FulfillmentOriginAddressInput;
  trackingInfo?: FulfillmentTrackingInput;
}

/** The input fields for the fulfillment hold applied on the fulfillment order. */
export interface FulfillmentOrderHoldInput {
  externalId?: string;
  fulfillmentOrderLineItems?: FulfillmentOrderLineItemInput[];
  handle?: string;
  notifyMerchant?: boolean;
  reason: FulfillmentHoldReason;
  reasonNotes?: string;
}

/** The input fields used to include the quantity of the fulfillment order line item that should be fulfilled. */
export interface FulfillmentOrderLineItemInput {
  id: string;
  quantity: number;
}

/** The input fields used to include the line items of a specified fulfillment order that should be fulfilled. */
export interface FulfillmentOrderLineItemsInput {
  fulfillmentOrderId: string;
  fulfillmentOrderLineItems?: FulfillmentOrderLineItemInput[];
}

/** The input fields for marking fulfillment order line items as ready for pickup. */
export interface FulfillmentOrderLineItemsPreparedForPickupInput {
  lineItemsByFulfillmentOrder: PreparedFulfillmentOrderLineItemsInput[];
}

/** The input fields for merging fulfillment orders. */
export interface FulfillmentOrderMergeInput {
  mergeIntents: FulfillmentOrderMergeInputMergeIntent[];
}

/** The input fields for merging fulfillment orders into a single merged fulfillment order. */
export interface FulfillmentOrderMergeInputMergeIntent {
  fulfillmentOrderId: string;
  fulfillmentOrderLineItems?: FulfillmentOrderLineItemInput[];
}

/** The input fields for the progress report for the fulfillment order. */
export interface FulfillmentOrderReportProgressInput {
  reasonNotes?: string;
}

/** The input fields for the split applied to the fulfillment order. */
export interface FulfillmentOrderSplitInput {
  fulfillmentOrderId: string;
  fulfillmentOrderLineItems: FulfillmentOrderLineItemInput[];
}

/** The input fields used to include the address at which the fulfillment occurred. This input object is intended for tax purposes, as a full address is required for tax providers to accurately calculate taxes. Typically this is the address of the warehouse or fulfillment center. ... */
export interface FulfillmentOriginAddressInput {
  address1?: string;
  address2?: string;
  city?: string;
  countryCode: string;
  provinceCode?: string;
  zip?: string;
}

/** The input fields that specify all possible fields for tracking information. */
export interface FulfillmentTrackingInput {
  company?: string;
  number?: string;
  numbers?: string[];
  url?: string;
  urls?: string[];
}

/** The input fields used to create a fulfillment from fulfillment orders. */
export interface FulfillmentV2Input {
  lineItemsByFulfillmentOrder: FulfillmentOrderLineItemsInput[];
  notifyCustomer?: boolean;
  originAddress?: FulfillmentOriginAddressInput;
  trackingInfo?: FulfillmentTrackingInput;
}

/** The input fields to issue a gift card. */
export interface GiftCardCreateInput {
  code?: string;
  customerId?: string;
  expiresOn?: string;
  initialValue: string;
  note?: string;
  recipientAttributes?: GiftCardRecipientInput;
  templateSuffix?: string;
}

/** The input fields for a gift card credit transaction. */
export interface GiftCardCreditInput {
  creditAmount: MoneyInput;
  note?: string;
  processedAt?: string;
}

/** The input fields for a gift card debit transaction. */
export interface GiftCardDebitInput {
  debitAmount: MoneyInput;
  note?: string;
  processedAt?: string;
}

/** The input fields to add a recipient to a gift card. */
export interface GiftCardRecipientInput {
  id: string;
  message?: string;
  preferredName?: string;
  sendNotificationAt?: string;
}

/** The input fields to update a gift card. */
export interface GiftCardUpdateInput {
  customerId?: string;
  expiresOn?: string;
  note?: string;
  recipientAttributes?: GiftCardRecipientInput;
  templateSuffix?: string;
}

/** The input fields that identify metafield definitions. */
export interface HasMetafieldsMetafieldIdentifierInput {
  key: string;
  namespace?: string;
}

/** The input fields for an image. */
export interface ImageInput {
  altText?: string;
  id?: string;
  src?: string;
}

/** The available options for transforming an image. */
export interface ImageTransformInput {
  crop?: CropRegion;
  maxHeight?: number;
  maxWidth?: number;
  preferredContentType?: ImageContentType;
  scale?: number;
}

/** The input fields for the incoming line item. */
export interface IncomingRequestLineItemInput {
  fulfillmentOrderLineItemId: string;
  message?: string;
}

/** The input fields required to adjust the available quantity of a product variant at a location. */
export interface InventoryAdjustmentInput {
  adjustment?: number;
  changeFromQuantity?: number;
  locationId: string;
}

/** The input fields required to adjust inventory quantities. */
export interface InventoryAdjustQuantitiesInput {
  changes: InventoryChangeInput[];
  name: string;
  reason: string;
  referenceDocumentUri?: string;
}

/** The input fields to specify whether the inventory item should be activated or not at the specified location. */
export interface InventoryBulkToggleActivationInput {
  activate: boolean;
  locationId: string;
}

/** The input fields for the change to be made to an inventory item at a location. */
export interface InventoryChangeInput {
  changeFromQuantity?: number;
  delta: number;
  inventoryItemId: string;
  ledgerDocumentUri?: string;
  locationId: string;
}

/** The input fields for an inventory item. */
export interface InventoryItemInput {
  cost?: string;
  countryCodeOfOrigin?: CountryCode;
  countryHarmonizedSystemCodes?: CountryHarmonizedSystemCodeInput[];
  harmonizedSystemCode?: string;
  measurement?: InventoryItemMeasurementInput;
  provinceCodeOfOrigin?: string;
  requiresShipping?: boolean;
  sku?: string;
  tracked?: boolean;
}

/** The input fields for an inventory item measurement. */
export interface InventoryItemMeasurementInput {
  shippingPackageId?: string;
  weight?: WeightInput;
}

/** The input fields for an inventory level. */
export interface InventoryLevelInput {
  availableQuantity: number;
  locationId: string;
}

/** The input fields required to move inventory quantities. */
export interface InventoryMoveQuantitiesInput {
  changes: InventoryMoveQuantityChange[];
  reason: string;
  referenceDocumentUri: string;
}

/** Represents the change to be made to an inventory item at a location. The change can either involve the same quantity name between different locations, or involve different quantity names between the same location. */
export interface InventoryMoveQuantityChange {
  from: InventoryMoveQuantityTerminalInput;
  inventoryItemId: string;
  quantity: number;
  to: InventoryMoveQuantityTerminalInput;
}

/** The input fields representing the change to be made to an inventory item at a location. */
export interface InventoryMoveQuantityTerminalInput {
  changeFromQuantity?: number;
  ledgerDocumentUri?: string;
  locationId: string;
  name: string;
}

/** The input fields for the quantity to be set for an inventory item at a location. */
export interface InventoryQuantityInput {
  changeFromQuantity?: number;
  inventoryItemId: string;
  locationId: string;
  quantity: number;
}

/** The input fields for a scheduled change of an inventory item. */
export interface InventoryScheduledChangeInput {
  expectedAt: string;
  fromName: string;
  toName: string;
}

/** The input fields for the inventory item associated with the scheduled changes that need to be applied. */
export interface InventoryScheduledChangeItemInput {
  inventoryItemId: string;
  ledgerDocumentUri: string;
  locationId: string;
  scheduledChanges: InventoryScheduledChangeInput[];
}

/** The input fields required to set inventory on hand quantities. */
export interface InventorySetOnHandQuantitiesInput {
  reason: string;
  referenceDocumentUri?: string;
  setQuantities: InventorySetQuantityInput[];
}

/** The input fields required to set inventory quantities. */
export interface InventorySetQuantitiesInput {
  name: string;
  quantities: InventoryQuantityInput[];
  reason: string;
  referenceDocumentUri?: string;
}

/** The input fields for the quantity to be set for an inventory item at a location. */
export interface InventorySetQuantityInput {
  changeFromQuantity?: number;
  inventoryItemId: string;
  locationId: string;
  quantity: number;
}

/** The input fields for setting up scheduled changes of inventory items. */
export interface InventorySetScheduledChangesInput {
  items: InventoryScheduledChangeItemInput[];
  reason: string;
  referenceDocumentUri: string;
}

/** The input fields to add a shipment. */
export interface InventoryShipmentCreateInput {
  barcode?: string;
  dateCreated?: string;
  lineItems: InventoryShipmentLineItemInput[];
  movementId: string;
  trackingInput?: InventoryShipmentTrackingInput;
}

/** The input fields for a line item on an inventory shipment. */
export interface InventoryShipmentLineItemInput {
  inventoryItemId: string;
  quantity: number;
}

/** The input fields to receive an item on an inventory shipment. */
export interface InventoryShipmentReceiveItemInput {
  quantity: number;
  reason: InventoryShipmentReceiveLineItemReason;
  shipmentLineItemId: string;
}

/** The input fields for an inventory shipment's tracking information. */
export interface InventoryShipmentTrackingInput {
  arrivesAt?: string;
  company?: string;
  trackingNumber?: string;
  trackingUrl?: string;
}

/** The input fields for a line item on an inventory shipment. */
export interface InventoryShipmentUpdateItemQuantitiesInput {
  quantity: number;
  shipmentLineItemId: string;
}

/** The input fields to create an inventory transfer. */
export interface InventoryTransferCreateAsReadyToShipInput {
  dateCreated?: string;
  destinationLocationId?: string;
  lineItems?: InventoryTransferLineItemInput[];
  note?: string;
  originLocationId?: string;
  referenceName?: string;
  tags?: string[];
}

/** The input fields to create an inventory transfer. */
export interface InventoryTransferCreateInput {
  dateCreated?: string;
  destinationLocationId?: string;
  lineItems?: InventoryTransferLineItemInput[];
  note?: string;
  originLocationId?: string;
  referenceName?: string;
  tags?: string[];
}

/** The input fields to edit an inventory transfer. */
export interface InventoryTransferEditInput {
  dateCreated?: string;
  destinationId?: string;
  note?: string;
  originId?: string;
  referenceName?: string;
  tags?: string[];
}

/** The input fields for a line item on an inventory transfer. */
export interface InventoryTransferLineItemInput {
  inventoryItemId: string;
  quantity: number;
}

/** The input fields to remove inventory items from a transfer. */
export interface InventoryTransferRemoveItemsInput {
  id: string;
  transferLineItemIds?: string[];
}

/** The input fields to the InventoryTransferSetItems mutation. */
export interface InventoryTransferSetItemsInput {
  id: string;
  lineItems: InventoryTransferLineItemInput[];
}

/** The input fields required to link a product option to a metafield. */
export interface LinkedMetafieldCreateInput {
  key: string;
  namespace: string;
  values?: string[];
}

/** The input fields for linking a combined listing option to a metafield. */
export interface LinkedMetafieldInput {
  key: string;
  namespace: string;
  values: string[];
}

/** The input fields required to link a product option to a metafield. */
export interface LinkedMetafieldUpdateInput {
  key: string;
  namespace: string;
}

/** The input fields for a LocalizationExtensionInput. */
export interface LocalizationExtensionInput {
  key: LocalizationExtensionKey;
  value: string;
}

/** The input fields for a LocalizedFieldInput. */
export interface LocalizedFieldInput {
  key: LocalizedFieldKey;
  value: string;
}

/** The input fields to use to specify the address while adding a location. */
export interface LocationAddAddressInput {
  address1?: string;
  address2?: string;
  city?: string;
  countryCode: CountryCode;
  phone?: string;
  provinceCode?: string;
  zip?: string;
}

/** The input fields to use to add a location. */
export interface LocationAddInput {
  address: LocationAddAddressInput;
  fulfillsOnlineOrders?: boolean;
  metafields?: MetafieldInput[];
  name: string;
}

/** The input fields to use to edit the address of a location. */
export interface LocationEditAddressInput {
  address1?: string;
  address2?: string;
  city?: string;
  countryCode?: CountryCode;
  phone?: string;
  provinceCode?: string;
  zip?: string;
}

/** The input fields to use to edit a location. */
export interface LocationEditInput {
  address?: LocationEditAddressInput;
  fulfillsOnlineOrders?: boolean;
  metafields?: MetafieldInput[];
  name?: string;
}

/** The input fields for identifying a location. */
export interface LocationIdentifierInput {
  customId?: UniqueMetafieldValueInput;
  id?: string;
}

/** The input fields to create or update a mailing address. */
export interface MailingAddressInput {
  address1?: string;
  address2?: string;
  city?: string;
  company?: string;
  countryCode?: CountryCode;
  firstName?: string;
  lastName?: string;
  phone?: string;
  provinceCode?: string;
  zip?: string;
  country?: string;
  id?: string;
  province?: string;
}

/** The input fields required to create or update a company location market condition. */
export interface MarketConditionsCompanyLocationsInput {
  applicationLevel?: MarketConditionApplicationType;
  companyLocationIds?: string[];
}

/** The input fields required to create or update the market conditions. */
export interface MarketConditionsInput {
  companyLocationsCondition?: MarketConditionsCompanyLocationsInput;
  locationsCondition?: MarketConditionsLocationsInput;
  regionsCondition?: MarketConditionsRegionsInput;
}

/** The input fields required to create or update a location market condition. */
export interface MarketConditionsLocationsInput {
  applicationLevel?: MarketConditionApplicationType;
  locationIds?: string[];
}

/** The input fields to specify a region condition. */
export interface MarketConditionsRegionInput {
  countryCode: CountryCode;
}

/** The input fields required to create or update a region market condition. */
export interface MarketConditionsRegionsInput {
  applicationLevel?: MarketConditionApplicationType;
  regionIds?: string[];
  regions?: MarketConditionsRegionInput[];
}

/** The input fields required to update a market condition. */
export interface MarketConditionsUpdateInput {
  conditionsToAdd?: MarketConditionsInput;
  conditionsToDelete?: MarketConditionsInput;
}

/** The input fields required to create a market. */
export interface MarketCreateInput {
  catalogs?: string[];
  conditions?: MarketConditionsInput;
  currencySettings?: MarketCurrencySettingsUpdateInput;
  handle?: string;
  makeDuplicateUniqueMarketsDraft?: boolean;
  name: string;
  priceInclusions?: MarketPriceInclusionsInput;
  status?: MarketStatus;
  webPresences?: string[];
  enabled?: boolean;
  makeDuplicateRegionMarketsDraft?: boolean;
  regions?: MarketRegionCreateInput[];
}

/** The input fields used to update the currency settings of a market. */
export interface MarketCurrencySettingsUpdateInput {
  baseCurrency?: CurrencyCode;
  baseCurrencyManualRate?: string;
  localCurrencies?: boolean;
  roundingEnabled?: boolean;
}

/** The input fields combining budget amount and its marketing budget type. */
export interface MarketingActivityBudgetInput {
  budgetType?: MarketingBudgetBudgetType;
  total?: MoneyInput;
}

/** The input fields for creating an externally-managed marketing activity. */
export interface MarketingActivityCreateExternalInput {
  adSpend?: MoneyInput;
  budget?: MarketingActivityBudgetInput;
  channelHandle?: string;
  end?: string;
  hierarchyLevel?: MarketingActivityHierarchyLevel;
  marketingChannelType: MarketingChannel;
  parentActivityId?: string;
  parentRemoteId?: string;
  referringDomain?: string;
  remoteId?: string;
  remotePreviewImageUrl?: string;
  remoteUrl: string;
  scheduledEnd?: string;
  scheduledStart?: string;
  start?: string;
  status?: MarketingActivityExternalStatus;
  tactic: MarketingTactic;
  title: string;
  urlParameterValue?: string;
  utm?: UTMInput;
  channel?: MarketingChannel;
}

/** The input fields required to create a marketing activity. Marketing activity app extensions are deprecated and will be removed in the near future. */
export interface MarketingActivityCreateInput {
  marketingActivityExtensionId: string;
  status: MarketingActivityStatus;
  budget?: MarketingActivityBudgetInput;
  context?: string;
  formData?: string;
  marketingActivityTitle?: string;
  urlParameterValue?: string;
  utm?: UTMInput;
}

/** The input fields required to update an externally managed marketing activity. */
export interface MarketingActivityUpdateExternalInput {
  adSpend?: MoneyInput;
  budget?: MarketingActivityBudgetInput;
  end?: string;
  marketingChannelType?: MarketingChannel;
  referringDomain?: string;
  remotePreviewImageUrl?: string;
  remoteUrl?: string;
  scheduledEnd?: string;
  scheduledStart?: string;
  start?: string;
  status?: MarketingActivityExternalStatus;
  tactic?: MarketingTactic;
  title?: string;
  channel?: MarketingChannel;
}

/** The input fields required to update a marketing activity. Marketing activity app extensions are deprecated and will be removed in the near future. */
export interface MarketingActivityUpdateInput {
  id: string;
  adSpend?: MoneyInput;
  budget?: MarketingActivityBudgetInput;
  context?: string;
  errors?: unknown;
  formData?: string;
  marketedResources?: string[];
  marketingRecommendationId?: string;
  status?: MarketingActivityStatus;
  targetStatus?: MarketingActivityStatus;
  title?: string;
  urlParameterValue?: string;
  utm?: UTMInput;
}

/** The input fields for creating or updating an externally-managed marketing activity. */
export interface MarketingActivityUpsertExternalInput {
  adSpend?: MoneyInput;
  budget?: MarketingActivityBudgetInput;
  channelHandle?: string;
  end?: string;
  hierarchyLevel?: MarketingActivityHierarchyLevel;
  marketingChannelType: MarketingChannel;
  parentRemoteId?: string;
  referringDomain?: string;
  remoteId: string;
  remotePreviewImageUrl?: string;
  remoteUrl: string;
  scheduledEnd?: string;
  scheduledStart?: string;
  start?: string;
  status: MarketingActivityExternalStatus;
  tactic: MarketingTactic;
  title: string;
  urlParameterValue?: string;
  utm?: UTMInput;
}

/** The input fields for a marketing engagement. */
export interface MarketingEngagementInput {
  adSpend?: MoneyInput;
  allConversions?: string;
  clicksCount?: number;
  commentsCount?: number;
  complaintsCount?: number;
  failsCount?: number;
  favoritesCount?: number;
  firstTimeCustomers?: string;
  impressionsCount?: number;
  isCumulative: boolean;
  occurredOn: string;
  orders?: string;
  primaryConversions?: string;
  returningCustomers?: string;
  sales?: MoneyInput;
  sendsCount?: number;
  sessionsCount?: number;
  sharesCount?: number;
  uniqueClicksCount?: number;
  uniqueViewsCount?: number;
  unsubscribesCount?: number;
  utcOffset: string;
  viewsCount?: number;
}

/** The input fields and values for creating or updating a market localization. */
export interface MarketLocalizationRegisterInput {
  key: string;
  marketId: string;
  marketLocalizableContentDigest: string;
  value: string;
}

/** The input fields used to create a price inclusion. */
export interface MarketPriceInclusionsInput {
  dutiesPricingStrategy?: InclusiveDutiesPricingStrategy;
  taxPricingStrategy?: InclusiveTaxPricingStrategy;
}

/** The input fields for creating a market region with exactly one required option. */
export interface MarketRegionCreateInput {
  countryCode: CountryCode;
}

/** The input fields used to update a market. */
export interface MarketUpdateInput {
  catalogsToAdd?: string[];
  catalogsToDelete?: string[];
  conditions?: MarketConditionsUpdateInput;
  currencySettings?: MarketCurrencySettingsUpdateInput;
  handle?: string;
  makeDuplicateUniqueMarketsDraft?: boolean;
  name?: string;
  priceInclusions?: MarketPriceInclusionsInput;
  removeCurrencySettings?: boolean;
  removePriceInclusions?: boolean;
  status?: MarketStatus;
  webPresencesToAdd?: string[];
  webPresencesToDelete?: string[];
  enabled?: boolean;
  makeDuplicateRegionMarketsDraft?: boolean;
}

/** The input fields used to create a web presence for a market. */
export interface MarketWebPresenceCreateInput {
  alternateLocales?: string[];
  defaultLocale: string;
  domainId?: string;
  subfolderSuffix?: string;
}

/** The input fields used to update a web presence for a market. */
export interface MarketWebPresenceUpdateInput {
  alternateLocales?: string[];
  defaultLocale?: string;
  domainId?: string;
  subfolderSuffix?: string;
}

/** The input fields required to create a valid menu item. */
export interface MenuItemCreateInput {
  items?: MenuItemCreateInput[];
  resourceId?: string;
  tags?: string[];
  title: string;
  type: MenuItemType;
  url?: string;
}

/** The input fields required to update a valid menu item. */
export interface MenuItemUpdateInput {
  id?: string;
  items?: MenuItemUpdateInput[];
  resourceId?: string;
  tags?: string[];
  title: string;
  type: MenuItemType;
  url?: string;
}

/** The input fields that set access permissions for the definition's metafields. */
export interface MetafieldAccessInput {
  admin?: MetafieldAdminAccessInput;
  customerAccount?: MetafieldCustomerAccountAccessInput;
  storefront?: MetafieldStorefrontAccessInput;
}

/** The input fields for the access settings for the metafields under the definition. */
export interface MetafieldAccessUpdateInput {
  admin?: MetafieldAdminAccessInput;
  customerAccount?: MetafieldCustomerAccountAccessInput;
  storefront?: MetafieldStorefrontAccessInput;
}

/** The input fields for enabling and disabling the admin filterable capability. */
export interface MetafieldCapabilityAdminFilterableInput {
  enabled: boolean;
}

/** The input fields for the analytics queryable capability. */
export interface MetafieldCapabilityAnalyticsQueryableInput {
  enabled: boolean;
}

/** The input fields for enabling or disabling the 'Cart to order copyable' capability. This capability is only available for order metafield definitions. */
export interface MetafieldCapabilityCartToOrderCopyableInput {
  enabled: boolean;
}

/** The input fields for creating a metafield capability. */
export interface MetafieldCapabilityCreateInput {
  adminFilterable?: MetafieldCapabilityAdminFilterableInput;
  analyticsQueryable?: MetafieldCapabilityAnalyticsQueryableInput;
  cartToOrderCopyable?: MetafieldCapabilityCartToOrderCopyableInput;
  smartCollectionCondition?: MetafieldCapabilitySmartCollectionConditionInput;
  uniqueValues?: MetafieldCapabilityUniqueValuesInput;
}

/** The input fields for enabling and disabling the smart collection condition capability. */
export interface MetafieldCapabilitySmartCollectionConditionInput {
  enabled: boolean;
}

/** The input fields for enabling and disabling the unique values capability. */
export interface MetafieldCapabilityUniqueValuesInput {
  enabled: boolean;
}

/** The input fields for updating a metafield capability. */
export interface MetafieldCapabilityUpdateInput {
  adminFilterable?: MetafieldCapabilityAdminFilterableInput;
  analyticsQueryable?: MetafieldCapabilityAnalyticsQueryableInput;
  cartToOrderCopyable?: MetafieldCapabilityCartToOrderCopyableInput;
  smartCollectionCondition?: MetafieldCapabilitySmartCollectionConditionInput;
  uniqueValues?: MetafieldCapabilityUniqueValuesInput;
}

/** The input fields required to create metafield definition [constraints](https://shopify.dev/apps/build/custom-data/metafields/conditional-metafield-definitions). Each constraint applies a metafield definition to a subtype of a resource. */
export interface MetafieldDefinitionConstraintsInput {
  key: string;
  values: string[];
}

/** The input fields used to identify a subtype of a resource for the purposes of metafield definition constraints. */
export interface MetafieldDefinitionConstraintSubtypeIdentifier {
  key: string;
  value: string;
}

/** The input fields required to update metafield definition [constraints](https://shopify.dev/apps/build/custom-data/metafields/conditional-metafield-definitions). Each constraint applies a metafield definition to a subtype of a resource. */
export interface MetafieldDefinitionConstraintsUpdatesInput {
  key?: string;
  values?: MetafieldDefinitionConstraintValueUpdateInput[];
}

/** The inputs fields for modifying a metafield definition's constraint subtype values. Exactly one option is required. */
export interface MetafieldDefinitionConstraintValueUpdateInput {
  create?: string;
  delete?: string;
}

/** The input fields that identify metafield definitions. */
export interface MetafieldDefinitionIdentifierInput {
  key: string;
  namespace?: string;
  ownerType: MetafieldOwnerType;
}

/** The input fields required to create a metafield definition. */
export interface MetafieldDefinitionInput {
  access?: MetafieldAccessInput;
  capabilities?: MetafieldCapabilityCreateInput;
  constraints?: MetafieldDefinitionConstraintsInput;
  description?: string;
  key: string;
  name: string;
  namespace?: string;
  ownerType: MetafieldOwnerType;
  pin?: boolean;
  type: string;
  validations?: MetafieldDefinitionValidationInput[];
  useAsCollectionCondition?: boolean;
}

/** The input fields required to update a metafield definition. */
export interface MetafieldDefinitionUpdateInput {
  access?: MetafieldAccessUpdateInput;
  capabilities?: MetafieldCapabilityUpdateInput;
  constraintsUpdates?: MetafieldDefinitionConstraintsUpdatesInput;
  description?: string;
  key: string;
  name?: string;
  namespace?: string;
  ownerType: MetafieldOwnerType;
  pin?: boolean;
  validations?: MetafieldDefinitionValidationInput[];
  useAsCollectionCondition?: boolean;
}

/** The name and value for a metafield definition validation. */
export interface MetafieldDefinitionValidationInput {
  name: string;
  value: string;
}

/** The input fields that identify metafields. */
export interface MetafieldIdentifierInput {
  key: string;
  namespace: string;
  ownerId: string;
}

/** The input fields to use to create or update a metafield through a mutation on the owning resource. An alternative way to create or update a metafield is by using the [metafieldsSet](https://shopify.dev/api/admin-graphql/latest/mutations/metafieldsSet) mutation. */
export interface MetafieldInput {
  id?: string;
  key?: string;
  namespace?: string;
  type?: string;
  value?: string;
}

/** The input fields for a metafield value to set. */
export interface MetafieldsSetInput {
  compareDigest?: string;
  key: string;
  namespace?: string;
  ownerId: string;
  type?: string;
  value: string;
}

/** The input fields that set access permissions for the definition's metaobjects. */
export interface MetaobjectAccessInput {
  admin?: MetaobjectAdminAccessInput;
  customerAccount?: MetaobjectCustomerAccountAccess;
  storefront?: MetaobjectStorefrontAccess;
}

/** Specifies the condition by which metaobjects are deleted. Exactly one field of input is required. */
export interface MetaobjectBulkDeleteWhereCondition {
  ids?: string[];
  type?: string;
}

/** The input fields for creating a metaobject capability. */
export interface MetaobjectCapabilityCreateInput {
  onlineStore?: MetaobjectCapabilityOnlineStoreInput;
  publishable?: MetaobjectCapabilityPublishableInput;
  renderable?: MetaobjectCapabilityRenderableInput;
  translatable?: MetaobjectCapabilityTranslatableInput;
}

/** The input fields for metaobject capabilities. */
export interface MetaobjectCapabilityDataInput {
  onlineStore?: MetaobjectCapabilityDataOnlineStoreInput;
  publishable?: MetaobjectCapabilityDataPublishableInput;
}

/** The input fields for the Online Store capability to control renderability on the Online Store. */
export interface MetaobjectCapabilityDataOnlineStoreInput {
  templateSuffix?: string;
}

/** The input fields for publishable capability to adjust visibility on channels. */
export interface MetaobjectCapabilityDataPublishableInput {
  status: MetaobjectStatus;
}

/** The input fields of the Online Store capability. */
export interface MetaobjectCapabilityDefinitionDataOnlineStoreInput {
  createRedirects?: boolean;
  urlHandle: string;
}

/** The input fields of the renderable capability for SEO aliases. */
export interface MetaobjectCapabilityDefinitionDataRenderableInput {
  metaDescriptionKey?: string;
  metaTitleKey?: string;
}

/** The input fields for enabling and disabling the Online Store capability. */
export interface MetaobjectCapabilityOnlineStoreInput {
  data?: MetaobjectCapabilityDefinitionDataOnlineStoreInput;
  enabled: boolean;
}

/** The input fields for enabling and disabling the publishable capability. */
export interface MetaobjectCapabilityPublishableInput {
  enabled: boolean;
}

/** The input fields for enabling and disabling the renderable capability. */
export interface MetaobjectCapabilityRenderableInput {
  data?: MetaobjectCapabilityDefinitionDataRenderableInput;
  enabled: boolean;
}

/** The input fields for enabling and disabling the translatable capability. */
export interface MetaobjectCapabilityTranslatableInput {
  enabled: boolean;
}

/** The input fields for updating a metaobject capability. */
export interface MetaobjectCapabilityUpdateInput {
  onlineStore?: MetaobjectCapabilityOnlineStoreInput;
  publishable?: MetaobjectCapabilityPublishableInput;
  renderable?: MetaobjectCapabilityRenderableInput;
  translatable?: MetaobjectCapabilityTranslatableInput;
}

/** The input fields for creating a metaobject. */
export interface MetaobjectCreateInput {
  capabilities?: MetaobjectCapabilityDataInput;
  fields?: MetaobjectFieldInput[];
  handle?: string;
  type: string;
}

/** The input fields for creating a metaobject definition. */
export interface MetaobjectDefinitionCreateInput {
  access?: MetaobjectAccessInput;
  capabilities?: MetaobjectCapabilityCreateInput;
  description?: string;
  displayNameKey?: string;
  fieldDefinitions?: MetaobjectFieldDefinitionCreateInput[];
  name?: string;
  type: string;
}

/** The input fields for updating a metaobject definition. */
export interface MetaobjectDefinitionUpdateInput {
  access?: MetaobjectAccessInput;
  capabilities?: MetaobjectCapabilityUpdateInput;
  description?: string;
  displayNameKey?: string;
  fieldDefinitions?: MetaobjectFieldDefinitionOperationInput[];
  name?: string;
  resetFieldOrder?: boolean;
}

/** The input fields for enabling and disabling the admin filterable capability. */
export interface MetaobjectFieldCapabilityAdminFilterableInput {
  enabled: boolean;
}

/** The input fields for creating capabilities on a metaobject field definition. */
export interface MetaobjectFieldDefinitionCapabilityCreateInput {
  adminFilterable?: MetaobjectFieldCapabilityAdminFilterableInput;
}

/** The input fields for creating a metaobject field definition. */
export interface MetaobjectFieldDefinitionCreateInput {
  capabilities?: MetaobjectFieldDefinitionCapabilityCreateInput;
  description?: string;
  key: string;
  name?: string;
  required?: boolean;
  type: string;
  validations?: MetafieldDefinitionValidationInput[];
}

/** The input fields for deleting a metaobject field definition. */
export interface MetaobjectFieldDefinitionDeleteInput {
  key: string;
}

/** The input fields for possible operations for modifying field definitions. Exactly one option is required. */
export interface MetaobjectFieldDefinitionOperationInput {
  create?: MetaobjectFieldDefinitionCreateInput;
  delete?: MetaobjectFieldDefinitionDeleteInput;
  update?: MetaobjectFieldDefinitionUpdateInput;
}

/** The input fields for updating a metaobject field definition. */
export interface MetaobjectFieldDefinitionUpdateInput {
  capabilities?: MetaobjectFieldDefinitionCapabilityCreateInput;
  description?: string;
  key: string;
  name?: string;
  required?: boolean;
  validations?: MetafieldDefinitionValidationInput[];
}

/** The input fields for a metaobject field value. */
export interface MetaobjectFieldInput {
  key: string;
  value: string;
}

/** The input fields for retrieving a metaobject by handle. */
export interface MetaobjectHandleInput {
  handle: string;
  type: string;
}

/** The input fields for updating a metaobject. */
export interface MetaobjectUpdateInput {
  capabilities?: MetaobjectCapabilityDataInput;
  fields?: MetaobjectFieldInput[];
  handle?: string;
  redirectNewHandle?: boolean;
}

/** The input fields for upserting a metaobject. */
export interface MetaobjectUpsertInput {
  capabilities?: MetaobjectCapabilityDataInput;
  fields?: MetaobjectFieldInput[];
  handle?: string;
}

/** The input fields for an Android based mobile platform application. */
export interface MobilePlatformApplicationCreateAndroidInput {
  applicationId?: string;
  appLinksEnabled: boolean;
  sha256CertFingerprints: string[];
}

/** The input fields for an Apple based mobile platform application. */
export interface MobilePlatformApplicationCreateAppleInput {
  appClipApplicationId?: string;
  appClipsEnabled?: boolean;
  appId?: string;
  sharedWebCredentialsEnabled: boolean;
  universalLinksEnabled: boolean;
}

/** The input fields for a mobile application platform type. */
export interface MobilePlatformApplicationCreateInput {
  android?: MobilePlatformApplicationCreateAndroidInput;
  apple?: MobilePlatformApplicationCreateAppleInput;
}

/** The input fields for an Android based mobile platform application. */
export interface MobilePlatformApplicationUpdateAndroidInput {
  applicationId?: string;
  appLinksEnabled?: boolean;
  sha256CertFingerprints?: string[];
}

/** The input fields for an Apple based mobile platform application. */
export interface MobilePlatformApplicationUpdateAppleInput {
  appClipApplicationId?: string;
  appClipsEnabled?: boolean;
  appId?: string;
  sharedWebCredentialsEnabled?: boolean;
  universalLinksEnabled?: boolean;
}

/** The input fields for the mobile platform application platform type. */
export interface MobilePlatformApplicationUpdateInput {
  android?: MobilePlatformApplicationUpdateAndroidInput;
  apple?: MobilePlatformApplicationUpdateAppleInput;
}

/** An input collection of monetary values in their respective currencies. Represents an amount in the shop's currency and the amount as converted to the customer's currency of choice (the presentment currency). */
export interface MoneyBagInput {
  presentmentMoney?: MoneyInput;
  shopMoney: MoneyInput;
}

/** The input fields for a monetary value with currency. */
export interface MoneyInput {
  amount: string;
  currencyCode: CurrencyCode;
}

/** The input for moving a single object to a specific position in a set. */
export interface MoveInput {
  id: string;
  newPosition: string;
}

/** The input fields for dimensions of an object. */
export interface ObjectDimensionsInput {
  height: number;
  length: number;
  unit: LengthUnit;
  width: number;
}

/** The input fields for the theme file body. */
export interface OnlineStoreThemeFileBodyInput {
  type: OnlineStoreThemeFileBodyInputType;
  value: string;
}

/** The input fields for the file to create or update. */
export interface OnlineStoreThemeFilesUpsertFileInput {
  body: OnlineStoreThemeFileBodyInput;
  filename: string;
}

/** The input fields for Theme attributes to update. */
export interface OnlineStoreThemeInput {
  name?: string;
}

/** The input fields for the options and values of the combined listing. */
export interface OptionAndValueInput {
  linkedMetafield?: LinkedMetafieldInput;
  name: string;
  optionId?: string;
  values: string[];
}

/** The input fields for creating a product option. */
export interface OptionCreateInput {
  linkedMetafield?: LinkedMetafieldCreateInput;
  name?: string;
  position?: number;
  values?: OptionValueCreateInput[];
}

/** The input fields for reordering a product option and/or its values. */
export interface OptionReorderInput {
  id?: string;
  name?: string;
  values?: OptionValueReorderInput[];
}

/** The input fields for creating or updating a product option. */
export interface OptionSetInput {
  id?: string;
  linkedMetafield?: LinkedMetafieldCreateInput;
  name?: string;
  position?: number;
  values?: OptionValueSetInput[];
}

/** The input fields for updating a product option. */
export interface OptionUpdateInput {
  id: string;
  linkedMetafield?: LinkedMetafieldUpdateInput;
  name?: string;
  position?: number;
}

/** The input fields required to create a product option value. */
export interface OptionValueCreateInput {
  linkedMetafieldValue?: string;
  name?: string;
}

/** The input fields for reordering a product option value. */
export interface OptionValueReorderInput {
  id?: string;
  name?: string;
}

/** The input fields for creating or updating a product option value. */
export interface OptionValueSetInput {
  id?: string;
  name?: string;
}

/** The input fields for updating a product option value. */
export interface OptionValueUpdateInput {
  id: string;
  linkedMetafieldValue?: string;
  name?: string;
}

/** The input fields used to specify the refund method for an order cancellation. */
export interface OrderCancelRefundMethodInput {
  originalPaymentMethodsRefund?: boolean;
  storeCreditRefund?: OrderCancelStoreCreditRefundInput;
}

/** The input fields used to refund to store credit. */
export interface OrderCancelStoreCreditRefundInput {
  expiresAt?: string;
}

/** The input fields for the authorized transaction to capture and the total amount to capture from it. */
export interface OrderCaptureInput {
  amount: string;
  currency?: CurrencyCode;
  finalCapture?: boolean;
  id: string;
  parentTransactionId: string;
}

/** The input fields for specifying an open order to close. */
export interface OrderCloseInput {
  id: string;
}

/** The input fields for identifying an existing customer to associate with the order. */
export interface OrderCreateAssociateCustomerAttributesInput {
  email?: string;
  id?: string;
}

/** The input fields for a note attribute for an order. */
export interface OrderCreateCustomAttributeInput {
  key: string;
  value: string;
}

/** The input fields for creating a customer's mailing address. */
export interface OrderCreateCustomerAddressInput {
  address1?: string;
  address2?: string;
  city?: string;
  company?: string;
  country?: string;
  firstName?: string;
  lastName?: string;
  phone?: string;
  province?: string;
  zip?: string;
}

/** The input fields for a customer to associate with an order. Allows creation of a new customer or specifying an existing one. */
export interface OrderCreateCustomerInput {
  toAssociate?: OrderCreateAssociateCustomerAttributesInput;
  toUpsert?: OrderCreateUpsertCustomerAttributesInput;
}

/** The input fields for a discount code to apply to an order. Only one type of discount can be applied to an order. */
export interface OrderCreateDiscountCodeInput {
  freeShippingDiscountCode?: OrderCreateFreeShippingDiscountCodeAttributesInput;
  itemFixedDiscountCode?: OrderCreateFixedDiscountCodeAttributesInput;
  itemPercentageDiscountCode?: OrderCreatePercentageDiscountCodeAttributesInput;
}

/** The input fields for a fixed amount discount code to apply to an order. */
export interface OrderCreateFixedDiscountCodeAttributesInput {
  amountSet?: MoneyBagInput;
  code: string;
}

/** The input fields for a free shipping discount code to apply to an order. */
export interface OrderCreateFreeShippingDiscountCodeAttributesInput {
  code: string;
}

/** The input fields for a fulfillment to create for an order. */
export interface OrderCreateFulfillmentInput {
  locationId: string;
  notifyCustomer?: boolean;
  originAddress?: FulfillmentOriginAddressInput;
  shipmentStatus?: FulfillmentEventStatus;
  trackingCompany?: string;
  trackingNumber?: string;
}

/** The input fields for a line item to create for an order. */
export interface OrderCreateLineItemInput {
  fulfillmentService?: string;
  giftCard?: boolean;
  priceSet?: MoneyBagInput;
  productId?: string;
  properties?: OrderCreateLineItemPropertyInput[];
  quantity: number;
  requiresShipping?: boolean;
  sku?: string;
  taxable?: boolean;
  taxLines?: OrderCreateTaxLineInput[];
  title?: string;
  variantId?: string;
  variantTitle?: string;
  vendor?: string;
  weight?: WeightInput;
}

/** The input fields for a line item property for an order. */
export interface OrderCreateLineItemPropertyInput {
  name: string;
  value: string;
}

/** The input fields that define the strategies for updating inventory and whether to send shipping and order confirmations to customers. */
export interface OrderCreateOptionsInput {
  inventoryBehaviour?: OrderCreateInputsInventoryBehavior;
  sendFulfillmentReceipt?: boolean;
  sendReceipt?: boolean;
}

/** The input fields for creating an order. */
export interface OrderCreateOrderInput {
  billingAddress?: MailingAddressInput;
  buyerAcceptsMarketing?: boolean;
  closedAt?: string;
  companyLocationId?: string;
  currency?: CurrencyCode;
  customAttributes?: OrderCreateCustomAttributeInput[];
  customer?: OrderCreateCustomerInput;
  discountCode?: OrderCreateDiscountCodeInput;
  email?: string;
  financialStatus?: OrderCreateFinancialStatus;
  fulfillment?: OrderCreateFulfillmentInput;
  fulfillmentStatus?: OrderCreateFulfillmentStatus;
  lineItems?: OrderCreateLineItemInput[];
  metafields?: MetafieldInput[];
  name?: string;
  note?: string;
  phone?: string;
  poNumber?: string;
  presentmentCurrency?: CurrencyCode;
  processedAt?: string;
  referringSite?: string;
  shippingAddress?: MailingAddressInput;
  shippingLines?: OrderCreateShippingLineInput[];
  sourceIdentifier?: string;
  sourceName?: string;
  sourceUrl?: string;
  tags?: string[];
  taxesIncluded?: boolean;
  taxLines?: OrderCreateTaxLineInput[];
  test?: boolean;
  transactions?: OrderCreateOrderTransactionInput[];
  userId?: string;
  customerId?: string;
}

/** The input fields for a transaction to create for an order. */
export interface OrderCreateOrderTransactionInput {
  amountSet: MoneyBagInput;
  authorizationCode?: string;
  deviceId?: string;
  gateway?: string;
  giftCardId?: string;
  kind?: OrderTransactionKind;
  locationId?: string;
  processedAt?: string;
  receiptJson?: unknown;
  status?: OrderTransactionStatus;
  test?: boolean;
  userId?: string;
}

/** The input fields for a percentage discount code to apply to an order. */
export interface OrderCreatePercentageDiscountCodeAttributesInput {
  code: string;
  percentage?: number;
}

/** The input fields for a shipping line to create for an order. */
export interface OrderCreateShippingLineInput {
  code?: string;
  priceSet: MoneyBagInput;
  source?: string;
  taxLines?: OrderCreateTaxLineInput[];
  title: string;
}

/** The input fields for a tax line to create for an order. */
export interface OrderCreateTaxLineInput {
  channelLiable?: boolean;
  priceSet?: MoneyBagInput;
  rate: string;
  title: string;
}

/** The input fields for creating a new customer object or identifying an existing customer to update & associate with the order. */
export interface OrderCreateUpsertCustomerAttributesInput {
  addresses?: OrderCreateCustomerAddressInput[];
  email?: string;
  firstName?: string;
  id?: string;
  lastName?: string;
  multipassIdentifier?: string;
  note?: string;
  phone?: string;
  tags?: string[];
  taxExempt?: boolean;
}

/** The input fields used to add a shipping line. */
export interface OrderEditAddShippingLineInput {
  price: MoneyInput;
  title: string;
}

/** The input fields used to add a discount during an order edit. */
export interface OrderEditAppliedDiscountInput {
  description?: string;
  fixedValue?: MoneyInput;
  percentValue?: number;
}

/** The input fields used to update a shipping line. */
export interface OrderEditUpdateShippingLineInput {
  price?: MoneyInput;
  title?: string;
}

/** The input fields for identifying a order. */
export interface OrderIdentifierInput {
  customId?: UniqueMetafieldValueInput;
  id?: string;
}

/** The input fields for specifying the information to be updated on an order when using the orderUpdate mutation. */
export interface OrderInput {
  customAttributes?: AttributeInput[];
  email?: string;
  id: string;
  localizedFields?: LocalizedFieldInput[];
  metafields?: MetafieldInput[];
  note?: string;
  phone?: string;
  poNumber?: string;
  shippingAddress?: MailingAddressInput;
  tags?: string[];
  localizationExtensions?: LocalizationExtensionInput[];
}

/** The input fields for specifying the order to mark as paid. */
export interface OrderMarkAsPaidInput {
  id: string;
}

/** The input fields for specifying a closed order to open. */
export interface OrderOpenInput {
  id: string;
}

/** The input fields for an order risk assessment. */
export interface OrderRiskAssessmentCreateInput {
  facts: OrderRiskAssessmentFactInput[];
  orderId: string;
  riskLevel: RiskAssessmentResult;
}

/** The input fields to create a fact on an order risk assessment. */
export interface OrderRiskAssessmentFactInput {
  description: string;
  sentiment: RiskFactSentiment;
}

/** The input fields for the information needed to create an order transaction. */
export interface OrderTransactionInput {
  amount: string;
  gateway: string;
  kind: OrderTransactionKind;
  orderId: string;
  parentId?: string;
}

/** The input fields to create a page. */
export interface PageCreateInput {
  body?: string;
  handle?: string;
  isPublished?: boolean;
  metafields?: MetafieldInput[];
  publishDate?: string;
  templateSuffix?: string;
  title: string;
}

/** The input fields to update a page. */
export interface PageUpdateInput {
  body?: string;
  handle?: string;
  isPublished?: boolean;
  metafields?: MetafieldInput[];
  publishDate?: string;
  redirectNewHandle?: boolean;
  templateSuffix?: string;
  title?: string;
}

/** The input fields to create and update a payment customization. */
export interface PaymentCustomizationInput {
  enabled?: boolean;
  functionHandle?: string;
  metafields?: MetafieldInput[];
  title?: string;
  functionId?: string;
}

/** The input fields used to create a payment schedule for payment terms. */
export interface PaymentScheduleInput {
  dueAt?: string;
  issuedAt?: string;
}

/** The input fields used to create a payment terms. */
export interface PaymentTermsCreateInput {
  paymentSchedules?: PaymentScheduleInput[];
  paymentTermsTemplateId: string;
}

/** The input fields used to delete the payment terms. */
export interface PaymentTermsDeleteInput {
  paymentTermsId: string;
}

/** The input fields to create payment terms. Payment terms set the date that payment is due. */
export interface PaymentTermsInput {
  paymentSchedules?: PaymentScheduleInput[];
  paymentTermsTemplateId?: string;
}

/** The input fields used to update the payment terms. */
export interface PaymentTermsUpdateInput {
  paymentTermsAttributes: PaymentTermsInput;
  paymentTermsId: string;
}

/** The input fields used to include the line items of a specified fulfillment order that should be marked as prepared for pickup by a customer. */
export interface PreparedFulfillmentOrderLineItemsInput {
  fulfillmentOrderId: string;
}

/** The input fields for updating the price of a parent product variant. */
export interface PriceInput {
  calculation?: PriceCalculationType;
  price?: string;
}

/** The input fields to set a price list adjustment. */
export interface PriceListAdjustmentInput {
  type: PriceListAdjustmentType;
  value: number;
}

/** The input fields to set a price list's adjustment settings. */
export interface PriceListAdjustmentSettingsInput {
  compareAtMode?: PriceListCompareAtMode;
}

/** The input fields to create a price list. */
export interface PriceListCreateInput {
  catalogId?: string;
  currency: CurrencyCode;
  name: string;
  parent: PriceListParentCreateInput;
}

/** The input fields to create a price list adjustment. */
export interface PriceListParentCreateInput {
  adjustment: PriceListAdjustmentInput;
  settings?: PriceListAdjustmentSettingsInput;
}

/** The input fields used to update a price list's adjustment. */
export interface PriceListParentUpdateInput {
  adjustment: PriceListAdjustmentInput;
  settings?: PriceListAdjustmentSettingsInput;
}

/** The input fields for providing the fields and values to use when creating or updating a fixed price list price. */
export interface PriceListPriceInput {
  compareAtPrice?: MoneyInput;
  price: MoneyInput;
  variantId: string;
}

/** The input fields representing the price for all variants of a product. */
export interface PriceListProductPriceInput {
  compareAtPrice?: MoneyInput;
  price: MoneyInput;
  productId: string;
}

/** The input fields used to update a price list. */
export interface PriceListUpdateInput {
  catalogId?: string;
  currency?: CurrencyCode;
  name?: string;
  parent?: PriceListParentUpdateInput;
}

/** The input fields for a single component related to a componentized product. */
export interface ProductBundleComponentInput {
  optionSelections: ProductBundleComponentOptionSelectionInput[];
  productId: string;
  quantity?: number;
  quantityOption?: ProductBundleComponentQuantityOptionInput;
}

/** The input fields for a single option related to a component product. */
export interface ProductBundleComponentOptionSelectionInput {
  componentOptionId: string;
  name: string;
  values: string[];
}

/** Input for the quantity option related to a component product. This will become a new option on the parent bundle product that doesn't have a corresponding option on the component. */
export interface ProductBundleComponentQuantityOptionInput {
  name: string;
  values: ProductBundleComponentQuantityOptionValueInput[];
}

/** The input fields for a single quantity option value related to a component product. */
export interface ProductBundleComponentQuantityOptionValueInput {
  name: string;
  quantity: number;
}

/** The input fields for mapping a consolidated option to a specific component option. */
export interface ProductBundleConsolidatedOptionComponentInput {
  componentOptionId?: string;
  componentOptionValue: string;
}

/** The input fields for a consolidated option on a componentized product. */
export interface ProductBundleConsolidatedOptionInput {
  optionName: string;
  optionSelections: ProductBundleConsolidatedOptionSelectionInput[];
}

/** The input fields for a consolidated option selection that maps to component options. */
export interface ProductBundleConsolidatedOptionSelectionInput {
  components: ProductBundleConsolidatedOptionComponentInput[];
  optionValue: string;
}

/** The input fields for creating a componentized product. */
export interface ProductBundleCreateInput {
  components: ProductBundleComponentInput[];
  consolidatedOptions?: ProductBundleConsolidatedOptionInput[];
  title: string;
}

/** The input fields for updating a componentized product. */
export interface ProductBundleUpdateInput {
  components?: ProductBundleComponentInput[];
  consolidatedOptions?: ProductBundleConsolidatedOptionInput[];
  productId: string;
  title?: string;
}

/** The input fields to claim ownership for Product features such as Bundles. */
export interface ProductClaimOwnershipInput {
  bundles?: boolean;
}

/** The input fields required to create a product. */
export interface ProductCreateInput {
  category?: string;
  claimOwnership?: ProductClaimOwnershipInput;
  collectionsToJoin?: string[];
  combinedListingRole?: CombinedListingsRole;
  descriptionHtml?: string;
  giftCard?: boolean;
  giftCardTemplateSuffix?: string;
  handle?: string;
  metafields?: MetafieldInput[];
  productOptions?: OptionCreateInput[];
  productType?: string;
  requiresSellingPlan?: boolean;
  seo?: SEOInput;
  status?: ProductStatus;
  tags?: string[];
  templateSuffix?: string;
  title?: string;
  vendor?: string;
}

/** The input fields for specifying the product to delete. */
export interface ProductDeleteInput {
  id: string;
}

/** Controls which product discounts can apply together on the same cart line. By default, only one product discount applies per line. Available only on a Shopify Plus plan. */
export interface ProductDiscountsWithTagsOnSameCartLineInput {
  add?: string[];
  remove?: string[];
}

/** The input fields required to create a product feed. */
export interface ProductFeedInput {
  channelId?: string;
  country: CountryCode;
  language: LanguageCode;
}

/** The input fields for identifying a product. */
export interface ProductIdentifierInput {
  customId?: UniqueMetafieldValueInput;
  handle?: string;
  id?: string;
}

/** The input fields for creating or updating a product. */
export interface ProductInput {
  category?: string;
  claimOwnership?: ProductClaimOwnershipInput;
  collectionsToJoin?: string[];
  collectionsToLeave?: string[];
  combinedListingRole?: CombinedListingsRole;
  descriptionHtml?: string;
  giftCard?: boolean;
  giftCardTemplateSuffix?: string;
  handle?: string;
  id?: string;
  metafields?: MetafieldInput[];
  productOptions?: OptionCreateInput[];
  productType?: string;
  redirectNewHandle?: boolean;
  requiresSellingPlan?: boolean;
  seo?: SEOInput;
  status?: ProductStatus;
  tags?: string[];
  templateSuffix?: string;
  title?: string;
  vendor?: string;
  productPublications?: ProductPublicationInput[];
  publications?: ProductPublicationInput[];
  publishDate?: string;
  published?: boolean;
  publishedAt?: string;
  publishOn?: string;
}

/** The input fields for specifying a publication to which a product will be published. */
export interface ProductPublicationInput {
  publicationId?: string;
  publishDate?: string;
  channelHandle?: string;
  channelId?: string;
}

/** The input fields for specifying a product to publish and the channels to publish it to. */
export interface ProductPublishInput {
  id: string;
  productPublications: ProductPublicationInput[];
}

/** The input fields used to create a product feedback. */
export interface ProductResourceFeedbackInput {
  channelId?: string;
  feedbackGeneratedAt: string;
  messages?: string[];
  productId: string;
  productUpdatedAt: string;
  state: ResourceFeedbackState;
}

/** The input fields required to identify a resource. */
export interface ProductSetIdentifiers {
  customId?: UniqueMetafieldValueInput;
  handle?: string;
  id?: string;
}

/** The input fields required to create or update a product via ProductSet mutation. */
export interface ProductSetInput {
  category?: string;
  claimOwnership?: ProductClaimOwnershipInput;
  collections?: string[];
  combinedListingRole?: CombinedListingsRole;
  descriptionHtml?: string;
  files?: FileSetInput[];
  giftCard?: boolean;
  giftCardTemplateSuffix?: string;
  handle?: string;
  metafields?: MetafieldInput[];
  productOptions?: OptionSetInput[];
  productType?: string;
  redirectNewHandle?: boolean;
  requiresSellingPlan?: boolean;
  seo?: SEOInput;
  status?: ProductStatus;
  tags?: string[];
  templateSuffix?: string;
  title?: string;
  variants?: ProductVariantSetInput[];
  vendor?: string;
  id?: string;
}

/** The input fields required to set inventory quantities using `productSet` mutation. */
export interface ProductSetInventoryInput {
  locationId: string;
  name: string;
  quantity: number;
}

/** The input fields for specifying a product to unpublish from a channel and the sales channels to unpublish it from. */
export interface ProductUnpublishInput {
  id: string;
  productPublications: ProductPublicationInput[];
}

/** The input fields required to identify a product for update. */
export interface ProductUpdateIdentifiers {
  customId?: UniqueMetafieldValueInput;
  handle?: string;
  id?: string;
}

/** The input fields for updating a product. */
export interface ProductUpdateInput {
  category?: string;
  collectionsToJoin?: string[];
  collectionsToLeave?: string[];
  deleteConflictingConstrainedMetafields?: boolean;
  descriptionHtml?: string;
  giftCardTemplateSuffix?: string;
  handle?: string;
  id?: string;
  metafields?: MetafieldInput[];
  productType?: string;
  redirectNewHandle?: boolean;
  requiresSellingPlan?: boolean;
  seo?: SEOInput;
  status?: ProductStatus;
  tags?: string[];
  templateSuffix?: string;
  title?: string;
  vendor?: string;
}

/** The input fields required to append media to a single variant. */
export interface ProductVariantAppendMediaInput {
  mediaIds: string[];
  variantId: string;
}

/** The input fields required to detach media from a single variant. */
export interface ProductVariantDetachMediaInput {
  mediaIds: string[];
  variantId: string;
}

/** The input fields for the bundle components for core. */
export interface ProductVariantGroupRelationshipInput {
  id: string;
  quantity: number;
}

/** The input fields for identifying a product variant. */
export interface ProductVariantIdentifierInput {
  customId?: UniqueMetafieldValueInput;
  id?: string;
}

/** The input fields representing a product variant position. */
export interface ProductVariantPositionInput {
  id: string;
  position: number;
}

/** The input fields for updating a composite product variant. */
export interface ProductVariantRelationshipUpdateInput {
  parentProductId?: string;
  parentProductVariantId?: string;
  priceInput?: PriceInput;
  productVariantRelationshipsToCreate?: ProductVariantGroupRelationshipInput[];
  productVariantRelationshipsToRemove?: string[];
  productVariantRelationshipsToUpdate?: ProductVariantGroupRelationshipInput[];
  removeAllProductVariantRelationships?: boolean;
}

/** The input fields for specifying a product variant to create as part of a variant bulk mutation. */
export interface ProductVariantsBulkInput {
  barcode?: string;
  compareAtPrice?: string;
  id?: string;
  inventoryItem?: InventoryItemInput;
  inventoryPolicy?: ProductVariantInventoryPolicy;
  inventoryQuantities?: InventoryLevelInput[];
  mediaId?: string;
  mediaSrc?: string[];
  metafields?: MetafieldInput[];
  optionValues?: VariantOptionValueInput[];
  price?: string;
  quantityAdjustments?: InventoryAdjustmentInput[];
  requiresComponents?: boolean;
  showUnitPrice?: boolean;
  taxable?: boolean;
  taxCode?: string;
  unitPriceMeasurement?: UnitPriceMeasurementInput;
}

/** The input fields for specifying a product variant to create or update. */
export interface ProductVariantSetInput {
  barcode?: string;
  compareAtPrice?: string;
  file?: FileSetInput;
  id?: string;
  inventoryItem?: InventoryItemInput;
  inventoryPolicy?: ProductVariantInventoryPolicy;
  inventoryQuantities?: ProductSetInventoryInput[];
  metafields?: MetafieldInput[];
  optionValues: VariantOptionValueInput[];
  position?: number;
  price?: string;
  requiresComponents?: boolean;
  showUnitPrice?: boolean;
  sku?: string;
  taxable?: boolean;
  taxCode?: string;
  unitPriceMeasurement?: UnitPriceMeasurementInput;
}

/** The input fields for creating a publication. */
export interface PublicationCreateInput {
  autoPublish?: boolean;
  catalogId?: string;
  defaultState?: PublicationCreateInputPublicationDefaultState;
}

/** The input fields required to publish a resource. */
export interface PublicationInput {
  publicationId?: string;
  publishDate?: string;
  channelId?: string;
}

/** The input fields for updating a publication. */
export interface PublicationUpdateInput {
  autoPublish?: boolean;
  publishablesToAdd?: string[];
  publishablesToRemove?: string[];
}

/** The input fields for a PubSub webhook subscription. */
export interface PubSubWebhookSubscriptionInput {
  filter?: string;
  format?: WebhookSubscriptionFormat;
  includeFields?: string[];
  metafieldNamespaces?: string[];
  metafields?: HasMetafieldsMetafieldIdentifierInput[];
  name?: string;
  pubSubProject: string;
  pubSubTopic: string;
}

/** The input fields for a purchasing company, which is a combination of company, company contact, and company location. */
export interface PurchasingCompanyInput {
  companyContactId: string;
  companyId: string;
  companyLocationId: string;
}

/** The input fields for a purchasing entity. Can either be a customer or a purchasing company. */
export interface PurchasingEntityInput {
  customerId?: string;
  purchasingCompany?: PurchasingCompanyInput;
}

/** The input fields and values to use when creating quantity price breaks. */
export interface QuantityPriceBreakInput {
  minimumQuantity: number;
  price: MoneyInput;
  variantId: string;
}

/** The input fields used to update quantity pricing. */
export interface QuantityPricingByVariantUpdateInput {
  pricesToAdd: PriceListPriceInput[];
  pricesToDeleteByVariantId: string[];
  quantityPriceBreaksToAdd: QuantityPriceBreakInput[];
  quantityPriceBreaksToDelete: string[];
  quantityPriceBreaksToDeleteByVariantId?: string[];
  quantityRulesToAdd: QuantityRuleInput[];
  quantityRulesToDeleteByVariantId: string[];
}

/** The input fields for the per-order quantity rule to be applied on the product variant. */
export interface QuantityRuleInput {
  increment: number;
  maximum?: number;
  minimum: number;
  variantId: string;
}

/** The input fields required to reimburse duties on a refund. */
export interface RefundDutyInput {
  dutyId: string;
  refundType?: RefundDutyRefundType;
}

/** The input fields to create a refund. */
export interface RefundInput {
  allowOverRefunding?: boolean;
  currency?: CurrencyCode;
  discrepancyReason?: OrderAdjustmentInputDiscrepancyReason;
  note?: string;
  notify?: boolean;
  orderId: string;
  processedAt?: string;
  refundDuties?: RefundDutyInput[];
  refundLineItems?: RefundLineItemInput[];
  refundMethods?: RefundMethodInput[];
  shipping?: ShippingRefundInput;
  transactions?: OrderTransactionInput[];
}

/** The input fields required to reimburse line items on a refund. */
export interface RefundLineItemInput {
  lineItemId: string;
  locationId?: string;
  quantity: number;
  restockType?: RefundLineItemRestockType;
}

/** The input fields for processing the financial outcome of a refund. */
export interface RefundMethodInput {
  storeCreditRefund?: StoreCreditRefundInput;
}

/** The input fields for the shipping cost to refund. */
export interface RefundShippingInput {
  fullRefund?: boolean;
  shippingRefundAmount?: MoneyInput;
}

/** The input fields for a remote Authorize.net customer payment profile. */
export interface RemoteAuthorizeNetCustomerPaymentProfileInput {
  customerPaymentProfileId?: string;
  customerProfileId: string;
}

/** The input fields for a remote Braintree customer payment profile. */
export interface RemoteBraintreePaymentMethodInput {
  customerId: string;
  paymentMethodToken?: string;
}

/** The input fields for a remote stripe payment method. */
export interface RemoteStripePaymentMethodInput {
  customerId: string;
  paymentMethodId?: string;
}

/** The input fields for a resource feedback object. */
export interface ResourceFeedbackCreateInput {
  channelId?: string;
  feedbackGeneratedAt: string;
  messages?: string[];
  state: ResourceFeedbackState;
}

/** The input fields for a restocking fee. */
export interface RestockingFeeInput {
  percentage: number;
}

/** The input fields for approving a customer's return request. */
export interface ReturnApproveRequestInput {
  id: string;
  notifyCustomer?: boolean;
  unprocessed?: boolean;
}

/** The input fields for declining a customer's return request. */
export interface ReturnDeclineRequestInput {
  declineNote?: string;
  declineReason: ReturnDeclineReason;
  id: string;
  notifyCustomer?: boolean;
}

/** The input fields for a return. */
export interface ReturnInput {
  exchangeLineItems?: ExchangeLineItemInput[];
  orderId: string;
  requestedAt?: string;
  returnLineItems: ReturnLineItemInput[];
  returnShippingFee?: ReturnShippingFeeInput;
  notifyCustomer?: boolean;
  unprocessed?: boolean;
}

/** The input fields for a return line item. */
export interface ReturnLineItemInput {
  fulfillmentLineItemId: string;
  quantity: number;
  restockingFee?: RestockingFeeInput;
  returnReasonDefinitionId?: string;
  returnReasonNote?: string;
  returnReason?: ReturnReason;
}

/** The input fields for a removing a return line item from a return. */
export interface ReturnLineItemRemoveFromReturnInput {
  quantity: number;
  returnLineItemId: string;
}

/** The input fields for an exchange line item. */
export interface ReturnProcessExchangeLineItemInput {
  id: string;
  quantity: number;
}

/** The input fields for the financial transfer for the return. */
export interface ReturnProcessFinancialTransferInput {
  issueRefund?: ReturnProcessRefundInput;
}

/** The input fields for processing a return. */
export interface ReturnProcessInput {
  exchangeLineItems?: ReturnProcessExchangeLineItemInput[];
  financialTransfer?: ReturnProcessFinancialTransferInput;
  note?: string;
  notifyCustomer?: boolean;
  refundDuties?: RefundDutyInput[];
  refundShipping?: RefundShippingInput;
  returnId: string;
  returnLineItems?: ReturnProcessReturnLineItemInput[];
  tipLineId?: string;
}

/** The input fields for the refund for the return. */
export interface ReturnProcessRefundInput {
  allowOverRefunding?: boolean;
  orderTransactions: ReturnRefundOrderTransactionInput[];
  refundMethods?: RefundMethodInput[];
}

/** The input fields for a return line item. */
export interface ReturnProcessReturnLineItemInput {
  dispositions?: ReverseFulfillmentOrderDisposeInput[];
  id: string;
  quantity: number;
}

/** The input fields to refund a return. */
export interface ReturnRefundInput {
  notifyCustomer?: boolean;
  orderTransactions?: ReturnRefundOrderTransactionInput[];
  refundDuties?: RefundDutyInput[];
  refundShipping?: RefundShippingInput;
  returnId: string;
  returnRefundLineItems: ReturnRefundLineItemInput[];
}

/** The input fields for a return refund line item. */
export interface ReturnRefundLineItemInput {
  quantity: number;
  returnLineItemId: string;
}

/** The input fields to create order transactions when refunding a return. */
export interface ReturnRefundOrderTransactionInput {
  parentId: string;
  transactionAmount: MoneyInput;
}

/** The input fields for requesting a return. */
export interface ReturnRequestInput {
  orderId: string;
  returnLineItems: ReturnRequestLineItemInput[];
  returnShippingFee?: ReturnShippingFeeInput;
}

/** The input fields for a return line item. */
export interface ReturnRequestLineItemInput {
  customerNote?: string;
  fulfillmentLineItemId: string;
  quantity: number;
  restockingFee?: RestockingFeeInput;
  returnReasonDefinitionId?: string;
  returnReason?: ReturnReason;
}

/** The input fields for a return shipping fee. */
export interface ReturnShippingFeeInput {
  amount: MoneyInput;
}

/** The input fields for a reverse label. */
export interface ReverseDeliveryLabelInput {
  fileUrl: string;
}

/** The input fields for a reverse delivery line item. */
export interface ReverseDeliveryLineItemInput {
  quantity: number;
  reverseFulfillmentOrderLineItemId: string;
}

/** The input fields for tracking information about a return delivery. */
export interface ReverseDeliveryTrackingInput {
  number?: string;
  url?: string;
}

/** The input fields to dispose a reverse fulfillment order line item. */
export interface ReverseFulfillmentOrderDisposeInput {
  dispositionType: ReverseFulfillmentOrderDispositionType;
  locationId?: string;
  quantity: number;
  reverseFulfillmentOrderLineItemId: string;
}

/** The input fields to create a saved search. */
export interface SavedSearchCreateInput {
  name: string;
  query: string;
  resourceType: SearchResultType;
}

/** The input fields to delete a saved search. */
export interface SavedSearchDeleteInput {
  id: string;
}

/** The input fields to update a saved search. */
export interface SavedSearchUpdateInput {
  id: string;
  name?: string;
  query?: string;
}

/** The input fields for a script tag. This input object is used when creating or updating a script tag to specify its URL, where it should be included, and how it will be cached. */
export interface ScriptTagInput {
  cache?: boolean;
  displayScope?: ScriptTagDisplayScope;
  src?: string;
}

/** The input fields for the selected variant option of the combined listing. */
export interface SelectedVariantOptionInput {
  linkedMetafieldValue?: string;
  name: string;
  value: string;
}

/** The input fields required to create or update a selling plan anchor. */
export interface SellingPlanAnchorInput {
  cutoffDay?: number;
  day?: number;
  month?: number;
  type?: SellingPlanAnchorType;
}

/** The input fields that are required to create or update a billing policy type. */
export interface SellingPlanBillingPolicyInput {
  fixed?: SellingPlanFixedBillingPolicyInput;
  recurring?: SellingPlanRecurringBillingPolicyInput;
}

/** The input fields that are required to create or update a checkout charge. */
export interface SellingPlanCheckoutChargeInput {
  type?: SellingPlanCheckoutChargeType;
  value?: SellingPlanCheckoutChargeValueInput;
}

/** The input fields required to create or update an checkout charge value. */
export interface SellingPlanCheckoutChargeValueInput {
  fixedValue?: string;
  percentage?: number;
}

/** The input fields that are required to create or update a delivery policy. */
export interface SellingPlanDeliveryPolicyInput {
  fixed?: SellingPlanFixedDeliveryPolicyInput;
  recurring?: SellingPlanRecurringDeliveryPolicyInput;
}

/** The input fields required to create or update a fixed billing policy. */
export interface SellingPlanFixedBillingPolicyInput {
  checkoutCharge?: SellingPlanCheckoutChargeInput;
  remainingBalanceChargeExactTime?: string;
  remainingBalanceChargeTimeAfterCheckout?: string;
  remainingBalanceChargeTrigger?: SellingPlanRemainingBalanceChargeTrigger;
}

/** The input fields required to create or update a fixed delivery policy. */
export interface SellingPlanFixedDeliveryPolicyInput {
  anchors?: SellingPlanAnchorInput[];
  cutoff?: number;
  fulfillmentExactTime?: string;
  fulfillmentTrigger?: SellingPlanFulfillmentTrigger;
  intent?: SellingPlanFixedDeliveryPolicyIntent;
  preAnchorBehavior?: SellingPlanFixedDeliveryPolicyPreAnchorBehavior;
}

/** The input fields required to create or update a fixed selling plan pricing policy. */
export interface SellingPlanFixedPricingPolicyInput {
  adjustmentType?: SellingPlanPricingPolicyAdjustmentType;
  adjustmentValue?: SellingPlanPricingPolicyValueInput;
  id?: string;
}

/** The input fields required to create or update a selling plan group. */
export interface SellingPlanGroupInput {
  appId?: string;
  description?: string;
  merchantCode?: string;
  name?: string;
  options?: string[];
  position?: number;
  sellingPlansToCreate?: SellingPlanInput[];
  sellingPlansToDelete?: string[];
  sellingPlansToUpdate?: SellingPlanInput[];
}

/** The input fields for resource association with a Selling Plan Group. */
export interface SellingPlanGroupResourceInput {
  productIds?: string[];
  productVariantIds?: string[];
}

/** The input fields to create or update a selling plan. */
export interface SellingPlanInput {
  billingPolicy?: SellingPlanBillingPolicyInput;
  category?: SellingPlanCategory;
  deliveryPolicy?: SellingPlanDeliveryPolicyInput;
  description?: string;
  id?: string;
  inventoryPolicy?: SellingPlanInventoryPolicyInput;
  metafields?: MetafieldInput[];
  name?: string;
  options?: string[];
  position?: number;
  pricingPolicies?: SellingPlanPricingPolicyInput[];
}

/** The input fields required to create or update an inventory policy. */
export interface SellingPlanInventoryPolicyInput {
  reserve?: SellingPlanReserve;
}

/** The input fields required to create or update a selling plan pricing policy. */
export interface SellingPlanPricingPolicyInput {
  fixed?: SellingPlanFixedPricingPolicyInput;
  recurring?: SellingPlanRecurringPricingPolicyInput;
}

/** The input fields required to create or update a pricing policy adjustment value. */
export interface SellingPlanPricingPolicyValueInput {
  fixedValue?: string;
  percentage?: number;
}

/** The input fields required to create or update a recurring billing policy. */
export interface SellingPlanRecurringBillingPolicyInput {
  anchors?: SellingPlanAnchorInput[];
  interval?: SellingPlanInterval;
  intervalCount?: number;
  maxCycles?: number;
  minCycles?: number;
}

/** The input fields to create or update a recurring delivery policy. */
export interface SellingPlanRecurringDeliveryPolicyInput {
  anchors?: SellingPlanAnchorInput[];
  cutoff?: number;
  intent?: SellingPlanRecurringDeliveryPolicyIntent;
  interval?: SellingPlanInterval;
  intervalCount?: number;
  preAnchorBehavior?: SellingPlanRecurringDeliveryPolicyPreAnchorBehavior;
}

/** The input fields required to create or update a recurring selling plan pricing policy. */
export interface SellingPlanRecurringPricingPolicyInput {
  adjustmentType?: SellingPlanPricingPolicyAdjustmentType;
  adjustmentValue?: SellingPlanPricingPolicyValueInput;
  afterCycle: number;
  id?: string;
}

/** The input fields for SEO information. */
export interface SEOInput {
  description?: string;
  title?: string;
}

/** The input fields for specifying the shipping details for the draft order. */
export interface ShippingLineInput {
  priceWithCurrency?: MoneyInput;
  shippingRateHandle?: string;
  title?: string;
  price?: string;
}

/** The input fields that are required to reimburse shipping costs. */
export interface ShippingRefundInput {
  amount?: string;
  fullRefund?: boolean;
}

/** The input fields required to update a dispute evidence object. */
export interface ShopifyPaymentsDisputeEvidenceUpdateInput {
  accessActivityLog?: string;
  cancellationPolicyDisclosure?: string;
  cancellationPolicyFile?: ShopifyPaymentsDisputeFileUploadUpdateInput;
  cancellationRebuttal?: string;
  customerCommunicationFile?: ShopifyPaymentsDisputeFileUploadUpdateInput;
  customerEmailAddress?: string;
  customerFirstName?: string;
  customerLastName?: string;
  refundPolicyDisclosure?: string;
  refundPolicyFile?: ShopifyPaymentsDisputeFileUploadUpdateInput;
  refundRefusalExplanation?: string;
  serviceDocumentationFile?: ShopifyPaymentsDisputeFileUploadUpdateInput;
  shippingAddress?: MailingAddressInput;
  shippingDocumentationFile?: ShopifyPaymentsDisputeFileUploadUpdateInput;
  submitEvidence?: boolean;
  uncategorizedFile?: ShopifyPaymentsDisputeFileUploadUpdateInput;
  uncategorizedText?: string;
}

/** The input fields required to update a dispute file upload object. */
export interface ShopifyPaymentsDisputeFileUploadUpdateInput {
  destroy?: boolean;
  id: string;
}

/** The input fields for a shop locale. */
export interface ShopLocaleInput {
  marketWebPresenceIds?: string[];
  published?: boolean;
}

/** The input fields required to update a policy. */
export interface ShopPolicyInput {
  body: string;
  type: ShopPolicyType;
}

/** The input fields for generating staged upload targets. */
export interface StagedUploadInput {
  filename: string;
  fileSize?: string;
  httpMethod?: StagedUploadHttpMethodType;
  mimeType: string;
  resource: StagedUploadTargetGenerateUploadResource;
}

/** The required fields and parameters to generate the URL upload an' asset to Shopify. */
export interface StagedUploadTargetGenerateInput {
  filename: string;
  fileSize?: string;
  httpMethod?: StagedUploadHttpMethodType;
  mimeType: string;
  resource: StagedUploadTargetGenerateUploadResource;
}

/** An image to be uploaded. */
export interface StageImageInput {
  filename: string;
  httpMethod?: StagedUploadHttpMethodType;
  mimeType: string;
  resource: StagedUploadTargetGenerateUploadResource;
}

/** The input fields for the access settings for the metafields under the standard definition. */
export interface StandardMetafieldDefinitionAccessInput {
  admin?: MetafieldAdminAccessInput;
  customerAccount?: MetafieldCustomerAccountAccessInput;
  storefront?: MetafieldStorefrontAccessInput;
}

/** The input fields for a store credit account credit transaction. */
export interface StoreCreditAccountCreditInput {
  creditAmount: MoneyInput;
  expiresAt?: string;
  notify?: boolean;
}

/** The input fields for a store credit account debit transaction. */
export interface StoreCreditAccountDebitInput {
  debitAmount: MoneyInput;
}

/** The input fields to process a refund to store credit. */
export interface StoreCreditRefundInput {
  amount: MoneyInput;
  expiresAt?: string;
}

/** The input fields to delete a storefront access token. */
export interface StorefrontAccessTokenDeleteInput {
  id: string;
}

/** The input fields for a storefront access token. */
export interface StorefrontAccessTokenInput {
  title: string;
}

/** The input fields for mapping a subscription line to a discount. */
export interface SubscriptionAtomicLineInput {
  discounts?: SubscriptionAtomicManualDiscountInput[];
  line: SubscriptionLineInput;
}

/** The input fields for mapping a subscription line to a discount. */
export interface SubscriptionAtomicManualDiscountInput {
  recurringCycleLimit?: number;
  title?: string;
  value?: SubscriptionManualDiscountValueInput;
}

/** The input fields required to complete a subscription billing attempt. */
export interface SubscriptionBillingAttemptInput {
  billingCycleSelector?: SubscriptionBillingCycleSelector;
  idempotencyKey: string;
  inventoryPolicy?: SubscriptionBillingAttemptInventoryPolicy;
  originTime?: string;
  paymentProcessingPolicy?: SubscriptionBillingAttemptPaymentProcessingPolicy;
}

/** The input fields for filtering subscription billing cycles in bulk actions. */
export interface SubscriptionBillingCycleBulkFilters {
  billingAttemptStatus?: SubscriptionBillingCycleBillingAttemptStatus;
  billingCycleStatus?: SubscriptionBillingCycleBillingCycleStatus[];
  contractStatus?: SubscriptionContractSubscriptionStatus[];
}

/** The input fields for specifying the subscription contract and selecting the associated billing cycle. */
export interface SubscriptionBillingCycleInput {
  contractId: string;
  selector: SubscriptionBillingCycleSelector;
}

/** The input fields for parameters to modify the schedule of a specific billing cycle. */
export interface SubscriptionBillingCycleScheduleEditInput {
  billingDate?: string;
  reason: SubscriptionBillingCycleScheduleEditInputScheduleEditReason;
  skip?: boolean;
}

/** The input fields to select a subset of subscription billing cycles within a date range. */
export interface SubscriptionBillingCyclesDateRangeSelector {
  endDate: string;
  startDate: string;
}

/** The input fields to select SubscriptionBillingCycle by either date or index. Both past and future billing cycles can be selected. */
export interface SubscriptionBillingCycleSelector {
  date?: string;
  index?: number;
}

/** The input fields to select a subset of subscription billing cycles within an index range. */
export interface SubscriptionBillingCyclesIndexRangeSelector {
  endIndex: number;
  startIndex: number;
}

/** The input fields for a Subscription Billing Policy. */
export interface SubscriptionBillingPolicyInput {
  anchors?: SellingPlanAnchorInput[];
  interval: SellingPlanInterval;
  intervalCount: number;
  maxCycles?: number;
  minCycles?: number;
}

/** The input fields required to create a Subscription Contract. */
export interface SubscriptionContractAtomicCreateInput {
  contract: SubscriptionDraftInput;
  currencyCode: CurrencyCode;
  customerId: string;
  discountCodes?: string[];
  lines: SubscriptionAtomicLineInput[];
  nextBillingDate: string;
}

/** The input fields required to create a Subscription Contract. */
export interface SubscriptionContractCreateInput {
  contract: SubscriptionDraftInput;
  currencyCode: CurrencyCode;
  customerId: string;
  nextBillingDate: string;
}

/** The input fields required to create a Subscription Contract. */
export interface SubscriptionContractProductChangeInput {
  currentPrice?: string;
  productVariantId?: string;
}

/** Specifies delivery method fields for a subscription draft. This is an input union: one, and only one, field can be provided. The field provided will determine which delivery method is to be used. */
export interface SubscriptionDeliveryMethodInput {
  localDelivery?: SubscriptionDeliveryMethodLocalDeliveryInput;
  pickup?: SubscriptionDeliveryMethodPickupInput;
  shipping?: SubscriptionDeliveryMethodShippingInput;
}

/** The input fields for a local delivery method. */
export interface SubscriptionDeliveryMethodLocalDeliveryInput {
  address?: MailingAddressInput;
  localDeliveryOption?: SubscriptionDeliveryMethodLocalDeliveryOptionInput;
}

/** The input fields for local delivery option. */
export interface SubscriptionDeliveryMethodLocalDeliveryOptionInput {
  code?: string;
  description?: string;
  instructions?: string;
  phone: string;
  presentmentTitle?: string;
  title?: string;
}

/** The input fields for a pickup delivery method. */
export interface SubscriptionDeliveryMethodPickupInput {
  pickupOption?: SubscriptionDeliveryMethodPickupOptionInput;
}

/** The input fields for pickup option. */
export interface SubscriptionDeliveryMethodPickupOptionInput {
  code?: string;
  description?: string;
  locationId: string;
  presentmentTitle?: string;
  title?: string;
}

/** Specifies shipping delivery method fields. */
export interface SubscriptionDeliveryMethodShippingInput {
  address?: MailingAddressInput;
  shippingOption?: SubscriptionDeliveryMethodShippingOptionInput;
}

/** The input fields for shipping option. */
export interface SubscriptionDeliveryMethodShippingOptionInput {
  carrierServiceId?: string;
  code?: string;
  description?: string;
  presentmentTitle?: string;
  title?: string;
}

/** The input fields for a Subscription Delivery Policy. */
export interface SubscriptionDeliveryPolicyInput {
  anchors?: SellingPlanAnchorInput[];
  interval: SellingPlanInterval;
  intervalCount: number;
}

/** The input fields required to create a Subscription Draft. */
export interface SubscriptionDraftInput {
  billingPolicy?: SubscriptionBillingPolicyInput;
  customAttributes?: AttributeInput[];
  deliveryMethod?: SubscriptionDeliveryMethodInput;
  deliveryPolicy?: SubscriptionDeliveryPolicyInput;
  deliveryPrice?: string;
  nextBillingDate?: string;
  note?: string;
  paymentMethodId?: string;
  status?: SubscriptionContractSubscriptionStatus;
}

/** The input fields for a subscription free shipping discount on a contract. */
export interface SubscriptionFreeShippingDiscountInput {
  recurringCycleLimit?: number;
  title?: string;
}

/** The input fields required to add a new subscription line to a contract. */
export interface SubscriptionLineInput {
  currentPrice: string;
  customAttributes?: AttributeInput[];
  pricingPolicy?: SubscriptionPricingPolicyInput;
  productVariantId: string;
  quantity: number;
  sellingPlanId?: string;
  sellingPlanName?: string;
}

/** The input fields required to update a subscription line on a contract. */
export interface SubscriptionLineUpdateInput {
  currentPrice?: string;
  customAttributes?: AttributeInput[];
  pricingPolicy?: SubscriptionPricingPolicyInput;
  productVariantId?: string;
  quantity?: number;
  sellingPlanId?: string;
  sellingPlanName?: string;
}

/** The input fields for the subscription lines the discount applies on. */
export interface SubscriptionManualDiscountEntitledLinesInput {
  all?: boolean;
  lines?: SubscriptionManualDiscountLinesInput;
}

/** The input fields for the fixed amount value of the discount and distribution on the lines. */
export interface SubscriptionManualDiscountFixedAmountInput {
  amount?: number;
  appliesOnEachItem?: boolean;
}

/** The input fields for a subscription discount on a contract. */
export interface SubscriptionManualDiscountInput {
  entitledLines?: SubscriptionManualDiscountEntitledLinesInput;
  recurringCycleLimit?: number;
  title?: string;
  value?: SubscriptionManualDiscountValueInput;
}

/** The input fields for line items that the discount refers to. */
export interface SubscriptionManualDiscountLinesInput {
  add?: string[];
  remove?: string[];
}

/** The input fields for the discount value and its distribution. */
export interface SubscriptionManualDiscountValueInput {
  fixedAmount?: SubscriptionManualDiscountFixedAmountInput;
  percentage?: number;
}

/** The input fields for an array containing all pricing changes for each billing cycle. */
export interface SubscriptionPricingPolicyCycleDiscountsInput {
  adjustmentType: SellingPlanPricingPolicyAdjustmentType;
  adjustmentValue: SellingPlanPricingPolicyValueInput;
  afterCycle: number;
  computedPrice: string;
}

/** The input fields for expected price changes of the subscription line over time. */
export interface SubscriptionPricingPolicyInput {
  basePrice: string;
  cycleDiscounts: SubscriptionPricingPolicyCycleDiscountsInput[];
}

/** The input fields for an exchange line item. */
export interface SuggestedOutcomeExchangeLineItemInput {
  id: string;
  quantity: number;
}

/** The input fields for a return line item. */
export interface SuggestedOutcomeReturnLineItemInput {
  id: string;
  quantity: number;
}

/** The input fields for the file copy. */
export interface ThemeFilesCopyFileInput {
  dstFilename: string;
  srcFilename: string;
}

/** The input fields and values for creating or updating a translation. */
export interface TranslationInput {
  key: string;
  locale: string;
  marketId?: string;
  translatableContentDigest: string;
  value: string;
}

/** The input fields that identify a unique valued metafield. */
export interface UniqueMetafieldValueInput {
  key: string;
  namespace?: string;
  value: string;
}

/** The input fields for the measurement used to calculate a unit price for a product variant (e.g. $9.99 / 100ml). */
export interface UnitPriceMeasurementInput {
  quantityUnit?: UnitPriceMeasurementMeasuredUnit;
  quantityValue?: number;
  referenceUnit?: UnitPriceMeasurementMeasuredUnit;
  referenceValue?: number;
}

/** The input fields required to update a media object. */
export interface UpdateMediaInput {
  alt?: string;
  id: string;
  previewImageSource?: string;
}

/** The input fields to create or update a URL redirect. */
export interface UrlRedirectInput {
  path?: string;
  target?: string;
}

/** Specifies the [Urchin Traffic Module (UTM) parameters](https://en.wikipedia.org/wiki/UTM_parameters) that are associated with a related marketing campaign. */
export interface UTMInput {
  campaign: string;
  medium: string;
  source: string;
}

/** The input fields required to install a validation. */
export interface ValidationCreateInput {
  blockOnFailure?: boolean;
  enable?: boolean;
  functionHandle?: string;
  metafields?: MetafieldInput[];
  title?: string;
  functionId?: string;
}

/** The input fields required to update a validation. */
export interface ValidationUpdateInput {
  blockOnFailure?: boolean;
  enable?: boolean;
  metafields?: MetafieldInput[];
  title?: string;
}

/** The input fields required to create or modify a product variant's option value. */
export interface VariantOptionValueInput {
  id?: string;
  linkedMetafieldValue?: string;
  name?: string;
  optionId?: string;
  optionName?: string;
}

/** The input fields for a webhook subscription. */
export interface WebhookSubscriptionInput {
  filter?: string;
  format?: WebhookSubscriptionFormat;
  includeFields?: string[];
  metafieldNamespaces?: string[];
  metafields?: HasMetafieldsMetafieldIdentifierInput[];
  name?: string;
  uri?: string;
  callbackUrl?: string;
}

/** The input fields for creating or updating a web pixel. */
export interface WebPixelInput {
  settings: unknown;
}

/** The input fields used to create a web presence. */
export interface WebPresenceCreateInput {
  alternateLocales?: string[];
  defaultLocale: string;
  domainId?: string;
  subfolderSuffix?: string;
}

/** The input fields used to update a web presence. */
export interface WebPresenceUpdateInput {
  alternateLocales?: string[];
  defaultLocale?: string;
  subfolderSuffix?: string;
}

/** The input fields for the weight unit and value inputs. */
export interface WeightInput {
  unit: WeightUnit;
  value: number;
}

