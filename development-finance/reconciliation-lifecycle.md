# Reconciliation Lifecycle

How a Stripe payment became a reconciled Dataverse record — from API retrieval
through donor matching, deposit creation, and bank reconciliation.

> **Evidence tier:** Reconstructed. This describes the sanitized reconstruction
> of the production workflow based on surviving technical notes, source
> structure, and portfolio documentation. It is reconstructed architecture, not
> a directly observed production export.

## Object model

The workflow moved between two systems and kept their object types distinct:

| Stripe object | Becomes in Dataverse | Represents |
|---|---|---|
| **Payout** | **Deposit** | the bank-level settlement of many payments |
| **Charge** | **Transaction** | a single donor payment |
| Charge's embedded **balance transaction** | gross / fee / net on the Transaction | the money math for that charge |

A payout settles many charges. So one **Deposit** links to many **Transactions**,
and the reconciliation chain is:

```text
Stripe payout  ->  Dataverse Deposit
                        |
        Stripe charges settled in that payout
                        |
                Dataverse Transactions linked to the Deposit
```

Charges, balance transactions, payouts, bank deposits, and Dataverse Transactions
are **not** interchangeable; each stage converts one into the next.

## Stage 1 — Incremental retrieval

Power Automate called the Stripe REST API for **both** charges and payouts. The
charge request was date-bounded and paginated, and expanded the balance
transaction so fee and net values arrived without a second call:

```text
GET /v1/charges
    ?limit=<page size>
    &created[gte]=<window start, unix>
    &created[lte]=<window end, unix>
    &starting_after=<last charge cursor>
    &expand[]=data.balance_transaction
```

`limit` is a **maximum** page size, not a guarantee of a full page. Pagination
continued until the response reported no more records.

## Stage 2 — Watermark state

A dedicated control record stored the last processed charge and payout state, so
each run retrieved only newer records instead of re-reading history:

| Control value (generalized) | Purpose |
|---|---|
| Last processed charge date | Defines the next charge window |
| Last charge cursor/timestamp | Incremental pagination state |
| Last processed payout date | Defines the next payout window |
| Last payout cursor/timestamp | Prevents historical re-reads |

Watermark updates stayed **sequential** — state could not advance before every
record in a page or window had been handled. This turned a one-time backfill into
an ongoing synchronization.

## Stage 3 — Payouts become Deposits

For each payout the workflow found or created the corresponding **Deposit**,
stored the processor payout reference, captured the expected bank-arrival date,
and retained the Deposit's Dataverse identifier for linking. Arrival-date
conversion was null-safe:

```text
if arrival_date is empty:
    deposit_arrival = null
else:
    deposit_arrival = unix_to_date(arrival_date)   # yyyy-MM-dd
```

Null handling mattered because a payout's arrival date could be unavailable until
Stripe finalized the settlement.

## Stage 4 — Charges become Transactions

Each charge became a **Transaction**, drawing gross/fee/net from the expanded
balance transaction:

| Transaction concept | Source |
|---|---|
| Processor charge reference | Stripe charge |
| Related payout reference | Stripe settlement data |
| Book date | Charge / balance transaction |
| Expected deposit date | Related payout |
| Donor (matched) | Billing details → matching |
| Gross / Fee / Net | Expanded balance transaction |
| Payment method | Charge payment data (card detail withheld) |
| Campaign source | Processor metadata |
| Recurring indicator | Payment/metadata context |

The surviving 74-charge sample **corroborates** that charges carried embedded
balance-transaction data (gross, fee, net).

## Stage 5 — Link transactions to deposits

Each Transaction bound to the Deposit representing its payout. The Dataverse
lookup required the **Deposit's Dataverse identifier**, not the Stripe payout
string:

```text
if deposit_id is empty:
    transaction.deposit_lookup = null
else:
    transaction.deposit_lookup = <Dataverse Deposit reference>
```

That relationship let processor settlement, bank deposit, and CRM transaction be
compared as one reconciliation chain.

## Stage 6 — Reconciliation and reporting

With Transactions linked to Deposits, the system could reconcile processor
settlement against bank deposits and feed acknowledgments and fundraising
reporting. This aligns with the documented annual-giving lifecycle:

```text
Campaign -> Gift received -> Donor matched/created -> Transaction recorded
        -> Financial reconciliation -> Acknowledgment -> Stewardship & reporting
```

## Related

- Matching detail: [`matching-model.md`](matching-model.md)
- Exceptions: [`exception-handling.md`](exception-handling.md)
- Diagram: [`../architecture/development-finance-lifecycle.md`](../architecture/development-finance-lifecycle.md)
