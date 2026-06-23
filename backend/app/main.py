from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import config, db
from .routers import entries, foods, suggestions


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Meal Tracker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")
api.include_router(foods.router)
api.include_router(entries.router)
api.include_router(suggestions.router)
app.include_router(api)


@app.get("/api/health")
def health():
    return {"ok": True}


# In production serve the built SPA; in dev this dir is absent and Vite serves it.
_dist = Path(config.FRONTEND_DIST)
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="static")
