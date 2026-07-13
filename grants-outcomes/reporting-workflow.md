# Reporting Workflow

How measured data becomes a funder report — the mechanics between "we have the
records" and "the report is submitted."

> **Evidence tier:** Working interpretation. The reporting entities
> (`msnfp_report`, `report`, `tr_adminreporting`, `tr_counselingreporting`) are
> **verified** as present in the Tracking area. The workflow described here is a
> reasonable reconstruction, not a step-verified export of the production
> automation.

## Reporting Cadence

- **Interim reports** — progress against targets partway through the grant
  period. In the verified 2026 proposal, the interim report was due
  **December 31, 2026**.
- **Final / closeout reports** — full-period results at grant end. In the same
  proposal, the final report was due **within 30 days after the 12-month grant
  period**.
- **Ad hoc / internal** — leadership dashboards and learning reviews between
  formal reports.

> Reporting-requirement dates above are verified from the 2026 grant proposal
> (see [`../docs/evidence-register.md`](../docs/evidence-register.md), Source 7).
> They are specific to that grant; other grants carry their own cadence.

## The Workflow

```text
1. DEFINE       Report requirements captured against the award
                (msnfp_award terms → msnfp_report definition)
        ↓
2. COLLECT      Live records accumulate through normal operations
                (msnfp_indicatorvalue, msnfp_result, tr_goals, surveys)
        ↓
3. AGGREGATE    Values rolled up per indicator, per program, per period
                (msnfp_result, reporting views)
        ↓
4. RECONCILE    Financial side aligned: award vs. disbursement
                (msnfp_award ↔ msnfp_disbursement ↔ msnfp_item)
        ↓
5. ASSEMBLE     Program narratives + numbers combined
                (tr_adminreporting, tr_counselingreporting, report)
        ↓
6. REVIEW       Compliance check against funder terms before submission
        ↓
7. SUBMIT       Report delivered in the funder's required format
        ↓
8. RETAIN       Audit-ready documentation preserved with traceable lineage
```

## Program Reporting Tables (custom)

The Programs group carries custom reporting tables that hold program-specific
narrative and operational detail feeding the formal reports:

| Table | Reporting role |
|---|---|
| `tr_adminreporting` | Administrative / cross-program reporting |
| `tr_counselingreporting` | Counseling-program reporting |
| `tr_busfare`, `tr_farmbus` | Program-specific support tracking (transportation) |

## Financial Compliance

Grant reporting is not only outcomes — it is also spend against award. The Grant
Management group ties these together:

```text
msnfp_award  →  msnfp_disbursement  →  msnfp_item
  (awarded)         (paid out)           (line detail)
```

Reconciling reported outcomes with reported spend is what keeps a grant
**compliant**, not just **complete**.

## Audit-Ready by Design

The final step is retention with lineage. Because every reported figure links
back through indicators to source records (see
[`measurement-model.md`](measurement-model.md)), an auditor can select any
number in a submitted report and trace it to the records that produced it.

## Known Gaps / Pending Verification

- The exact production automation (Power Automate flows, scheduled rollups) is
  **not** documented here yet; this is a structural reconstruction.
- The grant measurement **design counts** (9 KPI targets, 19 supporting items,
  20 curated measures, 23 proposal objectives) are now **verified**; the count of
  `msnfp_indicator` / `msnfp_measurementitem` **records deployed in Dataverse**
  remains **pending verification** (see [`measurement-model.md`](measurement-model.md)).
- Report templates and funder-specific formats are not included in this build.
