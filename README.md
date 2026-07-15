# Nonprofit Power Platform Ecosystem

A sanitized technical case study of a Microsoft Power Platform and Dataverse environment designed for a multi-site homeless-services nonprofit.

As sole systems developer and development operations administrator, I architected a six-area operational environment connecting fundraising, grants, outcomes, service delivery, finance, volunteers, employees, and communications.

## Architecture at a Glance

- **129 custom Dataverse tables** using the `tr_` publisher prefix
- **94 entities** organized within the primary model-driven application
- **6 operational areas** connected through one environment
- Custom grant KPI, outcomes, compliance, and reporting infrastructure —
  measurement design verified at **9 headline KPI targets**, **19 supporting
  measurement/implementation items**, a **20-measure** curated reporting
  framework, and **23** proposal objectives
- Structured community-resource and service-navigation data
- Donation and payment reconciliation workflows
- Power Automate flows, JavaScript web resources, and supporting documentation

## Operational Areas

1. **Development Finance & Revenue**
2. **Shelter & Case Management**
3. **Outcomes, Grants & Compliance**
4. **Volunteer & Community Engagement**
5. **Employee & Administrative Operations**
6. **Communications & Brand**

## Why This Repository Exists

This repository translates a large production Power Platform environment into a public, recruiter-friendly technical case study. It documents the architecture, design decisions, data models, automations, and reporting workflows without publishing confidential production records or raw employer exports.

## Start Here

New to this repository? Read in this order:

1. **[Outcomes, Grants & Compliance](grants-outcomes/README.md)** — the flagship module: how funder requirements become measured, audit-ready impact.
2. **[System Overview](architecture/system-overview.md)** — how the six operational areas connect through one Dataverse environment.
3. **[Dataverse Inventory Summary](dataverse/inventory-summary.md)** — how the 129 custom `tr_` tables were counted and classified (reproducible).
4. **[Application Sitemap & Entity Map](dataverse/application-sitemap.md)** — the 94 entities surfaced in the primary app, by area.
5. **[Development Finance & Revenue](development-finance/README.md)** — the Stripe→Dataverse reconciliation workflow (charges, payouts, donor matching, deposits, exceptions).
6. **[Source Evidence Register](docs/evidence-register.md)** — what every claim traces back to, and what remains unverified.

Governance: **[AGENTS.md](AGENTS.md)** (authoritative instructions) · **[SECURITY.md](SECURITY.md)** (publication policy) · **[RIGHTS.md](RIGHTS.md)** (no reuse license granted yet).

The central grant-management workflow is:

```text
FUNDER REQUIREMENTS
        ↓
PROGRAM DELIVERABLES
        ↓
KPIs AND MEASURES
        ↓
DATAVERSE RECORDS
        ↓
IMPACT ANALYSIS
        ↓
COMPLIANCE REPORTING
```

## Repository Modules

| Module | Purpose | Status |
|---|---|---|
| [`grants-outcomes/`](grants-outcomes/) | Lifecycle, measurement model, reporting workflow, data dictionary, sample records | **Initial module complete** |
| [`architecture/`](architecture/) | Simplified system + grant-reporting Mermaid diagrams | **Initial diagrams complete** |
| [`dataverse/`](dataverse/) | Custom-table catalog + inventory summary; application sitemap + entity catalog | **Inventory + sitemap complete** |
| [`scripts/`](scripts/) | Reproducible generators for the sanitized catalogs | **Complete + tested** |
| [`tests/`](tests/) | Unit tests for inventory classification/prefix logic | **Complete** |
| [`docs/`](docs/) | Governance context and the source evidence register | Evidence register complete; more planned |
| [`development-finance/`](development-finance/) | Stripe→Dataverse reconciliation lifecycle, matching model, exception handling, revenue engine, data dictionary, sample records, privacy controls | **Initial module complete** |
| [`service-navigation/`](service-navigation/) | Community-resource taxonomy and goal-pathway model | Placeholder — pending resource-directory review |
| [`power-automate/`](power-automate/) | Sanitized flow documentation and patterns | Placeholder — not started |
| [`web-resources/`](web-resources/) | Sanitized model-driven client-side patterns: form routing, returning-record auto-fill, duplicate prevention, date/time validation, cloud-flow refresh coordination, command security | **Initial module complete** |
| [`portfolio/`](portfolio/) | Recruiter-facing case-study copy and visuals | Stripe→Dataverse case study added |

## Publication and Sanitization Standard

This repository is a reconstruction and documentation project, not a production export.

- No client, donor, employee, volunteer, or guest records are published.
- Sample data uses invented values while preserving the original structure and logic.
- Screenshots and diagrams are sanitized, cropped, simplified, or rebuilt when necessary.
- Custom-table counts include core business tables, supporting process tables, and custom relationship/intersect tables.
- Standard Microsoft and nonprofit tables are described where they were materially extended, configured, or integrated.

See [`SECURITY.md`](SECURITY.md) for the repository's publication rules.

## Current Status

This repository is under active construction. **Complete so far:** the
**Outcomes, Grants & Compliance** module, the **Development Finance & Revenue**
module (Stripe→Dataverse reconciliation, with a reproducible sanitized schema
inspector, sample validator, and tests), the **Web Resources** module (sanitized
model-driven client-side patterns with a validator and tests), the Dataverse
inventory and application-sitemap documentation (with reproducible generator
scripts and tests), the architecture diagrams, and the source evidence register.
**Next:** service navigation (pending a separate resource-directory review) and
Power Automate documentation.

Placeholder modules above are labeled as such and should not be read as
completed work.

### Metric note

The two headline counts measure different things and are both verified:

- **129 custom `tr_` tables** — custom tables that *exist* in the environment
  (from the entity inventory).
- **94 entities** — entities *surfaced in the primary app's sitemap*, of which
  57 are custom `tr_` tables and 37 are Nonprofit Accelerator / standard /
  other-publisher entities.

See [`dataverse/inventory-summary.md`](dataverse/inventory-summary.md) and
[`dataverse/application-sitemap.md`](dataverse/application-sitemap.md).

### Grant measurement note

The grant measurement matrix defined **nine headline KPI targets** and **19
supporting measurement and implementation items** across case management and
counseling. A curated reporting framework translated that work into **20 tracked
measures**. The related 2026 proposal identified **23 measurable objectives** and
established interim and final reporting requirements. These four figures count
different things and are **not** additive. The 2026 proposal **requested
$100,000** (a request, not an award); dollar figures are grant-specific and are
not interchangeable between grants. See
[`grants-outcomes/measurement-model.md`](grants-outcomes/measurement-model.md)
and [`docs/evidence-register.md`](docs/evidence-register.md).

## Author

**Taylor Askew Ritchie**  
Operations · Systems · Grants · Data · Communications
