# Source Evidence Register

Every claim in this repository should trace to a source. This register records
which **private** source files (in `source-private/`, never committed) support
which public claims, what was done to sanitize them, and what remains
unverified.

- **Private source location:** `source-private/` (git-ignored; never committed)
- **Register last updated:** 2026-07-13
- **No source file contents are reproduced here** — only filenames, the claims
  they support, and the sanitization performed.

## Evidence Tiers

- **Verified** — reproducible from a named source file.
- **Reconstructed** — rebuilt from source structure into an original artifact.
- **Working interpretation** — reasonable but not confirmed.
- **Pending verification** — discussed but not yet grounded in a source.

---

## Source 1 — `Entities with brief descriptions.xlsx`

- **Supports:** the count of **129 custom `tr_` tables**; the 805 total-entity
  context; table names, descriptions, and classifications.
- **Verified?** **Yes.** 129 confirmed by `scripts/build_dataverse_inventory.py`
  (805 entities scanned → 129 with the `tr_` prefix).
- **Public derivatives:**
  - `dataverse/custom-table-catalog.csv`
  - `dataverse/inventory-summary.md`
- **Verified counts (revised source, SHA-256
  `eac37dbb…02ac8e8`, modified 2026-07-12):** 129 custom `tr_` tables, classified
  **core 94 / process-support 9 / relationship-intersect 25 / unclear 1**
  (total 129). The revised workbook now carries descriptions for nearly every
  table (0 blank, 3 literal `N/A`), so only **`tr_ActionItem`** (description
  `N/A`) remains unclear. Relationship/intersect tables (25) are classified by
  **schema structure** — the name embeds a second entity reference (e.g.
  `tr_msnfp_award_msnfp_indicator`) — independent of the description.
- **Sanitization performed:**
  - Only table-level metadata (entity name, schema/logical name, description,
    classification) is emitted. No record-level data exists in or was taken from
    this source. Descriptions were pattern-scanned for emails/phone numbers
    (0 hits).
  - **Clinical/behavioral-health name generalization:** **8 sensitive
    structures** have their exact internal schema identifiers **withheld** from
    the public catalog and summary; a generalized public domain label is published
    instead. The published domains are *Behavioral-health assessment*, *Clinical
    classification*, *Mental-status assessment*, *Counseling treatment goals*, and
    *Medication-management record*. The private schema-name → label mapping is
    **maintained locally in a git-ignored config
    (`source-private/sensitive-generalizations.json`) and is not committed**; the
    generator loads it at runtime and the original identifiers are never named in
    any tracked file. The source workbook is not altered. See `SECURITY.md`.
- **Unresolved questions:**
  - **1** custom `tr_` table has **no usable description** (`N/A`) in source →
    classified "unclear/manual review": `tr_ActionItem`. It is reported exactly,
    not force-classified.
  - 9 support-token classifications are name-based heuristics needing manual
    confirmation; 25 intersect classifications are structural and should each be
    confirmed as a true N:N intersect.
- **Last validated:** 2026-07-13

## Source 2 — `Davies Admin Bridge SiteMap x.xlsx`

- **Supports:** the count of **94 entities** surfaced in the primary
  model-driven application; the **6 operational areas**; the area → group →
  entity structure; the internal-area → public-label mapping.
- **Verified?** **Yes.** 94 unique entities confirmed by
  `scripts/build_application_catalog.py` (105 references, 94 unique across 6
  worksheets).
- **Public derivatives:**
  - `dataverse/application-entity-catalog.csv`
  - `dataverse/application-sitemap.md`
  - the six-area framing used across `architecture/` and `grants-outcomes/`
- **Sanitization performed:** only sitemap structure (area, group, entity
  logical name) is used. No record-level data exists in this source. Entity
  families derived from publisher prefixes.
- **Unresolved questions:**
  - The sitemap reflects a point-in-time export; it may lag later app changes.
  - 10 entities appear in multiple areas (documented); confirm this reflects
    intentional reuse.
- **Last validated:** 2026-07-12

## Source 3 — `Active Common Goals All Details ….xlsx`

- **Supports:** context that the `tr_commongoals` custom table backs a
  goal-pathway / service-navigation model (186 records in source).
- **Verified?** Structure verified (186 rows, 19 columns incl. goal/phase/need
  fields). Used for **context only** in this build.
- **Public derivatives:** **None committed.** No records or counts of goals are
  published.
- **Sanitization performed:** file inspected for structure only (header + row
  count). Contains contact-style fields (phone, website) → treated as
  resource-directory-adjacent and held out of publication.
