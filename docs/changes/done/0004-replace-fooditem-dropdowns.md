# 0004 — replace dropdowns with tabs and a list

> Status: **open** · Type: **feature** · Created: 2026-06-25

## Goal
Replace Source dropdown with tabs, replace food item dropdown with a list.

## Context
Food item dropdown limits extesibility. We can't add more data per item, search to it. Maybe we can but it would look weird.

Instead each food item needs to a list element. Element is just the item name for now, but keep it extensible to show recent serving size etc later.

The source dropdown needs to be replaced with horizontal scrollable tab strip with new tab value "All" added.
Tab order in the strip:
| All | Recent (same meal) | Top this slot | Top overall |

Default to `Recent (same meal)`.

Food items list is displayed below the tab strip, the list is populated based on tab selection.
List is limited to fit 5 items, scroll added as nessessary. 
Use fix element height, to calc list height. If some items have long text and are wrapped, the list height should not change.

`+ Add missing button` is below the list.

## Acceptance criteria
- [x] Dropdowns gone
- [x] `Recent (same meal)` is default tab when page loaded/slot changed
- [x] List items are updated based on tab selection
- [x] List item text is word-wrapped to fit width layout
- [x] List spans exactly 5 min height(no wrapping) elements.
- [x] DESIGN.md is checked for references to old layout and updated

## Scope / hints (optional)
- Affected areas: frontend only

## Notes / decisions
- **"All" tab uses `GET /api/foods`** (the catalogue list endpoint, no query param). Items are
  mapped to the same `{food_id, food_name, last_amount_grams: null}` shape as the suggestion
  endpoints so the rest of the selection/prefill logic stays unchanged.
- **`last_amount_grams` is `null` for the All tab** — the grams field is left blank when
  selecting from the full catalogue, since there's no history to prefill from.
- **Tab strip resets to `Recent (same meal)` on slot change** — handled via `on:change` on
  the slot select, keeping it simple without extra reactive tracking.
- **Fixed item height with `min-height`** — list items use `min-height: 2.75rem` (44 px) so
  long names word-wrap within the item rather than being truncated. The list container height
  is `calc(5 * 2.75rem)`; items that wrap beyond their min-height may push into the scroll
  area rather than expanding the container.
- **DESIGN.md updated** — section 9 layout diagram and Add-item form description rewritten;
  decision log entry added for 2026-06-25.
