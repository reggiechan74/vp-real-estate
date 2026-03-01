# Domain Data Dictionary: Commercial Lease Abstraction — North America

**Reference:** `re-ddd:lease_abstraction_commercial_na@1.0.0`

**Scope:** Field definitions for commercial lease abstraction across office and industrial lease types in North American jurisdictions.

**Relationship to REIXS:** This DDD is referenced by REIXS spec `REIXS-LA-NA-001` (Lease Abstraction — North American Commercial). The REIXS spec defines *how* to extract these fields (provenance, status tracking, conflict handling). This DDD defines *what* each field means and its data type.

---

## Sections

The schema defines **24 sections**. Sections 1-21 are extracted from the lease document. Sections 22-24 are derived/analytical.

### 1. documentInformation

Abstract metadata — not extracted from the lease, created by the abstraction process.

| Field | Type | Description |
|---|---|---|
| `abstractDate` | string (ISO 8601) | Date the abstraction was performed |
| `abstractedBy` | string | Person or system that performed the abstraction |
| `sourceDocument` | string | Filename or identifier of the source lease document |
| `lastUpdated` | string (ISO 8601) | Date the abstraction was last updated |

### 2. parties

The legal entities bound by the lease.

| Field | Type | Description |
|---|---|---|
| `landlord.name` | string | Full legal name of the landlord entity |
| `landlord.address` | string | Registered address of the landlord |
| `landlord.contact` | string | Contact information (name, phone, email) |
| `tenant.name` | string | Full legal name of the tenant entity |
| `tenant.address` | string | Registered address of the tenant |
| `tenant.contact` | string | Contact information (name, phone, email) |
| `indemnifier.name` | string | Full legal name of guarantor/indemnifier |
| `indemnifier.address` | string | Registered address of the indemnifier |
| `indemnifier.relationshipToTenant` | string | Legal relationship (e.g., parent company, principal) |

**Critical section** — 2x scoring weight. Misidentification of landlord/tenant is an AutoFail condition.

### 3. premises

Physical description of the leased space.

| Field | Type | Description |
|---|---|---|
| `propertyInformation.projectName` | string | Name of the building, complex, or project |
| `propertyInformation.buildingAddress` | string | Street address of the building |
| `propertyInformation.unitNumber` | string | Suite or unit number within the building |
| `propertyInformation.legalDescription` | string | Legal description (lot, plan, municipal reference) |
| `area.rentableAreaSqFt` | number | Rentable area in square feet |
| `area.measurementStandard` | string | Measurement standard used (e.g., ANSI/BOMA Z65.1) |
| `area.commonFacilities` | string | Description of shared/common areas |
| `area.parkingSpaces` | number | Number of allocated parking spaces |
| `area.storage` | string | Storage space description and allocation |
| `permittedUse.primaryUse` | string | Primary permitted use of the premises |
| `permittedUse.restrictions` | array[string] | Use restrictions imposed by the lease |
| `permittedUse.prohibitedUses` | array[string] | Explicitly prohibited uses |

**Critical section** — 2x scoring weight.

### 4. term

Duration and timing of the lease.

| Field | Type | Description |
|---|---|---|
| `leaseTerm.commencementDate` | string (ISO 8601) | Date the lease term begins |
| `leaseTerm.deliveryDate` | string (ISO 8601) | Date premises are delivered to tenant (may differ from commencement) |
| `leaseTerm.expiryDate` | string (ISO 8601) | Date the lease term ends |
| `leaseTerm.termLengthYears` | number | Length of the lease term in years |
| `leaseTerm.termLengthMonths` | number | Length of the lease term in months (if not whole years) |
| `leaseTerm.fixturingPeriod` | string | Duration and terms of any fixturing/build-out period |
| `renewalOptions.numberOfOptions` | number | Number of renewal options available to tenant |
| `renewalOptions.lengthOfEachOption` | string | Duration of each renewal option period |
| `renewalOptions.noticePeriodRequired` | string | Notice period to exercise renewal (e.g., "12 months prior to expiry") |
| `renewalOptions.rentDeterminationMethod` | string | How renewal rent is determined (e.g., fair market, fixed increase) |
| `earlyTermination.terminationRights` | boolean | Whether the tenant has early termination rights |
| `earlyTermination.conditions` | string | Conditions that must be met for early termination |
| `earlyTermination.noticePeriod` | string | Required notice period for early termination |
| `earlyTermination.penalties` | string | Financial penalties for early termination |

