// Auto-generated Shopify Admin GraphQL API 2026-04 - 624 enum types
// Do not edit manually - regenerate with parse_types.ps1

/** The set of valid sort keys for the AbandonedCheckout query. */
export type AbandonedCheckoutSortKeys =
  | 'CHECKOUT_ID'
  | 'CREATED_AT'
  | 'CUSTOMER_NAME'
  | 'ID'
  | 'RELEVANCE'
  | 'TOTAL_PRICE';

/** Specifies the abandonment type. */
export type AbandonmentAbandonmentType =
  | 'BROWSE'
  | 'CART'
  | 'CHECKOUT';

/** Specifies the delivery state of a marketing activity. */
export type AbandonmentDeliveryState =
  | 'NOT_SENT'
  | 'SCHEDULED'
  | 'SENT';

/** Specifies the email state. */
export type AbandonmentEmailState =
  | 'NOT_SENT'
  | 'SCHEDULED'
  | 'SENT';

/** Possible error codes that can be returned by `AbandonmentEmailStateUpdateUserError`. */
export type AbandonmentEmailStateUpdateUserErrorCode =
  | 'ABANDONMENT_NOT_FOUND';

/** Possible error codes that can be returned by `AbandonmentUpdateActivitiesDeliveryStatusesUserError`. */
export type AbandonmentUpdateActivitiesDeliveryStatusesUserErrorCode =
  | 'ABANDONMENT_NOT_FOUND'
  | 'DELIVERY_STATUS_INFO_NOT_FOUND'
  | 'MARKETING_ACTIVITY_NOT_FOUND';

/** Possible account types that a staff member can have. */
export type AccountType =
  | 'COLLABORATOR'
  | 'COLLABORATOR_TEAM_MEMBER'
  | 'INVITED'
  | 'INVITED_STORE_OWNER'
  | 'REGULAR'
  | 'REQUESTED'
  | 'RESTRICTED'
  | 'SAML';

/** The set of valid sort keys for the Adjustments query. */
export type AdjustmentsSortKeys =
  | 'ID'
  | 'TIME';

/** Possible types of app developer. */
export type AppDeveloperType =
  | 'MERCHANT'
  | 'PARTNER'
  | 'SHOPIFY'
  | 'UNKNOWN';

/** The possible categories of an app installation, based on their purpose or the environment they can run in. */
export type AppInstallationCategory =
  | 'CHANNEL'
  | 'POS_EMBEDDED';

/** The levels of privacy of an app installation. */
export type AppInstallationPrivacy =
  | 'PRIVATE'
  | 'PUBLIC';

/** The set of valid sort keys for the AppInstallation query. */
export type AppInstallationSortKeys =
  | 'APP_TITLE'
  | 'ID'
  | 'INSTALLED_AT';

/** The frequency at which the shop is billed for an app subscription. */
export type AppPricingInterval =
  | 'ANNUAL'
  | 'EVERY_30_DAYS';

/** The public-facing category for an app. */
export type AppPublicCategory =
  | 'CUSTOM'
  | 'OTHER'
  | 'PRIVATE'
  | 'PUBLIC';

/** The approval status of the app purchase. */
export type AppPurchaseStatus =
  | 'ACTIVE'
  | 'DECLINED'
  | 'EXPIRED'
  | 'PENDING'
  | 'ACCEPTED';

/** The set of valid sort keys for the AppRevenueAttributionRecord query. */
export type AppRevenueAttributionRecordSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** Represents the billing types of revenue attribution. */
export type AppRevenueAttributionType =
  | 'APPLICATION_PURCHASE'
  | 'APPLICATION_SUBSCRIPTION'
  | 'APPLICATION_USAGE'
  | 'OTHER';

/** Possible error codes that can be returned by `AppRevokeAccessScopesAppRevokeScopeError`. */
export type AppRevokeAccessScopesAppRevokeScopeErrorCode =
  | 'APP_NOT_INSTALLED'
  | 'APPLICATION_CANNOT_BE_FOUND'
  | 'CANNOT_REVOKE_IMPLIED_SCOPES'
  | 'CANNOT_REVOKE_REQUIRED_SCOPES'
  | 'CANNOT_REVOKE_UNDECLARED_SCOPES'
  | 'MISSING_SOURCE_APP'
  | 'UNKNOWN_SCOPES';

/** The replacement behavior when creating an app subscription for a merchant with an already existing app subscription. */
export type AppSubscriptionReplacementBehavior =
  | 'APPLY_IMMEDIATELY'
  | 'APPLY_ON_NEXT_BILLING_CYCLE'
  | 'STANDARD';

/** The set of valid sort keys for the AppSubscription query. */
export type AppSubscriptionSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** The status of the app subscription. */
export type AppSubscriptionStatus =
  | 'ACTIVE'
  | 'CANCELLED'
  | 'DECLINED'
  | 'EXPIRED'
  | 'FROZEN'
  | 'PENDING'
  | 'ACCEPTED';

/** Possible error codes that can be returned by `AppSubscriptionTrialExtendUserError`. */
export type AppSubscriptionTrialExtendUserErrorCode =
  | 'SUBSCRIPTION_NOT_ACTIVE'
  | 'SUBSCRIPTION_NOT_FOUND'
  | 'TRIAL_NOT_ACTIVE';

/** The set of valid sort keys for the AppTransaction query. */
export type AppTransactionSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** Possible error codes that can be returned by `AppUninstallAppUninstallError`. */
export type AppUninstallAppUninstallErrorCode =
  | 'APP_NOT_FOUND'
  | 'APP_NOT_INSTALLED'
  | 'APP_UNINSTALL_ERROR'
  | 'USER_PERMISSIONS_INSUFFICIENT';

/** The set of valid sort keys for the AppUsageRecord query. */
export type AppUsageRecordSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** Possible error codes that can be returned by `ArticleCreateUserError`. */
export type ArticleCreateUserErrorCode =
  | 'AMBIGUOUS_AUTHOR'
  | 'AMBIGUOUS_BLOG'
  | 'AUTHOR_FIELD_REQUIRED'
  | 'AUTHOR_MUST_EXIST'
  | 'BLANK'
  | 'BLOG_REFERENCE_REQUIRED'
  | 'INVALID'
  | 'INVALID_PUBLISH_DATE'
  | 'INVALID_TYPE'
  | 'INVALID_VALUE'
  | 'NOT_FOUND'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'UPLOAD_FAILED';

/** Possible error codes that can be returned by `ArticleDeleteUserError`. */
export type ArticleDeleteUserErrorCode =
  | 'NOT_FOUND';

/** The set of valid sort keys for the Article query. */
export type ArticleSortKeys =
  | 'AUTHOR'
  | 'BLOG_TITLE'
  | 'ID'
  | 'PUBLISHED_AT'
  | 'TITLE'
  | 'UPDATED_AT';

/** Possible sort of tags. */
export type ArticleTagSort =
  | 'ALPHABETICAL'
  | 'POPULAR';

/** Possible error codes that can be returned by `ArticleUpdateUserError`. */
export type ArticleUpdateUserErrorCode =
  | 'AMBIGUOUS_AUTHOR'
  | 'AMBIGUOUS_BLOG'
  | 'AUTHOR_MUST_EXIST'
  | 'BLANK'
  | 'INVALID'
  | 'INVALID_PUBLISH_DATE'
  | 'INVALID_TYPE'
  | 'INVALID_VALUE'
  | 'NOT_FOUND'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'UPLOAD_FAILED';

/** The intended audience for the order status page. */
export type Audience =
  | 'CUSTOMERVIEW'
  | 'MERCHANTVIEW';

/** The set of valid sort keys for the AutomaticDiscount query. */
export type AutomaticDiscountSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** The possible types for a badge. */
export type BadgeType =
  | 'ATTENTION'
  | 'CRITICAL'
  | 'DEFAULT'
  | 'INFO'
  | 'SUCCESS'
  | 'WARNING';

/** The set of valid sort keys for the BalanceTransaction query. */
export type BalanceTransactionSortKeys =
  | 'AMOUNT'
  | 'FEE'
  | 'ID'
  | 'NET'
  | 'ORDER_NAME'
  | 'PAYMENT_METHOD_NAME'
  | 'PAYOUT_DATE'
  | 'PAYOUT_STATUS'
  | 'PROCESSED_AT'
  | 'TRANSACTION_TYPE';

/** The type of bank account holder. */
export type BankAccountHolderType =
  | 'COMPANY'
  | 'INDIVIDUAL';

/** The type of bank account. */
export type BankAccountType =
  | 'CHECKING'
  | 'SAVINGS';

/** The valid types of actions a user should be able to perform in an financial app. */
export type BankingFinanceAppAccess =
  | 'MONEY_MOVEMENT_BLOCKED_MFA'
  | 'MONEY_MOVEMENT_RESTRICTED'
  | 'MOVE_MONEY'
  | 'READ_ACCESS';

/** Possible error codes that can be returned by `BillingAttemptUserError`. */
export type BillingAttemptUserErrorCode =
  | 'BILLING_CYCLE_CHARGE_BEFORE_EXPECTED_DATE'
  | 'BILLING_CYCLE_SKIPPED'
  | 'BLANK'
  | 'CONTRACT_NOT_FOUND'
  | 'CONTRACT_PAUSED'
  | 'CONTRACT_TERMINATED'
  | 'CONTRACT_UNDER_REVIEW'
  | 'CYCLE_INDEX_OUT_OF_RANGE'
  | 'CYCLE_START_DATE_OUT_OF_RANGE'
  | 'INVALID'
  | 'ORIGIN_TIME_BEFORE_CONTRACT_CREATION'
  | 'ORIGIN_TIME_OUT_OF_RANGE'
  | 'PROCESSING_FAILED'
  | 'THROTTLED'
  | 'UPCOMING_CYCLE_LIMIT_EXCEEDED';

/** Possible error codes that can be returned by `BlogCreateUserError`. */
export type BlogCreateUserErrorCode =
  | 'INCLUSION'
  | 'INVALID'
  | 'INVALID_TYPE'
  | 'INVALID_VALUE'
  | 'TOO_LONG';

/** Possible error codes that can be returned by `BlogDeleteUserError`. */
export type BlogDeleteUserErrorCode =
  | 'NOT_FOUND';

/** The set of valid sort keys for the Blog query. */
export type BlogSortKeys =
  | 'HANDLE'
  | 'ID'
  | 'TITLE';

/** Possible error codes that can be returned by `BlogUpdateUserError`. */
export type BlogUpdateUserErrorCode =
  | 'BLANK'
  | 'INCLUSION'
  | 'INVALID'
  | 'NOT_FOUND'
  | 'TOO_LONG';

/** Possible error codes that can be returned by `BulkMutationUserError`. */
export type BulkMutationErrorCode =
  | 'INTERNAL_FILE_SERVER_ERROR'
  | 'INVALID_MUTATION'
  | 'INVALID_STAGED_UPLOAD_FILE'
  | 'LIMIT_REACHED'
  | 'NO_SUCH_FILE'
  | 'OPERATION_IN_PROGRESS';

/** Error codes for failed bulk operations. */
export type BulkOperationErrorCode =
  | 'ACCESS_DENIED'
  | 'INTERNAL_SERVER_ERROR'
  | 'TIMEOUT';

/** The set of valid sort keys for the BulkOperations query. */
export type BulkOperationsSortKeys =
  | 'COMPLETED_AT'
  | 'CREATED_AT';

/** The valid values for the status of a bulk operation. */
export type BulkOperationStatus =
  | 'CANCELED'
  | 'CANCELING'
  | 'COMPLETED'
  | 'CREATED'
  | 'EXPIRED'
  | 'FAILED'
  | 'RUNNING';

/** The valid values for the bulk operation's type. */
export type BulkOperationType =
  | 'MUTATION'
  | 'QUERY';

/** Possible error codes that can be returned by `BulkOperationUserError`. */
export type BulkOperationUserErrorCode =
  | 'INVALID'
  | 'LIMIT_REACHED'
  | 'OPERATION_IN_PROGRESS';

/** Possible error codes that can be returned by `BulkProductResourceFeedbackCreateUserError`. */
export type BulkProductResourceFeedbackCreateUserErrorCode =
  | 'BLANK'
  | 'INVALID'
  | 'LESS_THAN_OR_EQUAL_TO'
  | 'MAXIMUM_FEEDBACK_LIMIT_EXCEEDED'
  | 'NOT_FOUND'
  | 'OUTDATED_FEEDBACK'
  | 'PRESENT'
  | 'PRODUCT_NOT_FOUND';

/** Possible error codes that can be returned by `BusinessCustomerUserError`. */
export type BusinessCustomerErrorCode =
  | 'BLANK'
  | 'FAILED_TO_DELETE'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'INVALID_INPUT'
  | 'LIMIT_REACHED'
  | 'NO_INPUT'
  | 'REQUIRED'
  | 'RESOURCE_NOT_FOUND'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'UNEXPECTED_TYPE';

/** Represents the staged status of a CalculatedShippingLine on a CalculatedOrder. */
export type CalculatedShippingLineStagedStatus =
  | 'ADDED'
  | 'NONE'
  | 'REMOVED';

/** Possible error codes that can be returned by `CarrierServiceCreateUserError`. */
export type CarrierServiceCreateUserErrorCode =
  | 'CARRIER_SERVICE_CREATE_FAILED';

/** Possible error codes that can be returned by `CarrierServiceDeleteUserError`. */
export type CarrierServiceDeleteUserErrorCode =
  | 'CARRIER_SERVICE_DELETE_FAILED';

/** The set of valid sort keys for the CarrierService query. */
export type CarrierServiceSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'UPDATED_AT';

/** Possible error codes that can be returned by `CarrierServiceUpdateUserError`. */
export type CarrierServiceUpdateUserErrorCode =
  | 'CARRIER_SERVICE_UPDATE_FAILED';

/** Possible error codes that can be returned by `CartTransformCreateUserError`. */
export type CartTransformCreateUserErrorCode =
  | 'FUNCTION_ALREADY_REGISTERED'
  | 'FUNCTION_DOES_NOT_IMPLEMENT'
  | 'FUNCTION_NOT_FOUND'
  | 'INPUT_INVALID'
  | 'INVALID_METAFIELDS'
  | 'MISSING_FUNCTION_IDENTIFIER'
  | 'MULTIPLE_FUNCTION_IDENTIFIERS';

/** Possible error codes that can be returned by `CartTransformDeleteUserError`. */
export type CartTransformDeleteUserErrorCode =
  | 'NOT_FOUND'
  | 'UNAUTHORIZED_APP_SCOPE';

/** The set of valid sort keys for the CashActivities query. */
export type CashActivitiesSortKeys =
  | 'ID'
  | 'TIME';

/** The type of adjustment activity. */
export type CashAdjustmentActivityType =
  | 'ADJUSTMENT'
  | 'CASH_PAYOUT'
  | 'CLOSING_ADJUSTMENT';

/** The type of count activity. */
export type CashCountActivityType =
  | 'CLOSING'
  | 'MID_SESSION'
  | 'OPENING';

/** Possible error codes that can be returned by `CashDrawerCreateUserError`. */
export type CashDrawerCreateUserErrorCode =
  | 'CASH_DRAWER_ALREADY_EXISTS'
  | 'INTERNAL_ERROR'
  | 'INVALID_NAME'
  | 'LOCATION_NOT_FOUND'
  | 'NOT_SAVED';

/** Possible error codes that can be returned by `CashDrawerFindOrCreateUserError`. */
export type CashDrawerFindOrCreateUserErrorCode =
  | 'CASH_DRAWER_ASSIGNMENT_ALREADY_EXISTS'
  | 'INTERNAL_ERROR'
  | 'LOCATION_NOT_FOUND'
  | 'NOT_SAVED'
  | 'POINT_OF_SALE_DEVICE_NOT_FOUND';

/** Possible error codes that can be returned by `CashDrawerUpdateUserError`. */
export type CashDrawerUpdateUserErrorCode =
  | 'CASH_DRAWER_ALREADY_EXISTS'
  | 'CASH_DRAWER_NOT_FOUND'
  | 'INTERNAL_ERROR'
  | 'INVALID_NAME'
  | 'NOT_SAVED';

/** Default reason codes for cash management. */
export type CashManagementDefaultReasonCodeEnum =
  | 'AUTO_END_SESSION_LOCATION_CHANGE'
  | 'AUTO_END_SESSION_LOGOUT'
  | 'AUTO_START_SESSION_CHECKOUT'
  | 'CASH_COUNT'
  | 'CASH_PAYOUT'
  | 'CASH_PICKUP'
  | 'CHANGE_CORRECTION'
  | 'PETTY_CASH'
  | 'TIP_PAYOUT';

/** Possible error codes that can be returned by `CashManagementReasonCodeCreateUserError`. */
export type CashManagementReasonCodeCreateUserErrorCode =
  | 'BLANK'
  | 'CODE_ALREADY_EXISTS'
  | 'NOT_SAVED';

/** Possible error codes that can be returned by `CashManagementReasonCodeDeleteUserError`. */
export type CashManagementReasonCodeDeleteUserErrorCode =
  | 'DATABASE_ERROR'
  | 'NOT_DELETABLE'
  | 'NOT_FOUND';

/** System reason codes for cash management. */
export type CashManagementSystemReasonCodeEnum =
  | 'AUTO_END_SESSION_LOCATION_CHANGE'
  | 'AUTO_END_SESSION_LOGOUT'
  | 'AUTO_START_SESSION_CHECKOUT'
  | 'CASH_PAYOUT'
  | 'FLOAT_SETUP'
  | 'OTHER';

/** The set of valid sort keys for the CashTrackingSessions query. */
export type CashTrackingSessionsSortKeys =
  | 'CLOSING_TIME_ASC'
  | 'CLOSING_TIME_DESC'
  | 'ID'
  | 'OPENING_TIME_ASC'
  | 'OPENING_TIME_DESC'
  | 'TOTAL_DISCREPANCY_ASC'
  | 'TOTAL_DISCREPANCY_DESC';

/** The set of valid sort keys for the CashTrackingSessionTransactions query. */
export type CashTrackingSessionTransactionsSortKeys =
  | 'ID'
  | 'PROCESSED_AT';

/** The type of transaction activity. */
export type CashTransactionActivityType =
  | 'CHANGE'
  | 'REFUND'
  | 'SALE';

/** The set of valid sort keys for the Catalog query. */
export type CatalogSortKeys =
  | 'ID'
  | 'RELEVANCE'
  | 'TITLE'
  | 'TYPE';

/** The state of a catalog. */
export type CatalogStatus =
  | 'ACTIVE'
  | 'ARCHIVED'
  | 'DRAFT';

/** The associated catalog's type. */
export type CatalogType =
  | 'APP'
  | 'COMPANY_LOCATION'
  | 'MARKET'
  | 'NONE';

/** Possible error codes that can be returned by `CatalogUserError`. */
export type CatalogUserErrorCode =
  | 'APP_CATALOG_PRICE_LIST_ASSIGNMENT'
  | 'BLANK'
  | 'CANNOT_ADD_MORE_THAN_ONE_MARKET'
  | 'CANNOT_CREATE_APP_CATALOG'
  | 'CANNOT_CREATE_MARKET_CATALOG'
  | 'CANNOT_DELETE_APP_CATALOG'
  | 'CANNOT_DELETE_MARKET_CATALOG'
  | 'CANNOT_MODIFY_APP_CATALOG'
  | 'CANNOT_MODIFY_MARKET_CATALOG'
  | 'CATALOG_CONTEXT_DOES_NOT_SUPPORT_QUANTITY_PRICE_BREAKS'
  | 'CATALOG_CONTEXT_DOES_NOT_SUPPORT_QUANTITY_RULES'
  | 'CATALOG_CONTEXT_LOCKED'
  | 'CATALOG_FAILED_TO_SAVE'
  | 'CATALOG_NOT_FOUND'
  | 'COMPANY_LOCATION_CATALOG_STATUS_PLAN'
  | 'COMPANY_LOCATION_NOT_FOUND'
  | 'CONTEXT_ALREADY_ASSIGNED_TO_CATALOG'
  | 'CONTEXT_CATALOG_LIMIT_REACHED'
  | 'CONTEXT_DRIVER_MISMATCH'
  | 'COUNTRY_CATALOG_PRICE_LIST_ASSIGNMENT'
  | 'COUNTRY_PRICE_LIST_ASSIGNMENT'
  | 'INVALID'
  | 'INVALID_CATALOG_CONTEXT_TYPE'
  | 'INVALID_CONTEXT_CHANGE'
  | 'MANAGED_COUNTRY_BELONGS_TO_ANOTHER_CATALOG'
  | 'MARKET_AND_PRICE_LIST_CURRENCY_MISMATCH'
  | 'MARKET_CATALOG_STATUS'
  | 'MARKET_NOT_FOUND'
  | 'MARKET_TAKEN'
  | 'MUST_PROVIDE_EXACTLY_ONE_CONTEXT_TYPE'
  | 'PRICE_LIST_FAILED_TO_SAVE'
  | 'PRICE_LIST_LOCKED'
  | 'PRICE_LIST_NOT_ALLOWED_FOR_PRIMARY_MARKET'
  | 'PRICE_LIST_NOT_FOUND'
  | 'PUBLICATION_NOT_FOUND'
  | 'REQUIRES_CONTEXTS_TO_ADD_OR_REMOVE'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT'
  | 'UNPERMITTED_ENTITLEMENTS_MARKET_CATALOGS'
  | 'UNSUPPORTED_CATALOG_ACTION';

/** Possible error codes that can be returned by `ChannelCreateUserError`. */
export type ChannelCreateUserErrorCode =
  | 'INVALID'
  | 'NOT_FOUND';

/** Possible error codes that can be returned by `ChannelDeleteUserError`. */
export type ChannelDeleteUserErrorCode =
  | 'INVALID'
  | 'NOT_FOUND';

/** Possible error codes that can be returned by `ChannelFullSyncUserError`. */
export type ChannelFullSyncUserErrorCode =
  | 'INVALID'
  | 'NOT_FOUND';

/** Possible error codes that can be returned by `ChannelUpdateUserError`. */
export type ChannelUpdateUserErrorCode =
  | 'INVALID'
  | 'NOT_FOUND';

/** The container background style. */
export type CheckoutAndAccountsConfigurationBrandingBackground =
  | 'BASE'
  | 'SUBDUED';

/** Possible values for the border. */
export type CheckoutAndAccountsConfigurationBrandingBorder =
  | 'BLOCK_END'
  | 'FULL'
  | 'NONE';

/** The container border style. */
export type CheckoutAndAccountsConfigurationBrandingBorderStyle =
  | 'BASE'
  | 'DASHED'
  | 'DOTTED';

/** The container border width. */
export type CheckoutAndAccountsConfigurationBrandingBorderWidth =
  | 'BASE'
  | 'LARGE'
  | 'LARGE_100'
  | 'LARGE_200';

/** Possible values for the cart link content type for the header. */
export type CheckoutAndAccountsConfigurationBrandingCartLinkContentType =
  | 'ICON'
  | 'IMAGE'
  | 'TEXT';

/** The options for customizing the corner radius of checkout-related objects. Examples include the primary button, the name text fields and the sections within the main area (if they have borders). */
export type CheckoutAndAccountsConfigurationBrandingCornerRadius =
  | 'BASE'
  | 'LARGE'
  | 'NONE'
  | 'SMALL';

/** The font loading strategy determines how a font face is displayed after it is loaded or failed to load. For more information: <https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display>. */
export type CheckoutAndAccountsConfigurationBrandingFontLoadingStrategy =
  | 'AUTO'
  | 'BLOCK'
  | 'FALLBACK'
  | 'OPTIONAL'
  | 'SWAP';

/** Possible values for the footer alignment. */
export type CheckoutAndAccountsConfigurationBrandingFooterAlignment =
  | 'CENTER'
  | 'END'
  | 'START';

/** Possible values for the footer position. */
export type CheckoutAndAccountsConfigurationBrandingFooterPosition =
  | 'END'
  | 'INLINE';

/** The possible header alignments. */
export type CheckoutAndAccountsConfigurationBrandingHeaderAlignment =
  | 'CENTER'
  | 'END'
  | 'START';

/** The possible header positions. */
export type CheckoutAndAccountsConfigurationBrandingHeaderPosition =
  | 'INLINE'
  | 'INLINE_SECONDARY'
  | 'START';

/** The label position options. */
export type CheckoutAndAccountsConfigurationBrandingLabelPosition =
  | 'INSIDE'
  | 'OUTSIDE';

/** The merchandise thumbnail badge background. */
export type CheckoutAndAccountsConfigurationBrandingMerchandiseThumbnailBadgeBackground =
  | 'ACCENT'
  | 'BASE';

/** Possible values for object fit. */
export type CheckoutAndAccountsConfigurationBrandingObjectFit =
  | 'CONTAIN'
  | 'COVER';

/** The container shadow. */
export type CheckoutAndAccountsConfigurationBrandingShadow =
  | 'BASE'
  | 'LARGE_100'
  | 'LARGE_200'
  | 'SMALL_100'
  | 'SMALL_200';

/** Possible choices to override corner radius customizations on all applicable objects. Note that this selection can only be used to set the override to `NONE` (0px). */
export type CheckoutAndAccountsConfigurationBrandingSharedCornerRadius =
  | 'NONE';

/** Possible values for the simple border. */
export type CheckoutAndAccountsConfigurationBrandingSimpleBorder =
  | 'FULL'
  | 'NONE';

/** Possible values for the spacing. */
export type CheckoutAndAccountsConfigurationBrandingSpacing =
  | 'BASE'
  | 'EXTRA_LOOSE'
  | 'EXTRA_TIGHT'
  | 'LOOSE'
  | 'NONE'
  | 'TIGHT';

/** The spacing between UI elements. */
export type CheckoutAndAccountsConfigurationBrandingSpacingKeyword =
  | 'BASE'
  | 'LARGE'
  | 'LARGE_100'
  | 'LARGE_200'
  | 'LARGE_300'
  | 'LARGE_400'
  | 'LARGE_500'
  | 'NONE'
  | 'SMALL'
  | 'SMALL_100'
  | 'SMALL_200'
  | 'SMALL_300'
  | 'SMALL_400'
  | 'SMALL_500';

/** The font selection. */
export type CheckoutAndAccountsConfigurationBrandingTypographyFont =
  | 'PRIMARY'
  | 'SECONDARY';

/** Possible values for the typography kerning. */
export type CheckoutAndAccountsConfigurationBrandingTypographyKerning =
  | 'BASE'
  | 'EXTRA_LOOSE'
  | 'LOOSE';

/** Possible values for the typography letter case. */
export type CheckoutAndAccountsConfigurationBrandingTypographyLetterCase =
  | 'LOWER'
  | 'NONE'
  | 'TITLE'
  | 'UPPER';

/** Possible choices for the font size. */
export type CheckoutAndAccountsConfigurationBrandingTypographySize =
  | 'BASE'
  | 'EXTRA_EXTRA_LARGE'
  | 'EXTRA_LARGE'
  | 'EXTRA_SMALL'
  | 'LARGE'
  | 'MEDIUM'
  | 'SMALL';

/** Possible values for the font weight. */
export type CheckoutAndAccountsConfigurationBrandingTypographyWeight =
  | 'BASE'
  | 'BOLD';

/** Possible visibility states. */
export type CheckoutAndAccountsConfigurationBrandingVisibility =
  | 'HIDDEN'
  | 'VISIBLE';

/** The set of valid sort keys for the CheckoutAndAccountsConfigurationsGraphQL query. */
export type CheckoutAndAccountsConfigurationsGraphQLSortKeys =
  | 'CREATED_AT'
  | 'EDITED_AT'
  | 'ID'
  | 'IS_PUBLISHED';

/** Possible error codes that can be returned by `CheckoutAndAccountsConfigurationUserError`. */
export type CheckoutAndAccountsConfigurationUserErrorCode =
  | 'BLANK'
  | 'INTERNAL_SERVER_ERROR'
  | 'INVALID'
  | 'MISSING'
  | 'NOT_FOUND'
  | 'TRANSIENT';

/** The container background style. */
export type CheckoutBrandingBackground =
  | 'BASE'
  | 'SUBDUED'
  | 'TRANSPARENT';

/** Possible values for the background style. */
export type CheckoutBrandingBackgroundStyle =
  | 'NONE'
  | 'SOLID';

/** Possible values for the border. */
export type CheckoutBrandingBorder =
  | 'BLOCK_END'
  | 'FULL'
  | 'NONE';

/** The container border style. */
export type CheckoutBrandingBorderStyle =
  | 'BASE'
  | 'DASHED'
  | 'DOTTED';

/** The container border width. */
export type CheckoutBrandingBorderWidth =
  | 'BASE'
  | 'LARGE'
  | 'LARGE_100'
  | 'LARGE_200';

/** Possible values for the cart link content type for the header. */
export type CheckoutBrandingCartLinkContentType =
  | 'ICON'
  | 'IMAGE'
  | 'TEXT';

/** The possible color schemes. */
export type CheckoutBrandingColorSchemeSelection =
  | 'COLOR_SCHEME1'
  | 'COLOR_SCHEME2'
  | 'COLOR_SCHEME3'
  | 'COLOR_SCHEME4'
  | 'COLOR_SCHEME5'
  | 'COLOR_SCHEME6'
  | 'TRANSPARENT';

/** The possible colors. */
export type CheckoutBrandingColorSelection =
  | 'TRANSPARENT';

/** The options for customizing the corner radius of checkout-related objects. Examples include the primary button, the name text fields and the sections within the main area (if they have borders). Refer to this complete [list](https://shopify.dev/docs/api/admin-graphql/latest/en... */
export type CheckoutBrandingCornerRadius =
  | 'BASE'
  | 'LARGE'
  | 'NONE'
  | 'SMALL';

/** The font loading strategy determines how a font face is displayed after it is loaded or failed to load. For more information: <https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display>. */
export type CheckoutBrandingFontLoadingStrategy =
  | 'AUTO'
  | 'BLOCK'
  | 'FALLBACK'
  | 'OPTIONAL'
  | 'SWAP';

/** Possible values for the footer alignment. */
export type CheckoutBrandingFooterAlignment =
  | 'CENTER'
  | 'END'
  | 'START';

/** Possible values for the footer position. */
export type CheckoutBrandingFooterPosition =
  | 'END'
  | 'INLINE';

/** Possible choices to override corner radius customizations on all applicable objects. Note that this selection can only be used to set the override to `NONE` (0px). */
export type CheckoutBrandingGlobalCornerRadius =
  | 'NONE';

/** The possible header alignments. */
export type CheckoutBrandingHeaderAlignment =
  | 'CENTER'
  | 'END'
  | 'START';

/** The possible header positions. */
export type CheckoutBrandingHeaderPosition =
  | 'INLINE'
  | 'INLINE_SECONDARY'
  | 'START';

/** Possible values for the label position. */
export type CheckoutBrandingLabelPosition =
  | 'INSIDE'
  | 'OUTSIDE';

/** The merchandise thumbnail badge background. */
export type CheckoutBrandingMerchandiseThumbnailBadgeBackground =
  | 'ACCENT'
  | 'BASE';

/** Possible values for object fit. */
export type CheckoutBrandingObjectFit =
  | 'CONTAIN'
  | 'COVER';

/** The container shadow. */
export type CheckoutBrandingShadow =
  | 'BASE'
  | 'LARGE_100'
  | 'LARGE_200'
  | 'SMALL_100'
  | 'SMALL_200';

/** Possible values for the simple border. */
export type CheckoutBrandingSimpleBorder =
  | 'FULL'
  | 'NONE';

/** Possible values for the spacing. */
export type CheckoutBrandingSpacing =
  | 'BASE'
  | 'EXTRA_LOOSE'
  | 'EXTRA_TIGHT'
  | 'LOOSE'
  | 'NONE'
  | 'TIGHT';

/** The spacing between UI elements. */
export type CheckoutBrandingSpacingKeyword =
  | 'BASE'
  | 'LARGE'
  | 'LARGE_100'
  | 'LARGE_200'
  | 'LARGE_300'
  | 'LARGE_400'
  | 'LARGE_500'
  | 'NONE'
  | 'SMALL'
  | 'SMALL_100'
  | 'SMALL_200'
  | 'SMALL_300'
  | 'SMALL_400'
  | 'SMALL_500';

/** The font selection. */
export type CheckoutBrandingTypographyFont =
  | 'PRIMARY'
  | 'SECONDARY';

/** Possible values for the typography kerning. */
export type CheckoutBrandingTypographyKerning =
  | 'BASE'
  | 'EXTRA_LOOSE'
  | 'LOOSE';

/** Possible values for the typography letter case. */
export type CheckoutBrandingTypographyLetterCase =
  | 'LOWER'
  | 'NONE'
  | 'TITLE'
  | 'UPPER';

/** Possible choices for the font size. */
export type CheckoutBrandingTypographySize =
  | 'BASE'
  | 'EXTRA_EXTRA_LARGE'
  | 'EXTRA_LARGE'
  | 'EXTRA_SMALL'
  | 'LARGE'
  | 'MEDIUM'
  | 'SMALL';

/** Possible values for the font weight. */
export type CheckoutBrandingTypographyWeight =
  | 'BASE'
  | 'BOLD';

/** Possible error codes that can be returned by `CheckoutBrandingUpsertUserError`. */
export type CheckoutBrandingUpsertUserErrorCode =
  | 'INTERNAL_ERROR';

/** Possible visibility states. */
export type CheckoutBrandingVisibility =
  | 'HIDDEN'
  | 'VISIBLE';

/** The set of valid sort keys for the CheckoutProfile query. */
export type CheckoutProfileSortKeys =
  | 'CREATED_AT'
  | 'EDITED_AT'
  | 'ID'
  | 'IS_PUBLISHED'
  | 'UPDATED_AT';

/** The set of valid sort keys for the CodeDiscount query. */
export type CodeDiscountSortKeys =
  | 'CREATED_AT'
  | 'ENDS_AT'
  | 'ID'
  | 'RELEVANCE'
  | 'STARTS_AT'
  | 'TITLE'
  | 'UPDATED_AT';

/** Possible error codes that can be returned by `CollectionAddProductsV2UserError`. */
export type CollectionAddProductsV2UserErrorCode =
  | 'CANT_ADD_TO_SMART_COLLECTION'
  | 'COLLECTION_DOES_NOT_EXIST';

/** The role a collection plays in a duplication operation. */
export type CollectionDuplicateOperationRole =
  | 'SOURCE'
  | 'TARGET';

/** Possible error codes that can be returned by `CollectionDuplicateUserError`. */
export type CollectionDuplicateUserErrorCode =
  | 'COLLECTION_NOT_FOUND';

/** Possible error codes that can be returned by `CollectionReorderProductsUserError`. */
export type CollectionReorderProductsUserErrorCode =
  | 'COLLECTION_NOT_FOUND'
  | 'INVALID_MOVE'
  | 'MANUALLY_SORTED_COLLECTION'
  | 'TOO_MANY_ATTEMPTS_TO_REORDER_PRODUCTS';

/** Specifies the attribute of a product being used to populate the smart collection. */
export type CollectionRuleColumn =
  | 'IS_PRICE_REDUCED'
  | 'PRODUCT_CATEGORY_ID'
  | 'PRODUCT_CATEGORY_ID_WITH_DESCENDANTS'
  | 'PRODUCT_METAFIELD_DEFINITION'
  | 'PRODUCT_TAXONOMY_NODE_ID'
  | 'TAG'
  | 'TITLE'
  | 'TYPE'
  | 'VARIANT_COMPARE_AT_PRICE'
  | 'VARIANT_INVENTORY'
  | 'VARIANT_METAFIELD_DEFINITION'
  | 'VARIANT_PRICE'
  | 'VARIANT_TITLE'
  | 'VARIANT_WEIGHT'
  | 'VENDOR';

