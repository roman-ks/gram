# 0013 — "All" tab doesn't prefill grams when a food is selected

> Status: **done** · Shipped: 2026-08-04 · Type: **bug** · Created: 2026-08-04

## Goal
Selecting a food from the "All" tab should prefill the grams input the same way selecting a food from the other tabs does.

## Repro
1. Open the app, on the Today page press "+" on any meal slot (e.g. Breakfast).
2. Switch to the "All" tab and select any food (e.g. "Test Apple").
3. Observe the grams input next to the 💾 save button.
4. For comparison, switch to the "Top overall" tab and select a food (e.g. "Банан").
5. Observe the grams input again.

**Expected:** Selecting a food on the "All" tab prefills the grams input with a default weight, same as on "Recent (same meal)", "Top this slot", and "Top overall".
**Actual:** Selecting a food on the "All" tab leaves the grams input empty. Selecting a food on "Top overall" (and the other non-"All" tabs) prefills it (e.g. "130" for "Банан").

## Acceptance criteria
- [x] Selecting a food from the "All" tab prefills the grams input with a default weight, consistent with the other tabs.

## Scope / hints (optional)
- Affected areas: <e.g. frontend/src/lib/AddFoodPage.svelte>
- Out of scope: <things to explicitly NOT touch>

## Notes / decisions
Root cause: `AddFoodPage.svelte`'s "All" tab built its suggestion list straight from `api.allFoods()`, hardcoding `last_amount_grams: null` for every food — unlike the other tabs, which get `last_amount_grams` from suggestion endpoints backed by entry history. Fixed by also fetching global usage history (`api.popular(null, 1000)`) alongside the food catalogue when the "All" tab loads, and using each food's last logged amount where available. Foods with no history at all (never logged) fall back to a `DEFAULT_GRAMS = 100` constant so the field is never left empty. `api.popular()` gained an optional `limit` param to support the large fetch. Verified in-browser: a never-before-logged food prefills to 100g on the "All" tab; after logging it once, reselecting it on "All" prefills the actual last-used amount.
