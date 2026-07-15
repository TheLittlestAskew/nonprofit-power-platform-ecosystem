# Metrics — Recomputed Safe Aggregates

**Evidence tier: Verified.** Every figure below was independently recomputed
on 2026-07-15 from the two private production exports using
`scripts/inspect_service_navigation.py` (run locally with the sources
present). No figure is copied from a prior review without recomputation. No
record value is published — aggregates only.

## Methodology

- **Worksheets analyzed:** each workbook's single data worksheet (the primary
  export sheet). Each workbook also carries a hidden Dataverse re-import
  metadata sheet, which was **excluded** from analysis and is withheld
  entirely (it embeds internal logical names and an encoded key).
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
- **Reconciliation:** type totals are checked against the analyzed row count
  (they must sum exactly).

## Resource directory

Analyzed: the resource export's data worksheet — 204 data rows, 0 blank.

| Aggregate | Value |
|---|---|
| Resource rows | **204** |
| Organization cells populated | 200 / 204 |
| Distinct organizations (normalized) | **199** |
| Organizations appearing on >1 row | 1 (2 rows) |
| Distinct program titles | 201 / 204 populated |
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
| Reconciliation | 32 + 68 + 86 = 186 ✓ |
| Rows linked to a directory resource | 165 (Goal 30/32, Action Item 55/68, Need 80/86) |
| Distinct resources referenced | 16 |
| Distinct top-level pathway codes | 31 |
| `optional_step` populated | 51 (yes 5 / no 46) |
| `phase` populated | 21 |

Hierarchy-code pattern shapes (digits replaced by `#`, letters by a letter
marker — shapes only, never values):

| Level | Shape | Rows |
|---|---|---|
| Goal | `#` | 31 (+1 blank code) |
| Action Item | `#.#` | 65 (+3 blank code) |
| Need | `#.#.#` | 84 |
| Need (sibling insertion) | `#.#.#` + letter suffix | 2 |

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
