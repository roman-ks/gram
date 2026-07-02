# 0008 — Recipes

> Status: **done** · Shipped: 2026-07-02 · Type: **feature** · Created: 2026-07-01

## Goal
Add ability to create composite meals from available individual ingredients and use it as a food item. 

## Context

### "Add missing" page change
- make it a normal page, not a modal one like currently is
- add two tabs on top of the page, similar to all/recent/top for "Add food" page. Tabs to be "meal" and "recipe"
- for "meal" tab use current layout of "Add missing" page

#### "Add missing" (recipe layout)
|-----------------|
| Meal  Recipe    | <- tabs(recipe is selected)
| Recipe name     | Text field for name
| Ingredients.  + | List header . + Button same as in Today page. Takes to "Add ingredient" page.
|  Rice      100g | list of food items and weight used in recipe
|  Vinegar     5g |
|...              |
|   cooked weight | text field to enter weight
| Save recipe     | Save button


#### "Add ingredient" page
Same as "Add food" except shows only All tab. ideally remove tabs at all, but think of worth reusing "Add food" or having totally separate page.


#### Db layout
- create separate table for recipe entries
- store recipe id, meal id and weights of each ingredient in the table
- store recipe as food item in food items table, with calc values for all nutritions per 100

Calc values as below (store second one, separate for calories, carbs,sugar, protein...)
```
total_nutrient = sum(ingredient_nutritient_per_100g * ingredient_g / 100)
meal_nutrient_per_100g= total_nutrient/cooked_weight * 100
```


#### Test data
||ingredient weight|proteins/g|fat/g|carbs/g|ccal/g|
|---|---|---|---|---|---|
|cheese|524|0.143|0.09|0.031|1.51|
|egg|110|0.12|0.1|0.008|1.55|
|flour|43|0.103|0.0011|0.705|3.31|
|||||||
|cheesecake(whole batch)|427|92.561|58.2073|47.439|1104.07|
|cheesecake(100g)|100|21.67704918|13.63168618|11.10983607|258.5644028|



## Acceptance criteria
- [x] Add cheese, egg and flour thu add missing meal flow. Use data from table above, but enter values in g/100g as table has them per g
- [x] Add new recipe of ingredients from test data above. Use 427g as cocked weight. Save with name "Cheesecake"
- [x] Start new Add meal flow. Confirm "Cheesecake" food item is available in All tab.
- [x] Add Cheesecake food item with weight 100g to todays list
- [x] Tags for Cheesecake item on todays page match values in last row in table above
- [x] New DB table contains list of ingredients for Cheesecake

## Scope / hints (optional)
- Affected areas: backend/app/db.py, backend/app/schemas.py, backend/app/main.py, backend/app/routers/recipes.py (new), frontend/src/lib/api.js, frontend/src/lib/i18n.js, frontend/src/lib/AddFoodPage.svelte, frontend/src/lib/NewFoodPage.svelte (new), frontend/src/lib/AddIngredientPage.svelte (new)

## Notes / decisions
- `NewFoodModal.svelte` replaced by full-page `NewFoodPage.svelte` with Meal/Recipe tabs; navigation is managed inline (showNewFood flag inside AddFoodPage, showIngredientPicker flag inside NewFoodPage) rather than lifting to App.svelte, keeping each component self-contained.
- `AddIngredientPage.svelte` is a separate component (not reusing AddFoodPage) to avoid complicating the existing save flow — it only needs food selection + grams, then dispatches `picked`.
- Optional nutrients (saturated_fat, sugar, fiber, salt) are included in recipe per-100g calculation with None treated as 0, matching how the existing entry snapshot works.
- `NewFoodModal.svelte` is now dead code (no longer imported); left in place, not deleted.
