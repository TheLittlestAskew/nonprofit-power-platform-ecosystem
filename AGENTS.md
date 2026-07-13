# AGENTS.md — Authoritative Project Instructions

This file governs how any human or AI agent works in this repository. Read it
in full before creating, editing, or committing anything. If an instruction
here conflicts with a request, follow this file and raise the conflict.

---

## 1. Repository Purpose

This repository is a **public, sanitized technical case study** of a Microsoft
Power Platform and Dataverse environment architected by Taylor Askew Ritchie
for a multi-site homeless-services nonprofit.

It exists to demonstrate systems-design, data-modeling, grants-compliance, and
operations-automation capability to recruiters and collaborators **without**
publishing any confidential production data.

It is **documentation and reconstruction**, not a production export.

## 2. Intended Audiences

- Grant-development and nonprofit-operations recruiters and hiring managers
- Power Platform / Dataverse practitioners reviewing architecture decisions
- Nonprofit-technology peers evaluating the design approach
- The author, as a durable portfolio artifact

Write for a reader who is technically literate but has **no access to the
original environment**. Every artifact must stand on its own.

## 3. Factuality Rules

1. **Never invent a metric.** Counts, totals, and measurements may only be
   stated if they are derived from a source file present in `source-private/`
   or already verified in this repository.
2. **Distinguish evidence tiers explicitly** in any document that makes claims:
   - **Verified** — traceable to a specific source file and reproducible.
   - **Reconstructed** — rebuilt from source structure into an original public
     artifact (e.g., a redrawn diagram or paraphrased schema).
   - **Working interpretation** — a reasonable reading not yet confirmed.
   - **Pending verification** — a claim discussed but not yet grounded in a
     local source file. Label it as such; do not present it as fact.
3. **Identify uncertainty rather than guessing.** If a fact cannot be
   confirmed from available sources, say so and record it as an open question
   (see `docs/evidence-register.md`).
4. Do not silently "improve" a verified metric to make it rounder or more
   impressive. Report discrepancies for human review instead of changing them.

## 4. Sanitization Rules

Governed jointly by this file and [`SECURITY.md`](SECURITY.md).

**Never commit** (in raw or lightly-redacted form):

- Raw Excel exports, raw JSON, or raw CSV pulled from the production tenant
- Employer documents, contracts, or internal operational files
- Production screenshots that show real records
- Donor, employee, volunteer, client, guest, or applicant records
- Personal records of any individual
- Payment/processor identifiers, Stripe charge IDs, connection strings,
  environment/tenant IDs, API keys, tokens, or secrets
- Production URLs that expose private systems

**May be published** (as original public derivatives):

- Table names and table-level descriptions
- System and solution architecture
- Aggregate counts (verified only)
- Invented sample records clearly marked as fictional
- Sanitized schemas and data dictionaries
- Generalized workflow and automation descriptions
- Pseudocode
- Reconstructed / redrawn diagrams

**Public resource-directory records are NOT yet approved for publication.**
Even where the underlying resource information may be public, it requires a
separate review before any of it is committed. Do not publish it yet.

## 5. The `source-private/` Prohibition

- `source-private/` holds production-derived exports and reference materials.
- It **must never** be committed, copied into a public path, or exposed in Git
  history — not now, not in a later commit, not through a diff.
- It is listed in `.gitignore`. Confirm it is ignored before reading the files
  (`git check-ignore source-private/`).
- Scripts may **read** from `source-private/` to generate sanitized public
  outputs. They must never **write** raw source contents into a tracked path.
- Every generated public file must contain only the categories allowed in
  Section 4.

## 6. Approved Terminology

Use these exact labels. Do not rename, reorder, or invent alternatives.

**The six operational areas** (public labels):

1. Development Finance & Revenue
2. Shelter & Case Management
3. Outcomes, Grants & Compliance
4. Volunteer & Community Engagement
5. Employee & Administrative Operations
6. Communications & Brand

**Internal → public area mapping** (the model-driven app's internal sitemap
area names map to the public labels above):

| Internal app area (source) | Public label |
|---|---|
| Finance Management | Development Finance & Revenue |
| Shelter Management | Shelter & Case Management |
| Tracking | Outcomes, Grants & Compliance |
| Volunteer Management | Volunteer & Community Engagement |
| Employee Management | Employee & Administrative Operations |
| Communications | Communications & Brand |

**Table-family terms:**

- **Custom `tr_` tables** — tables using the `tr_` publisher prefix, created
  specifically for this environment. **All `tr_` tables are custom.**
- **Nonprofit Accelerator tables** — the managed `msnfp_` (and related
  `msiati_`) tables from Microsoft's Nonprofit accelerator solutions.
- **Standard Microsoft tables** — first-party Dataverse tables
  (e.g., `account`, `contact`, `annotation`, `msdyn_*`, `systemuser`).
- Standard Microsoft and Nonprofit Accelerator tables were **materially
  modified, configured, extended, or integrated** in this environment, but
  they are **not** counted as custom `tr_` tables.

## 7. The Six Operational Areas (scope summary)

1. **Development Finance & Revenue** — income/expense tracking, budgeting,
   donor management, payment-processor reconciliation.
2. **Shelter & Case Management** — guest intake, bed/room management, case
   meetings, phases, goals, health/medication logs, discharge.
3. **Outcomes, Grants & Compliance** — impact measurement, grant KPIs and
   awards, program tracking, surveys, and compliance reporting. (Internal app
   area name: **Tracking**.)
4. **Volunteer & Community Engagement** — volunteers, attendance, engagement
   opportunities, groups.
5. **Employee & Administrative Operations** — employees, payroll, pay periods,
   time tracking, scheduling, reimbursements.
6. **Communications & Brand** — documents, templates, surveys, policies, and
   internal/guest communications.

## 8. Verified Current Metrics

These are confirmed against source files and reproducible (see
`dataverse/inventory-summary.md` and `docs/evidence-register.md`):

- **129 custom Dataverse tables** using the `tr_` publisher prefix
- **94 entities** organized within the primary model-driven application
- **6 major operational areas**

Additional verified context (from source, non-headline):

- 805 total entities exist in the environment (custom + Accelerator + standard).
- The 94 surfaced app entities comprise 57 custom `tr_` tables and 37
  Accelerator/standard/other-publisher entities.

Do not restate any other numeric claim as verified unless it is grounded in a
local source file and recorded in the evidence register.

## 9. Material Classification (public / reconstructed / sanitized / private)

| Class | Definition | May be committed? |
|---|---|---|
| **Public** | Original documentation written for this repo; verified aggregate facts; approved sample/fictional data | Yes |
| **Reconstructed** | Diagrams/schemas rebuilt from source structure into original artifacts | Yes, if they expose no confidential records |
| **Sanitized** | Source-derived output with all record-level and identifying data removed | Yes, after review against Section 4 |
| **Private** | Anything in `source-private/`; raw exports; real records | **Never** |

## 10. Working Discipline

- Do not commit directly to `main`. Use a working branch and open a pull
  request for human review.
- Prefer small, logical commits over one large commit.
- Label unfinished modules as unfinished. Never describe a placeholder as
  completed work.
- Keep the `README.md` navigation accurate: every module link must resolve.
- When a source count disagrees with a published metric, **report the
  discrepancy** in `dataverse/inventory-summary.md` and the evidence register;
  do not auto-edit the headline metric.
- No reuse license has been granted yet. See `RIGHTS.md`.
