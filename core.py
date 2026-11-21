"""Pure business logic (no database, no Gemini, no web framework).

Anyone can import these: the API, a notifications module, a PDF report, tests.
    from core import dashboard_metrics, build_alerts, format_inr
"""
from datetime import date
from statistics import median

# How many times per year each billing frequency is charged.
PER_YEAR = {"monthly": 12, "quarterly": 4, "annual": 1, "bi-weekly": 26}

# Ignore price changes smaller than this many percent (usage-based bills wobble).
MIN_PRICE_HIKE_PCT = 5


def format_inr(amount):
    """1499 -> '₹1,499', 149999 -> '₹1,49,999' (Indian digit grouping)."""
    n = round(amount)
    digits = str(abs(n))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        digits = ",".join(parts + [tail])
    return f"{'-' if n < 0 else ''}₹{digits}"


def dashboard_metrics(commitments):
    annual = sum(c["amount"] * PER_YEAR.get(c["frequency"], 12) for c in commitments)
    return {
        "monthly": round(annual / 12),
        "annual": round(annual),
        "active": len(commitments),
        "merchants": len({c["name"] for c in commitments}),
    }


def frequency_increased(history):
    """True if the recent gap between payments is much shorter than the earlier gaps."""
    days = [date.fromisoformat(h["date"]) for h in history]
    if len(days) < 4:
        return False
    gaps = [(b - a).days for a, b in zip(days, days[1:])]
    return median(gaps[-2:]) < 0.6 * median(gaps[:-2])


def _alert(kind, c, when, message, **extra):
    return {
        "id": f"{kind}:{c['id']}:{when}",  # stable -> notifications can de-duplicate on it
        "type": kind,
        "commitment_id": c["id"],
        "merchant": c["name"],
        "date": when,
        "message": message,
        **extra,
    }


def build_alerts(commitments):
    """Price hikes, free-trial conversions, new recurring payments, billing-frequency increases.

    Returns newest first. Alert types: price_hike | trial_converted | new | frequency_increased
    """
    alerts = []
    for c in commitments:
        history = c.get("history", [])
        name = c["name"]

        for prev, cur in zip(history, history[1:]):
            if prev["amount"] > 0 and cur["amount"] > prev["amount"]:
                pct = round((cur["amount"] - prev["amount"]) / prev["amount"] * 100)
                if pct >= MIN_PRICE_HIKE_PCT:
                    alerts.append(_alert(
                        "price_hike", c, cur["date"],
                        f"{name} raised its price from {format_inr(prev['amount'])} "
                        f"to {format_inr(cur['amount'])} (+{pct}%).",
                        old_amount=prev["amount"], new_amount=cur["amount"], pct=pct,
                    ))
            elif prev["amount"] == 0 and cur["amount"] > 0:
                alerts.append(_alert(
                    "trial_converted", c, cur["date"],
                    f"The free trial for {name} converted into a paid {format_inr(cur['amount'])} charge.",
                    new_amount=cur["amount"],
                ))

        if len(history) == 1:
            alerts.append(_alert(
                "new", c, history[0]["date"],
                f"New recurring payment detected: {name} ({format_inr(history[0]['amount'])}).",
                new_amount=history[0]["amount"],
            ))

        if frequency_increased(history):
            alerts.append(_alert(
                "frequency_increased", c, history[-1]["date"],
                f"{name} is now billed more often ({c['frequency']}).",
                frequency=c["frequency"],
            ))

    return sorted(alerts, key=lambda a: a["date"], reverse=True)
