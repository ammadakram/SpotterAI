# Progress

_Last updated: 2026-11-22_

## Status
Phase: **Build — Slice 3 code done** → Slice 4 done, deployed (Railway + Vercel) → next: Slice 5 (polish), then README + Loom.

## Done
- Claude context setup: CLAUDE.md, docs/ (PROGRESS, DECISIONS, ASSESSMENT), `/checkpoint` command.
- Requirements captured in `docs/ASSESSMENT.md`; research in `docs/RESEARCH.md`.
- All interpretation and stack questions answered (DECISIONS.md). Skills installed in `.claude/skills/`.
- Architecture in `docs/ARCHITECTURE.md`, all §5 open points decided (2026-11-15).
- Slice 1: Django + DRF backend (uv, ruff, pytest, health endpoint), Vite + React + TS frontend (Tailwind, oxlint, Prettier, Vitest, MapLibre map), GitHub Actions CI, Open-Meteo measured. CI green. HERE verified, fixtures recorded (Dallas → Denver routes, no-route case, autosuggest).
- Architecture walkthrough complete (Parts 1–7: shape, backend, domain, pipeline, API, frontend + map, testing).
- Slice 2: `domain/checkpoints.py` + `geometry.py` (TDD), HERE client + parser (`clients/here.py`), `/api/places` + `/api/plans` (routes + checkpoints), one error shape (`errors.py`); form with place search, route list, route lines + checkpoint dots on the map. 45 backend tests. Checked in the browser against real HERE; reviewed (/code-review + silent-failure-hunter), findings fixed.
- Slice 3 (code): `risk.py` (bands, load rules), `forecast.py` (hour pick), `assess.py`, `ranking.py` (TDD); Open-Meteo client (batches of 100, parallel, 30-min cache, strict parsing); plan response has risk, stretches, ranking; UI: coloured dots, legend, checkpoint popup, route cards with risk strip, recommendation + reason, Open-Meteo credit. 122 backend + 6 frontend tests. Reviewed; findings fixed.
- Slice 4: `corridor.py` (0.5° cells within 30 mi), `heatmap.py` (49 hours, same risk rules), heatmap in the response; `lib/heatmap.ts` (Vitest), fill layer under the routes, 0–48 h slider with play, Risk/Wind/Rain/Snow picker, shared `SegmentedControl`. Slider makes no network calls (checked). TRIP_TOO_LARGE (422) refuses plans over Open-Meteo's free per-minute limit before any call. 141 backend + 9 frontend tests. Reviewed; findings fixed.
- First deploy 2026-11-22: backend on Railway, frontend on Vercel (addresses kept out of the repo). Checked live: health, CORS (only the Vercel origin), noindex, LA → Chicago at 10 mi (629 checkpoints) in ~3.4 s with no Open-Meteo limit errors.
- Walkthrough fixes to ARCHITECTURE.md: `decidedBy` value list, `isLoadEscalated` example, heatmap `startsAt` = the hour bucket containing now, place-search debounce + `limit=5`.

## Next up
1. Slice 5 (`docs/PLAN.md`): edge states + polish; simplify route lines for display (LA → Chicago at 10 mi is ~370 KB gzipped); run the unslop pass.
2. Slice 6: README (known limits: 3 routes, unknown miles out of ranking, Open-Meteo free limit / TRIP_TOO_LARGE, free-tier hosts), then the Loom (outline with times and code pointers; re-check demo trips the day of recording).

## Open questions
- Open-Meteo: very long trips at 10 mi spacing can still exceed 600 calls/min (0.5° cells chosen; paid key if it shows up).
