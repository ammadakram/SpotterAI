# Progress

_Last updated: 2026-11-22_

## Status
Phase: **Ship** — all six slices built, deployed and checked live; README done → next: record the Loom, then submit.

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
- Slice 5: simplified route lines (10 m), same-place / 0 m routes refused, single-route reason, loading overlay, phone layout, unslop polish (Plex, radii, focus, copy). 150 backend + 10 frontend tests. Reviewed; findings fixed.
- Slice 6: README (what it does, how a plan is computed, answers to the brief's open questions, speed and cost, known limits, setup). Loom outline written to `loom-outline.md` (git-ignored via .git/info/exclude).
- Hosted checks 2026-11-22 (live API): normal plan, 45,001 lb / spacing 30 / +3 days → 400, same place → 400, Honolulu → 422 NO_ROUTE_FOUND, LA → Chicago 10 mi → 422 TRIP_TOO_LARGE, at 50 mi → 200. Severe/No-travel can't be reproduced in today's calm weather (covered by tests).
- First deploy 2026-11-22: backend on Railway, frontend on Vercel (addresses kept out of the repo). Checked live: health, CORS (only the Vercel origin), noindex, LA → Chicago at 10 mi (629 checkpoints) in ~3.4 s with no Open-Meteo limit errors.
- Walkthrough fixes to ARCHITECTURE.md: `decidedBy` value list, `isLoadEscalated` example, heatmap `startsAt` = the hour bucket containing now, place-search debounce + `limit=5`.

## Next up
1. Before recording: wake the backend (/api/health) and ask Claude to re-scan the forecast for demo trips with Severe and load escalation.
2. Record the Loom with `loom-outline.md`; submit the repo link, the live link and the video.

## Open questions
- None.
