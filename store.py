"""Where the app gets its commitments from. One function everyone should call:

    from store import get_commitments
    items = get_commitments()            # cached, never raises
    items = get_commitments(refresh=True)  # re-run Gemini on the live DB

Order of preference: fresh Gemini result > cache.json from an earlier run > sample_data.json.
If a refresh fails, the previous data keeps being served (the demo never breaks).

Extension point for notifications etc.:
    from store import on_update
    on_update(lambda commitments: ...)   # called every time Gemini produces fresh data
"""
import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path

from gemini_analyzer import get_commitments_from_gemini

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
CACHE_FILE = BASE_DIR / "cache.json"
SAMPLE_FILE = BASE_DIR / "sample_data.json"

_lock = threading.RLock()  # RLock: a listener may call get_commitments() without deadlocking
_state = {"data": None, "source": None, "updated_at": None}
_listeners = []


def on_update(callback):
    """Register callback(commitments) to run whenever fresh data arrives from Gemini."""
    _listeners.append(callback)


def _set(data, source):
    _state.update(data=data, source=source, updated_at=datetime.now(timezone.utc).isoformat())


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _try_gemini():
    """Run Gemini. On success store + cache + notify listeners. Returns True on success."""
    try:
        fresh = get_commitments_from_gemini()
    except Exception as exc:  # DB down, quota, bad key, ... -> keep serving old data
        log.error("Gemini/DB refresh failed: %s", exc)
        return False
    if not fresh:
        return False

    _set(fresh, "gemini")
    CACHE_FILE.write_text(json.dumps(fresh, ensure_ascii=False), encoding="utf-8")
    for callback in _listeners:
        try:
            callback(fresh)
        except Exception:
            log.exception("on_update listener failed")
    return True


def get_commitments(refresh=False):
    with _lock:
        if refresh:
            _try_gemini()
        if _state["data"] is None:
            if CACHE_FILE.exists():
                _set(_read_json(CACHE_FILE), "cache")
            elif not _try_gemini():
                _set(_read_json(SAMPLE_FILE), "sample")
        return _state["data"]


def get_status():
    """Where the current data came from: 'gemini' | 'cache' | 'sample', and when."""
    return {"source": _state["source"], "updated_at": _state["updated_at"]}
