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
- Prefer simple, readable solutions over clever ones; reviewers read this code.
