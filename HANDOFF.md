# HANDOFF — nonprofit-power-platform-ecosystem

> Sanitized public technical case study of a multi-site homeless-services
> nonprofit's Microsoft Power Platform / Dataverse environment. Documentation,
> not released software. **`AGENTS.md` is authoritative** — read it before any
> work. Absolute rule: never commit anything from `source-private/`.
> Handoff is **enabled** for this repo.

## Status

Repo is a recruiter-facing case study of a 6-area Power Platform environment
(129 `tr_` Dataverse tables, 94 app entities). Current working branch is
**`feat/service-navigation`** (clean tree, 5 commits ahead of `main`, pushed to
`origin/feat/service-navigation`). The Service Navigation module is built and
has been through a third-source evidence-correction pass: the Goal → Action Item
→ Need pathway model and the 204-entry resource directory are documented with a
unit-tested cross-workbook join backing the "16 of 204" coverage claim, and
several earlier over-claims were retracted (hybrid reference+snapshot linkage,
optional-step semantics, multi-program wording, inspector hardening). Six Python
test suites cover finance samples, inventory classification, service-navigation
inspector + samples, Stripe schema, and web-resource examples.

Three feature branches exist and are **not currently merged into local `main`**:
`feat/service-navigation` (current), `feat/web-resources`, `feat/development-finance`.
History references merged PRs #1–3, so origin/main state may differ from local —
reconcile before assuming anything is or isn't live.

## Next Steps

- [ ] Reconcile branch/merge state: confirm what's actually on `origin/main` and
      whether `feat/service-navigation` (and the other two feature branches)
      need PRs opened/merged, or are already reflected via PRs #1–3.
- [ ] Decide whether Service Navigation is "done" or needs one more evidence
      pass before merging to main.
- [ ] Continue `feat/development-finance` (Stripe → Dataverse reconciliation
      workflow docs) — branch exists, unmerged.
- [ ] Keep `docs/evidence-register.md` in sync as any new claim lands (every
      claim must trace to a source or be marked unverified).

## Context

> 🔒 **Privacy is the load-bearing constraint.** This repo publishes a real
> nonprofit's production environment as a sanitized case study. `source-private/`
> holds the raw evidence and is NEVER committed (see `.gitignore` + AGENTS.md +
> SECURITY.md). Sources are identified in output by role + SHA-256 only —
> filenames, paths, and export timestamps are withheld. Operating near-HIPAA
> without paid tooling; donor/guest privacy and grant-reporting compliance are
> the reason the sanitization rules are strict.

> 📐 **Verified metrics (do not drift):** 129 custom `tr_` tables · 94 entities
> in the primary model-driven app · 6 operational areas · 9 headline KPI targets
> · 20-measure reporting framework · 23 proposal objectives · 204-entry resource
> directory (199 orgs, 8 categories) · 186-row Goal→Action Item→Need pathway
> model (32/68/86). Numbers are audit-anchored — change them only with a source.

> 🧭 **Six operational areas:** Development Finance & Revenue · Shelter & Case
> Management · Outcomes/Grants & Compliance (flagship module) · Volunteer &
> Community Engagement · Employee & Administrative Operations · Communications &
> Brand.

---

## Log

### 2026-07-22 — Handoff created (retroactive bank)
Repo had accumulated ~3 sessions of heavy work (scaffold Jul 13, Service
Navigation module + privacy hardening Jul 14–15) with no HANDOFF and no memory
entry. Created this HANDOFF from the live repo state (branch/test/merge audit)
and added a `project` memory pointing here. No code changed. Work itself was
already committed to the repo and pushed to feature branches — this bank just
restores the knowledge-system trace so future sessions and the Observatory
dashboard can see the project exists and where it stands.
