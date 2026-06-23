import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/

# SQLite file. Override with MEAL_DB (e.g. /data/meals.db in Docker).
DB_PATH = os.environ.get("MEAL_DB", str(BASE_DIR / "meals.db"))

# Built SPA to serve in production. In dev this won't exist and Vite serves the UI.
FRONTEND_DIST = os.environ.get("FRONTEND_DIST", str(BASE_DIR.parent / "frontend" / "dist"))

# CORS — wide open for now (no auth yet). Tighten when Authentik lands. Capacitor-ready.
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
