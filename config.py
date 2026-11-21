"""Single place for settings. Import values from here instead of calling os.getenv elsewhere.

load_dotenv() runs BEFORE any os.getenv, so values from .env are always picked up.
Teammates: add your own settings here (e.g. SMTP_HOST, VAPID keys) and import them.
"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Comma-separated list of origins allowed to call the API from a browser.
# "*" is fine for a hackathon; set it to your real frontend URL later.
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
