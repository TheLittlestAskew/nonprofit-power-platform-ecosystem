# Changelog

All notable changes to this repository are documented here.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
and this project does not yet follow semantic versioning (it is documentation,
not released software).

## [Unreleased]

### Fixed

- **Service Navigation evidence corrections** (post-review pass, third source):
  - **Copy workflow is now source-backed.** A recovered production client-side
    script (Source 12, reviewed privately, never committed) directly
    demonstrates copying a reusable Goal template — with its child Action Items
    and Needs — into person-specific records: parent references preserved,
    duplicates checked within the person's case context, selected fields
    copied onto the new records. Production **parentage is a dedicated
    parent-reference field** (the dotted code is an identifier the workflow
    copies and uses for duplicate checks), and the linkage was a **hybrid
    reference + snapshot model**: resource references were retained *and*
    selected contact/link values were copied, so copied values can go stale
    unless refreshed. Removed earlier claims that pathway records never
    duplicated contact/link values and that directory edits automatically
    updated every pathway and plan; reference-only (or reference plus explicit
    snapshot) is now framed as a public design recommendation, not a
    production claim.
  - **Optional-step semantics:** the three source states are reported
    separately (yes 5 / no 46 / blank-unspecified 135). Blank is no longer
    presented as production evidence of "required"; a fail-safe default is a
    recommendation not preserved in the evidence.
  - **Coverage claims:** "16 of 204" is now backed by a deterministic,
    unit-tested **cross-workbook join** (16 distinct pathway references; each
    matched exactly one directory row; 0 ambiguous; 0 unmatched; denominator =
    204 analyzed directory rows) instead of being asserted from the reference
    count alone.
  - **Multi-program wording retracted:** the one repeated organization value
    does not carry distinct program titles; repeated organizations are now
    reported neutrally, with a dedicated aggregate
    ("repeated organizations with >1 distinct program title": 0).
  - **Inspector hardening:** type reconciliation is no longer tautological
    (passes only with zero unrecognized types and level counts summing to the
    row total); real hierarchy-integrity counts added (31/65/86 validly coded,
    0 malformed, 0 duplicates, 0 missing parents, 4 blank codes unresolved;
    letter-suffixed codes reported as observed shapes, not interpreted);
    worksheet selection is by **visibility + generalized schema** with an
    explicit ambiguity error (never by row count); and **source filenames,
    paths, and embedded export timestamps are withheld from output** (sources
    identified by role and SHA-256 only). All enforced by new invented-fixture
    tests.

### Added

