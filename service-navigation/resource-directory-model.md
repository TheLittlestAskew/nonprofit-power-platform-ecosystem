# Resource Directory Model

**Evidence tier:** field structure **directly supported** by a private
production export; public field names below are **invented** (sanitized
reconstruction); aggregates are **verified** by recomputation
(see [`metrics.md`](metrics.md)).

The resource directory answers *"where does help exist?"* It is a curated
knowledge base of community services — not a contact list. Each entry captures
who provides a service, what the service is, how it is classified, and how to
reach it, with enough descriptive context for a case manager to judge fit
before making a referral.

## The generalized resource record

One directory row represents **one program-level resource**. Public field
names are invented; each maps to a real source concept documented in
[`data-dictionary.csv`](data-dictionary.csv).

| Public field | Concept |
|---|---|
| `resource_reference` | Stable identifier for the resource record |
| `program_title` | The specific program or offering being cataloged |
| `organization_title` | The organization operating the program |
| `top_level_categories` | One or more broad service categories (multi-select) |
| `specialization` | Narrower focus within a category |
| `service_description` | What the resource actually does for a person |
| `contact_channels` | Phone / email availability (volatile; see below) |
| `location` | Physical address or service location |
| `web_link` | Public web presence |
| `hours_availability` | When the service can actually be reached |
| `summary` | Free-text descriptive overview |
| `average_rating` | Internal curation signal for usefulness/quality |
| `active_status` | Whether the entry is currently maintained and referable |

The analyzed export was an *active-filtered* view, which is direct evidence
that active/inactive state management existed; the exact status field design is
a reconstruction.

## Why organization and program are separate fields

A single organization legitimately operates multiple programs, and the
recomputed aggregates prove this shape exists in production: **204** resource
rows resolve to **199** distinct organizations and **201** distinct program
titles. Keeping the two concepts in separate columns means:

- The *program* is the referable unit (a person enrolls in a program, not an
  org chart), while the *organization* is the accountability and relationship
  unit (MOUs, partnership contacts, reputation).
- Duplicate organization values across rows are **legitimate**, not data
  errors — they represent one provider with several distinct offerings. A
  dedupe pass that keyed on organization alone would silently destroy programs.
- Rollups ("how many referral options does this partner give us?") stay
  possible without parsing combined name strings.

## Three taxonomy layers, three different jobs

Category, specialization, and service description look similar but answer
different questions (full treatment in
[`taxonomy-and-classification.md`](taxonomy-and-classification.md)):

- **Top-level category** (8 distinct in source) — the browse/filter axis.
  Small, stable, controlled vocabulary.
- **Specialization** — the within-category qualifier that distinguishes two
  resources in the same category (populated on 202 of 204 rows).
- **Service description** (175 distinct in source) — the free-text answer to
  "what will they actually do for this person?" It is nearly as cardinal as
  the row count because real services genuinely differ.

Collapsing these layers into one field forces a choice between a vocabulary
too coarse to describe services and one too fine to browse.

## Multi-category resources

The source stores top-level categories as a **multi-select** (semicolon-
separated in the export); 3 of 202 categorized rows carry more than one
category. Treatment rules:

- A resource appears under *every* category it holds — filtering must test
  membership, not equality.
- Category **counts** must deduplicate by resource when reporting "resources
  per category," or multi-category rows are double-counted.
- Multi-category assignment should stay rare and reviewed; if many rows need
  several categories, the taxonomy itself is too coarse.

## Contact information changes faster than taxonomy

Presence rates in the source make the volatility gradient visible: nearly
every row has a summary (200/204) and specialization (202/204), while hours
are populated on only 115/204 and email on 127/204. Phone numbers, staff
emails, and hours change on a provider's schedule, not the directory's;
categories and service descriptions change only when the *service itself*
changes. Design consequences:

- Contact fields need a *freshness* discipline (last-verified date), not just
  a value.
- A stale category is a taxonomy bug to fix once; a stale phone number is an
  operational hazard that recurs monthly.
- Verification effort should be budgeted to the volatile fields first.

## Directory maintenance requires review dates and ownership

A directory entry is an assertion — "this help exists, here, on these terms" —
and assertions decay. A referable directory therefore needs:

- **Review dates** per entry, so staleness is measurable instead of anecdotal.
- **Named ownership** of curation, so "who confirms this entry?" has an
  answer.
- **Active/inactive status** rather than deletion, preserving history while
  keeping dead entries out of referral workflows.
- **A rating or usefulness signal** (present in the source structure) so
  curation effort concentrates on the resources case managers actually use.

These are design recommendations grounded in the source structure (status
filtering and rating fields existed); the operational review cadence itself is
**not** evidenced by the exports and is not claimed as production fact.

## What is not published

The real organizations, programs, contacts, addresses, URLs, descriptions, and
category labels remain private. See [`privacy-controls.md`](privacy-controls.md).
Fictional examples of every concept above are in
[`fictional-samples.json`](fictional-samples.json).
