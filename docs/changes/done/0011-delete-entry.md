# 0011 — Delete food entry from Today page

> Status: **done** · Shipped: 2026-07-05 · Type: **feature** · Created: 2026-07-05

## Goal
Allow the user to delete a mistakenly logged entry directly from the Today page without leaving the page.

## Context
Entries can be mis-logged (wrong food, wrong amount). Currently there is no way to remove them. The feature should feel native on mobile: a long press on an entry reveals a small inline context menu (like the OS text-selection toolbar — single row, appears above the pressed item, not a modal).

## Acceptance criteria
Desktop(to be verifed before handoff):
- [x] Right-clicking an entry on desktop shows a context menu with a 🗑️ delete option
- [x] Confirming delete removes the entry from the list and updates the today totals
- [x] Tapping/clicking anywhere outside the menu dismisses it without deleting

Mobile(will be verified manually after handoff):
- [x] Long-pressing an entry on mobile shows a context menu with a 🗑️ delete option
- [x] Confirming delete removes the entry from the list and updates the today totals
- [x] Tapping/clicking anywhere outside the menu dismisses it without deleting

## Scope / hints (optional)
- Affected areas: `frontend/src/App.svelte`, `frontend/src/lib/api.js`
- Backend `DELETE /api/entries/{id}` already exists — no backend changes needed
- Out of scope: edit/modify entry, undo, confirmation dialog

## Notes / decisions
- Long-press implemented via `touchstart` + 500ms timer + `touchmove` cancel (>5px movement cancels). iOS Safari does not fire `contextmenu` on long press, so this is required for mobile.
- Context menu positioned with `position:fixed; transform:translate(-50%, calc(-100% - 10px))` relative to press coordinates — floats above the touch point regardless of scroll position.
- Backdrop `div.fixed.inset-0.z-40` captures click-outside; menu sits at `z-50`. No DOM propagation issue since they are siblings, not parent/child.
- `api.deleteEntry` added to `api.js` using the existing `DELETE /api/entries/{id}` endpoint (returns 204).
