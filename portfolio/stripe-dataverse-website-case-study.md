---
title: "Stripe → Dataverse Reconciliation"
kicker: "Development Finance & Revenue"
subtitle: "Building a repeatable payment-processing workflow from API ingestion through donor matching, deposit reconciliation, and reporting"
role: "Sole systems developer and development operations administrator"
tools:
  - Microsoft Power Automate
  - Microsoft Dataverse
  - Stripe REST API
  - Model-driven Power Apps
  - Power BI
status: "Sanitized reconstruction from surviving technical notes, source structure, and portfolio documentation"
metrics:
  - label: "Portfolio-documented Stripe-related records"
    value: "483+"
  - label: "Portfolio-documented automatic match rate"
    value: "89.7%"
  - label: "Portfolio-documented customer-matching process"
    value: "4 tiers"
  - label: "Separate surviving source sample"
    value: "74 charges"
---

# Stripe → Dataverse Reconciliation

Payment processing was only the first step. The real operational challenge was turning processor data into reliable donor records, financial transactions, bank deposits, acknowledgments, and fundraising reports.

I designed a repeatable Stripe-to-Dataverse workflow that retrieved new charges and payouts through the Stripe REST API, normalized payment data, matched transactions to donor records, created linked financial records in Dataverse, and supported bank reconciliation and revenue reporting.

> **Documented result:** Portfolio materials record **483+ Stripe-related payment records**, a **four-tier customer-matching process**, and an **89.7% automatic match rate**. The surviving private source sample contains 74 Stripe charge objects and supports the architecture and field model, but it is not the complete historical migration dataset.

## The problem

Stripe, donor records, bank deposits, and fundraising reporting represented different parts of the same transaction lifecycle, but they did not automatically function as one system.

The workflow needed to answer several questions consistently:

- Which Stripe records were new?
- Which donor or household did each payment belong to?
- Had the transaction already been imported?
- Which payout and bank deposit should the payment reconcile against?
- What gross, fee, and net values should be recorded?
- Which records required human review?
- How would the resulting data support acknowledgments and reporting?

A one-time spreadsheet import would not solve those problems. The system needed to become an incremental, repeatable synchronization process.

## System architecture

The following describes the sanitized reconstruction of the production workflow based on surviving technical notes, source structure, implementation details, and portfolio documentation.

```text
STRIPE CHARGES + PAYOUTS
        ↓
INCREMENTAL API RETRIEVAL
        ↓
WATERMARK + PAGINATION CONTROL
        ↓
BALANCE-TRANSACTION NORMALIZATION
        ↓
DONOR / CUSTOMER MATCHING
        ↓
DATAVERSE TRANSACTION CREATION
        ↓
PAYOUT-BASED DEPOSIT CREATION
        ↓
TRANSACTION-TO-DEPOSIT LINKING
        ↓
EXCEPTION REVIEW
        ↓
BANK RECONCILIATION
        ↓
ACKNOWLEDGMENT + FUNDRAISING REPORTING
```

## 1. Incremental retrieval from Stripe

Power Automate called the Stripe REST API for both charges and payouts.

The charge request used a structure resembling:

```text
/v1/charges
?limit=100
&created[gte]=<unix timestamp>
&created[lte]=<unix timestamp>
&starting_after=<last charge id>
&expand[]=data.balance_transaction
```

This design supported:

- date-bounded migration windows
- Stripe pagination
- incremental daily synchronization
- embedded balance-transaction details
- fee and net-value calculation without a second API call

The `limit=100` parameter represented a maximum page size, not a guarantee that every page contained exactly 100 records.

## 2. Watermark-based synchronization

A dedicated control record stored the last processed charge and payout state.

The watermark tracked generalized values such as:

| Control value | Purpose |
|---|---|
| Last processed charge date | Defines the next charge retrieval window |
| Last charge cursor or timestamp | Supports pagination and incremental state |
| Last processed payout date | Defines the next payout retrieval window |
| Last payout cursor or timestamp | Prevents historical rereads |

This shifted the solution from a historical backfill into an ongoing synchronization process.

Watermark updates remained sequential so the flow could not advance its state before all records in a page or date window had been handled successfully.

## 3. Payouts became Dataverse deposits

Stripe payouts represented the bank-level settlement layer.

For each payout, the workflow:

1. retrieved the payout record
2. converted Stripe Unix dates into Dataverse-ready dates
3. found or created the corresponding Deposit record
4. stored the processor payout reference
5. captured the expected bank-arrival date
6. retained the Dataverse Deposit identifier for transaction linking

A null-safe arrival-date conversion followed this pattern:

```text
if arrival_date is empty:
    return null
else:
    convert Unix seconds to yyyy-MM-dd
```

Null handling mattered because a payout's arrival date could be unavailable before Stripe finalized the settlement.

## 4. Charges became Dataverse transactions

Each Stripe charge was transformed into a Dataverse Transaction record.

The normalized transaction model included concepts such as:

