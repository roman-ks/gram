# 0015 — Selected food scrolls out of view when the on-screen keyboard opens (mobile)

> Status: **done** · Shipped: 2026-08-05 · Type: **bug** · Created: 2026-08-05

## Goal
On mobile, focusing the grams input on the add-food page should not cause the currently selected food item to be scrolled out of view / hidden behind the tab bar.

## Repro
1. On a mobile browser (e.g. Chrome for Android), open the app and press "+" on a meal slot to open the add-food page (tabs: "Всі" / "All", "Нещодавні (цей прийом)" / "Recent (same meal)", "Топ цього прийому" / "Top this slot", etc.).
2. On a tab with several items, tap a food item partway down the list to select it (it highlights, e.g. with an orange/peach background).
3. Before the keyboard appears, note the selected item's position: it is fully visible in the list, roughly in the middle of the screen, below the tab bar.
4. Tap the grams input field near the bottom of the screen to enter a weight.
5. The on-screen keyboard opens.

**Expected:** The selected food item stays visible in the space that remains above the keyboard. If it was already visible in that remaining space, it should stay in the same position (no unnecessary scroll/jump). If its original position would now be covered by the keyboard (e.g. it was near the bottom of a long list), the list should scroll just enough to keep the item visible instead of hiding it — there's no requirement to keep it pixel-identical in that case, just visible.

**Actual:** The whole food list scrolls upward when the keyboard opens. The selected item ends up scrolled almost entirely out of view, ending up underneath/behind the sticky tab bar ("Всі" / "Нещодавні" / "Топ...") with only a sliver of its text peeking out above the header, while an unrelated item (the one originally below it) is now the first fully visible list entry. The user has no visual confirmation of which item is still selected without dismissing the keyboard again.

This was observed on Chrome for Android (viewport ~1080×2400 physical / ~360×800 CSS px).

**Playwright cannot reproduce or verify this bug.** Confirmed by testing directly: with the browser resized to a 360×800 mobile-sized viewport, opening the add-food page and focusing the grams input, `window.visualViewport.height` stays at 800 throughout — it never shrinks, and no `resize` event fires. Playwright's Chromium runs on the desktop OS and never invokes a real on-screen keyboard (mobile viewport/device emulation only changes viewport size and touch/UA flags, not keyboard behavior), so there is nothing to trigger the layout shift this bug depends on. This isn't a matter of better selectors or timing — the browser genuinely never enters the state where the bug occurs. Automated end-to-end verification of the actual fix is not possible; see acceptance criteria below for how this is instead verified.

## Acceptance criteria
- [ ] (Manual, on a real phone) After the grams input is focused and the on-screen keyboard is showing, the selected/highlighted food item is fully visible within the remaining visible viewport (not covered by the keyboard, and not hidden behind the tab bar header).
- [ ] (Manual, on a real phone) If the selected item was already fully visible within the space that remains once the keyboard opens, its on-screen position does not change (no gratuitous scroll).
- [ ] (Manual, on a real phone) If keeping the item's exact position isn't possible (e.g. it was low enough in a long list that the keyboard would cover it), the list scrolls just enough to bring the item fully into view rather than leaving it hidden.
- [ ] (Manual, on a real phone) The grams input, save button, and macro preview row remain visible and usable while the keyboard is open (already true today — don't regress this).
- [x] (Automatable) The fix reacts to `window.visualViewport`'s `resize`/`scroll` events (or equivalent), not to Svelte's own reactivity alone — this can be confirmed by reading the implementation, or by dispatching a synthetic `visualViewport` resize event in a test and asserting the handler runs (e.g. that it calls `scrollIntoView` on the selected item). This checks the mechanism is wired up correctly; it cannot substitute for the manual checks above, since the real trigger condition (an actual keyboard shrinking the viewport) can't be produced in Playwright.
- [x] Desktop behavior is unaffected (verify manually or via Playwright at a desktop viewport size — no `visualViewport` resize occurs there today, so this should trivially pass, but confirm no regression from the new listener/logic).

## Scope / hints (optional)
- Affected areas: frontend/src/lib/AddFoodPage.svelte. Likely involves listening for the visual viewport shrinking (e.g. `window.visualViewport`'s `resize` event) when the keyboard opens, and scrolling the selected item into view (e.g. `element.scrollIntoView({ block: 'nearest' })`) relative to the newly-shrunk viewport.
- Out of scope: general redesign of the add-food page layout; desktop behavior (not affected, no on-screen keyboard).

## Notes / decisions
- Implementation: `frontend/src/lib/AddFoodPage.svelte`
  - Added `itemRefs` (food_id → button element), populated via `bind:this={itemRefs[s.food_id]}` on each list item button.
  - Added a second `onMount` that, when `window.visualViewport` exists, listens for its `resize` and `scroll` events and calls `itemRefs[selectedFoodId]?.scrollIntoView({ block: 'nearest' })`. Listener is removed on unmount. Guarded with `if (!vv) return`, so it's a no-op on browsers without `visualViewport` support.
  - Used `block: 'nearest'` (not `'center'`/`'start'`) so an already-visible item doesn't move — it only scrolls the minimum amount needed to bring a covered item back into view, per AC.
  - No changes to desktop layout/logic; the listener only ever fires in response to real `visualViewport` events, which don't occur on desktop.
- Verified: `svelte-check` (0 errors) and `vite build` succeed. Code path for the automatable AC reviewed directly (listener correctly bound to `visualViewport`, not Svelte reactivity).
- **Not verified this session:** the four manual, real-phone acceptance criteria above (checkboxes left unticked). A live Playwright desktop check was also skipped — the shared headless browser profile was locked by another running process at the time, so it wasn't safe to reuse (killing it risked another session's work). The `svelte-check`/build results give reasonable confidence there's no desktop regression, but that AC should still get a real visual pass before fully trusting it.
