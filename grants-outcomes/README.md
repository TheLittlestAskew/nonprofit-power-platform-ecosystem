# Outcomes, Grants & Compliance

The flagship module of this case study. It documents how the environment turns
**funder requirements** into **measured impact** and **audit-ready compliance
reporting**, using a combination of Microsoft Nonprofit Accelerator impact
entities and custom `tr_` tables.

> **Internal origin:** In the model-driven application, this work lives in the
> area originally named **"Tracking."** See
> [`../dataverse/application-sitemap.md`](../dataverse/application-sitemap.md)
> for the full area → group → entity structure.

## What This Area Supported

The Tracking area was built to support the full grant-outcomes cycle:

- **Impact-number collection** — capturing the counts and values that describe
  what programs delivered.
- **Grant KPI tracking** — recording performance against funder-defined key
  performance indicators.
- **Outcome measurement** — measuring change, not just activity.
- **Grant compliance** — keeping deliverables, awards, and disbursements
  aligned with funder terms.
- **Reporting preparation** — assembling the data behind each report.
- **Mid-year and final reporting** — producing periodic and closeout reports.
- **Audit-ready documentation** — retaining a traceable record from funder
  requirement through to reported result.

## The Lifecycle

```text
FUNDER REQUIREMENTS
        ↓
PROGRAM DELIVERABLES
        ↓
KPIs AND MEASURES
        ↓
DATAVERSE RECORDS
        ↓
IMPACT ANALYSIS
        ↓
COMPLIANCE REPORTING
```

Full walkthrough: [`grant-lifecycle.md`](grant-lifecycle.md).

## Files in This Module

| File | What it covers | Evidence tier |
|---|---|---|
| [`grant-lifecycle.md`](grant-lifecycle.md) | End-to-end lifecycle, stage by stage | Reconstructed from verified structure |
| [`measurement-model.md`](measurement-model.md) | How theory-of-change, indicators, and measures are modeled | Reconstructed from verified structure |
| [`reporting-workflow.md`](reporting-workflow.md) | How reports are prepared and produced | Reconstructed / working interpretation |
| [`data-dictionary.csv`](data-dictionary.csv) | Fields of the key measurement entities | Reconstructed |
| [`sample-records.json`](sample-records.json) | **Fictional** sample records illustrating structure | Invented sample |

## How This Was Built (Data Basis)

The **Tracking** area surfaces these entities (verified from the sitemap
source):

- **Mission group** (impact measurement): `msnfp_theoryofchange`,
  `msnfp_objective`, `msnfp_deliveryframework`, `msnfp_indicator`,
  `msnfp_indicatorvalue`, `msnfp_result`, `msnfp_operation`,
  `msnfp_programitem`, `msnfp_assessment`, `msnfp_workitem`.
- **Grant Management group**: `msnfp_award`, `msnfp_disbursement`, `msnfp_item`,
  `msnfp_measurementitem`, `msnfp_report`, plus standard `report` and `account`,
  and custom `tr_goals`.
- **Programs group** (custom): `tr_adminreporting`, `tr_counselingreporting`,
  `tr_busfare`, `tr_farmbus`.
- **Surveys group** (custom): `tr_intakesurvey`, `tr_exitsurvey`,
  `tr_followupsurvey`, `tr_casemeetingsurveys`, `tr_surveylinks`.

The `msnfp_*` entities are Microsoft **Nonprofit Accelerator** tables; the
`tr_*` entities are **custom** tables built for this environment.

## ⚠️ Pending Verification

Specific counts of **KPIs** and **measures** (for example a "nine KPIs" or
"twenty measures" figure) are **not verified**. No source file available to this
build enumerates them; the indicator and measure definitions live in
`msnfp_indicator` / `msnfp_measurementitem`, for which no data export was
available. These counts are **pending verification** and must not be stated as
fact until grounded in a source. See
[`../docs/evidence-register.md`](../docs/evidence-register.md).

## Out of Scope (for now)

Public resource-directory records (`tr_resourcecollection`, `tr_commongoals`)
are **not** published here. Even where the underlying information may be public,
it requires a separate review first.