**Critical section** — 2x scoring weight. Commencement/expiry dates without provenance is an AutoFail condition.

### 5. rent

Financial obligations for base rent and escalations.

| Field | Type | Description |
|---|---|---|
| `basicRent[].period` | string | Period label (e.g., "Year 1", "Months 1-12") |
| `basicRent[].annualRent` | number | Annual base rent amount |
| `basicRent[].monthlyRent` | number | Monthly base rent amount |
| `basicRent[].ratePerSqFt` | number | Rent rate per square foot |
| `rentEscalations.escalationType` | string | Type of escalation (fixed, CPI, market) |
| `rentEscalations.frequency` | string | How often escalations occur |
| `rentEscalations.baseYearOrIndex` | string | Base year or index used for escalation calculation |
| `rentEscalations.capPercentage` | number | Maximum annual increase percentage |
| `rentEscalations.floorPercentage` | number | Minimum annual increase percentage |
| `additionalRent.operatingCosts.tenantShare` | string | Tenant's share of operating costs |
| `additionalRent.operatingCosts.method` | string | Calculation method for operating cost share |
| `additionalRent.realtyTaxes.tenantShare` | string | Tenant's share of realty taxes |
| `additionalRent.realtyTaxes.method` | string | Calculation method for tax share |
| `additionalRent.managementFee.percentage` | number | Management fee as percentage |
| `additionalRent.managementFee.basis` | string | What the management fee is calculated on |
| `additionalRent.utilities.separatelyMetered` | boolean | Whether utilities are separately metered |
| `additionalRent.utilities.tenantResponsibility` | string | Which utilities tenant pays directly |
| `additionalRent.camCharges` | string | Common area maintenance charges |
| `proportionateShare.calculationMethod` | string | How proportionate share is calculated |
| `proportionateShare.percentage` | number | Tenant's proportionate share percentage |
| `proportionateShare.adjustmentProvisions` | string | How the share is adjusted over time |
| `paymentTerms.dueDate` | string | When rent payments are due |
| `paymentTerms.paymentMethod` | string | Accepted payment methods |
| `paymentTerms.latePaymentPenalty` | string | Penalty for late payment |
| `paymentTerms.nsfFee` | number | Fee for insufficient funds / bounced payment |

**Critical section** — 2x scoring weight. Financial values must be extracted verbatim with normalized form as a separate field. Wrong currency is an AutoFail condition.

### 6. depositsAndSecurity

Security deposits and credit instruments.

| Field | Type | Description |
|---|---|---|
| `rentDeposit.amount` | number | Deposit amount |
| `rentDeposit.heldAs` | string | How the deposit is held (e.g., trust, general account) |
| `rentDeposit.interest` | boolean | Whether interest accrues on the deposit |
| `rentDeposit.interestRate` | number | Interest rate applied to deposit |
| `rentDeposit.application` | string | When/how the deposit may be applied |
| `rentDeposit.returnConditions` | string | Conditions for return of deposit |
| `letterOfCredit.required` | boolean | Whether an LOC is required |
| `letterOfCredit.amount` | number | LOC face amount |
| `letterOfCredit.beneficiary` | string | Named beneficiary of the LOC |
| `letterOfCredit.expiry` | string | LOC expiry date or terms |
| `letterOfCredit.reductionProvisions` | string | How the LOC amount may be reduced over time |
| `otherSecurity.type` | string | Type of additional security |
| `otherSecurity.amount` | number | Amount of additional security |
| `otherSecurity.terms` | string | Terms governing additional security |