/** Specifies the relationship between the `column` and the `condition`. */
export type CollectionRuleRelation =
  | 'CONTAINS'
  | 'ENDS_WITH'
  | 'EQUALS'
  | 'GREATER_THAN'
  | 'IS_NOT_SET'
  | 'IS_SET'
  | 'LESS_THAN'
  | 'NOT_CONTAINS'
  | 'NOT_EQUALS'
  | 'STARTS_WITH';

/** The set of valid sort keys for the Collection query. */
export type CollectionSortKeys =
  | 'ID'
  | 'RELEVANCE'
  | 'TITLE'
  | 'UPDATED_AT';

/** Specifies the sort order for the products in the collection. */
export type CollectionSortOrder =
  | 'ALPHA_ASC'
  | 'ALPHA_DESC'
  | 'BEST_SELLING'
  | 'CREATED'
  | 'CREATED_DESC'
  | 'MANUAL'
  | 'PRICE_ASC'
  | 'PRICE_DESC';

/** The data type of a column. */
export type ColumnDataType =
  | 'ARRAY'
  | 'BOOLEAN'
  | 'COLOR'
  | 'DAY_DURATION'
  | 'DAY_OF_WEEK'
  | 'DAY_TIMESTAMP'
  | 'DECIMAL'
  | 'FLOAT'
  | 'HOUR_DURATION'
  | 'HOUR_OF_DAY'
  | 'HOUR_TIMESTAMP'
  | 'IDENTITY'
  | 'INTEGER'
  | 'MILLISECOND_DURATION'
  | 'MINUTE_DURATION'
  | 'MINUTE_TIMESTAMP'
  | 'MONEY'
  | 'MONTH_OF_YEAR'
  | 'MONTH_TIMESTAMP'
  | 'PERCENT'
  | 'QUARTER_TIMESTAMP'
  | 'RATING'
  | 'SECOND_DURATION'
  | 'SECOND_TIMESTAMP'
  | 'STRING'
  | 'STRING_IDENTITY'
  | 'TIMESTAMP'
  | 'UNSPECIFIED'
  | 'WEEK_OF_YEAR'
  | 'WEEK_TIMESTAMP'
  | 'YEAR_TIMESTAMP';

/** The role of the combined listing. */
export type CombinedListingsRole =
  | 'CHILD'
  | 'PARENT';

/** Possible error codes that can be returned by `CombinedListingUpdateUserError`. */
export type CombinedListingUpdateUserErrorCode =
  | 'CANNOT_HAVE_DUPLICATED_PRODUCTS'
  | 'CANNOT_HAVE_PARENT_AS_CHILD'
  | 'CANNOT_HAVE_REPEATED_OPTION_VALUES'
  | 'CANNOT_HAVE_REPEATED_OPTIONS'
  | 'CANT_ADD_OPTIONS_VALUES_IF_ALREADY_EXISTS'
  | 'COMBINED_LISTINGS_NOT_ENABLED'
  | 'EDIT_AND_REMOVE_ON_SAME_PRODUCTS'
  | 'FAILED_TO_ADD_PRODUCTS'
  | 'FAILED_TO_REMOVE_PRODUCTS'
  | 'FAILED_TO_UPDATE_PRODUCTS'
  | 'LINKED_METAFIELD_CANNOT_BE_CHANGED'
  | 'LINKED_METAFIELD_VALUE_MISSING'
  | 'LINKED_METAFIELDS_CANNOT_BE_REPEATED'
  | 'LINKED_OPTIONS_NOT_SUPPORTED_FOR_SHOP'
  | 'MISSING_OPTION_VALUES'
  | 'MUST_HAVE_SELECTED_OPTION_VALUES'
  | 'OPTION_NAME_CANNOT_BE_BLANK'
  | 'OPTION_NAME_CONTAINS_INVALID_CHARACTERS'
  | 'OPTION_NOT_FOUND'
  | 'OPTION_VALUES_CANNOT_BE_BLANK'
  | 'OPTION_VALUES_CANNOT_BE_EMPTY'
  | 'OPTION_VALUES_MUST_BE_COMPLETE'
  | 'OPTIONS_MUST_BE_EQUAL_TO_THE_OTHER_COMPONENTS'
  | 'PARENT_PRODUCT_CANNOT_BE_COMBINED_LISTING_CHILD'
  | 'PARENT_PRODUCT_MUST_BE_A_COMBINED_LISTING'
  | 'PARENT_PRODUCT_MUST_HAVE_CATEGORY'
  | 'PARENT_PRODUCT_NOT_FOUND'
  | 'PRODUCT_IS_ALREADY_A_CHILD'
  | 'PRODUCT_MEMBERSHIP_NOT_FOUND'
  | 'PRODUCT_NOT_FOUND'
  | 'TITLE_TOO_LONG'
  | 'TOO_MANY_PRODUCTS'
  | 'TOO_MANY_VARIANTS'
  | 'UNEXPECTED_ERROR';

/** Possible error codes that can be returned by `CommentApproveUserError`. */
export type CommentApproveUserErrorCode =
  | 'NOT_FOUND';

/** Possible error codes that can be returned by `CommentDeleteUserError`. */
export type CommentDeleteUserErrorCode =
  | 'NOT_FOUND';

/** Possible error codes that can be returned by `CommentNotSpamUserError`. */
export type CommentNotSpamUserErrorCode =
  | 'NOT_FOUND';

/** Possible comment policies for a blog. */
export type CommentPolicy =
  | 'AUTO_PUBLISHED'
  | 'CLOSED'
  | 'MODERATED';

/** The set of valid sort keys for the Comment query. */
export type CommentSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** Possible error codes that can be returned by `CommentSpamUserError`. */
export type CommentSpamUserErrorCode =
  | 'NOT_FOUND';

/** The status of a comment. */
export type CommentStatus =
  | 'PENDING'
  | 'PUBLISHED'
  | 'REMOVED'
  | 'SPAM'
  | 'UNAPPROVED';

/** The valid values for the address type of a company. */
export type CompanyAddressType =
  | 'BILLING'
  | 'SHIPPING';

/** The set of valid sort keys for the CompanyContactRoleAssignment query. */
export type CompanyContactRoleAssignmentSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'LOCATION_NAME'
  | 'UPDATED_AT';

/** The set of valid sort keys for the CompanyContactRole query. */
export type CompanyContactRoleSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'UPDATED_AT';

/** The set of valid sort keys for the CompanyContact query. */
export type CompanyContactSortKeys =
  | 'COMPANY_ID'
  | 'CREATED_AT'
  | 'EMAIL'
  | 'ID'
  | 'NAME'
  | 'NAME_EMAIL'
  | 'RELEVANCE'
  | 'TITLE'
  | 'UPDATED_AT';

/** The set of valid sort keys for the CompanyLocation query. */
export type CompanyLocationSortKeys =
  | 'COMPANY_AND_LOCATION_NAME'
  | 'COMPANY_ID'
  | 'CREATED_AT'
  | 'ID'
  | 'NAME'
  | 'RELEVANCE'
  | 'UPDATED_AT';

/** The set of valid sort keys for the CompanyLocationStaffMemberAssignment query. */
export type CompanyLocationStaffMemberAssignmentSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'UPDATED_AT';

/** The set of valid sort keys for the Company query. */
export type CompanySortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'NAME'
  | 'ORDER_COUNT'
  | 'SINCE_DATE'
  | 'TOTAL_SPENT'
  | 'UPDATED_AT';

/** Possible error codes that can be returned by `ConsentPolicyError`. */
export type ConsentPolicyErrorCode =
  | 'COUNTRY_CODE_REQUIRED'
  | 'REGION_CODE_MUST_MATCH_COUNTRY_CODE'
  | 'REGION_CODE_REQUIRED'
  | 'SHOPIFY_COOKIE_BANNER_NOT_DISABLED'
  | 'UNSUPORTED_CONSENT_POLICY';

/** The precision of the value returned by a count field. */
export type CountPrecision =
  | 'AT_LEAST'
  | 'EXACT';

/** The code designating a country/region, which generally follows ISO 3166-1 alpha-2 guidelines. If a territory doesn't have a country code value in the `CountryCode` enum, then it might be considered a subdivision of another country. For example, the territories associated with ... */
export type CountryCode =
  | 'AC'
  | 'AD'
  | 'AE'
  | 'AF'
  | 'AG'
  | 'AI'
  | 'AL'
  | 'AM'
  | 'AN'
  | 'AO'
  | 'AR'
  | 'AT'
  | 'AU'
  | 'AW'
  | 'AX'
  | 'AZ'
  | 'BA'
  | 'BB'
  | 'BD'
  | 'BE'
  | 'BF'
  | 'BG'
  | 'BH'
  | 'BI'
  | 'BJ'
  | 'BL'
  | 'BM'
  | 'BN'
  | 'BO'
  | 'BQ'
  | 'BR'
  | 'BS'
  | 'BT'
  | 'BV'
  | 'BW'
  | 'BY'
  | 'BZ'
  | 'CA'
  | 'CC'
  | 'CD'
  | 'CF'
  | 'CG'
  | 'CH'
  | 'CI'
  | 'CK'
  | 'CL'
  | 'CM'
  | 'CN'
  | 'CO'
  | 'CR'
  | 'CU'
  | 'CV'
  | 'CW'
  | 'CX'
  | 'CY'
  | 'CZ'
  | 'DE'
  | 'DJ'
  | 'DK'
  | 'DM'
  | 'DO'
  | 'DZ'
  | 'EC'
  | 'EE'
  | 'EG'
  | 'EH'
  | 'ER'
  | 'ES'
  | 'ET'
  | 'FI'
  | 'FJ'
  | 'FK'
  | 'FO'
  | 'FR'
  | 'GA'
  | 'GB'
  | 'GD'
  | 'GE'
  | 'GF'
  | 'GG'
  | 'GH'
  | 'GI'
  | 'GL'
  | 'GM'
  | 'GN'
  | 'GP'
  | 'GQ'
  | 'GR'
  | 'GS'
  | 'GT'
  | 'GW'
  | 'GY'
  | 'HK'
  | 'HM'
  | 'HN'
  | 'HR'
  | 'HT'
  | 'HU'
  | 'ID'
  | 'IE'
  | 'IL'
  | 'IM'
  | 'IN'
  | 'IO'
  | 'IQ'
  | 'IR'
  | 'IS'
  | 'IT'
  | 'JE'
  | 'JM'
  | 'JO'
  | 'JP'
  | 'KE'
  | 'KG'
  | 'KH'
  | 'KI'
  | 'KM'
  | 'KN'
  | 'KP'
  | 'KR'
  | 'KW'
  | 'KY'
  | 'KZ'
  | 'LA'
  | 'LB'
  | 'LC'
  | 'LI'
  | 'LK'
  | 'LR'
  | 'LS'
  | 'LT'
  | 'LU'
  | 'LV'
  | 'LY'
  | 'MA'
  | 'MC'
  | 'MD'
  | 'ME'
  | 'MF'
  | 'MG'
  | 'MK'
  | 'ML'
  | 'MM'
  | 'MN'
  | 'MO'
  | 'MQ'
  | 'MR'
  | 'MS'
  | 'MT'
  | 'MU'
  | 'MV'
  | 'MW'
  | 'MX'
  | 'MY'
  | 'MZ'
  | 'NA'
  | 'NC'
  | 'NE'
  | 'NF'
  | 'NG'
  | 'NI'
  | 'NL'
  | 'NO'
  | 'NP'
  | 'NR'
  | 'NU'
  | 'NZ'
  | 'OM'
  | 'PA'
  | 'PE'
  | 'PF'
  | 'PG'
  | 'PH'
  | 'PK'
  | 'PL'
  | 'PM'
  | 'PN'
  | 'PS'
  | 'PT'
  | 'PY'
  | 'QA'
  | 'RE'
  | 'RO'
  | 'RS'
  | 'RU'
  | 'RW'
  | 'SA'
  | 'SB'
  | 'SC'
  | 'SD'
  | 'SE'
  | 'SG'
  | 'SH'
  | 'SI'
  | 'SJ'
  | 'SK'
  | 'SL'
  | 'SM'
  | 'SN'
  | 'SO'
  | 'SR'
  | 'SS'
  | 'ST'
  | 'SV'
  | 'SX'
  | 'SY'
  | 'SZ'
  | 'TA'
  | 'TC'
  | 'TD'
  | 'TF'
  | 'TG'
  | 'TH'
  | 'TJ'
  | 'TK'
  | 'TL'
  | 'TM'
  | 'TN'
  | 'TO'
  | 'TR'
  | 'TT'
  | 'TV'
  | 'TW'
  | 'TZ'
  | 'UA'
  | 'UG'
  | 'UM'
  | 'US'
  | 'UY'
  | 'UZ'
  | 'VA'
  | 'VC'
  | 'VE'
  | 'VG'
  | 'VN'
  | 'VU'
  | 'WF'
  | 'WS'
  | 'XK'
  | 'YE'
  | 'YT'
  | 'ZA'
  | 'ZM'
  | 'ZW'
  | 'ZZ';

/** The part of the image that should remain after cropping. */
export type CropRegion =
  | 'BOTTOM'
  | 'CENTER'
  | 'LEFT'
  | 'RIGHT'
  | 'TOP';

/** The currency codes that represent the world currencies throughout the Admin API. Currency codes include [standard ISO 4217 codes](https://en.wikipedia.org/wiki/ISO_4217), legacy codes, non-standard codes, digital currency codes. */
export type CurrencyCode =
  | 'AED'
  | 'AFN'
  | 'ALL'
  | 'AMD'
  | 'ANG'
  | 'AOA'
  | 'ARS'
  | 'AUD'
  | 'AWG'
  | 'AZN'
  | 'BAM'
  | 'BBD'
  | 'BDT'
  | 'BGN'
  | 'BHD'
  | 'BIF'
  | 'BMD'
  | 'BND'
  | 'BOB'
  | 'BRL'
  | 'BSD'
  | 'BTN'
  | 'BWP'
  | 'BYN'
  | 'BZD'
  | 'CAD'
  | 'CDF'
  | 'CHF'
  | 'CLP'
  | 'CNY'
  | 'COP'
  | 'CRC'
  | 'CVE'
  | 'CZK'
  | 'DJF'
  | 'DKK'
  | 'DOP'
  | 'DZD'
  | 'EGP'
  | 'ERN'
  | 'ETB'
  | 'EUR'
  | 'FJD'
  | 'FKP'
  | 'GBP'
  | 'GEL'
  | 'GHS'
  | 'GIP'
  | 'GMD'
  | 'GNF'
  | 'GTQ'
  | 'GYD'
  | 'HKD'
  | 'HNL'
  | 'HRK'
  | 'HTG'
  | 'HUF'
  | 'IDR'
  | 'ILS'
  | 'INR'
  | 'IQD'
  | 'IRR'
  | 'ISK'
  | 'JEP'
  | 'JMD'
  | 'JOD'
  | 'JPY'
  | 'KES'
  | 'KGS'
  | 'KHR'
  | 'KID'
  | 'KMF'
  | 'KRW'
  | 'KWD'
  | 'KYD'
  | 'KZT'
  | 'LAK'
  | 'LBP'
  | 'LKR'
  | 'LRD'
  | 'LSL'
  | 'LTL'
  | 'LVL'
  | 'LYD'
  | 'MAD'
  | 'MDL'
  | 'MGA'
  | 'MKD'
  | 'MMK'
  | 'MNT'
  | 'MOP'
  | 'MRU'
  | 'MUR'
  | 'MVR'
  | 'MWK'
  | 'MXN'
  | 'MYR'
  | 'MZN'
  | 'NAD'
  | 'NGN'
  | 'NIO'
  | 'NOK'
  | 'NPR'
  | 'NZD'
  | 'OMR'
  | 'PAB'
  | 'PEN'
  | 'PGK'
  | 'PHP'
  | 'PKR'
  | 'PLN'
  | 'PYG'
  | 'QAR'
  | 'RON'
  | 'RSD'
  | 'RUB'
  | 'RWF'
  | 'SAR'
  | 'SBD'
  | 'SCR'
  | 'SDG'
  | 'SEK'
  | 'SGD'
  | 'SHP'
  | 'SLL'
  | 'SOS'
  | 'SRD'
  | 'SSP'
  | 'STN'
  | 'SYP'
  | 'SZL'
  | 'THB'
  | 'TJS'
  | 'TMT'
  | 'TND'
  | 'TOP'
  | 'TRY'
  | 'TTD'
  | 'TWD'
  | 'TZS'
  | 'UAH'
  | 'UGX'
  | 'USD'
  | 'USDC'
  | 'UYU'
  | 'UZS'
  | 'VED'
  | 'VES'
  | 'VND'
  | 'VUV'
  | 'WST'
  | 'XAF'
  | 'XCD'
  | 'XOF'
  | 'XPF'
  | 'XXX'
  | 'YER'
  | 'ZAR'
  | 'ZMW'
  | 'BYR'
  | 'STD'
  | 'VEF';

/** The type of customer account native page. */
export type CustomerAccountNativePagePageType =
  | 'NATIVE_ORDERS'
  | 'NATIVE_PROFILE'
  | 'NATIVE_SETTINGS'
  | 'UNKNOWN';

/** The login redirection target for customer accounts. */
export type CustomerAccountsVersion =
  | 'CLASSIC'
  | 'NEW_CUSTOMER_ACCOUNTS';

/** Possible error codes that can be returned by `CustomerCancelDataErasureUserError`. */
export type CustomerCancelDataErasureErrorCode =
  | 'DOES_NOT_EXIST'
  | 'FAILED_TO_CANCEL'
  | 'NOT_BEING_ERASED'
  | 'UNAUTHORIZED_CANCELLATION';

/** The source that collected the customer's consent to receive marketing materials. */
export type CustomerConsentCollectedFrom =
  | 'OTHER'
  | 'SHOPIFY';

/** Possible marketing states for the customer’s email address. */
export type CustomerEmailAddressMarketingState =
  | 'INVALID'
  | 'NOT_SUBSCRIBED'
  | 'PENDING'
  | 'SUBSCRIBED'
  | 'UNSUBSCRIBED';

/** The different levels related to whether a customer has opted in to having their opened emails tracked. */
export type CustomerEmailAddressOpenTrackingLevel =
  | 'OPTED_IN'
  | 'OPTED_OUT'
  | 'UNKNOWN';

/** Possible error codes that can be returned by `CustomerEmailMarketingConsentUpdateUserError`. */
export type CustomerEmailMarketingConsentUpdateUserErrorCode =
  | 'INCLUSION'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'MISSING_ARGUMENT';

/** The possible email marketing states for a customer. */
export type CustomerEmailMarketingState =
  | 'INVALID'
  | 'NOT_SUBSCRIBED'
  | 'PENDING'
  | 'REDACTED'
  | 'SUBSCRIBED'
  | 'UNSUBSCRIBED';

/** The possible values for the marketing subscription opt-in level enabled at the time the customer consented to receive marketing information. */
export type CustomerMarketingOptInLevel =
  | 'CONFIRMED_OPT_IN'
  | 'SINGLE_OPT_IN'
  | 'UNKNOWN';

/** Possible error codes that can be returned by `CustomerMergeUserError`. */
export type CustomerMergeErrorCode =
  | 'CUSTOMER_HAS_GIFT_CARDS'
  | 'INTERNAL_ERROR'
  | 'INVALID_CUSTOMER'
  | 'INVALID_CUSTOMER_ID'
  | 'MISSING_OVERRIDE_ATTRIBUTE'
  | 'OVERRIDE_ATTRIBUTE_INVALID';

/** The types of the hard blockers preventing a customer from being merged to another customer. */
export type CustomerMergeErrorFieldType =
  | 'COMPANY_CONTACT'
  | 'CUSTOMER_PAYMENT_METHODS'
  | 'DELETED_AT'
  | 'GIFT_CARDS'
  | 'MERGE_IN_PROGRESS'
  | 'MULTIPASS_IDENTIFIER'
  | 'OVERRIDE_FIELDS'
  | 'PENDING_DATA_REQUEST'
  | 'REDACTED_AT'
  | 'STORE_CREDIT'
  | 'SUBSCRIPTIONS';

/** The status of the customer merge request. */
export type CustomerMergeRequestStatus =
  | 'COMPLETED'
  | 'FAILED'
  | 'IN_PROGRESS'
  | 'REQUESTED';

/** Possible error codes that can be returned by `CustomerPaymentMethodGetUpdateUrlUserError`. */
export type CustomerPaymentMethodGetUpdateUrlUserErrorCode =
  | 'CUSTOMER_DOES_NOT_EXIST'
  | 'INVALID_INSTRUMENT'
  | 'PAYMENT_METHOD_DOES_NOT_EXIST'
  | 'TOO_MANY_REQUESTS';

/** Possible error codes that can be returned by `CustomerPaymentMethodRemoteUserError`. */
export type CustomerPaymentMethodRemoteUserErrorCode =
  | 'AUTHORIZE_NET_NOT_ENABLED_FOR_SUBSCRIPTIONS'
  | 'BRAINTREE_NOT_ENABLED_FOR_SUBSCRIPTIONS'
  | 'EXACTLY_ONE_REMOTE_REFERENCE_REQUIRED'
  | 'INVALID'
  | 'PRESENT'
  | 'TAKEN';

/** The revocation reason types for a customer payment method. */
export type CustomerPaymentMethodRevocationReason =
  | 'AUTHORIZE_NET_GATEWAY_NOT_ENABLED'
  | 'AUTHORIZE_NET_RETURNED_NO_PAYMENT_METHOD'
  | 'BRAINTREE_API_AUTHENTICATION_ERROR'
  | 'BRAINTREE_GATEWAY_NOT_ENABLED'
  | 'BRAINTREE_PAYMENT_METHOD_NOT_CARD'
  | 'BRAINTREE_RETURNED_NO_PAYMENT_METHOD'
  | 'CUSTOMER_REDACTED'
  | 'CVV_ATTEMPTS_LIMIT_EXCEEDED'
  | 'FAILED_TO_RETRIEVE_BILLING_ADDRESS'
  | 'FAILED_TO_UPDATE_CREDIT_CARD'
  | 'MANUALLY_REVOKED'
  | 'MERGED'
  | 'PAYMENT_METHOD_VERIFICATION_FAILED'
  | 'STRIPE_API_AUTHENTICATION_ERROR'
  | 'STRIPE_API_INVALID_REQUEST_ERROR'
  | 'STRIPE_GATEWAY_NOT_ENABLED'
  | 'STRIPE_PAYMENT_METHOD_NOT_CARD'
  | 'STRIPE_RETURNED_NO_PAYMENT_METHOD'
  | 'THREE_D_SECURE_FLOW_IN_VERIFICATION_NOT_IMPLEMENTED'
  | 'TOO_MANY_CONSECUTIVE_FAILURES';

/** Possible error codes that can be returned by `CustomerPaymentMethodUserError`. */
export type CustomerPaymentMethodUserErrorCode =
  | 'INVALID'
  | 'PRESENT'
  | 'TAKEN';

/** The valid tiers for the predicted spend of a customer with a shop. */
export type CustomerPredictedSpendTier =
  | 'HIGH'
  | 'LOW'
  | 'MEDIUM';

/** The possible product subscription states for a customer, as defined by the customer's subscription contracts. */
export type CustomerProductSubscriberStatus =
  | 'ACTIVE'
  | 'CANCELLED'
  | 'EXPIRED'
  | 'FAILED'
  | 'NEVER_SUBSCRIBED'
  | 'PAUSED';

/** Possible error codes that can be returned by `CustomerRequestDataErasureUserError`. */
export type CustomerRequestDataErasureErrorCode =
  | 'DOES_NOT_EXIST'
  | 'FAILED_TO_REQUEST';

/** The RFM (Recency, Frequency, Monetary) group for a customer. */
export type CustomerRfmGroup =
  | 'ACTIVE'
  | 'ALMOST_LOST'
  | 'AT_RISK'
  | 'CHAMPIONS'
  | 'DORMANT'
  | 'LOYAL'
  | 'NEEDS_ATTENTION'
  | 'NEW'
  | 'PREVIOUSLY_LOYAL'
  | 'PROMISING'
  | 'PROSPECTS';

/** The set of valid sort keys for the CustomerSavedSearch query. */
export type CustomerSavedSearchSortKeys =
  | 'ID'
  | 'NAME';

/** Possible error codes that can be returned by `CustomerSegmentMembersQueryUserError`. */
export type CustomerSegmentMembersQueryUserErrorCode =
  | 'INVALID';

/** Possible error codes that can be returned by `CustomerSendAccountInviteEmailUserError`. */
export type CustomerSendAccountInviteEmailUserErrorCode =
  | 'INVALID';

/** Possible error codes that can be returned by `CustomerSetUserError`. */
export type CustomerSetUserErrorCode =
  | 'BLANK'
  | 'ID_NOT_ALLOWED'
  | 'INCLUSION'
  | 'INPUT_MISMATCH'
  | 'INVALID'
  | 'METAFIELD_MISMATCH'
  | 'MISSING_FIELD_REQUIRED'
  | 'NOT_FOUND'
  | 'PRESENT'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT';

/** Possible error codes that can be returned by `CustomerSmsMarketingConsentError`. */
export type CustomerSmsMarketingConsentErrorCode =
  | 'INCLUSION'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'MISSING_ARGUMENT';

/** The valid SMS marketing states for a customer’s phone number. */
export type CustomerSmsMarketingState =
  | 'NOT_SUBSCRIBED'
  | 'PENDING'
  | 'REDACTED'
  | 'SUBSCRIBED'
  | 'UNSUBSCRIBED';

/** The set of valid sort keys for the Customer query. */
export type CustomerSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'LOCATION'
  | 'NAME'
  | 'RELEVANCE'
  | 'UPDATED_AT';

/** The valid values for the state of a customer's account with a shop. */
export type CustomerState =
  | 'DECLINED'
  | 'DISABLED'
  | 'ENABLED'
  | 'INVITED';

/** Possible error codes that can be returned by `DataSaleOptOutUserError`. */
export type DataSaleOptOutUserErrorCode =
  | 'FAILED';

/** Days of the week from Monday to Sunday. */
export type DayOfTheWeek =
  | 'FRIDAY'
  | 'MONDAY'
  | 'SATURDAY'
  | 'SUNDAY'
  | 'THURSDAY'
  | 'TUESDAY'
  | 'WEDNESDAY';

/** Possible error codes that can be returned by `DelegateAccessTokenCreateUserError`. */
export type DelegateAccessTokenCreateUserErrorCode =
  | 'DELEGATE_ACCESS_TOKEN'
  | 'EMPTY_ACCESS_SCOPE'
  | 'EXPIRES_AFTER_PARENT'
  | 'NEGATIVE_EXPIRES_IN'
  | 'PERSISTENCE_FAILED'
  | 'REFRESH_TOKEN'
  | 'UNKNOWN_SCOPES';

/** Possible error codes that can be returned by `DelegateAccessTokenDestroyUserError`. */
export type DelegateAccessTokenDestroyUserErrorCode =
  | 'ACCESS_DENIED'
  | 'ACCESS_TOKEN_NOT_FOUND'
  | 'CAN_ONLY_DELETE_DELEGATE_TOKENS'
  | 'PERSISTENCE_FAILED';

/** The set of valid sort keys for the DeletionEvent query. */
export type DeletionEventSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** The supported subject types of deletion events. */
export type DeletionEventSubjectType =
  | 'COLLECTION'
  | 'PRODUCT';

/** The field type that the condition will be applied to. */
export type DeliveryConditionField =
  | 'TOTAL_PRICE'
  | 'TOTAL_WEIGHT';

/** The operator to use to determine if the condition passes. */
export type DeliveryConditionOperator =
  | 'GREATER_THAN_OR_EQUAL_TO'
  | 'LESS_THAN_OR_EQUAL_TO';

/** Possible error codes that can be returned by `DeliveryCustomizationError`. */
export type DeliveryCustomizationErrorCode =
  | 'CUSTOM_APP_FUNCTION_NOT_ELIGIBLE'
  | 'DELIVERY_CUSTOMIZATION_FUNCTION_NOT_ELIGIBLE'
  | 'DELIVERY_CUSTOMIZATION_NOT_FOUND'
  | 'FUNCTION_DOES_NOT_IMPLEMENT'
  | 'FUNCTION_ID_CANNOT_BE_CHANGED'
  | 'FUNCTION_NOT_FOUND'
  | 'FUNCTION_PENDING_DELETION'
  | 'INVALID'
  | 'INVALID_METAFIELDS'
  | 'MAXIMUM_ACTIVE_DELIVERY_CUSTOMIZATIONS'
  | 'MISSING_FUNCTION_IDENTIFIER'
  | 'MULTIPLE_FUNCTION_IDENTIFIERS'
  | 'REQUIRED_INPUT_FIELD'
  | 'UNAUTHORIZED_APP_SCOPE';

/** Possible pickup time values that a location enabled for local pickup can have. */
export type DeliveryLocalPickupTime =
  | 'FIVE_OR_MORE_DAYS'
  | 'FOUR_HOURS'
  | 'ONE_HOUR'
  | 'TWENTY_FOUR_HOURS'
  | 'TWO_HOURS'
  | 'TWO_TO_FOUR_DAYS'
  | 'CUSTOM';

/** Possible error codes that can be returned by `DeliveryLocationLocalPickupSettingsError`. */
export type DeliveryLocationLocalPickupSettingsErrorCode =
  | 'ACTIVE_LOCATION_NOT_FOUND'
  | 'CUSTOM_PICKUP_TIME_NOT_ALLOWED'
  | 'GENERIC_ERROR';

/** The different types of method definitions to filter by. */
export type DeliveryMethodDefinitionType =
  | 'MERCHANT'
  | 'PARTICIPANT';

/** Possible method types that a delivery method can have. */
export type DeliveryMethodType =
  | 'LOCAL'
  | 'NONE'
  | 'PICK_UP'
  | 'PICKUP_POINT'
  | 'RETAIL'
  | 'SHIPPING';

/** The type of object that the participant is attached to. */
export type DeliveryPromiseParticipantOwnerType =
  | 'PRODUCTVARIANT';

/** Possible error codes that can be returned by `DeliveryPromiseProviderUpsertUserError`. */
export type DeliveryPromiseProviderUpsertUserErrorCode =
  | 'INVALID_TIME_ZONE'
  | 'MUST_BELONG_TO_APP'
  | 'NOT_FOUND'
  | 'TOO_LONG';

/** Digital wallet, such as Apple Pay, which can be used for accelerated checkouts. */
export type DigitalWallet =
  | 'AMAZON_PAY'
  | 'ANDROID_PAY'
  | 'APPLE_PAY'
  | 'FACEBOOK_PAY'
  | 'GOOGLE_PAY'
  | 'SHOPIFY_PAY';

/** The method by which the discount's value is allocated onto its entitled lines. */
export type DiscountApplicationAllocationMethod =
  | 'ACROSS'
  | 'EACH'
  | 'ONE';

/** The level at which the discount's value is applied. */
export type DiscountApplicationLevel =
  | 'LINE'
  | 'ORDER';

/** The lines on the order to which the discount is applied, of the type defined by the discount application's `targetType`. For example, the value `ENTITLED`, combined with a `targetType` of `LINE_ITEM`, applies the discount on all line items that are entitled to the discount. Th... */
export type DiscountApplicationTargetSelection =
  | 'ALL'
  | 'ENTITLED'
  | 'EXPLICIT';

/** The type of line (i.e. line item or shipping line) on an order that the discount is applicable towards. */
export type DiscountApplicationTargetType =
  | 'LINE_ITEM'
  | 'SHIPPING_LINE';

/** All buyers are eligible for the discount. */
export type DiscountBuyerSelection =
  | 'ALL';

/** The [discount class](https://help.shopify.com/manual/discounts/combining-discounts/discount-combinations) that's used to control how discounts can be combined. */
export type DiscountClass =
  | 'ORDER'
  | 'PRODUCT'
  | 'SHIPPING';

/** The set of valid sort keys for the DiscountCode query. */
export type DiscountCodeSortKeys =
  | 'CODE'
  | 'CREATED_AT'
  | 'ID'
  | 'RELEVANCE';

/** Possible error codes that can be returned by `DiscountUserError`. */
export type DiscountErrorCode =
  | 'ACTIVE_PERIOD_OVERLAP'
  | 'APPLIES_ON_NOTHING'
  | 'BLANK'
  | 'CONFLICT'
  | 'DUPLICATE'
  | 'END_DATE_BEFORE_START_DATE'
  | 'EQUAL_TO'
  | 'EXCEEDED_MAX'
  | 'GREATER_THAN'
  | 'GREATER_THAN_OR_EQUAL_TO'
  | 'IMPLICIT_DUPLICATE'
  | 'INCLUSION'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'INVALID_COMBINES_WITH_FOR_DISCOUNT_CLASS'
  | 'INVALID_DISCOUNT_CLASS_FOR_PRICE_RULE'
  | 'INVALID_PRODUCT_DISCOUNTS_FALSE_WITH_EXISTING_TAGS_ON_SAME_CART_LINE'
  | 'INVALID_PRODUCT_DISCOUNTS_WITH_TAGS_ON_SAME_CART_LINE_FOR_DISCOUNT_CLASS'
  | 'INVALID_PRODUCT_DISCOUNTS_WITH_TAGS_ON_SAME_CART_LINE_WITHOUT_PRODUCT_DISCOUNTS'
  | 'INVALID_TAG_LENGTH'
  | 'LESS_THAN'
  | 'LESS_THAN_OR_EQUAL_TO'
  | 'MAX_APP_DISCOUNTS'
  | 'MINIMUM_SUBTOTAL_AND_QUANTITY_RANGE_BOTH_PRESENT'
  | 'MISSING_ARGUMENT'
  | 'MISSING_FUNCTION_IDENTIFIER'
  | 'MULTIPLE_FUNCTION_IDENTIFIERS'
  | 'MULTIPLE_RECURRING_CYCLE_LIMIT_FOR_NON_SUBSCRIPTION_ITEMS'
  | 'PRESENT'
  | 'PRODUCT_DISCOUNTS_WITH_TAGS_ON_SAME_CART_LINE_NOT_ENTITLED'
  | 'RECURRING_CYCLE_LIMIT_NOT_A_VALID_INTEGER'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_MANY_ARGUMENTS'
  | 'TOO_MANY_PRODUCT_DISCOUNTS_WITH_TAGS_ON_SAME_CART_LINE'
  | 'TOO_MANY_TAGS'
  | 'TOO_SHORT'
  | 'VALUE_OUTSIDE_RANGE';

/** The type of page where a shareable discount URL lands. */
export type DiscountShareableUrlTargetType =
  | 'COLLECTION'
  | 'HOME'
  | 'PRODUCT';

/** The set of valid sort keys for the Discount query. */
export type DiscountSortKeys =
  | 'CREATED_AT'
  | 'ENDS_AT'
  | 'ID'
  | 'RELEVANCE'
  | 'STARTS_AT'
  | 'TITLE'
  | 'UPDATED_AT';

/** The status of the discount that describes its availability, expiration, or pending activation. */
export type DiscountStatus =
  | 'ACTIVE'
  | 'EXPIRED'
  | 'SCHEDULED';

/** The set of valid sort keys for the DiscountTag query. */
export type DiscountTagSortKeys =
  | 'ID'
  | 'TITLE';

/** The type of line (line item or shipping line) on an order that the subscription discount is applicable towards. */
export type DiscountTargetType =
  | 'LINE_ITEM'
  | 'SHIPPING_LINE';

/** The type of the subscription discount. */
export type DiscountType =
  | 'AUTOMATIC_DISCOUNT'
  | 'CODE_DISCOUNT'
  | 'MANUAL';