- **Service Navigation module** (`service-navigation/`): sanitized documentation
  of two linked production systems — a curated **resource directory** ("where
  help exists") and a **Goal → Action Item → Need pathway model** ("how to reach
  it") — plus the linkage architecture that carries case management from
  discovery to an individualized, status-tracked plan. Ships model docs,
  taxonomy/classification guidance, `architecture/service-navigation-lifecycle.md`,
  a sanitized data dictionary (invented public field names; per-field
  production-value treatment), clearly fictional samples, and privacy controls.
  Aggregates were **independently recomputed** from the two private exports:
  **204** directory rows, **199** distinct organizations, **175** distinct
  service descriptions (trim-only; 174 case-folded), **8** top-level categories,
  and **186** pathway rows = **32 Goals + 68 Action Items + 86 Needs**
  (reconciles exactly). Pathways link to **16** distinct resources (coverage was
  selective, not universal — stated plainly). Adds a safe-by-construction source
  inspector (`scripts/inspect_service_navigation.py`: aggregates only, raw
  headers withheld, every output line passes a leakage guard) and a module
  validator (`scripts/validate_service_navigation_samples.py`: hierarchy
  integrity, fiction markers, scans for GUIDs, checksums, emails, phones,
  URLs, addresses, and schema prefixes, plus Markdown-link and Mermaid
  checks), with unit tests on invented fixtures. **The row-level collection is not published**: no organization or
  program names, contacts, addresses, URLs, procedural instructions,
  identifiers, checksums, or timestamps appear in any tracked file.
- **Web Resources module** (`web-resources/`): sanitized, reconstructed
  model-driven client-side patterns — form routing, returning-record auto-fill,
  duplicate prevention, date/time validation, cloud-flow refresh coordination,
  and command security. Each pattern ships a documented `.md` and a
  `node --check`-clean `.js` example that opens with a SANITIZED EXAMPLE notice
  and uses invented names, `async/await`, and `Xrm.WebApi`. Adds reusable pattern
  guides, `architecture/model-driven-web-resource-lifecycle.md`, a reproducible
  validator (`scripts/validate_web_resource_examples.py`) that rejects GUIDs,
  organization schema prefixes, environment URLs, non-fictional emails,
  production role names, forbidden terminology, missing notices, legacy
  synchronous network calls, and private source references, plus unit tests.
  **Six primary production web resources were reviewed privately** (originals kept
  in the git-ignored `source-private/` area); each public example is a sanitized,
  reorganized derivative. Two examples note intentional deviations from source
  (duplicate-prevention fails closed; auto-fill uses `Xrm.WebApi.retrieveRecord`).
  Command-security docs state plainly that UI hiding is not authorization.
- **Development Finance & Revenue module** (`development-finance/`): a
  Stripe→Dataverse reconciliation case study — reconciliation lifecycle, matching
  model, exception handling, revenue engine, sanitized data dictionary, fictional
  sample records, and privacy controls. Plus
  `architecture/development-finance-lifecycle.md`.
- Recruiter-facing case study `portfolio/stripe-dataverse-website-case-study.md`.
- Reproducible finance tooling: `scripts/inspect_stripe_schema.py` (reads the
  private Stripe sample and emits **sanitized structure only** — never a value)
  and `scripts/validate_finance_samples.py`, with unit tests in `tests/`.
- Evidence discipline for the finance work: **483+** Stripe-related records,
  **89.7%** automatic match rate, and a **four-tier** matching process are
  **portfolio-documented** (not audited/reproduced/recalculated). A **separate**
  surviving sample of **74 charge objects** corroborates the schema only — it is
  not a subset of the 483+, not the 89.7% denominator, and not the full
  migration. Tier order/thresholds, exact query filters, the 89.7%
  numerator/denominator, and the 483+ object composition are **not preserved**.

### Changed

- Refreshed the Dataverse inventory from the revised source workbook (now carries
  descriptions for nearly every table: 0 blank, 3 literal `N/A`). Relationship/
  intersect tables are classified by **schema structure** (a `tr_` table embedding
  a second entity reference such as `tr_msnfp_award_msnfp_indicator`) and literal
  `N/A` descriptions are treated as no-description. Classification distribution is
  now **core 94 / support 9 / intersect 25 / unclear 1** (total 129); the sole
  unclear table is `tr_ActionItem` (`N/A` description).

### Security

- Generalized **8 especially sensitive clinical / behavioral-health** schema
  names in the public catalog and summary into public domains only
  (*Behavioral-health assessment*, *Clinical classification*, *Mental-status
  assessment*, *Counseling treatment goals*, *Medication-management record*). The
  exact internal schema identifiers are withheld from published files; the fact
  that each domain existed is preserved. The private schema-name → label mapping
  is maintained locally in a git-ignored config
  (`source-private/sensitive-generalizations.json`), loaded at runtime, and is
  **not committed**. Documented in `SECURITY.md` and `docs/evidence-register.md`.

### Verified

- Grant measurement design from two private grant sources: **9 headline KPI
  targets**, **19 supporting measurement/implementation items**, a curated
  **20-measure** reporting framework, and **23 measurable objectives** in the
  2026 proposal. The 2026 proposal **requested $100,000** (a request, not an
  award), proposed serving **150** individuals, and set an interim report
  (due 2026-12-31) and a final report (within 30 days of the 12-month period).
  These counts are distinct and not additive; dollar figures are grant-specific.

### Added

- Project governance and agent-instruction files: `AGENTS.md`, `CLAUDE.md`,
  `CONTRIBUTING.md`, `CHANGELOG.md`, `RIGHTS.md`.
- Reproducible Dataverse inventory tooling: `scripts/build_dataverse_inventory.py`
  with unit tests in `tests/`, producing `dataverse/custom-table-catalog.csv`
  and `dataverse/inventory-summary.md`.
- Application architecture documentation: `dataverse/application-sitemap.md` and
  `dataverse/application-entity-catalog.csv` covering the six operational areas
  and the 94 entities surfaced in the primary model-driven application.
- Initial **Outcomes, Grants & Compliance** module under `grants-outcomes/`:
  lifecycle, measurement model, reporting workflow, data dictionary, and a
  clearly fictional sample-records file.
- Mermaid architecture diagrams: `architecture/system-overview.md` and
  `architecture/grant-reporting-lifecycle.md`.
- Source evidence register: `docs/evidence-register.md`.
- `scripts/` and `tests/` directories.

### Verified

- 129 custom Dataverse tables using the `tr_` publisher prefix.
- 94 entities surfaced in the primary model-driven application.
- 6 major operational areas.

### Notes

- No reuse license granted yet (see `RIGHTS.md`).
- Public resource-directory records remain **out of scope** pending separate
  review.