### 7. operatingCostsAndTaxes

Lease structure and cost allocation.

| Field | Type | Description |
|---|---|---|
| `netLeaseProvisions.leaseType` | string | Lease classification (net, semi-gross, gross, modified gross) |
| `netLeaseProvisions.tenantObligations` | array[string] | Specific cost obligations assigned to tenant |
| `operatingCosts.includedItems` | array[string] | Items included in operating cost calculations |
| `operatingCosts.excludedItems` | array[string] | Items excluded from operating cost calculations |
| `operatingCosts.baseYear` | string | Base year for operating cost calculations |
| `operatingCosts.grossUpProvisions` | string | Gross-up provisions for occupancy adjustments |
| `operatingCosts.cap` | number | Cap on operating cost increases (percentage or amount) |
| `realtyTaxes.paymentMethod` | string | How tenant pays its tax share |
| `realtyTaxes.tenantShare` | string | Tenant's proportionate share of taxes |
| `realtyTaxes.contestRights` | string | Tenant's right to contest tax assessments |
| `realtyTaxes.taxIncreaseLimitations` | string | Limitations on tax increase pass-throughs |
| `businessAndSalesTaxes.responsibility` | string | Which party is responsible for business/sales taxes |
| `businessAndSalesTaxes.hstGst` | string | HST/GST applicability and responsibility |

### 8. useAndOperations

Permitted activities and operating requirements.

| Field | Type | Description |
|---|---|---|
| `permittedUse.specificUsesAllowed` | array[string] | Specific uses permitted |
| `permittedUse.buildingStandard` | string | Building standard applicable to the premises |
| `permittedUse.complianceRequirements` | array[string] | Compliance requirements for the permitted use |
| `prohibitedUses.specificProhibitions` | array[string] | Explicitly prohibited uses |
| `prohibitedUses.hazardousSubstances` | string | Restrictions on hazardous substances |
| `prohibitedUses.bioMedicalWaste` | string | Restrictions on biomedical waste |
| `operatingHours.businessHours` | string | Standard business hours for the building |
| `operatingHours.access` | string | Tenant access hours (may differ from business hours) |
| `operatingHours.afterHoursHVAC` | string | Availability and cost of after-hours HVAC |
| `signage.exteriorSignageRights` | string | Tenant's rights for exterior signage |
| `signage.interiorSignage` | string | Interior signage provisions |
| `signage.approvalRequirements` | string | Required approvals for signage |
| `signage.costResponsibility` | string | Who pays for signage installation and maintenance |

### 9. maintenanceAndRepairs

Maintenance responsibilities allocated between parties.

| Field | Type | Description |
|---|---|---|
| `landlordObligations.structural` | string | Structural maintenance responsibility |
| `landlordObligations.roof` | string | Roof maintenance responsibility |
| `landlordObligations.commonAreas` | string | Common area maintenance responsibility |
| `landlordObligations.buildingSystems` | string | Building systems (electrical, plumbing) maintenance |
| `landlordObligations.hvac` | string | HVAC system maintenance responsibility |
| `tenantObligations.interiorMaintenance` | string | Interior maintenance responsibility |
| `tenantObligations.equipment` | string | Equipment maintenance responsibility |
| `tenantObligations.janitorial` | string | Janitorial services responsibility |
| `tenantObligations.repairsUnderThreshold` | number | Dollar threshold below which tenant pays for repairs |
| `capitalImprovements.landlordsRights` | string | Landlord's rights regarding capital improvements |
| `capitalImprovements.tenantObligations` | string | Tenant's obligations for capital improvements |
| `capitalImprovements.amortization` | string | How capital improvement costs are amortized |

