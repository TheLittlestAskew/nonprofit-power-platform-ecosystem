# Custom Dataverse Table Inventory — Validation Summary

- **Source file:** `source-private/Entities with brief descriptions.xlsx` (private; not committed)
- **Generated:** 2026-07-12
- **Generator:** `scripts/build_dataverse_inventory.py`
- **Total entities scanned in source:** 805
- **Custom `tr_` tables identified:** **129**

## Counts by Classification

| Classification | Count |
|---|---|
| Core business table | 67 |
| Process/support table | 9 |
| Relationship/intersect table | 8 |
| Unclear / manual review | 45 |
| **Total custom `tr_`** | **129** |

## Prefix-Detection Rule

A row is counted as a **custom table** when its **Schema Name** OR **Logical Name** begins with `tr_` (case-insensitive, whitespace trimmed). A name that merely *contains* `tr_` but starts with a different publisher prefix (for example `cr57f_tr_budget_details`) is **excluded** — it belongs to a different publisher and is not a `tr_` custom table.

## Classification Rules

Applied in order, most-confident first:

1. **Relationship/intersect** — the schema name contains `_tr_`, the Dataverse convention for many-to-many *intersect* entities (`tr_<a>_tr_<b>`). Underscores or a "relational-looking" name alone are **not** treated as intersect evidence — only this explicit double-publisher pattern.
2. **Process/support** — the core segment (schema minus the leading `tr_`) contains a documented support token: `log`, `audit`, `history`, `mapping`, `tracker`, `migration`, `mirgration`. This is a **name-based heuristic**; every match is listed below for manual confirmation.
3. **Core business** — has a non-empty source description and no support or intersect signal.
4. **Unclear / manual review** — no description available in source, so the table's function cannot be verified here.

## Rows Flagged for Manual Review

**Relationship/intersect candidates (8)** — confident by naming pattern, but confirm each is a true N:N intersect:

- `tr_Attendee_tr_Volunteer`
- `tr_Bills_tr_DaviesLocations`
- `tr_CaseMeetings_tr_ResourceCollection`
- `tr_msnfp_deliveryframework_tr_DaviesLocati`
- `tr_msnfp_deliveryframework_tr_Employees`
- `tr_msnfp_engagementopportunity_tr_Voluntee`
- `tr_msnfp_Group_tr_Volunteer`
- `tr_msnfp_workitem_tr_DaviesLocations`

**Support-token heuristic matches (9)** — confirm whether each is genuinely a process/support table vs. a business table:

- `tr_FamilyHistory` — support-token heuristic: 'history' in name (confirm manually)
- `tr_JobHistory` — support-token heuristic: 'history' in name (confirm manually)
- `tr_LGLMirgrationTracker` — support-token heuristic: 'tracker' in name (confirm manually)
- `tr_LogReference` — support-token heuristic: 'log' in name (confirm manually)
- `tr_ManualAudit` — support-token heuristic: 'audit' in name (confirm manually)
- `tr_MedLog` — support-token heuristic: 'log' in name (confirm manually)
- `tr_PartnerHistory` — support-token heuristic: 'history' in name (confirm manually)
- `tr_TaxStatementLog` — support-token heuristic: 'log' in name (confirm manually)
- `tr_ViewHistory` — support-token heuristic: 'history' in name (confirm manually)

**Unclear / no description (45)**:

- `tr_ActionItem`
- `tr_AdminReporting`
- `tr_Attendee`
- `tr_BusFare`
- `tr_Children`
- `tr_CreditDebit`
- `tr_Date`
- `tr_DepositLedger`
- `tr_Diagnosis`
- `tr_DiagnosticImpressions`
- `tr_Documents`
- `tr_EmailtoSMS`
- `tr_EmployeeTypes`
- `tr_EmploymentVerification`
- `tr_FarmBus`
- `tr_Followup`
- `tr_Goals`
- `tr_GroupAttendee`
- `tr_IncomeBenefits`
- `tr_InventoryTracking`
- `tr_ManualView`
- `tr_ManualxRef`
- `tr_MeasurementSnapshot`
- `tr_MentalStatus`
- `tr_PartFullTime`
- `tr_PaymentFailures`
- `tr_Payments`
- `tr_Payroll`
- `tr_PHQ9`
- `tr_Policy`
- `tr_PotentialGuest`
- `tr_RecurringBilling`
- `tr_RecurringPayments`
- `tr_Reimbursements`
- `tr_ReportingbyDate`
- `tr_Scheduler`
- `tr_Session`
- `tr_SessionGroups`
- `tr_StripePropay`
- `tr_Tables`
- `tr_TaxWithholding`
- `tr_TimeClock`
- `tr_TimeEntries`
- `tr_TimePunch`
- `tr_TreatmentGoals`

## Unresolved Questions

- Are all support-token matches truly utility tables, or are some primary business entities whose names happen to contain a token (e.g. a medication log)?
- Do any *core business* tables actually function as intersect tables without following the `_tr_` naming pattern?
- This inventory reflects the source workbook only; it is not a live read of the environment and may lag later schema changes.

_This summary contains table-level metadata only. No record-level or operational data is included._
