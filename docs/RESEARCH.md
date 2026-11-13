# Research Notes

_Researched 2026-11-13. Recommendations, not final decisions; once a choice is made, record it in DECISIONS.md._

## 1. Domain primer: what an expert would know

**Truck ETA is not car ETA.**
- Trucks are often speed-governed (~62–68 mph), and some states set lower truck limits.
- Car routing APIs underestimate a truck's travel time.
- Use a routing API with a real truck profile (it takes weight and size into account).

**Hours of Service (FMCSA, property-carrying drivers).**
- At most 11 hours of driving inside a 14-hour on-duty window.
- A 30-minute break after 8 hours of cumulative driving.
- 10 hours off duty before the next shift.

Why this matters here: on a long route (e.g. Chicago → Denver, ~15 h of driving) the truck physically cannot arrive when the routing API's raw duration says it will. Checkpoints after the rest stop are reached about 10 hours later, so they need a different forecast hour. Adding HOS rest periods to the ETA calculation is optional but would set the submission apart, because it makes "weather at the truck's ETA" actually correct. If we add it, make it a visible toggle and explain it in the README.

**Wind is the main weather danger for trucks.**
- A trailer side is like a sail, and blow-overs happen on I-80 in Wyoming, I-25 in Colorado, and across the Plains.
- Wyoming DOT puts up a blow-over advisory for light trailers when gusts are above 50 mph, and closes roads to them at gusts of 60 mph or more.
- The NWS issues a High Wind Warning for sustained winds of 40 mph or more, or gusts of 58 mph or more.

In real life, *light or empty* trailers are the ones that blow over. The brief's load rules go the other way: heavier loads raise the risk level. This is probably about rollover, stopping distance and how hard a heavy truck is to control. **Implement the brief exactly as written.** In the walkthrough it's fine to mention that you noticed this, but don't "fix" the rules.

**Sustained wind or gusts?** The brief just says "wind". Gusts are what tip trucks over, but sustained wind is the standard measure. Recommendation: classify on sustained wind (`wind_speed_10m`), show gusts in the checkpoint details, and record this in DECISIONS.md. Classifying on gusts is also defensible. Either way, choose one and state it clearly.

**Snow in/hr** means snowfall depth rate, the measure NWS uses (1–2 in/hr is heavy). It is not liquid water equivalent. Open-Meteo `snowfall` with `precipitation_unit=inch` gives depth in inches per hour.

**Rain in/hr:** use Open-Meteo `rain + showers` in inches per hour. Don't use `precipitation`, because that also includes snow, which would count snow twice.

## 2. Routing API

| Option | 3 routes? | Truck profile | Long-haul alternatives | Notes |
|---|---|---|---|---|
| **HERE Routing v8** ✅ | `alternatives=2` → 3 routes | `transportMode=truck`, `vehicle[grossWeight]` (kg) | Yes | Same key also covers geocoding/autosuggest. Free tier exists, but its size is unclear, so confirm at sign-up. Returns flexible-polyline geometry and per-section durations. |
| Mapbox Directions | `alternatives=true` → up to 3 | No (car/traffic only) | Yes | 100k free requests/month. Good fallback; apply a truck speed adjustment. |
| OpenRouteService | max 3 | `driving-hgv` | **No: alternatives are capped at 100 km** | Unusable for cross-country trips. |
| GraphHopper | yes | truck on paid plans | yes | Free plan is non-commercial, 500 requests/day. |

**Recommendation:** HERE v8 in truck mode, sending load weight as `grossWeight`. That way the user's load input affects both the risk rules and the route itself.

**Edge case:** a routing API can return *fewer* than 3 alternatives (short trips, or only one sensible highway). Plan a fallback: generate extra routes through a via-waypoint offset from the main route. If that also fails, show however many routes exist and explain why. Mention this in the Loom.

## 3. Weather API

**Open-Meteo** ✅. Free, no API key, non-commercial use only (fine for an assessment).
- `hourly=wind_speed_10m,wind_gusts_10m,rain,showers,snowfall`, with `wind_speed_unit=mph` and `precipitation_unit=inch`. These units match the brief, so no conversion is needed.
- **Many locations in one request** (comma-separated latitudes and longitudes).
- Hourly forecast up to 16 days ahead, so the 48 h slider and future departure times are covered.
- Limits: 600 calls/min, 5k/hour, 10k/day. The docs don't say clearly whether a multi-location request counts as one call or one call per location. Assume one per location and cache.

**Call budget, worst case:** a 1,000-mile trip at 10-mile spacing × 3 routes ≈ 300 checkpoints, plus the heatmap grid. Spend it carefully:
- Snap coordinates to about 0.1° and cache by `(lat, lon, forecast run)` for about 30–60 min. Neighbouring routes share many points.
- Fetch all 48 hours once per point. The route ETA lookup and the heatmap slider then read the same cached data.

**Matching a checkpoint to its forecast hour:** use the nearest forecast hour to the ETA, or interpolate linearly between the two surrounding hours (more accurate, still simple). If the ETA is beyond the forecast range, mark the checkpoint "no forecast" and show it in the UI. Never quietly label it Low.

## 4. Map, heatmap and smoothness (40% of the grade)

