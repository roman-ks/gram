import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

Meal = Literal["breakfast", "lunch", "dinner", "snack"]


class FoodIn(BaseModel):
    name: str = Field(min_length=1)
    calories: float
    protein: float
    carbohydrate: float
    fat: float
    saturated_fat: Optional[float] = None
    sugar: Optional[float] = None
    fiber: Optional[float] = None
    salt: Optional[float] = None


class IngredientIn(BaseModel):
    food_id: int
    grams: float = Field(gt=0)


class RecipeIn(BaseModel):
    name: str = Field(min_length=1)
    cooked_weight: float = Field(gt=0)
    ingredients: list[IngredientIn] = Field(min_length=1)


class EntryIn(BaseModel):
    food_id: int
    amount_grams: float = Field(gt=0)
    meal: Meal
    consumed_date: Optional[datetime.date] = None
