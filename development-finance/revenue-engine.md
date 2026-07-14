# Annual Giving Revenue Engine

The operating model that the reconciliation workflow plugged into: how annual
giving was run as one repeatable revenue system rather than a set of disconnected
tasks.

> **Evidence tier:** Reconstructed from portfolio documentation. This is a
> qualitative operating model; it contains no confidential revenue figures,
> funder names, or production records. Dollar totals and funder-level detail from
> internal reporting are intentionally **excluded**.

## The idea

Annual giving connected campaigns, donor records, payment channels,
acknowledgments, stewardship, reconciliation, and reporting so they functioned as
a single system — making donor activity visible, trackable, and actionable.

## Core operating model

| Function | What it covered |
|---|---|
| Campaign planning | Annual-giving appeals, giving-society tracking, donor messaging |
| Gift processing | Multiple payment channels (card, recurring/mobile, campaign, and manual) |
| Donor records | Matching, CRM cleanup, transaction history, giving patterns |
| Acknowledgment & stewardship | Tax letters, thank-yous, impact updates, recognition |
| Revenue tracking | Donations, grants, events, and other income streams |
| Reporting | Dashboard views for revenue, source performance, and reconciliation |
| Optimization | Workflow improvements, less manual reconciliation, cleaner data |

## Payment channels

Gifts arrived through several channels, integrated with the CRM. The
Stripe → Dataverse reconciliation workflow (see
[`reconciliation-lifecycle.md`](reconciliation-lifecycle.md)) handled the
card-processor path: retrieving charges and payouts, matching donors, and
creating linked Transactions and Deposits. Manual channels (for example checks
and cash) followed a separate entry path into the same Transaction model.

## Where reconciliation fits

The revenue engine is the business context; reconciliation is the mechanism that
kept it honest:

```text
Campaign activity
    -> Gifts across channels
        -> Donor matched or created            (matching-model.md)
            -> Transactions + Deposits created (reconciliation-lifecycle.md)
                -> Bank reconciliation
                    -> Acknowledgments
                        -> Fundraising reporting
```

## What this demonstrates

Turning annual giving from disconnected tasks into a measurable operation:
faster reporting, cleaner donor records, more consistent stewardship, and better
visibility into how revenue moved through the organization — without publishing
any confidential financial detail.

> Headline operational figures (**483+** records, **89.7%** match rate,
> **four-tier** matching) are **portfolio-documented** and are described in the
> recruiter-facing case study
> ([`../portfolio/stripe-dataverse-website-case-study.md`](../portfolio/stripe-dataverse-website-case-study.md)),
> not audited or recalculated here.