- **Unresolved questions:** whether/what portion is publishable pending the
  separate resource-directory review (see Source 4).
- **Last validated:** 2026-07-12

## Source 4 — `Active Resource Collections ….xlsx`

- **Supports:** context that `tr_resourcecollection` backs a community
  **resource directory** (204 records in source).
- **Verified?** Structure verified (204 rows, 16 columns incl. Primary Email,
  Primary Phone, Full Address).
- **Public derivatives:** **None. Out of scope.** Per project rule, public
  resource-directory records are **not** published yet — even where the
  underlying information may be public, it needs separate review.
- **Sanitization performed:** file inspected for structure only. Contains
  emails, phones, and addresses → **must not** be committed in any form until
  reviewed.
- **Unresolved questions:** the entire publication decision for this dataset is
  deferred to a dedicated review.
- **Last validated:** 2026-07-12

## Source 5 — `Entity Diagram for Davies Admin Bridge.png`

- **Supports:** visual confirmation of the two table families (`tr_*` custom and
  `msnfp_*` Accelerator) and the overall relational scale of the environment.
- **Verified?** Used as **corroborating** evidence for the table-family
  narrative; not a numeric source.
- **Public derivatives:** **None committed.** The raw diagram is a production
  ERD and is not published. `architecture/system-overview.md` is an original
  simplified rendering, not this image.
- **Sanitization performed:** none published; the raw image stays in
  `source-private/`.
- **Unresolved questions:** whether a fully redrawn, sanitized ERD should be
  produced later for `architecture/`.
- **Last validated:** 2026-07-12

## Source 6 — `Atrium Grant KPIs and Metrics.docx`

- **Supports:** the grant **measurement matrix** — the split between headline KPI
  targets and supporting measurement/implementation work.
- **Verified counts:** the document is a single 3-column matrix with **28 data
  rows** = **9 headline KPI targets** (target-based KPIs: 70% to permanent
  housing, 60% employment/income, 45% financial-assistance enrollment, 100%
  receive a referral, 28 weekly case-management sessions, 16 weekly counseling
  sessions, 75% improved mental-health outcomes, 80% complete financial-literacy
  / job-coaching, 50% former-guest follow-up) plus **19 supporting measurement
  and implementation items** (additional outcome concepts, implementation notes,
  unresolved definitions, and open measurement-design questions). The **20-measure
  reporting framework** is a *curated derivative* built on the nine headline KPIs,
  **not** the raw row count of this file. These figures are distinct and **not**
  additive.
- **Public derivatives:**
  - `grants-outcomes/README.md`, `grants-outcomes/measurement-model.md`,
    `grants-outcomes/grant-lifecycle.md`, `grants-outcomes/reporting-workflow.md`
  - `architecture/grant-reporting-lifecycle.md`, root `README.md`, `CHANGELOG.md`
- **Sanitization performed:** only aggregate counts and paraphrased KPI target
  language are published. A staff first name that appears in two cells and
  internal “assign to a person” notes were **not** copied. No record-level data
  exists in this source.
- **Unresolved questions:** several of the 19 supporting items are explicitly
  open design questions in-source (how to measure resilience/self-sufficiency,
  what “credentialing”/“job coaching” refer to); they are not finalized KPIs.
- **Last validated:** 2026-07-13

## Source 7 — `Atrium Health Floyd-Polk Foundation Grantee Portal 2026.pdf`

- **Supports:** the 2026 grant **proposal** parameters and reporting
  requirements.
