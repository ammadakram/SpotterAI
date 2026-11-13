# Progress

_Last updated: 2026-11-13_

## Status
Phase: **Setup** → next: background research, then build.

## Done
- Repo initialized (backend/ + frontend/ planned, .gitignore).
- Claude context setup: CLAUDE.md, docs/ (PROGRESS, DECISIONS, ASSESSMENT), `/checkpoint` command.

- Assessment PDF in `docs/`; requirements, risk rules, ranking and evaluation weights captured in `docs/ASSESSMENT.md`.

- Background research written to `docs/RESEARCH.md` (domain, routing/weather APIs, map/heatmap, hosting, architecture sketch).

## Next up
1. Answer the open questions below.
2. Install the chosen skills into `.claude/skills/`.
3. Write `docs/ARCHITECTURE.md` (system design), then the build plan.

## Open questions (need the user's call)
- Stack confirm: HERE truck routing, Open-Meteo, MapLibre; hosting (VPS vs Vercel+Render).
- Weather failure: drop the MET Norway fallback (no snowfall data, conflicts with no-silent-fallbacks) → clear error instead?
- Departure window: how far ahead can departure be (48 h vs 7 days)?
- Heatmap: hour 0 = now or = departure? Show combined risk, or a picker for wind/rain/snow?
- Load weight = cargo weight (not gross)? Valid range (0–45,000 lb)?
- US only?
- Time zones: input and display in the browser's time zone?
- Frontend in TypeScript?
- No database; in-process cache only?
- Testing: pytest (domain + API with recorded fixtures) + Vitest (pure helpers only); ruff + ESLint/Prettier.
- CI: one GitHub Actions workflow (lint, test, build); deploys through the host's git integration.
