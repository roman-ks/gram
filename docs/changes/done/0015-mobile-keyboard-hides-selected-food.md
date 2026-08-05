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
- [x] (Manual, on a real phone) After the grams input is focused and the on-screen keyboard is showing, the selected/highlighted food item is fully visible within the remaining visible viewport (not covered by the keyboard, and not hidden behind the tab bar header).
- [x] (Manual, on a real phone) If the selected item was already fully visible within the space that remains once the keyboard opens, its on-screen position does not change (no gratuitous scroll).
- [x] (Manual, on a real phone) If keeping the item's exact position isn't possible (e.g. it was low enough in a long list that the keyboard would cover it), the list scrolls just enough to bring the item fully into view rather than leaving it hidden.
- [x] (Manual, on a real phone) The grams input, save button, and macro preview row remain visible and usable while the keyboard is open (already true today — don't regress this).
- [x] (Automatable) The fix reacts to `window.visualViewport`'s `resize`/`scroll` events (or equivalent), not to Svelte's own reactivity alone — this can be confirmed by reading the implementation, or by dispatching a synthetic `visualViewport` resize event in a test and asserting the handler runs (e.g. that it calls `scrollIntoView` on the selected item). This checks the mechanism is wired up correctly; it cannot substitute for the manual checks above, since the real trigger condition (an actual keyboard shrinking the viewport) can't be produced in Playwright.
- [x] Desktop behavior is unaffected (verify manually or via Playwright at a desktop viewport size — no `visualViewport` resize occurs there today, so this should trivially pass, but confirm no regression from the new listener/logic).

## Scope / hints (optional)
- Affected areas: frontend/src/lib/AddFoodPage.svelte. Likely involves listening for the visual viewport shrinking (e.g. `window.visualViewport`'s `resize` event) when the keyboard opens, and scrolling the selected item into view (e.g. `element.scrollIntoView({ block: 'nearest' })`) relative to the newly-shrunk viewport.
- Out of scope: general redesign of the add-food page layout; desktop behavior (not affected, no on-screen keyboard).

## Notes / decisions

### Attempt 1 (reverted from "done" — did not fix the bug on-device)
- Added `itemRefs` (food_id → button element) and, on `window.visualViewport`'s `resize`/`scroll`, called `itemRefs[selectedFoodId]?.scrollIntoView({ block: 'nearest' })`.
- Confirmed still broken on a real phone: reporter observed the top-selected item now jumping/scrolling out of view several times during the keyboard-open animation, worse than a single clean jump. Root cause: the page container relied on `h-dvh` in normal document flow (not `position: fixed`). On focus, the browser's own "scroll focused input into view" behavior scrolls the whole document (dragging the header along with it), and that native scroll fights with our own `scrollIntoView` call — two competing scroll actors produce the jumpiness, rather than fixing it.

### Attempt 2 (current)
- User's diagnosis/proposal: pin the header (back button + tabs) so it can't move, and resize only the list to fill the remaining space when the keyboard opens.
- Implementation: `frontend/src/lib/AddFoodPage.svelte`
  - The whole page root is now `position: fixed; left/right: 0` with `top`/`height` driven from JS (`vvTop` / `vvHeight`, sourced from `window.visualViewport.offsetTop` / `.height`), falling back to `100dvh` before `visualViewport` is available.
  - Because the root is `position: fixed`, there's nothing left in normal document flow for the browser's native "scroll into view" to act on — that eliminates the competing scroll that caused attempt 1's jumping.
  - The header/tabs/bottom-bar stay `shrink-0` inside a `flex flex-col h-full` — since the *root's* height now shrinks with the keyboard (not just relying on `dvh`), the food list (`flex-1 overflow-y-auto`) is what absorbs the shrink, exactly per the user's ask ("resize only the list, use all remaining space").
  - Kept the `itemRefs` + `scrollIntoView({ block: 'nearest' })` call (now awaiting `tick()` after the resize so it reads post-resize layout) for the case where the selected item ends up below the new, shorter list viewport and needs an explicit scroll to come back into view.
- Verified this session: `svelte-check` (0 errors, 0 warnings) and `vite build` succeed.
- Confirmed by reporter on a real phone: all manual ACs pass. Marking done.
