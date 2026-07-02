# Gram — Design & Decisions

> Living document. Status as of 2026-06-23.
> This locks in the **tech stack & architecture**. Data model and UX/UI are designed
> in later sections once the foundation is agreed.

## 1. What we're building

A small, self-hosted meal/calorie tracker for personal use:

- Add foods to a catalogue (filled gradually from package labels / open sources like
  USDA FoodData Central) and log them into daily meals.
- Mobile-first, "super easy" input. Runs on a Raspberry Pi in Docker, SQLite storage.
- Replaces reliance on FatSecret. FatSecret's API stays a *possible future import
  source* only — its terms forbid storing nutrition/diary content long-term, which is
  the main reason we own the data instead (label/USDA values are ours to keep).

### Scope for v1
- Input items + add to **today's** meals.
- Running **today total** (start with calories only).
- Lightweight **history-driven quick input** (not a full history browser):
  - what you ate around *this time of day* on the last few days,
  - most popular items for *this time of day*,
  - most popular items overall.
- No auth yet (added later, see §4).
- Single user.

## 2. Tech stack (LOCKED)

| Layer | Choice | Why |
|---|---|---|
| Frontend | **Svelte SPA** (Vite, plain Svelte — no SSR) | Lightweight, great mobile DX, compiles to static assets (Capacitor-ready). |
| i18n | `src/lib/i18n.js` — plain JS translation map, `t(key)` function | No extra deps. Language detected from `navigator.languages` (same source as `Accept-Language`). **All UI strings must go through `t()` — never hardcode display text in components.** Add new languages / keys there. |
| Styling | **Tailwind + DaisyUI** | Utilities for fast iteration + ready dropdown/modal components. |
| Backend | **Python + FastAPI** (JSON API) | Async, typed, simple; serves API + static SPA. |
| Database | **SQLite** (file on a mounted volume) | Single-user, zero-ops, perfect for a Pi. |
| Packaging | **Docker**, single container | FastAPI serves API + built SPA; multi-stage build (Node build stage → copy `dist/` into Python image). Build image off-Pi (dev/buildx), not on the Pi. |
| Host | Raspberry Pi (ARM) | Existing hardware. |

### Explicitly rejected
- **HTMX / server-rendered UI** — clean and light, but server-rendered HTML can't be
  bundled into a native app. Killed by the "keep native option open" requirement.
- **React** — viable and more future-optionality (React Native), but heavier than we
  need; Svelte preferred for simplicity.
- **NiceGUI** — websocket/stateful model makes mobile polish and auth awkward.
- **Electron** — desktop-only; irrelevant to an Android target.

## 3. Architecture principle: stay "Capacitor-ready"

We will **not** build a native app now, but we keep the option open at near-zero cost by
following these constraints from day one. (Capacitor = the modern web→native wrapper;
ships our static SPA inside a native WebView with a JS bridge to device plugins.)

1. **Pure static SPA build** — frontend is static files calling an API; no SSR coupling.
2. **Configurable API base URL** — all calls go through one `API_BASE` constant, never a
   hardcoded same-origin `/api`. (Same-origin in browser; points at the server in a
   native shell.)
3. **Token-capable auth, not cookie-only** — backend accepts the session token via
   **either** an httpOnly cookie (web) **or** an `Authorization: Bearer` header (native).
   See §4.
4. **CORS ready** — enable FastAPI CORS middleware now (no-op while same-origin), so a
   different app origin (`capacitor://localhost`) works later.
5. **OIDC handled server-side** — the native deep-link redirect becomes a config value
   later, not an architecture change.

These are conventions, not extra infrastructure — no native toolchain is added today.
Ships as an installable **PWA** now; **Capacitor** wraps the same `dist/` when we want a
Play Store app.

## 4. Auth model (LOCKED in shape, deferred in time)

Pattern: **the "Immich model"** — backend is a **confidential OIDC client** doing the
**Authorization Code** flow server-side, then issuing **its own session token**.

- IdP: **Authentik** (OIDC provider). Backend holds the client secret; browser/app never
  see IdP tokens.
- After login the backend mints its own session token; clients send it back as a cookie
  (web) or bearer header (native) — satisfies §3.3.
- Native login later = open IdP in an in-app browser, deep-link back
  (`com.<x>.meals://callback`), backend exchanges the code. Same flow as Immich mobile.
- **v1 ships with no auth.** Because OIDC is server-side and token-based, adding it later
  doesn't touch the data model or the SPA's API calls.

## 5. Deployment shape

- One Docker image: `uvicorn` (FastAPI) serving `/api/*` + the built SPA static files.
- SQLite DB on a mounted volume (survives container rebuilds; easy to back up).
- Dev: Vite dev server with a proxy `/api` → FastAPI for hot reload.