/** Possible error codes that can be returned by `DisputeEvidenceUpdateUserError`. */
export type DisputeEvidenceUpdateUserErrorCode =
  | 'DISPUTE_EVIDENCE_NOT_FOUND'
  | 'EVIDENCE_ALREADY_ACCEPTED'
  | 'EVIDENCE_PAST_DUE_DATE'
  | 'FILE_NOT_FOUND'
  | 'FILES_SIZE_EXCEEDED_LIMIT'
  | 'INVALID'
  | 'TOO_LARGE';

/** The possible statuses of a dispute. */
export type DisputeStatus =
  | 'ACCEPTED'
  | 'LOST'
  | 'NEEDS_RESPONSE'
  | 'PREVENTED'
  | 'UNDER_REVIEW'
  | 'WON'
  | 'CHARGE_REFUNDED';

/** The possible types for a dispute. */
export type DisputeType =
  | 'CHARGEBACK'
  | 'INQUIRY';

/** Units of measurement for distance. */
export type DistanceUnit =
  | 'KILOMETERS'
  | 'MILES';

/** The valid discount types that can be applied to a draft order. */
export type DraftOrderAppliedDiscountType =
  | 'FIXED_AMOUNT'
  | 'PERCENTAGE';

/** The set of valid sort keys for the DraftOrder query. */
export type DraftOrderSortKeys =
  | 'CUSTOMER_NAME'
  | 'ID'
  | 'NUMBER'
  | 'RELEVANCE'
  | 'STATUS'
  | 'TOTAL_PRICE'
  | 'UPDATED_AT';

/** The valid statuses for a draft order. */
export type DraftOrderStatus =
  | 'COMPLETED'
  | 'INVOICE_SENT'
  | 'OPEN';

/** Possible error codes that can be returned by `ErrorsServerPixelUserError`. */
export type ErrorsServerPixelUserErrorCode =
  | 'ALREADY_EXISTS'
  | 'NEEDS_CONFIGURATION_TO_CONNECT'
  | 'NOT_FOUND'
  | 'PUB_SUB_ERROR';

/** Possible error codes that can be returned by `ErrorsWebPixelUserError`. */
export type ErrorsWebPixelUserErrorCode =
  | 'BLANK'
  | 'INVALID_CONFIGURATION_JSON'
  | 'INVALID_RUNTIME_CONTEXT'
  | 'INVALID_SETTINGS'
  | 'INVALID_SETTINGS_DEFINITION'
  | 'NO_EXTENSION'
  | 'NOT_FOUND'
  | 'TAKEN'
  | 'UNEXPECTED_ERROR'
  | 'UNABLE_TO_DELETE';

/** The set of valid sort keys for the Event query. */
export type EventSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** The type of the resource that generated the event. */
export type EventSubjectType =
  | 'ARTICLE'
  | 'BLOG'
  | 'COLLECTION'
  | 'COMMENT'
  | 'COMPANY'
  | 'COMPANY_LOCATION'
  | 'CUSTOMER'
  | 'DISCOUNT_AUTOMATIC_BXGY'
  | 'DISCOUNT_AUTOMATIC_NODE'
  | 'DISCOUNT_CODE_NODE'
  | 'DISCOUNT_NODE'
  | 'DRAFT_ORDER'
  | 'INVENTORY_TRANSFER'
  | 'ORDER'
  | 'PAGE'
  | 'PRICE_RULE'
  | 'PRODUCT'
  | 'PRODUCT_VARIANT'
  | 'UNKNOWN';

/** The possible content types for a file object. */
export type FileContentType =
  | 'EXTERNAL_VIDEO'
  | 'FILE'
  | 'IMAGE'
  | 'MODEL_3D'
  | 'VIDEO';

/** The input fields for handling if filename is already in use. */
export type FileCreateInputDuplicateResolutionMode =
  | 'APPEND_UUID'
  | 'RAISE_ERROR'
  | 'REPLACE';

/** The error types for a file. */
export type FileErrorCode =
  | 'DUPLICATE_FILENAME_ERROR'
  | 'EXTERNAL_VIDEO_EMBED_DISABLED'
  | 'EXTERNAL_VIDEO_EMBED_NOT_FOUND_OR_TRANSCODING'
  | 'EXTERNAL_VIDEO_INVALID_ASPECT_RATIO'
  | 'EXTERNAL_VIDEO_NOT_FOUND'
  | 'EXTERNAL_VIDEO_UNLISTED'
  | 'FILE_STORAGE_LIMIT_EXCEEDED'
  | 'GENERIC_FILE_DOWNLOAD_FAILURE'
  | 'GENERIC_FILE_INVALID_SIZE'
  | 'IMAGE_DOWNLOAD_FAILURE'
  | 'IMAGE_PROCESSING_FAILURE'
  | 'INVALID_IMAGE_ASPECT_RATIO'
  | 'INVALID_IMAGE_FILE_SIZE'
  | 'INVALID_IMAGE_RESOLUTION'
  | 'INVALID_SIGNED_URL'
  | 'MEDIA_TIMEOUT_ERROR'
  | 'MODEL3D_GLB_OUTPUT_CREATION_ERROR'
  | 'MODEL3D_GLB_TO_USDZ_CONVERSION_ERROR'
  | 'MODEL3D_PROCESSING_FAILURE'
  | 'MODEL3D_THUMBNAIL_GENERATION_ERROR'
  | 'MODEL3D_THUMBNAIL_REGENERATION_ERROR'
  | 'MODEL3D_VALIDATION_ERROR'
  | 'UNKNOWN'
  | 'UNSUPPORTED_IMAGE_FILE_TYPE'
  | 'VIDEO_INVALID_FILETYPE_ERROR'
  | 'VIDEO_MAX_DURATION_ERROR'
  | 'VIDEO_MAX_HEIGHT_ERROR'
  | 'VIDEO_MAX_WIDTH_ERROR'
  | 'VIDEO_METADATA_READ_ERROR'
  | 'VIDEO_MIN_DURATION_ERROR'
  | 'VIDEO_MIN_HEIGHT_ERROR'
  | 'VIDEO_MIN_WIDTH_ERROR'
  | 'VIDEO_VALIDATION_ERROR';

/** Possible error codes that can be returned by `FilesUserError`. */
export type FilesErrorCode =
  | 'ALT_VALUE_LIMIT_EXCEEDED'
  | 'BLANK_SEARCH'
  | 'FILE_DOES_NOT_EXIST'
  | 'FILE_LOCKED'
  | 'FILENAME_ALREADY_EXISTS'
  | 'INVALID'
  | 'INVALID_DUPLICATE_MODE_FOR_TYPE'
  | 'INVALID_DUPLICATE_RESOLUTION_MODE'
  | 'INVALID_FAILED_MEDIA_STATE'
  | 'INVALID_FILENAME'
  | 'INVALID_FILENAME_EXTENSION'
  | 'INVALID_IMAGE_SOURCE_URL'
  | 'INVALID_QUERY'
  | 'MEDIA_CANNOT_BE_MODIFIED'
  | 'MISMATCHED_FILENAME_AND_ORIGINAL_SOURCE'
  | 'MISSING_ARGUMENTS'
  | 'MISSING_FILENAME_FOR_DUPLICATE_MODE_REPLACE'
  | 'NON_IMAGE_MEDIA_PER_SHOP_LIMIT_EXCEEDED'
  | 'NON_READY_STATE'
  | 'PRODUCT_MEDIA_LIMIT_EXCEEDED'
  | 'PRODUCT_SUSPENDED'
  | 'REFERENCE_TARGET_DOES_NOT_EXIST'
  | 'TOO_MANY_ARGUMENTS'
  | 'TOO_MANY_FILE_REFERENCE'
  | 'UNACCEPTABLE_ASSET'
  | 'UNACCEPTABLE_TRIAL_ASSET'
  | 'UNACCEPTABLE_UNVERIFIED_TRIAL_ASSET'
  | 'UNSUPPORTED_FILE_REFERENCE'
  | 'UNSUPPORTED_MEDIA_TYPE_FOR_FILENAME_UPDATE';

/** The set of valid sort keys for the File query. */
export type FileSortKeys =
  | 'CREATED_AT'
  | 'FILENAME'
  | 'ID'
  | 'ORIGINAL_UPLOAD_SIZE'
  | 'RELEVANCE'
  | 'UPDATED_AT';

/** The possible statuses for a file object. */
export type FileStatus =
  | 'FAILED'
  | 'PROCESSING'
  | 'READY'
  | 'UPLOADED';

/** Possible error codes that can be returned by `FulfillmentConstraintRuleCreateUserError`. */
export type FulfillmentConstraintRuleCreateUserErrorCode =
  | 'CUSTOM_APP_FUNCTION_NOT_ELIGIBLE'
  | 'FUNCTION_ALREADY_REGISTERED'
  | 'FUNCTION_DOES_NOT_IMPLEMENT'
  | 'FUNCTION_NOT_FOUND'
  | 'FUNCTION_PENDING_DELETION'
  | 'INPUT_INVALID'
  | 'MAXIMUM_FULFILLMENT_CONSTRAINT_RULES_REACHED'
  | 'MISSING_FUNCTION_IDENTIFIER'
  | 'MULTIPLE_FUNCTION_IDENTIFIERS';

/** Possible error codes that can be returned by `FulfillmentConstraintRuleDeleteUserError`. */
export type FulfillmentConstraintRuleDeleteUserErrorCode =
  | 'NOT_FOUND'
  | 'UNAUTHORIZED_APP_SCOPE';

/** Possible error codes that can be returned by `FulfillmentConstraintRuleUpdateUserError`. */
export type FulfillmentConstraintRuleUpdateUserErrorCode =
  | 'NOT_FOUND'
  | 'UNAUTHORIZED_APP_SCOPE';

/** The display status of a fulfillment. */
export type FulfillmentDisplayStatus =
  | 'ATTEMPTED_DELIVERY'
  | 'CANCELED'
  | 'CARRIER_PICKED_UP'
  | 'CONFIRMED'
  | 'DELAYED'
  | 'DELIVERED'
  | 'FAILURE'
  | 'FULFILLED'
  | 'IN_TRANSIT'
  | 'LABEL_PRINTED'
  | 'LABEL_PURCHASED'
  | 'LABEL_VOIDED'
  | 'MARKED_AS_FULFILLED'
  | 'NOT_DELIVERED'
  | 'OUT_FOR_DELIVERY'
  | 'PICKED_UP'
  | 'READY_FOR_PICKUP'
  | 'SUBMITTED';

/** The set of valid sort keys for the FulfillmentEvent query. */
export type FulfillmentEventSortKeys =
  | 'HAPPENED_AT'
  | 'ID';

/** The status that describes a fulfillment or delivery event. */
export type FulfillmentEventStatus =
  | 'ATTEMPTED_DELIVERY'
  | 'CARRIER_PICKED_UP'
  | 'CONFIRMED'
  | 'DELAYED'
  | 'DELIVERED'
  | 'FAILURE'
  | 'IN_TRANSIT'
  | 'LABEL_PRINTED'
  | 'LABEL_PURCHASED'
  | 'OUT_FOR_DELIVERY'
  | 'READY_FOR_PICKUP';

/** The reason for a fulfillment hold. */
export type FulfillmentHoldReason =
  | 'AWAITING_PAYMENT'
  | 'AWAITING_RETURN_ITEMS'
  | 'HIGH_RISK_OF_FRAUD'
  | 'INCORRECT_ADDRESS'
  | 'INVENTORY_OUT_OF_STOCK'
  | 'ONLINE_STORE_POST_PURCHASE_CROSS_SELL'
  | 'OTHER'
  | 'UNKNOWN_DELIVERY_DATE';

/** The actions that can be taken on a fulfillment order. */
export type FulfillmentOrderAction =
  | 'CANCEL_FULFILLMENT_ORDER'
  | 'CREATE_FULFILLMENT'
  | 'EXTERNAL'
  | 'HOLD'
  | 'MARK_AS_OPEN'
  | 'MERGE'
  | 'MOVE'
  | 'RELEASE_HOLD'
  | 'REPORT_PROGRESS'
  | 'REQUEST_CANCELLATION'
  | 'REQUEST_FULFILLMENT'
  | 'SPLIT';

/** The assigment status to be used to filter fulfillment orders. */
export type FulfillmentOrderAssignmentStatus =
  | 'CANCELLATION_REQUESTED'
  | 'FULFILLMENT_ACCEPTED'
  | 'FULFILLMENT_REQUESTED'
  | 'FULFILLMENT_UNSUBMITTED';

/** Possible error codes that can be returned by `FulfillmentOrderCancelError`. */
export type FulfillmentOrderCancelErrorCode =
  | 'FULFILLMENT_ORDER_HAS_MANUALLY_REPORTED_PROGRESS';

/** Possible error codes that can be returned by `FulfillmentOrderHoldUserError`. */
export type FulfillmentOrderHoldUserErrorCode =
  | 'DUPLICATE_FULFILLMENT_HOLD_HANDLE'
  | 'DUPLICATED_FULFILLMENT_ORDER_LINE_ITEMS'
  | 'FULFILLMENT_ORDER_HOLD_LIMIT_REACHED'
  | 'FULFILLMENT_ORDER_NOT_FOUND'
  | 'FULFILLMENT_ORDER_NOT_SPLITTABLE'
  | 'GREATER_THAN_ZERO'
  | 'INVALID_LINE_ITEM_QUANTITY'
  | 'TAKEN';

/** Possible error codes that can be returned by `FulfillmentOrderLineItemsPreparedForPickupUserError`. */
export type FulfillmentOrderLineItemsPreparedForPickupUserErrorCode =
  | 'FULFILLMENT_ORDER_INVALID'
  | 'NO_LINE_ITEMS_TO_PREPARE_FOR_FULFILLMENT_ORDER'
  | 'UNABLE_TO_PREPARE_QUANTITY';

/** The kinds of request merchants can make to a fulfillment service. */
export type FulfillmentOrderMerchantRequestKind =
  | 'CANCELLATION_REQUEST'
  | 'FULFILLMENT_REQUEST';

/** Possible error codes that can be returned by `FulfillmentOrderMergeUserError`. */
export type FulfillmentOrderMergeUserErrorCode =
  | 'FULFILLMENT_ORDER_NOT_FOUND'
  | 'GREATER_THAN'
  | 'INVALID_LINE_ITEM_QUANTITY';

/** Possible error codes that can be returned by `FulfillmentOrderMoveFulfillmentOrderMoveUserError`. */
export type FulfillmentOrderMoveFulfillmentOrderMoveUserErrorCode =
  | 'CANNOT_MOVE_FULFILLMENT_ORDER_WITH_REPORTED_PROGRESS';

/** The reason for a fulfillment order rejection. */
export type FulfillmentOrderRejectionReason =
  | 'INCORRECT_ADDRESS'
  | 'INCORRECT_PRODUCT_INFO'
  | 'INELIGIBLE_PRODUCT'
  | 'INTERNATIONAL_SHIPPING_UNAVAILABLE'
  | 'INVALID_CONTACT_INFORMATION'
  | 'INVALID_SKU'
  | 'INVENTORY_OUT_OF_STOCK'
  | 'MERCHANT_BLOCKED_OR_SUSPENDED'
  | 'MISSING_CUSTOMS_INFO'
  | 'ORDER_TOO_LARGE'
  | 'OTHER'
  | 'PACKAGE_PREFERENCE_NOT_SET'
  | 'PAYMENT_DECLINED'
  | 'UNDELIVERABLE_DESTINATION';

/** Possible error codes that can be returned by `FulfillmentOrderReleaseHoldUserError`. */
export type FulfillmentOrderReleaseHoldUserErrorCode =
  | 'FULFILLMENT_ORDER_NOT_FOUND'
  | 'INVALID_ACCESS';

/** Possible error codes that can be returned by `FulfillmentOrderReportProgressUserError`. */
export type FulfillmentOrderReportProgressUserErrorCode =
  | 'FULFILLMENT_ORDER_CONTAINS_PICKED_ITEMS'
  | 'FULFILLMENT_ORDER_INVALID_DELIVERY_METHOD'
  | 'FULFILLMENT_ORDER_INVALID_FULFILLMENT_SERVICE_OWNERSHIP'
  | 'FULFILLMENT_ORDER_NOT_FOUND'
  | 'FULFILLMENT_ORDER_STATUS_INVALID'
  | 'FULFILLMENT_ORDER_UNSUPPORTED_ACTION'
  | 'MARKETPLACE_APP_NOT_ELIGIBLE';

/** The request status of a fulfillment order. */
export type FulfillmentOrderRequestStatus =
  | 'ACCEPTED'
  | 'CANCELLATION_ACCEPTED'
  | 'CANCELLATION_REJECTED'
  | 'CANCELLATION_REQUESTED'
  | 'CLOSED'
  | 'REJECTED'
  | 'SUBMITTED'
  | 'UNSUBMITTED';

/** Possible error codes that can be returned by `FulfillmentOrderRescheduleUserError`. */
export type FulfillmentOrderRescheduleUserErrorCode =
  | 'FULFILLMENT_ORDER_NOT_FOUND';

/** The set of valid sort keys for the FulfillmentOrder query. */
export type FulfillmentOrderSortKeys =
  | 'ID'
  | 'UPDATED_AT';

/** Possible error codes that can be returned by `FulfillmentOrderSplitUserError`. */
export type FulfillmentOrderSplitUserErrorCode =
  | 'FULFILLMENT_ORDER_NOT_FOUND'
  | 'GREATER_THAN'
  | 'INVALID_LINE_ITEM_QUANTITY'
  | 'NO_LINE_ITEMS_PROVIDED_TO_SPLIT';

/** Possible error codes that can be returned by `FulfillmentOrdersRerouteUserError`. */
export type FulfillmentOrdersRerouteUserErrorCode =
  | 'CANNOT_MOVE_FULFILLMENT_ORDER_WITH_REPORTED_PROGRESS'
  | 'CANNOT_REASSIGN_LOCATION_FOR_FULFILLMENT_ORDERS'
  | 'DELIVERY_METHOD_TYPE_NOT_SUPPORTED'
  | 'FULFILLMENT_ORDER_NOT_FOUND'
  | 'FULFILLMENT_ORDERS_MUST_BELONG_TO_SAME_LOCATION'
  | 'FULFILLMENT_ORDERS_NOT_FROM_THE_SAME_ORDER'
  | 'FULFILLMENT_ORDERS_STATE_NOT_SUPPORTED'
  | 'NO_FULFILLMENT_ORDER_IDS'
  | 'SINGLE_LOCATION_SHOP_NOT_SUPPORTED';

/** Possible error codes that can be returned by `FulfillmentOrdersSetFulfillmentDeadlineUserError`. */
export type FulfillmentOrdersSetFulfillmentDeadlineUserErrorCode =
  | 'FULFILLMENT_ORDERS_NOT_FOUND';

/** The status of a fulfillment order. */
export type FulfillmentOrderStatus =
  | 'CANCELLED'
  | 'CLOSED'
  | 'IN_PROGRESS'
  | 'INCOMPLETE'
  | 'ON_HOLD'
  | 'OPEN'
  | 'SCHEDULED';

/** Actions that can be taken at the location when a client requests the deletion of the fulfillment service. */
export type FulfillmentServiceDeleteInventoryAction =
  | 'DELETE'
  | 'KEEP'
  | 'TRANSFER';

/** The type of a fulfillment service. */
export type FulfillmentServiceType =
  | 'GIFT_CARD'
  | 'MANUAL'
  | 'THIRD_PARTY';

/** The status of a fulfillment. */
export type FulfillmentStatus =
  | 'CANCELLED'
  | 'ERROR'
  | 'FAILURE'
  | 'SUCCESS'
  | 'OPEN'
  | 'PENDING';

/** The supported units for gift card expiration. */
export type GiftCardConfigurationExpirationUnit =
  | 'DAYS'
  | 'MONTHS'
  | 'YEARS';

/** Possible error codes that can be returned by `GiftCardDeactivateUserError`. */
export type GiftCardDeactivateUserErrorCode =
  | 'GIFT_CARD_NOT_FOUND';

/** Possible error codes that can be returned by `GiftCardUserError`. */
export type GiftCardErrorCode =
  | 'CUSTOMER_NOT_FOUND'
  | 'GIFT_CARD_LIMIT_EXCEEDED'
  | 'GREATER_THAN'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'MISSING_ARGUMENT'
  | 'RECIPIENT_NOT_FOUND'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT';

/** Possible error codes that can be returned by `GiftCardSendNotificationToCustomerUserError`. */
export type GiftCardSendNotificationToCustomerUserErrorCode =
  | 'CUSTOMER_NOT_FOUND'
  | 'GIFT_CARD_NOT_FOUND'
  | 'INVALID';

/** Possible error codes that can be returned by `GiftCardSendNotificationToRecipientUserError`. */
export type GiftCardSendNotificationToRecipientUserErrorCode =
  | 'GIFT_CARD_NOT_FOUND'
  | 'INVALID'
  | 'RECIPIENT_NOT_FOUND';

/** The set of valid sort keys for the GiftCard query. */
export type GiftCardSortKeys =
  | 'AMOUNT_SPENT'
  | 'BALANCE'
  | 'CODE'
  | 'CREATED_AT'
  | 'CUSTOMER_NAME'
  | 'DISABLED_AT'
  | 'EXPIRES_ON'
  | 'ID'
  | 'INITIAL_VALUE'
  | 'UPDATED_AT';

/** Possible error codes that can be returned by `GiftCardTransactionUserError`. */
export type GiftCardTransactionUserErrorCode =
  | 'GIFT_CARD_LIMIT_EXCEEDED'
  | 'GIFT_CARD_NOT_FOUND'
  | 'INSUFFICIENT_FUNDS'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'MISMATCHING_CURRENCY'
  | 'NEGATIVE_OR_ZERO_AMOUNT';

/** List of supported image content types. */
export type ImageContentType =
  | 'JPG'
  | 'PNG'
  | 'WEBP';

/** Answers the question if prices include duties and / or taxes. */
export type InclusiveDutiesPricingStrategy =
  | 'ADD_DUTIES_AT_CHECKOUT'
  | 'INCLUDE_DUTIES_IN_PRICE';

/** Answers the question if prices include duties and / or taxes. */
export type InclusiveTaxPricingStrategy =
  | 'ADD_TAXES_AT_CHECKOUT'
  | 'INCLUDES_TAXES_IN_PRICE'
  | 'INCLUDES_TAXES_IN_PRICE_BASED_ON_COUNTRY';

/** Possible error codes that can be returned by `InventoryAdjustQuantitiesUserError`. */
export type InventoryAdjustQuantitiesUserErrorCode =
  | 'ADJUST_QUANTITIES_FAILED'
  | 'CHANGE_FROM_QUANTITY_STALE'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INTERNAL_LEDGER_DOCUMENT'
  | 'INVALID_AVAILABLE_DOCUMENT'
  | 'INVALID_INVENTORY_ITEM'
  | 'INVALID_LEDGER_DOCUMENT'
  | 'INVALID_LOCATION'
  | 'INVALID_QUANTITY_DOCUMENT'
  | 'INVALID_QUANTITY_NAME'
  | 'INVALID_QUANTITY_TOO_HIGH'
  | 'INVALID_QUANTITY_TOO_LOW'
  | 'INVALID_REASON'
  | 'INVALID_REFERENCE_DOCUMENT'
  | 'ITEM_NOT_STOCKED_AT_LOCATION'
  | 'MAX_ONE_LEDGER_DOCUMENT'
  | 'NON_MUTABLE_INVENTORY_ITEM'
  | 'SERVICE_UNAVAILABLE';

/** Possible error codes that can be returned by `InventoryBulkToggleActivationUserError`. */
export type InventoryBulkToggleActivationUserErrorCode =
  | 'CANNOT_DEACTIVATE_FROM_ONLY_LOCATION'
  | 'COMMITTED_INVENTORY_AT_LOCATION'
  | 'FAILED_TO_STOCK_AT_LOCATION'
  | 'FAILED_TO_UNSTOCK_FROM_LOCATION'
  | 'GENERIC_ERROR'
  | 'INCOMING_INVENTORY_AT_LOCATION'
  | 'INVENTORY_ITEM_NOT_FOUND'
  | 'INVENTORY_MANAGED_BY_3RD_PARTY'
  | 'INVENTORY_MANAGED_BY_SHOPIFY'
  | 'LOCATION_NOT_FOUND'
  | 'MISSING_SKU'
  | 'RESERVED_INVENTORY_AT_LOCATION'
  | 'COMMITTED_AND_INCOMING_INVENTORY_AT_LOCATION';

/** Possible error codes that can be returned by `InventoryMoveQuantitiesUserError`. */
export type InventoryMoveQuantitiesUserErrorCode =
  | 'CHANGE_FROM_QUANTITY_STALE'
  | 'DIFFERENT_LOCATIONS'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INTERNAL_LEDGER_DOCUMENT'
  | 'INVALID_AVAILABLE_DOCUMENT'
  | 'INVALID_INVENTORY_ITEM'
  | 'INVALID_LEDGER_DOCUMENT'
  | 'INVALID_LOCATION'
  | 'INVALID_QUANTITY_DOCUMENT'
  | 'INVALID_QUANTITY_NAME'
  | 'INVALID_QUANTITY_NEGATIVE'
  | 'INVALID_QUANTITY_TOO_HIGH'
  | 'INVALID_REASON'
  | 'INVALID_REFERENCE_DOCUMENT'
  | 'ITEM_NOT_STOCKED_AT_LOCATION'
  | 'MAXIMUM_LEDGER_DOCUMENT_URIS'
  | 'MOVE_QUANTITIES_FAILED'
  | 'NON_MUTABLE_INVENTORY_ITEM'
  | 'SAME_QUANTITY_NAME'
  | 'SERVICE_UNAVAILABLE';

/** Possible error codes that can be returned by `InventorySetOnHandQuantitiesUserError`. */
export type InventorySetOnHandQuantitiesUserErrorCode =
  | 'CHANGE_FROM_QUANTITY_STALE'
  | 'COMPARE_QUANTITY_STALE'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INVALID_INVENTORY_ITEM'
  | 'INVALID_LOCATION'
  | 'INVALID_QUANTITY_NEGATIVE'
  | 'INVALID_QUANTITY_TOO_HIGH'
  | 'INVALID_REASON'
  | 'INVALID_REFERENCE_DOCUMENT'
  | 'ITEM_NOT_STOCKED_AT_LOCATION'
  | 'NON_MUTABLE_INVENTORY_ITEM'
  | 'SERVICE_UNAVAILABLE'
  | 'SET_ON_HAND_QUANTITIES_FAILED';

/** Possible error codes that can be returned by `InventorySetQuantitiesUserError`. */
export type InventorySetQuantitiesUserErrorCode =
  | 'CHANGE_FROM_QUANTITY_STALE'
  | 'COMPARE_QUANTITY_REQUIRED'
  | 'COMPARE_QUANTITY_STALE'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INVALID_INVENTORY_ITEM'
  | 'INVALID_LOCATION'
  | 'INVALID_NAME'
  | 'INVALID_QUANTITY_NEGATIVE'
  | 'INVALID_QUANTITY_TOO_HIGH'
  | 'INVALID_QUANTITY_TOO_LOW'
  | 'INVALID_REASON'
  | 'INVALID_REFERENCE_DOCUMENT'
  | 'ITEM_NOT_STOCKED_AT_LOCATION'
  | 'NO_DUPLICATE_INVENTORY_ITEM_ID_GROUP_ID_PAIR'
  | 'NON_MUTABLE_INVENTORY_ITEM';

/** Possible error codes that can be returned by `InventorySetScheduledChangesUserError`. */
export type InventorySetScheduledChangesUserErrorCode =
  | 'DUPLICATE_FROM_NAME'
  | 'DUPLICATE_TO_NAME'
  | 'ERROR_UPDATING_SCHEDULED'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INCLUSION'
  | 'INVALID_FROM_NAME'
  | 'INVALID_REASON'
  | 'INVALID_TO_NAME'
  | 'INVENTORY_ITEM_NOT_FOUND'
  | 'INVENTORY_STATE_NOT_FOUND'
  | 'ITEMS_EMPTY'
  | 'LEDGER_DOCUMENT_INVALID'
  | 'LOCATION_NOT_FOUND'
  | 'SAME_FROM_TO_NAMES';

/** Possible error codes that can be returned by `InventoryShipmentAddItemsUserError`. */
export type InventoryShipmentAddItemsUserErrorCode =
  | 'ACTIVATION_FAILED'
  | 'DUPLICATE_ITEM'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INVALID_QUANTITY'
  | 'INVALID_SHIPMENT_STATUS'
  | 'INVENTORY_STATE_NOT_ACTIVE'
  | 'ITEM_NOT_FOUND'
  | 'LOCATION_NOT_ACTIVE'
  | 'LOCATION_NOT_FOUND'
  | 'SHIPMENT_NOT_FOUND'
  | 'UNTRACKED_ITEM';

/** Possible error codes that can be returned by `InventoryShipmentCreateInTransitUserError`. */
export type InventoryShipmentCreateInTransitUserErrorCode =
  | 'DUPLICATE_ITEM'
  | 'EMPTY_SHIPMENT_INPUT'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INVALID_ITEM'
  | 'INVALID_QUANTITY'
  | 'INVALID_SHIPMENT_INPUT'
  | 'INVALID_TRANSFER_STATUS'
  | 'INVALID_URL'
  | 'INVENTORY_STATE_NOT_ACTIVE'
  | 'ITEM_NOT_FOUND'
  | 'ITEMS_EMPTY'
  | 'LOCATION_NOT_ACTIVE'
  | 'SHIPMENT_NOT_FOUND'
  | 'TRANSFER_NOT_FOUND'
  | 'UNTRACKED_ITEM';

/** Possible error codes that can be returned by `InventoryShipmentCreateUserError`. */
export type InventoryShipmentCreateUserErrorCode =
  | 'BARCODE_DUPLICATE'
  | 'BARCODE_TOO_LONG'
  | 'BUNDLED_ITEM'
  | 'DUPLICATE_ITEM'
  | 'EMPTY_SHIPMENT_INPUT'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'IDEMPOTENCY_RECORD_NOT_FOUND'
  | 'INVALID_ITEM'
  | 'INVALID_QUANTITY'
  | 'INVALID_SHIPMENT_INPUT'
  | 'INVALID_TRANSFER_STATUS'
  | 'INVALID_URL'
  | 'ITEM_NOT_FOUND'
  | 'LOCATION_NOT_ACTIVE'
  | 'TRANSFER_NOT_FOUND'
  | 'UNTRACKED_ITEM';

/** Possible error codes that can be returned by `InventoryShipmentDeleteUserError`. */
export type InventoryShipmentDeleteUserErrorCode =
  | 'INVALID_SHIPMENT_STATUS'
  | 'SHIPMENT_NOT_FOUND';

/** Possible error codes that can be returned by `InventoryShipmentMarkInTransitUserError`. */
export type InventoryShipmentMarkInTransitUserErrorCode =
  | 'ACTIVATION_FAILED'
  | 'INVALID_QUANTITY'
  | 'INVALID_SHIPMENT_STATUS'
  | 'INVENTORY_STATE_NOT_ACTIVE'
  | 'ITEM_NOT_FOUND'
  | 'ITEMS_EMPTY'
  | 'LOCATION_NOT_ACTIVE'
  | 'SHIPMENT_NOT_FOUND'
  | 'UNTRACKED_ITEM';

/** The reason for receiving a line item on an inventory shipment. */
export type InventoryShipmentReceiveLineItemReason =
  | 'ACCEPTED'
  | 'REJECTED';

/** Possible error codes that can be returned by `InventoryShipmentReceiveUserError`. */
export type InventoryShipmentReceiveUserErrorCode =
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INTERNAL_ERROR'
  | 'INVALID_QUANTITY'
  | 'INVALID_SHIPMENT_STATUS'
  | 'INVENTORY_STATE_NOT_ACTIVE'
  | 'ITEM_NOT_FOUND'
  | 'LOCATION_NOT_ACTIVE'
  | 'LOCATION_NOT_FOUND'
  | 'SHIPMENT_NOT_FOUND';

/** Possible error codes that can be returned by `InventoryShipmentRemoveItemsUserError`. */
export type InventoryShipmentRemoveItemsUserErrorCode =
  | 'INTERNAL_ERROR'
  | 'INVALID_SHIPMENT_STATUS'
  | 'ITEM_NOT_FOUND'
  | 'LOCATION_NOT_ACTIVE'
  | 'LOCATION_NOT_FOUND'
  | 'SHIPMENT_NOT_FOUND';

/** Possible error codes that can be returned by `InventoryShipmentSetBarcodeUserError`. */
export type InventoryShipmentSetBarcodeUserErrorCode =
  | 'BARCODE_DUPLICATE'
  | 'BARCODE_TOO_LONG'
  | 'SHIPMENT_NOT_FOUND';

/** Possible error codes that can be returned by `InventoryShipmentSetTrackingUserError`. */
export type InventoryShipmentSetTrackingUserErrorCode =
  | 'INVALID_URL'
  | 'SHIPMENT_NOT_FOUND';

/** The set of valid sort keys for the InventoryShipment query. */
export type InventoryShipmentSortKeys =
  | 'ID'
  | 'STATUS';

/** The status of an inventory shipment. */
export type InventoryShipmentStatus =
  | 'DRAFT'
  | 'IN_TRANSIT'
  | 'OTHER'
  | 'PARTIALLY_RECEIVED'
  | 'RECEIVED';

/** Possible error codes that can be returned by `InventoryShipmentUpdateItemQuantitiesUserError`. */
export type InventoryShipmentUpdateItemQuantitiesUserErrorCode =
  | 'INVALID_QUANTITY'
  | 'INVALID_SHIPMENT_STATUS'
  | 'ITEM_NOT_FOUND'
  | 'LOCATION_NOT_ACTIVE'
  | 'LOCATION_NOT_FOUND'
  | 'SHIPMENT_NOT_FOUND';

/** Possible error codes that can be returned by `InventoryTransferCancelUserError`. */
export type InventoryTransferCancelUserErrorCode =
  | 'INVALID_TRANSFER_STATUS'
  | 'SHIPMENT_EXISTS'
  | 'TRANSFER_NOT_FOUND';

/** Possible error codes that can be returned by `InventoryTransferCreateAsReadyToShipUserError`. */
export type InventoryTransferCreateAsReadyToShipUserErrorCode =
  | 'BUNDLED_ITEM'
  | 'DUPLICATE_ITEM'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INVALID_QUANTITY'
  | 'INVALID_TRANSFER_STATUS'
  | 'INVENTORY_STATE_NOT_ACTIVE'
  | 'ITEM_NOT_FOUND'
  | 'ITEMS_EMPTY'
  | 'LOCATION_NOT_ACTIVE'
  | 'LOCATION_NOT_FOUND'
  | 'LOCATION_REQUIRED'
  | 'TAG_EXCEEDS_MAX_LENGTH'
  | 'TRANSFER_NOT_FOUND'
  | 'TRANSFER_ORIGIN_CANNOT_BE_THE_SAME_AS_DESTINATION'
  | 'UNTRACKED_ITEM';

/** Possible error codes that can be returned by `InventoryTransferCreateUserError`. */
export type InventoryTransferCreateUserErrorCode =
  | 'BUNDLED_ITEM'
  | 'DUPLICATE_ITEM'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INVALID_QUANTITY'
  | 'INVENTORY_STATE_NOT_ACTIVE'
  | 'ITEM_NOT_FOUND'
  | 'LOCATION_NOT_ACTIVE'
  | 'LOCATION_NOT_FOUND'
  | 'TAG_EXCEEDS_MAX_LENGTH'
  | 'TRANSFER_NOT_FOUND'
  | 'TRANSFER_ORIGIN_CANNOT_BE_THE_SAME_AS_DESTINATION'
  | 'UNTRACKED_ITEM';

/** Possible error codes that can be returned by `InventoryTransferDeleteUserError`. */
export type InventoryTransferDeleteUserErrorCode =
  | 'INVALID_TRANSFER_STATUS'
  | 'TRANSFER_NOT_FOUND';

