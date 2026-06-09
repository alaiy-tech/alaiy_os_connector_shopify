// Auto-generated Shopify Admin GraphQL API 2026-04 - 45 interface types
// Do not edit manually - regenerate with parse_types.ps1

import type { AppPurchaseStatus, CatalogStatus, CurrencyCode, DiscountApplicationAllocationMethod, DiscountApplicationLevel, DiscountApplicationTargetSelection, DiscountApplicationTargetType, FileStatus, MediaContentType, MediaStatus, OrderActionType, ResourceOperationStatus, ReturnReason, SaleActionType, SaleLineType, SellingPlanPricingPolicyAdjustmentType, StoreCreditSystemEvent, SubscriptionBillingAttemptErrorCode } from './enums';
import type { App, Attribute, CheckoutAndAccountsConfigurationBranding, Count, Customer, CustomerPaymentMethod, FileError, GiftCard, MediaError, MediaPreviewImage, MediaWarning, Metafield, MoneyBag, MoneyV2, PointOfSaleDevicePaymentSession, PriceList, Publication, ReturnReasonDefinition, RowCount, SaleTax, StaffMember, StoreCreditAccount, Translation } from './objects';
import type { ChannelConnection, EventConnection, LocalizationExtensionConnection, LocalizedFieldConnection, MetafieldConnection, MetafieldDefinitionConnection, OrderConnection, PublicationConnection, ResourcePublicationConnection, ResourcePublicationV2Connection, SaleConnection, StoreCreditAccountConnection, SubscriptionLineConnection, SubscriptionManualDiscountConnection } from './connections';
import type { PricingValue, SellingPlanPricingPolicyAdjustmentValue, StoreCreditAccountTransactionOrigin, SubscriptionDeliveryMethod } from './unions';

export interface AppPurchase {
  createdAt: string;
  name: string;
  price: MoneyV2;
  status: AppPurchaseStatus;
  test: boolean;
}

export interface BasePaymentDetails {
  paymentMethodName: string | null;
}

export interface CalculatedDiscountApplication {
  allocationMethod: DiscountApplicationAllocationMethod;
  appliedTo: DiscountApplicationLevel;
  description: string | null;
  id: string;
  targetSelection: DiscountApplicationTargetSelection;
  targetType: DiscountApplicationTargetType;
  value: PricingValue;
}

export interface CalculatedReturnFee {
  amountSet: MoneyBag;
  id: string;
}

export interface CashActivity {
  cash: MoneyV2;
  paymentSession: PointOfSaleDevicePaymentSession;
  staffMember: StaffMember;
  time: string;
}

export interface Catalog {
  id: string;
  operations: ResourceOperation[];
  priceList: PriceList | null;
  publication: Publication | null;
  status: CatalogStatus;
  title: string;
}

/** Represents a checkout and accounts configuration interface. */
export interface CheckoutAndAccountsConfigurationInterface {
  branding: CheckoutAndAccountsConfigurationBranding | null;
  createdAt: string;
  editedAt: string;
  name: string;
  updatedAt: string;
}

/** interface CheckoutBrandingFont { */
export interface CheckoutBrandingFont {
  sources: string | null;
  weight: number | null;
}

/** The subject line of a comment event. */
export interface CommentEventSubject {
  hasTimelineComment: boolean;
  id: string;
}

export interface CustomerAccountPage {
  defaultCursor: string;
  handle: string;
  id: string;
  title: string;
}

export interface CustomerMoment {
  occurredAt: string;
}

/** Discount applications capture the intentions of a discount source at the time of application on an order's line items or shipping lines. */
export interface DiscountApplication {
  allocationMethod: DiscountApplicationAllocationMethod;
  index: number;
  targetSelection: DiscountApplicationTargetSelection;
  targetType: DiscountApplicationTargetType;
  value: PricingValue;
}

/** Represents an error in the input of a mutation. */
export interface DisplayableError {
  field: string[];
  message: string;
}

export interface DraftOrderWarning {
  errorCode: string;
  field: string;
  message: string;
}

/** Events chronicle resource activities such as the creation of an article, the fulfillment of an order, or the addition of a product. */
export interface Event {
  action: string;
  appTitle: string | null;
  attributeToApp: boolean;
  attributeToUser: boolean;
  createdAt: string;
  criticalAlert: boolean;
  id: string;
  message: string;
}

export interface Fee {
  id: string;
}

export interface File {
  alt: string | null;
  createdAt: string;
  fileErrors: FileError[];
  fileStatus: FileStatus;
  id: string;
  preview: MediaPreviewImage | null;
  updatedAt: string;
}

export interface GiftCardTransaction {
  amount: MoneyV2;
  giftCard: GiftCard;
  id: string;
  metafield: Metafield | null;
  metafields: MetafieldConnection;
  note: string | null;
  processedAt: string;
}

/** Represents a summary of the current version of data in a resource. */
export interface HasCompareDigest {
  compareDigest: string;
}

/** Represents an object that has a list of events. */
export interface HasEvents {
  events: EventConnection;
}

/** Localization extensions associated with the specified resource. For example, the tax id for government invoice. */
export interface HasLocalizationExtensions {
  localizationExtensions: LocalizationExtensionConnection;
}