### 10. alterationsAndImprovements

Modifications to the premises.

| Field | Type | Description |
|---|---|---|
| `landlordWork.description` | string | Description of landlord's initial work/build-out |
| `landlordWork.completionDate` | string (ISO 8601) | Date landlord's work must be completed |
| `landlordWork.allowance` | number | Tenant improvement allowance from landlord |
| `tenantWork.preApprovalRequired` | boolean | Whether landlord approval is required for tenant work |
| `tenantWork.approvalThreshold` | number | Dollar threshold above which approval is required |
| `tenantWork.architectEngineerRequirements` | string | Professional requirements for tenant's work |
| `tenantWork.insuranceDuringConstruction` | string | Insurance requirements during construction |
| `tenantWork.permitsResponsibility` | string | Who is responsible for obtaining permits |
| `leaseholdImprovements.ownership` | string | Who owns leasehold improvements during the term |
| `leaseholdImprovements.removalAtEndOfTerm` | string | Requirements for removal at end of term |
| `leaseholdImprovements.restorationObligations` | string | Restoration obligations at end of term |
| `tradeFixtures.definition` | string | How trade fixtures are defined in the lease |
| `tradeFixtures.removalRights` | string | Tenant's rights to remove trade fixtures |
| `tradeFixtures.restoration` | string | Restoration requirements after fixture removal |

### 11. insuranceAndIndemnity

Insurance requirements and indemnification provisions.

| Field | Type | Description |
|---|---|---|
| `landlordInsurance.propertyInsurance` | string | Landlord's property insurance coverage |
| `landlordInsurance.liabilityInsurance` | string | Landlord's liability insurance coverage |
| `landlordInsurance.other` | string | Other insurance carried by landlord |
| `tenantInsuranceRequirements.commercialGeneralLiability.minimumCoverage` | number | Minimum CGL coverage amount |
| `tenantInsuranceRequirements.commercialGeneralLiability.namedInsured` | string | Who must be named as additional insured |
| `tenantInsuranceRequirements.propertyInsurance.allRiskCoverage` | number | All-risk property coverage amount |
| `tenantInsuranceRequirements.propertyInsurance.businessInterruption` | number | Business interruption coverage amount |
| `tenantInsuranceRequirements.otherRequiredCoverage` | array[string] | Other insurance coverages tenant must maintain |
| `tenantInsuranceRequirements.certificateRequirements` | string | When/how insurance certificates must be provided |
| `tenantInsuranceRequirements.renewalNotice` | string | Notice requirements for insurance renewal |
| `waiverOfSubrogation.appliesTo` | array[string] | Parties to whom waiver of subrogation applies |
| `indemnification.tenantIndemnifiesLandlordFor` | array[string] | Events for which tenant indemnifies landlord |
| `indemnification.landlordIndemnifiesTenantFor` | array[string] | Events for which landlord indemnifies tenant |
| `indemnification.exceptions` | array[string] | Exceptions to indemnification provisions |

### 12. damageAndDestruction

Casualty provisions.

| Field | Type | Description |
|---|---|---|
| `casualtyProvisions.landlordRepairObligation` | string | Landlord's obligation to repair after damage |
| `casualtyProvisions.timeToRepair` | string | Timeframe for landlord to complete repairs |
| `casualtyProvisions.substantialDamageDefinition` | string | How "substantial damage" is defined |
| `casualtyProvisions.substantialDamageRights` | string | Rights of parties when damage is substantial |
| `rentAbatement.duringRepairs` | string | Rent abatement provisions during repairs |
| `rentAbatement.conditions` | string | Conditions for rent abatement |
| `rentAbatement.tenantAccess` | string | Tenant access provisions during repairs |
| `uninsuredCasualty.landlordObligations` | string | Landlord's obligations for uninsured damage |
| `uninsuredCasualty.terminationRights` | string | Termination rights for uninsured damage |

