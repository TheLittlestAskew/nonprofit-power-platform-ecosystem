# Measurement Model

How the environment models impact — from a theory of change down to a single
recorded value — using Microsoft Nonprofit Accelerator entities combined with
custom survey and goal tables.

> **Evidence tier:** Reconstructed. The entities and their presence in the
> Tracking area are **verified** from the sitemap source. How they are wired
> together is a **working interpretation** based on the Nonprofit Accelerator's
> standard impact-tracking model. The grant measurement **design counts** (9
> headline KPI targets, 19 supporting items, 20 curated measures, 23 proposal
> objectives) are now **verified** from two grant sources; the live Dataverse
> `msnfp_indicator` / `msnfp_measurementitem` record counts remain **pending
> verification.**

## The Entity Backbone

The Accelerator's impact model is a hierarchy from strategy to data point:

```text
msnfp_theoryofchange      "The change we intend to create"
        ↓
msnfp_objective           "A specific objective within that theory"
        ↓
msnfp_deliveryframework   "The framework of programs that deliver it"
        ↓
msnfp_programitem         "A program / service line"
        ↓
msnfp_indicator           "A KPI: what we measure to know if it's working"
        ↓
msnfp_indicatorvalue      "A recorded value for that indicator"
        ↓
msnfp_result              "An analyzed result / outcome"
```

Supporting entities:

| Entity | Role |
|---|---|
| `msnfp_measurementitem` | A specific measure definition attached to indicators |
| `msnfp_assessment` | Structured assessment instrument (e.g., standardized screens) |
| `msnfp_operation` | Operational unit of delivery |
| `msnfp_workitem` | A tracked unit of work that generates measurable records |
| `tr_goals` | Custom goal records (client/program goals) that feed outcome measures |

## Outputs vs. Outcomes

A credible measurement model separates the two:

- **Outputs** — what the program did (sessions held, supports provided). These
  come largely from `msnfp_workitem`, `msnfp_programitem`, and operational
  records elsewhere in the environment.
- **Outcomes** — what changed for people (housing stability, income, wellbeing).
  These come from `msnfp_result`, `msnfp_assessment`, `tr_goals` progress, and
  the survey instruments below.

Funders increasingly ask for outcomes, not just outputs. Modeling both — and
linking each to a `msnfp_indicator` — is what lets the same system answer both
"what did you do?" and "what difference did it make?"

## Survey Instruments (custom)

Measures are fed by custom survey tables that capture change at key moments in
the guest journey:

| Survey table | Captured at | Feeds |
|---|---|---|
| `tr_intakesurvey` | Program entry (baseline) | Baseline measures |
| `tr_casemeetingsurveys` | During case meetings | Progress measures |
| `tr_exitsurvey` | Program exit | Outcome measures |
| `tr_followupsurvey` | Post-exit follow-up | Durability of outcomes |
| `tr_surveylinks` | (linking/util) | Connects surveys to records |

The intake → exit → follow-up sequence is what enables **change over time**
measurement rather than a single snapshot.

## Traceability Rule

Every measure should resolve to:

1. a **funder requirement** (via `msnfp_award` / `msnfp_objective`),
2. an **indicator definition** (`msnfp_indicator` / `msnfp_measurementitem`), and
3. the **records** it is computed from (`msnfp_indicatorvalue`, `msnfp_result`,
   survey and operational tables).

If a measure can't complete that chain, it isn't audit-ready.

## The Grant Measurement Matrix (verified)

The design behind the indicators and measures is now grounded in two private
grant sources (see [`../docs/evidence-register.md`](../docs/evidence-register.md),
Sources 6 and 7):

> The grant measurement matrix defined nine headline KPI targets and 19
> supporting measurement and implementation items across case management and
> counseling. A curated reporting framework translated that work into 20 tracked
> measures. The related 2026 proposal identified 23 measurable objectives and
> established interim and final reporting requirements.

These figures count **different things** and are **not** additive:

- **9 headline KPI targets** — target-based KPIs (percentages and weekly session
  counts) split across case management and counseling.
- **19 supporting measurement and implementation items** — additional outcome
  concepts, implementation notes, and unresolved measurement-design questions.
  Not all 19 are finalized KPIs; several are open design questions.
- **20 tracked measures** — a curated reporting framework built on the nine
  headline KPIs. This is a *designed* framework, not the raw matrix row count.
- **23 measurable objectives** — listed in the 2026 grant proposal.

## ⚠️ Still Pending Verification

- **Deployed indicator/measure record counts:** the number of `msnfp_indicator`
  and `msnfp_measurementitem` **records configured in Dataverse** is still not
  enumerated by any source in this build. The verified figures above describe the
  grant measurement *design*, not the count of live Dataverse rows.

See [`../docs/evidence-register.md`](../docs/evidence-register.md).
