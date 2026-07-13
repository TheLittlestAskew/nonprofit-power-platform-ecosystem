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

The internal application area called **Tracking** was built to support the full
grant-outcomes cycle:

- **Impact-number collection** — capturing the counts and values that describe
  what programs delivered.
- **Grant KPI tracking** — recording performance against funder-defined key
  performance indicators.
- **Outcome measurement** — measuring change, not just activity.
- **Compliance monitoring** — keeping deliverables, awards, and disbursements
  aligned with funder terms.
- **Reporting preparation** — assembling the data behind each report.
- **Interim and final reports** — producing periodic and closeout reports on the
  funder's required cadence.
- **Audit-ready supporting documentation** — retaining a traceable record from
  funder requirement through to reported result.

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

## Verified Grant Measurement Counts

Grounded in two private grant sources (see
[`../docs/evidence-register.md`](../docs/evidence-register.md), Sources 6 and 7):

> The grant measurement matrix defined nine headline KPI targets and 19
> supporting measurement and implementation items across case management and
> counseling. A curated reporting framework translated that work into 20 tracked
> measures. The related 2026 proposal identified 23 measurable objectives and
> established interim and final reporting requirements.

Keep these three figures **distinct** — they describe different things and are
**not** additive:

| Figure | What it counts | Source |
|---|---|---|
| **9** headline KPI targets | Target-based KPIs (e.g., 70% to permanent housing, 28 weekly CM sessions) | Grant KPIs & Metrics matrix (verified) |
| **19** supporting items | Additional outcome concepts, implementation notes, and open measurement-design questions | Grant KPIs & Metrics matrix (verified) |
| **20** tracked measures | A curated reporting framework derived from the nine KPIs — *not* the raw matrix row count | Portfolio reporting framework (curated) |
| **23** measurable objectives | Objectives listed in the 2026 grant proposal | Grantee Portal proposal (verified) |

Still **pending verification:** the live record-level counts of
`msnfp_indicator` and `msnfp_measurementitem` in Dataverse — no source in this
build enumerates the deployed indicator/measure *rows*. The figures above verify
the grant measurement **design**, not the count of configured Dataverse records.

## Out of Scope (for now)

Public resource-directory records (`tr_resourcecollection`, `tr_commongoals`)
are **not** published here. Even where the underlying information may be public,
it requires a separate review first.
