# Evidence and Limitations — Service Navigation

Every claim in this module carries one of four labels. The private sources are
**three** production artifacts held in the git-ignored
`source-private/service-navigation/` area: two Dataverse Excel exports and a
recovered client-side copy-workflow script (filenames, hashes, and the full
sanitization record live in the ignored private evidence manifest there; see
also `docs/evidence-register.md`, Sources 3, 4, and 12).

## Directly supported

Recomputed on 2026-07-15 by `scripts/inspect_service_navigation.py` from the
private workbooks (method in [`metrics.md`](metrics.md)), plus a privately
reviewed production script:

- The two private workbooks existed: a resource-directory export and a
  goal-pathway export, each a single visible data worksheet plus a hidden
  Dataverse re-import sheet (the inspector selects the data sheet by
  visibility and generalized schema, never by size).
- The **directory field structure**: program title, organization title,
  multi-select category, specialization, service description, phone, email,
  address, website, hours, descriptive summary, rating, copy-target, plus
  Dataverse identifier/checksum/modified-on metadata columns.
- The **pathway field structure**: hierarchy code, type, resource lookup,
  name, description, goal description, note, website, phone, phase,
  applications, forms, two rationale columns, need-text column (unused),
  optional-step flag, plus the same Dataverse metadata columns.
- **Aggregates:** 204 resource rows; 199 distinct organizations (200
  populated; the one repeated organization value does **not** carry more than
  one distinct program title); 204 program-title cells populated with 201
  distinct titles; 175 distinct service descriptions (trim-only; 174
  casefolded); 8 top-level categories (3 multi-category rows); 186 pathway
  rows = 32 Goals + 68 Action Items + 86 Needs (reconciliation passes: zero
  unrecognized types and the three levels sum to the row count); all presence
  rates in [`metrics.md`](metrics.md).
- The presence of the **Goal, Action Item, and Need hierarchy concepts**,
  encoded as row types plus a dotted hierarchy code. **Hierarchy-integrity
  counts:** 31/65/86 validly coded rows by level, 0 malformed, 0 duplicates,
  and every coded child's prefix matches an existing coded parent (0 missing);
  4 blank-code rows remain explicitly unresolved.
- **Optional-step states:** yes 5 / no 46 / blank-unspecified 135. Blank is a
  third state, not evidence of "required."
- **Resource references, join-verified:** 165 of 186 pathway rows contain a
  resource reference (Goal 30/32, Action Item 55/68, Need 80/86), carrying 16
  distinct normalized reference values; a deterministic cross-workbook join
  matches each of the 16 to exactly one of the 204 directory rows
  (0 ambiguous, 0 unmatched).
- **The copy workflow existed.** A recovered production client-side script
  directly demonstrates: selecting a reusable Goal template (with a type
  check); copying the Goal into a person-specific record; retrieving child
  Action Items and child Needs through a dedicated **parent-reference field**
  (the production parentage mechanism, which the export view does not
  include); creating the copies so each child binds to its newly created
  parent (hierarchy preserved); checking for duplicates by hierarchy code
  within the person's case context (with confirmation); associating the copies
  with a person-specific case context; and copying selected pathway fields —
  including contact/link fields — onto the new records (the **hybrid
  reference + snapshot model**; see [`linkage-model.md`](linkage-model.md)).

## Sanitized reconstruction

Original artifacts built to explain the source structure without reproducing
it:

- All public entity and field names (`resource_reference`, `step_code`,
  `parent_step`, …)
- The public status vocabulary and the fictional individualized-plan example
  in [`fictional-samples.json`](fictional-samples.json) (the copy workflow is
  evidenced; the production status fields and plan record design are not
  shown by the evidence)
- The diagrams in [`linkage-model.md`](linkage-model.md) and
  `architecture/service-navigation-lifecycle.md`
- [`data-dictionary.csv`](data-dictionary.csv)
- The normalized taxonomy examples (invented labels)
- The maintenance workflow and governance recommendations, including the
  reference-only / reference-plus-explicit-snapshot design recommendation
  (a recommendation, **not** a claim about the production model)

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
- From the copy-workflow script: the production schema (table, field, and
  namespace names), form logic and identifiers, person/case terminology,
  option-set values, notification/dialog text, and the exact field mappings

## Unverified

Not demonstrated by the analyzed sources; never presented as fact:

- Any implementation behavior beyond what the exports and the reviewed script
  show (forms, views, other automation, security model of these tables)
- **Universal pathway coverage** — the evidence shows the opposite shape:
  the join confirms pathways covered 16 of the 204 directory entries, and 21
  pathway rows carry no resource reference. Coverage was selective.
- The semantics of the two letter-suffixed Need codes (an observed shape;
  the reviewed script does not demonstrate insertion semantics)
- The tree position of the 4 blank-code rows (presumably held by the
  parent-reference field, which the export view does not include)
- Current accuracy of any external contact information in the private data
  (the exports are point-in-time; provider contacts decay; copied snapshot
  fields in person records may be stale)
- Usage or outcome metrics (referral volumes, completion rates, ratings'
  operational meaning, how often the copy workflow ran) — no usage data
  exists in the evidence
- The operational review cadence for directory curation (recommended in
  [`resource-directory-model.md`](resource-directory-model.md), not evidenced)

## Known source anomalies (reported exactly, not repaired)

- 4 pathway rows have a blank hierarchy code (1 Goal, 3 Action Items)
- 2 Need rows carry a letter-suffixed code (observed shape; semantics
  uninterpreted)
- 1 organization value appears on 2 directory rows, without distinct program
  titles
- The pathway export's need-text column is populated on 0 of 186 rows
- The directory copy-target field is populated on exactly 1 of 204 rows
