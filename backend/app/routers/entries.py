import datetime

from fastapi import APIRouter, Depends, HTTPException

from ..db import NUTRIENTS, db_dep
from ..schemas import EntryIn

router = APIRouter(prefix="/entries", tags=["entries"])


def _snapshot(food_row, grams: float) -> dict:
    """Nutrition for the eaten amount: per-100g * grams / 100, rounded to 3dp."""
    factor = grams / 100.0
    out = {}
    for n in NUTRIENTS:
        v = food_row[n]
        out[n] = None if v is None else round(v * factor, 3)
    return out


def _entry_with_name(conn, entry_id: int) -> dict:
    row = conn.execute(
        """SELECT entry.*, food.name AS food_name
           FROM entry JOIN food ON food.id = entry.food_id
           WHERE entry.id = ?""",
        (entry_id,),
    ).fetchone()
    return dict(row)


@router.post("")
def add_entry(entry: EntryIn, conn=Depends(db_dep)):
    food = conn.execute("SELECT * FROM food WHERE id = ?", (entry.food_id,)).fetchone()
    if not food:
        raise HTTPException(404, "food not found")
    consumed = (entry.consumed_date or datetime.date.today()).isoformat()
    snap = _snapshot(food, entry.amount_grams)

    cols = ["food_id", "amount_grams", "meal", "consumed_date"] + NUTRIENTS
    vals = [entry.food_id, entry.amount_grams, entry.meal, consumed] + [snap[n] for n in NUTRIENTS]
    placeholders = ", ".join("?" * len(cols))
    cur = conn.execute(f"INSERT INTO entry ({', '.join(cols)}) VALUES ({placeholders})", vals)
    conn.commit()
    return _entry_with_name(conn, cur.lastrowid)


@router.get("/today")
def today_entries(conn=Depends(db_dep)):
    today = datetime.date.today().isoformat()
    rows = conn.execute(
        """SELECT entry.*, food.name AS food_name
           FROM entry JOIN food ON food.id = entry.food_id
           WHERE consumed_date = ?
           ORDER BY entry.id""",
        (today,),
    ).fetchall()
    return [dict(r) for r in rows]


@router.delete("/{entry_id}")
def delete_entry(entry_id: int, conn=Depends(db_dep)):
    conn.execute("DELETE FROM entry WHERE id = ?", (entry_id,))
    conn.commit()
    return {"ok": True}
