# Progress

_Last updated: 2026-11-15_

## Status
Phase: **Build — Slice 1** (scaffold done; HERE checks waiting on an API key).

## Done
- Claude context setup: CLAUDE.md, docs/ (PROGRESS, DECISIONS, ASSESSMENT), `/checkpoint` command.
- Requirements captured in `docs/ASSESSMENT.md`; research in `docs/RESEARCH.md`.
- All interpretation and stack questions answered (DECISIONS.md). Skills installed in `.claude/skills/`.
- Architecture in `docs/ARCHITECTURE.md`, all §5 open points decided (2026-11-15).
- Slice 1 so far: Django + DRF backend (uv, ruff, pytest, health endpoint), Vite + React + TS frontend (Tailwind, oxlint, Prettier, Vitest, MapLibre map), GitHub Actions CI, Open-Meteo measured. CI green.
- Architecture walkthrough complete (Parts 1–7: shape, backend, domain, pipeline, API, frontend + map, testing).
- Walkthrough fixes to ARCHITECTURE.md: `decidedBy` value list, `isLoadEscalated` example, heatmap `startsAt` = the hour bucket containing now, place-search debounce + `limit=5`.

## Next up
1. Finish Slice 1: user adds `HERE_API_KEY` to `backend/.env`; then check HERE per-piece durations (spans vs actions) and max `alternatives`; record Dallas → Denver HERE + Open-Meteo responses as test fixtures.
2. Decide on request throttling for our own API (protects the HERE and Open-Meteo quotas once hosted).
3. Slice 2 (`docs/PLAN.md`).

## Open questions
- Open-Meteo: very long trips at 10 mi spacing can still exceed 600 calls/min (0.5° cells chosen; paid key if it shows up).
- Hosting (VPS vs Vercel + Render). Needed by Slice 3 (first deploy).
