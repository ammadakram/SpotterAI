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
- LATER — HOS rest breaks as an optional toggle, after the core is done.
- LATER — Hosting: Open-Meteo rate-limits per IP, so we need caching plus a fallback (MET Norway or an API key). A VPS (own IP) is being considered; Hetzner is sold out.

## Tried & rejected / mistakes
- _(none yet)_
