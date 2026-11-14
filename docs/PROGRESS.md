# Progress

_Last updated: 2026-11-14_

## Status
Phase: **Architecture walkthrough** (user learning the design until they own it) → then build plan.

## Done
- Claude context setup: CLAUDE.md, docs/ (PROGRESS, DECISIONS, ASSESSMENT), `/checkpoint` command.
- Requirements captured in `docs/ASSESSMENT.md`; research in `docs/RESEARCH.md`.
- All interpretation and stack questions answered (DECISIONS.md). Skills installed in `.claude/skills/`.
- Architecture drafted in `docs/ARCHITECTURE.md`.
- Walkthrough so far (user passed the check questions):
  - Parts 1–3: overall shape, backend layout, pure `domain/`, `plan_trip` with injected fakes and a fixed `now`, error codes (4xx vs 5xx, 400 vs 422, upstream codes never passed through).
  - Part 4: the full pipeline, steps 1–10 (routes, timeline, checkpoints + midpoint rule, grid, weather; forecast hour, classify + load rules, assess, rank, heatmap frames).
  - Part 5 started: `/api/places` and the plan request (user skipped Q21–Q22, knows them).

## Next up
1. Continue the walkthrough at **Part 5: the response** (routes, checkpoints, ranking incl. `decidedBy`, heatmap arrays → `r0…r48` in the frontend), then errors recap, Part 6 (frontend + map), Part 7 (testing).
   Teaching style: plain English, skip web basics (user has ~2 yrs experience), quiz until correct; move on only with the user's explicit OK.
2. After the walkthrough: user confirms the 4 PROPOSED points in ARCHITECTURE.md §5.
3. Build plan (vertical slices). Slice 1: scaffold + CI + verify HERE per-piece duration params, Open-Meteo multi-location counting and batch size.

## Open questions
- ARCHITECTURE.md §5 (no-forecast miles, no-safe-route screen, heatmap style, Tailwind).
- Open-Meteo batch size (plan ~100 locations/request; measure in slice 1).
- Hosting (VPS vs Vercel + Render). Deferred.
