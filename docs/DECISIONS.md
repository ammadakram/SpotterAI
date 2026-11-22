# Decisions & Lessons

One line each. Newest at the bottom. Include *why*, and record dead ends so they aren't repeated.

## Decisions
- 2026-11-13 — Stack: Django API + React frontend in one repo. Why: matches the role and the assessment.
- 2026-11-13 — Session context lives in-repo (CLAUDE.md + docs/), not in chat history. Why: survives new sessions and machines, reviewable in git.
- 2026-11-13 — Pre-trip planner only; no live in-trip re-planning. "Re-plan from current position" goes in README/Loom as future work.
- 2026-11-13 — Fewer than 3 routes: show what we have, no banner (noise).
- 2026-11-13 — No safe route (every route has No Travel): show no route, only a clear "no safe route available" message.
- 2026-11-13 — Ranking: No Travel excludes a route, then the brief's order: Severe miles → High miles → avg risk → travel time. No extra tie-breakers.
- 2026-11-13 — Checkpoint level = worst of wind/rain/snow, after load rules. All three readings are shown per checkpoint in the UI, but are not used in ranking.
- 2026-11-13 — Load rules only escalate wind. Every combination not listed uses the plain table.
- 2026-11-13 — Band edges: each band starts at its lower bound ([lower, upper)); no rounding. 0.25 in/hr rain = High, 34.5 mph = Moderate. Rain/snow No Travel is strictly > 1.00 / > 3.0; wind No Travel is >= 55.
- 2026-11-13 — Wind: classify on sustained 10 m wind; show gusts in checkpoint details.
- 2026-11-13 — Risk scale: Low 0, Moderate 1, High 2, Severe 3, No Travel 4. Average is distance-weighted.
- 2026-11-13 — Spacing: user-selectable 10/25/50 dropdown, default 25.
- 2026-11-13 — ETA past the forecast range: checkpoint shows "No forecast" with a one-line reason, never Low.
- 2026-11-13 — Miles per checkpoint: we only sample weather at checkpoints, and each mile of road takes the weather of its nearest checkpoint (midpoint to midpoint; the first and last checkpoints reach the route ends). The stretches sum exactly to the route length, and a test asserts this.
- 2026-11-13 — UI adopts two industry patterns: side-by-side route comparison cards, and a trip summary that says *where* the risk is ("Severe for 18 mi between mile 140–158, ~2 h after departure"), not just totals.
- 2026-11-13 — Extensions (road surface, NWS alerts, 7-day range, delay prediction) are not built and not mentioned in the Loom.
- 2026-11-13 — No silent fallbacks: failures surface as clear errors, never quietly substituted data. Why: a fallback in the wrong place hides bugs and wrong data.
- 2026-11-13 — Services confirmed: HERE v8 truck routing (+ HERE geocoding), Open-Meteo weather, MapLibre map.
- 2026-11-13 — No weather backup source (MET Norway dropped: it has no snowfall data, and the no-silent-fallbacks rule applies). If Open-Meteo fails, the user sees a clear error. Prevention: caching, plus a dedicated IP or an Open-Meteo API key.
- 2026-11-13 — Departure: from now to +48 h.
- 2026-11-13 — Heatmap: slider hour 0 = now. Shows combined risk level by default, with a picker for wind / rain / snow.
- 2026-11-13 — Load weight = cargo weight (not gross). Valid range 0–45,000 lb (80,000 lb legal gross minus ~35,000 lb tractor-trailer).
- 2026-11-13 — US only.
- 2026-11-13 — Time: input and display in the browser's time zone with an abbreviation label; UTC internally.
- 2026-11-13 — Frontend: React + Vite + TypeScript. No database; Django in-process cache only.
- 2026-11-13 — Testing: pytest (risk logic + API with recorded fixtures), Vitest (pure helpers). No Playwright/component tests. Linting: ruff, oxlint + Prettier (see 2026-11-15).
- 2026-11-13 — CI: one GitHub Actions workflow (lint, test, build), added with the project scaffold. No CD for now.
- 2026-11-13 — Skills vendored in `.claude/skills/`: codebase-design, tdd (Matt Pocock), api-and-interface-design (Addy Osmani).
- 2026-11-14 — Weather cache: key = rounded location only (checkpoints to nearest 0.05°, grid cells = centre on fixed 0.5° lines (see 2026-11-15)), 30 min. Every location is fetched for one fixed range (now → +4 days). Why: the key holds no time, so a shorter per-trip range would give cache hits with missing hours (false NO_FORECAST). HERE routes are not cached (low hit rate). Errors are never cached.
- 2026-11-14 — Corridor width (30 mi) is our choice, not from the brief. Why: wide enough to show weather approaching the route.
- 2026-11-14 — Place search: starts from the first character (no minimum), 300 ms debounce, TanStack Query cache; server sends HERE `limit=5`. Why: user wants instant suggestions; the limit keeps the dropdown short and can't be raised by the client.
- 2026-11-15 — Route count: request exactly 3 routes (alternatives=2), as the brief says. If all 3 have No Travel we show "no safe route" even though a 4th HERE alternative might be safe. Why: brief asks for 3; extra alternatives are usually near-duplicates and cost more weather lookups. Mention this limit (and "depart later" as future work) in the README and Loom.
- 2026-11-15 — `decidedBy` values: SEVERE_MILES, HIGH_MILES, AVERAGE_RISK, DURATION, ONLY_DRIVABLE, or null. A full four-way tie keeps HERE's order and reports DURATION. Why: the frontend needs the full list to write the "why this route" sentence.
- 2026-11-15 — NO_FORECAST miles: counted as `unknown`, left out of ranking; shown whenever > 0 (small route-card note + grey checkpoint dots). No threshold. Why: it's rare, and hiding small gaps behind a threshold would be a quiet omission; grey dots reuse checkpoint data, so no backend change.
- 2026-11-15 — No-safe-route screen: message + corridor heatmap, no routes. Tailwind for styling.
- 2026-11-15 — Heatmap style: filled squares, not MapLibre's heatmap layer. Why: risk is 5 discrete levels; a blended heatmap paints in-between colours that no cell has.
- 2026-11-15 — Frontend lint: oxlint (the current Vite template's default) + Prettier, not ESLint. Why: typescript-eslint supports TypeScript < 6.1 and the template ships TypeScript 7.
- 2026-11-15 — Python tooling: uv (pyproject + uv.lock), no package build. Django with no database apps (no admin/auth/sessions).
- 2026-11-15 — Heatmap cells 0.5° (~35 × 28 mi), not 0.25°. Why: Open-Meteo charges 1 call per location and the free limit is 600/min; 0.25° cells made one plan cost up to ~1,300 calls. 0.5° cuts grid calls ~4×. The heatmap is only a picture, so the coarser cells cost little.
- 2026-11-16 — Checkpoint miles come from HERE's span lengths; the drawn line only says where a mile is. Why: span lengths sum exactly to HERE's distance, while the decoded line is ~0.7 mi shorter on Dallas → Denver, so measuring the line would make checkpoints disagree with `distanceMi`.
- 2026-11-16 — Departure: the server accepts up to 10 min in the past; the form's empty departure means "now", computed at submit. Why: "leave now" arrives seconds late, and a default timestamp frozen at page load went stale.
- 2026-11-16 — HERE routes with a `critical` section notice (e.g. violated truck restriction) are dropped; if none remain → NO_ROUTE_FOUND. Why: such a route is not legal for this truck.
- 2026-11-16 — API tests fake HERE at the HTTP level (`httpx.MockTransport` serving recorded JSON), not with a fake client object. Why: the tests then also cover our request params (gross weight, limit=5) and parsing.
- 2026-11-16 — Place-search failures use ROUTING_UNAVAILABLE (502) with their own message; no extra error code. Why: same provider (HERE), and the UI only shows the message.
- LATER (Slice 5) — Simplify route geometry for display (now ~8,800 points per route, response ~550 KB), as ARCHITECTURE.md specifies.
- 2026-11-16 — Rain = Open-Meteo `rain` + `showers` (user confirmed). Gusts are display-only, so a missing gust doesn't make a checkpoint NO_FORECAST.
- 2026-11-16 — `isLoadEscalated` is true only when the load rule changed the checkpoint's final level. Why: if rain is already Severe, the load changed nothing the driver sees.
- 2026-11-16 — Stretches cover the whole route (Low included) and sum to its length. Route card = one summary line (No travel / Severe / High miles, Avg, No forecast) + the coloured risk strip; no per-stretch text. Why (user): stretch details repeat what the map shows and confused the card.
- 2026-11-16 — Ranking compares miles rounded to 0.1 and the average to 0.01, the precision shown. Why: float noise must not decide a winner on a difference nobody can see.
- 2026-11-16 — A route with no usable forecast at all → 502 WEATHER_UNAVAILABLE, not a plan of grey dots. Weather values that are NaN, infinite or negative are rejected.
- 2026-11-16 — Checkpoint spacing is a 3-button toggle, not a native select (user: the native popup covered the field). Load is a digits-only text field (no spinner).
- 2026-11-16 — Hosting: Vercel (frontend) + Railway (backend), not Render's free plan (sleeps after ~15 min idle; the next visitor waits 30–60 s). Gunicorn: 1 worker, 8 threads, so the in-memory weather cache is shared. Frontend reads `VITE_API_BASE_URL` (backend URL stays out of the repo); backend allows only that origin (CORS). Gzip on: plan response 565 KB → 153 KB. Steps in docs/DEPLOY.md.
- 2026-11-16 — Kept: unknown (no-forecast) miles stay out of ranking. Known limit: a long trip leaving at +48 h can run past the 4-day forecast, and a mostly-unknown route could then win on average risk. User chose not to add a rule the brief doesn't give. Mention in the Loom.
- 2026-11-22 — Back to Railway. Briefly switched to Render's free plan (2026-11-21, to save the ~$5/month), but Render's site was down for days, so the switch was reverted. Railway also avoids the free plan's 30–60 s wake-up.
- 2026-11-22 — Plans too big for Open-Meteo's free per-minute limit (600 places/min/IP) fail fast with 422 TRIP_TOO_LARGE, counted before any call (only uncached places count; budget 550). Why: such a plan can never finish (LA → Chicago at 10 mi needs 792 places), and trying used up the minute so every other plan failed too. Rejected: silently coarser cells/spacing (hides what the user asked for), waiting for the next minute (over a minute per plan). A paid key removes the check.
- 2026-11-22 — Heatmap: computed in the same weather pass as the checkpoints (one budget, no repeats); same `classify` with load rules; risk sent as 0–4 (null = no forecast, drawn grey). Values are floored (wind 0.1, rain/snow 0.001), not rounded, so the Wind/Rain/Snow views never jump a band edge the risk view doesn't. Wind/Rain/Snow views colour by the brief's bands for that variable alone, in the risk colours.
- 2026-11-22 — TRIP_TOO_LARGE advice depends on spacing: below 50 mi it suggests a larger spacing; at 50 mi it says the trip is too long for the free weather service (heatmap cells don't shrink with spacing).
- 2026-11-22 — Progressive loading not needed: the heatmap adds ~10 KB gzipped (Dallas → Denver: 124 cells; plan 167 KB gzipped, 4.4 s cold / 2.0 s cached).
- LATER — HOS rest breaks as an optional toggle, after the core is done.
- LATER — Loom: mention WeatherOptics (the industry's white-label risk engine) once the core is built.

## Tried & rejected / mistakes
- 2026-11-16 — Place search kept the previous query's results visible (`keepPreviousData`) so Enter could pick a place for older text; and Enter in a loading list submitted the form. Fixed: results only count when they match the current text, and Enter in an open list never submits.
