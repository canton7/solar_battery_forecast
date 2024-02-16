# Generated by ariadne-codegen

from .account_query import (
    AccountQuery,
    AccountQueryAccount,
    AccountQueryAccountElectricityAgreements,
    AccountQueryAccountElectricityAgreementsMeterPoint,
    AccountQueryAccountElectricityAgreementsMeterPointMeters,
    AccountQueryAccountElectricityAgreementsMeterPointMetersSmartExportElectricityMeter,
    AccountQueryAccountElectricityAgreementsMeterPointMetersSmartImportElectricityMeter,
    AccountQueryAccountElectricityAgreementsTariffDayNightTariff,
    AccountQueryAccountElectricityAgreementsTariffHalfHourlyTariff,
    AccountQueryAccountElectricityAgreementsTariffHalfHourlyTariffUnitRates,
    AccountQueryAccountElectricityAgreementsTariffPrepayTariff,
    AccountQueryAccountElectricityAgreementsTariffStandardTariff,
    AccountQueryAccountElectricityAgreementsTariffThreeRateTariff,
)
from .async_base_client import AsyncBaseClient
from .authenticate import Authenticate, AuthenticateObtainKrakenToken
from .base_model import BaseModel, Upload
from .client import Client
from .enums import (
    AccountApplicationStatus,
    AccountBillingOptionsPeriodLength,
    AccountCreditReasonType,
    AccountEventType,
    AccountPaymentStatusOptions,
    AccountPaymentTransactionTypeChoices,
    AccountReminderTypes,
    AccountRepaymentStatusOptions,
    AccountStatementStatus,
    AccountStatus,
    AccountStatusChoices,
    AccountTypeChoices,
    AccountUserRoleEnum,
    AddressTypeEnum,
    AgentContractStatusType,
    Alignment,
    APIExceptionCategories,
    APIExceptionPriority,
    APIExceptionResolutionStatus,
    APIExceptionResolutionType,
    APIExceptionTags,
    AppointmentStatus,
    AppSessionOutcome,
    BatteryCouplingType,
    BillsOrderBy,
    BillTypeEnum,
    BlackBoxMeterAmpChoices,
    BrandChoices,
    BroaderGroupRejectionReason,
    BusinessTypeOptions,
    ButtonStyle,
    ButtonVariance,
    CableFromMeterToChargePointChoices,
    CannotClaimReason,
    Category,
    CertificateType,
    ChargePointInstallationChoices,
    CHFConnectionMethod,
    CHFFaultReason,
    CHFFaultReturnType,
    CHFInstallType,
    CHFLocation,
    CHFNoFaultReturnType,
    ClientType,
    CollectDepositStatusChoices,
    CollectionCampaignType,
    CollectionMethod,
    CommsDeliveryPreference,
    CommsHubStatusUpdateType,
    CommsStrategyType,
    ConnectionStatus,
    ConsumptionGroupings,
    ConsumptionUnit,
    CurrencyOptions,
    CurrentQualifyingComponentOptions,
    DataFrequency,
    DebtCollectionProceedingStopReason,
    DeletePushNotificationBindingOutput,
    DeviceStatus,
    DeviceStatuses,
    DeviceType,
    DirectDebitInstructionStatus,
    DispatchNoticeTypeChoices,
    DistanceFromMeterToChargePointChoices,
    DNOStatus,
    ElectricityAgentContractContractType,
    ElectricityMeterMeterType,
    ElectricityMeterTypes,
    ElectricitySupplyType,
    EmailFormats,
    EnergyProductAvailability,
    EnergyProductDirection,
    EnergyProductFilters,
    EnergyUnit,
    EnodeVendors,
    EnrolmentStatus,
    EnrolmentStatusOptions,
    EnrolmentStepStatus,
    EVChargerTypes,
    EventReasonChoices,
    ExpiringTokenScope,
    ExportTechnologyType,
    ExternalAccountEventCategory,
    ExternalAccountEventContentType,
    ExternalAccountEventSubCategory,
    FITStatus,
    FormType,
    FuelType,
    FuelTypeChoices,
    GasAgentContactContractType,
    GasMeterMechanism,
    GasMeterPointMarketCategory,
    GasMeterPointMarketSectorCode,
    GasMeterPointMeterOwnershipType,
    GasMeterStatus,
    GasMeterTypes,
    GasSupplyType,
    GreennessForecastIndex,
    HardshipAgreementHardshipEntryReason,
    HardshipAgreementHardshipType,
    HeatPumpHeatType,
    HeatPumpPropertyType,
    HeatPumpQuoteExternalWall,
    HeatPumpQuoteStatus,
    HeatPumpQuoteWaterTank,
    IneligibilityReasons,
    InkCommunicationChannel,
    InkConversationStatus,
    InkMessageDeliveryStatus,
    InkMessageDirection,
    Interval,
    JoinableDeviceType,
    JoinConsumerDeviceChoices,
    KrakenFlexDeviceStatusChoices,
    KrakenFlexDeviceTypes,
    LineItemGroupingOptions,
    LineItemTypeOptions,
    LineLinkErrorType,
    LinkedObjectType,
    LinkTrainingStatus,
    MaximumRefundReasonChoices,
    MessageChannel,
    MeterLocationChoices,
    MeterReadingEventType,
    MeterStatus,
    MeterType,
    MeterTypeChoices,
    MeterTypes,
    Mode,
    NewMeterCategory,
    NonBespokeElectricityRateTypeChoices,
    NotifiableApplicationExternalProvider,
    NotifiableApplicationService,
    OctoplusRewardStatus,
    OperationAction,
    PaymentFrequencyOptions,
    PaymentMethodChoices,
    PaymentMethods,
    PaymentMode,
    PaymentReasonOptions,
    PaymentScheduleReasonOptions,
    PaymentsVendorChoices,
    PaymentType,
    PortfolioUserRoleEnum,
    PowerUnit,
    PremiseType,
    PreSignedTokenScope,
    PrintBatchStatus,
    ProductRateBands,
    ProviderChoices,
    QualifyingComponentOptions,
    QualifyingCriteriaOptions,
    QuotePaymentMethod,
    QuotePaymentMethodChoices,
    RateTypeChoices,
    ReadingDirectionType,
    ReadingFrequencyType,
    ReadingQualityType,
    ReadingStatisticTypeEnum,
    ReferralSchemeTypeChoices,
    ReferralStatusChoices,
    RemoveConsumerDeviceChoices,
    RepaymentMethod,
    RepaymentRequestStatus,
    RequestableRepaymentMethod,
    SalesChannelChoices,
    SavingSessionsAccountEventResultStatusChoices,
    SavingSessionsAccountEventStatus,
    ScheduleType,
    SensorType,
    SiteworksAppointmentAgent,
    SiteworksAppointmentStatus,
    SiteworksEventType,
    SmartFlexDeviceLifecycleStatus,
    SmartMeterInterestChoices,
    SmartMeterInterestSourceChoices,
    SmartMeterReadingFrequencyChoices,
    SmartOnboardingEventType,
    SmartOnboardingTariffCodes,
    SmartOnboardingTermsStatuses,
    SmartPrepayPaymentStatusChoices,
    SmartPrepayProcessStatusChoices,
    SMETS2InterestReason,
    Songs,
    State,
    StatementReversalsAfterClose,
    Status,
    SupplyType,
    TaxUnitType,
    TelemetryGrouping,
    TemperatureUnit,
    TestDispatchAssessmentFailureReason,
    TextStyle,
    TransactionsOrderBy,
    TransactionTypeFilter,
    UtilityType,
    WANCoverageStrengths,
    WhdAccountType,
    WorkCategory,
    YesNoAnswer,
    YesNoIDontKnowAnswer,
    Zone,
    ZoneType,
)
from .exceptions import (
    GraphQLClientError,
    GraphQLClientGraphQLError,
    GraphQLClientGraphQLMultiError,
    GraphQLClientHttpError,
    GraphQLClientInvalidResponseError,
)
from .input_types import (
    AcceptGoodsQuoteInput,
    AcceptTermsAndConditionsInput,
    AccountBillingAddressInput,
    AccountLedgerInput,
    AccountNumberInput,
    AccountReferenceInput,
    AccountSearchInputType,
    AccountUserInput,
    AddCampaignToAccountInput,
    AddEvPublicChargingTokenInput,
    AddressDetailsInput,
    AddressInput,
    AddressSearchType,
    AgreementRenewalProductInput,
    AmendPaymentInput,
    AmendUnbilledReadingInput,
    APIExceptionQueryInput,
    AssignInkBucketInput,
    AuthenticationInput,
    BackendScreenEventInput,
    BackendScreenParamInputType,
    BankDetailsInput,
    BatteryChargingPreferencesInput,
    BespokeElectricityUnitRatesInput,
    BespokeTariffRatesInput,
    BillingAddressDetailsInput,
    BillToLatestSmartMeterSnapshotInput,
    CancelRepaymentRequestInputType,
    CancelSiteworksAppointmentInput,
    Certificate,
    ChargeCarbonOffsetInput,
    ChargePointInput,
    ClimateControlStateInput,
    CollectDepositInput,
    CollectPaymentInput,
    CommissionInput,
    CommissionMeterInput,
    CompleteDeviceRegistrationInput,
    ConfirmSiteworksAppointmentSlotInput,
    ContactDetailsInput,
    CreateAccountChargeInput,
    CreateAccountCreditInput,
    CreateAccountFileAttachmentInput,
    CreateAccountNoteInput,
    CreateAccountReminderInput,
    CreateAcquisitionQuoteRequestForProductsInput,
    CreateAffiliateLinkInputType,
    CreateAffiliateOrganisationInputType,
    CreateAffiliateSessionInputType,
    CreateAPICallInput,
    CreateAPIExceptionEventInput,
    CreateAPIExceptionInput,
    CreateAPIExceptionNoteInput,
    CreateContributionAgreementInput,
    CreateDepositAgreementInput,
    CreateDirectDebitInstructionInput,
    CreateElectricJuiceAgreementInput,
    CreateElectricJuiceChargeCardInput,
    CreateElectricJuiceChargeInput,
    CreateElectricJuiceCreditInput,
    CreateEVChargersLeadInput,
    CreateEvPublicChargingAgreementInput,
    CreateExternalAccountEventInput,
    CreateGoodsQuoteInput,
    CreateGoodsQuoteWithoutAccountInput,
    CreateHeatPumpGoodsQuoteInput,
    CreateInkInboundMessageInput,
    CreateOrUpdateLoyaltyCardInput,
    CreateOrUpdateSiteworksAppointmentInput,
    CreatePaymentIntentInput,
    CreatePortfolioInput,
    CreatePortfolioUserRoleInput,
    CreatePurchaseInput,
    CreateQuoteInput,
    CreateQuoteRequestForProductsInput,
    CreateReferralInput,
    CreateRenewalQuoteRequestInput,
    CreateShellAccountInput,
    CreateSiteworksEventInput,
    CreditScoreData,
    CustomerFeedbackInputType,
    CustomerProfileInput,
    DeAuthenticationInput,
    DecommissionSmartDeviceInput,
    DeleteAccountReferenceInput,
    DeleteBoostChargeInput,
    DeletePushNotificationBindingInput,
    DepositAgreementInput,
    DeviceDetailsInput,
    DeviceRegistrationInput,
    DirectDebitInstructionLocalBankDetailsInput,
    DirectDebitPaymentDayUpdateInput,
    ElectricityBespokeRates,
    ElectricityConsumptionInput,
    ElectricityFiltersInput,
    ElectricityMeterPointConsumptionInput,
    ElectricityMeterPointInput,
    ElectricityMeterPointProductsInput,
    ElectricityProductInput,
    EndContributionAgreementInput,
    EVChargersLeadInput,
    EVPCLineItem,
    EVPCTaxItem,
    ExpireEvPublicChargingTokenInput,
    ExternalAccountEventContent,
    FanClubDiscountNotificationInput,
    FitInstallationInput,
    FitMeterInput,
    FitMeterReadingInput,
    FitReadingInput,
    ForceReauthenticationInput,
    FormSubmissionInput,
    GasBespokeRates,
    GasConsumptionInput,
    GasFiltersInput,
    GasMeterPointConsumptionInput,
    GasMeterPointInput,
    GasMeterPointProductsInput,
    GasProductInput,
    GenerateInkPresignedUrlInput,
    GetEmbeddedSecretForNewPaymentInstructionInput,
    HeatPumpInput,
    HotWaterStateInput,
    InitiateStandalonePaymentInput,
    InkEmailMessageInput,
    InkGenericMessageAttachmentInput,
    InkGenericMessageInput,
    InkMessageInput,
    InstalledAppliancesInput,
    InvalidatePaymentInstructionInput,
    InvalidatePreSignedTokenInput,
    InvalidatePreSignedTokensForUserInput,
    InvalidateRefreshTokenInput,
    InvalidateRefreshTokensForUserInput,
    JoinConsumerDeviceInput,
    JoinFanClubInput,
    JoinSavingSessionsCampaignInput,
    JoinSavingSessionsEventInput,
    LinkUserToLineInput,
    MetadataInput,
    MeterInput,
    MeterPointSwitchContext,
    MoveInNewProperty,
    MoveOutInput,
    MoveOutNewTenant,
    NewAccountInput,
    ObtainJSONWebTokenInput,
    ObtainLongLivedRefreshTokenInput,
    OccupyInput,
    OCPPAuthenticationInput,
    PaymentScheduleInput,
    PositionInput,
    PostCreditInput,
    PostEVPublicChargingChargeInput,
    PostEVPublicChargingCreditInput,
    ProductToPurchaseInput,
    ProductToQuoteInput,
    PropertyDetailsInput,
    PropertyProfileInput,
    ProvisioningClaimRequestParameters,
    PublishTransactionalMessagingTriggerInput,
    QuoteAccountOnProductsInput,
    QuoteAddressInput,
    QuoteCampaignOfferInput,
    QuoteNewMeterPointsInput,
    QuoteNewMeterPointsOnBespokeProductsInput,
    ReadingInputType,
    ReauthenticateDeviceInput,
    RedeemLoyaltyPointsInput,
    RedeemOctoPointsInput,
    RefreshQuoteInput,
    RefundRequestInput,
    RegisterDeviceInput,
    RegisterHeatPumpInput,
    RegisterPushNotificationBindingInput,
    RegisterSmartDeviceInput,
    RemoveConsumerDeviceInput,
    RemovedElectricityMeterInput,
    RemovedElectricityMeterPointInput,
    RemovedElectricityMeterRegisterInput,
    RemovedGasMeterInput,
    RemovedGasMeterPointInput,
    RemovedMeterPrepayDataInput,
    RenewAgreementForMeterPointInput,
    RenewAgreementsForAccountInput,
    RenewAgreementsInput,
    RepaymentInput,
    ReplaceAgreementInput,
    ReplaceCommsHubInput,
    ReportRemovedMeterDetailsInput,
    RequestConsumptionDataInput,
    RequestPasswordResetInput,
    RequestRepaymentInputType,
    RequestResetPasswordMutationInput,
    RequoteInput,
    ResetPasswordMutationInput,
    RoomTemperatureInput,
    SavingSessionsEnrolmentOptions,
    ScheduleSettings,
    SensorDisplayNameUpdate,
    SetLoyaltyPointsUserInput,
    SetUpDirectDebitInstructionInput,
    SetZoneModeParameters,
    SetZonePrimarySensorParameters,
    SetZoneSchedulesParameters,
    ShareGoodsQuoteInput,
    SmartMeterDeviceInput,
    SmartPrepayMeterAmountInput,
    StartExportOnboardingProcessInput,
    StartSmartOnboardingProcessInput,
    StoreElectricJuicePaymentInstructionInput,
    StorePaymentInstructionInput,
    SwitchMeterPointProductsInput,
    TermsAndConditions,
    TermsVersionInput,
    TransferLedgerBalanceInputType,
    TransferLoyaltyPointsBetweenUsersInput,
    TypedSourceInputType,
    UpdateAccountBillingEmailInput,
    UpdateAccountSmartMeterInterestInput,
    UpdateAccountUserCommsPreferencesMutationInput,
    UpdateAccountUserMutationInput,
    UpdateAffiliateLinkInputType,
    UpdateAffiliateOrganisationInputType,
    UpdateAPIExceptionInput,
    UpdateAPIExceptionNoteInput,
    UpdateCommsDeliveryPreferenceInput,
    UpdateCommsHubStatusInput,
    UpdateMessageTagsInput,
    UpdatePasswordInput,
    UpdatePaymentSchedulePaymentAmountInput,
    UpdatePaymentSchedulePaymentDayInput,
    UpdateSmartMeterDataPreferencesInput,
    UpdateSpecialCircumstancesInput,
    UpdateSsdInput,
    UpdateUserInput,
    UtilityFiltersInput,
    ValidateEmailInput,
    ValidatePhoneNumberInput,
    VehicleChargingPreferencesInput,
    VehicleEligibilityInputType,
    VehicleInput,
    WarmHomeDiscountApplicationInputType,
    WheelOfFortuneSpinInput,
    ZoneSchedule,
)
from .saving_sessions_query import (
    SavingSessionsQuery,
    SavingSessionsQuerySavingSessions,
    SavingSessionsQuerySavingSessionsAccount,
    SavingSessionsQuerySavingSessionsAccountJoinedEvents,
    SavingSessionsQuerySavingSessionsEvents,
)

