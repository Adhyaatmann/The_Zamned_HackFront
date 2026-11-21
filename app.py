import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import CORS_ORIGINS
from routers import analysis

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(title="The Missing Rupee API")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=False,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(analysis.router)
# from routers import notifications        # <- teammates add their routers here
# app.include_router(notifications.router)

# Keep this LAST. Local only: on Vercel the CDN serves public/ itself.
PUBLIC_DIR = Path(__file__).parent / "public"
if PUBLIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")