# Security and Publication Policy

This repository documents a former production environment through sanitized examples, reconstructed diagrams, and technical explanation.

## Never Publish

- Personally identifiable information
- Donor, client, guest, employee, volunteer, or applicant records
- Authentication secrets, API keys, tokens, connection strings, or environment variables
- Production URLs that expose private systems
- Raw payment processor payloads containing real customer or transaction identifiers
- Unredacted grant, finance, personnel, or case-management records
- Full production solution exports without component-level review

## Safe Publication Patterns

- Replace real values with clearly invented sample data.
- Preserve field structure and logic only when it is necessary to explain the design.
- Rebuild screenshots when redaction would leave a confusing or visually damaged artifact.
- Use simplified architecture diagrams in recruiter-facing documentation.
- Keep full technical diagrams only when they contain no confidential data.
- Describe standard Microsoft and nonprofit tables by function rather than publishing unnecessary metadata dumps.

## Review Checklist

Before committing any artifact, confirm:

- [ ] No personal or confidential information is present.
- [ ] No secret, credential, tenant ID, environment ID, or private endpoint is present.
- [ ] Sample records are invented and cannot be mistaken for production data.
- [ ] Employer-owned source material has been transformed into original explanatory documentation where appropriate.
- [ ] The artifact supports a specific technical claim made in the case study.
- [ ] The artifact is understandable without access to the original environment.

## The `source-private/` Directory

- `source-private/` contains production-derived exports and reference materials.
- It is listed in `.gitignore` and **must never** be committed, copied into a
  public path, or exposed in Git history.
- Scripts in `scripts/` may **read** from it locally to generate sanitized
  public outputs; they must never write raw source contents to a tracked path.
- Confirm it is ignored before working with it: `git check-ignore source-private/`.

## Generalized Clinical / Behavioral-Health Schema Names

A small number of custom tables model **especially sensitive clinical or
behavioral-health** domains. For those tables the exact internal schema
identifier is **withheld** from every published artifact (the catalog CSV and the
inventory summary) and a generalized **public domain label** is published
instead. This preserves the fact that the domain existed while avoiding
publication of the precise instrument or record name.

**8 sensitive structures** are generalized, into these public domains:

- Behavioral-health assessment
- Clinical classification
- Mental-status assessment
- Counseling treatment goals
- Medication-management record

Rules applied:

- The private mapping (production schema name → generalized public label) is
  **not stored in any tracked file.** It lives only in the git-ignored
  `source-private/sensitive-generalizations.json` and is loaded by
  `scripts/build_dataverse_inventory.py` **at runtime**. The exact identifiers
  are never hard-coded in the generator, printed, logged, or committed.
- If that config is missing the generator **fails with a clear error** rather
  than publishing exact identifiers.
- The sanitization is **reproducible** and covers every generated public file,
  including the manual-review lists in the summary.
- The public catalog CSV carries a `Public Identifier` column marking each row as
  `as-published` or `generalized`.
- The **source workbook is never altered**; generalization happens only in the
  generated public outputs.
- Exact schema names are retained for ordinary nonclinical tables unless a
  separate privacy concern is found.

## Payment-Processor Data (Stripe)

Raw payment-processor exports carry donor PII, partial card data, and processor
identifiers. They are handled under strict rules:

- The raw Stripe export and the detailed reconstruction notes live only under
  `source-private/` and are **never** committed.
- Stripe fields are classified into seven privacy categories (see
  `development-finance/privacy-controls.md`). Only a field's **category** and
  **name** may be published — **never a value**. Field names are Stripe's public
  API vocabulary; values (amounts, ids, emails, card data, metadata, timestamps)
  are always withheld or replaced with invented samples.
- `scripts/inspect_stripe_schema.py` reads the private sample and emits sanitized
  structure only; it never prints or writes a field value.
- `scripts/validate_finance_samples.py` fails if any sample record contains a
  real-looking Stripe id, email, GUID, or card-like digit run.
- Operational figures (e.g. record counts and match rates) are published only as
  **portfolio-documented** claims, never as audited or recalculated results, and
  never accompanied by confidential FY totals, funder names, or grant amounts.

## Client-Side Web Resources

Original model-driven JavaScript web resources carry production schema names,
form/record GUIDs, role names, and operational logic. They are handled under
strict rules:

- Original exports live only in the git-ignored private source area and are
  **never** committed, copied into `web-resources/`, or named in any tracked file.
- Public examples are **sanitized reconstructions** with invented names
  (`sample_*`, `SAMPLE_*_FORM_ID`, `Sample Administrator`). Every `.js` file opens
  with a `SANITIZED EXAMPLE` notice.
- Never publish: production schema names or publisher prefixes (`tr_`, `new_`,
  `msnfp_`, …), form/record GUIDs, environment URLs, business-unit or real
  security-role names, protected service rules, or exact production notification
  text.
- **UI command hiding is not authorization.** Any operation a privileged command
  performs must be enforced server-side (security roles, table/column
  permissions, or plug-in logic).
- **Sensitive fields and domain-specific rules are removed from reviewed
  derivatives** (a reviewed script keeps its generalized technique, not its
  protected fields or rules). **Separately scoped high-risk scripts** whose
  primary purpose was sensitive identifiers, workforce compensation, or protected
  service controls are **not reconstructed at all**.
- `scripts/validate_web_resource_examples.py` enforces these rules over
  `web-resources/` and is covered by unit tests.

## Privacy Scan

Before a release, tracked files are scanned for common leakage patterns:
email addresses, phone numbers, street addresses, personal names, raw payment
identifiers, Stripe charge IDs, tokens, and secrets. A clean scan **reduces**
risk but does not guarantee privacy — it is one control among the review
checklist above, not a substitute for human judgment.

## Reporting a Concern

Open a repository issue describing the file and concern without reposting any sensitive content.
