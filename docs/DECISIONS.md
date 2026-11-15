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
- 2026-11-14 — Weather cache: key = rounded location only (checkpoints to nearest 0.05°, grid cells = centre on fixed 0.25° lines), 30 min. Every location is fetched for one fixed range (now → +4 days). Why: the key holds no time, so a shorter per-trip range would give cache hits with missing hours (false NO_FORECAST). HERE routes are not cached (low hit rate). Errors are never cached.
- 2026-11-14 — Corridor width (30 mi) and cell size (0.25°) are our choices, not from the brief. Why: wide enough to show weather approaching the route, small enough to keep ~250 cells for a 1,000-mile trip.
- 2026-11-14 — Place search: starts from the first character (no minimum), 300 ms debounce, TanStack Query cache; server sends HERE `limit=5`. Why: user wants instant suggestions; the limit keeps the dropdown short and can't be raised by the client.
- 2026-11-15 — Route count: request exactly 3 routes (alternatives=2), as the brief says. If all 3 have No Travel we show "no safe route" even though a 4th HERE alternative might be safe. Why: brief asks for 3; extra alternatives are usually near-duplicates and cost more weather lookups. Mention this limit (and "depart later" as future work) in the README and Loom.
- 2026-11-15 — `decidedBy` values: SEVERE_MILES, HIGH_MILES, AVERAGE_RISK, DURATION, ONLY_DRIVABLE, or null. A full four-way tie keeps HERE's order and reports DURATION. Why: the frontend needs the full list to write the "why this route" sentence.
- 2026-11-15 — NO_FORECAST miles: counted as `unknown`, left out of ranking; shown whenever > 0 (small route-card note + grey checkpoint dots). No threshold. Why: it's rare, and hiding small gaps behind a threshold would be a quiet omission; grey dots reuse checkpoint data, so no backend change.
- 2026-11-15 — No-safe-route screen: message + corridor heatmap, no routes. Tailwind for styling.
- 2026-11-15 — Heatmap style: filled squares, not MapLibre's heatmap layer. Why: risk is 5 discrete levels; a blended heatmap paints in-between colours that no cell has.
- 2026-11-15 — Frontend lint: oxlint (the current Vite template's default) + Prettier, not ESLint. Why: typescript-eslint supports TypeScript < 6.1 and the template ships TypeScript 7.
- 2026-11-15 — Python tooling: uv (pyproject + uv.lock), no package build. Django with no database apps (no admin/auth/sessions).
- LATER (v2) — Progressive loading: send routes + checkpoints + ranking first, heatmap in a second request. Measure the v1 response time first; only do it if the wait is noticeable.
- LATER — HOS rest breaks as an optional toggle, after the core is done.
- LATER — Loom: mention WeatherOptics (the industry's white-label risk engine) once the core is built.
- LATER — Hosting: VPS vs Vercel + Render. Affects the Open-Meteo rate limit (shared vs dedicated IP).

## Tried & rejected / mistakes
- _(none yet)_
