from fastapi import APIRouter, Depends

from ..db import NUTRIENTS, db_dep
from ..schemas import FoodIn

router = APIRouter(prefix="/foods", tags=["foods"])


@router.post("")
def add_food(food: FoodIn, conn=Depends(db_dep)):
    cols = ["name"] + NUTRIENTS
    vals = [food.name] + [getattr(food, n) for n in NUTRIENTS]
    placeholders = ", ".join("?" * len(cols))
    cur = conn.execute(f"INSERT INTO food ({', '.join(cols)}) VALUES ({placeholders})", vals)
    conn.commit()
    row = conn.execute("SELECT * FROM food WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


@router.get("")
def list_foods(q: str = "", limit: int = 20, conn=Depends(db_dep)):
    rows = conn.execute(
        "SELECT * FROM food WHERE name LIKE ? ORDER BY name LIMIT ?",
        (f"%{q}%", limit),
    ).fetchall()
    return [dict(r) for r in rows]
