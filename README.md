# Nonprofit Power Platform Ecosystem

A sanitized technical case study of a Microsoft Power Platform and Dataverse environment designed for a multi-site homeless-services nonprofit.

As sole systems developer and development operations administrator, I architected a six-area operational environment connecting fundraising, grants, outcomes, service delivery, finance, volunteers, employees, and communications.

## Architecture at a Glance

- **129 custom Dataverse tables** using the `tr_` publisher prefix
- **94 entities** organized within the primary model-driven application
- **6 operational areas** connected through one environment
- Custom grant KPI, outcomes, compliance, and reporting infrastructure
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

| Module | Purpose |
|---|---|
| [`docs/`](docs/) | Business context, scope, governance, and implementation notes |
| [`architecture/`](architecture/) | Simplified application and data-model diagrams |
| [`dataverse/`](dataverse/) | Table catalog, domain groupings, naming conventions, and relationships |
| [`grants-outcomes/`](grants-outcomes/) | KPI framework, measure dictionary, reporting workflow, and sample records |
| [`development-finance/`](development-finance/) | Donor operations, payment reconciliation, and revenue workflows |
| [`service-navigation/`](service-navigation/) | Community-resource taxonomy and goal-pathway model |
| [`power-automate/`](power-automate/) | Sanitized flow documentation, expressions, and implementation patterns |
| [`web-resources/`](web-resources/) | Selected JavaScript, HTML, and SVG resources |
| [`portfolio/`](portfolio/) | Recruiter-facing case-study copy and selected visuals |

## Publication and Sanitization Standard

This repository is a reconstruction and documentation project, not a production export.

- No client, donor, employee, volunteer, or guest records are published.
- Sample data uses invented values while preserving the original structure and logic.
- Screenshots and diagrams are sanitized, cropped, simplified, or rebuilt when necessary.
- Custom-table counts include core business tables, supporting process tables, and custom relationship/intersect tables.
- Standard Microsoft and nonprofit tables are described where they were materially extended, configured, or integrated.

See [`SECURITY.md`](SECURITY.md) for the repository's publication rules.

## Current Status

This repository is under active construction. The first complete module will be **Outcomes, Grants & Compliance**, followed by Dataverse architecture, service navigation, and development-finance automation.

## Author

**Taylor Askew Ritchie**  
Operations · Systems · Grants · Data · Communications
