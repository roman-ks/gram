# 0014 — Enter key doesn't submit the add-food form

> Status: **done** · Shipped: 2026-08-04 · Type: **bug** · Created: 2026-08-04

## Goal
Pressing Enter while in the add-food flow (not the "Add missing" food flow) should save the entry, same as pressing the 💾 save button.

## Repro
1. Open the app, on the Today page press "+" on any meal slot (e.g. Lunch).
2. Switch to the "All" tab and select a food (e.g. "Egg").
3. Click into the grams input and type a weight (e.g. 60).
4. Press Enter on the keyboard (do not click the 💾 save button).
5. Check the grams input value and the Today page's Lunch section.
6. For comparison, repeat steps 1-3 and this time click the 💾 save button instead of pressing Enter.

**Expected:** Pressing Enter saves the entry and returns to the Today page, same as clicking 💾 (in step 6, the entry is saved and appears on the Today page immediately).
**Actual:** Pressing Enter does nothing — the add-food page stays open, the grams input keeps its typed value, and no entry is added (confirmed the Today page total/list is unchanged). Clicking 💾 for the same food/weight does save correctly.

## Acceptance criteria
- [x] Pressing Enter while focused in the grams input on the add-food page saves the entry, identically to clicking the 💾 button.
- [x] This does not affect the separate "Add missing" food flow, which is out of scope for this bug.

## Scope / hints (optional)
- Affected areas: <e.g. frontend/src/lib/AddFoodPage.svelte>
- Out of scope: "Add missing" / new-food creation flow (frontend/src/lib/NewFoodPage.svelte)

## Notes / decisions
Root cause: the grams input and 💾 save button in `AddFoodPage.svelte` were bare siblings in a `<div>`, not wrapped in a `<form>`, so Enter in the number input had nothing to submit to. Wrapped them in a `<form on:submit|preventDefault={save}>` with the button as `type="submit"`; this only affects the grams-entry row, leaving the separate "Add missing" flow (`NewFoodPage.svelte`) untouched. Verified in-browser: typing a weight and pressing Enter saves the entry (grams field clears, entry appears on the Today page) the same as clicking 💾.
