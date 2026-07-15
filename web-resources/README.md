# Web Resources

Sanitized, reconstructed **client-side patterns** for a model-driven Power Apps
environment: form routing, returning-record auto-fill, duplicate prevention,
date/time validation, cloud-flow refresh coordination, and command security.

> **Internal origin:** these scripts supported record-intake, scheduling, and
> command experiences in the model-driven application. Every example here is a
> **reconstruction with invented names** — no production web resource is
> published.

## Evidence model (read this first)

This module follows the repository's factuality rules
([`../AGENTS.md`](../AGENTS.md)). It is a **sanitized reconstruction**, not a
production export.

- **Pattern origin:** each example reconstructs a documented production
  web-resource *pattern*. The private originals were **not present in this build
  environment**; nothing was read or copied from them. The examples implement the
  described technique using standard Client API / Web API practice.
- **Sanitized reconstruction:** all schema names, form and record identifiers,
  role names, query values, and business rules are **invented**. Code is
  organized for readability and privacy.
- **Not preserved / intentionally withheld:** production schema, form and record
  GUIDs, internal role and business-unit names, protected service logic, and
  exact operational notification text. Scripts touching sensitive personal
  identifiers, workforce time/compensation, or protected service rules were
  **not reconstructed at all** (see [`privacy-controls.md`](privacy-controls.md)).

None of these examples is a deployable production export.

## The six patterns

| Pattern | Doc | Example |
|---|---|---|
| Form routing (new vs. existing → intake/main form) | [`form-routing.md`](form-routing.md) | [`examples/form-routing.js`](examples/form-routing.js) |
| Returning-record auto-fill (map prior values forward) | [`returning-record-autofill.md`](returning-record-autofill.md) | [`examples/returning-record-autofill.js`](examples/returning-record-autofill.js) |
| Duplicate prevention (async check before save) | [`duplicate-prevention.md`](duplicate-prevention.md) | [`examples/duplicate-prevention.js`](examples/duplicate-prevention.js) |
| Date/time validation (auto end-time, overnight, cleanup) | [`date-time-validation.md`](date-time-validation.md) | [`examples/date-time-validation.js`](examples/date-time-validation.js) |
| Cloud-flow refresh coordination (bounded polling) | [`flow-refresh-coordination.md`](flow-refresh-coordination.md) | [`examples/flow-refresh-coordination.js`](examples/flow-refresh-coordination.js) |
| Command security (role-aware visibility) | [`command-security.md`](command-security.md) | [`examples/command-security.js`](examples/command-security.js) |

## Reusable patterns

- [`patterns/client-api-patterns.md`](patterns/client-api-patterns.md) — formContext, attributes, controls, notifications.
- [`patterns/dataverse-web-api-patterns.md`](patterns/dataverse-web-api-patterns.md) — `Xrm.WebApi` retrieve/query, OData options.
- [`patterns/async-form-events.md`](patterns/async-form-events.md) — deferring saves, bounded retries, re-entrancy.

Architecture:
[`../architecture/model-driven-web-resource-lifecycle.md`](../architecture/model-driven-web-resource-lifecycle.md).

## Conventions

All examples share invented placeholders: `sample_person`, `sample_case_record`,
`sample_related_record`, `sample_schedule`, `sample_sensitive_identifier`,
`SAMPLE_INTAKE_FORM_ID`, `SAMPLE_MAIN_FORM_ID`, and role names `Sample
Administrator` / `Sample Reviewer`. Every `.js` file opens with a **SANITIZED
EXAMPLE** notice.

## Reproducible checks

`../scripts/validate_web_resource_examples.py` rejects GUIDs, organization schema
prefixes, environment URLs, non-fictional emails, production-looking role names,
forbidden terminology, missing sanitized notices, legacy synchronous network
calls, and private source references. Unit tests live in
[`../tests/test_web_resource_examples.py`](../tests/test_web_resource_examples.py).
