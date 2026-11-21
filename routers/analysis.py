"""Dashboard API. Endpoints are plain `def` (not async) so FastAPI runs them in a worker thread,
which means the slow Gemini call never freezes other requests."""
from fastapi import APIRouter

from core import build_alerts, dashboard_metrics
from store import get_commitments, get_status

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/health")
def health():
    return {"ok": True}


@router.get("/analysis")
def analysis(refresh: bool = False):
    """Everything the frontend needs in one call. ?refresh=true re-runs Gemini."""
    commitments = get_commitments(refresh)
    return {
        "commitments": commitments,
        "metrics": dashboard_metrics(commitments),
        "alerts": build_alerts(commitments),
        "meta": get_status(),
    }


@router.get("/commitments")
def commitments():
    return get_commitments()


@router.get("/alerts")
def alerts():
    return build_alerts(get_commitments())
