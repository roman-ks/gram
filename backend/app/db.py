import sqlite3

from . import config

# Nutrition fields (per 100 g on food; computed snapshot on entry). See DESIGN.md §8.
REQUIRED_NUTRIENTS = ["calories", "protein", "carbohydrate", "fat"]
OPTIONAL_NUTRIENTS = ["saturated_fat", "sugar", "fiber", "salt"]
NUTRIENTS = REQUIRED_NUTRIENTS + OPTIONAL_NUTRIENTS

SCHEMA = """
CREATE TABLE IF NOT EXISTS food (
  id            INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,
  calories      REAL NOT NULL,
  protein       REAL NOT NULL,
  carbohydrate  REAL NOT NULL,
  fat           REAL NOT NULL,
  saturated_fat REAL,
  sugar         REAL,
  fiber         REAL,
  salt          REAL,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS entry (
  id            INTEGER PRIMARY KEY,
  food_id       INTEGER NOT NULL REFERENCES food(id),
  amount_grams  REAL NOT NULL,
  meal          TEXT NOT NULL CHECK (meal IN ('breakfast','lunch','dinner','snack')),
  consumed_date TEXT NOT NULL,
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  calories      REAL NOT NULL,
  protein       REAL NOT NULL,
  carbohydrate  REAL NOT NULL,
  fat           REAL NOT NULL,
  saturated_fat REAL,
  sugar         REAL,
  fiber         REAL,
  salt          REAL
);

CREATE INDEX IF NOT EXISTS idx_entry_date      ON entry(consumed_date);
CREATE INDEX IF NOT EXISTS idx_entry_meal_date ON entry(meal, consumed_date);
CREATE INDEX IF NOT EXISTS idx_entry_food      ON entry(food_id);
"""


def get_conn() -> sqlite3.Connection:
    # check_same_thread=False: FastAPI runs sync deps/handlers across threadpool
    # threads, so the open/use/close of one request's connection may hop threads.
    # Safe because each request gets its own connection (never shared concurrently).
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def db_dep():
    """FastAPI dependency: one connection per request."""
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()
