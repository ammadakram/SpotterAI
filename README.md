# SpotterAI — Weather-Aware Truck Routing

React + Django app built for a job assessment.

- `backend/` – Django API (Python 3.12, managed with [uv](https://docs.astral.sh/uv/))
- `frontend/` – React + Vite + TypeScript app

## Run locally

Backend (needs a HERE API key):

```bash
cd backend
cp .env.example .env   # then fill in DJANGO_SECRET_KEY and HERE_API_KEY
uv sync
uv run python manage.py runserver 8000
```

Frontend (in a second terminal; `/api` is proxied to port 8000):

```bash
cd frontend
npm install
npm run dev
```

## Deploy

Backend on Railway, frontend on Vercel: see [docs/DEPLOY.md](docs/DEPLOY.md).

## Checks

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest
cd frontend && npm run lint && npm run format:check && npm test && npm run build
```
