# Gram — Claude Code context

## What this project is

Gram is a self-hosted meal/calorie tracker. Svelte 4 SPA + FastAPI backend + SQLite. Runs on a Raspberry Pi in production; dev uses hot-reload servers.

## Project structure

```
backend/
  app/
    main.py          # FastAPI app, mounts routers
    db.py            # SQLite connection + schema init
    schemas.py       # Pydantic models
    config.py        # env vars (MEAL_DB path)
    routers/
      entries.py     # CRUD for daily log entries
      foods.py       # food/recipe catalogue
      recipes.py     # recipe creation
      suggestions.py # recent/popular suggestions

frontend/
  src/
    App.svelte               # Today page + routing (page = 'today' | 'add')
    lib/
      AddFoodPage.svelte     # Full-screen food picker + weight input
      NewFoodPage.svelte     # Create meal or recipe (tabs)
      AddIngredientPage.svelte  # Ingredient picker for recipes
      api.js                 # fetch wrapper for all backend calls
      i18n.js                # t() translation, en + uk
    app.css                  # Tailwind base + DaisyUI
  public/
    service-worker.js        # PWA caching (cache-first for assets)
    manifest.json
  vite.config.js             # proxies /api → :8000

docs/
  DESIGN.md                  # Architectural decisions only (§11)
  changes/
    CHANGELOG.md             # One line per shipped feature, newest first
    TEMPLATE.md              # Spec template
    open/                    # Pending specs (0NNN-slug.md)
    done/                    # Completed specs (0NNN-slug.md)

.claude/skills/
  implement/        # /implement skill — spec → code → done/
  run-meal-advice/  # /run skill — starts both dev servers
```

## Docs workflow

- New feature idea → create spec in `docs/changes/open/` using `TEMPLATE.md`
- After shipping → tick ACs, update status, move to `done/`, add line to `CHANGELOG.md`
- Architectural decisions only → also log in `DESIGN.md §11`

## Testing gotcha — service worker caches old JS

The PWA service worker (`public/service-worker.js`) uses cache-first for all assets. When running Playwright tests against the dev server, the browser may serve stale compiled JS even after a full page reload.

**Symptom:** code changes aren't reflected; element classes or behaviour match the old version.

**Fix — unregister the SW before testing:**
```js
await page.evaluate(() =>
  navigator.serviceWorker.getRegistrations()
    .then(regs => Promise.all(regs.map(r => r.unregister())))
);
await page.reload();
```

Or inline in a Playwright evaluate before your first assertion. Do this once per browser session; the SW won't re-register until the next full navigation after the page has loaded.