/** Possible error codes that can be returned by `InventoryTransferDuplicateUserError`. */
export type InventoryTransferDuplicateUserErrorCode =
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'TRANSFER_NOT_FOUND';

/** Possible error codes that can be returned by `InventoryTransferEditUserError`. */
export type InventoryTransferEditUserErrorCode =
  | 'INTERNAL_ERROR'
  | 'INVENTORY_STATE_NOT_ACTIVE'
  | 'LOCATION_NOT_ACTIVE'
  | 'LOCATION_NOT_FOUND'
  | 'TAG_EXCEEDS_MAX_LENGTH'
  | 'TRANSFER_LOCATION_IMMUTABLE'
  | 'TRANSFER_NOT_FOUND'
  | 'TRANSFER_ORIGIN_CANNOT_BE_THE_SAME_AS_DESTINATION';

/** Possible error codes that can be returned by `InventoryTransferMarkAsReadyToShipUserError`. */
export type InventoryTransferMarkAsReadyToShipUserErrorCode =
  | 'INVALID_ITEM'
  | 'INVALID_TRANSFER_STATUS'
  | 'ITEMS_EMPTY'
  | 'LOCATION_NOT_ACTIVE'
  | 'LOCATION_NOT_FOUND'
  | 'LOCATION_REQUIRED'
  | 'TRANSFER_NOT_FOUND';

/** Possible error codes that can be returned by `InventoryTransferRemoveItemsUserError`. */
export type InventoryTransferRemoveItemsUserErrorCode =
  | 'ALL_QUANTITY_SHIPPED'
  | 'CANT_REMOVE_ALL_ITEMS_FROM_READY_TO_SHIP_TRANSFER'
  | 'INVALID_TRANSFER_STATUS'
  | 'ITEM_NOT_FOUND'
  | 'ITEM_PRESENT_ON_DRAFT_SHIPMENT_WITH_ZERO_QUANTITY'
  | 'LOCATION_NOT_FOUND'
  | 'TRANSFER_NOT_FOUND';

/** Possible error codes that can be returned by `InventoryTransferSetItemsUserError`. */
export type InventoryTransferSetItemsUserErrorCode =
  | 'BUNDLED_ITEM'
  | 'DUPLICATE_ITEM'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'INVALID_QUANTITY'
  | 'INVALID_TRANSFER_STATUS'
  | 'INVENTORY_STATE_NOT_ACTIVE'
  | 'ITEM_NOT_FOUND'
  | 'LOCATION_NOT_ACTIVE'
  | 'LOCATION_NOT_FOUND'
  | 'TRANSFER_NOT_FOUND'
  | 'UNTRACKED_ITEM';

/** The status of a transfer. */
export type InventoryTransferStatus =
  | 'CANCELED'
  | 'DRAFT'
  | 'IN_PROGRESS'
  | 'OTHER'
  | 'READY_TO_SHIP'
  | 'TRANSFERRED';

/** Language codes supported by Shopify. */
export type LanguageCode =
  | 'AF'
  | 'AK'
  | 'AM'
  | 'AR'
  | 'AS'
  | 'AZ'
  | 'BE'
  | 'BG'
  | 'BM'
  | 'BN'
  | 'BO'
  | 'BR'
  | 'BS'
  | 'CA'
  | 'CE'
  | 'CKB'
  | 'CS'
  | 'CU'
  | 'CY'
  | 'DA'
  | 'DE'
  | 'DZ'
  | 'EE'
  | 'EL'
  | 'EN'
  | 'EO'
  | 'ES'
  | 'ET'
  | 'EU'
  | 'FA'
  | 'FF'
  | 'FI'
  | 'FIL'
  | 'FO'
  | 'FR'
  | 'FY'
  | 'GA'
  | 'GD'
  | 'GL'
  | 'GU'
  | 'GV'
  | 'HA'
  | 'HE'
  | 'HI'
  | 'HR'
  | 'HU'
  | 'HY'
  | 'IA'
  | 'ID'
  | 'IG'
  | 'II'
  | 'IS'
  | 'IT'
  | 'JA'
  | 'JV'
  | 'KA'
  | 'KI'
  | 'KK'
  | 'KL'
  | 'KM'
  | 'KN'
  | 'KO'
  | 'KS'
  | 'KU'
  | 'KW'
  | 'KY'
  | 'LB'
  | 'LG'
  | 'LN'
  | 'LO'
  | 'LT'
  | 'LU'
  | 'LV'
  | 'MG'
  | 'MI'
  | 'MK'
  | 'ML'
  | 'MN'
  | 'MR'
  | 'MS'
  | 'MT'
  | 'MY'
  | 'NB'
  | 'ND'
  | 'NE'
  | 'NL'
  | 'NN'
  | 'NO'
  | 'OM'
  | 'OR'
  | 'OS'
  | 'PA'
  | 'PL'
  | 'PS'
  | 'PT'
  | 'PT_BR'
  | 'PT_PT'
  | 'QU'
  | 'RM'
  | 'RN'
  | 'RO'
  | 'RU'
  | 'RW'
  | 'SA'
  | 'SC'
  | 'SD'
  | 'SE'
  | 'SG'
  | 'SI'
  | 'SK'
  | 'SL'
  | 'SN'
  | 'SO'
  | 'SQ'
  | 'SR'
  | 'SU'
  | 'SV'
  | 'SW'
  | 'TA'
  | 'TE'
  | 'TG'
  | 'TH'
  | 'TI'
  | 'TK'
  | 'TO'
  | 'TR'
  | 'TT'
  | 'UG'
  | 'UK'
  | 'UR'
  | 'UZ'
  | 'VI'
  | 'VO'
  | 'WO'
  | 'XH'
  | 'YI'
  | 'YO'
  | 'ZH'
  | 'ZH_CN'
  | 'ZH_TW'
  | 'ZU';

/** Units of measurement for length. */
export type LengthUnit =
  | 'CENTIMETERS'
  | 'FEET'
  | 'INCHES'
  | 'METERS'
  | 'MILLIMETERS'
  | 'YARDS';

/** Specifies the type of the underlying localizable content. This can be used to conditionally render different UI elements such as input fields. */
export type LocalizableContentType =
  | 'FILE_REFERENCE'
  | 'HTML'
  | 'INLINE_RICH_TEXT'
  | 'JSON'
  | 'JSON_STRING'
  | 'LINK'
  | 'LIST_FILE_REFERENCE'
  | 'LIST_LINK'
  | 'LIST_MULTI_LINE_TEXT_FIELD'
  | 'LIST_SINGLE_LINE_TEXT_FIELD'
  | 'LIST_URL'
  | 'MULTI_LINE_TEXT_FIELD'
  | 'RICH_TEXT_FIELD'
  | 'SINGLE_LINE_TEXT_FIELD'
  | 'STRING'
  | 'URI'
  | 'URL';

/** The key of a localization extension. */
export type LocalizationExtensionKey =
  | 'SHIPPING_CREDENTIAL_BR'
  | 'SHIPPING_CREDENTIAL_CL'
  | 'SHIPPING_CREDENTIAL_CN'
  | 'SHIPPING_CREDENTIAL_CO'
  | 'SHIPPING_CREDENTIAL_CR'
  | 'SHIPPING_CREDENTIAL_EC'
  | 'SHIPPING_CREDENTIAL_ES'
  | 'SHIPPING_CREDENTIAL_GT'
  | 'SHIPPING_CREDENTIAL_ID'
  | 'SHIPPING_CREDENTIAL_KR'
  | 'SHIPPING_CREDENTIAL_MX'
  | 'SHIPPING_CREDENTIAL_MY'
  | 'SHIPPING_CREDENTIAL_PE'
  | 'SHIPPING_CREDENTIAL_PT'
  | 'SHIPPING_CREDENTIAL_PY'
  | 'SHIPPING_CREDENTIAL_TR'
  | 'SHIPPING_CREDENTIAL_TW'
  | 'SHIPPING_CREDENTIAL_TYPE_CO'
  | 'TAX_CREDENTIAL_BR'
  | 'TAX_CREDENTIAL_CL'
  | 'TAX_CREDENTIAL_CO'
  | 'TAX_CREDENTIAL_CR'
  | 'TAX_CREDENTIAL_EC'
  | 'TAX_CREDENTIAL_ES'
  | 'TAX_CREDENTIAL_GT'
  | 'TAX_CREDENTIAL_ID'
  | 'TAX_CREDENTIAL_IT'
  | 'TAX_CREDENTIAL_MX'
  | 'TAX_CREDENTIAL_MY'
  | 'TAX_CREDENTIAL_PE'
  | 'TAX_CREDENTIAL_PT'
  | 'TAX_CREDENTIAL_PY'
  | 'TAX_CREDENTIAL_TR'
  | 'TAX_CREDENTIAL_TYPE_CO'
  | 'TAX_CREDENTIAL_TYPE_MX'
  | 'TAX_CREDENTIAL_USE_MX'
  | 'TAX_EMAIL_IT';

/** The purpose of a localization extension. */
export type LocalizationExtensionPurpose =
  | 'SHIPPING'
  | 'TAX';

/** The key of a localized field. */
export type LocalizedFieldKey =
  | 'SHIPPING_CREDENTIAL_BR'
  | 'SHIPPING_CREDENTIAL_CL'
  | 'SHIPPING_CREDENTIAL_CN'
  | 'SHIPPING_CREDENTIAL_CO'
  | 'SHIPPING_CREDENTIAL_CR'
  | 'SHIPPING_CREDENTIAL_EC'
  | 'SHIPPING_CREDENTIAL_ES'
  | 'SHIPPING_CREDENTIAL_GT'
  | 'SHIPPING_CREDENTIAL_ID'
  | 'SHIPPING_CREDENTIAL_KR'
  | 'SHIPPING_CREDENTIAL_MX'
  | 'SHIPPING_CREDENTIAL_MY'
  | 'SHIPPING_CREDENTIAL_PE'
  | 'SHIPPING_CREDENTIAL_PT'
  | 'SHIPPING_CREDENTIAL_PY'
  | 'SHIPPING_CREDENTIAL_TR'
  | 'SHIPPING_CREDENTIAL_TW'
  | 'SHIPPING_CREDENTIAL_TYPE_CO'
  | 'TAX_CREDENTIAL_BR'
  | 'TAX_CREDENTIAL_CL'
  | 'TAX_CREDENTIAL_CO'
  | 'TAX_CREDENTIAL_CR'
  | 'TAX_CREDENTIAL_EC'
  | 'TAX_CREDENTIAL_ES'
  | 'TAX_CREDENTIAL_GT'
  | 'TAX_CREDENTIAL_ID'
  | 'TAX_CREDENTIAL_IT'
  | 'TAX_CREDENTIAL_MX'
  | 'TAX_CREDENTIAL_MY'
  | 'TAX_CREDENTIAL_PE'
  | 'TAX_CREDENTIAL_PT'
  | 'TAX_CREDENTIAL_PY'
  | 'TAX_CREDENTIAL_TR'
  | 'TAX_CREDENTIAL_TYPE_CO'
  | 'TAX_CREDENTIAL_TYPE_MX'
  | 'TAX_CREDENTIAL_USE_MX'
  | 'TAX_EMAIL_IT';

/** The purpose of a localized field. */
export type LocalizedFieldPurpose =
  | 'SHIPPING'
  | 'TAX';

/** Possible error codes that can be returned by `LocationActivateUserError`. */
export type LocationActivateUserErrorCode =
  | 'GENERIC_ERROR'
  | 'HAS_NON_UNIQUE_NAME'
  | 'HAS_ONGOING_RELOCATION'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'LOCATION_LIMIT'
  | 'LOCATION_NOT_FOUND';

/** Possible error codes that can be returned by `LocationAddUserError`. */
export type LocationAddUserErrorCode =
  | 'APP_NOT_AUTHORIZED'
  | 'BLANK'
  | 'CAPABILITY_VIOLATION'
  | 'DISALLOWED_OWNER_TYPE'
  | 'GENERIC_ERROR'
  | 'INCLUSION'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'INVALID_TYPE'
  | 'INVALID_US_ZIPCODE'
  | 'INVALID_VALUE'
  | 'PRESENT'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT'
  | 'UNSTRUCTURED_RESERVED_NAMESPACE';

/** Possible error codes that can be returned by `LocationDeactivateUserError`. */
export type LocationDeactivateUserErrorCode =
  | 'CANNOT_DISABLE_ONLINE_ORDER_FULFILLMENT'
  | 'DESTINATION_LOCATION_IS_THE_SAME_LOCATION'
  | 'DESTINATION_LOCATION_NOT_FOUND_OR_INACTIVE'
  | 'DESTINATION_LOCATION_NOT_SHOPIFY_MANAGED'
  | 'FAILED_TO_RELOCATE_ACTIVE_INVENTORIES'
  | 'FAILED_TO_RELOCATE_INCOMING_MOVEMENTS'
  | 'FAILED_TO_RELOCATE_OPEN_PURCHASE_ORDERS'
  | 'HAS_ACTIVE_INVENTORY_ERROR'
  | 'HAS_ACTIVE_RETAIL_SUBSCRIPTIONS'
  | 'HAS_FULFILLMENT_ORDERS_ERROR'
  | 'HAS_INCOMING_FROM_EXTERNAL_DOCUMENT_SOURCES'
  | 'HAS_INCOMING_MOVEMENTS_ERROR'
  | 'HAS_OPEN_PURCHASE_ORDERS_ERROR'
  | 'IDEMPOTENCY_CONCURRENT_REQUEST'
  | 'IDEMPOTENCY_KEY_PARAMETER_MISMATCH'
  | 'LOCATION_NOT_FOUND'
  | 'PERMANENTLY_BLOCKED_FROM_DEACTIVATION_ERROR'
  | 'TEMPORARILY_BLOCKED_FROM_DEACTIVATION_ERROR';

/** Possible error codes that can be returned by `LocationDeleteUserError`. */
export type LocationDeleteUserErrorCode =
  | 'GENERIC_ERROR'
  | 'LOCATION_HAS_ACTIVE_RETAIL_SUBSCRIPTION'
  | 'LOCATION_HAS_INVENTORY'
  | 'LOCATION_HAS_PENDING_ORDERS'
  | 'LOCATION_IS_ACTIVE'
  | 'LOCATION_NOT_FOUND';

/** Possible error codes that can be returned by `LocationEditUserError`. */
export type LocationEditUserErrorCode =
  | 'APP_NOT_AUTHORIZED'
  | 'BLANK'
  | 'CANNOT_DISABLE_ONLINE_ORDER_FULFILLMENT'
  | 'CANNOT_MODIFY_ONLINE_ORDER_FULFILLMENT_FOR_FS_LOCATION'
  | 'CAPABILITY_VIOLATION'
  | 'DISALLOWED_OWNER_TYPE'
  | 'GENERIC_ERROR'
  | 'INCLUSION'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'INVALID_TYPE'
  | 'INVALID_US_ZIPCODE'
  | 'INVALID_VALUE'
  | 'NOT_FOUND'
  | 'PRESENT'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT'
  | 'UNSTRUCTURED_RESERVED_NAMESPACE';

/** The set of valid sort keys for the Location query. */
export type LocationSortKeys =
  | 'ID'
  | 'NAME'
  | 'RELEVANCE';

/** Highest level of validation concerns identified for the address. */
export type MailingAddressValidationResult =
  | 'ERROR'
  | 'NO_ISSUES'
  | 'WARNING';

/** The type of resource a payment mandate can be used for. */
export type MandateResourceType =
  | 'CHECKOUT'
  | 'CREDENTIAL_ON_FILE'
  | 'DRAFT_ORDER'
  | 'ORDER'
  | 'SUBSCRIPTIONS';

/** The application level for a market condition. */
export type MarketConditionApplicationType =
  | 'ALL'
  | 'SPECIFIED';

/** The condition types for the condition set. */
export type MarketConditionType =
  | 'COMPANY_LOCATION'
  | 'LOCATION'
  | 'REGION';

/** Possible error codes that can be returned by `MarketCurrencySettingsUserError`. */
export type MarketCurrencySettingsUserErrorCode =
  | 'MANAGED_MARKET'
  | 'MARKET_NOT_FOUND'
  | 'MULTIPLE_CURRENCIES_NOT_SUPPORTED'
  | 'NO_LOCAL_CURRENCIES_ON_SINGLE_COUNTRY_MARKET'
  | 'PRIMARY_MARKET_USES_SHOP_CURRENCY'
  | 'UNIFIED_MARKETS_ENABLED'
  | 'UNSUPPORTED_CURRENCY';

/** The error code resulted from the marketing activity extension integration. */
export type MarketingActivityExtensionAppErrorCode =
  | 'API_ERROR'
  | 'INSTALL_REQUIRED_ERROR'
  | 'NOT_ONBOARDED_ERROR'
  | 'PLATFORM_ERROR'
  | 'VALIDATION_ERROR';

/** Set of possible statuses for an external marketing activity. */
export type MarketingActivityExternalStatus =
  | 'ACTIVE'
  | 'DELETED_EXTERNALLY'
  | 'INACTIVE'
  | 'PAUSED'
  | 'SCHEDULED'
  | 'UNDEFINED';

/** Hierarchy levels for external marketing activities. */
export type MarketingActivityHierarchyLevel =
  | 'AD'
  | 'AD_GROUP'
  | 'CAMPAIGN';

/** The set of valid sort keys for the MarketingActivity query. */
export type MarketingActivitySortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'TITLE';

/** Status helps to identify if this marketing activity has been completed, queued, failed etc. */
export type MarketingActivityStatus =
  | 'ACTIVE'
  | 'DELETED'
  | 'DELETED_EXTERNALLY'
  | 'DISCONNECTED'
  | 'DRAFT'
  | 'FAILED'
  | 'INACTIVE'
  | 'PAUSED'
  | 'PENDING'
  | 'SCHEDULED'
  | 'UNDEFINED';

/** StatusBadgeType helps to identify the color of the status badge. */
export type MarketingActivityStatusBadgeType =
  | 'ATTENTION'
  | 'CRITICAL'
  | 'DEFAULT'
  | 'INFO'
  | 'SUCCESS'
  | 'WARNING';

/** Possible error codes that can be returned by `MarketingActivityUserError`. */
export type MarketingActivityUserErrorCode =
  | 'ACTIVITY_NOT_EXTERNAL'
  | 'CANNOT_DELETE_ACTIVITY_WITH_CHILD_EVENTS'
  | 'CANNOT_UPDATE_TACTIC_IF_ORIGINALLY_STOREFRONT_APP'
  | 'CANNOT_UPDATE_TACTIC_TO_STOREFRONT_APP'
  | 'CURRENCY_CODE_MISMATCH_INPUT'
  | 'DELETE_JOB_ENQUEUED'
  | 'DELETE_JOB_FAILED_TO_ENQUEUE'
  | 'IMMUTABLE_CHANNEL_HANDLE'
  | 'IMMUTABLE_HIERARCHY_LEVEL'
  | 'IMMUTABLE_PARENT_ID'
  | 'IMMUTABLE_URL_PARAMETER'
  | 'IMMUTABLE_UTM_PARAMETERS'
  | 'INVALID'
  | 'INVALID_CHANNEL_HANDLE'
  | 'INVALID_DELETE_ACTIVITY_EXTERNAL_ARGUMENTS'
  | 'INVALID_DELETE_ENGAGEMENTS_ARGUMENTS'
  | 'INVALID_MARKETING_ACTIVITY_EXTERNAL_ARGUMENTS'
  | 'INVALID_MARKETING_ENGAGEMENT_ARGUMENT_MISSING'
  | 'INVALID_MARKETING_ENGAGEMENT_ARGUMENTS'
  | 'INVALID_REMOTE_ID'
  | 'MARKETING_ACTIVITY_CURRENCY_CODE_MISMATCH'
  | 'MARKETING_ACTIVITY_DOES_NOT_EXIST'
  | 'MARKETING_ACTIVITY_WITH_REMOTE_ID_ALREADY_EXISTS'
  | 'MARKETING_ACTIVITY_WITH_URL_PARAMETER_VALUE_ALREADY_EXISTS'
  | 'MARKETING_ACTIVITY_WITH_UTM_CAMPAIGN_ALREADY_EXISTS'
  | 'MARKETING_EVENT_DOES_NOT_EXIST'
  | 'NON_HIERARCHIAL_REQUIRES_UTM_URL_PARAMETER'
  | 'TAKEN';

/** The budget type for a marketing activity. */
export type MarketingBudgetBudgetType =
  | 'DAILY'
  | 'LIFETIME';

/** The medium through which the marketing activity and event reached consumers. This is used for reporting aggregation. */
export type MarketingChannel =
  | 'DISPLAY'
  | 'EMAIL'
  | 'REFERRAL'
  | 'SEARCH'
  | 'SOCIAL';

/** The set of valid sort keys for the MarketingEvent query. */
export type MarketingEventSortKeys =
  | 'ID'
  | 'STARTED_AT';

/** The available types of tactics for a marketing activity. */
export type MarketingTactic =
  | 'ABANDONED_CART'
  | 'AD'
  | 'AFFILIATE'
  | 'LINK'
  | 'LOYALTY'
  | 'MESSAGE'
  | 'NEWSLETTER'
  | 'NOTIFICATION'
  | 'POST'
  | 'RETARGETING'
  | 'SEO'
  | 'STOREFRONT_APP'
  | 'TRANSACTIONAL';

/** The type of resources that are market localizable. */
export type MarketLocalizableResourceType =
  | 'METAFIELD'
  | 'METAOBJECT';

/** The set of valid sort keys for the Markets query. */
export type MarketsSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'MARKET_CONDITION_TYPES'
  | 'MARKET_TYPE'
  | 'NAME'
  | 'STATUS'
  | 'UPDATED_AT';

/** The possible market statuses. */
export type MarketStatus =
  | 'ACTIVE'
  | 'DRAFT';

/** The market types. */
export type MarketType =
  | 'COMPANY_LOCATION'
  | 'LOCATION'
  | 'NONE'
  | 'REGION';

/** Possible error codes that can be returned by `MarketUserError`. */
export type MarketUserErrorCode =
  | 'B2B_MARKET_MUST_BE_MERCHANT_MANAGED'
  | 'BLANK'
  | 'CANNOT_ADD_CUSTOMER_DOMAIN'
  | 'CANNOT_DELETE_ONLY_REGION'
  | 'CANNOT_DELETE_PRIMARY_MARKET'
  | 'CANNOT_DISABLE_PRIMARY_MARKET'
  | 'CANNOT_HAVE_BOTH_SUBFOLDER_AND_DOMAIN_WEB_PRESENCES'
  | 'CANNOT_HAVE_MULTIPLE_SUBFOLDERS_PER_MARKET'
  | 'CANNOT_HAVE_SUBFOLDER_AND_DOMAIN'
  | 'CANNOT_SET_DEFAULT_LOCALE_TO_NULL'
  | 'CATALOG_CONDITION_TYPES_MUST_BE_THE_SAME'
  | 'CATALOG_NOT_COMPATIBLE_WITH_CONDITION_TYPES'
  | 'CATALOG_TYPE_NOT_SUPPORTED'
  | 'CATALOGS_WITH_VOLUME_PRICING_OR_QUANTITY_RULES_NOT_SUPPORTED'
  | 'CONDITIONS_NOT_FOUND'
  | 'CONTAINS_REGIONS_THAT_CANNOT_BE_MANAGED'
  | 'CUSTOMIZATIONS_NOT_FOUND'
  | 'DISABLED_LANGUAGE'
  | 'DOMAIN_NOT_FOUND'
  | 'DUPLICATE_LANGUAGES'
  | 'DUPLICATE_REGION_MARKET'
  | 'DUPLICATE_UNIQUE_MARKET'
  | 'EXCEEDS_MAX_MULTI_CONTEXT_MARKETS'
  | 'GENERIC_ERROR'
  | 'INCLUSION'
  | 'INCLUSIVE_PRICING_NOT_COMPATIBLE_WITH_CONDITION_TYPES'
  | 'INCOMPATIBLE_CONDITIONS'
  | 'INVALID'
  | 'INVALID_PROVINCE_FORMAT'
  | 'INVALID_STATUS_AND_ENABLED_COMBINATION'
  | 'LOCATION_MATCH_ALL_REQUIRES_ONE_SPECIFIC_REGION'
  | 'LOCATION_REGION_COUNTRY_MISMATCH'
  | 'MANAGED_MARKET'
  | 'MANAGED_MARKETS_CATALOG_NOT_ALLOWED'
  | 'MARKET_CANT_HAVE_DIRECT_CONNECTION_CATALOG'
  | 'MARKET_NOT_FOUND'
  | 'MARKET_REACHED_WEB_PRESENCE_LIMIT'
  | 'MISSING_COUNTRY_CODE'
  | 'MISSING_PROVINCE_CODE'
  | 'MIXED_COUNTRY_LOCATIONS_NOT_ALLOWED'
  | 'MULTIPLE_CURRENCIES_NOT_SUPPORTED'
  | 'MUST_HAVE_AT_LEAST_ONE_ACTIVE_REGION_MARKET'
  | 'NO_LANGUAGES'
  | 'NOT_ENTITLED_TO_ACTIVATE_MARKET'
  | 'POS_LOCATION_MARKET_MUST_BE_MERCHANT_MANAGED'
  | 'PROVINCE_DOES_NOT_EXIST'
  | 'REGION_NOT_FOUND'
  | 'REGION_SPECIFIC_LANGUAGE'
  | 'REQUIRES_DOMAIN_OR_SUBFOLDER'
  | 'RETAIL_LOCATION_CURRENCY_MUST_BE_LOCAL'
  | 'SHOP_MUST_HAVE_PRIMARY_DOMAIN_WEB_PRESENCE'
  | 'SPECIFIED_CONDITIONS_CANNOT_BE_EMPTY'
  | 'SPECIFIED_NOT_VALID_FOR_INPUT'
  | 'SUBFOLDER_SUFFIX_CANNOT_BE_SCRIPT_CODE'
  | 'SUBFOLDER_SUFFIX_MUST_BE_AT_LEAST_2_LETTERS'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT'
  | 'UNPERMITTED_ENTITLEMENTS_MARKET_CATALOGS'
  | 'UNPUBLISHED_LANGUAGE'
  | 'UNSUPPORTED_COUNTRY_REGION'
  | 'UNSUPPORTED_CURRENCY'
  | 'USER_LACKS_PERMISSION'
  | 'WEB_PRESENCE_NOT_COMPATIBLE_WITH_CONDITION_TYPES'
  | 'WEB_PRESENCE_NOT_FOUND'
  | 'WEB_PRESENCE_REACHED_MARKETS_LIMIT'
  | 'WILDCARD_NOT_SUPPORTED'
  | 'CANNOT_ADD_REGIONS_TO_PRIMARY_MARKET'
  | 'CANNOT_ADD_WEB_PRESENCE_TO_PRIMARY_MARKET'
  | 'CANNOT_DELETE_PRIMARY_MARKET_WEB_PRESENCE'
  | 'INVALID_RESPONDER_FOR_PROVINCE_DRIVEN_MARKET'
  | 'MARKET_NOT_COMPATIBLE_WITH_CONDITION_TYPES'
  | 'NO_LOCAL_CURRENCIES_ON_SINGLE_COUNTRY_MARKET'
  | 'NO_ROUNDING_ON_LEGACY_MARKET'
  | 'PRIMARY_MARKET_MUST_USE_PRIMARY_DOMAIN'
  | 'REQUIRES_EXACTLY_ONE_OPTION'
  | 'SHOP_REACHED_MARKETS_LIMIT'
  | 'SUBFOLDER_SUFFIX_MUST_CONTAIN_ONLY_LETTERS'
  | 'UNIFIED_MARKETS_NOT_ENABLED'
  | 'WEB_PRESENCE_RETAIL_LOCATION';

/** The possible content types for a media object. */
export type MediaContentType =
  | 'EXTERNAL_VIDEO'
  | 'IMAGE'
  | 'MODEL_3D'
  | 'VIDEO';

/** Error types for media. */
export type MediaErrorCode =
  | 'DUPLICATE_FILENAME_ERROR'
  | 'EXTERNAL_VIDEO_EMBED_DISABLED'
  | 'EXTERNAL_VIDEO_EMBED_NOT_FOUND_OR_TRANSCODING'
  | 'EXTERNAL_VIDEO_INVALID_ASPECT_RATIO'
  | 'EXTERNAL_VIDEO_NOT_FOUND'
  | 'EXTERNAL_VIDEO_UNLISTED'
  | 'FILE_STORAGE_LIMIT_EXCEEDED'
  | 'GENERIC_FILE_DOWNLOAD_FAILURE'
  | 'GENERIC_FILE_INVALID_SIZE'
  | 'IMAGE_DOWNLOAD_FAILURE'
  | 'IMAGE_PROCESSING_FAILURE'
  | 'INVALID_IMAGE_ASPECT_RATIO'
  | 'INVALID_IMAGE_FILE_SIZE'
  | 'INVALID_IMAGE_RESOLUTION'
  | 'INVALID_SIGNED_URL'
  | 'MEDIA_TIMEOUT_ERROR'
  | 'MODEL3D_GLB_OUTPUT_CREATION_ERROR'
  | 'MODEL3D_GLB_TO_USDZ_CONVERSION_ERROR'
  | 'MODEL3D_PROCESSING_FAILURE'
  | 'MODEL3D_THUMBNAIL_GENERATION_ERROR'
  | 'MODEL3D_THUMBNAIL_REGENERATION_ERROR'
  | 'MODEL3D_VALIDATION_ERROR'
  | 'UNKNOWN'
  | 'UNSUPPORTED_IMAGE_FILE_TYPE'
  | 'VIDEO_INVALID_FILETYPE_ERROR'
  | 'VIDEO_MAX_DURATION_ERROR'
  | 'VIDEO_MAX_HEIGHT_ERROR'
  | 'VIDEO_MAX_WIDTH_ERROR'
  | 'VIDEO_METADATA_READ_ERROR'
  | 'VIDEO_MIN_DURATION_ERROR'
  | 'VIDEO_MIN_HEIGHT_ERROR'
  | 'VIDEO_MIN_WIDTH_ERROR'
  | 'VIDEO_VALIDATION_ERROR';

/** Host for a Media Resource. */
export type MediaHost =
  | 'VIMEO'
  | 'YOUTUBE';

/** The possible statuses for a media preview image. */
export type MediaPreviewImageStatus =
  | 'FAILED'
  | 'PROCESSING'
  | 'READY'
  | 'UPLOADED';

/** The possible statuses for a media object. */
export type MediaStatus =
  | 'FAILED'
  | 'PROCESSING'
  | 'READY'
  | 'UPLOADED';

/** Possible error codes that can be returned by `MediaUserError`. */
export type MediaUserErrorCode =
  | 'BLANK'
  | 'INVALID'
  | 'INVALID_MEDIA_TYPE'
  | 'MAXIMUM_VARIANT_MEDIA_PAIRS_EXCEEDED'
  | 'MEDIA_CANNOT_BE_MODIFIED'
  | 'MEDIA_DOES_NOT_EXIST'
  | 'MEDIA_DOES_NOT_EXIST_ON_PRODUCT'
  | 'MEDIA_IS_NOT_ATTACHED_TO_VARIANT'
  | 'MISSING_ARGUMENTS'
  | 'MODEL3D_THROTTLE_EXCEEDED'
  | 'MODEL3D_VALIDATION_ERROR'
  | 'NON_READY_MEDIA'
  | 'PRODUCT_DOES_NOT_EXIST'
  | 'PRODUCT_MEDIA_LIMIT_EXCEEDED'
  | 'PRODUCT_SUSPENDED'
  | 'PRODUCT_VARIANT_ALREADY_HAS_MEDIA'
  | 'PRODUCT_VARIANT_DOES_NOT_EXIST_ON_PRODUCT'
  | 'PRODUCT_VARIANT_SPECIFIED_MULTIPLE_TIMES'
  | 'SHOP_MEDIA_LIMIT_EXCEEDED'
  | 'TOO_MANY_MEDIA_PER_INPUT_PAIR'
  | 'VIDEO_THROTTLE_EXCEEDED'
  | 'VIDEO_VALIDATION_ERROR';

/** Warning types for media. */
export type MediaWarningCode =
  | 'MODEL_LARGE_PHYSICAL_SIZE'
  | 'MODEL_PREVIEW_IMAGE_FAIL'
  | 'MODEL_SMALL_PHYSICAL_SIZE';

/** Possible error codes that can be returned by `MenuCreateUserError`. */
export type MenuCreateUserErrorCode =
  | 'NESTING_TOO_DEEP'
  | 'NOT_FOUND';

/** Possible error codes that can be returned by `MenuDeleteUserError`. */
export type MenuDeleteUserErrorCode =
  | 'MENU_DOES_NOT_EXIST'
  | 'UNABLE_TO_DELETE_DEFAULT_MENU';

/** A menu item type. */
export type MenuItemType =
  | 'ARTICLE'
  | 'BLOG'
  | 'CATALOG'
  | 'COLLECTION'
  | 'COLLECTIONS'
  | 'CUSTOMER_ACCOUNT_PAGE'
  | 'FRONTPAGE'
  | 'HTTP'
  | 'METAOBJECT'
  | 'PAGE'
  | 'PRODUCT'
  | 'SEARCH'
  | 'SHOP_POLICY';

/** The set of valid sort keys for the Menu query. */
export type MenuSortKeys =
  | 'ID'
  | 'TITLE'
  | 'UPDATED_AT';

/** Possible error codes that can be returned by `MenuUpdateUserError`. */
export type MenuUpdateUserErrorCode =
  | 'NESTING_TOO_DEEP'
  | 'NOT_FOUND';

/** The [discount class](https://help.shopify.com/manual/discounts/combining-discounts/discount-combinations) that's used to control how discounts can be combined. */
export type MerchandiseDiscountClass =
  | 'ORDER'
  | 'PRODUCT';

/** Metafield access permissions for the Admin API. */
export type MetafieldAdminAccess =
  | 'MERCHANT_READ'
  | 'MERCHANT_READ_WRITE'
  | 'PRIVATE'
  | 'PUBLIC_READ'
  | 'PUBLIC_READ_WRITE';

/** Metafield access permissions for the Admin API. */
export type MetafieldAdminAccessInput =
  | 'MERCHANT_READ'
  | 'MERCHANT_READ_WRITE';

/** Metafield access permissions for the Customer Account API. */
export type MetafieldCustomerAccountAccess =
  | 'NONE'
  | 'READ'
  | 'READ_WRITE';

/** Metafield access permissions for the Customer Account API. */
export type MetafieldCustomerAccountAccessInput =
  | 'NONE'
  | 'READ'
  | 'READ_WRITE';

/** Possible filter statuses associated with a metafield definition for use in admin filtering. */
export type MetafieldDefinitionAdminFilterStatus =
  | 'FAILED'
  | 'FILTERABLE'
  | 'IN_PROGRESS'
  | 'NOT_FILTERABLE';

/** Metafield definition constraint criteria to filter metafield definitions by. */
export type MetafieldDefinitionConstraintStatus =
  | 'CONSTRAINED_AND_UNCONSTRAINED'
  | 'CONSTRAINED_ONLY'
  | 'UNCONSTRAINED_ONLY';

