# Metrics — Recomputed Safe Aggregates

**Evidence tier: Verified.** Every figure below was independently recomputed
on 2026-07-15 from the two private production exports using
`scripts/inspect_service_navigation.py` (run locally with the sources
present). No figure is copied from a prior review without recomputation. No
record value is published — aggregates only.

## Methodology

- **Worksheet selection:** the data sheet is selected by **visibility and
  generalized schema**, never by size — the sheet must be visible and its
  header must classify to the expected directory or pathway field set; if no
  visible sheet or more than one matches, the inspector stops with an explicit
  error. Each workbook also carries a hidden Dataverse re-import metadata
  sheet, which is **excluded** by state and schema and is withheld entirely
  (it embeds internal logical names and an encoded key).
- **Blank rows:** excluded by rule (a row is blank when every cell is empty
  or whitespace). Both exports contained **0** blank rows, so exclusion
  changed nothing — the rule exists so reruns stay deterministic.
- **Duplicate organizations:** normalized by trim → internal-whitespace
  collapse → casefold before counting distinct values. Rows are never merged;
  duplicates are counted, not removed.
- **Unique service descriptions:** headline count uses **trim-only**
  normalization; a stricter trim + whitespace-collapse + casefold cross-check
  is reported alongside it.
- **Top-level categories:** the multi-select category cell is split on `;`,
  each token trimmed and casefolded, and distinct tokens counted.
- **Type values:** trimmed and casefolded. The source's middle-level label is
  plural ("Action Items"); public docs use the singular *Action Item* for the
  concept. No other Type variants exist in the source.
- **Reconciliation:** passes only when **every row carries a recognized type**
  (zero unrecognized) **and** the Goal + Action Item + Need counts sum exactly
  to the analyzed row count.
- **Optional-step states:** yes, no, and **blank** are reported as three
  separate states. Blank values are reported as *unspecified* — they are never
  folded into "no" or "required." A future implementation may choose a
  fail-safe default, but that policy is not preserved in the source evidence.
- **Cross-workbook join:** the pathway resource-reference lookup displays the
  referenced record's primary name, which corresponds to the directory's
  program-title column. Each distinct normalized reference value is joined
  against normalized directory program titles and classified as *matched*
  (exactly one directory row), *ambiguous* (more than one), or *unmatched*
  (none). Denominator: the 204 analyzed directory rows. The join is
  deterministic and unit-tested; only counts are emitted, never the values
  being matched.

## Resource directory

Analyzed: the resource export's data worksheet — 204 data rows, 0 blank.

| Aggregate | Value |
|---|---|
| Resource rows | **204** |
| Organization cells populated | 200 / 204 |
| Distinct organizations (normalized) | **199** |
| Organization values appearing on multiple rows | 1 (2 rows) |
| Repeated organizations with >1 distinct program title | **0** |
| Program-title cells populated | 204 / 204 |
| Distinct normalized program titles | 201 |
| Service-description cells populated | 202 / 204 |
| Distinct service descriptions (trim-only) | **175** |
| Distinct service descriptions (trim+casefold+ws-collapse) | 174 |
| Category cells populated | 202 / 204 |
| Distinct top-level categories | **8** |
| Rows with multiple categories | 3 |

Field presence (populated cells / 204):

| Public field | Populated |
|---|---|
| `program_title` | 204 |
| `average_rating` | 204 |
| `specialization` | 202 |
| `service_description` | 202 |
| `summary` | 200 |
| `organization_title` | 200 |
| `web_link` | 192 |
| `contact_channels` (phone) | 184 |
| `location` | 171 |
| `contact_channels` (email) | 127 |
| `hours_availability` | 115 |
| copy-target field | 1 |

## Goal pathway

Analyzed: the pathway export's data worksheet — 186 data rows, 0 blank.

| Aggregate | Value |
|---|---|
| Total pathway rows | **186** |
| Goal rows | **32** |
| Action Item rows | **68** |
| Need rows | **86** |
| Reconciliation | **PASS** — 0 unrecognized types and 32 + 68 + 86 = 186 |
| Rows with a resource reference | 165 (Goal 30/32, Action Item 55/68, Need 80/86) |
| Distinct normalized reference values | 16 |
| Distinct top-level pathway codes | 31 |
| `optional_step` states | **yes 5 / no 46 / blank-unspecified 135** |
| `phase` populated | 21 |

Hierarchy-code pattern shapes (digits replaced by `#`, letters by a letter
marker — shapes only, never values):

| Level | Shape | Rows |
|---|---|---|
| Goal | `#` | 31 (+1 blank code) |
| Action Item | `#.#` | 65 (+3 blank code) |
| Need | `#.#.#` | 84 |
| Need (observed variant) | `#.#.#` + letter suffix | 2 |

The letter-suffixed codes are an **observed shape**; their semantics are not
established by the evidence and are not interpreted.

### Hierarchy integrity (code convention; counts only)

A code is *valid* for its level when it parses as dotted numeric segments
(with an optional single trailing letter) and its depth matches the level.
Parentage is checked by numeric prefix among valid codes. (The production
parent mechanism is a dedicated parent-reference field demonstrated by the
recovered copy workflow; that field is not present in the export view, so
these checks cover the code convention.)

| Check | Result |
|---|---|
| Coded Goals / Action Items / Needs | 31 / 65 / 86 |
| Blank codes | 4 (1 Goal, 3 Action Items) — explicitly unresolved |
| Malformed codes | **0** |
| Duplicate valid codes | **0** |
| Action Items whose Goal parent code exists | 65 of 65 (0 missing) |
| Needs whose Action Item parent code exists | 86 of 86 (0 missing) |

### Cross-workbook resource-reference join

| Measure | Value |
|---|---|
| Denominator | 204 analyzed directory rows (join key: normalized program title, the lookup's primary name) |
| Distinct pathway references | 16 |
| Matched exactly one directory row | **16** |
| Ambiguous (more than one row) | 0 |
| Unmatched | 0 |

Every distinct reference resolves to exactly one directory row, so the
pathways covered **16 of the 204 directory entries**.

Field presence (populated cells / 186): `step_title` 186, `step_summary` 126,
`goal_summary` 109, `rationale` (why-step) 34, `rationale` (why-goal) 26,
`support_links` (web) 47, `form_links` 17, `support_contact` (phone) 11,
`application_links` 8, `note` 23, unused need-text column **0**.

## Consistency against the prior review

The prior review's expected targets — ~204 resource rows, ~199 distinct
organizations, ~175 unique service descriptions, 8 top-level categories, and
186 / 32 / 68 / 86 pathway rows — were all **confirmed by this independent
recomputation**. The only definitional nuance: 175 distinct services holds
under trim-only normalization (174 under the stricter rule), and the 199
organization count is measured over the 200 rows with the organization cell
populated.

Two earlier claims were **corrected** in this pass: the repeated organization
value does **not** carry more than one distinct program title (so repeated
rows are reported neutrally, not as a "multi-program shape"), and the
"16 of 204" coverage statement is now backed by the deterministic join above
rather than asserted from the reference count alone.
