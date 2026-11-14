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
  - Part 4a: pipeline steps 1–5 (routes, per-piece timeline + interpolation, checkpoints + midpoint rule, corridor grid, weather snapping/batching/caching).

## Next up
1. Continue the walkthrough at **Part 4b, steps 6–7** (forecast hour, classify). Open check questions, waiting for the user's answers:
   - Q8: ETAs 14:00 and 14:05, which hourly value each? (14:00 → 14:00; 14:05 → 15:00)
   - Q9: 35,000 lb, wind 47, rain 0.30, no snow? (wind No Travel via load rule, rain High, checkpoint No Travel)
   - Q10: same at exactly 30,000 lb? (wind Severe, rule needs >30,000; checkpoint Severe)
2. Then steps 8–10 (assess, rank, heatmap frames), Part 5 (API), Part 6 (frontend + map), Part 7 (testing).
   Teaching style: plain English, one part at a time, quiz until fully correct before moving on.
3. After the walkthrough: user confirms the 4 PROPOSED points in ARCHITECTURE.md §5.
4. Build plan (vertical slices). Slice 1: scaffold + CI + verify HERE per-piece duration params, Open-Meteo multi-location counting and batch size.

## Open questions
- ARCHITECTURE.md §5 (no-forecast miles, no-safe-route screen, heatmap style, Tailwind).
- Open-Meteo batch size (plan ~100 locations/request; measure in slice 1).
- Hosting (VPS vs Vercel + Render). Deferred.