/** Possible error codes that can be returned by `MetafieldDefinitionCreateUserError`. */
export type MetafieldDefinitionCreateUserErrorCode =
  | 'ADMIN_ACCESS_INPUT_NOT_ALLOWED'
  | 'BLANK'
  | 'CAPABILITY_REQUIRED_BUT_DISABLED'
  | 'DUPLICATE_OPTION'
  | 'INCLUSION'
  | 'INVALID'
  | 'INVALID_CAPABILITY'
  | 'INVALID_CHARACTER'
  | 'INVALID_CONSTRAINTS'
  | 'INVALID_INPUT_COMBINATION'
  | 'INVALID_OPTION'
  | 'LIMIT_EXCEEDED'
  | 'OWNER_TYPE_LIMIT_EXCEEDED_FOR_AUTOMATED_COLLECTIONS'
  | 'OWNER_TYPE_LIMIT_EXCEEDED_FOR_USE_AS_ADMIN_FILTERS'
  | 'PINNED_LIMIT_REACHED'
  | 'PRESENT'
  | 'RESERVED_NAMESPACE_KEY'
  | 'RESOURCE_TYPE_LIMIT_EXCEEDED'
  | 'RESOURCE_TYPE_LIMIT_EXCEEDED_BY_APP'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT'
  | 'TYPE_NOT_ALLOWED_FOR_CONDITIONS'
  | 'UNSTRUCTURED_ALREADY_EXISTS'
  | 'UNSUPPORTED_PINNING';

/** Possible error codes that can be returned by `MetafieldDefinitionDeleteUserError`. */
export type MetafieldDefinitionDeleteUserErrorCode =
  | 'APP_CONFIG_MANAGED'
  | 'DISALLOWED_OWNER_TYPE'
  | 'ID_TYPE_DELETION_ERROR'
  | 'INTERNAL_ERROR'
  | 'METAFIELD_DEFINITION_IN_USE'
  | 'NOT_FOUND'
  | 'PRESENT'
  | 'REFERENCE_TYPE_DELETION_ERROR'
  | 'RESERVED_NAMESPACE_ORPHANED_METAFIELDS'
  | 'STANDARD_METAFIELD_DEFINITION_DEPENDENT_ON_APP';

/** Possible metafield definition pinned statuses. */
export type MetafieldDefinitionPinnedStatus =
  | 'ANY'
  | 'PINNED'
  | 'UNPINNED';

/** Possible error codes that can be returned by `MetafieldDefinitionPinUserError`. */
export type MetafieldDefinitionPinUserErrorCode =
  | 'ALREADY_PINNED'
  | 'DISALLOWED_OWNER_TYPE'
  | 'INTERNAL_ERROR'
  | 'NOT_FOUND'
  | 'PINNED_LIMIT_REACHED'
  | 'UNSUPPORTED_PINNING';

/** The set of valid sort keys for the MetafieldDefinition query. */
export type MetafieldDefinitionSortKeys =
  | 'ID'
  | 'NAME'
  | 'PINNED_POSITION'
  | 'RELEVANCE';

/** Possible error codes that can be returned by `MetafieldDefinitionUnpinUserError`. */
export type MetafieldDefinitionUnpinUserErrorCode =
  | 'APP_CONFIG_MANAGED'
  | 'DISALLOWED_OWNER_TYPE'
  | 'INTERNAL_ERROR'
  | 'NOT_FOUND'
  | 'NOT_PINNED';

/** Possible error codes that can be returned by `MetafieldDefinitionUpdateUserError`. */
export type MetafieldDefinitionUpdateUserErrorCode =
  | 'ADMIN_ACCESS_INPUT_NOT_ALLOWED'
  | 'APP_CONFIG_MANAGED'
  | 'BLANK'
  | 'CAPABILITY_CANNOT_BE_DISABLED'
  | 'CAPABILITY_REQUIRED_BUT_DISABLED'
  | 'DISALLOWED_OWNER_TYPE'
  | 'DUPLICATE_OPTION'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'INVALID_CAPABILITY'
  | 'INVALID_CONSTRAINTS'
  | 'INVALID_INPUT'
  | 'INVALID_INPUT_COMBINATION'
  | 'INVALID_OPTION'
  | 'METAFIELD_DEFINITION_IN_USE'
  | 'METAOBJECT_DEFINITION_CHANGED'
  | 'NOT_FOUND'
  | 'OWNER_TYPE_LIMIT_EXCEEDED_FOR_AUTOMATED_COLLECTIONS'
  | 'OWNER_TYPE_LIMIT_EXCEEDED_FOR_USE_AS_ADMIN_FILTERS'
  | 'PINNED_LIMIT_REACHED'
  | 'PRESENT'
  | 'TOO_LONG'
  | 'TYPE_NOT_ALLOWED_FOR_CONDITIONS'
  | 'UNSUPPORTED_PINNING';

/** Possible metafield definition validation statuses. */
export type MetafieldDefinitionValidationStatus =
  | 'ALL_VALID'
  | 'IN_PROGRESS'
  | 'SOME_INVALID';

/** Possible types of a metafield's owner resource. */
export type MetafieldOwnerType =
  | 'API_PERMISSION'
  | 'ARTICLE'
  | 'BLOG'
  | 'CARTTRANSFORM'
  | 'COLLECTION'
  | 'COMPANY'
  | 'COMPANY_LOCATION'
  | 'CUSTOMER'
  | 'DELIVERY_CUSTOMIZATION'
  | 'DISCOUNT'
  | 'DRAFTORDER'
  | 'FULFILLMENT_CONSTRAINT_RULE'
  | 'GIFT_CARD_TRANSACTION'
  | 'LOCATION'
  | 'MARKET'
  | 'ORDER'
  | 'ORDER_ROUTING_LOCATION_RULE'
  | 'PAGE'
  | 'PAYMENT_CUSTOMIZATION'
  | 'PRODUCT'
  | 'PRODUCTVARIANT'
  | 'SELLING_PLAN'
  | 'SHOP'
  | 'VALIDATION'
  | 'MEDIA_IMAGE';

/** Possible error codes that can be returned by `MetafieldsSetUserError`. */
export type MetafieldsSetUserErrorCode =
  | 'APP_NOT_AUTHORIZED'
  | 'BLANK'
  | 'CAPABILITY_VIOLATION'
  | 'INCLUSION'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'INVALID_COMPARE_DIGEST'
  | 'INVALID_TYPE'
  | 'INVALID_VALUE'
  | 'LESS_THAN_OR_EQUAL_TO'
  | 'PRESENT'
  | 'STALE_OBJECT'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT';

/** Metafield access permissions for the Storefront API. */
export type MetafieldStorefrontAccess =
  | 'NONE'
  | 'PUBLIC_READ';

/** Metafield access permissions for the Storefront API. */
export type MetafieldStorefrontAccessInput =
  | 'NONE'
  | 'PUBLIC_READ';

/** Possible metafield validation statuses. */
export type MetafieldValidationStatus =
  | 'ANY'
  | 'INVALID'
  | 'VALID';

/** Legacy type information for the stored value. Replaced by `type`. */
export type MetafieldValueType =
  | 'BOOLEAN'
  | 'INTEGER'
  | 'JSON_STRING'
  | 'STRING';

/** Metaobject access permissions for the Admin API. When the metaobject is app-owned, the owning app always has full access. */
export type MetaobjectAdminAccess =
  | 'MERCHANT_READ'
  | 'MERCHANT_READ_WRITE'
  | 'PRIVATE'
  | 'PUBLIC_READ'
  | 'PUBLIC_READ_WRITE';

/** Metaobject access permissions for the Admin API. When the metaobject is app-owned, the owning app always has full access. */
export type MetaobjectAdminAccessInput =
  | 'MERCHANT_READ'
  | 'MERCHANT_READ_WRITE';

/** Metaobject Capabilities types which can be enabled. */
export type MetaobjectCapabilityType =
  | 'ONLINE_STORE'
  | 'PUBLISHABLE'
  | 'RENDERABLE'
  | 'TRANSLATABLE';

/** Metaobject access permissions for the Customer Account API. */
export type MetaobjectCustomerAccountAccess =
  | 'NONE'
  | 'READ';

/** Defines visibility status for metaobjects. */
export type MetaobjectStatus =
  | 'ACTIVE'
  | 'DRAFT';

/** Metaobject access permissions for the Storefront API. */
export type MetaobjectStorefrontAccess =
  | 'NONE'
  | 'PUBLIC_READ';

/** Possible error codes that can be returned by `MetaobjectUserError`. */
export type MetaobjectUserErrorCode =
  | 'ADMIN_ACCESS_INPUT_NOT_ALLOWED'
  | 'APP_CONFIG_MANAGED'
  | 'BLANK'
  | 'CAPABILITY_NOT_ENABLED'
  | 'DISPLAY_NAME_CONFLICT'
  | 'DUPLICATE_FIELD_INPUT'
  | 'FIELD_TYPE_INVALID'
  | 'IMMUTABLE'
  | 'INCLUSION'
  | 'INPUT_LIMIT_EXCEEDED'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'INVALID_OPTION'
  | 'INVALID_TYPE'
  | 'INVALID_VALUE'
  | 'MAX_DEFINITIONS_EXCEEDED'
  | 'MAX_OBJECTS_EXCEEDED'
  | 'MISSING_REQUIRED_KEYS'
  | 'NOT_AUTHORIZED'
  | 'OBJECT_FIELD_REQUIRED'
  | 'OBJECT_FIELD_TAKEN'
  | 'PRESENT'
  | 'RECORD_NOT_FOUND'
  | 'REFERENCE_EXISTS_ERROR'
  | 'RESERVED_NAME'
  | 'STANDARD_METAOBJECT_DEFINITION_DEPENDENT_ON_APP'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT'
  | 'UNDEFINED_OBJECT_FIELD'
  | 'UNDEFINED_OBJECT_TYPE'
  | 'URL_HANDLE_BLANK'
  | 'URL_HANDLE_INVALID'
  | 'URL_HANDLE_TAKEN';

/** The set of valid sort keys for the MethodDefinition query. */
export type MethodDefinitionSortKeys =
  | 'ID'
  | 'RATE_PROVIDER_TYPE';

/** Possible error codes that can be returned by `MobilePlatformApplicationUserError`. */
export type MobilePlatformApplicationUserErrorCode =
  | 'INVALID'
  | 'NOT_FOUND'
  | 'TOO_LONG';

/** The valid values for the notification usage, specifying the intended notification environment usage for certain operations. */
export type NotificationUsage =
  | 'SMS'
  | 'WEB';

/** The input type for a theme file body. */
export type OnlineStoreThemeFileBodyInputType =
  | 'BASE64'
  | 'TEXT'
  | 'URL';

/** Type of a theme file operation result. */
export type OnlineStoreThemeFileResultType =
  | 'BAD_REQUEST'
  | 'CONFLICT'
  | 'ERROR'
  | 'NOT_FOUND'
  | 'SUCCESS'
  | 'TIMEOUT'
  | 'UNPROCESSABLE_ENTITY';

/** Possible error codes that can be returned by `OnlineStoreThemeFilesUserErrors`. */
export type OnlineStoreThemeFilesUserErrorsCode =
  | 'ACCESS_DENIED'
  | 'DUPLICATE_FILE_INPUT'
  | 'ERROR'
  | 'FILE_VALIDATION_ERROR'
  | 'LESS_THAN_OR_EQUAL_TO'
  | 'NOT_FOUND'
  | 'THEME_FILES_CONFLICT'
  | 'THEME_LIMITED_PLAN'
  | 'THROTTLED';

/** The possible order action types for a [sales agreement](https://shopify.dev/api/admin-graphql/latest/interfaces/salesagreement). */
export type OrderActionType =
  | 'ORDER'
  | 'ORDER_EDIT'
  | 'REFUND'
  | 'RETURN'
  | 'UNKNOWN';

/** Discrepancy reasons for order adjustments. */
export type OrderAdjustmentDiscrepancyReason =
  | 'CUSTOMER'
  | 'DAMAGE'
  | 'FULL_RETURN_BALANCING_ADJUSTMENT'
  | 'PENDING_REFUND_DISCREPANCY'
  | 'REFUND_DISCREPANCY'
  | 'RESTOCK';

/** Discrepancy reasons for order adjustments. */
export type OrderAdjustmentInputDiscrepancyReason =
  | 'CUSTOMER'
  | 'DAMAGE'
  | 'OTHER'
  | 'RESTOCK';

/** Represents the reason for the order's cancellation. */
export type OrderCancelReason =
  | 'CUSTOMER'
  | 'DECLINED'
  | 'FRAUD'
  | 'INVENTORY'
  | 'OTHER'
  | 'STAFF';

/** Possible error codes that can be returned by `OrderCancelUserError`. */
export type OrderCancelUserErrorCode =
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'NO_REFUND_PERMISSION'
  | 'NO_REFUND_TO_STORE_CREDIT_PERMISSION'
  | 'NOT_FOUND'
  | 'STORE_CREDIT_REFUND_B2B_NOT_SUPPORTED'
  | 'STORE_CREDIT_REFUND_EXPIRATION_IN_PAST'
  | 'STORE_CREDIT_REFUND_MISSING_CUSTOMER';

/** The status of payments associated with the order. Can only be set when the order is created. */
export type OrderCreateFinancialStatus =
  | 'AUTHORIZED'
  | 'EXPIRED'
  | 'PAID'
  | 'PARTIALLY_PAID'
  | 'PARTIALLY_REFUNDED'
  | 'PENDING'
  | 'REFUNDED'
  | 'VOIDED';

/** The order's status in terms of fulfilled line items. */
export type OrderCreateFulfillmentStatus =
  | 'FULFILLED'
  | 'PARTIAL'
  | 'RESTOCKED';

/** The types of behavior to use when updating inventory. */
export type OrderCreateInputsInventoryBehavior =
  | 'BYPASS'
  | 'DECREMENT_IGNORING_POLICY'
  | 'DECREMENT_OBEYING_POLICY';

/** Possible error codes that can be returned by `OrderCreateMandatePaymentUserError`. */
export type OrderCreateMandatePaymentUserErrorCode =
  | 'ORDER_MANDATE_PAYMENT_ERROR_CODE';

/** Possible error codes that can be returned by `OrderCreateManualPaymentOrderCreateManualPaymentError`. */
export type OrderCreateManualPaymentOrderCreateManualPaymentErrorCode =
  | 'AMOUNT_EXCEEDS_BALANCE'
  | 'AMOUNT_NOT_POSITIVE'
  | 'CURRENCY_MISMATCH'
  | 'GATEWAY_NOT_FOUND'
  | 'ORDER_IS_TEMPORARILY_UNAVAILABLE'
  | 'ORDER_NOT_FOUND'
  | 'PROCESSED_AT_INVALID';

/** Possible error codes that can be returned by `OrderCreateUserError`. */
export type OrderCreateUserErrorCode =
  | 'FULFILLMENT_SERVICE_INVALID'
  | 'INVALID'
  | 'INVENTORY_CLAIM_FAILED'
  | 'PROCESSED_AT_INVALID'
  | 'REDUNDANT_CUSTOMER_FIELDS'
  | 'SHOP_DORMANT'
  | 'TAX_LINE_RATE_MISSING';

/** Possible error codes that can be returned by `OrderCustomerRemoveUserError`. */
export type OrderCustomerRemoveUserErrorCode =
  | 'INVALID'
  | 'NOT_FOUND'
  | 'NOT_SAVED';

/** Possible error codes that can be returned by `OrderCustomerSetUserError`. */
export type OrderCustomerSetUserErrorCode =
  | 'INVALID'
  | 'NOT_FOUND'
  | 'NOT_PERMITTED'
  | 'NOT_SAVED';

/** Possible error codes that can be returned by `OrderDeleteUserError`. */
export type OrderDeleteUserErrorCode =
  | 'INVALID'
  | 'NOT_FOUND';

/** Represents the order's current financial status. */
export type OrderDisplayFinancialStatus =
  | 'AUTHORIZED'
  | 'EXPIRED'
  | 'PAID'
  | 'PARTIALLY_PAID'
  | 'PARTIALLY_REFUNDED'
  | 'PENDING'
  | 'REFUNDED'
  | 'VOIDED';

/** Represents the order's aggregated fulfillment status for display purposes. */
export type OrderDisplayFulfillmentStatus =
  | 'FULFILLED'
  | 'IN_PROGRESS'
  | 'ON_HOLD'
  | 'OPEN'
  | 'PARTIALLY_FULFILLED'
  | 'PENDING_FULFILLMENT'
  | 'REQUEST_DECLINED'
  | 'RESTOCKED'
  | 'SCHEDULED'
  | 'UNFULFILLED';

/** Possible error codes that can be returned by `OrderEditAddShippingLineUserError`. */
export type OrderEditAddShippingLineUserErrorCode =
  | 'INVALID';

/** Possible error codes that can be returned by `OrderEditRemoveDiscountUserError`. */
export type OrderEditRemoveDiscountUserErrorCode =
  | 'INVALID';

/** Possible error codes that can be returned by `OrderEditRemoveShippingLineUserError`. */
export type OrderEditRemoveShippingLineUserErrorCode =
  | 'INVALID';

/** Possible error codes that can be returned by `OrderEditUpdateDiscountUserError`. */
export type OrderEditUpdateDiscountUserErrorCode =
  | 'INVALID';

/** Possible error codes that can be returned by `OrderEditUpdateShippingLineUserError`. */
export type OrderEditUpdateShippingLineUserErrorCode =
  | 'INVALID';

/** Possible error codes that can be returned by `OrderInvoiceSendUserError`. */
export type OrderInvoiceSendUserErrorCode =
  | 'ORDER_INVOICE_SEND_UNSUCCESSFUL';

/** The type of a payment status. */
export type OrderPaymentStatusResult =
  | 'AUTHORIZED'
  | 'CAPTURED'
  | 'ERROR'
  | 'INITIATED'
  | 'PENDING'
  | 'PROCESSING'
  | 'PURCHASED'
  | 'REDIRECT_REQUIRED'
  | 'REFUNDED'
  | 'RETRYABLE'
  | 'SUCCESS'
  | 'UNKNOWN'
  | 'VOIDED';

/** The order's aggregated return status that's used for display purposes. An order might have multiple returns, so this field communicates the prioritized return status. The `OrderReturnStatus` enum is a supported filter parameter in the [`orders` query](https://shopify.dev/api/a... */
export type OrderReturnStatus =
  | 'IN_PROGRESS'
  | 'INSPECTION_COMPLETE'
  | 'NO_RETURN'
  | 'RETURN_FAILED'
  | 'RETURN_REQUESTED'
  | 'RETURNED';

/** Possible error codes that can be returned by `OrderRiskAssessmentCreateUserError`. */
export type OrderRiskAssessmentCreateUserErrorCode =
  | 'INVALID'
  | 'NOT_FOUND'
  | 'ORDER_ALREADY_FULFILLED'
  | 'TOO_MANY_FACTS';

/** The likelihood that an order is fraudulent. This enum is deprecated in favor of [RiskAssessmentResult](https://shopify.dev/api/admin-graphql/latest/enums/RiskAssessmentResult) which allows for more granular risk levels, including PENDING and NONE. */
export type OrderRiskLevel =
  | 'HIGH'
  | 'LOW'
  | 'MEDIUM';

/** List of possible values for an OrderRiskRecommendation recommendation. */
export type OrderRiskRecommendationResult =
  | 'ACCEPT'
  | 'CANCEL'
  | 'INVESTIGATE'
  | 'NONE';

/** The set of valid sort keys for the Order query. */
export type OrderSortKeys =
  | 'CREATED_AT'
  | 'CURRENT_TOTAL_PRICE'
  | 'CUSTOMER_NAME'
  | 'DESTINATION'
  | 'FINANCIAL_STATUS'
  | 'FULFILLMENT_STATUS'
  | 'ID'
  | 'ORDER_NUMBER'
  | 'PO_NUMBER'
  | 'PROCESSED_AT'
  | 'RELEVANCE'
  | 'TOTAL_ITEMS_QUANTITY'
  | 'TOTAL_PRICE'
  | 'UPDATED_AT';

/** A standardized error code, independent of the payment provider. */
export type OrderTransactionErrorCode =
  | 'AMAZON_PAYMENTS_INVALID_PAYMENT_METHOD'
  | 'AMAZON_PAYMENTS_MAX_AMOUNT_CHARGED'
  | 'AMAZON_PAYMENTS_MAX_AMOUNT_REFUNDED'
  | 'AMAZON_PAYMENTS_MAX_AUTHORIZATIONS_CAPTURED'
  | 'AMAZON_PAYMENTS_MAX_REFUNDS_PROCESSED'
  | 'AMAZON_PAYMENTS_ORDER_REFERENCE_CANCELED'
  | 'AMAZON_PAYMENTS_STALE'
  | 'AMOUNT_TOO_LARGE'
  | 'AMOUNT_TOO_SMALL'
  | 'AUTHENTICATION_FAILED'
  | 'AUTHENTICATION_REQUIRED'
  | 'AUTHORIZATION_EXPIRED'
  | 'CALL_ISSUER'
  | 'CANCELLED_PAYMENT'
  | 'CARD_DECLINED'
  | 'CARD_TESTING'
  | 'CONFIG_ERROR'
  | 'DO_NOT_HONOR'
  | 'EXPIRED_CARD'
  | 'FRAUD_SUSPECTED'
  | 'GENERIC_ERROR'
  | 'INCORRECT_ADDRESS'
  | 'INCORRECT_CVC'
  | 'INCORRECT_NUMBER'
  | 'INCORRECT_PIN'
  | 'INCORRECT_ZIP'
  | 'INSTRUMENT_DECLINED'
  | 'INSUFFICIENT_FUNDS'
  | 'INVALID_AMOUNT'
  | 'INVALID_COUNTRY'
  | 'INVALID_CURRENCY'
  | 'INVALID_CVC'
  | 'INVALID_EXPIRY_DATE'
  | 'INVALID_NUMBER'
  | 'INVALID_PAYMENT_METHOD'
  | 'INVALID_PURCHASE_TYPE'
  | 'MERCHANT_ACCOUNT_ERROR'
  | 'MERCHANT_RULE'
  | 'PAYMENT_METHOD_UNAVAILABLE'
  | 'PAYMENT_METHOD_UNSUPPORTED'
  | 'PAYMENT_PROVIDER_ERROR'
  | 'PICK_UP_CARD'
  | 'PROCESSING_ERROR'
  | 'RETRY_DECLINED'
  | 'TEST_MODE_LIVE_CARD'
  | 'TRANSACTION_LIMIT_EXCEEDED'
  | 'UNSUPPORTED_FEATURE';

/** The different kinds of order transactions. */
export type OrderTransactionKind =
  | 'AUTHORIZATION'
  | 'CAPTURE'
  | 'CHANGE'
  | 'EMV_AUTHORIZATION'
  | 'REFUND'
  | 'SALE'
  | 'SUGGESTED_REFUND'
  | 'VOID';

/** The different states that an `OrderTransaction` can have. */
export type OrderTransactionStatus =
  | 'AWAITING_RESPONSE'
  | 'ERROR'
  | 'FAILURE'
  | 'PENDING'
  | 'SUCCESS'
  | 'UNKNOWN';

/** Possible error codes that can be returned by `PageCreateUserError`. */
export type PageCreateUserErrorCode =
  | 'BLANK'
  | 'INVALID'
  | 'INVALID_PUBLISH_DATE'
  | 'INVALID_TYPE'
  | 'INVALID_VALUE'
  | 'TAKEN'
  | 'TOO_BIG'
  | 'TOO_LONG';

/** Possible error codes that can be returned by `PageDeleteUserError`. */
export type PageDeleteUserErrorCode =
  | 'NOT_FOUND';

/** The set of valid sort keys for the Page query. */
export type PageSortKeys =
  | 'ID'
  | 'PUBLISHED_AT'
  | 'TITLE'
  | 'UPDATED_AT';

/** Possible error codes that can be returned by `PageUpdateUserError`. */
export type PageUpdateUserErrorCode =
  | 'BLANK'
  | 'INVALID'
  | 'INVALID_PUBLISH_DATE'
  | 'INVALID_TYPE'
  | 'INVALID_VALUE'
  | 'NOT_FOUND'
  | 'TAKEN'
  | 'TOO_BIG'
  | 'TOO_LONG';

/** Possible error codes that can be returned by `PaymentCustomizationError`. */
export type PaymentCustomizationErrorCode =
  | 'CUSTOM_APP_FUNCTION_NOT_ELIGIBLE'
  | 'FUNCTION_DOES_NOT_IMPLEMENT'
  | 'FUNCTION_ID_CANNOT_BE_CHANGED'
  | 'FUNCTION_NOT_FOUND'
  | 'FUNCTION_PENDING_DELETION'
  | 'INVALID'
  | 'INVALID_METAFIELDS'
  | 'MAXIMUM_ACTIVE_PAYMENT_CUSTOMIZATIONS'
  | 'MISSING_FUNCTION_IDENTIFIER'
  | 'MULTIPLE_FUNCTION_IDENTIFIERS'
  | 'PAYMENT_CUSTOMIZATION_FUNCTION_NOT_ELIGIBLE'
  | 'PAYMENT_CUSTOMIZATION_NOT_FOUND'
  | 'REQUIRED_INPUT_FIELD';

/** Some of the payment methods used in Shopify. */
export type PaymentMethods =
  | 'AMERICAN_EXPRESS'
  | 'BANCONTACT'
  | 'BITCOIN'
  | 'BOGUS'
  | 'CARTES_BANCAIRES'
  | 'DANKORT'
  | 'DINERS_CLUB'
  | 'DISCOVER'
  | 'DOGECOIN'
  | 'EFTPOS'
  | 'ELO'
  | 'FORBRUGSFORENINGEN'
  | 'INTERAC'
  | 'JCB'
  | 'LITECOIN'
  | 'MAESTRO'
  | 'MASTERCARD'
  | 'PAYPAL'
  | 'UNIONPAY'
  | 'VISA';

/** Possible error codes that can be returned by `PaymentReminderSendUserError`. */
export type PaymentReminderSendUserErrorCode =
  | 'PAYMENT_REMINDER_SEND_UNSUCCESSFUL';

/** Possible error codes that can be returned by `PaymentTermsCreateUserError`. */
export type PaymentTermsCreateUserErrorCode =
  | 'PAYMENT_TERMS_CREATION_UNSUCCESSFUL';

/** Possible error codes that can be returned by `PaymentTermsDeleteUserError`. */
export type PaymentTermsDeleteUserErrorCode =
  | 'PAYMENT_TERMS_DELETE_UNSUCCESSFUL';

/** The type of a payment terms or a payment terms template. */
export type PaymentTermsType =
  | 'FIXED'
  | 'FULFILLMENT'
  | 'NET'
  | 'RECEIPT'
  | 'UNKNOWN';

/** Possible error codes that can be returned by `PaymentTermsUpdateUserError`. */
export type PaymentTermsUpdateUserErrorCode =
  | 'PAYMENT_TERMS_UPDATE_UNSUCCESSFUL';

/** The set of valid sort keys for the Payout query. */
export type PayoutSortKeys =
  | 'ADJUSTMENT_GROSS'
  | 'ADVANCE_GROSS'
  | 'AMOUNT'
  | 'CHARGE_GROSS'
  | 'DUTIES_GROSS'
  | 'FEE_AMOUNT'
  | 'ID'
  | 'ISSUED_AT'
  | 'REFUND_GROSS'
  | 'SHIPPING_LABEL_GROSS'
  | 'STATUS';

/** Represents a valid PayPal Express subscriptions gateway status. */
export type PaypalExpressSubscriptionsGatewayStatus =
  | 'DISABLED'
  | 'ENABLED'
  | 'PENDING';

/** Possible error codes that can be returned by `PointOfSaleDeviceAssignToCashDrawerUserError`. */
export type PointOfSaleDeviceAssignToCashDrawerUserErrorCode =
  | 'CASH_DRAWER_NOT_FOUND'
  | 'INTERNAL_ERROR'
  | 'LOCATION_MISMATCH'
  | 'POINT_OF_SALE_DEVICE_NOT_FOUND';

/** Possible error codes that can be returned by `PointOfSaleDevicePaymentSessionCloseUserError`. */
export type PointOfSaleDevicePaymentSessionCloseUserErrorCode =
  | 'CURRENCY_MISMATCH'
  | 'FAILED_TO_CLOSE_SESSION'
  | 'NO_CASH_DRAWER_ASSOCIATED'
  | 'PAYMENT_SESSION_NOT_FOUND'
  | 'REASON_CODE_NOT_FOUND'
  | 'SESSION_ALREADY_CLOSED'
  | 'STAFF_MEMBER_NOT_FOUND'
  | 'TIME_BEFORE_SESSION_OPEN';

/** Possible error codes that can be returned by `PointOfSaleDevicePaymentSessionCountUserError`. */
export type PointOfSaleDevicePaymentSessionCountUserErrorCode =
  | 'CURRENCY_MISMATCH'
  | 'FAILED_TO_RECORD_COUNT'
  | 'NO_CASH_DRAWER_ASSOCIATED'
  | 'PAYMENT_SESSION_NOT_FOUND'
  | 'REASON_CODE_NOT_FOUND'
  | 'SESSION_ALREADY_CLOSED'
  | 'STAFF_MEMBER_NOT_FOUND'
  | 'TIME_BEFORE_SESSION_OPEN';

/** Possible error codes that can be returned by `PointOfSaleDevicePaymentSessionOpenUserError`. */
export type PointOfSaleDevicePaymentSessionOpenUserErrorCode =
  | 'ALREADY_OPEN'
  | 'CURRENCY_MISMATCH'
  | 'NO_CASH_DRAWER_ASSOCIATED'
  | 'NOT_SAVED'
  | 'POINT_OF_SALE_DEVICE_NOT_FOUND'
  | 'REASON_CODE_NOT_FOUND'
  | 'STAFF_MEMBER_NOT_FOUND';

/** The set of valid sort keys for the PointOfSaleDevicePaymentSession query. */
export type PointOfSaleDevicePaymentSessionSortKeys =
  | 'CLOSING_TIME'
  | 'ID'
  | 'OPENING_TIME';

/** The status of the point of sale device payment session. Payments can't be processed or refunded during a closed session, and the cash drawer balance can't be adjusted or corrected. */
export type PointOfSaleDevicePaymentSessionStatus =
  | 'CLOSED'
  | 'OPEN';

/** How to calculate the parent product variant's price while bulk updating variant relationships. */
export type PriceCalculationType =
  | 'COMPONENTS_SUM'
  | 'FIXED'
  | 'NONE';

/** Represents a percentage price adjustment type. */
export type PriceListAdjustmentType =
  | 'PERCENTAGE_DECREASE'
  | 'PERCENTAGE_INCREASE';

/** Represents how the compare at price will be determined for a price list. */
export type PriceListCompareAtMode =
  | 'ADJUSTED'
  | 'NULLIFY';

/** Possible error codes that can be returned by `PriceListFixedPricesByProductBulkUpdateUserError`. */
export type PriceListFixedPricesByProductBulkUpdateUserErrorCode =
  | 'DUPLICATE_ID_IN_INPUT'
  | 'ID_MUST_BE_MUTUALLY_EXCLUSIVE'
  | 'LOCAL_CURRENCY_GIFT_CARD_ISSUANCE_CURRENCY_MISMATCH'
  | 'LOCAL_CURRENCY_GIFT_CARD_LIMIT_EXCEEDED'
  | 'NO_UPDATE_OPERATIONS_SPECIFIED'
  | 'PRICE_LIMIT_EXCEEDED'
  | 'PRICE_LIST_DOES_NOT_EXIST'
  | 'PRICES_TO_ADD_CURRENCY_MISMATCH'
  | 'PRODUCT_DOES_NOT_EXIST';

/** Represents the origin of a price, either fixed (defined on the price list) or relative (calculated using a price list adjustment configuration). For examples, refer to [PriceList](https://shopify.dev/api/admin-graphql/latest/queries/priceList#section-examples). */
export type PriceListPriceOriginType =
  | 'FIXED'
  | 'RELATIVE';

/** Possible error codes that can be returned by `PriceListPriceUserError`. */
export type PriceListPriceUserErrorCode =
  | 'BLANK'
  | 'LOCAL_CURRENCY_GIFT_CARD_ISSUANCE_CURRENCY_MISMATCH'
  | 'LOCAL_CURRENCY_GIFT_CARD_LIMIT_EXCEEDED'
  | 'PRICE_LIST_CURRENCY_MISMATCH'
  | 'PRICE_LIST_NOT_FOUND'
  | 'PRICE_NOT_FIXED'
  | 'VARIANT_NOT_FOUND';

/** The set of valid sort keys for the PriceList query. */
export type PriceListSortKeys =
  | 'ID'
  | 'NAME';

/** Possible error codes that can be returned by `PriceListUserError`. */
export type PriceListUserErrorCode =
  | 'BLANK'
  | 'CATALOG_CONTEXT_DOES_NOT_SUPPORT_QUANTITY_PRICE_BREAKS'
  | 'CATALOG_CONTEXT_DOES_NOT_SUPPORT_QUANTITY_RULES'
  | 'CATALOG_DOES_NOT_EXIST'
  | 'CATALOG_MARKET_AND_PRICE_LIST_CURRENCY_MISMATCH'
  | 'CATALOG_TAKEN'
  | 'CONTEXT_RULE_LIMIT_ONE_OPTION'
  | 'COUNTRY_PRICE_LIST_ASSIGNMENT'
  | 'CURRENCY_MARKET_MISMATCH'
  | 'CURRENCY_NOT_SUPPORTED'
  | 'GENERIC_ERROR'
  | 'INCLUSION'
  | 'INVALID_ADJUSTMENT_MAX_VALUE'
  | 'INVALID_ADJUSTMENT_MIN_VALUE'
  | 'INVALID_ADJUSTMENT_VALUE'
  | 'PRICE_LIST_LOCKED'
  | 'PRICE_LIST_NOT_ALLOWED_FOR_PRIMARY_MARKET'
  | 'PRICE_LIST_NOT_FOUND'
  | 'TAKEN'
  | 'TOO_LONG';

/** The method by which the price rule's value is allocated to its entitled items. */
export type PriceRuleAllocationMethod =
  | 'ACROSS'
  | 'EACH';

/** The list of features that can be supported by a price rule. */
export type PriceRuleFeature =
  | 'BULK'
  | 'BUY_ONE_GET_ONE'
  | 'BUY_ONE_GET_ONE_WITH_ALLOCATION_LIMIT'
  | 'QUANTITY_DISCOUNTS'
  | 'SPECIFIC_CUSTOMERS';

/** The type of page where a shareable price rule URL lands. */
export type PriceRuleShareableUrlTargetType =
  | 'COLLECTION'
  | 'HOME'
  | 'PRODUCT';

/** The status of the price rule. */
export type PriceRuleStatus =
  | 'ACTIVE'
  | 'EXPIRED'
  | 'SCHEDULED';

/** The type of lines (line\_item or shipping\_line) to which the price rule applies. */
export type PriceRuleTarget =
  | 'LINE_ITEM'
  | 'SHIPPING_LINE';

/** The list of features that can be supported by a price rule. */
export type PriceRuleTrait =
  | 'BULK'
  | 'BUY_ONE_GET_ONE'
  | 'BUY_ONE_GET_ONE_WITH_ALLOCATION_LIMIT'
  | 'QUANTITY_DISCOUNTS'
  | 'SPECIFIC_CUSTOMERS';