**Map:** MapLibre GL JS through `react-map-gl/maplibre`. It renders on the GPU (WebGL), is open source, needs no Mapbox token, and handles thousands of features easily. Base tiles: OpenFreeMap (free, no key), or the MapTiler/Stadia free tiers.

**Heatmap: the main design decision.**
- MapLibre's built-in `heatmap` layer shows *density*: overlapping points add together. Weather risk is a *value* at each point, not a count, so a density heatmap can mislead (closely spaced points look "hotter").
- Better options for a value field:
  - A **grid of colored cells or circles** along the route corridor (each grid point colored by its risk or by the raw value of the selected variable), or
  - A heatmap layer with `heatmap-weight` set from the value and the grid spacing kept even, so density stays constant and only the value drives the color.
- deck.gl is more powerful but heavier. Our dataset is only a few hundred to a few thousand points, so the built-in MapLibre layers are enough.

**What makes the slider smooth:**
1. **No network calls while sliding.** The backend returns the whole 0–48 h × corridor grid in one response, and the slider only chooses which hour to show.
2. Update the map through MapLibre's `setData` / `setPaintProperty` or a style expression on an `hour` property, not by re-rendering React components.
3. Keep the GeoJSON small: simplify the route geometry for display and round coordinates.
4. Optional: debounce the slider, and animate a "play" through the 48 hours.

**Corridor grid:** sample points along the main route (e.g. every 25 mi) plus points offset to each side (e.g. ±15–30 mi). That makes a band, not just a line, which is what "along the trip corridor" means.

## 5. Hosting

| Part | Option | Notes |
|---|---|---|
| Frontend | Vercel or Netlify | Free, automatic deploys from GitHub. |
| Backend (Django) | Render free web service | **Sleeps after 15 min idle, and the first request takes ~1 min to wake it.** Reviewers may assume the app is broken. Fixes: upgrade to the $7/mo plan for the review period, or run a free uptime pinger plus a "waking server…" message in the UI. |
| | Railway / Fly.io | No real free tier for an always-on app in 2026; Railway has about $5 of trial credit. |

**Recommendation:** Vercel + Render. Pay for the cheapest always-on Render plan during the review window (~$7), because an app that's asleep when a reviewer opens it looks bad for 40% of the grade. Keep API keys on the backend only. The frontend never calls HERE directly.

## 6. Architecture at a glance

```
React (Vite, MapLibre)
  └─ POST /api/plan {origin, destination, departure, load_lbs, interval_mi}
Django (DRF)
  ├─ geocode (HERE)              ← autosuggest endpoint for the input boxes
  ├─ routes (HERE truck, 3 alts)
  ├─ checkpoints: every N mi along each polyline + ETA (+ optional HOS stops)
  ├─ weather (Open-Meteo, batched + cached)
  ├─ risk engine: pure functions, unit-tested against the brief's table
  ├─ ranking: (no_travel_miles, severe_miles, high_miles, avg_risk, duration)
  └─ corridor grid × 48 h for the heatmap
```

Keep the **risk engine and ranking as pure, framework-free Python modules with thorough unit tests**: every boundary value in the table, each load rule, and ranking tie-breaks. That part is 40% of the grade, and it's the easiest place to prove it's correct.

## 7. Other public submissions (found 2026-11-13)

At least 15 public GitHub repos implement this exact brief (search "weather-aware truck routing"). Their READMEs mostly agree:
lower-inclusive band edges, sustained wind (gusts shown, not scored), No Travel miles ranked first, distance-weighted 0–4
average, user-selectable 10/25/50 spacing. Only about one in ten adds optional HOS breaks. Takeaways:
- Getting the logic right is the minimum everyone meets. What sets a submission apart is UI and map smoothness (40%), clear decision docs, and polish.
- Practical gotcha several reported: Open-Meteo rate-limits **per IP**, and shared hosts (Render free) hit it. Fallbacks they used: MET Norway (keyless), or an Open-Meteo API key. Plan a cache plus a fallback.
- Don't read their code closely. Our work must be independent.
- Spotter's *other* full-stack assessment is an FMCSA HOS trip planner, so HOS is core domain knowledge at Spotter.

## Sources
- [HERE pricing](https://developer.here.com/pricing) · [HERE truck routing](https://docs.here.com/routing/docs/routing-v8-truck-routing) · [HERE vehicle properties](https://docs.here.com/routing/docs/routing-v8-vehicle-properties)
- [ORS hosted API restrictions](https://giscience.github.io/openrouteservice/hosted-api-restrictions)
- [Routing API pricing comparison](https://gotime.readthedocs.io/en/latest/pricing.html) · [Mapbox pricing](https://storerocket.io/learn/mapbox-pricing)
- [Open-Meteo docs](https://open-meteo.com/en/docs) · [Open-Meteo pricing](https://open-meteo.com/en/pricing)
- [MapLibre heatmap (Stadia)](https://stadiamaps.com/blog/google-maps-heatmap-deprecated-maplibre-migration/) · [deck.gl vs MapLibre](https://atlas.co/comparisons/deck-gl-vs-maplibre/)
- [WYDOT blow-over advisories](https://dot.state.wy.us/news/light-trailer-advisories-alert-motorists-of-possible-blow-over-risks) · [FreightWaves: high winds](https://www.freightwaves.com/news/high-winds-pose-invisible-threat)
- [Render free tier](https://render.com/articles/platforms-with-a-real-free-tier-for-developers-in-2026)
