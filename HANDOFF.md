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

### 2026-09-04 · Claude Code (HANDOFF.md/TOOLS.md heading for `main` via PR — they only ever existed on this branch)
- **Changed:** No content change to the case study. A PAT-rotation verification pass found that this is the **only** one of the ten handoff-enabled repos whose `HANDOFF.md` and `TOOLS.md` are absent from the default branch — they were created on `feat/service-navigation` in September and never reached `main`. `git` + `Claude Code` rows bumped in `TOOLS.md`. A branch off `main` carrying byte-identical copies of both files has been pushed for a PR; per `AGENTS.md:173` this cannot be a direct commit to `main`, so **Taylor merges it**.
- **Commit:** `<this branch's commit>` · PR branch `chore/handoff-on-default-branch`
- **Next:** Unchanged. See `## Next Steps` above — and note this closes part of its first item, since the branch/merge state question is now answered concretely: `main` holds PRs #1–3, `feat/web-resources` and `feat/development-finance` are content-identical to `main` at root, and this branch is the only one carrying unmerged work.
- **Watch out:** ⚠️ **Why this mattered rather than being cosmetic.** The GitHub Contents API — the path Claude desktop/chat uses to write handoffs — reads the **default branch** when given no `?ref=`. So a desktop session here would `GET HANDOFF.md`, receive a 404 from `main`, and the skill's error table would translate that to *"this repo isn't handoff-enabled"* — a wrong diagnosis for a repo that is. Worse, the follow-up `PUT` would have **created a second `HANDOFF.md` on `main`**, silently forking the log away from the one on this branch. The skill has been corrected to pin an explicit branch on both calls. ⚠️ The two files are byte-identical across `main` and this branch on purpose, so the eventual merge sees no conflict in them unless one side is edited first. ⚠️ `AGENTS.md` on `main` already instructed Codex to maintain `HANDOFF.md` while `main` had none — that contradiction is what this resolves.

### 2026-09-02 22:20 ET · Claude Code (TOOLS.md tool inventory added)
- **Changed:** Added `TOOLS.md` (10 active rows) — Power Platform, Dataverse, Power Automate, Python 3, pytest, openpyxl, and the repo tooling, with what each is used for and when last used. `AGENTS.md` gained a `## 11. Handoff and Tool Inventory` section (this repo's AGENTS.md uses numbered sections, not the shared handoff-contract shape).
- **Commit:** `60b6ef3`
- **Next:** Unchanged. See the block above this log.
- **Watch out:** 🛑 `TOOLS.md` is a **public file in a public repo** and §4 sanitization applies to it in full. Name the platform, never the organization's instance: no tenant IDs, environment URLs, client names, or anything traceable to `source-private/`. The seeded table deliberately says "Documented, not connected from this repo" in the Access column for all three Microsoft rows.

### 2026-07-22 — Handoff created (retroactive bank)
Repo had accumulated ~3 sessions of heavy work (scaffold Jul 13, Service
Navigation module + privacy hardening Jul 14–15) with no HANDOFF and no memory
entry. Created this HANDOFF from the live repo state (branch/test/merge audit)
and added a `project` memory pointing here. No code changed. Work itself was
already committed to the repo and pushed to feature branches — this bank just
restores the knowledge-system trace so future sessions and the Observatory
dashboard can see the project exists and where it stands.