### 13. assignmentAndSubletting

Transfer and subletting restrictions.

| Field | Type | Description |
|---|---|---|
| `transferRestrictions.assignmentAllowed` | string | Whether and under what conditions assignment is permitted |
| `transferRestrictions.sublettingAllowed` | string | Whether and under what conditions subletting is permitted |
| `transferRestrictions.consentStandard` | string | Standard for landlord consent (e.g., "not to be unreasonably withheld") |
| `landlordRights.recaptureRight` | boolean | Whether landlord has right to recapture space |
| `landlordRights.profitSharing` | number | Percentage of subletting profit shared with landlord |
| `landlordRights.processingFee` | number | Administrative fee for processing transfer requests |
| `permittedTransfers.affiliateTransfers` | string | Rules for transfers to affiliates |
| `permittedTransfers.changeOfControl` | string | Whether change of control triggers consent requirement |
| `permittedTransfers.conditions` | array[string] | Conditions for permitted transfers |
| `transferRequirements.noticePeriod` | string | Required notice period for transfer requests |
| `transferRequirements.informationRequired` | array[string] | Information that must be provided with transfer request |
| `transferRequirements.financialCovenant` | string | Financial requirements for proposed transferee |
| `transferRequirements.ongoingLiability` | string | Whether original tenant remains liable after transfer |

### 14. defaultAndRemedies

Default events and remedial provisions.

| Field | Type | Description |
|---|---|---|
| `eventsOfDefault.nonPayment.gracePeriod` | string | Grace period for non-payment of rent |
| `eventsOfDefault.breachOfCovenants.curePeriod` | string | Cure period for breach of lease covenants |
| `eventsOfDefault.bankruptcyInsolvency` | string | Default triggered by bankruptcy or insolvency |
| `eventsOfDefault.abandonment` | string | Default triggered by abandonment of premises |
| `eventsOfDefault.other` | array[string] | Other events constituting default |
| `landlordRemedies.termination` | string | Landlord's right to terminate upon default |
| `landlordRemedies.reEntry` | string | Landlord's right of re-entry |
| `landlordRemedies.damages` | string | Landlord's right to claim damages |
| `landlordRemedies.distress` | string | Landlord's right of distress (seizure of property) |
| `landlordRemedies.other` | array[string] | Other remedies available to landlord |
| `interestOnLatePayments.rate` | string | Interest rate on overdue payments |
| `interestOnLatePayments.calculationMethod` | string | How interest on late payments is calculated |
| `costs.legalFeesResponsibility` | string | Responsibility for legal fees in default proceedings |
| `costs.collectionCosts` | string | Responsibility for collection costs |

### 15. servicesAndUtilities

Building services and utility arrangements.

| Field | Type | Description |
|---|---|---|
| `utilitiesProvidedByLandlord.electricity` | string | Electricity provisions by landlord |
| `utilitiesProvidedByLandlord.waterSewer` | string | Water/sewer provisions by landlord |
| `utilitiesProvidedByLandlord.gas` | string | Gas provisions by landlord |
| `utilitiesProvidedByLandlord.hvac` | string | HVAC provisions by landlord |
| `utilitiesProvidedByLandlord.other` | array[string] | Other services provided by landlord |
| `utilitiesTenantResponsibility.separatelyMetered` | array[string] | Utilities separately metered to tenant |
| `utilitiesTenantResponsibility.paymentMethod` | string | How tenant pays for separately metered utilities |
| `utilitiesTenantResponsibility.afterHoursHVAC` | string | After-hours HVAC availability and cost |
| `serviceInterruptions.landlordLiability` | string | Landlord's liability for service interruptions |
| `serviceInterruptions.rentAbatement` | string | Rent abatement for prolonged service interruption |
| `serviceInterruptions.forceMajeure` | string | Force majeure provisions for service interruptions |

### 16. environmental

Environmental compliance and remediation.

