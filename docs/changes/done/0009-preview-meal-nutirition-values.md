# NNNN — Preview meal nutrition values

> Status: **done** · Type: **feature** · Created: 2026-07-02 · Shipped: 2026-07-02

## Goal
User is able to know nutrition values for the selected food item and entered weight.

## Context
On Add meal page user can select item and enter weight. But they don't know if the weight is too little or too much as the final values for the weight are only shown on Today page.

The values need to be shown for currently entered weight below the weight field in same tags format as on todays page. Update values as weight input changes, no button press needed. 

## Acceptance criteria
- [x] On Add food page, once food item is selected, as weight is being entered the tags appear below the input field displaying nutrition values for current weight of food item
- [x] tags exist even when no weight or food item entered

## Scope / hints (optional)
- Affected areas: <e.g. backend/app/main.py, frontend/src/App.svelte>
- Out of scope: </things to explicitly NOT touch>

## Notes / decisions
- Frontend-only change: no backend needed. `Recent`/`Popular` suggestion APIs return only `food_id`/`food_name`, so a `foodsMap` (food_id → full food object) is lazily populated via `allFoods()` for non-All tabs.
- For the `All` tab the map is populated inline while building suggestions (no extra fetch).
- Tags always render (showing 0 when no food/weight), satisfying the "exist even when empty" AC without layout shift.
- `stat-tag` CSS duplicated from `App.svelte` — kept scoped per component rather than extracting a shared class.