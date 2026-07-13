# Changelog

All notable changes to this repository are documented here.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
and this project does not yet follow semantic versioning (it is documentation,
not released software).

## [Unreleased]

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
