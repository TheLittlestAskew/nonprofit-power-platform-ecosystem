# Goal Pathway Model

**Evidence tier:** the three-level hierarchy, its field structure, and all
counts are **directly supported** by a private production export and
**verified** by recomputation ([`metrics.md`](metrics.md)). A recovered
private production client script **directly demonstrates** the copy workflow:
selecting a reusable Goal template, copying it with its child Action Items and
Needs into person-specific records, preserving parent references, checking for
duplicates, and associating the copies with a person-specific case context.
Public field names, the public status vocabulary, and the fictional examples
are **invented** (see [`linkage-model.md`](linkage-model.md) and
[`evidence-and-limitations.md`](evidence-and-limitations.md)).

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

**Parent-child relationships.** In production, parentage is a dedicated
**parent reference** on each record: the recovered copy script retrieves a
Goal's children by querying that parent reference (with a type filter), not by
parsing codes. The analyzed export view does not include the parent-reference
column, so the reference itself is evidenced by the script rather than the
spreadsheet. Alongside it, every row carries a dotted **hierarchy code**
(`1`, `1.1`, `1.1.1`) that mirrors the tree in human-readable form: level
(segment depth), pathway membership (leading segment), and sibling order
(final segment). The copy workflow copies this code onto the person-specific
records and uses it for duplicate checks.

**Hierarchy-integrity results (recomputed).** The code convention holds
cleanly across the coded rows: 31 coded Goals, 65 coded Action Items, and 86
coded Needs; **0 malformed codes, 0 duplicate codes**; every coded Action
Item's leading segment matches an existing coded Goal, and every coded Need's
two-segment prefix matches an existing coded Action Item (0 missing parents).
Four rows carry a **blank code** (1 Goal, 3 Action Items) and remain
explicitly unresolved — their tree position is presumably held by the
parent-reference field, which the export does not show. Two Needs carry a
letter-suffixed code (`#.#.#` plus a letter): an **observed shape** whose
meaning is not established by the evidence and is not interpreted here.

**Pathway identifiers.** The top-level code segment doubles as the **pathway
identifier**: every coded row of one pathway shares the Goal's leading number
(31 distinct top-level prefixes). A **validly coded** row is self-describing —
type, pathway membership, and position recover from `step_type` + `step_code`;
blank-code rows are not, and depend on the parent reference.

**Optional versus required steps.** An explicit `optional_step` flag exists in
the source, with three observed states: **yes (5), no (46), and blank /
unspecified (135)**. Blank values are reported as unspecified. A future
implementation may choose a fail-safe default (treating unspecified as
required, since skipping a required step breaks a plan while performing an
optional one merely costs time), but that policy is **not preserved in the
source evidence** and is a design recommendation only. The flag lets one
reusable pathway serve people in different situations without forking the
template; the copy workflow carries the flag onto the person-specific copies.

**Linkage to a resource.** Pathway rows may reference a generalized directory
resource record: 165 of 186 source rows do, carrying 16 distinct normalized
reference values, and a deterministic cross-workbook join confirms each of the
16 matches exactly one directory row (see [`metrics.md`](metrics.md)). The
reference appears at every level: on the Goal (which resource this pathway
pursues), and on Action Items and Needs where a *different* supporting
resource applies to a single step. The production model was a **hybrid**:
the reference was kept *and* selected contact/link fields were copied onto
person-specific records as snapshots — see
[`linkage-model.md`](linkage-model.md).

## Generalized pathway-step record

| Public field | Concept |
|---|---|
| `step_reference` | Stable identifier for the step record |
| `step_code` | Dotted hierarchy code (`1`, `1.2`, `1.2.3`): level, order, and pathway membership; also used by the copy workflow's duplicate check |
| `parent_step` | Parent reference (the production parentage mechanism; evidenced by the copy workflow, not present in the analyzed export view) |
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

The 186 rows analyzed here are **reusable templates**: the generic,
person-independent route to an outcome. A recovered production client script
**directly demonstrates** the reuse mechanism: it selects a template Goal,
verifies its type, checks for an existing copy in the person's case context
(by the hierarchy code, with a confirmation prompt on a hit), then creates
person-specific copies of the Goal, each child Action Item, and each child
Need — re-binding the new records to each other so the hierarchy survives the
copy, and to the person's case context. Selected template fields (including
the code, the optional flag, rationale, and contact/link fields) are copied
onto the new records. The template itself is never modified by the copy. The
full linkage model — and why status lives on the copies, never the template —
is covered in [`linkage-model.md`](linkage-model.md).

## What is not published

The real pathways are withheld: goal wording, step instructions, eligibility
requirements, document lists, agency names, applications, forms, phone
numbers, and URLs. Structure and counts only. Fictional demonstrations of
every mechanic above — including a multi-Action-Item pathway, a multi-Need
step, and an optional step — are in
[`fictional-samples.json`](fictional-samples.json).
