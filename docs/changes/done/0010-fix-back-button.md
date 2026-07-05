# 0010 — Back navigation button doesn't navigate back

> Status: **done** · Type: **bug** · Created: 2026-07-02 · Shipped: 2026-07-02

## Goal
Make browser back button navigate to previous screen same way as on-page button does.

## Repro
1. Navigate to Add meal page
2. Select any food item and enter any weight
3. Press save button
4. Press Back navigation button in browser
**Expected:** Today page is displayed
**Actual:** Tab goes back to New Tab or precious page opened in this page, not to Today page


## Acceptance criteria
- [x] Navigate back browser button causes navigation to previous page
- [x] Browser back button causes back navigation for all pages that have Back button on page

## Scope / hints (optional)
- Affected areas: <e.g. backend/app/main.py, frontend/src/App.svelte>
- Out of scope: </things to explicitly NOT touch>

## Notes / decisions
- Used `history.pushState({d: N})` at each navigation level (d=1 add food, d=2 new food, d=3 ingredient picker). On-page back buttons now call `history.back()` instead of dispatching the `back` event.
- Each component registers its own `popstate` listener (in `onMount`, cleaned up on destroy) and closes itself when `event.state.d` drops to its parent's depth.
- When a sub-page closes programmatically (food created, ingredient picked), `history.back()` is called after setting the flag to false, so the stale history entry is popped without re-triggering the close logic (the guard checks the flag first).
- `on:back` event bindings removed from all parent components since they are never dispatched anymore.