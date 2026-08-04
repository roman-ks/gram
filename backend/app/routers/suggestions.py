import datetime
from typing import Optional

from fastapi import APIRouter, Depends

from ..db import db_dep
from ..schemas import Meal

router = APIRouter(tags=["suggestions"])


@router.get("/today/summary")
def today_summary(conn=Depends(db_dep)):
    today = datetime.date.today().isoformat()
    row = conn.execute(
        """SELECT COALESCE(SUM(calories), 0)     AS calories,
                  COALESCE(SUM(protein), 0)      AS protein,
                  COALESCE(SUM(carbohydrate), 0) AS carbohydrate,
                  COALESCE(SUM(fat), 0)          AS fat
           FROM entry WHERE consumed_date = ?""",
        (today,),
    ).fetchone()
    return {k: round(row[k], 1) for k in row.keys()}


@router.get("/suggestions/same-meal")
def same_meal(meal: Meal, days: int = 5, conn=Depends(db_dep)):
    """Distinct foods eaten at this meal over the previous `days` days (incl. today)."""
    today = datetime.date.today()
    start = (today - datetime.timedelta(days=days - 1)).isoformat()
    end = today.isoformat()
    # SQLite: with a single MAX(), bare columns come from the max row -> last amount.
    rows = conn.execute(
        """SELECT entry.food_id,
                  food.name              AS food_name,
                  MAX(entry.consumed_date) AS last_date,
                  entry.amount_grams     AS last_amount_grams
           FROM entry JOIN food ON food.id = entry.food_id
           WHERE entry.meal = ? AND entry.consumed_date BETWEEN ? AND ?
           GROUP BY entry.food_id
           ORDER BY last_date DESC""",
        (meal, start, end),
    ).fetchall()
    return [dict(r) for r in rows]


@router.get("/suggestions/popular")
def popular(meal: Optional[Meal] = None, limit: int = 10, conn=Depends(db_dep)):
    """Foods ranked by number of distinct days logged (optionally within a meal)."""
    where = "WHERE entry.meal = ?" if meal else ""
    params: list = [meal] if meal else []
    rows = conn.execute(
        f"""SELECT entry.food_id,
                   food.name                       AS food_name,
                   COUNT(DISTINCT entry.consumed_date) AS days,
                   MAX(entry.consumed_date)        AS last_date,
                   entry.amount_grams              AS last_amount_grams
            FROM entry JOIN food ON food.id = entry.food_id
            {where}
            GROUP BY entry.food_id
            ORDER BY days DESC, last_date DESC
            LIMIT ?""",
        params + [limit],
    ).fetchall()
    return [dict(r) for r in rows]
