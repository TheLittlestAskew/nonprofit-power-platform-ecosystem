# Primary Model-Driven Application — Sitemap & Entity Map

This document describes the structure of the primary model-driven application
(internal name: **Davies Admin Bridge**) that surfaces the environment's data
across the six operational areas.

- **Source:** `source-private/Davies Admin Bridge SiteMap x.xlsx` (private; not committed)
- **Generated catalog:** [`application-entity-catalog.csv`](application-entity-catalog.csv)
  (produced by `scripts/build_application_catalog.py`)
- **Evidence tier:** Verified (structure read directly from the sitemap export)
- **Last validated:** 2026-07-12

## Verified Totals

| Metric | Value |
|---|---|
| Operational areas (sitemap areas) | 6 |
| Entity references surfaced | 105 |
| **Unique entities surfaced** | **94** |
| — Custom `tr_` tables | 57 |
| — Nonprofit Accelerator (`msnfp_` / `msiati_`) | 22 |
| — Standard Microsoft | 12 |
| — Other publisher (budget solution, `cr57f_`) | 3 |

The application surfaces **94 unique entities** across **105 placements** —
11 references are the same entity reused in more than one area (see
[Cross-Area Entities](#cross-area-entities)).

## Discrepancy Check vs. README

The README states **94 entities** in the primary model-driven application. The
sitemap source confirms **94 unique entities**. ✓ **No discrepancy.** No README
metric change is required by this analysis.

> Note on the two headline numbers: the **129 custom `tr_` tables** metric
> counts custom tables that *exist* in the environment (from the entity
> inventory), while the **94 entities** metric counts entities *surfaced in the
> app's sitemap*. Only 57 of the 94 surfaced entities are custom `tr_` tables;
> the remaining custom tables exist in the environment but are not placed on
> this application's sitemap. The two numbers measure different things and are
> both verified.

## Area → Group → Entity Structure

Internal sitemap area names map to public operational-area labels as follows.

### 1. Development Finance & Revenue
*(internal area: Finance Management — 20 entities)*

| Group | Entities |
|---|---|
| Income & Expenses | `tr_inex`, `tr_depositledger`, `tr_bills`, `tr_deposit`, `msnfp_transaction`, `tr_stripepropay` |
| Budgeting | `msnfp_budget`, `cr57f_tr_budget_categorieses`, `cr57f_tr_budget_sub_categorieses`, `cr57f_tr_budget_details` |
| Donor Management | `contact`, `msnfp_donorcommitment`, `msnfp_designation`, `msnfp_workitem`, `account`, `organization`, `cdm_company`, `tr_lglmirgrationtracker`, `tr_processorcustomers`, `tr_vendormapping` |

### 2. Shelter & Case Management
*(internal area: Shelter Management — 24 entities)*

| Group | Entities |
|---|---|
| Case Management | `tr_sheltercalendar`, `tr_guest`, `tr_bedsroomsmen`, `tr_bedsrooms`, `tr_casemeetings`, `tr_casemeeting`, `tr_childinfo`, `tr_discharge`, `tr_guestwins`, `tr_healthinfo`, `tr_infractions`, `tr_phase1`, `tr_phase2`, `tr_phase3`, `tr_waitlist`, *Medication-management record*, *Medication-management record*, `tr_resourcecollection`, `tr_commongoals`, `tr_guestsresources`, `tr_nightwatch`, `tr_benefitsincome`, `tr_goals`, `tr_employmentincome` |

> Two entries above appear as the generalized public label *Medication-management
> record*; their exact clinical schema identifiers are **withheld** for privacy
> (see [`../SECURITY.md`](../SECURITY.md)). The 24-entity count is unchanged.

### 3. Outcomes, Grants & Compliance
*(internal area: Tracking — 27 entities)*

| Group | Entities |
|---|---|
| Mission | `msnfp_objective`, `msnfp_deliveryframework`, `msnfp_theoryofchange`, `msnfp_indicator`, `msnfp_indicatorvalue`, `msnfp_result`, `msnfp_operation`, `msnfp_programitem`, `msnfp_assessment`, `msnfp_workitem` |
| Grant Management | `msnfp_award`, `msnfp_disbursement`, `msnfp_item`, `msnfp_report`, `report`, `account`, `tr_goals`, `msnfp_measurementitem` |
| Programs | `tr_adminreporting`, `tr_busfare`, `tr_farmbus`, `tr_counselingreporting` |
| Surveys | `tr_casemeetingsurveys`, `tr_exitsurvey`, `tr_followupsurvey`, `tr_intakesurvey`, `tr_surveylinks` |

> The **Tracking** area is the internal home of the **Outcomes, Grants &
> Compliance** work. Its **Mission** and **Grant Management** groups are built
> on Microsoft Nonprofit Accelerator impact and grant entities (`msnfp_*`),
> combined with custom `tr_` program, survey, and goal tables. This is the
> foundation of the [`grants-outcomes/`](../grants-outcomes/) module.

### 4. Volunteer & Community Engagement
*(internal area: Volunteer Management — 8 entities)*

| Group | Entities |
|---|---|
| Volunteers | `tr_sheltercalendar`, `activitypointer`, `msnfp_engagementopportunity`, `tr_volunteer`, `tr_attendee`, `msnfp_group`, `msnfp_groupmembership`, `msnfp_workitem` |

### 5. Employee & Administrative Operations
*(internal area: Employee Management — 13 entities)*

| Group | Entities |
|---|---|
| Employee Management | `tr_employees`, `tr_payperiods`, `tr_payroll`, `tr_reimbursements`, `team`, `tr_timeclock`, `tr_timeentries`, `tr_timepunch`, `tr_timesheet`, `systemuser`, `contact`, `tr_date`, `tr_scheduler` |

### 6. Communications & Brand
*(internal area: Communications — 13 entities)*

| Group | Entities |
|---|---|
| Communications | `tr_documents`, `emailsignature`, `template`, `tr_casemeetingsurveys`, `tr_exitsurvey`, `tr_followupsurvey`, `tr_intakesurvey`, `tr_surveylinks`, `tr_formspolicies`, `tr_admincommunications`, `tr_guestcommunication`, `flowrun`, `annotation` |

## Cross-Area Entities

Ten entities are surfaced in more than one area (11 duplicate references total),
reflecting shared data reused across workflows:

| Entity | Areas | Family |
|---|---|---|
| `msnfp_workitem` | Development Finance, Outcomes/Grants, Volunteer (3) | Accelerator |
| `account` | Development Finance, Outcomes/Grants | Standard |
| `contact` | Development Finance, Employee Ops | Standard |
| `tr_sheltercalendar` | Shelter, Volunteer | Custom |
| `tr_goals` | Shelter, Outcomes/Grants | Custom |
| `tr_intakesurvey` | Outcomes/Grants, Communications | Custom |
| `tr_exitsurvey` | Outcomes/Grants, Communications | Custom |
| `tr_followupsurvey` | Outcomes/Grants, Communications | Custom |
| `tr_casemeetingsurveys` | Outcomes/Grants, Communications | Custom |
| `tr_surveylinks` | Outcomes/Grants, Communications | Custom |

## Method & Limitations

- Entity families are derived from logical-name publisher prefixes: `tr_` →
  custom; `msnfp_`/`msiati_` → Nonprofit Accelerator; `cr57f_` → a separate
  budget-solution publisher; a fixed allow-list of first-party names → standard
  Microsoft. Every surfaced entity resolved to a family (0 unresolved).
- This reflects the sitemap export at the time of capture; it is not a live
  read and may lag later application changes.
- Only structural sitemap metadata is used. No record-level data exists in or
  was read from this source.
