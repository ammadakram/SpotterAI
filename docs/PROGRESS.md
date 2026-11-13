# Progress

_Last updated: 2026-11-13_

## Status
Phase: **Setup** → next: background research, then build.

## Done
- Repo initialized (backend/ + frontend/ planned, .gitignore).
- Claude context setup: CLAUDE.md, docs/ (PROGRESS, DECISIONS, ASSESSMENT), `/checkpoint` command.

- Assessment PDF in `docs/`; requirements, risk rules, ranking and evaluation weights captured in `docs/ASSESSMENT.md`.

- Background research written to `docs/RESEARCH.md` (domain, routing/weather APIs, map/heatmap, hosting, architecture sketch).

## Next up
1. Confirm stack picks from RESEARCH.md (HERE truck routing, Open-Meteo, MapLibre, Vercel + Render) → DECISIONS.md.
2. Resolve the ambiguities in `docs/ASSESSMENT.md` (band edges, wind vs gusts, No Travel ranking, miles per checkpoint, avg risk scale, HOS in ETA) → DECISIONS.md.
3. Sign up for a HERE API key; scaffold backend + frontend.
4. Build the risk engine + ranking first, with unit tests.

## Open questions / blockers
- Ambiguities in the brief (see ASSESSMENT.md) — not decided yet.

## Deadline
- TBD (fill in from the email)