/** A country code from the `ISO 3166` standard. e.g. `CA` for Canada. */
export type PrivacyCountryCode =
  | 'AC'
  | 'AD'
  | 'AE'
  | 'AF'
  | 'AG'
  | 'AI'
  | 'AL'
  | 'AM'
  | 'AN'
  | 'AO'
  | 'AQ'
  | 'AR'
  | 'AS'
  | 'AT'
  | 'AU'
  | 'AW'
  | 'AX'
  | 'AZ'
  | 'BA'
  | 'BB'
  | 'BD'
  | 'BE'
  | 'BF'
  | 'BG'
  | 'BH'
  | 'BI'
  | 'BJ'
  | 'BL'
  | 'BM'
  | 'BN'
  | 'BO'
  | 'BQ'
  | 'BR'
  | 'BS'
  | 'BT'
  | 'BV'
  | 'BW'
  | 'BY'
  | 'BZ'
  | 'CA'
  | 'CC'
  | 'CD'
  | 'CF'
  | 'CG'
  | 'CH'
  | 'CI'
  | 'CK'
  | 'CL'
  | 'CM'
  | 'CN'
  | 'CO'
  | 'CR'
  | 'CU'
  | 'CV'
  | 'CW'
  | 'CX'
  | 'CY'
  | 'CZ'
  | 'DE'
  | 'DJ'
  | 'DK'
  | 'DM'
  | 'DO'
  | 'DZ'
  | 'EC'
  | 'EE'
  | 'EG'
  | 'EH'
  | 'ER'
  | 'ES'
  | 'ET'
  | 'FI'
  | 'FJ'
  | 'FK'
  | 'FM'
  | 'FO'
  | 'FR'
  | 'GA'
  | 'GB'
  | 'GD'
  | 'GE'
  | 'GF'
  | 'GG'
  | 'GH'
  | 'GI'
  | 'GL'
  | 'GM'
  | 'GN'
  | 'GP'
  | 'GQ'
  | 'GR'
  | 'GS'
  | 'GT'
  | 'GU'
  | 'GW'
  | 'GY'
  | 'HK'
  | 'HM'
  | 'HN'
  | 'HR'
  | 'HT'
  | 'HU'
  | 'ID'
  | 'IE'
  | 'IL'
  | 'IM'
  | 'IN'
  | 'IO'
  | 'IQ'
  | 'IR'
  | 'IS'
  | 'IT'
  | 'JE'
  | 'JM'
  | 'JO'
  | 'JP'
  | 'KE'
  | 'KG'
  | 'KH'
  | 'KI'
  | 'KM'
  | 'KN'
  | 'KP'
  | 'KR'
  | 'KW'
  | 'KY'
  | 'KZ'
  | 'LA'
  | 'LB'
  | 'LC'
  | 'LI'
  | 'LK'
  | 'LR'
  | 'LS'
  | 'LT'
  | 'LU'
  | 'LV'
  | 'LY'
  | 'MA'
  | 'MC'
  | 'MD'
  | 'ME'
  | 'MF'
  | 'MG'
  | 'MH'
  | 'MK'
  | 'ML'
  | 'MM'
  | 'MN'
  | 'MO'
  | 'MP'
  | 'MQ'
  | 'MR'
  | 'MS'
  | 'MT'
  | 'MU'
  | 'MV'
  | 'MW'
  | 'MX'
  | 'MY'
  | 'MZ'
  | 'NA'
  | 'NC'
  | 'NE'
  | 'NF'
  | 'NG'
  | 'NI'
  | 'NL'
  | 'NO'
  | 'NP'
  | 'NR'
  | 'NS'
  | 'NU'
  | 'NZ'
  | 'OM'
  | 'PA'
  | 'PE'
  | 'PF'
  | 'PG'
  | 'PH'
  | 'PK'
  | 'PL'
  | 'PM'
  | 'PN'
  | 'PR'
  | 'PS'
  | 'PT'
  | 'PW'
  | 'PY'
  | 'QA'
  | 'RE'
  | 'RO'
  | 'RS'
  | 'RU'
  | 'RW'
  | 'SA'
  | 'SB'
  | 'SC'
  | 'SD'
  | 'SE'
  | 'SG'
  | 'SH'
  | 'SI'
  | 'SJ'
  | 'SK'
  | 'SL'
  | 'SM'
  | 'SN'
  | 'SO'
  | 'SR'
  | 'SS'
  | 'ST'
  | 'SV'
  | 'SX'
  | 'SY'
  | 'SZ'
  | 'TA'
  | 'TC'
  | 'TD'
  | 'TF'
  | 'TG'
  | 'TH'
  | 'TJ'
  | 'TK'
  | 'TL'
  | 'TM'
  | 'TN'
  | 'TO'
  | 'TR'
  | 'TT'
  | 'TV'
  | 'TW'
  | 'TZ'
  | 'UA'
  | 'UG'
  | 'UM'
  | 'US'
  | 'UY'
  | 'UZ'
  | 'VA'
  | 'VC'
  | 'VE'
  | 'VG'
  | 'VI'
  | 'VN'
  | 'VU'
  | 'WF'
  | 'WS'
  | 'XK'
  | 'XX'
  | 'YE'
  | 'YT'
  | 'ZA'
  | 'ZM'
  | 'ZW';

/** Possible error codes that can be returned by `PrivacyFeaturesDisableUserError`. */
export type PrivacyFeaturesDisableUserErrorCode =
  | 'FAILED';

/** The input fields for a shop's privacy settings. */
export type PrivacyFeaturesEnum =
  | 'COOKIE_BANNER'
  | 'DATA_SALE_OPT_OUT_PAGE'
  | 'PRIVACY_POLICY';

/** The status of a component option value related to a bundle. */
export type ProductBundleComponentOptionSelectionStatus =
  | 'DESELECTED'
  | 'NEW'
  | 'SELECTED'
  | 'UNAVAILABLE';

/** Possible error codes that can be returned by `ProductBundleMutationUserError`. */
export type ProductBundleMutationUserErrorCode =
  | 'GENERIC_ERROR'
  | 'INVALID_INPUT'
  | 'JOB_ERROR'
  | 'PRODUCT_DOES_NOT_EXIST';

/** Possible error codes that can be returned by `ProductChangeStatusUserError`. */
export type ProductChangeStatusUserErrorCode =
  | 'COMBINED_LISTINGS_NOT_COMPATIBLE_WITH_SHOP'
  | 'PRODUCT_NOT_FOUND';

/** The set of valid sort keys for products belonging to a collection. */
export type ProductCollectionSortKeys =
  | 'BEST_SELLING'
  | 'COLLECTION_DEFAULT'
  | 'CREATED'
  | 'ID'
  | 'MANUAL'
  | 'PRICE'
  | 'RELEVANCE'
  | 'TITLE';

/** Possible error codes that can be returned by `ProductFeedCreateUserError`. */
export type ProductFeedCreateUserErrorCode =
  | 'INVALID'
  | 'TAKEN';

/** Possible error codes that can be returned by `ProductFeedDeleteUserError`. */
export type ProductFeedDeleteUserErrorCode =
  | 'INVALID';

/** The valid values for the status of product feed. */
export type ProductFeedStatus =
  | 'ACTIVE'
  | 'INACTIVE';

/** Possible error codes that can be returned by `ProductFullSyncUserError`. */
export type ProductFullSyncUserErrorCode =
  | 'INVALID';

/** The set of valid sort keys for the ProductImage query. */
export type ProductImageSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'POSITION';

/** The set of valid sort keys for the ProductMedia query. */
export type ProductMediaSortKeys =
  | 'ID'
  | 'POSITION';

/** Represents the state of this product operation. */
export type ProductOperationStatus =
  | 'ACTIVE'
  | 'COMPLETE'
  | 'CREATED';

export type ProductOptionCreateVariantStrategy =
  | 'CREATE'
  | 'LEAVE_AS_IS';

export type ProductOptionDeleteStrategy =
  | 'DEFAULT'
  | 'NON_DESTRUCTIVE'
  | 'POSITION';

/** Possible error codes that can be returned by `ProductOptionsCreateUserError`. */
export type ProductOptionsCreateUserErrorCode =
  | 'CANNOT_COMBINE_LINKED_METAFIELD_AND_OPTION_VALUES'
  | 'CANNOT_MAKE_CHANGES_IF_VARIANT_IS_MISSING_REQUIRED_SKU'
  | 'DUPLICATE_LINKED_OPTION'
  | 'DUPLICATED_OPTION_NAME'
  | 'DUPLICATED_OPTION_VALUE'
  | 'INVALID_METAFIELD_VALUE_FOR_LINKED_OPTION'
  | 'INVALID_NAME'
  | 'LINKED_METAFIELD_DEFINITION_NOT_FOUND'
  | 'LINKED_METAFIELD_VALUE_WITHOUT_LINKED_OPTION'
  | 'LINKED_OPTIONS_NOT_SUPPORTED_FOR_SHOP'
  | 'MISSING_METAFIELD_VALUES_FOR_LINKED_OPTION'
  | 'NEW_OPTION_WITHOUT_VALUE_FOR_EXISTING_VARIANTS'
  | 'OPTION_ALREADY_EXISTS'
  | 'OPTION_LINKED_METAFIELD_ALREADY_TAKEN'
  | 'OPTION_NAME_MISSING'
  | 'OPTION_NAME_TOO_LONG'
  | 'OPTION_POSITION_MISSING'
  | 'OPTION_VALUE_NAME_TOO_LONG'
  | 'OPTION_VALUES_MISSING'
  | 'OPTION_VALUES_OVER_LIMIT'
  | 'OPTIONS_OVER_LIMIT'
  | 'POSITION_OUT_OF_BOUNDS'
  | 'PRODUCT_DOES_NOT_EXIST'
  | 'PRODUCT_SUSPENDED'
  | 'TOO_MANY_VARIANTS_CREATED'
  | 'UNSUPPORTED_COMBINED_LISTING_PARENT_OPERATION';

/** Possible error codes that can be returned by `ProductOptionsDeleteUserError`. */
export type ProductOptionsDeleteUserErrorCode =
  | 'CANNOT_DELETE_OPTION_WITH_MULTIPLE_VALUES'
  | 'CANNOT_DELETE_VARIANT_WITHOUT_PERMISSION'
  | 'CANNOT_MAKE_CHANGES_IF_VARIANT_IS_MISSING_REQUIRED_SKU'
  | 'CANNOT_USE_NON_DESTRUCTIVE_STRATEGY'
  | 'OPTION_DOES_NOT_EXIST'
  | 'OPTIONS_DO_NOT_BELONG_TO_THE_SAME_PRODUCT'
  | 'PRODUCT_DOES_NOT_EXIST'
  | 'PRODUCT_SUSPENDED'
  | 'UNSUPPORTED_COMBINED_LISTING_PARENT_OPERATION';

/** Possible error codes that can be returned by `ProductOptionsReorderUserError`. */
export type ProductOptionsReorderUserErrorCode =
  | 'CANNOT_MAKE_CHANGES_IF_VARIANT_IS_MISSING_REQUIRED_SKU'
  | 'DUPLICATED_OPTION_NAME'
  | 'DUPLICATED_OPTION_VALUE'
  | 'MISSING_OPTION_NAME'
  | 'MISSING_OPTION_VALUE'
  | 'MIXING_ID_AND_NAME_KEYS_IS_NOT_ALLOWED'
  | 'NO_KEY_ON_REORDER'
  | 'OPTION_ID_DOES_NOT_EXIST'
  | 'OPTION_NAME_DOES_NOT_EXIST'
  | 'OPTION_VALUE_DOES_NOT_EXIST'
  | 'OPTION_VALUE_ID_DOES_NOT_EXIST'
  | 'PRODUCT_DOES_NOT_EXIST'
  | 'PRODUCT_SUSPENDED';

/** Possible error codes that can be returned by `ProductOptionUpdateUserError`. */
export type ProductOptionUpdateUserErrorCode =
  | 'CANNOT_COMBINE_LINKED_AND_NONLINKED_OPTION_VALUES'
  | 'CANNOT_CREATE_VARIANTS_ABOVE_LIMIT'
  | 'CANNOT_DELETE_ALL_OPTION_VALUES_IN_OPTION'
  | 'CANNOT_DELETE_VARIANT_WITHOUT_PERMISSION'
  | 'CANNOT_LEAVE_OPTIONS_WITHOUT_VARIANTS'
  | 'CANNOT_MAKE_CHANGES_IF_VARIANT_IS_MISSING_REQUIRED_SKU'
  | 'DUPLICATE_LINKED_OPTION'
  | 'DUPLICATED_OPTION_VALUE'
  | 'INVALID_METAFIELD_VALUE_FOR_LINKED_OPTION'
  | 'INVALID_NAME'
  | 'INVALID_POSITION'
  | 'KEY_MISSING_IN_INPUT'
  | 'LINKED_METAFIELD_DEFINITION_NOT_FOUND'
  | 'LINKED_OPTION_UPDATE_MISSING_VALUES'
  | 'LINKED_OPTIONS_NOT_SUPPORTED_FOR_SHOP'
  | 'NO_KEY_ON_CREATE'
  | 'OPTION_ALREADY_EXISTS'
  | 'OPTION_DOES_NOT_EXIST'
  | 'OPTION_LINKED_METAFIELD_ALREADY_TAKEN'
  | 'OPTION_NAME_TOO_LONG'
  | 'OPTION_VALUE_ALREADY_EXISTS'
  | 'OPTION_VALUE_CONFLICTING_OPERATION'
  | 'OPTION_VALUE_DOES_NOT_EXIST'
  | 'OPTION_VALUE_HAS_VARIANTS'
  | 'OPTION_VALUE_NAME_TOO_LONG'
  | 'OPTION_VALUES_OVER_LIMIT'
  | 'PRODUCT_DOES_NOT_EXIST'
  | 'PRODUCT_SUSPENDED'
  | 'TOO_MANY_VARIANTS_CREATED'
  | 'UNSUPPORTED_COMBINED_LISTING_PARENT_OPERATION';

export type ProductOptionUpdateVariantStrategy =
  | 'LEAVE_AS_IS'
  | 'MANAGE';

/** Possible error codes that can be returned by `ProductSetUserError`. */
export type ProductSetUserErrorCode =
  | 'CANNOT_COMBINE_LINKED_AND_NONLINKED_OPTION_VALUES'
  | 'CAPABILITY_VIOLATION'
  | 'DUPLICATE_LINKED_OPTION'
  | 'DUPLICATED_METAFIELD_VALUE'
  | 'DUPLICATED_OPTION_NAME'
  | 'DUPLICATED_OPTION_VALUE'
  | 'DUPLICATED_VALUE'
  | 'GENERIC_ERROR'
  | 'GIFT_CARD_ATTRIBUTE_CANNOT_BE_CHANGED'
  | 'GIFT_CARDS_NOT_ACTIVATED'
  | 'HANDLE_NOT_UNIQUE'
  | 'ID_NOT_ALLOWED'
  | 'INPUT_MISMATCH'
  | 'INVALID_INPUT'
  | 'INVALID_METAFIELD'
  | 'INVALID_METAFIELD_VALUE_FOR_LINKED_OPTION'
  | 'INVALID_PRODUCT'
  | 'INVALID_VARIANT'
  | 'INVENTORY_QUANTITIES_LIMIT_EXCEEDED'
  | 'JOB_ERROR'
  | 'LINKED_METAFIELD_DEFINITION_NOT_FOUND'
  | 'LINKED_OPTIONS_NOT_SUPPORTED_FOR_SHOP'
  | 'METAFIELD_MISMATCH'
  | 'MISSING_FIELD_REQUIRED'
  | 'NOT_FOUND'
  | 'OPTION_DOES_NOT_EXIST'
  | 'OPTION_VALUE_DOES_NOT_EXIST'
  | 'OPTION_VALUES_MISSING'
  | 'OPTION_VALUES_OVER_LIMIT'
  | 'OPTIONS_OVER_LIMIT'
  | 'PRODUCT_DOES_NOT_EXIST'
  | 'PRODUCT_OPTIONS_INPUT_MISSING'
  | 'PRODUCT_SUSPENDED'
  | 'PRODUCT_VARIANT_DOES_NOT_EXIST'
  | 'VARIANTS_INPUT_MISSING'
  | 'VARIANTS_OVER_LIMIT';

/** The set of valid sort keys for the Product query. */
export type ProductSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'INVENTORY_TOTAL'
  | 'PRODUCT_TYPE'
  | 'PUBLISHED_AT'
  | 'RELEVANCE'
  | 'TITLE'
  | 'UPDATED_AT'
  | 'VENDOR';

/** The possible product statuses. */
export type ProductStatus =
  | 'ACTIVE'
  | 'ARCHIVED'
  | 'DRAFT'
  | 'UNLISTED';

/** The valid values for the inventory policy of a product variant once it is out of stock. */
export type ProductVariantInventoryPolicy =
  | 'CONTINUE'
  | 'DENY';

/** Possible error codes that can be returned by `ProductVariantRelationshipBulkUpdateUserError`. */
export type ProductVariantRelationshipBulkUpdateUserErrorCode =
  | 'CHILD_PRODUCT_VARIANT_CANNOT_BE_COMBINED_LISTING'
  | 'CIRCULAR_REFERENCE'
  | 'DUPLICATE_PRODUCT_VARIANT_RELATIONSHIP'
  | 'EXCEEDED_PRODUCT_VARIANT_RELATIONSHIP_LIMIT'
  | 'FAILED_TO_CREATE'
  | 'FAILED_TO_REMOVE'
  | 'FAILED_TO_UPDATE'
  | 'FAILED_TO_UPDATE_PARENT_PRODUCT_VARIANT_PRICE'
  | 'INVALID_QUANTITY'
  | 'MUST_SPECIFY_COMPONENTS'
  | 'NESTED_PARENT_PRODUCT_VARIANT'
  | 'PARENT_PRODUCT_VARIANT_CANNOT_BE_COMBINED_LISTING'
  | 'PARENT_PRODUCT_VARIANT_CANNOT_BE_GIFT_CARD'
  | 'PARENT_PRODUCT_VARIANT_CANNOT_REQUIRE_SELLING_PLAN'
  | 'PARENT_REQUIRED'
  | 'PRODUCT_EXPANDER_APP_OWNERSHIP_ALREADY_EXISTS'
  | 'PRODUCT_VARIANT_RELATIONSHIP_TYPE_CONFLICT'
  | 'PRODUCT_VARIANTS_NOT_COMPONENTS'
  | 'PRODUCT_VARIANTS_NOT_FOUND'
  | 'UNEXPECTED_ERROR'
  | 'UNSUPPORTED_MULTIPACK_RELATIONSHIP'
  | 'UPDATE_PARENT_VARIANT_PRICE_REQUIRED';

/** The set of strategies available for use on the `productVariantsBulkCreate` mutation. */
export type ProductVariantsBulkCreateStrategy =
  | 'DEFAULT'
  | 'PRESERVE_STANDALONE_VARIANT'
  | 'REMOVE_STANDALONE_VARIANT';

/** Possible error codes that can be returned by `ProductVariantsBulkCreateUserError`. */
export type ProductVariantsBulkCreateUserErrorCode =
  | 'CANNOT_SET_NAME_FOR_LINKED_OPTION_VALUE'
  | 'GREATER_THAN_OR_EQUAL_TO'
  | 'INVALID'
  | 'INVALID_INPUT'
  | 'INVENTORY_QUANTITIES_LIMIT_EXCEEDED'
  | 'MUST_BE_FOR_THIS_PRODUCT'
  | 'NEED_TO_ADD_OPTION_VALUES'
  | 'NEGATIVE_PRICE_VALUE'
  | 'NO_KEY_ON_CREATE'
  | 'NOT_DEFINED_FOR_SHOP'
  | 'OPTION_VALUES_FOR_NUMBER_OF_UNKNOWN_OPTIONS'
  | 'PRODUCT_DOES_NOT_EXIST'
  | 'PRODUCT_SUSPENDED'
  | 'SUBSCRIPTION_VIOLATION'
  | 'TOO_MANY_INVENTORY_LOCATIONS'
  | 'TRACKED_VARIANT_LOCATION_NOT_FOUND'
  | 'UNSUPPORTED_COMBINED_LISTING_PARENT_OPERATION'
  | 'VARIANT_ALREADY_EXISTS'
  | 'VARIANT_ALREADY_EXISTS_CHANGE_OPTION_VALUE';

/** Possible error codes that can be returned by `ProductVariantsBulkDeleteUserError`. */
export type ProductVariantsBulkDeleteUserErrorCode =
  | 'AT_LEAST_ONE_VARIANT_DOES_NOT_BELONG_TO_THE_PRODUCT'
  | 'CANNOT_DELETE_LAST_VARIANT'
  | 'PRODUCT_DOES_NOT_EXIST'
  | 'PRODUCT_SUSPENDED'
  | 'UNSUPPORTED_COMBINED_LISTING_PARENT_OPERATION';

/** Possible error codes that can be returned by `ProductVariantsBulkReorderUserError`. */
export type ProductVariantsBulkReorderUserErrorCode =
  | 'DUPLICATED_VARIANT_ID'
  | 'GENERIC_ERROR'
  | 'INVALID_POSITION'
  | 'MISSING_VARIANT'
  | 'PRODUCT_DOES_NOT_EXIST';

/** Possible error codes that can be returned by `ProductVariantsBulkUpdateUserError`. */
export type ProductVariantsBulkUpdateUserErrorCode =
  | 'BLANK'
  | 'CANNOT_SET_NAME_FOR_LINKED_OPTION_VALUE'
  | 'CANNOT_SPECIFY_BOTH'
  | 'GREATER_THAN_OR_EQUAL_TO'
  | 'INVALID_INPUT'
  | 'INVALID_VALUE'
  | 'INVENTORY_QUANTITIES_LIMIT_EXCEEDED'
  | 'MUST_BE_FOR_THIS_PRODUCT'
  | 'MUST_SPECIFY_ONE_OF_PAIR'
  | 'NEED_TO_ADD_OPTION_VALUES'
  | 'NEGATIVE_PRICE_VALUE'
  | 'NO_INVENTORY_QUANTITES_DURING_UPDATE'
  | 'NO_INVENTORY_QUANTITIES_ON_VARIANTS_UPDATE'
  | 'NOT_DEFINED_FOR_SHOP'
  | 'OPTION_DOES_NOT_EXIST'
  | 'OPTION_VALUE_DOES_NOT_EXIST'
  | 'OPTION_VALUE_NAME_TOO_LONG'
  | 'OPTION_VALUES_FOR_NUMBER_OF_UNKNOWN_OPTIONS'
  | 'PRODUCT_DOES_NOT_EXIST'
  | 'PRODUCT_SUSPENDED'
  | 'PRODUCT_VARIANT_DOES_NOT_EXIST'
  | 'PRODUCT_VARIANT_ID_MISSING'
  | 'SUBSCRIPTION_VIOLATION'
  | 'TOO_LONG'
  | 'TOO_SHORT'
  | 'UNSUPPORTED_COMBINED_LISTING_PARENT_OPERATION'
  | 'VARIANT_ALREADY_EXISTS';

/** The set of valid sort keys for the ProductVariant query. */
export type ProductVariantSortKeys =
  | 'FULL_TITLE'
  | 'ID'
  | 'INVENTORY_LEVELS_AVAILABLE'
  | 'INVENTORY_MANAGEMENT'
  | 'INVENTORY_POLICY'
  | 'INVENTORY_QUANTITY'
  | 'NAME'
  | 'POPULAR'
  | 'POSITION'
  | 'RELEVANCE'
  | 'SKU'
  | 'TITLE';

/** The set of valid sort keys for the ProfileItem query. */
export type ProfileItemSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'INVENTORY_TOTAL'
  | 'PRODUCT_TYPE'
  | 'PUBLISHED_AT'
  | 'RELEVANCE'
  | 'TITLE'
  | 'UPDATED_AT'
  | 'VENDOR';

/** The input fields for the possible values for the default state of a publication. */
export type PublicationCreateInputPublicationDefaultState =
  | 'ALL_PRODUCTS'
  | 'EMPTY';

/** Possible error codes that can be returned by `PublicationUserError`. */
export type PublicationUserErrorCode =
  | 'BLANK'
  | 'CANNOT_MODIFY_APP_CATALOG'
  | 'CANNOT_MODIFY_APP_CATALOG_PUBLICATION'
  | 'CANNOT_MODIFY_MARKET_CATALOG'
  | 'CANNOT_MODIFY_MARKET_CATALOG_PUBLICATION'
  | 'CATALOG_NOT_FOUND'
  | 'INVALID'
  | 'INVALID_PUBLISHABLE_ID'
  | 'MARKET_NOT_FOUND'
  | 'PRODUCT_TYPE_INCOMPATIBLE_WITH_CATALOG_TYPE'
  | 'PUBLICATION_LOCKED'
  | 'PUBLICATION_NOT_FOUND'
  | 'PUBLICATION_UPDATE_LIMIT_EXCEEDED'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT'
  | 'UNSUPPORTED_PUBLICATION_ACTION'
  | 'UNSUPPORTED_PUBLISHABLE_TYPE';

/** Possible error codes that can be returned by `PubSubWebhookSubscriptionCreateUserError`. */
export type PubSubWebhookSubscriptionCreateUserErrorCode =
  | 'INVALID_PARAMETERS'
  | 'TAKEN';

/** Possible error codes that can be returned by `PubSubWebhookSubscriptionUpdateUserError`. */
export type PubSubWebhookSubscriptionUpdateUserErrorCode =
  | 'INVALID_PARAMETERS'
  | 'TAKEN';

/** The set of valid sort keys for the QuantityPriceBreak query. */
export type QuantityPriceBreakSortKeys =
  | 'ID'
  | 'MINIMUM_QUANTITY';

/** Possible error codes that can be returned by `QuantityPricingByVariantUserError`. */
export type QuantityPricingByVariantUserErrorCode =
  | 'BLANK'
  | 'GENERIC_ERROR'
  | 'PRICE_ADD_CURRENCY_MISMATCH'
  | 'PRICE_ADD_DUPLICATE_INPUT_FOR_VARIANT'
  | 'PRICE_ADD_LOCAL_CURRENCY_GIFT_CARD_ISSUANCE_CURRENCY_MISMATCH'
  | 'PRICE_ADD_LOCAL_CURRENCY_GIFT_CARD_LIMIT_EXCEEDED'
  | 'PRICE_ADD_VARIANT_NOT_FOUND'
  | 'PRICE_DELETE_PRICE_NOT_FIXED'
  | 'PRICE_DELETE_VARIANT_NOT_FOUND'
  | 'PRICE_LIST_NOT_FOUND'
  | 'QUANTITY_PRICE_BREAK_ADD_CURRENCY_MISMATCH'
  | 'QUANTITY_PRICE_BREAK_ADD_DUPLICATE_INPUT_FOR_VARIANT_AND_MIN'
  | 'QUANTITY_PRICE_BREAK_ADD_FAILED_TO_SAVE'
  | 'QUANTITY_PRICE_BREAK_ADD_INVALID'
  | 'QUANTITY_PRICE_BREAK_ADD_LIMIT_EXCEEDED'
  | 'QUANTITY_PRICE_BREAK_ADD_MIN_HIGHER_THAN_QUANTITY_RULES_MAX'
  | 'QUANTITY_PRICE_BREAK_ADD_MIN_LOWER_THAN_QUANTITY_RULES_MIN'
  | 'QUANTITY_PRICE_BREAK_ADD_MIN_NOT_A_MULTIPLE_OF_QUANTITY_RULES_INCREMENT'
  | 'QUANTITY_PRICE_BREAK_ADD_PRICE_LIST_PRICE_NOT_FOUND'
  | 'QUANTITY_PRICE_BREAK_ADD_VARIANT_NOT_FOUND'
  | 'QUANTITY_PRICE_BREAK_DELETE_BY_VARIANT_ID_VARIANT_NOT_FOUND'
  | 'QUANTITY_PRICE_BREAK_DELETE_FAILED'
  | 'QUANTITY_PRICE_BREAK_DELETE_NOT_FOUND'
  | 'QUANTITY_RULE_ADD_CATALOG_CONTEXT_NOT_SUPPORTED'
  | 'QUANTITY_RULE_ADD_DUPLICATE_INPUT_FOR_VARIANT'
  | 'QUANTITY_RULE_ADD_INCREMENT_IS_GREATER_THAN_MINIMUM'
  | 'QUANTITY_RULE_ADD_INCREMENT_IS_LESS_THAN_ONE'
  | 'QUANTITY_RULE_ADD_INCREMENT_NOT_A_MULTIPLE_OF_QUANTITY_PRICE_BREAK_MIN'
  | 'QUANTITY_RULE_ADD_MAX_LOWER_THAN_QUANTITY_PRICE_BREAK_MIN'
  | 'QUANTITY_RULE_ADD_MAXIMUM_IS_LESS_THAN_ONE'
  | 'QUANTITY_RULE_ADD_MAXIMUM_NOT_A_MULTIPLE_OF_INCREMENT'
  | 'QUANTITY_RULE_ADD_MIN_HIGHER_THAN_QUANTITY_PRICE_BREAK_MIN'
  | 'QUANTITY_RULE_ADD_MINIMUM_GREATER_THAN_MAXIMUM'
  | 'QUANTITY_RULE_ADD_MINIMUM_IS_LESS_THAN_ONE'
  | 'QUANTITY_RULE_ADD_MINIMUM_NOT_A_MULTIPLE_OF_INCREMENT'
  | 'QUANTITY_RULE_ADD_VARIANT_NOT_FOUND'
  | 'QUANTITY_RULE_DELETE_RULE_NOT_FOUND'
  | 'QUANTITY_RULE_DELETE_VARIANT_NOT_FOUND';

/** The origin of quantity rule on a price list. */
export type QuantityRuleOriginType =
  | 'FIXED'
  | 'RELATIVE';

/** Possible error codes that can be returned by `QuantityRuleUserError`. */
export type QuantityRuleUserErrorCode =
  | 'BLANK'
  | 'CATALOG_CONTEXT_DOES_NOT_SUPPORT_QUANTITY_RULES'
  | 'DUPLICATE_INPUT_FOR_VARIANT'
  | 'GENERIC_ERROR'
  | 'GREATER_THAN_OR_EQUAL_TO'
  | 'INCREMENT_IS_GREATER_THAN_MINIMUM'
  | 'INCREMENT_NOT_A_MULTIPLE_OF_QUANTITY_PRICE_BREAK_MINIMUM'
  | 'MAXIMUM_IS_LOWER_THAN_QUANTITY_PRICE_BREAK_MINIMUM'
  | 'MAXIMUM_NOT_MULTIPLE_OF_INCREMENT'
  | 'MINIMUM_IS_GREATER_THAN_MAXIMUM'
  | 'MINIMUM_IS_HIGHER_THAN_QUANTITY_PRICE_BREAK_MINIMUM'
  | 'MINIMUM_NOT_MULTIPLE_OF_INCREMENT'
  | 'PRICE_LIST_DOES_NOT_EXIST'
  | 'PRODUCT_VARIANT_DOES_NOT_EXIST'
  | 'VARIANT_QUANTITY_RULE_DOES_NOT_EXIST';

/** The type of refund to perform for a particular refund duty. */
export type RefundDutyRefundType =
  | 'FULL'
  | 'PROPORTIONAL';

/** The type of restock performed for a particular refund line item. */
export type RefundLineItemRestockType =
  | 'CANCEL'
  | 'LEGACY_RESTOCK'
  | 'NO_RESTOCK'
  | 'RETURN';

/** The different methods that a refund amount can be allocated to. */
export type RefundMethodAllocation =
  | 'ORIGINAL_PAYMENT_METHODS'
  | 'STORE_CREDIT';

/** The available icons for resource alerts. */
export type ResourceAlertIcon =
  | 'CHECKMARK_CIRCLE'
  | 'INFORMATION_CIRCLE';

/** The possible severity levels for a resource alert. */
export type ResourceAlertSeverity =
  | 'CRITICAL'
  | 'DEFAULT'
  | 'INFO'
  | 'SUCCESS'
  | 'WARNING'
  | 'ERROR';

/** The state of the resource feedback. */
export type ResourceFeedbackState =
  | 'ACCEPTED'
  | 'REQUIRES_ACTION';

/** Represents the state of this catalog operation. */
export type ResourceOperationStatus =
  | 'ACTIVE'
  | 'COMPLETE'
  | 'CREATED';

/** The reason why the merchant declined a customer's return request. */
export type ReturnDeclineReason =
  | 'FINAL_SALE'
  | 'OTHER'
  | 'RETURN_PERIOD_ENDED';

/** Possible error codes that can be returned by `ReturnUserError`. */
export type ReturnErrorCode =
  | 'ALREADY_EXISTS'
  | 'BLANK'
  | 'CREATION_FAILED'
  | 'EQUAL_TO'
  | 'FEATURE_NOT_ENABLED'
  | 'GREATER_THAN'
  | 'GREATER_THAN_OR_EQUAL_TO'
  | 'INCLUSION'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'INVALID_STATE'
  | 'LESS_THAN'
  | 'LESS_THAN_OR_EQUAL_TO'
  | 'MISSING_PERMISSION'
  | 'NOT_A_NUMBER'
  | 'NOT_EDITABLE'
  | 'NOT_FOUND'
  | 'NOTIFICATION_FAILED'
  | 'PRESENT'
  | 'TAKEN'
  | 'TOO_BIG'
  | 'TOO_LONG'
  | 'TOO_MANY_ARGUMENTS'
  | 'TOO_SHORT'
  | 'WRONG_LENGTH';

/** Filter line items based on processing status. */
export type ReturnProcessingStatusFilterInput =
  | 'PROCESSABLE'
  | 'PROCESSED';

/** The reason for returning the return line item. */
export type ReturnReason =
  | 'COLOR'
  | 'DEFECTIVE'
  | 'NOT_AS_DESCRIBED'
  | 'OTHER'
  | 'SIZE_TOO_LARGE'
  | 'SIZE_TOO_SMALL'
  | 'STYLE'
  | 'UNKNOWN'
  | 'UNWANTED'
  | 'WRONG_ITEM';

/** The set of valid sort keys for the ReturnReasonDefinition query. */
export type ReturnReasonDefinitionSortKeys =
  | 'HANDLE'
  | 'ID'
  | 'NAME';

/** The status of a return. */
export type ReturnStatus =
  | 'CANCELED'
  | 'CLOSED'
  | 'DECLINED'
  | 'OPEN'
  | 'REQUESTED';

/** The final arrangement of an item from a reverse fulfillment order. */
export type ReverseFulfillmentOrderDispositionType =
  | 'MISSING'
  | 'NOT_RESTOCKED'
  | 'PROCESSING_REQUIRED'
  | 'RESTOCKED';

/** The status of a reverse fulfillment order. */
export type ReverseFulfillmentOrderStatus =
  | 'CANCELED'
  | 'CLOSED'
  | 'OPEN';

/** The status of a reverse fulfillment order third-party confirmation. */
export type ReverseFulfillmentOrderThirdPartyConfirmationStatus =
  | 'ACCEPTED'
  | 'CANCEL_ACCEPTED'
  | 'CANCEL_REJECTED'
  | 'PENDING_ACCEPTANCE'
  | 'PENDING_CANCELATION'
  | 'REJECTED';

/** List of possible values for a RiskAssessment result. */
export type RiskAssessmentResult =
  | 'HIGH'
  | 'LOW'
  | 'MEDIUM'
  | 'NONE'
  | 'PENDING';

/** List of possible values for a RiskFact sentiment. */
export type RiskFactSentiment =
  | 'NEGATIVE'
  | 'NEUTRAL'
  | 'POSITIVE';

/** The possible order action types for a sale. */
export type SaleActionType =
  | 'ORDER'
  | 'RETURN'
  | 'UNKNOWN'
  | 'UPDATE';

/** The possible line types for a sale record. One of the possible order line types for a sale is an adjustment. Sales adjustments occur when a refund is issued for a line item that is either more or less than the total value of the line item. Examples are restocking fees and good... */
export type SaleLineType =
  | 'ADDITIONAL_FEE'
  | 'ADJUSTMENT'
  | 'DUTY'
  | 'FEE'
  | 'GIFT_CARD'
  | 'PRODUCT'
  | 'SHIPPING'
  | 'TIP'
  | 'UNKNOWN';

/** The set of valid sort keys for the ScheduledChange query. */
export type ScheduledChangeSortKeys =
  | 'EXPECTED_AT'
  | 'ID';

/** The page or pages on the online store where the script should be included. */
export type ScriptTagDisplayScope =
  | 'ONLINE_STORE'
  | 'ALL'
  | 'ORDER_STATUS';

