# Build Plan

Vertical slices: each one ends in something that runs and can be shown. `main` stays deployable after every slice.
Design details live in `ARCHITECTURE.md`; this file is only the order of work.

## Slice 1 — Scaffold, CI, API checks
- Django + DRF project (`config/`, `planner/`), ruff, pytest. `HERE_API_KEY` checked at startup; `.env.example`.
- Vite + React + TS, Tailwind, ESLint + Prettier, Vitest, TanStack Query, react-map-gl/maplibre.
- GitHub Actions: ruff + pytest, ESLint + Vitest + `tsc` + `vite build`.
- Check with real calls, write results into ARCHITECTURE.md:
  - HERE: which parameter gives per-piece durations (spans vs actions); the max `alternatives`.
  - Open-Meteo: how multi-location requests count against the free limit; a safe batch size.
- Record real responses (Dallas → Denver) as JSON fixtures for tests.
- **Done when:** both apps start locally, CI is green, fixtures are saved.

## Slice 2 — Routes and checkpoints on the map (no weather yet)
- `domain/`: geometry, timeline + ETA interpolation, checkpoint placement, `coversMi` (TDD; agree test seams first).
- `clients/here.py` (routing + autosuggest), parsed into domain types; bad data → `ROUTING_UNAVAILABLE`.
- `GET /api/places`, `POST /api/plans` returning routes + checkpoints; validation + one error shape.
- Frontend: plan form (place search, departure, load, spacing), map with route lines and checkpoint dots, error message.
- **Done when:** Dallas → Denver shows 3 routes with checkpoints at the chosen spacing.

## Slice 3 — Weather, risk and the recommendation
- `domain/`: forecast-hour pick, classify + load rules, assess (risk miles, average, stretches), rank + `decidedBy` (TDD).
- `clients/open_meteo.py`: batching, parallel calls, 30 min cache, snapping; bad data → `WEATHER_UNAVAILABLE`.
- Frontend: route cards, recommendation + why, trip summary, checkpoint popup, coloured dots.
- **Deploy a first version** here, to see the real Open-Meteo per-IP limit early (hosting decision needed by now).
- **Done when:** each route shows its risk, and the safest is recommended with a reason.

## Slice 4 — Corridor heatmap
- `domain/corridor.py` grid + 49 hourly frames; add to the response.
- Frontend: `lib/heatmap.ts` (cells → squares with `r0…r48` etc.), `fill` layer, slider + play, variable picker.
- Measure response time; decide on v2 progressive loading only if the wait is noticeable.
- **Done when:** the slider moves through 48 h smoothly with no network calls.

## Slice 5 — Edge states and polish
- No safe route screen, `NO_FORECAST` note + grey dots, loading states, fewer than 3 routes.
- `unslop` pass on each screen; `/code-review` + silent-failure-hunter.
- **Done when:** every case in ASSESSMENT.md has been tried in the hosted app.

## Slice 6 — Ship
- Final deploy, README (setup, design choices, known limits: 3 routes only, "depart later" as future work), Loom.
