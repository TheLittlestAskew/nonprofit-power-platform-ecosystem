# Taxonomy and Classification

**Evidence tier:** the three-layer structure and all counts are **directly
supported** and **verified** by recomputation ([`metrics.md`](metrics.md)).
The example labels below are **invented** — the real category vocabulary is
withheld pending separate review (see
[`privacy-controls.md`](privacy-controls.md)).

## Three layers, from coarse to fine

The directory classifies every resource on three layers that serve different
retrieval jobs:

```text
Top-level category      8 distinct values     browse / filter axis
  └── Specialization    per-resource          disambiguation within a category
        └── Service description   175 distinct   what the resource actually does
```

Invented illustration (no real label appears in this repository):

```text
Category:        Transportation Support
Specialization:  Rural route access
Service:         Weekly scheduled rides to medical and benefits appointments
```

### Top-level category — the controlled vocabulary

Eight distinct values classify all 202 categorized rows in the source. This
layer is deliberately small: it is the axis a case manager browses when the
question is broad ("what food help do we know?"). Its value comes from
stability — categories change only when the *service landscape* changes, so
counts, dashboards, and muscle memory built on them keep working.

The category field is a **multi-select**: 3 of 202 categorized rows carry
more than one category (exported as a semicolon-separated list). Rules for
handling that are in
[`resource-directory-model.md`](resource-directory-model.md).

### Specialization — the disambiguator

Populated on 202 of 204 rows. Two resources in the same category are usually
*not* interchangeable, and specialization is where that difference is stated
compactly — the population served, the modality, the constraint. It remains a
short curated phrase, not a second free-text description.

### Service description — the ground truth

175 distinct values across 202 populated rows (trim-only normalization; 174
after case-insensitive normalization — the near-identity of the two counts
shows casing noise is minimal). The high cardinality is the point: services
genuinely differ, and this layer is where the difference is fully expressed.
It is search material, not filter material.

## Why the layers must not collapse

- Category alone cannot answer "will this program help *this* person" — too
  coarse.
- Service description alone cannot drive browsing or reporting — 175 values
  is not a filter list.
- Specialization without the other two is context-free.

Each layer is cheap to maintain precisely because the other two exist.

## Normalization rules (as recomputed)

The aggregate counts in this module were produced with explicit, deterministic
normalization, so they are reproducible:

| Field | Rule | Result |
|---|---|---|
| Organization | trim → collapse internal whitespace → casefold | 199 distinct of 200 populated |
| Service description | trim only (headline) | 175 distinct of 202 populated |
| Service description | trim + whitespace-collapse + casefold (cross-check) | 174 distinct |
| Top-level category | split on `;` → trim → casefold per token | 8 distinct tokens |
| Pathway `step_type` | trim + casefold; the source label for the middle level is plural (normalized to the singular *Action Item* in public docs) | Goal 32 / Action Items 68 / Need 86 |

Organization values appearing on multiple rows *can* be legitimate (one
organization, multiple programs); in this export the one repeated value does
not carry distinct program titles, so it is reported neutrally
(see [`metrics.md`](metrics.md)). Normalization deduplicates for *counting*,
never for merging rows.

## Curation guidance

- Keep the top-level list under ~10 values; pressure to add a ninth-plus
  category is usually a specialization trying to escalate.
- Review multi-category assignments explicitly; they should stay rare.
- Normalize organization spelling at entry time (pick-lists or lookup to an
  organization record) so distinct-organization counts stay honest without
  fuzzy matching.
- Treat service descriptions as owned prose: rewritten when the service
  changes, not appended to.
