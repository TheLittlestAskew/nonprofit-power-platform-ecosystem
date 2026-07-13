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
- **Verified counts (revised 2026-07-13):** 129 custom `tr_` tables, classified
  **core 50 / process-support 9 / relationship-intersect 25 / unclear 45**
  (total 129). This replaces the earlier 67 / 9 / 8 / 45 distribution: 17 join
  tables that carried a literal `N/A` description (e.g.
  `tr_msnfp_award_msnfp_indicator`) were reclassified from *core* to
  *relationship/intersect* on the basis of **schema structure** — the name embeds
  a second entity reference — not description text.
- **Sanitization performed:**
  - Only table-level metadata (entity name, schema/logical name, description,
    classification) is emitted. No record-level data exists in or was taken from
    this source. Descriptions were pattern-scanned for emails/phone numbers
    (0 hits).
  - **Clinical/behavioral-health name generalization:** the exact internal schema
    identifiers for especially sensitive clinical structures are **withheld** from
    the public catalog and summary; a generalized domain label is published
    instead (PHQ-9/GAD-7 → *Behavioral-health assessment*; Diagnosis / Diagnostic
    Impressions → *Clinical classification*; Mental Status → *Mental-status
    assessment*; Treatment Goals → *Counseling treatment goals*; Medications /
    Med Log → *Medication-management record*). Implemented reproducibly in
    `scripts/build_dataverse_inventory.py` (`SENSITIVE_GENERALIZATION`); the
    source workbook is not altered. See `SECURITY.md`.
- **Unresolved questions:**
  - 45 custom `tr_` tables have **no usable description** (blank or `N/A`) in
    source → classified "unclear/manual review." Their function is unverified and
    they are reported exactly, not force-classified to shrink the count.
    `tr_ActionItem` in particular carries no description (`N/A`) in the revised
    source and remains unverified.
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

---

## Standing Open Questions

- **Grant measurement design counts are now verified** (Sources 6 & 7): 9
  headline KPI targets, 19 supporting measurement/implementation items, a curated
  20-measure framework, and 23 proposal objectives. What remains **pending
  verification** is the count of `msnfp_indicator` / `msnfp_measurementitem`
  **records deployed in Dataverse** — no source in this build enumerates the live
  rows.
- 45 custom `tr_` tables lack usable descriptions and need manual classification;
  reported exactly, not force-classified.
- The *awarded* grant amount (vs. the $100,000 requested) is unverified.
- The resource-directory datasets (Sources 3 & 4) await a dedicated publication
  review.