| Field | Type | Description |
|---|---|---|
| `environmentalCompliance.tenantObligations` | array[string] | Tenant's environmental compliance obligations |
| `environmentalCompliance.hazardousSubstances` | string | Restrictions on hazardous substances |
| `environmentalCompliance.phaseRequirements` | string | Environmental assessment phase requirements |
| `environmentalIndemnity.scope` | string | Scope of environmental indemnification |
| `environmentalIndemnity.survival` | string | Whether environmental indemnity survives lease termination |
| `remediation.responsibility` | string | Responsibility for environmental remediation |
| `remediation.costAllocation` | string | How remediation costs are allocated |
| `remediation.accessForTesting` | string | Access provisions for environmental testing |

### 17. subordinationAndAttornment

Priority and registration provisions.

| Field | Type | Description |
|---|---|---|
| `subordination.leaseSubordinateTo` | string | Instruments to which the lease is subordinate |
| `subordination.sndaRequired` | boolean | Whether an SNDA is required |
| `subordination.sndaProvided` | boolean | Whether an SNDA has been provided |
| `subordination.conditions` | array[string] | Conditions for subordination |
| `registration.leaseRegistration` | string | Whether/how the lease is registered on title |
| `registration.noticeOfLease` | string | Whether a notice or caveat is registered |

### 18. notices

Notice delivery requirements.

| Field | Type | Description |
|---|---|---|
| `noticeRequirements.form` | string | Required form of notice (written, electronic) |
| `noticeRequirements.deliveryMethod` | array[string] | Acceptable delivery methods (personal, registered mail, courier) |
| `noticeRequirements.deemedReceived` | string | When notice is deemed received after sending |
| `noticeAddresses.landlord.address` | string | Landlord's notice address |
| `noticeAddresses.landlord.attention` | string | Attention line for landlord notices |
| `noticeAddresses.landlord.email` | string | Landlord's email for notices (if permitted) |
| `noticeAddresses.tenant.address` | string | Tenant's notice address |
| `noticeAddresses.tenant.attention` | string | Attention line for tenant notices |
| `noticeAddresses.tenant.email` | string | Tenant's email for notices (if permitted) |
| `noticeAddresses.copyTo` | array[string] | Additional parties who receive copies of notices |

### 19. endOfTerm

Lease expiration provisions.

| Field | Type | Description |
|---|---|---|
| `surrenderRequirements.condition` | string | Required condition of premises upon surrender |
| `surrenderRequirements.removalOfImprovements` | array[string] | Improvements tenant must remove |
| `surrenderRequirements.removalOfEquipment` | string | Equipment removal requirements |
| `surrenderRequirements.cleaning` | string | Cleaning requirements upon surrender |
| `overholding.permitted` | boolean | Whether overholding is permitted |
| `overholding.rentDuringOverholding` | string | Rent rate during overholding (e.g., "150% of last month's rent") |
| `overholding.consequences` | string | Other consequences of overholding |
| `finalStatement.reconciliation` | string | Final cost reconciliation provisions |
| `finalStatement.timing` | string | Timing for final statement and reconciliation |

### 20. specialProvisions

Custom terms, typically from Schedule G or equivalent.

| Field | Type | Description |
|---|---|---|
| `customTerms` | array[string] | List of special provisions that modify or supplement the standard lease terms |

Schedule G provisions that contradict main body terms trigger the `schedule_override` SESF rule — the Schedule G value takes precedence and the override must be flagged.

### 21. schedulesAndExhibits

Attached schedules (A through J, or as applicable).

| Field | Type | Description |
|---|---|---|
| `attachedSchedules.schedule{X}.title` | string | Title of the schedule |
| `attachedSchedules.schedule{X}.attached` | boolean | Whether the schedule is attached to the lease |
| `attachedSchedules.schedule{X}.summary` | string | Summary of key contents |
| `keyItemsFromSchedules` | array[string] | Key items extracted from attached schedules |

