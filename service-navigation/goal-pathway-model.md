# Goal Pathway Model

**Evidence tier:** the three-level hierarchy, its field structure, and all
counts are **directly supported** by a private production export and
**verified** by recomputation ([`metrics.md`](metrics.md)). Public field names
are **invented**. The individualized-plan copy workflow is a **sanitized
reconstruction** (see [`linkage-model.md`](linkage-model.md)).

The goal pathway answers *"how do I reach it?"* Where the resource directory
identifies available help, the pathway decomposes a broad outcome into an
actionable, ordered sequence a case manager and participant can execute:

```text
Goal            "what we are trying to achieve"
  └── Action Item    "a concrete step toward it"
        └── Need          "what this step requires first"
```

The production export contains **186** pathway rows: **32** Goals,
**68** Action Items, and **86** Needs (totals reconcile to the analyzed row
count).

## The three levels

### Goal

The desired outcome. A well-formed goal is **broad enough to orient the whole
plan** (it names an outcome, not a task) yet **specific enough to connect to a
resource or service pathway** — "obtain stable transportation" rather than
"improve life." In the source, most Goals (30 of 32) link directly to a
directory resource, and Goals carry rationale fields explaining *why this
goal* matters for the pathway.

### Action Item

A concrete, executable step toward the goal: submit an application, attend an
orientation, gather records. Action Items:

- belong to exactly one Goal (parent-child, expressed in the hierarchy code);
- may carry an **order** within the goal and an optional **phase** grouping
  (phases appear on 21 of 186 source rows — used selectively, not uniformly);
- may link to an application, form, website, or supporting resource that the
  step is performed against (application/form/link fields exist in the source
  structure and are sparsely populated — 8, 17, and 47 rows respectively).

### Need

A prerequisite or supporting condition required to complete an Action Item: a
document, a payment, transportation, a piece of information. Needs are the
level where plans actually stall, so modeling them explicitly — instead of
burying them in step notes — is what makes the pathway *actionable*. Needs are
the most numerous level in the source (86 of 186 rows), which matches field
reality: one step commonly requires several things.

## Hierarchy mechanics

**Parent-child relationships and ordering.** The source encodes the hierarchy
in a dotted **hierarchy code** on each row: Goals are `1`, `2`, …; Action
Items are `1.1`, `1.2`, …; Needs are `1.1.1`, `1.1.2`, …. The code carries
three jobs at once: parentage (prefix), level (segment depth), and sibling
order (final segment). Recomputed pattern shapes confirm this: Goal rows are
single-segment, Action Items two-segment, Needs three-segment, with a small
number of deviations documented in
[`evidence-and-limitations.md`](evidence-and-limitations.md) (4 rows with a
blank code, 2 Needs with a letter-suffixed code such as `#.#.#a` — an
insertion between existing siblings).

**Pathway identifiers.** The top-level segment doubles as the **pathway
identifier**: every row of one pathway shares the Goal's leading number
(31 distinct top-level prefixes across the coded rows). A row is therefore
self-describing — type, pathway membership, parent, and position all recover
from `step_type` + `step_code`.

**Optional versus required steps.** An explicit `optional_step` flag exists in
the source (populated on 51 rows: 5 yes, 46 no; blank elsewhere). Blank is
operationally treated as *required* — the safe default, because skipping a
required step breaks a plan while performing an optional one merely costs
time. The flag lets one reusable pathway serve people in different situations
without forking the template.

**Linkage to a resource.** Pathway rows may reference a generalized directory
resource record (165 of 186 source rows do, across 16 distinct resources).
The reference appears at every level: on the Goal (which resource this pathway
pursues), and on Action Items and Needs where a *different* supporting
resource applies to a single step.

## Generalized pathway-step record

| Public field | Concept |
|---|---|
| `step_reference` | Stable identifier for the step record |
| `step_code` | Dotted hierarchy code (`1`, `1.2`, `1.2.3`) — parent, level, order |
| `step_type` | `Goal`, `Action Item`, or `Need` |
| `pathway_reference` | Top-level code segment shared by the whole pathway |
| `linked_resource` | Reference to a generalized directory resource |
| `step_title` | Short name of the goal/step/need |
| `step_summary` | What the step involves |
| `goal_summary` | Outcome statement (goal-level narrative) |
| `rationale` | Why this step / why this goal |
| `phase` | Optional coarse grouping of steps |
| `application_links` / `form_links` / `support_links` | Where the step is performed |
| `support_contact` | Step-specific contact channel |
| `optional_step` | Whether the step may be skipped |
| `note` | Free-text working notes |

One source column (a `Need` text column distinct from the Need row type) is
**unpopulated on all 186 rows** — an unused remnant documented in
[`evidence-and-limitations.md`](evidence-and-limitations.md), not part of the
working model.

## Reuse: template pathways and individual plans

The 186 rows analyzed here are **reusable templates** ("common goals"): the
generic, person-independent route to an outcome. Executing one for a specific
person means **copying** the template into an individualized plan — preserving
the hierarchy and codes, adding person-specific status, dates, and notes — so
the template stays clean for the next person. The copy workflow, and why
status must never live on the template, is covered in
[`linkage-model.md`](linkage-model.md).

## What is not published

The real pathways are withheld: goal wording, step instructions, eligibility
requirements, document lists, agency names, applications, forms, phone
numbers, and URLs. Structure and counts only. Fictional demonstrations of
every mechanic above — including a multi-Action-Item pathway, a multi-Need
step, and an optional step — are in
[`fictional-samples.json`](fictional-samples.json).
