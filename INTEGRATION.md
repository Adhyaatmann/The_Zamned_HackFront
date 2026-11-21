# Integration guide (for teammates)

## File ownership: to avoid merge conflicts, add files, don't edit shared ones

| File | What it is | Edit it? |
|---|---|---|
| `config.py` | env settings | Add your own settings at the bottom |
| `db.py` | DB connection + `fetch_debits()` | Add new query functions at the bottom |
| `gemini_analyzer.py` | Gemini grouping | Only its owner |
| `core.py` | pure logic: metrics, alerts, `format_inr` | Only add new functions |
| `store.py` | cached commitments, `on_update` hook | Don't edit, just import |
| `routers/analysis.py` | dashboard endpoints | Only its owner |
| `app.py` | registers routers | One line per feature (see below) |
| `routers/<yourfeature>.py` | **your feature** | Yours |

## Add a feature in 3 steps (example: notifications)

1. Create `routers/notifications.py`:
   ```python
   from fastapi import APIRouter
   from core import build_alerts
   from store import get_commitments, on_update

   router = APIRouter(prefix="/api/notifications", tags=["notifications"])

   @router.get("")
   def list_notifications():
       return build_alerts(get_commitments())   # each alert has a stable "id" for de-duplication

   on_update(lambda commitments: print("fresh data, check for new alerts"))  # optional hook
   ```
2. In `app.py` add two lines under the router section:
   ```python
   from routers import notifications
   app.include_router(notifications.router)
   ```
3. Run `uvicorn app:app --reload` and test at `/docs`.

## Data contract

**Commitment** (`GET /api/commitments`)
```json
{
  "id": "netflix", "name": "Netflix", "frequency": "monthly | annual | quarterly | bi-weekly",
  "category": "Entertainment", "amount": 799, "date": "2025-08-15",
  "initial": "N", "bg": "#FEE2E2", "payment_mechanism": "Card recurring",
  "cancellation_steps": ["..."],
  "history": [{"date": "2025-07-15", "description": "ACH DEBIT PAYPAL *NETFLIX", "amount": 799}]
}
```
`amount` is always a **number in rupees**. Format it with `format_inr()` in Python or
`Intl.NumberFormat('en-IN', {style:'currency', currency:'INR', maximumFractionDigits:0})` in JS.

**Alert** (`GET /api/alerts`): newest first
```json
{
  "id": "price_hike:netflix:2025-07-15", "type": "price_hike | trial_converted | new | frequency_increased",
  "commitment_id": "netflix", "merchant": "Netflix", "date": "2025-07-15",
  "message": "Netflix raised its price from ₹649 to ₹799 (+23%)."
}
```
Plus type-specific numbers (`old_amount`, `new_amount`, `pct`, `frequency`).

**Everything at once:** `GET /api/analysis[?refresh=true]` returns
`{commitments, metrics: {monthly, annual, active, merchants}, alerts, meta: {source, updated_at}}`.
`meta.source` is `gemini` (fresh), `cache` (earlier run) or `sample` (fallback data).

## Rules of thumb
- Get data through `store.get_commitments()`. Never call Gemini or open your own DB connection for dashboard data.
- Never put secrets in code: add them to `.env` and read them in `config.py`.
- Use plain `def` endpoints (not `async def`) if your code blocks (DB, email, HTTP calls).