- **Verified counts:** proposal **requested $100,000** (a *request*, not an
  award — and distinct from any other grant's dollar figure); **150** estimated
  individuals served; **23 measurable objectives** listed in the proposal;
  **interim report due December 31, 2026**; **final report due within 30 days
  after the 12-month grant period**.
- **Public derivatives:**
  - `grants-outcomes/grant-lifecycle.md`, `grants-outcomes/reporting-workflow.md`
  - root `README.md`, `CHANGELOG.md`, `grants-outcomes/data-dictionary.csv`
- **Sanitization performed:** only the verified counts, dollar request, and
  reporting deadlines are published. **Not copied:** organization address, FEIN /
  tax IDs, operating-budget figure, founding date, contact names, phone numbers,
  email addresses, partner-organization roster, attachment/file lists, and the
  county/location detail. No record-level data is published.
- **Dollar-figure discipline:** the **$100,000** here is the 2026 proposal
  *request*. An earlier **$80,000** figure belongs to a *different*
  grant/reporting artifact and is **not** interchangeable — each dollar amount
  stays tied to its own grant context and must not be silently substituted.
- **Unresolved questions:** the *awarded* amount (vs. requested) is not
  established by this source; award outcome is unverified here.
- **Last validated:** 2026-07-13

## Source 8 — `stripejson.txt` (Stripe charge export)

- **Supports:** the field-level **schema** of the Stripe charge source behind the
  development-finance module.
- **Verified counts:** a single Stripe `list` response, `object: "list"`,
  `has_more: false`, containing **74 records, all `charge` objects** (every
  `balance_transaction.reporting_category` = `charge`). 48 top-level fields, with
  embedded `balance_transaction`, `billing_details`, card `source`, `metadata`,
  and `refunds`.
- **Public derivatives:** `development-finance/data-dictionary.csv` (field names +
  privacy category only); `scripts/inspect_stripe_schema.py` output (structure
  only).
- **Sanitization performed:** only field **names**, JSON **types**, and
  **presence %** are emitted — **never a value**. No id, email, name, address,
  card data, amount, timestamp, metadata value, or URL is published.
- **Distinct-object discipline:** these are **charges**, not payouts. The
  portfolio "483+ … payout records" claim references a different object type; the
  74 charges are a **separate** surviving sample, **not** a known subset of the
  483+ and **not** the 89.7% denominator.
- **Unresolved questions:** the full migration population, the payout dataset, and
  the object composition of the 483+ total are **not preserved** in this file.
- **Last validated:** 2026-07-14

## Source 9 — `stripe-dataverse-process-reconstruction.md` (private notes)

- **Supports:** the **reconstructed architecture** of the Stripe→Dataverse
  workflow (API retrieval, watermark state, pagination, payout→Deposit,
  charge→Transaction, email normalization, deposit linking, duplicate prevention,
  concurrency).
- **Verified?** Working reconstruction from surviving technical notes; the
  matching **inputs** are corroborated, the exact four-tier order/thresholds and
  final production export are **not preserved**.
- **Public derivatives:** `development-finance/*.md`,
  `portfolio/stripe-dataverse-website-case-study.md`,
  `architecture/development-finance-lifecycle.md`.
- **Sanitization performed:** real internal field names, expressions, and API
  endpoints stay private. Public artifacts use generalized concepts and
  pseudocode only — no internal schema names, GUIDs, Stripe ids, URLs, or values.
- **Unresolved questions:** exact tier sequence/thresholds, exact query filters,
  the 89.7% numerator/denominator, and the 483+ object composition are **not
  preserved** (recorded as *not preserved*, not *pending verification*).
- **Last validated:** 2026-07-14

## Source 10 — Portfolio design PDFs (fundraising operations)

- **Supports:** the **portfolio-documented** operational results and the
  annual-giving operating model.
- **Content:** `Annual Giving Workflow.pdf` and `Revenue Engine.pdf` are a
  two-page recruiter-facing portfolio set stating **483+** Stripe-related records,
  an **89.7%** automatic match rate, a **four-tier** matching process, and a
  7-step annual-giving lifecycle. `Annual Fundraising Performance.pdf` is a
  **production reporting dashboard** (FY2025) — highest sensitivity.
- **Verified?** The figures are **portfolio-documented self-assertions**, not
  independently reproducible from data. Published as documented, never as audited.
- **Public derivatives:** `development-finance/revenue-engine.md`,
  `portfolio/stripe-dataverse-website-case-study.md` (qualitative model only).
- **Sanitization performed:** **no** FY2025 revenue totals, by-source breakdowns,
  funder names, grant amounts, preparer name, or org legal name are published.
- **Last validated:** 2026-07-14

---

## Standing Open Questions

- **Grant measurement design counts are now verified** (Sources 6 & 7): 9
  headline KPI targets, 19 supporting measurement/implementation items, a curated
  20-measure framework, and 23 proposal objectives. What remains **pending
  verification** is the count of `msnfp_indicator` / `msnfp_measurementitem`
  **records deployed in Dataverse** — no source in this build enumerates the live
  rows.
- 1 custom `tr_` table (`tr_ActionItem`) lacks a usable description and needs
  manual classification; reported exactly, not force-classified.
- The *awarded* grant amount (vs. the $100,000 requested) is unverified.
- **Finance (Sources 8–10):** the 483+ / 89.7% / four-tier figures are
  **portfolio-documented**, not reproducible from the surviving data. The exact
  tier order/thresholds, query filters, 89.7% numerator/denominator, 483+ object
  composition, and the payout dataset are **not preserved** (not the same as
  pending verification). The surviving sample is **74 charges**, a separate
  export.
- The resource-directory datasets (Sources 3 & 4) await a dedicated publication
  review.
