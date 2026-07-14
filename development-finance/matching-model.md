# Customer-Matching Model

How incoming Stripe payments were resolved to donor records.

> **Evidence tier:** The existence of a **four-tier** customer-matching process
> and an **89.7% automatic match rate** is **portfolio-documented** — recorded in
> surviving portfolio materials, and presented as documented, not independently
> audited, reproduced, or recalculated. The matching **inputs** below are
> corroborated by the surviving source structure and technical notes. The exact
> **order and thresholds of the four tiers are not preserved and are not
> invented here.**

## The problem

Processor payment data often carried incomplete or inconsistent contact
information. The workflow had to answer, for each payment: *which existing donor
or household does this belong to — and if none, what happens?*

## Matching inputs (corroborated)

The surviving structure and notes identify these matching signals:

- an existing **processor-customer relationship** (a stored link between a Stripe
  customer and a Dataverse Contact)
- a **normalized email** (billing email, falling back to receipt email)
- **billing name** and identity information
- **invoice / form metadata** from the payment
- existing **Dataverse Contact** records
- a controlled **manual-review / new-Contact** path for anything unresolved

### Email normalization (reconstructed)

Before searching, the email value was normalized so inconsistent casing or
whitespace did not defeat a match:

```text
normalized_email =
    lowercase(
        trim(
            billing_email
            ?? receipt_email
            ?? ""          # final null-safe fallback
        )
    )
```

The final empty-string fallback prevented `trim()` from receiving a null value
and failing the run.

## The four tiers (documented, order not preserved)

Portfolio materials document that matching ran as a **four-tier** process, and
that most payments resolved automatically while ambiguous or incomplete records
took an exception path. The exact tier **sequence** and any confidence
**thresholds** are **not preserved** in any available source.

> This case study does **not** invent a tier order. It documents that four tiers
> existed and lists the corroborated inputs the tiers drew on. Do not read the
> input list above as the tier sequence.

What can be stated:

- **Documented:** four tiers; an 89.7% automatic match rate (portfolio figure).
- **Corroborated:** the signals available to matching (customer link, normalized
  email, name, metadata, existing Contacts).
- **Not preserved:** the ordering of the tiers, their thresholds, the exact
  Dataverse query filters, and the numerator/denominator behind 89.7%.

## Why a tiered design fits

A tiered matcher tries the most reliable signal first and falls back to weaker
signals, sending anything ambiguous to review. That shape is consistent with the
documented result — a high automatic rate with a preserved exception path — even
though the precise tier definitions did not survive. See
[`exception-handling.md`](exception-handling.md) for the fallback path.

## Sample

`sample-records.json` includes fictional `donor_match_examples`, each labeled by
its **match signal** (not by a reconstructed tier number), plus fictional
exception records. No real donor, email, or identifier appears.
