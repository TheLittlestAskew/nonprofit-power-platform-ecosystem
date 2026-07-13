# Changelog

All notable changes to this repository are documented here.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
and this project does not yet follow semantic versioning (it is documentation,
not released software).

## [Unreleased]

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
