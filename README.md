# Weather-Aware Truck Routing

Plan a truck trip and see which route is safest. Given an origin, a destination, a departure
time and the load weight, the app asks HERE for up to three truck routes, checks the weather
at checkpoints along each route **at the time the truck will be there**, rates every
checkpoint with the brief's risk and load rules, and recommends the safest route with the
reason. A corridor heatmap with a 0–48 h slider shows the weather around the routes.

Built with Django (DRF) and React (Vite, TypeScript) for the Spotter.ai full-stack assessment.
The hosted version's address is shared with the submission rather than in this repo.

## What you can do

- Search origin and destination (US places), choose a departure (now to +48 h), load
  (0–45,000 lb) and checkpoint spacing (10 / 25 / 50 mi).
- Compare up to three routes: distance, driving time, arrival, a strip that shows *where* the
  risk is, and the miles per risk level.
- See the recommendation and why it won, e.g. "Fewest Severe miles: 0.0 mi vs 30.0 mi on
  Route A".
- Click a checkpoint for its arrival time, wind, gusts, rain and snow, the level of each, and
  whether the load raised it.
- Move the slider or press play to watch the corridor weather over 48 hours, as overall risk
  or as wind, rain or snow alone. The slider makes no network requests.
- Works on phones (map on top, panel below).

## How a plan is computed

One request, `POST /api/plans`, does everything; `backend/planner/service.py` → `plan_trip`
runs the steps. All rules live in pure functions in `backend/planner/domain/`.

1. **Routes.** HERE Routing v8 in **truck mode** with the truck's gross weight (load +
   35,000 lb tractor-trailer). Each route comes with ~0.5 km pieces, each with its own length
   and driving time (`clients/here.py`).
2. **Checkpoints** every 10 / 25 / 50 mi plus the destination. Miles come from HERE's piece
   lengths; the ETA at any mile is interpolated inside its piece, so slow city miles and fast
   highway miles keep their own speeds (`domain/checkpoints.py`).
3. **Corridor grid.** 0.5° cells whose centre is within 30 mi of any route
   (`domain/corridor.py`).
4. **Weather.** Open-Meteo hourly wind, gusts, rain, showers and snow for every checkpoint
   and cell, in one pass (`clients/open_meteo.py`).
5. **Forecast hour.** Rain and snow at hour T are the total for the hour *ending* at T, so a
   truck at a checkpoint at 9:45 uses the 10:00 value (`domain/forecast.py`).
6. **Risk.** Each condition gets its band from the brief's table, the load rules raise wind,
   and the checkpoint takes the worst of the three (`domain/risk.py`).
7. **Route assessment.** Miles per level, a distance-weighted average risk, and stretches of
   equal risk with their times (`domain/assess.py`).
8. **Ranking.** Routes with any No Travel are dropped; the rest are ordered by Severe miles →
   High miles → average risk → driving time, and the response says which criterion decided
   (`domain/ranking.py`).
9. **Heatmap.** Every cell's risk, wind, rain and snow for 49 hours from now, with the same
   rules and load (`domain/heatmap.py`).

## Decisions on the brief's open questions

Every decision, with its reason, is logged in [docs/DECISIONS.md](docs/DECISIONS.md).

| Question | What the app does |
|---|---|
| Band edges overlap (rain 0.25 is in two bands; 34.5 mph falls between) | Each band starts at its lower bound: 0.25 in/hr is High, 34.5 mph is Moderate. No Travel for rain and snow is strictly above 1.00 / 3.0, as written; wind No Travel is ≥ 55 mph. |
| Combining wind, rain and snow | The checkpoint is the worst of the three, after the load rules. |
| Load rules | They raise wind only: 45–54 mph with > 30,000 lb → No Travel; 35–44 mph with > 40,000 lb → Severe. The checkpoint is marked when the load changed its level. Load means cargo; 45,000 lb keeps the truck under 80,000 lb gross. |
| No Travel in the ranking | A route with any No Travel is not drivable and is not ranked. If no route is drivable, the app says there is no safe route and recommends none. |
| How many miles a checkpoint stands for | Halfway to its neighbours (the first and last reach the route ends), so the miles add up to the route's length. |
| Average risk | Low 0, Moderate 1, High 2, Severe 3, No Travel 4, weighted by miles. |
| Wind speed or gusts | Sustained wind decides; gusts are shown. |
| Rain | Open-Meteo `rain` + `showers`. |
| ETA source | HERE's truck profile with the real gross weight, so ETAs are truck ETAs. Rest breaks are not modelled. |
| Arrival past the forecast | That checkpoint shows "No forecast" with the reason, never Low. Its miles are shown as unknown and left out of the ranking. |
| Heatmap time vs. route ETA | The slider's hour 0 is the current hour; the corridor view is separate from each checkpoint's ETA weather. |

