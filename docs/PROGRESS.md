# Progress

_Last updated: 2026-11-16_

## Status
Phase: **Build — Slice 2 done** → next: Slice 3 (weather, risk, recommendation, first deploy).

## Done
- Claude context setup: CLAUDE.md, docs/ (PROGRESS, DECISIONS, ASSESSMENT), `/checkpoint` command.
- Requirements captured in `docs/ASSESSMENT.md`; research in `docs/RESEARCH.md`.
- All interpretation and stack questions answered (DECISIONS.md). Skills installed in `.claude/skills/`.
- Architecture in `docs/ARCHITECTURE.md`, all §5 open points decided (2026-11-15).
- Slice 1: Django + DRF backend (uv, ruff, pytest, health endpoint), Vite + React + TS frontend (Tailwind, oxlint, Prettier, Vitest, MapLibre map), GitHub Actions CI, Open-Meteo measured. CI green. HERE verified, fixtures recorded (Dallas → Denver routes, no-route case, autosuggest).
- Architecture walkthrough complete (Parts 1–7: shape, backend, domain, pipeline, API, frontend + map, testing).
- Slice 2: `domain/checkpoints.py` + `geometry.py` (TDD), HERE client + parser (`clients/here.py`), `/api/places` + `/api/plans` (routes + checkpoints), one error shape (`errors.py`); form with place search, route list, route lines + checkpoint dots on the map. 45 backend tests. Checked in the browser against real HERE; reviewed (/code-review + silent-failure-hunter), findings fixed.
- Walkthrough fixes to ARCHITECTURE.md: `decidedBy` value list, `isLoadEscalated` example, heatmap `startsAt` = the hour bucket containing now, place-search debounce + `limit=5`.

## Next up
1. Slice 3 (`docs/PLAN.md`): record an Open-Meteo fixture for the Dallas → Denver checkpoints, then TDD `risk.py` (classify), forecast-hour pick, assess + `ranking.py`; Open-Meteo client; add risk to the plan response; colour checkpoints; credit Open-Meteo on the map. Agree test seams with the user first.
2. Decide hosting before Slice 3's first deploy.

## Open questions
- Open-Meteo: very long trips at 10 mi spacing can still exceed 600 calls/min (0.5° cells chosen; paid key if it shows up).
- Hosting (VPS vs Vercel + Render). Needed by Slice 3 (first deploy).
