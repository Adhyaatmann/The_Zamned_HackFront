"""Turns raw bank debits into recurring "commitments" using Gemini.

Key idea: Gemini only GROUPS transactions (it returns transaction ids). We build the payment
history ourselves from the real database rows, so amounts and dates can never be invented.

Public function:  get_commitments_from_gemini() -> list[dict]
Commitment shape (see README "Data contract"):
    id, name, frequency, category, amount (number), date, initial, bg,
    payment_mechanism, cancellation_steps[], history[{date, description, amount}]
"""
import json
import logging
import re

from google import genai
from google.genai import errors, types
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from config import GEMINI_API_KEY, GEMINI_MODEL
from db import fetch_debits

log = logging.getLogger(__name__)

CATEGORIES = ["Shopping", "Education", "Entertainment", "Health", "Insurance", "Productivity", "Utilities"]
FREQUENCIES = ["monthly", "annual", "quarterly", "bi-weekly"]

BG_COLOR_MAP = {
    "A": "#DCFCE7", "C": "#E0F2FE", "D": "#FEF3C7", "G": "#DCFCE7",
    "H": "#E0F2FE", "L": "#DCFCE7", "N": "#FEE2E2", "O": "#E0F2FE",
    "S": "#DCFCE7", "Y": "#FEE2E2", "Z": "#FEF3C7",
}
DEFAULT_BG = "#F1F5F9"

PROMPT = """You analyze raw bank debit records to find recurring subscription commitments.

TRANSACTIONS (JSON list of {id, date, description, amount in INR}):
__TRANSACTIONS__

Find every recurring subscription (also clear annual plans that appear only once).
Return ONLY a JSON array. Each element must have exactly these keys:
- "name": clean merchant name (e.g. 'POS DEBIT AWS SERVICES SEATTLE WA' -> 'AWS Cloud')
- "frequency": one of __FREQUENCIES__
- "category": one of __CATEGORIES__
- "payment_mechanism": e.g. 'Card recurring', 'UPI Autopay', 'e-Mandate'
- "cancellation_steps": array of short, merchant-specific steps to cancel or turn off auto-renew
- "transaction_ids": array with the id of EVERY transaction above that belongs to this subscription

Rules: use only ids that appear above. Never invent transactions. Skip one-off purchases."""


# ---------------------------------------------------------------- Gemini call (with retries)
def _is_retryable(exc):
    """Retry only when waiting can help: Google server errors and rate limits (429)."""
    return isinstance(exc, errors.ServerError) or (
        isinstance(exc, errors.APIError) and exc.code == 429
    )


@retry(
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _call_gemini(client, prompt):
    return client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )


# ---------------------------------------------------------------- turning Gemini output into commitments
def _slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "merchant"


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_commitments(llm_items, txs):
    """Combine Gemini's grouping with the real transaction rows. Pure function (easy to test)."""
    by_id = {t["id"]: t for t in txs}
    used_slugs = set()
    commitments = []

    for item in llm_items:
        if not isinstance(item, dict) or not item.get("name"):
            continue

        raw_ids = item.get("transaction_ids") or []
        ids = {i for i in map(_to_int, raw_ids) if i in by_id}
        if not ids:  # Gemini invented a merchant with no real transactions -> drop it
            continue

        history = sorted((by_id[i] for i in ids), key=lambda t: t["date"])
        name = str(item["name"]).strip()
        initial = name[0].upper()

        slug = base = _slug(name)
        n = 2
        while slug in used_slugs:
            slug = f"{base}-{n}"
            n += 1
        used_slugs.add(slug)

        frequency = item.get("frequency")
        category = item.get("category")
        commitments.append({
            "id": slug,
            "name": name,
            "frequency": frequency if frequency in FREQUENCIES else "monthly",
            "category": category if category in CATEGORIES else "Utilities",
            "amount": history[-1]["amount"],
            "date": history[-1]["date"],
            "initial": initial,
            "bg": BG_COLOR_MAP.get(initial, DEFAULT_BG),
            "payment_mechanism": item.get("payment_mechanism") or "",
            "cancellation_steps": [str(s) for s in (item.get("cancellation_steps") or [])],
            "history": [
                {"date": h["date"], "description": h["description"], "amount": h["amount"]}
                for h in history
            ],
        })
    return commitments


# ---------------------------------------------------------------- public entry point
def get_commitments_from_gemini():
    """DB -> Gemini -> list of commitments. Raises on DB/API failure; returns [] if nothing found."""
    txs = fetch_debits()
    if not txs:
        log.warning("No debit transactions found in the 'transactions' table.")
        return []

    prompt = (
        PROMPT.replace("__TRANSACTIONS__", json.dumps(txs, ensure_ascii=False, separators=(",", ":")))
        .replace("__FREQUENCIES__", json.dumps(FREQUENCIES))
        .replace("__CATEGORIES__", json.dumps(CATEGORIES))
    )

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = _call_gemini(client, prompt)

    try:
        llm_items = json.loads(response.text)
    except (json.JSONDecodeError, TypeError):
        log.error("Gemini returned invalid JSON: %s", (response.text or "")[:500])
        return []

    if isinstance(llm_items, dict):  # model wrapped the list in an object
        llm_items = next((v for v in llm_items.values() if isinstance(v, list)), [])

    commitments = build_commitments(llm_items, txs)
    log.info("Gemini found %d recurring commitments from %d debits.", len(commitments), len(txs))
    return commitments
