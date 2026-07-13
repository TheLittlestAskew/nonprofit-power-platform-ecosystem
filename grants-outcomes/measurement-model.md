# Measurement Model

How the environment models impact — from a theory of change down to a single
recorded value — using Microsoft Nonprofit Accelerator entities combined with
custom survey and goal tables.

> **Evidence tier:** Reconstructed. The entities and their presence in the
> Tracking area are **verified** from the sitemap source. How they are wired
> together is a **working interpretation** based on the Nonprofit Accelerator's
> standard impact-tracking model. Specific counts (KPIs, measures) are
> **pending verification.**

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

## ⚠️ Pending Verification

- **Number of KPIs / indicators:** pending verification (no source enumerates
  `msnfp_indicator` records for this build).
- **Number of measures:** pending verification (no source enumerates
  `msnfp_measurementitem` records for this build).
- Any specific "nine KPIs" / "twenty measures" figures discussed elsewhere are
  **not** confirmed here and must not be presented as verified.

See [`../docs/evidence-register.md`](../docs/evidence-register.md).
