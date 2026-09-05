# Service Navigation

This module documents two related but distinct systems that together support
case-management service navigation in the Dataverse environment:

1. **Resource Directory** — *where help exists.* A curated directory of
   organizations, programs, service categories, specializations, services,
   contact channels, locations, hours, and descriptive information.
2. **Goal Pathway** — *how to reach it.* A hierarchical model that turns a
   broad outcome into an actionable sequence: **Goal → Action Item → Need**.

They solve different navigation problems. The directory identifies available
help; the pathway explains the steps, prerequisites, and supporting resources
needed to pursue that help. Linking them lets a case-management workflow move
from **discovery** ("a mobility program exists") to **action** ("here is the
sequence of steps and documents needed to enroll"). The directory is a
structured knowledge base with taxonomy, curation, and maintenance
obligations — not merely a contact list.

## Verified scale (recomputed 2026-07-15)

From three private production sources — two exports plus a recovered
client-side copy-workflow script (structure and aggregates only; no record
values are published; see
[`evidence-and-limitations.md`](evidence-and-limitations.md)):

- **204** resource-directory rows, **199** distinct organizations,
  **175** distinct service descriptions, **8** top-level resource categories
- **186** goal-pathway rows: **32** Goals, **68** Action Items, **86** Needs
  (reconciliation passes: zero unrecognized types; levels sum to 186)
- **165** pathway rows carry a resource reference (16 distinct values, each
  join-verified to exactly one directory row — pathways covered **16 of 204**
  directory entries; coverage was selective, not universal)
- A production **copy workflow existed**: it copied a Goal template with its
  child Action Items and Needs into person-specific records, preserving
  parent references and checking for duplicates

## Module Contents

| File | What it covers |
|---|---|
| [`resource-directory-model.md`](resource-directory-model.md) | Generalized directory model: organization vs. program, taxonomy layers, contact volatility, maintenance |
| [`goal-pathway-model.md`](goal-pathway-model.md) | The Goal → Action Item → Need hierarchy, ordering, optional steps, phases |
| [`linkage-model.md`](linkage-model.md) | How directory, pathway, and individualized plans connect; template vs. copied records |
| [`taxonomy-and-classification.md`](taxonomy-and-classification.md) | Category / specialization / service-description layering and normalization rules |
| [`privacy-controls.md`](privacy-controls.md) | What is published, what is withheld, and why |
| [`metrics.md`](metrics.md) | The recomputed safe aggregates and exactly how each was calculated |
| [`data-dictionary.csv`](data-dictionary.csv) | Sanitized public field dictionary with production-value treatment per field |
| [`fictional-samples.json`](fictional-samples.json) | Fully invented sample records demonstrating the model |
| [`evidence-and-limitations.md`](evidence-and-limitations.md) | Evidence tiers: directly supported, reconstructed, withheld, unverified |

Architecture diagram: [`../architecture/service-navigation-lifecycle.md`](../architecture/service-navigation-lifecycle.md)

Tooling: `scripts/inspect_service_navigation.py` (reads the private exports
locally and emits **aggregates only**) and
`scripts/validate_service_navigation_samples.py` (privacy/structure validator
for this module), with tests in `tests/`.

## Sanitization standard

The private exports contain organization names, direct contact information,
addresses, URLs, procedural instructions, and internal Dataverse metadata.
**None of that is published.** This module publishes safe aggregate counts,
generalized field structure with invented public field names, taxonomy design,
architectural diagrams, and clearly fictional samples. See
[`privacy-controls.md`](privacy-controls.md).
