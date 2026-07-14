# Privacy Controls — Processor Data

How this module documents a payment-processor integration **without** publishing
any donor, card, or account data.

> **Evidence tier:** Reference. This records the controls applied; it makes no
> operational claims.

## The boundary

Two artifacts hold the sensitive material, and **neither is committed**:

- `source-private/stripejson.txt` — a Stripe export of charge objects (donor
  PII, partial card data, processor identifiers, amounts, timestamps).
- `source-private/stripe-dataverse-process-reconstruction.md` — detailed
  reconstruction notes (real internal field names, expressions, endpoints).

Both live under `source-private/`, which is git-ignored and verified before use
(`git check-ignore source-private/`). Scripts may **read** them locally to
produce sanitized public output; they never write raw values to a tracked path.

## Field categories

Every Stripe field is classified into one of seven privacy categories. Only
category and **field name** are ever published — never a value. This taxonomy is
implemented in `../scripts/inspect_stripe_schema.py` and published, name-only, in
[`data-dictionary.csv`](data-dictionary.csv).

| Category | Value publishable? | Examples (names only) |
|---|---|---|
| Safe structural | Yes | `object`, `status`, `paid`, `captured`, `reporting_category` |
| Pagination / API | Yes | `has_more`, `total_count` |
| Financial | Schema only (names yes, values no) | `amount`, `fee`, `net`, `currency` |
| Personal / contact | No | billing `name`, `email`, `phone`, `address`, `tax_id` |
| Processor identifier | No | `id`, `customer`, `payment_intent` |
| Payment-method / card | No | `last4`, `brand`, `fingerprint`, `exp_month` |
| Metadata / free-text | No | `metadata.*`, `statement_descriptor` |

"Schema only" means the field **name** may appear in a data dictionary while its
**value** is always withheld or replaced with an invented sample.

## What is never published

- donor names, emails, phones, addresses, tax IDs
- card brand, last4, expiry, or fingerprint
- Stripe object IDs, customer IDs, payment-intent IDs
- exact internal Dataverse schema/field names or record GUIDs
- production API URLs or endpoints
- confidential FY revenue totals, funder names, or grant amounts
- any real amount, receipt, or timestamp tied to a record

## What is published

- Stripe's public **field names** with a privacy category (a sanitized schema)
- **generalized** Dataverse target concepts (no internal schema names)
- **reconstructed** architecture and pseudocode
- **invented** sample records, clearly flagged `sample_data: true`

## Automated controls

- `../scripts/inspect_stripe_schema.py` reads the private sample and emits only
  field name / category / presence — it never prints a value.
- `../scripts/validate_finance_samples.py` fails the build if any sample record
  contains a real-looking Stripe id, email, GUID, or card-like digit run, or if a
  sample id lacks a fiction marker.
- The repository privacy scan checks all **tracked** files for leakage patterns
  before release (see [`../SECURITY.md`](../SECURITY.md)).

A clean scan reduces risk but does not replace human review — it is one control
among several.
