# Grant Reporting Lifecycle

A diagram of how a single funder requirement travels all the way to a submitted,
audit-ready report. Written for grant-development and nonprofit-operations
readers: it shows the flow, not every table.

> **Evidence tier:** Reconstructed. The stages and the entities named are
> **verified** as present in the Tracking area; the end-to-end flow is a
> structural reconstruction. KPI/measure counts are **pending verification.**

## The Lifecycle

```mermaid
flowchart TD
    FR["Funder Requirement\n(grant agreement)"]
    AD["Award Deliverable\n(what we promised to deliver)"]
    KPI["KPI Definition\n(msnfp_indicator)"]
    MEAS["Measure Definition\n(msnfp_measurementitem)"]
    REC["Program Activity Record\n(msnfp_indicatorvalue, workitems, surveys)"]
    ANALYSIS["Outcome Analysis\n(msnfp_result)"]
    REVIEW["Compliance Review\n(award vs. disbursement, terms check)"]
    REPORT["Mid-Year or Final Report\n(msnfp_report / report)"]

    FR --> AD --> KPI --> MEAS --> REC --> ANALYSIS --> REVIEW --> REPORT

    REPORT -. "traceable back to" .-> REC
```

## Stage Reference

| Stage | Entity/entities | What happens |
|---|---|---|
| Funder Requirement | `msnfp_award`, `account` | Grant terms captured |
| Award Deliverable | `msnfp_objective`, `msnfp_deliveryframework`, `msnfp_programitem` | Requirements become deliverables |
| KPI Definition | `msnfp_indicator` | Each deliverable gets a KPI |
| Measure Definition | `msnfp_measurementitem` | Each KPI gets a concrete measure |
| Program Activity Record | `msnfp_indicatorvalue`, `msnfp_workitem`, `tr_*surveys` | Live records accumulate |
| Outcome Analysis | `msnfp_result`, `msnfp_assessment` | Records analyzed into outcomes |
| Compliance Review | `msnfp_award` ↔ `msnfp_disbursement` ↔ `msnfp_item` | Outcomes + spend reconciled |
| Mid-Year / Final Report | `msnfp_report`, `report`, `tr_adminreporting`, `tr_counselingreporting` | Report assembled and submitted |

## Why the Dotted Line Matters

The dotted "traceable back to" arrow is the whole point of an audit-ready
system: any number in a submitted report can be traced back to the program
activity records that produced it. Full detail in
[`../grants-outcomes/grant-lifecycle.md`](../grants-outcomes/grant-lifecycle.md).

## Pending Verification

- Exact counts of KPIs (`msnfp_indicator`) and measures
  (`msnfp_measurementitem`) are **not** confirmed by any available source.