## 6. API surface (v1 draft)

Implied tables (full data model = next section):
- `food` — catalogue, nutrition per 100g, filled gradually.
- `entry` — a log referencing a `food`, with an amount, a **meal slot**, the **consumed
  date** (which day's meal), and a **created-at** timestamp (when the row was inserted —
  kept for later visualisations of logging behaviour).

Conventions used below:
- **Meal slot** — every entry is tagged `breakfast | lunch | dinner | snack`, chosen from
  a dropdown. The frontend remembers the **last-used slot** and defaults to it for the
  next item (a run of same-meal entries needs no re-picking).
- **"recent days"** = the previous **5** days (excluding today).
- **"popular"** = ranked by the **number of distinct days** a food was logged, all-time
  (eating bread 5× in one day counts as 1, not 5). Tunable later with real usage.

### Core (write + read)
- `POST /api/foods` — add a food to the catalogue `{name, kcal_per_100g, …macros later}`.
- `GET  /api/foods?q=` — search the catalogue (for the picker).
- `POST /api/entries` — log a food `{food_id, amount_grams, meal, consumed_date?}`
  (`consumed_date` defaults to today); server sets `created_at` and computes kcal.
- `GET  /api/entries/today` — today's entries, grouped by meal slot (the running list).
- `DELETE /api/entries/{id}` — remove a mis-logged entry.

### History-driven helpers (the "smart input")
1. `GET /api/today/summary` — today's totals. v1: `{ "calories": <sum> }`.
2. `GET /api/suggestions/same-meal?meal=<slot>&days=5` — what you ate at this meal on each
   of the previous `days` days. Grouped by day → food + amount.
3. `GET /api/suggestions/popular?meal=<slot>&limit=10` — foods most logged at this meal,
   ranked by **distinct days logged**. **Omit `meal` for most-popular overall.**

## 7. Resolved

All semantics resolved 2026-06-23:
- Meal slots = **breakfast / lunch / dinner / snack** (no "other"), chosen via a dropdown
  that remembers the last-used slot (frontend-persisted).
- `entry` keys off the slot (not a time window); also stores `consumed_date` and a
  `created_at` insertion timestamp (for future visualisations).
- Popularity → **distinct days logged**, all-time (re-logging a food within a day counts
  once). Tunable later.
- Suggestions do **not** hide foods already logged today.
- same-meal helper looks at the previous 5 days (excludes today).

## 8. Data model

SQLite, two tables. Nutrition is entered **once** on the food (per 100 g); each entry
stores a **computed snapshot** of the amount actually eaten — so daily totals need no
join or recompute, and past entries stay correct even if a food's values are edited later.

### Nutrition fields (the label set)
Captured per food so you never re-enter: **required** `calories` (kcal), `protein`,
`carbohydrate`, `fat`; **optional** `saturated_fat`, `sugar`, `fiber`, `salt` (fill if the
label lists them). All grams except `calories` (kcal). Extensible later.

### `food` — catalogue (values per 100 g)
```sql
CREATE TABLE food (
  id            INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,
  calories      REAL NOT NULL,   -- kcal / 100 g
  protein       REAL NOT NULL,   -- g / 100 g
  carbohydrate  REAL NOT NULL,
  fat           REAL NOT NULL,
  saturated_fat REAL,            -- optional label fields
  sugar         REAL,
  fiber         REAL,
  salt          REAL,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### `entry` — a logged item (snapshot for the amount eaten)
```sql
CREATE TABLE entry (
  id            INTEGER PRIMARY KEY,
  food_id       INTEGER NOT NULL REFERENCES food(id),
  amount_grams  REAL NOT NULL,
  meal          TEXT NOT NULL CHECK (meal IN ('breakfast','lunch','dinner','snack')),
  consumed_date TEXT NOT NULL,   -- 'YYYY-MM-DD' (which day's meal)
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),  -- insertion time
  -- snapshot = food.<field> * amount_grams / 100, computed at insert
  calories      REAL NOT NULL,
  protein       REAL NOT NULL,
  carbohydrate  REAL NOT NULL,
  fat           REAL NOT NULL,
  saturated_fat REAL,
  sugar         REAL,
  fiber         REAL,
  salt          REAL
);

