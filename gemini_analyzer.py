import json
import os
import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

BG_COLOR_MAP = {
    "A": "#DCFCE7",
    "C": "#E0F2FE",
    "G": "#DCFCE7",
    "H": "#E0F2FE",
    "L": "#DCFCE7",
    "N": "#FEE2E2",
    "O": "#E0F2FE",
    "S": "#DCFCE7",
    "Y": "#FEE2E2",
}


def fetch_raw_transactions_from_db():
    """Queries raw debit transactions from Supabase sorted by date ascending."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            transaction_date::text, 
            description, 
            amount::float
        FROM transactions 
        WHERE transaction_type = 'debit'
        ORDER BY transaction_date ASC;
    """
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {"date": r[0][:10], "description": r[1], "amount": r[2]} for r in rows
    ]


def get_commitments_from_gemini():
    """Passes raw statement lines to Gemini AI to clean descriptors, detect recurring subscriptions, compile transaction history, and generate merchant-specific cancellation steps."""
    raw_txs = fetch_raw_transactions_from_db()

    if not raw_txs:
        return []

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are a financial AI analyzing raw bank transaction records to detect recurring subscription commitments and dark patterns (e.g., hidden price hikes or sneaky free trial conversions).

RAW BANK TRANSACTIONS:
{json.dumps(raw_txs, indent=2)}

TASK:
1. Parse the cryptic descriptions (e.g. 'ACH DEBIT PAYPAL *NETFLIX DIGI' -> 'Netflix').
2. Identify repeating subscription patterns and charges.
3. Detect price escalations or sneaky trial conversions.
4. Categorize each commitment into one of: ['Shopping', 'Education', 'Entertainment', 'Health', 'Insurance', 'Productivity', 'Utilities'].
5. Determine frequency: 'monthly', 'annual', or 'quarterly'.
6. Extract the latest transaction date ('YYYY-MM-DD').
7. Format amount as Indian Rupees (e.g. '₹649', '₹1,499', '₹3,999').
8. Aggregate ALL matching historical transaction instances into a `history` array sorted chronologically.
9. Provide 3-4 exact, accurate, step-by-step instructions in `cancellation_steps` on how a user can cancel/turn off auto-renew for this specific merchant in India (e.g., website/app navigation paths).
10. Identify `payment_mechanism` (e.g., 'UPI Autopay', 'Card recurring', 'e-Mandate').

Return a JSON array of objects matching this exact format per commitment:
[
  {{
    "name": "Netflix",
    "frequency": "monthly",
    "category": "Entertainment",
    "amount": "₹799",
    "date": "2025-08-15",
    "initial": "N",
    "payment_mechanism": "Card recurring",
    "cancellation_steps": [
      "Sign in to Netflix.com in a web browser.",
      "Click your profile icon at the top right and open 'Account'.",
      "Under 'Membership & Billing', click 'Cancel Membership'.",
      "Confirm cancellation on the next screen to stop future charges."
    ],
    "history": [
      {{ "date": "2025-03-15", "description": "ACH DEBIT PAYPAL *NETFLIX", "amount": "₹649" }},
      {{ "date": "2025-08-15", "description": "ACH DEBIT PAYPAL *NETFLIX", "amount": "₹799" }}
    ]
  }}
]
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    try:
        parsed_data = json.loads(response.text)

        # Inject badge background colors for UI
        for item in parsed_data:
            first_char = item.get("initial", item["name"][0]).upper()
            item["initial"] = first_char
            item["bg"] = BG_COLOR_MAP.get(first_char, "#F1F5F9")

        return parsed_data
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return []