## Speed and cost

- **One request per plan.** Choosing a route, moving the slider and switching layers happen
  in the browser.
- **Map drawing on the GPU.** Routes, checkpoints and heatmap squares are MapLibre layers,
  uploaded once per plan. Selecting a route or moving the slider only changes a paint rule.
- **Weather cache.** Places are rounded (checkpoints to 0.05°, cells to fixed 0.5° lines) and
  cached for 30 minutes, so routes share most lookups and repeated plans are cheap. Failures
  are never cached.
- **Batched, parallel requests.** Up to 100 places per Open-Meteo request, several at once.
- **Within the free weather limit.** Open-Meteo's free plan allows 600 places per minute per
  IP. A plan that needs more new places is refused before any call (`TRIP_TOO_LARGE`, with
  advice), so it cannot use up the minute for everyone.
- **Small responses.** Route lines are simplified for drawing (Dallas → Denver: 8,791 →
  1,266 points; miles and ETAs still use the full line) and responses are gzipped (Dallas →
  Denver at 25 mi: ~40 KB).

A typical plan (Dallas → Denver, 25 mi) takes 2–5 s, most of it waiting on HERE and Open-Meteo.

## Known limits and future work

- **Three routes only**, as the brief asks. If all three meet No Travel, a fourth HERE
  alternative might be safe; suggesting a later departure would be the natural next feature.
- **Unknown miles are not ranked.** A long trip leaving near +48 h can run past the 4-day
  forecast; a route that is mostly unknown could then win on average risk. Kept as decided
  rather than adding a rule the brief doesn't give.
- **Free weather plan.** Very long trips at 10 mi spacing exceed Open-Meteo's per-minute limit
  and are refused with advice; a paid key (`OPEN_METEO_API_KEY`) removes the limit.
- **Planning before the trip only.** No live re-planning from the truck's position, no rest
  breaks, US only.
- The hosted site asks search engines not to index it.

## Run locally

Needs Python 3.12 with [uv](https://docs.astral.sh/uv/), Node 22 and a
[HERE](https://platform.here.com/) API key (Base plan).

```bash
cd backend
cp .env.example .env   # then set DJANGO_SECRET_KEY and HERE_API_KEY
uv sync
uv run python manage.py runserver 8000
```

In a second terminal (the dev server proxies `/api` to port 8000):

```bash
cd frontend
npm install
npm run dev
```

## Checks

The backend tests use recorded HERE and Open-Meteo responses, so they make no network calls.

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest
cd frontend && npm run lint && npm run format:check && npm test && npm run build
```

GitHub Actions runs the same on every push.

## Deploy

Backend on Railway, frontend on Vercel: see [docs/DEPLOY.md](docs/DEPLOY.md).

## Project layout

```
backend/planner/
  domain/     pure rules: checkpoints, risk, forecast hour, assessment, ranking, corridor, heatmap
  clients/    HERE and Open-Meteo: requests, parsing and checking their answers
  service.py  plan_trip: runs the steps above
  serializers.py, views.py, errors.py   API input checks, JSON output, one error shape
frontend/src/
  features/   plan form, route cards, map, forecast slider
  lib/        API types and calls, heatmap squares, risk colours, formatting
docs/         brief, architecture, decisions, deploy steps
```

The design is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Data and credits

Routing and place search by [HERE](https://www.here.com/). Weather by
[Open-Meteo](https://open-meteo.com/) (CC BY 4.0). Map tiles by
[OpenFreeMap](https://openfreemap.org/) with data © [OpenStreetMap](https://www.openstreetmap.org/copyright)
contributors, drawn with [MapLibre](https://maplibre.org/).