CREATE INDEX idx_entry_date      ON entry(consumed_date);
CREATE INDEX idx_entry_meal_date ON entry(meal, consumed_date);
CREATE INDEX idx_entry_food      ON entry(food_id);
```

Insert-time computation: `entry.X = round(food.X_per_100g * amount_grams / 100, 3)` for
each present field (NULL stays NULL). 3 decimals keeps sub-gram portions honest
(e.g. 3.15 g fat/100 g × 50 g = 1.575, not 1.58); 4+ is overkill.

### How the queries map
- **today/summary** → `SELECT sum(calories), sum(protein), … FROM entry WHERE consumed_date = ?`
- **same-meal** → `WHERE meal = ? AND consumed_date BETWEEN ? AND ?` (previous 5 days)
- **popular[meal]** → `SELECT food_id, count(DISTINCT consumed_date) d FROM entry
  [WHERE meal = ?] GROUP BY food_id ORDER BY d DESC` (distinct-days ranking)

### Deferred
- Amounts are in **grams**; per-item foods (e.g. "1 egg") are entered by weight for now —
  optional per-food serving weights can come later.
- Foods are deduplicated by picking from the catalogue; no auto-merge in v1.

## 9. UX/UI — current version

**One mobile-first page**, no routing except the new-food popup. No grouping, no nesting,
no edit/delete UI yet.

Layout (top → bottom):

```
┌─────────────────────────────┐
│         1 850 kcal          │  ← today's total calories (top, centered)
├─────────────────────────────┤
│ Eggs                        │
│ Oat flakes                  │  ← today's items: flat list, names only
│ Bread                       │     (just confirms it was entered)
│ …                           │
├─────────────────────────────┤
│ [ Breakfast ▾ ]             │  ← meal slot (defaults to last used)
│ All | Recent | Top slot | … │  ← source tab strip (horizontally scrollable)
│ ┌─────────────────────────┐ │
│ │ Eggs                    │ │
│ │ Oat flakes              │ │  ← food list (5-item fixed height, scrollable)
│ │ Bread                   │ │     tap to select; active item highlighted
│ │ Chicken                 │ │
│ │ Rice                    │ │
│ └─────────────────────────┘ │
│ [ + Add missing ]           │  ← opens new-food popup
│ [ grams ____ ]   [ Save ]   │  ← weight + submit
└─────────────────────────────┘
```

### Add-item form
- **Slot dropdown** — breakfast/lunch/dinner/snack; defaults to last-used (frontend-stored).
  Changing slot resets the source tab to `Recent (same meal)`.
- **Source tab strip** — horizontally scrollable strip of four tabs that controls which
  food list is shown:
  - `All` — full food catalogue (`GET /api/foods`)
  - `Recent (same meal)` — foods eaten at this slot in the last 5 days (default)
  - `Top this slot` — most popular foods for this slot (distinct-days ranking)
  - `Top overall` — most popular foods regardless of slot
  Tapping a tab fetches the relevant list and updates the food list below.
- **Food list** — fixed-height container (exactly 5 base-item heights; scrolls if more).
  Each row has a minimum height; long names word-wrap within that height. Tapping a row
  selects it (highlighted) and pre-fills the last-used gram amount if available.
- **Add missing** — food not in any list → opens the **new-food popup** (modal) with the
  per-100g nutrition form (calories + macros required; sat-fat, sugar, fiber, salt
  optional). Saving `POST /api/foods`, then selects the new food in the list.
- **Weight** — single grams field; pre-filled from the selected item's last logged amount.
- **Save** — `POST /api/entries {food_id, amount_grams, meal, consumed_date=today}`; the
  response (with computed calories) is appended to the list and added to the total.

### Out of scope for this UI pass
Edit/delete entries, grouping by meal, macros display (calories total only), history
browser, free-text food search.

## 10. Open / Next

- [x] Data model, API surface, UX/UI (initial) — drafted.
- [x] Styling framework → **Tailwind + DaisyUI**.
- [ ] Scaffold skeleton: FastAPI + SQLite schema + Svelte shell (Tailwind+DaisyUI) + Dockerfile.

## 11. Decision log

| Date | Decision |
|---|---|
| 2026-06-23 | Build own tracker instead of depending on FatSecret (storable-data terms). |
| 2026-06-23 | Stack: Svelte SPA + FastAPI + SQLite + Docker on Pi. |
| 2026-06-23 | Stay Capacitor-ready (SPA + JSON API + token auth); no native build yet. |
| 2026-06-23 | Auth = Immich model (server-side confidential OIDC client, own session), Authentik IdP; deferred to post-v1. |
| 2026-06-23 | v1 includes lightweight history (same-meal / popular helpers + today total). |
| 2026-06-23 | History keys off **named meal slots** (4, no "other"); popularity = distinct-days count, all-time. |
| 2026-06-23 | `entry` stores `consumed_date` + `created_at`; frontend remembers last meal slot. |
| 2026-06-23 | Nutrition = full label set on `food` (per 100g); `entry` stores a computed snapshot. |
| 2026-06-23 | Entry snapshot rounded to 3 decimals. Styling = Tailwind + DaisyUI. |
| 2026-06-24 | i18n via `src/lib/i18n.js` (`t()` + `navigator.languages`); en + uk supported. `?lang=` param overrides. |
