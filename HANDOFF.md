# HANDOFF — font-wizard

**Last updated: 2026-11-22 (America/New_York).**
**Repo:** `mhvnsnt/font-wizard` (PUBLIC), default branch `main`.
**Purpose of this file:** any agent that picks up work here reads this FIRST, then the linked docs. It states what we've done, where we're at, and what we're working toward — so the owner can say "go to this repo, pick up the work" and you just know. Update this file in the same PR whenever the state changes (add, don't delete).

## 1. What this repo is

Font Wizard — a free, open-source custom font foundry. Build, federate, and ship font packs with free tools and APIs. Created 2026-10-10. Public. ~1.2 GB on main (the `fonts/` collection is the bulk).

Layout: `fonts/` (the packs), `pipeline/`, `api/`, `tools/`, `assets/`, `docs/`, `TOOLS.md`, `LICENSE`, `requirements.txt`.

## 2. Where we're at

### DONE
- **Anti-clobber laws (2026-10-17, PR #16 merged):** the owner's anti-clobber laws landed after the DXMMII 54k-file wipe.
- **Working method statement (2026-10-27):** `WORKING-METHOD.md` landed.

### IN PROGRESS
- Nothing is actively in progress in this repo that the repo itself records. Last push was the 2026-10-27 sweep commit (via the 2026-11-20 push batch).
- **PRE-MADE PARTS FIRST rule (open PR #18).** Standing-rule PR, unmerged.

### BLOCKED
- Nothing recorded as blocked in this repo. No releases.

## 3. What we're working toward

Font packs the shows and games can actually ship with — built with free tools, federated, and documented. The bar: a pack only counts when it is built by the pipeline, stored in `fonts/`, and its source/license is written down next to it. Menus, HUDs, and buttons in the owner's games are built from real front-end code and real fonts — never hand-tooled lookalikes.

## 4. Standing rules that apply here

- **Branch → PR → merge, always.** Never push to main directly. Add-only, zero-conflict PRs, no force pushes.
- **Checkpoint-and-save law:** CHECKPOINT.md first, update after every step; the repo is the save; resume, never restart.
- **No-temp-storage law:** nothing in /tmp or any wipeable location, ever.
- **Real-source-only:** build from the real sources, wired up fully — no hand-tooled lookalikes.
- **Paid-tool equivalents:** find the free top-level industry-standard equivalent first; never bring the owner a purchase list.
- **Licence-not-a-gate:** licence status never blocks pulling in or using material that helps — licence/source is still logged honestly next to the item.
- **Never kill in-progress work.**

## 5. Key files and paths

| What | Where |
|---|---|
| Font packs | `fonts/` |
| Build pipeline | `pipeline/` |
| API / tools | `api/`, `tools/` |
| Assets / docs | `assets/`, `docs/` |
| Tool notes | `TOOLS.md` |
| Agent rules | `AGENTS.md` |
| Method doc | `WORKING-METHOD.md` |
| Open PR | #18 (PRE-MADE PARTS FIRST rule) |

## 6. Open decisions needing the owner

- **Which font packs to build next:** driven by what the shows and games need. His call.
- No other decisions are recorded in this repo.

## 7. How to pick up

1. Read this HANDOFF.md first, then `README.md` and `WORKING-METHOD.md`.
2. Check `fonts/` to see what packs already exist before building anything (never build a duplicate blind).
3. Check what other agents are already doing before starting anything.
4. Resume from the stated next step — never restart, never re-derive finished work.
5. Land work branch → PR → merge, add-only. Log source + license next to every pack.
6. Update this HANDOFF.md in the same PR when the state changes. Verify with your own eyes before claiming anything built.