| Transaction concept | Source |
|---|---|
| Processor charge reference | Stripe charge |
| Related payout reference | Stripe settlement data |
| Transaction or book date | Charge or balance transaction |
| Expected deposit date | Related payout |
| Donor or payer name | Billing details |
| Gross amount | Expanded balance transaction |
| Processing fee | Expanded balance transaction |
| Net amount | Expanded balance transaction |
| Payment method | Charge payment data |
| Receipt reference | Stripe receipt data |
| Form or campaign source | Stripe metadata |
| Recurring-payment indicator | Payment or metadata context |

The surviving source sample confirms that the charge records included embedded balance-transaction data, including gross, fee, and net fields.

## 5. Donor-identification data was normalized

Payment data often contained incomplete or inconsistent contact information.

The workflow created a normalized email value using:

1. billing email
2. receipt email as fallback
3. an empty string as the final null-safe fallback
4. trimming and lowercasing before search

Conceptually:

```text
normalized_email =
    lowercase(
        trim(
            billing_email
            ?? receipt_email
            ?? ""
        )
    )
```

The final empty-string fallback prevented `trim()` from receiving a null value and failing the flow.

## 6. Four-tier customer matching

Portfolio materials document a four-tier customer-matching process.

The exact historical tier order was not preserved, but the surviving implementation evidence identifies the matching inputs:

- existing processor-customer relationships
- normalized billing or receipt email
- billing name and identity information
- invoice and form metadata
- existing Dataverse Contact records
- controlled manual review or new-contact creation

These inputs allowed the system to resolve most payments automatically while preserving an exception path for ambiguous or incomplete records.

> The four-tier process is documented, but its final production ordering and thresholds are no longer available. This case study does not invent those missing details.

## 7. Transactions were linked to deposits

The reconciliation model depended on connecting each imported transaction to the Dataverse Deposit representing its Stripe payout.

```text
Stripe payout
    ↓
Dataverse Deposit
    ↓
Stripe charges included in that settlement
    ↓
Dataverse Transactions linked to the Deposit
```

The Dataverse lookup required the Deposit record's Dataverse identifier, not the Stripe payout string.

Conceptually:

```text
if Deposit ID is empty:
    lookup = null
else:
    lookup = Dataverse Deposit reference
```

That relationship made it possible to compare processor settlement, bank deposit, and CRM transaction records as one reconciliation chain.

## 8. Duplicate prevention and idempotency

The workflow used two complementary controls.

### Watermarks

Date and cursor state limited API requests to newer records.

### Processor identifiers

Unique Stripe references allowed the flow to determine whether a Dataverse record had already been created.

The generalized logic was:

```text
search for existing transaction by processor identifier

if found:
    update or skip
else:
    create transaction
```

Together, these controls reduced duplicate creation during retries, reruns, and incremental synchronization.

## 9. Concurrency was controlled deliberately

Not every part of the process was safe to parallelize.

Sequential execution was important for:

- Stripe pagination
- watermark updates
- payout and Deposit creation
- shared Deposit identifiers
- donor or Contact creation
- duplicate checks

Independent charge transformations could potentially run in parallel only after the correct Deposit had been resolved and without relying on shared mutable variables.

The broader design rule was simple:

> Parallelize isolated transformations, not shared state.

## Exception handling

Records could leave the automatic path for several reasons:

- no matching donor found
- multiple possible donor matches
- missing contact information
- missing payout or Deposit relationship
- duplicate processor identifier
- incomplete or invalid source data
- contact creation requiring review
- reconciliation mismatch

The public case study represents these exceptions with fictional sample records rather than former-employer production data.

## Outcome

The integration connected what had previously been separate operational stages:

```text
Campaign
→ Gift received
→ Donor matched or created
→ Transaction recorded
→ Financial reconciliation
→ Acknowledgment
→ Stewardship and reporting
```

It created a repeatable foundation for:

- cleaner donor records
- less manual reconciliation
- more consistent transaction history
- payout-to-bank visibility
- faster acknowledgments
- more reliable fundraising reporting

## What this demonstrates

- Power Automate orchestration
- Stripe REST API integration
- pagination and incremental synchronization
- watermark-based state management
- Dataverse relationship design
- data normalization and null-safe expressions
- multi-signal record matching
- idempotency and duplicate prevention
- concurrency control
- finance and donor-operations integration
- privacy-conscious public documentation

## Evidence and limitations

This case study is a sanitized reconstruction, not a production export or financial audit.

### Documented operational results

- 483+ Stripe-related payment records
- four-tier customer-matching process
- 89.7% automatic match rate

### Directly corroborated by surviving source structure

- 74 Stripe charge objects
- expanded balance-transaction data
- billing, customer, metadata, fee, and net-value fields
- charge-oriented source schema

### Reconstructed from surviving technical notes

- charge and payout API retrieval
- watermark design
- payout-to-Deposit creation
- charge-to-Transaction transformation
- email normalization
- Deposit lookup binding
- duplicate prevention
- concurrency strategy

### Not preserved

- exact four-tier order and thresholds
- exact Dataverse query filters
- numerator and denominator behind 89.7%
- exact object-type composition of the 483+ historical total
- final production Power Automate export
