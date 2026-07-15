# Development Finance & Revenue

How donation and payment-processor data became reliable donor records, financial
transactions, bank deposits, and audit-ready fundraising reporting.

> **Internal origin:** In the model-driven application this work lives in the
> area originally named **Finance Management**. See
> [`../dataverse/application-sitemap.md`](../dataverse/application-sitemap.md).

This module documents a **Stripe → Dataverse reconciliation** workflow: it
retrieved charges and payouts from the Stripe REST API, normalized payment data,
matched transactions to donor records, created linked financial records in
Dataverse, and supported bank reconciliation and revenue reporting.

## Evidence model (read this first)

This module follows the repository's factuality rules
([`../AGENTS.md`](../AGENTS.md)). Claims are labeled by how they are supported.

**Portfolio-documented operational results** — recorded in surviving portfolio
materials; presented as documented, **not** independently audited, reproduced, or
recalculated here:

- **483+** Stripe-related payment records
- **89.7%** automatic match rate
- a **four-tier** customer-matching process

**Directly corroborated** by the surviving private source structure:

- a **separate** surviving sample of **74 Stripe charge objects**
- embedded balance-transaction structure (gross, fee, net)
- billing, customer, metadata, and fee/net fields

**Reconstructed implementation** (from surviving technical notes and source
structure — reconstructed architecture, not directly observed production
behavior):

- charge and payout API retrieval; incremental watermark state
- pagination and date-window controls; balance-transaction normalization
- payout-to-Deposit creation; charge-to-Transaction creation
- donor matching inputs; transaction-to-deposit linking
- duplicate prevention; concurrency controls

**Not preserved** (absent from every available source; recorded as *not
preserved*, not as pending verification):

- the exact four-tier sequence and thresholds
- the exact Dataverse query filters
- the numerator and denominator behind the 89.7% figure
- the exact object-type composition of the 483+ total
- the final production Power Automate export

> The **74**-charge sample is a **separate** surviving export. It is **not** a
> known subset of the 483+ total, **not** the denominator behind 89.7%, and
> **not** the complete migration population. It supports schema documentation
> only.

## Files in this module

| File | What it covers | Evidence tier |
|---|---|---|
| [`reconciliation-lifecycle.md`](reconciliation-lifecycle.md) | Payout→Deposit, charge→Transaction, linking, reconciliation | Reconstructed |
| [`matching-model.md`](matching-model.md) | The documented four-tier matching (inputs corroborated; order not preserved) | Portfolio-documented + reconstructed |
| [`exception-handling.md`](exception-handling.md) | How records leave the automatic path | Reconstructed |
| [`revenue-engine.md`](revenue-engine.md) | The annual-giving operating model | Reconstructed from portfolio |
| [`data-dictionary.csv`](data-dictionary.csv) | Stripe source fields + generalized Dataverse concepts, with privacy category | Reconstructed |
| [`sample-records.json`](sample-records.json) | **Fictional** reconciliation sample records | Invented sample |
| [`privacy-controls.md`](privacy-controls.md) | How processor data is handled without leakage | Reference |

Recruiter-facing narrative:
[`../portfolio/stripe-dataverse-website-case-study.md`](../portfolio/stripe-dataverse-website-case-study.md).
Architecture diagram:
[`../architecture/development-finance-lifecycle.md`](../architecture/development-finance-lifecycle.md).

## Reproducible tooling

- `../scripts/inspect_stripe_schema.py` — reads the private Stripe sample and
  reports **sanitized structure only**: dotted field paths (including nested
  objects and list items), privacy category, observed JSON types, presence %, and
  aggregate record/object-type counts. **No production record value is published**
  — it never prints or writes a field value.
- `../scripts/validate_finance_samples.py` — validates that
  `sample-records.json` stays fictional and complete.

Both are covered by unit tests in [`../tests/`](../tests/).

## Privacy boundary

The raw Stripe export and the detailed reconstruction notes live under
`source-private/` and are **never** committed. Only sanitized schema, generalized
architecture, and invented samples appear here. See
[`privacy-controls.md`](privacy-controls.md) and [`../SECURITY.md`](../SECURITY.md).