__all__ = [
    "APIExceptionCategories",
    "APIExceptionPriority",
    "APIExceptionQueryInput",
    "APIExceptionResolutionStatus",
    "APIExceptionResolutionType",
    "APIExceptionTags",
    "AcceptGoodsQuoteInput",
    "AcceptTermsAndConditionsInput",
    "AccountApplicationStatus",
    "AccountBillingAddressInput",
    "AccountBillingOptionsPeriodLength",
    "AccountCreditReasonType",
    "AccountEventType",
    "AccountLedgerInput",
    "AccountNumberInput",
    "AccountPaymentStatusOptions",
    "AccountPaymentTransactionTypeChoices",
    "AccountQuery",
    "AccountQueryAccount",
    "AccountQueryAccountElectricityAgreements",
    "AccountQueryAccountElectricityAgreementsMeterPoint",
    "AccountQueryAccountElectricityAgreementsMeterPointMeters",
    "AccountQueryAccountElectricityAgreementsMeterPointMetersSmartExportElectricityMeter",
    "AccountQueryAccountElectricityAgreementsMeterPointMetersSmartImportElectricityMeter",
    "AccountQueryAccountElectricityAgreementsTariffDayNightTariff",
    "AccountQueryAccountElectricityAgreementsTariffHalfHourlyTariff",
    "AccountQueryAccountElectricityAgreementsTariffHalfHourlyTariffUnitRates",
    "AccountQueryAccountElectricityAgreementsTariffPrepayTariff",
    "AccountQueryAccountElectricityAgreementsTariffStandardTariff",
    "AccountQueryAccountElectricityAgreementsTariffThreeRateTariff",
    "AccountReferenceInput",
    "AccountReminderTypes",
    "AccountRepaymentStatusOptions",
    "AccountSearchInputType",
    "AccountStatementStatus",
    "AccountStatus",
    "AccountStatusChoices",
    "AccountTypeChoices",
    "AccountUserInput",
    "AccountUserRoleEnum",
    "AddCampaignToAccountInput",
    "AddEvPublicChargingTokenInput",
    "AddressDetailsInput",
    "AddressInput",
    "AddressSearchType",
    "AddressTypeEnum",
    "AgentContractStatusType",
    "AgreementRenewalProductInput",
    "Alignment",
    "AmendPaymentInput",
    "AmendUnbilledReadingInput",
    "AppSessionOutcome",
    "AppointmentStatus",
    "AssignInkBucketInput",
    "AsyncBaseClient",
    "Authenticate",
    "AuthenticateObtainKrakenToken",
    "AuthenticationInput",
    "BackendScreenEventInput",
    "BackendScreenParamInputType",
    "BankDetailsInput",
    "BaseModel",
    "BatteryChargingPreferencesInput",
    "BatteryCouplingType",
    "BespokeElectricityUnitRatesInput",
    "BespokeTariffRatesInput",
    "BillToLatestSmartMeterSnapshotInput",
    "BillTypeEnum",
    "BillingAddressDetailsInput",
    "BillsOrderBy",
    "BlackBoxMeterAmpChoices",
    "BrandChoices",
    "BroaderGroupRejectionReason",
    "BusinessTypeOptions",
    "ButtonStyle",
    "ButtonVariance",
    "CHFConnectionMethod",
    "CHFFaultReason",
    "CHFFaultReturnType",
    "CHFInstallType",
    "CHFLocation",
    "CHFNoFaultReturnType",
    "CableFromMeterToChargePointChoices",
    "CancelRepaymentRequestInputType",
    "CancelSiteworksAppointmentInput",
    "CannotClaimReason",
    "Category",
    "Certificate",
    "CertificateType",
    "ChargeCarbonOffsetInput",
    "ChargePointInput",
    "ChargePointInstallationChoices",
    "Client",
    "ClientType",
    "ClimateControlStateInput",
    "CollectDepositInput",
    "CollectDepositStatusChoices",
    "CollectPaymentInput",
    "CollectionCampaignType",
    "CollectionMethod",
    "CommissionInput",
    "CommissionMeterInput",
    "CommsDeliveryPreference",
    "CommsHubStatusUpdateType",
    "CommsStrategyType",
    "CompleteDeviceRegistrationInput",
    "ConfirmSiteworksAppointmentSlotInput",
    "ConnectionStatus",
    "ConsumptionGroupings",
    "ConsumptionUnit",
    "ContactDetailsInput",
    "CreateAPICallInput",
    "CreateAPIExceptionEventInput",
    "CreateAPIExceptionInput",
    "CreateAPIExceptionNoteInput",
    "CreateAccountChargeInput",
    "CreateAccountCreditInput",
    "CreateAccountFileAttachmentInput",
    "CreateAccountNoteInput",
    "CreateAccountReminderInput",
    "CreateAcquisitionQuoteRequestForProductsInput",
    "CreateAffiliateLinkInputType",
    "CreateAffiliateOrganisationInputType",
    "CreateAffiliateSessionInputType",
    "CreateContributionAgreementInput",
    "CreateDepositAgreementInput",
    "CreateDirectDebitInstructionInput",
    "CreateEVChargersLeadInput",
    "CreateElectricJuiceAgreementInput",
    "CreateElectricJuiceChargeCardInput",
    "CreateElectricJuiceChargeInput",
    "CreateElectricJuiceCreditInput",
    "CreateEvPublicChargingAgreementInput",
    "CreateExternalAccountEventInput",
    "CreateGoodsQuoteInput",
    "CreateGoodsQuoteWithoutAccountInput",
    "CreateHeatPumpGoodsQuoteInput",
    "CreateInkInboundMessageInput",
    "CreateOrUpdateLoyaltyCardInput",
    "CreateOrUpdateSiteworksAppointmentInput",
    "CreatePaymentIntentInput",
    "CreatePortfolioInput",
    "CreatePortfolioUserRoleInput",
    "CreatePurchaseInput",
    "CreateQuoteInput",
    "CreateQuoteRequestForProductsInput",
    "CreateReferralInput",
    "CreateRenewalQuoteRequestInput",
    "CreateShellAccountInput",
    "CreateSiteworksEventInput",
    "CreditScoreData",
    "CurrencyOptions",
    "CurrentQualifyingComponentOptions",
    "CustomerFeedbackInputType",
    "CustomerProfileInput",
    "DNOStatus",
    "DataFrequency",
    "DeAuthenticationInput",
    "DebtCollectionProceedingStopReason",
    "DecommissionSmartDeviceInput",
    "DeleteAccountReferenceInput",
    "DeleteBoostChargeInput",
    "DeletePushNotificationBindingInput",
    "DeletePushNotificationBindingOutput",
    "DepositAgreementInput",
    "DeviceDetailsInput",
    "DeviceRegistrationInput",
    "DeviceStatus",
    "DeviceStatuses",
    "DeviceType",
    "DirectDebitInstructionLocalBankDetailsInput",
    "DirectDebitInstructionStatus",
    "DirectDebitPaymentDayUpdateInput",
    "DispatchNoticeTypeChoices",
    "DistanceFromMeterToChargePointChoices",
    "EVChargerTypes",
    "EVChargersLeadInput",
    "EVPCLineItem",
    "EVPCTaxItem",
    "ElectricityAgentContractContractType",
    "ElectricityBespokeRates",
    "ElectricityConsumptionInput",
    "ElectricityFiltersInput",
    "ElectricityMeterMeterType",
    "ElectricityMeterPointConsumptionInput",
    "ElectricityMeterPointInput",
    "ElectricityMeterPointProductsInput",
    "ElectricityMeterTypes",
    "ElectricityProductInput",
    "ElectricitySupplyType",
    "EmailFormats",
    "EndContributionAgreementInput",
    "EnergyProductAvailability",
    "EnergyProductDirection",
    "EnergyProductFilters",
    "EnergyUnit",
    "EnodeVendors",
    "EnrolmentStatus",
    "EnrolmentStatusOptions",
    "EnrolmentStepStatus",
    "EventReasonChoices",
    "ExpireEvPublicChargingTokenInput",
    "ExpiringTokenScope",
    "ExportTechnologyType",
    "ExternalAccountEventCategory",
    "ExternalAccountEventContent",
    "ExternalAccountEventContentType",
    "ExternalAccountEventSubCategory",
    "FITStatus",
    "FanClubDiscountNotificationInput",
    "FitInstallationInput",
    "FitMeterInput",
    "FitMeterReadingInput",
    "FitReadingInput",
    "ForceReauthenticationInput",
    "FormSubmissionInput",
    "FormType",
    "FuelType",
    "FuelTypeChoices",
    "GasAgentContactContractType",
    "GasBespokeRates",
    "GasConsumptionInput",
    "GasFiltersInput",
    "GasMeterMechanism",
    "GasMeterPointConsumptionInput",
    "GasMeterPointInput",
    "GasMeterPointMarketCategory",
    "GasMeterPointMarketSectorCode",
    "GasMeterPointMeterOwnershipType",
    "GasMeterPointProductsInput",
    "GasMeterStatus",
    "GasMeterTypes",
    "GasProductInput",
    "GasSupplyType",
    "GenerateInkPresignedUrlInput",
    "GetEmbeddedSecretForNewPaymentInstructionInput",
    "GraphQLClientError",
    "GraphQLClientGraphQLError",
    "GraphQLClientGraphQLMultiError",
    "GraphQLClientHttpError",
    "GraphQLClientInvalidResponseError",
    "GreennessForecastIndex",
    "HardshipAgreementHardshipEntryReason",
    "HardshipAgreementHardshipType",
    "HeatPumpHeatType",
    "HeatPumpInput",
    "HeatPumpPropertyType",
    "HeatPumpQuoteExternalWall",
    "HeatPumpQuoteStatus",
    "HeatPumpQuoteWaterTank",
    "HotWaterStateInput",
    "IneligibilityReasons",
    "InitiateStandalonePaymentInput",
    "InkCommunicationChannel",
    "InkConversationStatus",
    "InkEmailMessageInput",
    "InkGenericMessageAttachmentInput",
    "InkGenericMessageInput",
    "InkMessageDeliveryStatus",
    "InkMessageDirection",
    "InkMessageInput",
    "InstalledAppliancesInput",
    "Interval",
    "InvalidatePaymentInstructionInput",
    "InvalidatePreSignedTokenInput",
    "InvalidatePreSignedTokensForUserInput",
    "InvalidateRefreshTokenInput",
    "InvalidateRefreshTokensForUserInput",
    "JoinConsumerDeviceChoices",
    "JoinConsumerDeviceInput",
    "JoinFanClubInput",
    "JoinSavingSessionsCampaignInput",
    "JoinSavingSessionsEventInput",
    "JoinableDeviceType",
    "KrakenFlexDeviceStatusChoices",
    "KrakenFlexDeviceTypes",
    "LineItemGroupingOptions",
    "LineItemTypeOptions",
    "LineLinkErrorType",
    "LinkTrainingStatus",
    "LinkUserToLineInput",
    "LinkedObjectType",
    "MaximumRefundReasonChoices",
    "MessageChannel",
    "MetadataInput",
    "MeterInput",
    "MeterLocationChoices",
    "MeterPointSwitchContext",
    "MeterReadingEventType",
    "MeterStatus",
    "MeterType",
    "MeterTypeChoices",
    "MeterTypes",
    "Mode",
    "MoveInNewProperty",
    "MoveOutInput",
    "MoveOutNewTenant",
    "NewAccountInput",
    "NewMeterCategory",
    "NonBespokeElectricityRateTypeChoices",
    "NotifiableApplicationExternalProvider",
    "NotifiableApplicationService",
    "OCPPAuthenticationInput",
    "ObtainJSONWebTokenInput",
    "ObtainLongLivedRefreshTokenInput",
    "OccupyInput",
    "OctoplusRewardStatus",
    "OperationAction",
    "PaymentFrequencyOptions",
    "PaymentMethodChoices",
    "PaymentMethods",
    "PaymentMode",
    "PaymentReasonOptions",
    "PaymentScheduleInput",
    "PaymentScheduleReasonOptions",
    "PaymentType",
    "PaymentsVendorChoices",
    "PortfolioUserRoleEnum",
    "PositionInput",
    "PostCreditInput",
    "PostEVPublicChargingChargeInput",
    "PostEVPublicChargingCreditInput",
    "PowerUnit",
    "PreSignedTokenScope",
    "PremiseType",
    "PrintBatchStatus",
    "ProductRateBands",
    "ProductToPurchaseInput",
    "ProductToQuoteInput",
    "PropertyDetailsInput",
    "PropertyProfileInput",
    "ProviderChoices",
    "ProvisioningClaimRequestParameters",
    "PublishTransactionalMessagingTriggerInput",
    "QualifyingComponentOptions",
    "QualifyingCriteriaOptions",
    "QuoteAccountOnProductsInput",
    "QuoteAddressInput",
    "QuoteCampaignOfferInput",
    "QuoteNewMeterPointsInput",
    "QuoteNewMeterPointsOnBespokeProductsInput",
    "QuotePaymentMethod",
    "QuotePaymentMethodChoices",
    "RateTypeChoices",
    "ReadingDirectionType",
    "ReadingFrequencyType",
    "ReadingInputType",
    "ReadingQualityType",
    "ReadingStatisticTypeEnum",
    "ReauthenticateDeviceInput",
    "RedeemLoyaltyPointsInput",
    "RedeemOctoPointsInput",
    "ReferralSchemeTypeChoices",
    "ReferralStatusChoices",
    "RefreshQuoteInput",
    "RefundRequestInput",
    "RegisterDeviceInput",
    "RegisterHeatPumpInput",
    "RegisterPushNotificationBindingInput",
    "RegisterSmartDeviceInput",
    "RemoveConsumerDeviceChoices",
    "RemoveConsumerDeviceInput",
    "RemovedElectricityMeterInput",
    "RemovedElectricityMeterPointInput",
    "RemovedElectricityMeterRegisterInput",
    "RemovedGasMeterInput",
    "RemovedGasMeterPointInput",
    "RemovedMeterPrepayDataInput",
    "RenewAgreementForMeterPointInput",
    "RenewAgreementsForAccountInput",
    "RenewAgreementsInput",
    "RepaymentInput",
    "RepaymentMethod",
    "RepaymentRequestStatus",
    "ReplaceAgreementInput",
    "ReplaceCommsHubInput",
    "ReportRemovedMeterDetailsInput",
    "RequestConsumptionDataInput",
    "RequestPasswordResetInput",
    "RequestRepaymentInputType",
    "RequestResetPasswordMutationInput",
    "RequestableRepaymentMethod",
    "RequoteInput",
    "ResetPasswordMutationInput",
    "RoomTemperatureInput",
    "SMETS2InterestReason",
    "SalesChannelChoices",
    "SavingSessionsAccountEventResultStatusChoices",
    "SavingSessionsAccountEventStatus",
    "SavingSessionsEnrolmentOptions",
    "SavingSessionsQuery",
    "SavingSessionsQuerySavingSessions",
    "SavingSessionsQuerySavingSessionsAccount",
    "SavingSessionsQuerySavingSessionsAccountJoinedEvents",
    "SavingSessionsQuerySavingSessionsEvents",
    "ScheduleSettings",
    "ScheduleType",
    "SensorDisplayNameUpdate",
    "SensorType",
    "SetLoyaltyPointsUserInput",
    "SetUpDirectDebitInstructionInput",
    "SetZoneModeParameters",
    "SetZonePrimarySensorParameters",
    "SetZoneSchedulesParameters",
    "ShareGoodsQuoteInput",
    "SiteworksAppointmentAgent",
    "SiteworksAppointmentStatus",
    "SiteworksEventType",
    "SmartFlexDeviceLifecycleStatus",
    "SmartMeterDeviceInput",
    "SmartMeterInterestChoices",
    "SmartMeterInterestSourceChoices",
    "SmartMeterReadingFrequencyChoices",
    "SmartOnboardingEventType",
    "SmartOnboardingTariffCodes",
    "SmartOnboardingTermsStatuses",
    "SmartPrepayMeterAmountInput",
    "SmartPrepayPaymentStatusChoices",
    "SmartPrepayProcessStatusChoices",
    "Songs",
    "StartExportOnboardingProcessInput",
    "StartSmartOnboardingProcessInput",
    "State",
    "StatementReversalsAfterClose",
    "Status",
    "StoreElectricJuicePaymentInstructionInput",
    "StorePaymentInstructionInput",
    "SupplyType",
    "SwitchMeterPointProductsInput",
    "TaxUnitType",
    "TelemetryGrouping",
    "TemperatureUnit",
    "TermsAndConditions",
    "TermsVersionInput",
    "TestDispatchAssessmentFailureReason",
    "TextStyle",
    "TransactionTypeFilter",
    "TransactionsOrderBy",
    "TransferLedgerBalanceInputType",
    "TransferLoyaltyPointsBetweenUsersInput",
    "TypedSourceInputType",
    "UpdateAPIExceptionInput",
    "UpdateAPIExceptionNoteInput",
    "UpdateAccountBillingEmailInput",
    "UpdateAccountSmartMeterInterestInput",
    "UpdateAccountUserCommsPreferencesMutationInput",
    "UpdateAccountUserMutationInput",
    "UpdateAffiliateLinkInputType",
    "UpdateAffiliateOrganisationInputType",
    "UpdateCommsDeliveryPreferenceInput",
    "UpdateCommsHubStatusInput",
    "UpdateMessageTagsInput",
    "UpdatePasswordInput",
    "UpdatePaymentSchedulePaymentAmountInput",
    "UpdatePaymentSchedulePaymentDayInput",
    "UpdateSmartMeterDataPreferencesInput",
    "UpdateSpecialCircumstancesInput",
    "UpdateSsdInput",
    "UpdateUserInput",
    "Upload",
    "UtilityFiltersInput",
    "UtilityType",
    "ValidateEmailInput",
    "ValidatePhoneNumberInput",
    "VehicleChargingPreferencesInput",
    "VehicleEligibilityInputType",
    "VehicleInput",
    "WANCoverageStrengths",
    "WarmHomeDiscountApplicationInputType",
    "WhdAccountType",
    "WheelOfFortuneSpinInput",
    "WorkCategory",
    "YesNoAnswer",
    "YesNoIDontKnowAnswer",
    "Zone",
    "ZoneSchedule",
    "ZoneType",
]
