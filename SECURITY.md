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

## Privacy Scan

Before a release, tracked files are scanned for common leakage patterns:
email addresses, phone numbers, street addresses, personal names, raw payment
identifiers, Stripe charge IDs, tokens, and secrets. A clean scan **reduces**
risk but does not guarantee privacy — it is one control among the review
checklist above, not a substitute for human judgment.

## Reporting a Concern

Open a repository issue describing the file and concern without reposting any sensitive content.
