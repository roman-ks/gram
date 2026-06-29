# 0007 — Separate Add food page, more stats on Today page

> Status: **done** · Shipped: 2026-06-29 · Type: **feature** · Created: 2026-06-29

## Goal
Add a separate Add food page to have more vertical space to show food lists.

## Context
Currently list of food consumed and add food form are on one page which forces scrolling and limits size of list of foods in recent/all/top list to show. 


### Pages separation
#### Today page
Difference with old layout:
- slots added(breakfast/lunch...)
- app navigation added
- removed slot selection, all/recent/top tabs and list, weight input and save button
Layout (top → bottom):

```
┌─────────────────────────────┐
|                    💪 12.3g |  ← protein weight consumed today. aligned vertically with fats and carbs. All three together are same height as kcal counter, Prot, fat, carb need smaller font size, kcal font unchanged. 
│         1 850 kcal 🥑 56.4g │  ← today's total calories (top, centered). Fats weight consumed today
|                    🌾 78.9g |  ← carbs consumed today  
├─────────────────────────────┤
│Breakfast                  + |  ← slot name is on diff tabulation level then its items. + is on the right
| Eggs                        │
| 200g ⚡250 💪10g 🥑20g 🌾0.4 |  ← weight, calorie, protein, fat carb for Eggs. Always as separate line, always same order of components. Have components as tags with slightly diff backgrounds, ideally to match representing emoji.small enouth font size to always take no more than one line
│ Oat flakes                  │  ← today's items: flat list, names only
| ...                         |
│ Bread                       │     (just confirms it was entered)
│ …                           │
│Lunch                      + |  ← empty slot is still shown
|...                          | 
└─────────────────────────────┘
```

#### Add food page
Opened on one of the slot + buttons press on Today page. 
That slot becomes context for Add food page, all lists are filtered as it was selected in slot dropdown on previous layout.
Difference with old layout:
- add primary/secondary color to tabs. Make selected one have color
- have list section fill whole screen except leave space for Add missing and grams input line in the bottom of a screen.
Layout (top → bottom):

```
┌─────────────────────────────┐
| ←                           |  ← back button to return to Today screen    
│ All | Recent | Top slot | … │  ← source tab strip (horizontally scrollable)
│ ┌─────────────────────────┐ │
│ │ Eggs                    │ │
│ │ Oat flakes              │ │  ← food list (full screen height, scrollable)
│ │ Bread                   │ │     tap to select; active item highlighted
│ │ Chicken                 │ │
│ │ Rice                    │ │
│ └─────────────────────────┘ │
│ [ + Add missing ]           │  ← opens new-food popup
│ [ grams ____ ]   [ Save ]   │  ← weight + submit
└─────────────────────────────┘
```


## Acceptance criteria
Today page:
- [x] Today page is opened first on load
- [x] Displays Kcal on top center, breakdown in grams to the right of it(smaller font size)
- [x] List of todays items has slots
- [x] Slot has + button aligned to right
- [x] Food items are one sublever to the right from slot name
- [x] Food item has new line with weight, Kcal and breakdown
- [x] On + press near any slot the Add food page is opened
Add food page:
- [x] Pages not modal, instead a full screen page, same as Today
- [x] has back button
- [x] tabs have colored fill(primary/secondary color)
- [x] lists are in context of slot for which page was opened
- [x] list is fills in vertical space, Add missing and gram input are always visible

## Scope / hints (optional)
n/a

## Notes / decisions

### Routing
No router library added. Simple `page` state variable in `App.svelte` switches between `'today'` and `'add'`. `activeMeal` prop is passed to `AddFoodPage`. Keeps zero dependencies.

### Component split
- `App.svelte` → Today page only (summary + slot-grouped entries + `+` buttons)
- `AddFoodPage.svelte` (new) → full-screen add flow. Dispatches `saved` (entry added, today refreshes silently) and `back` (navigate back + refresh).

### Summary macros layout
Used `flex justify-center items-center gap-4`: left block is the big kcal counter, right block is a stacked column of protein/fat/carbs in smaller text. Macros sourced directly from `api.todaySummary()` which already returns all four fields.

### Stat tags on food entries
Each entry row shows a second line of colored mini-tags (weight, ⚡kal, 💪protein, 🥑fat, 🌾carbs) using Tailwind background utilities (`bg-base-300`, `bg-amber-100`, `bg-blue-100`, `bg-green-100`, `bg-yellow-100`). Custom `.stat-tag` CSS class for shared padding/radius.

### Tab strip styling on Add food page
Replaced DaisyUI `tabs-bordered` with custom pill buttons (`rounded-full`). Active tab uses `bg-primary text-primary-content`, inactive uses `bg-base-200`. Simpler and visually clearer than DaisyUI tab variants.

### `h-dvh` on Add food page
Used `h-dvh` (dynamic viewport height) instead of `h-screen` so the bottom bar stays visible on mobile browsers with dynamic address bar.
