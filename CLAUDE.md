# SpotterAI — Full Stack Assessment

Take-home assessment for a Full Stack Developer role at Spotter.ai (trucking-ops AI platform: TMS, fuel-cost optimization, Sentinel driver screening, Lens freight data, driver app).
Only ~4% of submissions advance, so quality bar is high: correctness first, then polish, then clear communication.

**The task:** Weather-Aware Truck Routing — given origin, destination, departure time and load weight, generate 3 routes, sample weather at each checkpoint at the truck's ETA, classify risk (wind/rain/snow + load rules), recommend the safest route, and show routes + checkpoints + a 0–48 h corridor weather heatmap on a map. Full brief: `docs/ASSESSMENT.md`.

**Graded on:** 40% routing/weather/risk/recommendation logic · 40% UI, map & heatmap smoothness/performance · 15% code quality · 5% docs & walkthrough. Correctness and clarity over extra features.

**Deliverables:** GitHub repo link · hosted live version · 5–10 min Loom walkthrough.

## Start of every session
1. Read `docs/PROGRESS.md` — current status, next step, open questions.
2. Skim `docs/DECISIONS.md` — what was decided and what was tried and rejected. Don't re-litigate settled decisions without a new reason.
3. Requirements live in `docs/ASSESSMENT.md` (source PDF: `docs/fs-assessment-spotter.pdf`). Requirements win over assumptions.

## End of every session (or before context runs out)
Run `/checkpoint`, which updates PROGRESS.md and DECISIONS.md. Keep both short — they are a handoff note, not a diary.

## Stack & layout
- `backend/` — Django (+ DRF) API, Python
- `frontend/` — React (Vite)
- `docs/` — assessment brief, progress, decisions, research notes

## Working rules
- Small, focused commits with clear messages; `main` stays deployable.
- Never commit secrets — use `.env` (gitignored) and keep `.env.example` current.
- Before calling a feature done: it runs locally, edge cases checked, and it would hold up in the Loom demo.
- Prefer simple, readable solutions over clever ones; reviewers read this code. Don't overcomplicate.
- Reusable components and functions. Extract when something is used twice, not before.
- **Testing:** pytest for the risk logic (most tests) and for the API layer, with routing and weather stubbed by recorded JSON fixtures (no network in tests). Vitest for pure frontend helpers only. No component or browser (Playwright) tests. Lint with ruff, and with ESLint + Prettier.
- **No unnecessary fallbacks.** Never silently substitute default or fallback data when something fails. Fail loudly with a clear error that reaches the UI. A silent fallback in the wrong place hides bugs.

## Skills (in `.claude/skills/`)
- `codebase-design`: use when designing modules. Pure core (risk, checkpoints, ranking) behind small interfaces; I/O at the edges.
- `tdd`: use for the risk/checkpoint/ranking logic. Agree the test seams with the user first.
- `api-and-interface-design`: use for `/api/plan`. Contract first, one error shape, validate at the boundary, treat third-party responses as untrusted. **Ignore** its pagination, PATCH and idempotency sections; our endpoint computes and stores nothing.
- `unslop` (global): run as a polish pass after each screen is built.
- Before committing, review with `/code-review` and the `silent-failure-hunter` agent.