/** Specifies the type of resources to be returned from a search. */
export type SearchResultType =
  | 'ARTICLE'
  | 'BALANCE_TRANSACTION'
  | 'BLOG'
  | 'COLLECTION'
  | 'CUSTOMER'
  | 'DISCOUNT_REDEEM_CODE'
  | 'DRAFT_ORDER'
  | 'FILE'
  | 'INVENTORY_TRANSFER'
  | 'ORDER'
  | 'PAGE'
  | 'PRICE_RULE'
  | 'PRODUCT'
  | 'URL_REDIRECT';

/** The set of valid sort keys for the Segment query. */
export type SegmentSortKeys =
  | 'CREATION_DATE'
  | 'ID'
  | 'LAST_EDIT_DATE'
  | 'RELEVANCE';

/** Represents the anchor type. */
export type SellingPlanAnchorType =
  | 'MONTHDAY'
  | 'WEEKDAY'
  | 'YEARDAY';

/** The category of the selling plan. For the `OTHER` category, you must fill out our [request form](https://docs.google.com/forms/d/e/1FAIpQLSeU18Xmw0Q61V8wdH-dfGafFqIBfRchQKUO8WAF3yJTvgyyZQ/viewform), where we'll review your request for a new purchase option. */
export type SellingPlanCategory =
  | 'OTHER'
  | 'PRE_ORDER'
  | 'SUBSCRIPTION'
  | 'TRY_BEFORE_YOU_BUY';

/** The checkout charge when the full amount isn't charged at checkout. */
export type SellingPlanCheckoutChargeType =
  | 'PERCENTAGE'
  | 'PRICE';

/** Possible intentions of a Delivery Policy. */
export type SellingPlanFixedDeliveryPolicyIntent =
  | 'FULFILLMENT_BEGIN';

/** The fulfillment or delivery behavior of the first fulfillment when the orderis placed before the anchor. */
export type SellingPlanFixedDeliveryPolicyPreAnchorBehavior =
  | 'ASAP'
  | 'NEXT';

/** Describes what triggers fulfillment. */
export type SellingPlanFulfillmentTrigger =
  | 'ANCHOR'
  | 'ASAP'
  | 'EXACT_TIME'
  | 'UNKNOWN';

/** The set of valid sort keys for the SellingPlanGroup query. */
export type SellingPlanGroupSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'NAME'
  | 'UPDATED_AT';

/** Possible error codes that can be returned by `SellingPlanGroupUserError`. */
export type SellingPlanGroupUserErrorCode =
  | 'BILLING_AND_DELIVERY_POLICY_TYPES_MUST_BE_THE_SAME'
  | 'BILLING_POLICY_INTERVAL_TOO_LARGE'
  | 'BLANK'
  | 'CHECKOUT_CHARGE_VALUE_AND_TYPE_MUST_MATCH'
  | 'DELIVERY_POLICY_INTERVAL_TOO_LARGE'
  | 'EQUAL_TO'
  | 'ERROR_ADDING_RESOURCE_TO_GROUP'
  | 'FULFILLMENT_EXACT_TIME_NOT_ALLOWED'
  | 'FULFILLMENT_EXACT_TIME_REQUIRED'
  | 'GREATER_THAN'
  | 'GREATER_THAN_OR_EQUAL_TO'
  | 'GROUP_COULD_NOT_BE_DELETED'
  | 'GROUP_DOES_NOT_EXIST'
  | 'INCLUSION'
  | 'INVALID'
  | 'INVALID_INPUT'
  | 'LESS_THAN'
  | 'LESS_THAN_OR_EQUAL_TO'
  | 'NOT_A_NUMBER'
  | 'NOT_FOUND'
  | 'ONLY_NEED_ONE_BILLING_POLICY_TYPE'
  | 'ONLY_NEED_ONE_CHECKOUT_CHARGE_VALUE'
  | 'ONLY_NEED_ONE_DELIVERY_POLICY_TYPE'
  | 'ONLY_NEED_ONE_PRICING_POLICY_TYPE'
  | 'ONLY_NEED_ONE_PRICING_POLICY_VALUE'
  | 'ONLY_ONE_OF_FIXED_OR_RECURRING_BILLING'
  | 'ONLY_ONE_OF_FIXED_OR_RECURRING_DELIVERY'
  | 'PLAN_DOES_NOT_EXIST'
  | 'PLAN_ID_MUST_BE_SPECIFIED_TO_UPDATE'
  | 'PRESENT'
  | 'PRICING_POLICY_ADJUSTMENT_VALUE_AND_TYPE_MUST_MATCH'
  | 'PRODUCT_DOES_NOT_EXIST'
  | 'PRODUCT_VARIANT_DOES_NOT_EXIST'
  | 'REMAINING_BALANCE_CHARGE_EXACT_TIME_NOT_ALLOWED'
  | 'REMAINING_BALANCE_CHARGE_EXACT_TIME_REQUIRED'
  | 'REMAINING_BALANCE_CHARGE_TIME_AFTER_CHECKOUT_MUST_BE_GREATER_THAN_ZERO'
  | 'REMAINING_BALANCE_CHARGE_TRIGGER_NO_REMAINING_BALANCE_ON_PARTIAL_PERCENTAGE_CHECKOUT_CHARGE'
  | 'REMAINING_BALANCE_CHARGE_TRIGGER_NO_REMAINING_BALANCE_ON_PRICE_CHECKOUT_CHARGE'
  | 'REMAINING_BALANCE_CHARGE_TRIGGER_ON_FULL_CHECKOUT'
  | 'RESOURCE_LIST_CONTAINS_INVALID_IDS'
  | 'SELLING_PLAN_ANCHORS_NOT_ALLOWED'
  | 'SELLING_PLAN_ANCHORS_REQUIRED'
  | 'SELLING_PLAN_BILLING_AND_DELIVERY_POLICY_ANCHORS_MUST_BE_EQUAL'
  | 'SELLING_PLAN_BILLING_CYCLE_MUST_BE_A_MULTIPLE_OF_DELIVERY_CYCLE'
  | 'SELLING_PLAN_BILLING_POLICY_MISSING'
  | 'SELLING_PLAN_COUNT_LOWER_BOUND'
  | 'SELLING_PLAN_COUNT_UPPER_BOUND'
  | 'SELLING_PLAN_DELIVERY_POLICY_MISSING'
  | 'SELLING_PLAN_DUPLICATE_NAME'
  | 'SELLING_PLAN_DUPLICATE_OPTIONS'
  | 'SELLING_PLAN_FIXED_PRICING_POLICIES_LIMIT'
  | 'SELLING_PLAN_MAX_CYCLES_MUST_BE_GREATER_THAN_MIN_CYCLES'
  | 'SELLING_PLAN_MISSING_OPTION2_LABEL_ON_PARENT_GROUP'
  | 'SELLING_PLAN_MISSING_OPTION3_LABEL_ON_PARENT_GROUP'
  | 'SELLING_PLAN_OPTION2_REQUIRED_AS_DEFINED_ON_PARENT_GROUP'
  | 'SELLING_PLAN_OPTION3_REQUIRED_AS_DEFINED_ON_PARENT_GROUP'
  | 'SELLING_PLAN_PRICING_POLICIES_LIMIT'
  | 'SELLING_PLAN_PRICING_POLICIES_MUST_CONTAIN_A_FIXED_PRICING_POLICY'
  | 'TAKEN'
  | 'TOO_BIG'
  | 'TOO_LONG'
  | 'TOO_SHORT'
  | 'WRONG_LENGTH';

/** Represents valid selling plan interval. */
export type SellingPlanInterval =
  | 'DAY'
  | 'MONTH'
  | 'WEEK'
  | 'YEAR';

/** Represents a selling plan pricing policy adjustment type. */
export type SellingPlanPricingPolicyAdjustmentType =
  | 'FIXED_AMOUNT'
  | 'PERCENTAGE'
  | 'PRICE';

/** Whether the delivery policy is merchant or buyer-centric. */
export type SellingPlanRecurringDeliveryPolicyIntent =
  | 'FULFILLMENT_BEGIN';

/** The fulfillment or delivery behaviors of the first fulfillment when the orderis placed before the anchor. */
export type SellingPlanRecurringDeliveryPolicyPreAnchorBehavior =
  | 'ASAP'
  | 'NEXT';

/** When to capture the payment for the remaining amount due. */
export type SellingPlanRemainingBalanceChargeTrigger =
  | 'EXACT_TIME'
  | 'NO_REMAINING_BALANCE'
  | 'ON_FULFILLMENT'
  | 'TIME_AFTER_CHECKOUT';

/** When to reserve inventory for a selling plan. */
export type SellingPlanReserve =
  | 'ON_FULFILLMENT'
  | 'ON_SALE';

/** The current state of a server pixel. */
export type ServerPixelStatus =
  | 'CONNECTED'
  | 'DISCONNECTED_CONFIGURED'
  | 'DISCONNECTED_UNCONFIGURED';

/** The set of valid sort keys for the ShipmentLineItem query. */
export type ShipmentLineItemSortKeys =
  | 'ID';

/** The [discount class](https://help.shopify.com/manual/discounts/combining-discounts/discount-combinations) that's used to control how discounts can be combined. */
export type ShippingDiscountClass =
  | 'SHIPPING';

/** Type of a shipping package. */
export type ShippingPackageType =
  | 'BOX'
  | 'ENVELOPE'
  | 'FLAT_RATE'
  | 'SOFT_PACK';

/** Possible branding of a shop. Branding can be used to define the look of a shop including its styling and logo in the Shopify Admin. */
export type ShopBranding =
  | 'ROGERS'
  | 'SHOPIFY'
  | 'SHOPIFY_GOLD'
  | 'SHOPIFY_PLUS';

/** Represents the shop's customer account requirement preference. */
export type ShopCustomerAccountsSetting =
  | 'DISABLED'
  | 'OPTIONAL'
  | 'REQUIRED';

/** The payout status of the balance transaction. */
export type ShopifyPaymentsBalanceTransactionPayoutStatus =
  | 'ACTION_REQUIRED'
  | 'CANCELED'
  | 'FAILED'
  | 'PAID'
  | 'PENDING'
  | 'SCHEDULED'
  | 'IN_TRANSIT';

/** The bank account status. */
export type ShopifyPaymentsBankAccountStatus =
  | 'ERRORED'
  | 'NEW'
  | 'VALIDATED'
  | 'VERIFIED';

/** The business type of a Shopify Payments account. */
export type ShopifyPaymentsBusinessType =
  | 'CORPORATION'
  | 'FREE_ZONE_ESTABLISHMENT'
  | 'FREE_ZONE_LLC'
  | 'GOVERNMENT'
  | 'INCORPORATED_PARTNERSHIP'
  | 'INDIVIDUAL'
  | 'LLC'
  | 'NON_PROFIT'
  | 'NON_PROFIT_INCORPORATED'
  | 'NON_PROFIT_REGISTERED_CHARITY'
  | 'NON_PROFIT_UNINCORPORATED'
  | 'NON_PROFIT_UNINCORPORATED_ASSOCIATION'
  | 'NOT_SET'
  | 'PARTNERSHIP'
  | 'PRIVATE_CORPORATION'
  | 'PRIVATE_MULTI_MEMBER_LLC'
  | 'PRIVATE_PARTNERSHIP'
  | 'PRIVATE_SINGLE_MEMBER_LLC'
  | 'PRIVATE_UNINCORPORATED_ASSOCIATION'
  | 'PUBLIC_COMPANY'
  | 'PUBLIC_CORPORATION'
  | 'PUBLIC_PARTNERSHIP'
  | 'SOLE_ESTABLISHMENT'
  | 'SOLE_PROP'
  | 'UNINCORPORATED_PARTNERSHIP';

/** The possible dispute evidence file types. */
export type ShopifyPaymentsDisputeEvidenceFileType =
  | 'CANCELLATION_POLICY_FILE'
  | 'CUSTOMER_COMMUNICATION_FILE'
  | 'REFUND_POLICY_FILE'
  | 'RESPONSE_SUMMARY_FILE'
  | 'SERVICE_DOCUMENTATION_FILE'
  | 'SHIPPING_DOCUMENTATION_FILE'
  | 'UNCATEGORIZED_FILE';

/** The reason for the dispute provided by the cardholder's bank. */
export type ShopifyPaymentsDisputeReason =
  | 'BANK_CANNOT_PROCESS'
  | 'CREDIT_NOT_PROCESSED'
  | 'CUSTOMER_INITIATED'
  | 'DEBIT_NOT_AUTHORIZED'
  | 'DUPLICATE'
  | 'FRAUDULENT'
  | 'GENERAL'
  | 'INCORRECT_ACCOUNT_DETAILS'
  | 'INSUFFICIENT_FUNDS'
  | 'NONCOMPLIANT'
  | 'PRODUCT_NOT_RECEIVED'
  | 'PRODUCT_UNACCEPTABLE'
  | 'SUBSCRIPTION_CANCELLED'
  | 'UNRECOGNIZED';

/** Possible error codes that can be returned by `ShopifyPaymentsPayoutAlternateCurrencyCreateUserError`. */
export type ShopifyPaymentsPayoutAlternateCurrencyCreateUserErrorCode =
  | 'ALTERNATE_CURRENCY_PAYOUT_FAILED_NO_ELIGIBLE_BALANCE'
  | 'ALTERNATE_CURRENCY_PAYOUT_FAILED_STRIPE_ERROR'
  | 'MISSING_PROVIDER_ACCOUNT'
  | 'UNKNOWN_CORE_ERROR';

/** The interval at which payouts are sent to the connected bank account. */
export type ShopifyPaymentsPayoutInterval =
  | 'DAILY'
  | 'MANUAL'
  | 'MONTHLY'
  | 'WEEKLY';

/** The transfer status of the payout. */
export type ShopifyPaymentsPayoutStatus =
  | 'CANCELED'
  | 'FAILED'
  | 'PAID'
  | 'SCHEDULED'
  | 'IN_TRANSIT';

/** The possible transaction types for a payout. */
export type ShopifyPaymentsPayoutTransactionType =
  | 'DEPOSIT'
  | 'WITHDRAWAL';

/** The possible source types for a balance transaction. */
export type ShopifyPaymentsSourceType =
  | 'ADJUSTMENT'
  | 'ADJUSTMENT_REVERSAL'
  | 'CHARGE'
  | 'DISPUTE'
  | 'REFUND'
  | 'SYSTEM_ADJUSTMENT'
  | 'TRANSFER';

/** The type of tax identification field. */
export type ShopifyPaymentsTaxIdentificationType =
  | 'EIN'
  | 'FULL_SSN'
  | 'SSN_LAST4_DIGITS';

/** The possible types of transactions. */
export type ShopifyPaymentsTransactionType =
  | 'ACH_BANK_FAILURE_DEBIT_FEE'
  | 'ACH_BANK_FAILURE_DEBIT_REVERSAL_FEE'
  | 'ADJUSTMENT'
  | 'ADS_PUBLISHER_CREDIT'
  | 'ADS_PUBLISHER_CREDIT_REVERSAL'
  | 'ADVANCE'
  | 'ADVANCE_FUNDING'
  | 'ANOMALY_CREDIT'
  | 'ANOMALY_CREDIT_REVERSAL'
  | 'ANOMALY_DEBIT'
  | 'ANOMALY_DEBIT_REVERSAL'
  | 'APPLICATION_FEE_REFUND'
  | 'BALANCE_TRANSFER_INBOUND'
  | 'BALANCE_TRANSFER_OUTBOUND'
  | 'BILLING_DEBIT'
  | 'BILLING_DEBIT_REVERSAL'
  | 'CHANNEL_CREDIT'
  | 'CHANNEL_CREDIT_REVERSAL'
  | 'CHANNEL_PROMOTION_CREDIT'
  | 'CHANNEL_PROMOTION_CREDIT_REVERSAL'
  | 'CHANNEL_TRANSFER_CREDIT'
  | 'CHANNEL_TRANSFER_CREDIT_REVERSAL'
  | 'CHANNEL_TRANSFER_DEBIT'
  | 'CHANNEL_TRANSFER_DEBIT_REVERSAL'
  | 'CHARGE'
  | 'CHARGE_ADJUSTMENT'
  | 'CHARGEBACK_FEE'
  | 'CHARGEBACK_FEE_REFUND'
  | 'CHARGEBACK_HOLD'
  | 'CHARGEBACK_HOLD_RELEASE'
  | 'CHARGEBACK_PROTECTION_CREDIT'
  | 'CHARGEBACK_PROTECTION_CREDIT_REVERSAL'
  | 'CHARGEBACK_PROTECTION_DEBIT'
  | 'CHARGEBACK_PROTECTION_DEBIT_REVERSAL'
  | 'COLLECTIONS_CREDIT'
  | 'COLLECTIONS_CREDIT_REVERSAL'
  | 'CUSTOMS_DUTY'
  | 'CUSTOMS_DUTY_ADJUSTMENT'
  | 'DISPUTE_REVERSAL'
  | 'DISPUTE_WITHDRAWAL'
  | 'IMPORT_TAX'
  | 'IMPORT_TAX_ADJUSTMENT'
  | 'IMPORT_TAX_REFUND'
  | 'LENDING_CAPITAL_REFUND'
  | 'LENDING_CAPITAL_REFUND_REVERSAL'
  | 'LENDING_CAPITAL_REMITTANCE'
  | 'LENDING_CAPITAL_REMITTANCE_REVERSAL'
  | 'LENDING_CREDIT'
  | 'LENDING_CREDIT_REFUND'
  | 'LENDING_CREDIT_REFUND_REVERSAL'
  | 'LENDING_CREDIT_REMITTANCE'
  | 'LENDING_CREDIT_REMITTANCE_REVERSAL'
  | 'LENDING_CREDIT_REVERSAL'
  | 'LENDING_DEBIT'
  | 'LENDING_DEBIT_REVERSAL'
  | 'MARKETPLACE_FEE_CREDIT'
  | 'MARKETPLACE_FEE_CREDIT_REVERSAL'
  | 'MARKETS_PRO_CREDIT'
  | 'MERCHANT_GOODWILL_CREDIT'
  | 'MERCHANT_GOODWILL_CREDIT_REVERSAL'
  | 'MERCHANT_TO_MERCHANT_CREDIT'
  | 'MERCHANT_TO_MERCHANT_CREDIT_REVERSAL'
  | 'MERCHANT_TO_MERCHANT_DEBIT'
  | 'MERCHANT_TO_MERCHANT_DEBIT_REVERSAL'
  | 'PROMOTION_CREDIT'
  | 'PROMOTION_CREDIT_REVERSAL'
  | 'REFERRAL_FEE'
  | 'REFERRAL_FEE_TAX'
  | 'REFUND'
  | 'REFUND_ADJUSTMENT'
  | 'REFUND_FAILURE'
  | 'RESERVED_FUNDS'
  | 'RESERVED_FUNDS_REVERSAL'
  | 'RESERVED_FUNDS_WITHDRAWAL'
  | 'RISK_REVERSAL'
  | 'RISK_WITHDRAWAL'
  | 'SELLER_PROTECTION_CREDIT'
  | 'SELLER_PROTECTION_CREDIT_REVERSAL'
  | 'SHIPPING_LABEL'
  | 'SHIPPING_LABEL_ADJUSTMENT'
  | 'SHIPPING_LABEL_ADJUSTMENT_BASE'
  | 'SHIPPING_LABEL_ADJUSTMENT_SURCHARGE'
  | 'SHIPPING_OTHER_CARRIER_CHARGE_ADJUSTMENT'
  | 'SHIPPING_RETURN_TO_ORIGIN_ADJUSTMENT'
  | 'SHOP_CASH_BILLING_DEBIT'
  | 'SHOP_CASH_BILLING_DEBIT_REVERSAL'
  | 'SHOP_CASH_CAMPAIGN_BILLING_CREDIT'
  | 'SHOP_CASH_CAMPAIGN_BILLING_CREDIT_REVERSAL'
  | 'SHOP_CASH_CAMPAIGN_BILLING_DEBIT'
  | 'SHOP_CASH_CAMPAIGN_BILLING_DEBIT_REVERSAL'
  | 'SHOP_CASH_CREDIT'
  | 'SHOP_CASH_CREDIT_REVERSAL'
  | 'SHOP_CASH_REFUND_DEBIT'
  | 'SHOP_CASH_REFUND_DEBIT_REVERSAL'
  | 'SHOPIFY_COLLECTIVE_CREDIT'
  | 'SHOPIFY_COLLECTIVE_CREDIT_REVERSAL'
  | 'SHOPIFY_COLLECTIVE_DEBIT'
  | 'SHOPIFY_COLLECTIVE_DEBIT_REVERSAL'
  | 'SHOPIFY_SOURCE_CREDIT'
  | 'SHOPIFY_SOURCE_CREDIT_REVERSAL'
  | 'SHOPIFY_SOURCE_DEBIT'
  | 'SHOPIFY_SOURCE_DEBIT_REVERSAL'
  | 'STRIPE_FEE'
  | 'TAX_ADJUSTMENT_CREDIT'
  | 'TAX_ADJUSTMENT_CREDIT_REVERSAL'
  | 'TAX_ADJUSTMENT_DEBIT'
  | 'TAX_ADJUSTMENT_DEBIT_REVERSAL'
  | 'TRANSFER'
  | 'TRANSFER_CANCEL'
  | 'TRANSFER_FAILURE'
  | 'TRANSFER_REFUND'
  | 'VAT_REFUND_CREDIT'
  | 'VAT_REFUND_CREDIT_REVERSAL';

/** The status of an order's eligibility for protection against fraudulent chargebacks by Shopify Protect. */
export type ShopifyProtectEligibilityStatus =
  | 'ELIGIBLE'
  | 'NOT_ELIGIBLE'
  | 'PENDING';

/** The status of an order's protection with Shopify Protect. */
export type ShopifyProtectStatus =
  | 'ACTIVE'
  | 'INACTIVE'
  | 'NOT_PROTECTED'
  | 'PENDING'
  | 'PROTECTED';

/** Represents the delivery method type for a Shop Pay payment request. */
export type ShopPayPaymentRequestDeliveryMethodType =
  | 'PICKUP'
  | 'SHIPPING';

/** A standardized error code, independent of the payment provider. */
export type ShopPayPaymentRequestReceiptProcessingStatusErrorCode =
  | 'AMOUNT_TOO_SMALL'
  | 'CALL_ISSUER'
  | 'CARD_DECLINED'
  | 'CONFIG_ERROR'
  | 'CVV_ATTEMPTS_EXCEEDED'
  | 'EXPIRED_CARD'
  | 'FRAUD_SUSPECTED'
  | 'GENERIC_ERROR'
  | 'INCORRECT_ADDRESS'
  | 'INCORRECT_CVC'
  | 'INCORRECT_NUMBER'
  | 'INCORRECT_PIN'
  | 'INCORRECT_ZIP'
  | 'INVALID_AMOUNT'
  | 'INVALID_COUNTRY'
  | 'INVALID_CVC'
  | 'INVALID_EXPIRY_DATE'
  | 'INVALID_NUMBER'
  | 'PAYMENT_METHOD_UNAVAILABLE'
  | 'PICK_UP_CARD'
  | 'PROCESSING_ERROR'
  | 'TEST_MODE_LIVE_CARD'
  | 'THREE_D_SECURE_FAILED'
  | 'UNSUPPORTED_FEATURE';

/** The state of the payment request receipt. */
export type ShopPayPaymentRequestReceiptProcessingStatusState =
  | 'ACTION_REQUIRED'
  | 'COMPLETED'
  | 'FAILED'
  | 'PROCESSING'
  | 'READY';

/** The set of valid sort keys for the ShopPayPaymentRequestReceipts query. */
export type ShopPayPaymentRequestReceiptsSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** Possible error codes that can be returned by `ShopPolicyUserError`. */
export type ShopPolicyErrorCode =
  | 'TOO_BIG';

/** Available shop policy types. */
export type ShopPolicyType =
  | 'CONTACT_INFORMATION'
  | 'LEGAL_NOTICE'
  | 'PRIVACY_POLICY'
  | 'REFUND_POLICY'
  | 'SHIPPING_POLICY'
  | 'SUBSCRIPTION_POLICY'
  | 'TERMS_OF_SALE'
  | 'TERMS_OF_SERVICE';

/** Possible error codes that can be returned by `ShopResourceFeedbackCreateUserError`. */
export type ShopResourceFeedbackCreateUserErrorCode =
  | 'BLANK'
  | 'FEEDBACK_DATE_IN_FUTURE'
  | 'INVALID'
  | 'NOT_FOUND'
  | 'OUTDATED_FEEDBACK'
  | 'PRESENT';

/** Possible sort of tags. */
export type ShopTagSort =
  | 'ALPHABETICAL'
  | 'POPULAR';

/** Represents the fallback avatar image for a staff member. This is used only if the staff member has no avatar image. */
export type StaffMemberDefaultImage =
  | 'DEFAULT'
  | 'NOT_FOUND'
  | 'TRANSPARENT';

/** Represents access permissions for a staff member. */
export type StaffMemberPermission =
  | 'APPLICATIONS'
  | 'CHANNELS'
  | 'CREATE_AND_EDIT_CUSTOMERS'
  | 'CREATE_AND_EDIT_GIFT_CARDS'
  | 'CREATE_AND_EDIT_MARKETS'
  | 'CUSTOMERS'
  | 'DASHBOARD'
  | 'DEACTIVATE_GIFT_CARDS'
  | 'DELETE_CUSTOMERS'
  | 'DELETE_MARKETS'
  | 'DOMAINS'
  | 'DRAFT_ORDERS'
  | 'EDIT_ORDERS'
  | 'ERASE_CUSTOMER_DATA'
  | 'EXPORT_CUSTOMERS'
  | 'EXPORT_GIFT_CARDS'
  | 'GIFT_CARDS'
  | 'LINKS'
  | 'LOCATIONS'
  | 'MARKETING'
  | 'MARKETING_SECTION'
  | 'MERGE_CUSTOMERS'
  | 'ORDERS'
  | 'OVERVIEWS'
  | 'PAGES'
  | 'PAY_ORDERS_BY_VAULTED_CARD'
  | 'PREFERENCES'
  | 'PRODUCTS'
  | 'REPORTS'
  | 'REQUEST_CUSTOMER_DATA'
  | 'THEMES'
  | 'VIEW_MARKETS'
  | 'FULL'
  | 'TRANSLATIONS';

/** The set of valid sort keys for the StaffMembers query. */
export type StaffMembersSortKeys =
  | 'EMAIL'
  | 'FIRST_NAME'
  | 'ID'
  | 'LAST_NAME';

/** The possible HTTP methods that can be used when sending a request to upload a file using information from a [StagedMediaUploadTarget](https://shopify.dev/api/admin-graphql/latest/objects/StagedMediaUploadTarget). */
export type StagedUploadHttpMethodType =
  | 'POST'
  | 'PUT';

/** The resource type to receive. */
export type StagedUploadTargetGenerateUploadResource =
  | 'BULK_MUTATION_VARIABLES'
  | 'COLLECTION_IMAGE'
  | 'DISPUTE_FILE_UPLOAD'
  | 'FILE'
  | 'IMAGE'
  | 'MODEL_3D'
  | 'RETURN_LABEL'
  | 'SHOP_IMAGE'
  | 'URL_REDIRECT_IMPORT'
  | 'VIDEO'
  | 'PRODUCT_IMAGE';

/** Possible error codes that can be returned by `StandardMetafieldDefinitionEnableUserError`. */
export type StandardMetafieldDefinitionEnableUserErrorCode =
  | 'ADMIN_ACCESS_INPUT_NOT_ALLOWED'
  | 'CAPABILITY_CANNOT_BE_DISABLED'
  | 'INVALID'
  | 'INVALID_CAPABILITY'
  | 'INVALID_INPUT_COMBINATION'
  | 'LIMIT_EXCEEDED'
  | 'OWNER_TYPE_LIMIT_EXCEEDED_FOR_USE_AS_ADMIN_FILTERS'
  | 'TAKEN'
  | 'TEMPLATE_NOT_FOUND'
  | 'TYPE_NOT_ALLOWED_FOR_CONDITIONS'
  | 'UNSTRUCTURED_ALREADY_EXISTS'
  | 'UNSUPPORTED_PINNING';

/** Possible error codes that can be returned by `StoreCreditAccountCreditUserError`. */
export type StoreCreditAccountCreditUserErrorCode =
  | 'ACCOUNT_NOT_FOUND'
  | 'CREDIT_LIMIT_EXCEEDED'
  | 'EXPIRES_AT_IN_PAST'
  | 'MISMATCHING_CURRENCY'
  | 'NEGATIVE_OR_ZERO_AMOUNT'
  | 'OWNER_NOT_FOUND'
  | 'UNSUPPORTED_CURRENCY';

/** Possible error codes that can be returned by `StoreCreditAccountDebitUserError`. */
export type StoreCreditAccountDebitUserErrorCode =
  | 'ACCOUNT_NOT_FOUND'
  | 'INSUFFICIENT_FUNDS'
  | 'MISMATCHING_CURRENCY'
  | 'NEGATIVE_OR_ZERO_AMOUNT';

/** The event that caused the store credit account transaction. */
export type StoreCreditSystemEvent =
  | 'ADJUSTMENT'
  | 'ORDER_CANCELLATION'
  | 'ORDER_PAYMENT'
  | 'ORDER_REFUND'
  | 'PAYMENT_FAILURE'
  | 'PAYMENT_RETURNED'
  | 'TAX_FINALIZATION';

/** The possible error codes associated with making billing attempts. The error codes supplement the `error_message` to provide consistent results and help with dunning management. */
export type SubscriptionBillingAttemptErrorCode =
  | 'AMOUNT_TOO_LARGE'
  | 'AMOUNT_TOO_SMALL'
  | 'AUTHENTICATION_ERROR'
  | 'AUTHENTICATION_FAILED'
  | 'AUTHENTICATION_REQUIRED'
  | 'BUYER_CANCELED_PAYMENT_METHOD'
  | 'CALL_ISSUER'
  | 'CANCELLED_PAYMENT'
  | 'CARD_DECLINED'
  | 'CARD_NUMBER_INCORRECT'
  | 'CONFIRMATION_REJECTED'
  | 'CUSTOMER_INVALID'
  | 'CUSTOMER_NOT_FOUND'
  | 'DO_NOT_HONOR'
  | 'EXPIRED_BUYER_ACTION'
  | 'EXPIRED_CARD'
  | 'EXPIRED_PAYMENT_METHOD'
  | 'FRAUD_SUSPECTED'
  | 'FREE_GIFT_CARD_NOT_ALLOWED'
  | 'GENERIC_ERROR'
  | 'INCORRECT_ADDRESS'
  | 'INCORRECT_NUMBER'
  | 'INCORRECT_ZIP'
  | 'INSUFFICIENT_FUNDS'
  | 'INSUFFICIENT_INVENTORY'
  | 'INVALID_BILLING_ADDRESS'
  | 'INVALID_CURRENCY'
  | 'INVALID_CUSTOMER_BILLING_AGREEMENT'
  | 'INVALID_EXPIRY_DATE'
  | 'INVALID_NUMBER'
  | 'INVALID_PAYMENT_METHOD'
  | 'INVALID_PURCHASE_TYPE'
  | 'INVALID_SHIPPING_ADDRESS'
  | 'INVENTORY_ALLOCATIONS_NOT_FOUND'
  | 'INVOICE_ALREADY_PAID'
  | 'MERCHANT_ACCOUNT_ERROR'
  | 'MERCHANT_RULE'
  | 'NON_TEST_ORDER_LIMIT_REACHED'
  | 'OFF_SESSION_REJECTED'
  | 'PAYMENT_METHOD_DECLINED'
  | 'PAYMENT_METHOD_INCOMPATIBLE_WITH_GATEWAY_CONFIG'
  | 'PAYMENT_METHOD_NOT_FOUND'
  | 'PAYMENT_METHOD_NOT_SPECIFIED'
  | 'PAYMENT_METHOD_UNSUPPORTED'
  | 'PAYMENT_PROVIDER_ERROR'
  | 'PAYMENT_PROVIDER_IS_NOT_ENABLED'
  | 'PAYPAL_ERROR_GENERAL'
  | 'PROCESSING_ERROR'
  | 'PURCHASE_TYPE_NOT_SUPPORTED'
  | 'RETRY_DECLINED'
  | 'TEST_MODE'
  | 'TRANSACTION_LIMIT_EXCEEDED'
  | 'TRANSIENT_ERROR'
  | 'UNEXPECTED_ERROR';

/** Error codes for other billing attempt failures. */
export type SubscriptionBillingAttemptGeneralErrorCode =
  | 'CUSTOMER_INVALID'
  | 'CUSTOMER_NOT_FOUND'
  | 'FREE_GIFT_CARD_NOT_ALLOWED'
  | 'INVALID_BILLING_ADDRESS'
  | 'MERCHANT_ACCOUNT_ERROR'
  | 'NON_TEST_ORDER_LIMIT_REACHED'
  | 'PAYMENT_METHOD_INCOMPATIBLE_WITH_GATEWAY_CONFIG'
  | 'PAYMENT_METHOD_NOT_FOUND'
  | 'PAYMENT_METHOD_NOT_SPECIFIED'
  | 'PAYMENT_PROVIDER_IS_NOT_ENABLED';

/** Error codes for inventory-related billing attempt failures. */
export type SubscriptionBillingAttemptInventoryErrorCode =
  | 'INSUFFICIENT_INVENTORY'
  | 'INVENTORY_ALLOCATIONS_NOT_FOUND';

/** The inventory policy for a billing attempt. */
export type SubscriptionBillingAttemptInventoryPolicy =
  | 'ALLOW_OVERSELLING'
  | 'PRODUCT_VARIANT_INVENTORY_POLICY';

/** The status of the billing attempt authentication process. */
export type SubscriptionBillingAttemptPaymentChallengeStatus =
  | 'OFF_SESSION_REJECTED'
  | 'ON_SESSION_CHALLENGED';

/** Error codes for payment-related billing attempt failures. */
export type SubscriptionBillingAttemptPaymentErrorCode =
  | 'AMOUNT_TOO_LARGE'
  | 'AMOUNT_TOO_SMALL'
  | 'AUTHENTICATION_ERROR'
  | 'AUTHENTICATION_FAILED'
  | 'AUTHENTICATION_REQUIRED'
  | 'BUYER_CANCELED_PAYMENT_METHOD'
  | 'CALL_ISSUER'
  | 'CANCELLED_PAYMENT'
  | 'CARD_DECLINED'
  | 'CARD_NUMBER_INCORRECT'
  | 'CONFIRMATION_REJECTED'
  | 'DO_NOT_HONOR'
  | 'EXPIRED_BUYER_ACTION'
  | 'EXPIRED_CARD'
  | 'EXPIRED_PAYMENT_METHOD'
  | 'FRAUD_SUSPECTED'
  | 'GENERIC_ERROR'
  | 'INCORRECT_ADDRESS'
  | 'INCORRECT_NUMBER'
  | 'INCORRECT_ZIP'
  | 'INSUFFICIENT_FUNDS'
  | 'INVALID_CURRENCY'
  | 'INVALID_CUSTOMER_BILLING_AGREEMENT'
  | 'INVALID_EXPIRY_DATE'
  | 'INVALID_NUMBER'
  | 'INVALID_PAYMENT_METHOD'
  | 'INVALID_PURCHASE_TYPE'
  | 'INVALID_SHIPPING_ADDRESS'
  | 'INVOICE_ALREADY_PAID'
  | 'MERCHANT_RULE'
  | 'OFF_SESSION_REJECTED'
  | 'PAYMENT_METHOD_DECLINED'
  | 'PAYMENT_METHOD_UNSUPPORTED'
  | 'PAYMENT_PROVIDER_ERROR'
  | 'PAYPAL_ERROR_GENERAL'
  | 'PROCESSING_ERROR'
  | 'PURCHASE_TYPE_NOT_SUPPORTED'
  | 'RETRY_DECLINED'
  | 'TEST_MODE'
  | 'TRANSACTION_LIMIT_EXCEEDED'
  | 'TRANSIENT_ERROR';

