# Changelog

One line per shipped change, newest first. Each links its full request in `done/`.
Format: `YYYY-MM-DD · type · summary (#NNNN)`

2026-07-11 · bug · Service worker served stale index.html (old hashed asset URLs → 404) after redeploys on the same origin; navigation requests are now network-first, static assets stay cache-first (no spec)
2026-07-05 · feature · Delete entry from Today page: long-press (mobile) or right-click (desktop) opens a floating 🗑️ context menu above the entry ([#0011](done/0011-delete-entry.md))
2026-07-02 · bug · Fix browser back button: pushState at each nav level so the browser history matches in-app navigation ([#0010](done/0010-fix-back-button.md))
2026-07-02 · feature · Live nutrition preview on Add food page: stat-tags below weight input update reactively as weight is typed ([#0009](done/0009-preview-meal-nutirition-values.md))
2026-07-02 · feature · Add Recipes: build a dish from weighted ingredients; per-100g nutrition computed from cooked weight ([#0008](done/0008-recipes.md))
2026-06-29 · feature · Split into Today page (slot-grouped entries + macros) and Add food page (full-screen, slot-aware) ([#0007](done/0007-separate-add-food-page.md))
2026-06-26 · feature · Update primary colors to warm peachy theme (#E8B89F/#D4956E) for better brand identity ([#0006](done/0006-warm-peachy-brand-colors.md))
2026-06-26 · feature · Add PWA manifest and service worker for Chrome WebAPK installability on Android ([#0005](done/0005-chrome-installable-webapp.md))
2026-06-25 · feature · Replace food-picker dropdowns with pill tab strip (All / Recent / Top slot / Top overall) and scrollable list ([#0004](done/0004-replace-fooditem-dropdowns.md))
2026-06-24 · feature · Add i18n: English and Ukrainian via t() function, language auto-detected from browser ([#0003](done/0003-add-i18n.md))
2026-06-24 · feature · Improve "Add missing" form: reorder fields (Calories/Protein/Carbs/Sugar/Fat/Sat-fat) with floating labels ([#0001](done/0001-improve-add-missing-window.md))
