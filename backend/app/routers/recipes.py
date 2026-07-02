from fastapi import APIRouter, Depends, HTTPException

from ..db import NUTRIENTS, db_dep
from ..schemas import RecipeIn

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("")
def create_recipe(recipe: RecipeIn, conn=Depends(db_dep)):
    # Fetch nutrition for every ingredient
    ingredient_rows = []
    for ing in recipe.ingredients:
        food = conn.execute("SELECT * FROM food WHERE id = ?", (ing.food_id,)).fetchone()
        if not food:
            raise HTTPException(404, f"food {ing.food_id} not found")
        ingredient_rows.append((food, ing.grams))

    # Sum total nutrients, then scale to per-100g of cooked weight
    totals = {n: 0.0 for n in NUTRIENTS}
    for food_row, grams in ingredient_rows:
        for n in NUTRIENTS:
            v = food_row[n]
            totals[n] += (v or 0.0) * grams / 100.0

    per_100g = {n: totals[n] / recipe.cooked_weight * 100.0 for n in NUTRIENTS}

    # Insert food row for the recipe
    required = ["calories", "protein", "carbohydrate", "fat"]
    optional = ["saturated_fat", "sugar", "fiber", "salt"]
    cols = ["name"] + required + optional
    vals = [recipe.name] + [per_100g[n] for n in required] + [per_100g[n] for n in optional]
    placeholders = ", ".join("?" * len(cols))
    cur = conn.execute(f"INSERT INTO food ({', '.join(cols)}) VALUES ({placeholders})", vals)
    food_id = cur.lastrowid

    # Insert recipe row
    cur2 = conn.execute("INSERT INTO recipe (food_id) VALUES (?)", (food_id,))
    recipe_id = cur2.lastrowid

    # Insert ingredients
    for food_row, grams in ingredient_rows:
        conn.execute(
            "INSERT INTO recipe_ingredient (recipe_id, food_id, grams) VALUES (?, ?, ?)",
            (recipe_id, food_row["id"], grams),
        )

    conn.commit()
    row = conn.execute("SELECT * FROM food WHERE id = ?", (food_id,)).fetchone()
    return dict(row)
