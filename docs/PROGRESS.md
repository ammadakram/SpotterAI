# Progress

_Last updated: 2026-11-15_

## Status
Phase: **Architecture confirmed by walkthrough** → next: build plan.

## Done
- Claude context setup: CLAUDE.md, docs/ (PROGRESS, DECISIONS, ASSESSMENT), `/checkpoint` command.
- Requirements captured in `docs/ASSESSMENT.md`; research in `docs/RESEARCH.md`.
- All interpretation and stack questions answered (DECISIONS.md). Skills installed in `.claude/skills/`.
- Architecture in `docs/ARCHITECTURE.md`, all §5 open points decided (2026-11-15).
- Architecture walkthrough complete (Parts 1–7: shape, backend, domain, pipeline, API, frontend + map, testing).
- Walkthrough fixes to ARCHITECTURE.md: `decidedBy` value list, `isLoadEscalated` example, heatmap `startsAt` = the hour bucket containing now, place-search debounce + `limit=5`.

## Next up
1. Build plan (vertical slices). Slice 1: scaffold + CI + verify HERE per-piece duration params, the HERE alternatives limit, Open-Meteo multi-location counting and batch size.

## Open questions
- Open-Meteo batch size (plan ~100 locations/request; measure in slice 1).
- Hosting (VPS vs Vercel + Render). Deferred.
