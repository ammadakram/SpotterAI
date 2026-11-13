# Decisions & Lessons

One line each. Newest at the bottom. Include *why*, and record dead ends so they aren't repeated.

## Decisions
- 2026-11-13 — Stack: Django API + React frontend in one repo. Why: matches the role and the assessment.
- 2026-11-13 — Session context lives in-repo (CLAUDE.md + docs/), not in chat history. Why: survives new sessions and machines, reviewable in git.
- 2026-11-13 — Fewer than 3 routes from the API: show what we have plus a small banner explaining why. (agreed)
- 2026-11-13 — ETA beyond forecast range: checkpoint shows "No forecast" with a one-line reason, never defaults to Low. (agreed)
- 2026-11-13 — Checkpoint level = worst of wind/rain/snow (after load rules). Per-condition levels are shown in the UI but NOT used in ranking — the brief's step 4 (travel time) breaks ties. (agreed)
- 2026-11-13 — Load rules only escalate wind; every unlisted combination uses the plain table. (agreed)
- 2026-11-13 — Live in-trip re-planning is out of scope; the app is a pre-trip planner. Mention "re-plan from current position" as future work in README/Loom. (agreed)
- PROPOSED — Ranking: No Travel miles first, then the brief's 4 steps. If every route has No Travel, still show the least-bad one under a clear "no safe route" warning.
- PROPOSED — Band edges: every band starts at its lower bound ([lower, upper)), so 0.25 in/hr rain = High, 34.5 mph = Moderate; no rounding. Rain/snow No Travel is strictly > 1.00 / > 3.0 as written; wind No Travel is >= 55.
- PROPOSED — Wind: classify on sustained 10 m wind; show gusts in checkpoint details.
- PROPOSED — Risk scale Low 0 … Severe 3, No Travel 4; average is distance-weighted.
- PROPOSED — Spacing: user-selectable 10/25/50, default 25. Each checkpoint represents half the gap to each neighbour, so miles sum to the route length.
- PROPOSED — HOS rest breaks: optional toggle, built only after the core is solid.

## Tried & rejected / mistakes
- _(none yet)_
