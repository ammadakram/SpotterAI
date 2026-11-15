# Progress

_Last updated: 2026-11-16_

## Status
Phase: **Build — Slice 3 code done** → next: first deploy (Vercel + Render/Railway), then Slice 4 (heatmap).

## Done
- Claude context setup: CLAUDE.md, docs/ (PROGRESS, DECISIONS, ASSESSMENT), `/checkpoint` command.
- Requirements captured in `docs/ASSESSMENT.md`; research in `docs/RESEARCH.md`.
- All interpretation and stack questions answered (DECISIONS.md). Skills installed in `.claude/skills/`.
- Architecture in `docs/ARCHITECTURE.md`, all §5 open points decided (2026-11-15).
- Slice 1: Django + DRF backend (uv, ruff, pytest, health endpoint), Vite + React + TS frontend (Tailwind, oxlint, Prettier, Vitest, MapLibre map), GitHub Actions CI, Open-Meteo measured. CI green. HERE verified, fixtures recorded (Dallas → Denver routes, no-route case, autosuggest).
- Architecture walkthrough complete (Parts 1–7: shape, backend, domain, pipeline, API, frontend + map, testing).
- Slice 2: `domain/checkpoints.py` + `geometry.py` (TDD), HERE client + parser (`clients/here.py`), `/api/places` + `/api/plans` (routes + checkpoints), one error shape (`errors.py`); form with place search, route list, route lines + checkpoint dots on the map. 45 backend tests. Checked in the browser against real HERE; reviewed (/code-review + silent-failure-hunter), findings fixed.
- Slice 3 (code): `risk.py` (bands, load rules), `forecast.py` (hour pick), `assess.py`, `ranking.py` (TDD); Open-Meteo client (batches of 100, parallel, 30-min cache, strict parsing); plan response has risk, stretches, ranking; UI: coloured dots, legend, checkpoint popup, route cards with risk strip, recommendation + reason, Open-Meteo credit. 122 backend + 6 frontend tests. Reviewed; findings fixed.
- Walkthrough fixes to ARCHITECTURE.md: `decidedBy` value list, `isLoadEscalated` example, heatmap `startsAt` = the hour bucket containing now, place-search debounce + `limit=5`.

## Next up
1. First deploy: backend on Render or Railway (gunicorn, 1 worker + threads, env vars), frontend on Vercel (API base URL, CORS). Check the real Open-Meteo per-IP limit.
2. Slice 4 (`docs/PLAN.md`): corridor grid + heatmap + 0–48 h slider.

## Open questions
- Open-Meteo: very long trips at 10 mi spacing can still exceed 600 calls/min (0.5° cells chosen; paid key if it shows up).