Standard schedule mapping (varies by lease):

| Schedule | Typical Title |
|---|---|
| A | Legal Description of Project |
| B | Outline Plan of Premises |
| C | Landlord's and Tenant's Work |
| D | Rent Deposit Agreement |
| E | Environmental Questionnaire |
| F | Rules and Regulations |
| G | Special Provisions |
| H | Indemnity Agreement |
| I | Pre-Authorized Debit (PAD) Authorization |
| J | Letter of Credit Agreement |

### 22. criticalDatesSummary

*Derived section* — compiled from extracted dates across all sections.

| Field | Type | Description |
|---|---|---|
| `criticalDates[].event` | string | Description of the date event |
| `criticalDates[].date` | string (ISO 8601) | The date |
| `criticalDates[].noticeRequired` | string | Notice requirements associated with this date |
| `criticalDates[].actionRequired` | string | Action required by this date |

Standard events include: Lease Commencement, First Rent Payment, Renewal Option Notice, Lease Expiry. Additional events are derived from the lease.

### 23. financialObligationsSummary

*Derived section* — calculated from extracted financial data.

| Field | Type | Description |
|---|---|---|
| `initialCosts.firstMonthRent` | number | First month's rent payment |
| `initialCosts.rentDeposit` | number | Required rent deposit |
| `initialCosts.letterOfCredit` | number | Letter of credit amount |
| `initialCosts.other` | number | Other initial costs |
| `initialCosts.total` | number | Total initial costs |
| `ongoingMonthlyCosts.basicRent` | number | Monthly base rent |
| `ongoingMonthlyCosts.operatingCosts` | number | Monthly operating cost share |
| `ongoingMonthlyCosts.realtyTaxes` | number | Monthly realty tax share |
| `ongoingMonthlyCosts.managementFee` | number | Monthly management fee |
| `ongoingMonthlyCosts.utilities` | number | Monthly utility costs |
| `ongoingMonthlyCosts.estimatedTotal` | number | Estimated total monthly cost |

### 24. keyIssuesAndRisks

*Derived section* — analytical assessment of the lease terms.

| Field | Type | Description |
|---|---|---|
| `favorableTerms` | array[string] | Terms that are favorable to the tenant |
| `unfavorableTermsRisks` | array[string] | Terms that are unfavorable or create risk for the tenant |
| `itemsRequiringFurtherReview` | array[string] | Items that require legal or business review |

For markdown output: limit to top 5 critical red flags, top 5-7 favorable, top 5-7 unfavorable, top 10 review items.

---

## Field Status Tracking

Every field in this DDD, when extracted, MUST carry a status indicator:

| Status | Meaning | Required Metadata |
|---|---|---|
| `FACT` | Value found verbatim in source document | `provenance` (page, clause, verbatim quote) |
| `INFERENCE` | Value derived or interpreted from source | `confidence` (0.0-1.0), `reasoning` |
| `MISSING` | Field not found in source document | value = `null` (JSON) or `"Not specified"` (markdown) |
| `CONFLICT` | Multiple conflicting values found | All values with individual `provenance`, `reasoning` |

## Data Types

| Type | JSON Representation | Notes |
|---|---|---|
| `string` | `"value"` | Text values |
| `string (ISO 8601)` | `"YYYY-MM-DD"` | All dates normalized to ISO 8601 |
| `number` | `45.00` | Numeric values without currency symbols |
| `boolean` | `true` / `false` | Yes/no values |
| `array[string]` | `["item1", "item2"]` | Lists |
| `null` | `null` | Missing or absent values |

## Versioning

This DDD follows semantic versioning:
- **Patch** (1.0.x): Field description clarifications, no schema changes
- **Minor** (1.x.0): New optional fields added, no existing fields removed
- **Major** (x.0.0): Breaking changes — fields renamed, removed, or restructured
