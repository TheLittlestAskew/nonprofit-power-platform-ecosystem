# Grant Lifecycle

How a funder requirement becomes a reported, audit-ready outcome. Each stage
below names the Dataverse entities that carry the data, so the lifecycle maps
onto the real model, not an abstraction.

> **Evidence tier:** Reconstructed from verified sitemap structure (the
> Tracking area). Entity names are verified; the stage-to-entity narrative is a
> working interpretation of how they fit together.

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

## Stage 1 — Funder Requirements

A grant agreement defines what the funder expects: the population served, the
activities funded, the outcomes promised, and the reporting cadence.

- **Where it lands:** the award and its terms are represented by
  `msnfp_award` (grant), related `account` (funder), and the theory-of-change
  scaffolding in `msnfp_theoryofchange` and `msnfp_objective`.
- **Why it matters:** every downstream measure should trace back to a specific
  funder requirement. If it doesn't, it's activity without accountability.
- **Verified worked example (2026 proposal):** one related 2026 foundation
  proposal **requested $100,000** (a request, *not* an awarded amount), proposed
  serving **150** individuals, listed **23 measurable objectives**, and
  established **interim** (due December 31, 2026) and **final** (due within 30
  days of the 12-month grant period) reporting requirements. Dollar figures are
  grant-specific: this $100,000 request must not be conflated with amounts from
  other grants or reporting artifacts.

## Stage 2 — Program Deliverables

Requirements are decomposed into what programs will actually deliver — the
services, sessions, and supports that produce the promised outcomes.

- **Where it lands:** `msnfp_deliveryframework`, `msnfp_programitem`,
  `msnfp_operation`, and program-specific custom tables in the Programs group
  (`tr_counselingreporting`, `tr_adminreporting`, `tr_busfare`, `tr_farmbus`).
- **Design note:** deliverables are the bridge between funder language and
  operational reality — they translate "reduce housing instability" into
  "N counseling sessions" or "N transportation supports."

## Stage 3 — KPIs and Measures

Each deliverable gets the indicators and measures that quantify success —
both **outputs** (what was done) and **outcomes** (what changed).

- **Where it lands:** `msnfp_indicator` (the KPI definition),
  `msnfp_measurementitem` (the specific measure), and `msnfp_assessment`
  (structured assessment instruments). Survey instruments feed measures from
  `tr_intakesurvey`, `tr_exitsurvey`, `tr_followupsurvey`, and
  `tr_casemeetingsurveys`.
- **Verified design counts:** the grant measurement matrix defined **9 headline
  KPI targets** and **19 supporting measurement and implementation items** across
  case management and counseling; a curated reporting framework translated that
  work into **20 tracked measures**. These count different things and are **not**
  additive. See [`measurement-model.md`](measurement-model.md).
- ⚠️ **Still pending verification:** the number of `msnfp_indicator` /
  `msnfp_measurementitem` **records deployed in Dataverse** is not enumerated by
  any available source; the counts above describe the measurement *design*, not
  live record totals.

## Stage 4 — Dataverse Records

Live operational work generates the records that measures are calculated from.
This is where the grants area connects to the rest of the environment.

- **Where it lands:** `msnfp_indicatorvalue` (recorded indicator values),
  `msnfp_result` (results), `msnfp_workitem` (units of tracked work), and
  `tr_goals` (goal progress). Operational source data flows in from Shelter &
  Case Management (case meetings, phases, discharge) and other areas.
- **Design note:** because measures read from live records rather than
  re-entered summaries, the numbers stay consistent between operations and
  reporting.

## Stage 5 — Impact Analysis

Records are aggregated and analyzed into the impact story: how many people were
served, what changed, and how results compare to targets.

- **Where it lands:** `msnfp_result`, `msnfp_assessment`, and reporting
  aggregates surfaced through `report` / dashboards.
- **Analytical questions:** Are we on pace against target? Which programs move
  which outcomes? What does the intake-to-exit change look like?

## Stage 6 — Compliance Reporting

Analysis is packaged into the funder's required format on the required cadence,
with a traceable link back to the underlying records.

- **Where it lands:** `msnfp_report` and standard `report`, backed by
  `msnfp_award` / `msnfp_disbursement` for the financial side, and
  `tr_adminreporting` / `tr_counselingreporting` for program reporting.
- **Cadence:** mid-year and final reports, plus audit-ready documentation that
  preserves the chain from funder requirement to reported result.

## The Compliance Chain (why traceability matters)

```text
msnfp_award  →  msnfp_objective  →  msnfp_indicator  →  msnfp_indicatorvalue
   (grant)        (what we promised)   (how we measure)     (what we recorded)
                                                                   ↓
                                                            msnfp_result
                                                                   ↓
                                                     msnfp_report / report
```

Every reported number should be able to walk backward along this chain to the
records that produced it. That is what makes the reporting **audit-ready**.

## Related

- Measurement detail: [`measurement-model.md`](measurement-model.md)
- Reporting mechanics: [`reporting-workflow.md`](reporting-workflow.md)
- Diagram: [`../architecture/grant-reporting-lifecycle.md`](../architecture/grant-reporting-lifecycle.md)
