# Gram

Self-hosted meal/calorie tracker. Svelte (Tailwind + DaisyUI) SPA + FastAPI + SQLite,
runs in K8s on a Raspberry Pi. Design & decisions: [docs/DESIGN.md](docs/DESIGN.md).

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

## Deployment
Relies on GitOps infra(GitHub self-hosted runner and ArgoCD) deployed in [home-projects-parent-k8s](https://github.com/roman-ks/home-projects-parent-k8s).
The goal is to have application deployment require as little manual intervention as possible.

Flow:
1. Pushes to `main` branch trigger GitHub Action
2. GitHub Action starts a self-hosted runner in K8s.
3. The runner checks out this repo, builds the Docker image, 
   and pushes it to the local registry tagged with the current 
   commit SHA. It then checks out the [Gram Helm chart](https://github.com/roman-ks/home-projects-parent-k8s/tree/main/charts/gram)
   from the GitOps repository, updates `gitops-values.yaml` with the new image
   tag, commits the change, and pushes it back.
4. [Argo CD application](https://github.com/roman-ks/home-projects-parent-k8s/blob/main/kustomize/argocd/base/application-gram.yaml) watches GitOps repo, detects values change and auto-syncs to application in K8s

## Notes

- No auth yet (planned: Authentik OIDC, Immich-style — see DESIGN §4).
- Kept Capacitor-ready: pure SPA + JSON API + configurable `VITE_API_BASE`.
