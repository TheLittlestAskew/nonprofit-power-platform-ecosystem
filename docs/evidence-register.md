# Source Evidence Register

Every claim in this repository should trace to a source. This register records
which **private** source files (in `source-private/`, never committed) support
which public claims, what was done to sanitize them, and what remains
unverified.

- **Private source location:** `source-private/` (git-ignored; never committed)
- **Register last updated:** 2026-07-12
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
- **Sanitization performed:** only table-level metadata (entity name, schema/
  logical name, description, classification) is emitted. No record-level data
  exists in or was taken from this source. Descriptions were pattern-scanned for
  emails/phone numbers (0 hits).
- **Unresolved questions:**
  - 45 custom `tr_` tables have **no description** in source → classified
    "unclear/manual review." Their function is unverified.
  - 9 support-token classifications are name-based heuristics needing manual
    confirmation.
  - Some table names expose behavioral-health schema (e.g. `tr_PHQ9`,
    `tr_Diagnosis`, `tr_MentalStatus`) — names only, no records; flagged for
    the author's review before wide sharing.
- **Last validated:** 2026-07-12

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

---

## Standing Open Questions

- KPI count (`msnfp_indicator`) and measure count (`msnfp_measurementitem`) are
  **pending verification** — no source in this build enumerates them. Any
  "nine KPIs" / "twenty measures" figure is unconfirmed.
- 45 custom `tr_` tables lack descriptions and need manual classification.
- The resource-directory datasets (Sources 3 & 4) await a dedicated publication
  review.
