# TOOLS — nonprofit-power-platform-ecosystem

> What this project uses and what for. Maintained by the handoff motion: whenever
> a tool is used here, add or bump its row.
> Types: `Skill` · `MCP` · `CLI` · `App` · `Service` · `Site` · `Library` · `Data` · `Task`
> A `~` before a date means inferred, not observed. `—` means unknown.
>
> ⚠️ **This file is public.** `AGENTS.md` §4 sanitization applies in full: name the
> platform, never the organization's instance of it. No tenant IDs, environment
> URLs, client names, or anything traceable to `source-private/`.

## Active

| Tool | Type | Used for | Access | Last used | Cost | Notes |
|---|---|---|---|---|---|---|
| **Microsoft Power Platform** | Service | The subject of the case study — the six operational areas being documented | Documented, not connected from this repo | ~2026-07-22 | Paid (nonprofit tier) | This repo describes the build; it does not touch a live environment |
| **Microsoft Dataverse** | Service | The `tr_` table estate the inventory is generated from | Documented, not connected | ~2026-07-22 | Paid (nonprofit tier) | 129 tables verified in the inventory summary |
| **Power Automate** | Service | The flow layer documented under `power-automate/` | Documented, not connected | ~2026-07-22 | Paid (nonprofit tier) | — |
| **Python 3** | CLI | Running the generator and validator scripts under `scripts/` | local install | 2026-07-15 | Free | No `requirements.txt` — stdlib plus `openpyxl` and `pytest` |
| **pytest** | Library | The test suite under `tests/` (7 test modules) | `import pytest` | 2026-07-15 | Free | Not pinned in a requirements file; installed ambiently |
| **openpyxl** | Library | Reading the source workbooks the inventory builders parse | `import openpyxl` | ~2026-07-14 | Free | Only path that touches spreadsheet input |
| **git** | CLI | Version control, handoff motion | `C:\Program Files\Git` | 2026-09-04 | Free | Working branch + PR, never direct to `main` (`AGENTS.md:173`) |
| **/handoff** | Skill | Banking work here — the log entry and this table | `~/.claude/skills/handoff` | 2026-09-04 | Free | ⚠️ Its Contents-API path must pin an explicit branch for this repo; the handoff files live on `main` **and** the working branch |
| **GitHub** | Service | Remote host for `TheLittlestAskew/nonprofit-power-platform-ecosystem` | github.com | 2026-07-22 | Free | Public repo; three PRs merged 2026-07-22, some branches still unmerged |
| **Claude Code** | App | Generator scripts, sanitization passes, evidence register | CLI / IDE extension | 2026-09-04 | Paid | — |
| **septentrion-sync** | Skill | Rolls this repo's tool table into the vault master | `~/.claude/skills/septentrion-sync` | 2026-09-02 | Free | ⚠️ In `TOOLS_REPOS` but **not** `REPOS` — its handoff state is not on the dashboard |

## Retired

| Tool | Type | Was used for | Retired | Why |
|---|---|---|---|---|
| ~~**wip-backup.ps1**~~ | Task | Automatic WIP snapshotting into this repo | 2026-07-14 | 🛑 Risked pushing `source-private/` material to a public remote. Disabled and renamed; never re-enable here |
