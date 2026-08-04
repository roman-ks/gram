# 0012 — "Recent (same meal)" tab doesn't reflect food just added via "All" tab

> Status: **done** · Shipped: 2026-08-04 · Type: **bug** · Created: 2026-08-04

## Goal
An entry added through the "All" tab should immediately show up in "Recent (same meal)" the next time the add-food flow is opened for that meal slot.

## Repro
1. Open the app, on the Today page press "+" on the Breakfast slot.
2. On the add-food page, switch to the "All" tab.
3. Select a food (e.g. "Cheese") that has never been logged for Breakfast before.
4. Enter a weight (e.g. 50) and press the 💾 save button.
5. Confirm on the Today page that "Cheese" now appears under Breakfast (50g).
6. Press "+" on the Breakfast slot again to reopen the add-food page.
7. Switch to the "Recent (same meal)" tab.

**Expected:** "Cheese" is visible in "Recent (same meal)" right away, since it was just logged for this meal slot.
**Actual:** "Recent (same meal)" still shows "— none —", as if the entry hadn't been added at all. (Reported by user: it eventually shows up, but only after a delay of roughly a day.)

## Acceptance criteria
- [x] Immediately after saving an entry for a given meal slot, reopening the add-food page for that same slot and switching to "Recent (same meal)" shows the food just added.
- [x] This holds regardless of which tab ("All", "Top this slot", "Top overall") the food was originally selected from.

## Scope / hints (optional)
- Affected areas: <e.g. backend/app/routers/suggestions.py, frontend/src/lib/AddFoodPage.svelte>
- Out of scope: <things to explicitly NOT touch>

## Notes / decisions
Root cause: `same_meal()` in `backend/app/routers/suggestions.py` queried the window `[today - days, today - 1]`, excluding today entirely — so an entry logged today never appeared until the window advanced past it the next day. Fixed the window to `[today - (days - 1), today]`, keeping it `days` days wide but including today. Verified in-browser: logging a never-before-seen food for a slot makes it show up in "Recent (same meal)" for that slot immediately on reopen.
