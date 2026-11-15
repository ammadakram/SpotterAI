# Progress

_Last updated: 2026-11-15_

## Status
Phase: **Build — Slice 1 done** → next: Slice 2 (routes and checkpoints on the map).

## Done
- Claude context setup: CLAUDE.md, docs/ (PROGRESS, DECISIONS, ASSESSMENT), `/checkpoint` command.
- Requirements captured in `docs/ASSESSMENT.md`; research in `docs/RESEARCH.md`.
- All interpretation and stack questions answered (DECISIONS.md). Skills installed in `.claude/skills/`.
- Architecture in `docs/ARCHITECTURE.md`, all §5 open points decided (2026-11-15).
- Slice 1: Django + DRF backend (uv, ruff, pytest, health endpoint), Vite + React + TS frontend (Tailwind, oxlint, Prettier, Vitest, MapLibre map), GitHub Actions CI, Open-Meteo measured. CI green. HERE verified, fixtures recorded (Dallas → Denver routes, no-route case, autosuggest).
- Architecture walkthrough complete (Parts 1–7: shape, backend, domain, pipeline, API, frontend + map, testing).
- Walkthrough fixes to ARCHITECTURE.md: `decidedBy` value list, `isLoadEscalated` example, heatmap `startsAt` = the hour bucket containing now, place-search debounce + `limit=5`.

## Next up
1. Slice 2 (`docs/PLAN.md`): domain geometry/timeline/checkpoints (TDD — agree test seams with the user first), HERE client, `/api/places` + `/api/plans` (routes + checkpoints), form + map.
   Needs a flexible-polyline decoder (HERE's `flexpolyline` package).
2. Record an Open-Meteo fixture for the Dallas → Denver checkpoints in Slice 3, once checkpoints exist.

## Open questions
- Open-Meteo: very long trips at 10 mi spacing can still exceed 600 calls/min (0.5° cells chosen; paid key if it shows up).
- Hosting (VPS vs Vercel + Render). Needed by Slice 3 (first deploy).