/** The payment processing policy for a billing attempt. */
export type SubscriptionBillingAttemptPaymentProcessingPolicy =
  | 'FAIL_UNLESS_VALID_PAYMENT_METHOD'
  | 'SKIP_PAYMENT_AND_CREATE_UNPAID_ORDER';

/** The set of valid sort keys for the SubscriptionBillingAttempts query. */
export type SubscriptionBillingAttemptsSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** The presence of billing attempts on Billing Cycles. */
export type SubscriptionBillingCycleBillingAttemptStatus =
  | 'ANY'
  | 'HAS_ATTEMPT'
  | 'NO_ATTEMPT';

/** The possible status values of a subscription billing cycle. */
export type SubscriptionBillingCycleBillingCycleStatus =
  | 'BILLED'
  | 'UNBILLED';

/** Possible error codes that can be returned by `SubscriptionBillingCycleBulkUserError`. */
export type SubscriptionBillingCycleBulkUserErrorCode =
  | 'BLANK'
  | 'END_DATE_IN_THE_FUTURE'
  | 'INVALID'
  | 'INVALID_DATE_RANGE'
  | 'START_DATE_BEFORE_END_DATE';

/** Possible error codes that can be returned by `SubscriptionBillingCycleUserError`. */
export type SubscriptionBillingCycleErrorCode =
  | 'BILLING_DATE_SET_ON_SKIPPED'
  | 'CYCLE_INDEX_OUT_OF_RANGE'
  | 'CYCLE_NOT_FOUND'
  | 'CYCLE_START_DATE_OUT_OF_RANGE'
  | 'EMPTY_BILLING_CYCLE_EDIT_SCHEDULE_INPUT'
  | 'INCOMPLETE_BILLING_ATTEMPTS'
  | 'INVALID'
  | 'INVALID_CYCLE_INDEX'
  | 'INVALID_DATE'
  | 'NO_CYCLE_EDITS'
  | 'OUT_OF_BOUNDS'
  | 'UPCOMING_CYCLE_LIMIT_EXCEEDED';

/** The input fields for possible reasons for editing the billing cycle's schedule. */
export type SubscriptionBillingCycleScheduleEditInputScheduleEditReason =
  | 'BUYER_INITIATED'
  | 'DEV_INITIATED'
  | 'MERCHANT_INITIATED';

/** Possible error codes that can be returned by `SubscriptionBillingCycleSkipUserError`. */
export type SubscriptionBillingCycleSkipUserErrorCode =
  | 'INVALID';

/** The set of valid sort keys for the SubscriptionBillingCycles query. */
export type SubscriptionBillingCyclesSortKeys =
  | 'CYCLE_INDEX'
  | 'ID';

/** Select subscription billing cycles to be targeted. */
export type SubscriptionBillingCyclesTargetSelection =
  | 'ALL';

/** Possible error codes that can be returned by `SubscriptionBillingCycleUnskipUserError`. */
export type SubscriptionBillingCycleUnskipUserErrorCode =
  | 'INVALID';

/** Possible error codes that can be returned by `SubscriptionContractUserError`. */
export type SubscriptionContractErrorCode =
  | 'INVALID';

/** The possible values of the last billing error on a subscription contract. */
export type SubscriptionContractLastBillingErrorType =
  | 'CUSTOMER_ERROR'
  | 'INVENTORY_ERROR'
  | 'OTHER'
  | 'PAYMENT_ERROR';

/** The possible status values of the last payment on a subscription contract. */
export type SubscriptionContractLastPaymentStatus =
  | 'FAILED'
  | 'SUCCEEDED';

/** The set of valid sort keys for the SubscriptionContracts query. */
export type SubscriptionContractsSortKeys =
  | 'CREATED_AT'
  | 'ID'
  | 'STATUS'
  | 'UPDATED_AT';

/** Possible error codes that can be returned by `SubscriptionContractStatusUpdateUserError`. */
export type SubscriptionContractStatusUpdateErrorCode =
  | 'CONTRACT_TERMINATED'
  | 'INVALID';

/** The possible status values of a subscription. */
export type SubscriptionContractSubscriptionStatus =
  | 'ACTIVE'
  | 'CANCELLED'
  | 'EXPIRED'
  | 'FAILED'
  | 'PAUSED';

/** The reason a discount on a subscription draft was rejected. */
export type SubscriptionDiscountRejectionReason =
  | 'CURRENTLY_INACTIVE'
  | 'CUSTOMER_NOT_ELIGIBLE'
  | 'CUSTOMER_USAGE_LIMIT_REACHED'
  | 'INCOMPATIBLE_PURCHASE_TYPE'
  | 'INTERNAL_ERROR'
  | 'NO_ENTITLED_LINE_ITEMS'
  | 'NO_ENTITLED_SHIPPING_LINES'
  | 'NOT_FOUND'
  | 'PURCHASE_NOT_IN_RANGE'
  | 'QUANTITY_NOT_IN_RANGE'
  | 'USAGE_LIMIT_REACHED';

/** Possible error codes that can be returned by `SubscriptionDraftUserError`. */
export type SubscriptionDraftErrorCode =
  | 'ALREADY_REMOVED'
  | 'BILLING_CYCLE_ABSENT'
  | 'BILLING_CYCLE_CONTRACT_DRAFT_BILLING_POLICY_INVALID'
  | 'BILLING_CYCLE_CONTRACT_DRAFT_DELIVERY_POLICY_INVALID'
  | 'BILLING_CYCLE_PRESENT'
  | 'BLANK'
  | 'COMMITTED'
  | 'CONCATENATION_BILLING_CYCLE_CONTRACT_DRAFT_REQUIRED'
  | 'CONCATENATION_UNCOMMITTED_CONTRACT_DRAFT'
  | 'CURRENCY_NOT_ENABLED'
  | 'CUSTOMER_DOES_NOT_EXIST'
  | 'CUSTOMER_MISMATCH'
  | 'CUSTOMER_REDACTED'
  | 'CYCLE_DISCOUNTS_UNIQUE_AFTER_CYCLE'
  | 'CYCLE_INDEX_OUT_OF_RANGE'
  | 'CYCLE_SELECTOR_VALIDATE_ONE_OF'
  | 'CYCLE_START_DATE_OUT_OF_RANGE'
  | 'DELIVERY_METHOD_REQUIRED'
  | 'DELIVERY_MUST_BE_MULTIPLE_OF_BILLING'
  | 'DUPLICATE_CONCATENATED_CONTRACTS'
  | 'EXCEEDED_MAX_CONCATENATED_CONTRACTS'
  | 'GREATER_THAN'
  | 'GREATER_THAN_OR_EQUAL_TO'
  | 'HAS_FUTURE_EDITS'
  | 'INVALID'
  | 'INVALID_ADJUSTMENT_TYPE'
  | 'INVALID_ADJUSTMENT_VALUE'
  | 'INVALID_BILLING_DATE'
  | 'INVALID_LINES'
  | 'INVALID_NOTE_LENGTH'
  | 'LESS_THAN'
  | 'LESS_THAN_OR_EQUAL_TO'
  | 'MISSING_CUSTOMER_PAYMENT_METHOD'
  | 'MISSING_LOCAL_DELIVERY_OPTIONS'
  | 'NO_ENTITLED_LINES'
  | 'NOT_AN_INTEGER'
  | 'NOT_IN_RANGE'
  | 'PRESENCE'
  | 'SELLING_PLAN_MAX_CYCLES_MUST_BE_GREATER_THAN_MIN_CYCLES'
  | 'STALE_CONTRACT'
  | 'TOO_LONG'
  | 'TOO_MANY_DISCOUNTS'
  | 'TOO_MANY_LINES'
  | 'TOO_SHORT'
  | 'UPCOMING_CYCLE_LIMIT_EXCEEDED';

/** Specifies the kind of the suggested order transaction. */
export type SuggestedOrderTransactionKind =
  | 'SUGGESTED_REFUND';

/** Possible error codes that can be returned by `TaxAppConfigureUserError`. */
export type TaxAppConfigureUserErrorCode =
  | 'TAX_PARTNER_ALREADY_ACTIVE'
  | 'TAX_PARTNER_NOT_FOUND'
  | 'TAX_PARTNER_STATE_UPDATE_FAILED';

/** Available customer tax exemptions. */
export type TaxExemption =
  | 'CA_BC_COMMERCIAL_FISHERY_EXEMPTION'
  | 'CA_BC_CONTRACTOR_EXEMPTION'
  | 'CA_BC_PRODUCTION_AND_MACHINERY_EXEMPTION'
  | 'CA_BC_RESELLER_EXEMPTION'
  | 'CA_BC_SUB_CONTRACTOR_EXEMPTION'
  | 'CA_DIPLOMAT_EXEMPTION'
  | 'CA_MB_COMMERCIAL_FISHERY_EXEMPTION'
  | 'CA_MB_FARMER_EXEMPTION'
  | 'CA_MB_RESELLER_EXEMPTION'
  | 'CA_NS_COMMERCIAL_FISHERY_EXEMPTION'
  | 'CA_NS_FARMER_EXEMPTION'
  | 'CA_ON_PURCHASE_EXEMPTION'
  | 'CA_PE_COMMERCIAL_FISHERY_EXEMPTION'
  | 'CA_SK_COMMERCIAL_FISHERY_EXEMPTION'
  | 'CA_SK_CONTRACTOR_EXEMPTION'
  | 'CA_SK_FARMER_EXEMPTION'
  | 'CA_SK_PRODUCTION_AND_MACHINERY_EXEMPTION'
  | 'CA_SK_RESELLER_EXEMPTION'
  | 'CA_SK_SUB_CONTRACTOR_EXEMPTION'
  | 'CA_STATUS_CARD_EXEMPTION'
  | 'EU_REVERSE_CHARGE_EXEMPTION_RULE'
  | 'US_AK_RESELLER_EXEMPTION'
  | 'US_AL_RESELLER_EXEMPTION'
  | 'US_AR_RESELLER_EXEMPTION'
  | 'US_AZ_RESELLER_EXEMPTION'
  | 'US_CA_RESELLER_EXEMPTION'
  | 'US_CO_RESELLER_EXEMPTION'
  | 'US_CT_RESELLER_EXEMPTION'
  | 'US_DC_RESELLER_EXEMPTION'
  | 'US_DE_RESELLER_EXEMPTION'
  | 'US_FL_RESELLER_EXEMPTION'
  | 'US_GA_RESELLER_EXEMPTION'
  | 'US_HI_RESELLER_EXEMPTION'
  | 'US_IA_RESELLER_EXEMPTION'
  | 'US_ID_RESELLER_EXEMPTION'
  | 'US_IL_RESELLER_EXEMPTION'
  | 'US_IN_RESELLER_EXEMPTION'
  | 'US_KS_RESELLER_EXEMPTION'
  | 'US_KY_RESELLER_EXEMPTION'
  | 'US_LA_RESELLER_EXEMPTION'
  | 'US_MA_RESELLER_EXEMPTION'
  | 'US_MD_RESELLER_EXEMPTION'
  | 'US_ME_RESELLER_EXEMPTION'
  | 'US_MI_RESELLER_EXEMPTION'
  | 'US_MN_RESELLER_EXEMPTION'
  | 'US_MO_RESELLER_EXEMPTION'
  | 'US_MS_RESELLER_EXEMPTION'
  | 'US_MT_RESELLER_EXEMPTION'
  | 'US_NC_RESELLER_EXEMPTION'
  | 'US_ND_RESELLER_EXEMPTION'
  | 'US_NE_RESELLER_EXEMPTION'
  | 'US_NH_RESELLER_EXEMPTION'
  | 'US_NJ_RESELLER_EXEMPTION'
  | 'US_NM_RESELLER_EXEMPTION'
  | 'US_NV_RESELLER_EXEMPTION'
  | 'US_NY_RESELLER_EXEMPTION'
  | 'US_OH_RESELLER_EXEMPTION'
  | 'US_OK_RESELLER_EXEMPTION'
  | 'US_OR_RESELLER_EXEMPTION'
  | 'US_PA_RESELLER_EXEMPTION'
  | 'US_RI_RESELLER_EXEMPTION'
  | 'US_SC_RESELLER_EXEMPTION'
  | 'US_SD_RESELLER_EXEMPTION'
  | 'US_TN_RESELLER_EXEMPTION'
  | 'US_TX_RESELLER_EXEMPTION'
  | 'US_UT_RESELLER_EXEMPTION'
  | 'US_VA_RESELLER_EXEMPTION'
  | 'US_VT_RESELLER_EXEMPTION'
  | 'US_WA_RESELLER_EXEMPTION'
  | 'US_WI_RESELLER_EXEMPTION'
  | 'US_WV_RESELLER_EXEMPTION'
  | 'US_WY_RESELLER_EXEMPTION';

/** State of the tax app configuration. */
export type TaxPartnerState =
  | 'ACTIVE'
  | 'PENDING'
  | 'READY';

/** Possible error codes that can be returned by `TaxSummaryCreateUserError`. */
export type TaxSummaryCreateUserErrorCode =
  | 'GENERAL_ERROR'
  | 'ORDER_NOT_FOUND';

/** Possible error codes that can be returned by `ThemeCreateUserError`. */
export type ThemeCreateUserErrorCode =
  | 'INVALID_THEME_ROLE_FOR_THEME_CREATION'
  | 'INVALID_ZIP'
  | 'THEME_CREATION_NOT_ALLOWED_FOR_THEME_LIMITED_PLAN'
  | 'ZIP_IS_EMPTY'
  | 'ZIP_TOO_LARGE';

/** Possible error codes that can be returned by `ThemeDeleteUserError`. */
export type ThemeDeleteUserErrorCode =
  | 'NOT_FOUND';

/** Possible error codes that can be returned by `ThemeDuplicateUserError`. */
export type ThemeDuplicateUserErrorCode =
  | 'NOT_FOUND';

/** Possible error codes that can be returned by `ThemePublishUserError`. */
export type ThemePublishUserErrorCode =
  | 'CANNOT_PUBLISH_THEME_DURING_INSTALL'
  | 'NOT_FOUND'
  | 'THEME_PUBLISH_NOT_AVAILABLE_FOR_THEME_LIMITED_PLAN';

/** The role of the theme. */
export type ThemeRole =
  | 'ARCHIVED'
  | 'DEMO'
  | 'DEVELOPMENT'
  | 'LOCKED'
  | 'MAIN'
  | 'UNPUBLISHED'
  | 'MOBILE';

/** Possible error codes that can be returned by `ThemeUpdateUserError`. */
export type ThemeUpdateUserErrorCode =
  | 'INVALID'
  | 'NOT_FOUND'
  | 'TOO_LONG';

/** The set of valid sort keys for the Transaction query. */
export type TransactionSortKeys =
  | 'CREATED_AT'
  | 'EXPIRES_AT';

/** Possible error codes that can be returned by `TransactionVoidUserError`. */
export type TransactionVoidUserErrorCode =
  | 'AUTH_NOT_SUCCESSFUL'
  | 'AUTH_NOT_VOIDABLE'
  | 'GENERIC_ERROR'
  | 'TRANSACTION_NOT_FOUND';

/** The set of valid sort keys for the Transfer query. */
export type TransferSortKeys =
  | 'CREATED_AT'
  | 'DESTINATION_NAME'
  | 'EXPECTED_SHIPMENT_ARRIVAL'
  | 'ID'
  | 'NAME'
  | 'ORIGIN_NAME'
  | 'SOURCE_NAME'
  | 'STATUS';

/** Specifies the type of resources that are translatable. */
export type TranslatableResourceType =
  | 'ARTICLE'
  | 'ARTICLE_IMAGE'
  | 'BLOG'
  | 'COLLECTION'
  | 'COLLECTION_IMAGE'
  | 'DELIVERY_METHOD_DEFINITION'
  | 'EMAIL_TEMPLATE'
  | 'FILTER'
  | 'LINK'
  | 'MEDIA_IMAGE'
  | 'MENU'
  | 'METAFIELD'
  | 'METAOBJECT'
  | 'ONLINE_STORE_THEME'
  | 'ONLINE_STORE_THEME_APP_EMBED'
  | 'ONLINE_STORE_THEME_JSON_TEMPLATE'
  | 'ONLINE_STORE_THEME_LOCALE_CONTENT'
  | 'ONLINE_STORE_THEME_SECTION_GROUP'
  | 'ONLINE_STORE_THEME_SETTINGS_CATEGORY'
  | 'ONLINE_STORE_THEME_SETTINGS_DATA_SECTIONS'
  | 'PACKING_SLIP_TEMPLATE'
  | 'PAGE'
  | 'PAYMENT_GATEWAY'
  | 'PRODUCT'
  | 'PRODUCT_OPTION'
  | 'PRODUCT_OPTION_VALUE'
  | 'SELLING_PLAN'
  | 'SELLING_PLAN_GROUP'
  | 'SHOP'
  | 'SHOP_POLICY';

/** Possible error codes that can be returned by `TranslationUserError`. */
export type TranslationErrorCode =
  | 'BLANK'
  | 'FAILS_RESOURCE_VALIDATION'
  | 'INVALID'
  | 'INVALID_CODE'
  | 'INVALID_FORMAT'
  | 'INVALID_KEY_FOR_MODEL'
  | 'INVALID_LOCALE_FOR_SHOP'
  | 'INVALID_MARKET_LOCALIZABLE_CONTENT'
  | 'INVALID_TRANSLATABLE_CONTENT'
  | 'INVALID_VALUE_FOR_HANDLE_TRANSLATION'
  | 'MARKET_CUSTOM_CONTENT_NOT_ALLOWED'
  | 'MARKET_DOES_NOT_EXIST'
  | 'MARKET_LOCALE_CREATION_FAILED'
  | 'RESOURCE_NOT_FOUND'
  | 'RESOURCE_NOT_MARKET_CUSTOMIZABLE'
  | 'RESOURCE_NOT_TRANSLATABLE'
  | 'TOO_MANY_KEYS_FOR_RESOURCE'
  | 'INVALID_LOCALE_FOR_MARKET';

/** The accepted types of unit of measurement. */
export type UnitPriceMeasurementMeasuredType =
  | 'AREA'
  | 'COUNT'
  | 'LENGTH'
  | 'UNKNOWN'
  | 'VOLUME'
  | 'WEIGHT';

/** The valid units of measurement for a unit price measurement. */
export type UnitPriceMeasurementMeasuredUnit =
  | 'CL'
  | 'CM'
  | 'FLOZ'
  | 'FT'
  | 'FT2'
  | 'G'
  | 'GAL'
  | 'IN'
  | 'ITEM'
  | 'KG'
  | 'L'
  | 'LB'
  | 'M'
  | 'M2'
  | 'M3'
  | 'MG'
  | 'ML'
  | 'MM'
  | 'OZ'
  | 'PT'
  | 'QT'
  | 'UNKNOWN'
  | 'YD';

/** Systems of weights and measures. */
export type UnitSystem =
  | 'IMPERIAL_SYSTEM'
  | 'METRIC_SYSTEM';

/** Possible error codes that can be returned by `UrlRedirectBulkDeleteByIdsUserError`. */
export type UrlRedirectBulkDeleteByIdsUserErrorCode =
  | 'IDS_EMPTY';

/** Possible error codes that can be returned by `UrlRedirectBulkDeleteBySavedSearchUserError`. */
export type UrlRedirectBulkDeleteBySavedSearchUserErrorCode =
  | 'INVALID_SAVED_SEARCH_QUERY'
  | 'SAVED_SEARCH_NOT_FOUND';

/** Possible error codes that can be returned by `UrlRedirectBulkDeleteBySearchUserError`. */
export type UrlRedirectBulkDeleteBySearchUserErrorCode =
  | 'INVALID_SEARCH_ARGUMENT';

/** Possible error codes that can be returned by `UrlRedirectUserError`. */
export type UrlRedirectErrorCode =
  | 'CREATE_FAILED'
  | 'DELETE_FAILED'
  | 'DOES_NOT_EXIST'
  | 'UPDATE_FAILED';

/** Possible error codes that can be returned by `UrlRedirectImportUserError`. */
export type UrlRedirectImportErrorCode =
  | 'ALREADY_IMPORTED'
  | 'IN_PROGRESS'
  | 'NOT_FOUND'
  | 'FILE_DOES_NOT_EXIST';

/** The set of valid sort keys for the UrlRedirect query. */
export type UrlRedirectSortKeys =
  | 'ID'
  | 'PATH'
  | 'RELEVANCE';

/** The set of valid sort keys for the Validation query. */
export type ValidationSortKeys =
  | 'ID';

/** Possible error codes that can be returned by `ValidationUserError`. */
export type ValidationUserErrorCode =
  | 'APP_NOT_AUTHORIZED'
  | 'BLANK'
  | 'CAPABILITY_VIOLATION'
  | 'CUSTOM_APP_FUNCTION_NOT_ELIGIBLE'
  | 'DISALLOWED_OWNER_TYPE'
  | 'FUNCTION_DOES_NOT_IMPLEMENT'
  | 'FUNCTION_NOT_FOUND'
  | 'FUNCTION_PENDING_DELETION'
  | 'INCLUSION'
  | 'INTERNAL_ERROR'
  | 'INVALID'
  | 'INVALID_TYPE'
  | 'INVALID_VALUE'
  | 'MAX_VALIDATIONS_ACTIVATED'
  | 'MISSING_FUNCTION_IDENTIFIER'
  | 'MULTIPLE_FUNCTION_IDENTIFIERS'
  | 'NOT_FOUND'
  | 'PRESENT'
  | 'PUBLIC_APP_NOT_ALLOWED'
  | 'TAKEN'
  | 'TOO_LONG'
  | 'TOO_SHORT'
  | 'UNSTRUCTURED_RESERVED_NAMESPACE';

/** The supported formats for webhook subscriptions. */
export type WebhookSubscriptionFormat =
  | 'JSON'
  | 'XML';

/** The set of valid sort keys for the WebhookSubscription query. */
export type WebhookSubscriptionSortKeys =
  | 'CREATED_AT'
  | 'ID';

/** The supported topics for webhook subscriptions. You can use webhook subscriptions to receive notifications about particular events in a shop. */
export type WebhookSubscriptionTopic =
  | 'APP_PURCHASES_ONE_TIME_UPDATE'
  | 'APP_SCOPES_UPDATE'
  | 'APP_SUBSCRIPTIONS_APPROACHING_CAPPED_AMOUNT'
  | 'APP_SUBSCRIPTIONS_UPDATE'
  | 'APP_UNINSTALLED'
  | 'AUDIT_EVENTS_ADMIN_API_ACTIVITY'
  | 'BULK_OPERATIONS_FINISH'
  | 'CARTS_CREATE'
  | 'CARTS_UPDATE'
  | 'CHANNELS_DELETE'
  | 'CHECKOUTS_CREATE'
  | 'CHECKOUTS_DELETE'
  | 'CHECKOUTS_UPDATE'
  | 'COLLECTION_LISTINGS_ADD'
  | 'COLLECTION_LISTINGS_REMOVE'
  | 'COLLECTION_LISTINGS_UPDATE'
  | 'COLLECTION_PUBLICATIONS_CREATE'
  | 'COLLECTION_PUBLICATIONS_DELETE'
  | 'COLLECTION_PUBLICATIONS_UPDATE'
  | 'COLLECTIONS_CREATE'
  | 'COLLECTIONS_DELETE'
  | 'COLLECTIONS_UPDATE'
  | 'COMPANIES_CREATE'
  | 'COMPANIES_DELETE'
  | 'COMPANIES_UPDATE'
  | 'COMPANY_CONTACT_ROLES_ASSIGN'
  | 'COMPANY_CONTACT_ROLES_REVOKE'
  | 'COMPANY_CONTACTS_CREATE'
  | 'COMPANY_CONTACTS_DELETE'
  | 'COMPANY_CONTACTS_UPDATE'
  | 'COMPANY_LOCATIONS_CREATE'
  | 'COMPANY_LOCATIONS_DELETE'
  | 'COMPANY_LOCATIONS_UPDATE'
  | 'CUSTOMER_ACCOUNT_SETTINGS_UPDATE'
  | 'CUSTOMER_GROUPS_CREATE'
  | 'CUSTOMER_GROUPS_DELETE'
  | 'CUSTOMER_GROUPS_UPDATE'
  | 'CUSTOMER_JOINED_SEGMENT'
  | 'CUSTOMER_LEFT_SEGMENT'
  | 'CUSTOMER_PAYMENT_METHODS_CREATE'
  | 'CUSTOMER_PAYMENT_METHODS_REVOKE'
  | 'CUSTOMER_PAYMENT_METHODS_UPDATE'
  | 'CUSTOMER_TAGS_ADDED'
  | 'CUSTOMER_TAGS_REMOVED'
  | 'CUSTOMERS_CREATE'
  | 'CUSTOMERS_DELETE'
  | 'CUSTOMERS_DISABLE'
  | 'CUSTOMERS_EMAIL_MARKETING_CONSENT_UPDATE'
  | 'CUSTOMERS_ENABLE'
  | 'CUSTOMERS_MARKETING_CONSENT_UPDATE'
  | 'CUSTOMERS_MERGE'
  | 'CUSTOMERS_PURCHASING_SUMMARY'
  | 'CUSTOMERS_UPDATE'
  | 'DELIVERY_PROMISE_SETTINGS_UPDATE'
  | 'DISCOUNTS_CREATE'
  | 'DISCOUNTS_DELETE'
  | 'DISCOUNTS_REDEEMCODE_ADDED'
  | 'DISCOUNTS_REDEEMCODE_REMOVED'
  | 'DISCOUNTS_UPDATE'
  | 'DISPUTES_CREATE'
  | 'DISPUTES_UPDATE'
  | 'DOMAINS_CREATE'
  | 'DOMAINS_DESTROY'
  | 'DOMAINS_UPDATE'
  | 'DRAFT_ORDERS_CREATE'
  | 'DRAFT_ORDERS_DELETE'
  | 'DRAFT_ORDERS_UPDATE'
  | 'FINANCE_APP_STAFF_MEMBER_DELETE'
  | 'FINANCE_APP_STAFF_MEMBER_GRANT'
  | 'FINANCE_APP_STAFF_MEMBER_REVOKE'
  | 'FINANCE_APP_STAFF_MEMBER_UPDATE'
  | 'FINANCE_KYC_INFORMATION_UPDATE'
  | 'FULFILLMENT_EVENTS_CREATE'
  | 'FULFILLMENT_EVENTS_DELETE'
  | 'FULFILLMENT_HOLDS_ADDED'
  | 'FULFILLMENT_HOLDS_RELEASED'
  | 'FULFILLMENT_ORDERS_CANCELLATION_REQUEST_ACCEPTED'
  | 'FULFILLMENT_ORDERS_CANCELLATION_REQUEST_REJECTED'
  | 'FULFILLMENT_ORDERS_CANCELLATION_REQUEST_SUBMITTED'
  | 'FULFILLMENT_ORDERS_CANCELLED'
  | 'FULFILLMENT_ORDERS_FULFILLMENT_REQUEST_ACCEPTED'
  | 'FULFILLMENT_ORDERS_FULFILLMENT_REQUEST_REJECTED'
  | 'FULFILLMENT_ORDERS_FULFILLMENT_REQUEST_SUBMITTED'
  | 'FULFILLMENT_ORDERS_FULFILLMENT_SERVICE_FAILED_TO_COMPLETE'
  | 'FULFILLMENT_ORDERS_HOLD_RELEASED'
  | 'FULFILLMENT_ORDERS_LINE_ITEMS_PREPARED_FOR_LOCAL_DELIVERY'
  | 'FULFILLMENT_ORDERS_LINE_ITEMS_PREPARED_FOR_PICKUP'
  | 'FULFILLMENT_ORDERS_MANUALLY_REPORTED_PROGRESS_STOPPED'
  | 'FULFILLMENT_ORDERS_MERGED'
  | 'FULFILLMENT_ORDERS_MOVED'
  | 'FULFILLMENT_ORDERS_ORDER_ROUTING_COMPLETE'
  | 'FULFILLMENT_ORDERS_PLACED_ON_HOLD'
  | 'FULFILLMENT_ORDERS_PROGRESS_REPORTED'
  | 'FULFILLMENT_ORDERS_RESCHEDULED'
  | 'FULFILLMENT_ORDERS_SCHEDULED_FULFILLMENT_ORDER_READY'
  | 'FULFILLMENT_ORDERS_SPLIT'
  | 'FULFILLMENTS_CREATE'
  | 'FULFILLMENTS_UPDATE'
  | 'INVENTORY_ITEMS_CREATE'
  | 'INVENTORY_ITEMS_DELETE'
  | 'INVENTORY_ITEMS_UPDATE'
  | 'INVENTORY_LEVELS_CONNECT'
  | 'INVENTORY_LEVELS_DISCONNECT'
  | 'INVENTORY_LEVELS_UPDATE'
  | 'INVENTORY_SHIPMENTS_ADD_ITEMS'
  | 'INVENTORY_SHIPMENTS_CREATE'
  | 'INVENTORY_SHIPMENTS_DELETE'
  | 'INVENTORY_SHIPMENTS_MARK_IN_TRANSIT'
  | 'INVENTORY_SHIPMENTS_RECEIVE_ITEMS'
  | 'INVENTORY_SHIPMENTS_REMOVE_ITEMS'
  | 'INVENTORY_SHIPMENTS_UPDATE_ITEM_QUANTITIES'
  | 'INVENTORY_SHIPMENTS_UPDATE_TRACKING'
  | 'INVENTORY_TRANSFERS_ADD_ITEMS'
  | 'INVENTORY_TRANSFERS_CANCEL'
  | 'INVENTORY_TRANSFERS_COMPLETE'
  | 'INVENTORY_TRANSFERS_READY_TO_SHIP'
  | 'INVENTORY_TRANSFERS_REMOVE_ITEMS'
  | 'INVENTORY_TRANSFERS_UPDATE_ITEM_QUANTITIES'
  | 'LOCALES_CREATE'
  | 'LOCALES_DESTROY'
  | 'LOCALES_UPDATE'
  | 'LOCATIONS_ACTIVATE'
  | 'LOCATIONS_CREATE'
  | 'LOCATIONS_DEACTIVATE'
  | 'LOCATIONS_DELETE'
  | 'LOCATIONS_UPDATE'
  | 'MARKETS_BACKUP_REGION_UPDATE'
  | 'MARKETS_CREATE'
  | 'MARKETS_DELETE'
  | 'MARKETS_UPDATE'
  | 'METAFIELD_DEFINITIONS_CREATE'
  | 'METAFIELD_DEFINITIONS_DELETE'
  | 'METAFIELD_DEFINITIONS_UPDATE'
  | 'METAOBJECTS_CREATE'
  | 'METAOBJECTS_DELETE'
  | 'METAOBJECTS_UPDATE'
  | 'ORDER_TRANSACTIONS_CREATE'
  | 'ORDERS_CANCELLED'
  | 'ORDERS_CREATE'
  | 'ORDERS_DELETE'
  | 'ORDERS_EDITED'
  | 'ORDERS_FULFILLED'
  | 'ORDERS_LINK_REQUESTED'
  | 'ORDERS_PAID'
  | 'ORDERS_PARTIALLY_FULFILLED'
  | 'ORDERS_RISK_ASSESSMENT_CHANGED'
  | 'ORDERS_SHOPIFY_PROTECT_ELIGIBILITY_CHANGED'
  | 'ORDERS_UPDATED'
  | 'PAYMENT_SCHEDULES_DUE'
  | 'PAYMENT_TERMS_CREATE'
  | 'PAYMENT_TERMS_DELETE'
  | 'PAYMENT_TERMS_UPDATE'
  | 'PRODUCT_FEEDS_CREATE'
  | 'PRODUCT_FEEDS_FULL_SYNC'
  | 'PRODUCT_FEEDS_FULL_SYNC_FINISH'
  | 'PRODUCT_FEEDS_INCREMENTAL_SYNC'
  | 'PRODUCT_FEEDS_UPDATE'
  | 'PRODUCT_LISTINGS_ADD'
  | 'PRODUCT_LISTINGS_REMOVE'
  | 'PRODUCT_LISTINGS_UPDATE'
  | 'PRODUCT_PUBLICATIONS_CREATE'
  | 'PRODUCT_PUBLICATIONS_DELETE'
  | 'PRODUCT_PUBLICATIONS_UPDATE'
  | 'PRODUCTS_CREATE'
  | 'PRODUCTS_DELETE'
  | 'PRODUCTS_UPDATE'
  | 'PROFILES_CREATE'
  | 'PROFILES_DELETE'
  | 'PROFILES_UPDATE'
  | 'REFUNDS_CREATE'
  | 'RETURNS_APPROVE'
  | 'RETURNS_CANCEL'
  | 'RETURNS_CLOSE'
  | 'RETURNS_DECLINE'
  | 'RETURNS_PROCESS'
  | 'RETURNS_REOPEN'
  | 'RETURNS_REQUEST'
  | 'RETURNS_UPDATE'
  | 'REVERSE_DELIVERIES_ATTACH_DELIVERABLE'
  | 'REVERSE_FULFILLMENT_ORDERS_DISPOSE'
  | 'SCHEDULED_PRODUCT_LISTINGS_ADD'
  | 'SCHEDULED_PRODUCT_LISTINGS_REMOVE'
  | 'SCHEDULED_PRODUCT_LISTINGS_UPDATE'
  | 'SEGMENTS_CREATE'
  | 'SEGMENTS_DELETE'
  | 'SEGMENTS_UPDATE'
  | 'SELLING_PLAN_GROUPS_CREATE'
  | 'SELLING_PLAN_GROUPS_DELETE'
  | 'SELLING_PLAN_GROUPS_UPDATE'
  | 'SHIPPING_ADDRESSES_CREATE'
  | 'SHIPPING_ADDRESSES_UPDATE'
  | 'SHOP_UPDATE'
  | 'SUBSCRIPTION_BILLING_ATTEMPTS_CHALLENGED'
  | 'SUBSCRIPTION_BILLING_ATTEMPTS_FAILURE'
  | 'SUBSCRIPTION_BILLING_ATTEMPTS_SUCCESS'
  | 'SUBSCRIPTION_BILLING_CYCLE_EDITS_CREATE'
  | 'SUBSCRIPTION_BILLING_CYCLE_EDITS_DELETE'
  | 'SUBSCRIPTION_BILLING_CYCLE_EDITS_UPDATE'
  | 'SUBSCRIPTION_BILLING_CYCLES_SKIP'
  | 'SUBSCRIPTION_BILLING_CYCLES_UNSKIP'
  | 'SUBSCRIPTION_CONTRACTS_ACTIVATE'
  | 'SUBSCRIPTION_CONTRACTS_CANCEL'
  | 'SUBSCRIPTION_CONTRACTS_CREATE'
  | 'SUBSCRIPTION_CONTRACTS_EXPIRE'
  | 'SUBSCRIPTION_CONTRACTS_FAIL'
  | 'SUBSCRIPTION_CONTRACTS_PAUSE'
  | 'SUBSCRIPTION_CONTRACTS_UPDATE'
  | 'TAX_SERVICES_CREATE'
  | 'TAX_SERVICES_UPDATE'
  | 'TENDER_TRANSACTIONS_CREATE'
  | 'THEMES_CREATE'
  | 'THEMES_DELETE'
  | 'THEMES_PUBLISH'
  | 'THEMES_UPDATE'
  | 'VARIANTS_IN_STOCK'
  | 'VARIANTS_OUT_OF_STOCK';

/** Units of measurement for weight. */
export type WeightUnit =
  | 'GRAMS'
  | 'KILOGRAMS'
  | 'OUNCES'
  | 'POUNDS';

