# Meal Tracker

Self-hosted meal/calorie tracker. Svelte (Tailwind + DaisyUI) SPA + FastAPI + SQLite,
runs in Docker on a Raspberry Pi. Design & decisions: [docs/DESIGN.md](docs/DESIGN.md).

## Run with Docker (prod-like)

```bash
docker compose up --build
# open http://localhost:8000
```

SQLite lives in the `meal-data` volume (`/data/meals.db`).

## Local development (hot reload)

Two processes — backend on :8000, Vite dev server proxies `/api` to it.

```bash
# backend
python3 -m venv .venv && ./.venv/bin/pip install -r backend/requirements.txt
./.venv/bin/uvicorn backend.app.main:app --reload      # :8000

# frontend (separate terminal)
cd frontend && npm install && npm run dev               # :5173, proxies /api -> :8000
```

Open the Vite URL (http://localhost:5173).

## API (under `/api`)

| Method | Path | Purpose |
|---|---|---|
| POST | `/foods` | add a food (per-100g nutrition) |
| GET | `/foods?q=` | search the catalogue |
| POST | `/entries` | log a food `{food_id, amount_grams, meal, consumed_date?}` |
| GET | `/entries/today` | today's entries |
| DELETE | `/entries/{id}` | remove an entry |
| GET | `/today/summary` | today's totals (calories + macros) |
| GET | `/suggestions/same-meal?meal=&days=5` | foods eaten at this meal, last 5 days |
| GET | `/suggestions/popular?meal=&limit=10` | top foods (distinct-days), opt. per meal |

## Layout

```
backend/   FastAPI app (app/main.py), SQLite schema (app/db.py)
frontend/  Vite + Svelte SPA (src/App.svelte)
docs/      DESIGN.md
```

## Notes

- No auth yet (planned: Authentik OIDC, Immich-style — see DESIGN §4).
- Kept Capacitor-ready: pure SPA + JSON API + configurable `VITE_API_BASE`.
