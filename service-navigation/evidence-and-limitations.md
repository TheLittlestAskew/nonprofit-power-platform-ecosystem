# Evidence and Limitations — Service Navigation

Every claim in this module carries one of four labels. The private sources are
two production Dataverse Excel exports held in the git-ignored
`source-private/service-navigation/` area (filenames, hashes, and the full
sanitization record live in the ignored private evidence manifest there; see
also `docs/evidence-register.md`, Sources 3 and 4).

## Directly supported

Recomputed on 2026-07-15 by `scripts/inspect_service_navigation.py` from the
private workbooks (method in [`metrics.md`](metrics.md)):

- The two private workbooks existed: a resource-directory export and a
  goal-pathway export, each a single data worksheet plus a hidden Dataverse
  re-import sheet.
- The **directory field structure**: program title, organization title,
  multi-select category, specialization, service description, phone, email,
  address, website, hours, descriptive summary, rating, copy-target, plus
  Dataverse identifier/checksum/modified-on metadata columns.
- The **pathway field structure**: hierarchy code, type, resource lookup,
  name, description, goal description, note, website, phone, phase,
  applications, forms, two rationale columns, need-text column (unused),
  optional-step flag, plus the same Dataverse metadata columns.
- **Aggregates:** 204 resource rows; 199 distinct organizations (200
  populated); 175 distinct service descriptions (trim-only; 174 casefolded);
  8 top-level categories (3 multi-category rows); 186 pathway rows = 32 Goals
  + 68 Action Items + 86 Needs (reconciles exactly); all presence rates in
  [`metrics.md`](metrics.md).
- The presence of the **Goal, Action Item, and Need hierarchy concepts**,
  encoded as row types plus a dotted hierarchy code (`#`, `#.#`, `#.#.#`
  shapes; 31 distinct top-level codes; 4 blank codes; 2 letter-suffixed
  sibling insertions).
- **Resource-to-pathway linkage where demonstrated:** 165 of 186 pathway rows
  reference a directory resource, across 16 distinct resources
  (Goal 30/32, Action Item 55/68, Need 80/86).

## Sanitized reconstruction

Original artifacts built to explain the source structure without reproducing
it:

- All public entity and field names (`resource_reference`, `step_code`, …)
- The diagrams in [`linkage-model.md`](linkage-model.md) and
  `architecture/service-navigation-lifecycle.md`
- [`data-dictionary.csv`](data-dictionary.csv)
- [`fictional-samples.json`](fictional-samples.json) (entirely invented)
- The normalized taxonomy examples (invented labels)
- The maintenance workflow and governance recommendations
- The individualized-plan example and copy workflow: the source contains a
  copy-target field (populated on 1 row) and the template design implies
  copying, but **no person-level plan data was present in or derived from the
  analyzed exports**

## Not published / intentionally withheld

- Production records (every row value of both workbooks)
- Organization and program names
- Contact data (phones, emails)
- Addresses and URLs
- Detailed procedural requirements (application/form instructions, step
  guidance, prerequisites, documentation requirements)
- Internal identifiers, row checksums, modification timestamps, the hidden
  re-import sheets, and exact record-to-record relationships
- The real category vocabulary (publishable only after a separate review)

## Unverified

Not demonstrated by the analyzed workbooks; never presented as fact:

- Any implementation behavior beyond what the exports show (forms, views,
  automation, security model of these tables)
- **Universal pathway coverage** — the evidence shows the opposite shape:
  pathways cover 16 of 204 directory resources, and 21 pathway rows carry no
  resource link. Coverage was selective.
- Current accuracy of any external contact information in the private data
  (the exports are point-in-time; provider contacts decay)
- Usage or outcome metrics (referral volumes, completion rates, ratings'
  operational meaning) — no usage data exists in the evidence
- The operational review cadence for directory curation (recommended in
  [`resource-directory-model.md`](resource-directory-model.md), not evidenced)

## Known source anomalies (reported exactly, not repaired)

- 4 pathway rows have a blank hierarchy code (1 Goal, 3 Action Items)
- 2 Need rows carry a letter-suffixed code (sibling insertion between
  existing steps)
- 1 organization appears on 2 directory rows (legitimate multi-program shape)
- The pathway export's need-text column is populated on 0 of 186 rows
- The directory copy-target field is populated on exactly 1 of 204 rows
