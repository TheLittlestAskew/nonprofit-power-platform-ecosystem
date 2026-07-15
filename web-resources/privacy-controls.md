# Privacy Controls — Web Resources

How client-side scripts are documented **without** exposing production schema,
identifiers, roles, or operational logic.

> **Evidence tier:** Reference. This records the controls applied; it makes no
> operational claims.

## The boundary

Original web-resource exports are private. They live only in the repository's
git-ignored private source area (see [`../SECURITY.md`](../SECURITY.md)) when
present, and are **never** committed, copied into `web-resources/`, or referenced
by filename in any tracked file. In this build the originals were **not present
locally**, so the module was reconstructed from documented pattern descriptions
rather than from source — nothing was read or copied.

## What every public example is

- A **reconstruction** of a documented technique, using invented names.
- Opened with a **SANITIZED EXAMPLE** notice.
- Written with modern, readable JavaScript (`async/await`, `Xrm.WebApi`, explicit
  null checks, bounded retries, centralized constants).

## What is never published

- production table or column schema names, or publisher prefixes (`tr_`, `new_`,
  `msnfp_`, etc.)
- production form GUIDs or record GUIDs
- environment URLs or endpoints
- business-unit names or real security-role names
- organization-specific service rules
- exact production notification, banner, or alert wording
- employee names or real contact information
- real Web API query values

## What is published

- generalized Client API / Web API **techniques**
- invented placeholder names (`sample_person`, `sample_case_record`,
  `SAMPLE_INTAKE_FORM_ID`, `Sample Administrator`, …)
- reconstructed pseudocode and readable examples

## Intentionally not reconstructed

Some documented scripts were **excluded entirely** because reconstructing them
would risk exposing sensitive operations even in generalized form. These include
scripts that:

- mask or handle **sensitive personal identifiers**,
- drive **workforce time-and-compensation** forms,
- encode **protected service-qualification** logic, or
- gate record removal / closure workflows tied to protected outcomes.

Their existence is acknowledged here; their logic, schema, and wording are not
reproduced.

## Automated controls

`../scripts/validate_web_resource_examples.py` scans `web-resources/` and rejects
GUIDs, organization schema prefixes, environment URLs, non-fictional emails,
production-looking role names, forbidden terminology, missing sanitized notices,
legacy synchronous network calls, and private source references. It is covered by
unit tests and complements — but does not replace — human review and the
repository-wide privacy scan in [`../SECURITY.md`](../SECURITY.md).
