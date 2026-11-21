"""App entry point.  Run locally:  uvicorn app:app --reload
Interactive API docs (free test UI):  http://127.0.0.1:8000/docs
"""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from config import CORS_ORIGINS
from routers import analysis

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(title="The Missing Rupee API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Routers: one file per feature in routers/. To add yours: import it and include it. ----
app.include_router(analysis.router)
# from routers import notifications      # <- teammate example
# app.include_router(notifications.router)

# ---- Frontend (static/index.html), served if it exists ----
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    page = STATIC_DIR / "index.html"
    return FileResponse(page) if page.exists() else RedirectResponse("/docs")
