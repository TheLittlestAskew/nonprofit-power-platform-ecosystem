# Exception Handling

How records left the automatic path — and how they were resolved without
corrupting the reconciliation chain.

> **Evidence tier:** Reconstructed architecture from surviving technical notes.
> The 89.7% automatic match rate is portfolio-documented; this document describes
> the **exception path** that handled the remainder. It does not claim that all
> reconciliation was automated.

## When a record left the automatic path

A payment could not be auto-processed for several reasons:

| Exception | Cause |
|---|---|
| No matching donor found | No signal resolved to an existing Contact |
| Multiple possible matches | Signals resolved ambiguously to more than one Contact |
| Missing contact information | Too little identifying data to match safely |
| Missing payout/Deposit relationship | The charge's payout had not yet settled |
| Duplicate processor identifier | The record had already been imported |
| Incomplete or invalid source data | The record could not be transformed |
| Contact creation requiring review | A new Contact needed human confirmation |
| Reconciliation mismatch | Settlement, deposit, and transaction did not agree |

## Resolution paths

- **New-Contact creation with review** — when no donor matched, a Contact could
  be created through a controlled path that a human confirmed, rather than
  silently generating records.
- **Held for human review** — ambiguous (multiple-match) records were parked for
  a person to resolve rather than guessed.
- **Deferred reconciliation** — a charge whose payout had not settled could not
  bind to a Deposit yet, so it waited for settlement instead of binding
  incorrectly.
- **Skip / update on duplicate** — a record already present (by processor
  identifier) was updated or skipped, never duplicated. See
  [`reconciliation-lifecycle.md`](reconciliation-lifecycle.md) and duplicate
  prevention below.

## Duplicate prevention

Two complementary controls kept retries and reruns idempotent:

- **Watermarks** limited each API request to newer records.
- **Processor identifiers** let the flow check whether a Dataverse record already
  existed before creating one:

```text
find existing transaction by processor identifier
if found:  update or skip
else:      create transaction
```

The exact Dataverse query filters used for that lookup are **not preserved**.

## Why exceptions matter

The exception path is what makes the automatic rate trustworthy: a high match
rate is only credible if the unmatched remainder is visibly and safely handled
rather than force-matched. In the public samples, exceptions are represented with
**fictional** records (`exception_examples` in
[`sample-records.json`](sample-records.json)), never former-employer production
data.
