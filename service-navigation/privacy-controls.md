# Privacy Controls — Service Navigation

This module is built from two private production exports that mix several
sensitivity classes in the same rows:

- internal record identifiers (Dataverse GUIDs)
- row checksums and modification metadata
- public-but-curated organization information
- direct contact information (phones, emails)
- physical addresses
- URLs
- detailed procedural instructions (applications, forms, step guidance)
- potentially sensitive prerequisites and documentation requirements

The governing decision: **the public repository does not publish the
row-level collection.** Even where a given organization's information is
publicly available elsewhere, the *curated dataset* — which resources were
selected, how they were rated and classified, how pathways sequence steps and
prerequisites, and the internal relationships between records — is private
operational work product and stays private.

## Allowed in public files

| Published | Where |
|---|---|
| Safe aggregate counts (recomputed, reproducible) | [`metrics.md`](metrics.md), module docs |
| Generalized field structure with invented public names | [`data-dictionary.csv`](data-dictionary.csv), model docs |
| Generalized taxonomy design (layer structure, counts) | [`taxonomy-and-classification.md`](taxonomy-and-classification.md) |
| Hierarchy counts and pattern shapes | [`goal-pathway-model.md`](goal-pathway-model.md) |
| Invented samples, clearly flagged | [`fictional-samples.json`](fictional-samples.json) |
| Architectural diagrams (original renderings) | [`linkage-model.md`](linkage-model.md), `architecture/` |
| Maintenance and governance recommendations | model docs |

## Withheld from public files

- Organization and program lists (names, in any form)
- Direct contacts (phone numbers, email addresses)
- Physical addresses
- Actual websites and URLs
- Detailed application/form instructions and step guidance
- Agency-specific prerequisites and documentation requirements
- Internal identifiers (GUIDs) and row checksums
- Production modification timestamps
- Exact record-to-record mappings (which real resource a real pathway serves)
- The real category vocabulary (taxonomy labels are publishable only after a
  separate review; none are published here)
- Any person-specific data (none was present in the analyzed exports, which
  are template/directory data — but the individualized-plan design in
  [`linkage-model.md`](linkage-model.md) is case data by definition and no
  real plan is represented anywhere in this module)

## Enforcement

- The private exports live only under `source-private/service-navigation/`
  (git-ignored; verified untracked before and after the build). Original
  filenames, byte counts, SHA-256 hashes, and the full sanitization record are
  kept in an **ignored private evidence manifest** in that directory.
- `scripts/inspect_service_navigation.py` reads the exports locally and emits
  **aggregates only** — it is safe by construction and never prints a cell
  value, GUID, checksum, timestamp, email, phone, URL, organization name, or
  raw column header. Unit tests prove leakage patterns cannot appear in its
  output using entirely invented fixtures.
- `scripts/validate_service_navigation_samples.py` scans every public file in
  this module for GUIDs, checksum/base64-like runs, emails outside the
  reserved `example.invalid` domain, phone-like digit runs, non-fictional
  URLs, and production schema prefixes, and validates the fictional samples
  structurally (hierarchy integrity, parent references, fiction markers).
- Both are wired into the repository test suite (`tests/`).

See also the repository-wide policy in [`../SECURITY.md`](../SECURITY.md) and
the evidence accounting in
[`evidence-and-limitations.md`](evidence-and-limitations.md).