/** Localized fields associated with the specified resource. */
export interface HasLocalizedFields {
  localizedFields: LocalizedFieldConnection;
}

/** Resources that metafield definitions can be applied to. */
export interface HasMetafieldDefinitions {
  metafieldDefinitions: MetafieldDefinitionConnection;
}

/** Represents information about the metafields associated to the specified resource. */
export interface HasMetafields {
  metafield: Metafield | null;
  metafields: MetafieldConnection;
}

/** Published translations associated with the resource. */
export interface HasPublishedTranslations {
  translations: Translation[];
}

export interface HasStoreCreditAccounts {
  storeCreditAccounts: StoreCreditAccountConnection;
}

/** A job corresponds to some long running task that the client should poll for status. */
export interface JobResult {
  done: boolean;
  id: string;
}

/** Interoperability metadata for types that directly correspond to a REST Admin API resource. For example, on the Product type, LegacyInteroperability returns metadata for the corresponding [Product object](https://shopify.dev/api/admin-graphql/latest/objects/product) in the REST... */
export interface LegacyInteroperability {
  legacyResourceId: string;
}

export interface MarketRegion {
  id: string;
  name: string;
}

export interface Media {
  alt: string | null;
  id: string;
  mediaContentType: MediaContentType;
  mediaErrors: MediaError[];
  mediaWarnings: MediaWarning[];
  preview: MediaPreviewImage | null;
  status: MediaStatus;
}

/** A default cursor that you can use in queries to paginate your results. Each edge in a connection can return a cursor, which is a reference to the edge's position in the connection. You can use an edge's cursor as the starting point to retrieve the nodes before or after it in a... */
export interface Navigable {
  defaultCursor: string;
}

/** An object with an ID field to support global identification, in accordance with the [Relay specification](https://relay.dev/graphql/objectidentification.htm#sec-Node-Interface). This interface is used by the [node](https://shopify.dev/api/admin-graphql/unstable/queries/node) a... */
export interface Node {
  id: string;
}

/** Online Store preview URL of the object. */
export interface OnlineStorePreviewable {
  onlineStorePreviewUrl: string | null;
}

/** A resource that can be published or unpublished to channels. */
export interface Publishable {
  resourcePublications: ResourcePublicationConnection;
  resourcePublicationsV2: ResourcePublicationV2Connection;
  unpublishedChannels: ChannelConnection;
  unpublishedPublications: PublicationConnection;
}

export interface ResourceOperation {
  id: string;
  processedRowCount: number | null;
  rowCount: RowCount | null;
  status: ResourceOperationStatus;
}

export interface ReturnLineItemType {
  customerNote: string | null;
  id: string;
  processableQuantity: number;
  processedQuantity: number;
  quantity: number;
  refundableQuantity: number;
  refundedQuantity: number;
  returnReasonDefinition: ReturnReasonDefinition | null;
  returnReasonNote: string;
  unprocessedQuantity: number;
  returnReason: ReturnReason;
}

export interface Sale {
  actionType: SaleActionType;
  id: string;
  lineType: SaleLineType;
  quantity: number | null;
  taxes: SaleTax[];
  totalAmount: MoneyBag;
  totalDiscountAmountAfterTaxes: MoneyBag;
  totalDiscountAmountBeforeTaxes: MoneyBag;
  totalTaxAmount: MoneyBag;
}

export interface SalesAgreement {
  app: App | null;
  happenedAt: string;
  id: string;
  reason: OrderActionType;
  sales: SaleConnection;
  user: StaffMember | null;
}

export interface SegmentFilter {
  localizedName: string;
  multiValue: boolean;
  queryName: string;
}

export interface SellingPlanPricingPolicyBase {
  adjustmentType: SellingPlanPricingPolicyAdjustmentType;
  adjustmentValue: SellingPlanPricingPolicyAdjustmentValue;
}

export interface ShopifyPaymentsChargeStatementDescriptor {
  default: string | null;
  prefix: string;
}

export interface StoreCreditAccountTransaction {
  account: StoreCreditAccount;
  amount: MoneyV2;
  balanceAfterTransaction: MoneyV2;
  createdAt: string;
  event: StoreCreditSystemEvent;
  origin: StoreCreditAccountTransactionOrigin | null;
}

/** An error that prevented a billing attempt. */
export interface SubscriptionBillingAttemptProcessingError {
  code: SubscriptionBillingAttemptErrorCode;
  message: string;
}

export interface SubscriptionContractBase {
  app: App | null;
  appAdminUrl: string | null;
  currencyCode: CurrencyCode;
  customAttributes: Attribute[];
  customer: Customer | null;
  customerPaymentMethod: CustomerPaymentMethod | null;
  deliveryMethod: SubscriptionDeliveryMethod | null;
  deliveryPrice: MoneyV2;
  discounts: SubscriptionManualDiscountConnection;
  lines: SubscriptionLineConnection;
  linesCount: Count | null;
  note: string | null;
  orders: OrderConnection;
  updatedAt: string;
  lineCount: number;
}

export interface SuggestedRefundMethod {
  amount: MoneyBag;
  maximumRefundable: MoneyBag;
}

