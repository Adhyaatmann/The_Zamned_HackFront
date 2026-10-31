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
    "A": "#DCFCE7", "C": "#E0F2FE", "D": "#FEF3C7", "G": "#DCFCE7",
    "H": "#E0F2FE", "L": "#DCFCE7", "N": "#FEE2E2", "O": "#E0F2FE",
    "S": "#DCFCE7", "Y": "#FEE2E2", "Z": "#FEF3C7",
}


def fetch_raw_transactions_from_db():
    """Queries raw debit transactions from Supabase."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            transaction_date::text, 
            description, 
            amount::float
        FROM transactions 
        WHERE LOWER(transaction_type) = 'debit'
        ORDER BY transaction_date ASC;
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    tx_list = [{"date": r[0][:10], "description": r[1], "amount": r[2]} for r in rows]
    print(f"DEBUG: Pulled {len(tx_list)} raw debit rows from Supabase.")
    return tx_list


def get_commitments_from_gemini():
    raw_txs = fetch_raw_transactions_from_db()

    if not raw_txs:
        print("DEBUG: No transactions found in database table 'transactions'.")
        return []

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are a financial AI analyzing raw bank transaction records to detect recurring subscription commitments and dark patterns.

RAW BANK TRANSACTIONS:
{json.dumps(raw_txs, indent=2)}

TASK:
1. Clean cryptic descriptions into recognizable merchant names (e.g. 'POS DEBIT DUOLINGO BIWEEKLY' -> 'Duolingo', 'POS DEBIT AWS SERVICES SEATTLE WA' -> 'AWS Cloud').
2. Group repeating charges (even with irregular dates or variable usage amounts).
3. Categorize into one of: ['Shopping', 'Education', 'Entertainment', 'Health', 'Insurance', 'Productivity', 'Utilities'].
4. Determine frequency: 'monthly', 'annual', 'quarterly', or 'bi-weekly'.
5. Format amount as Indian Rupees (e.g. '₹149', '₹1,499').
6. Provide exact step-by-step cancellation instructions in `cancellation_steps`.
7. Extract all matching payment records into `history` sorted chronologically.

Return a JSON array of objects matching this exact structure:
[
  {{
    "name": "Duolingo",
    "frequency": "bi-weekly",
    "category": "Education",
    "amount": "₹149",
    "date": "2025-08-26",
    "initial": "D",
    "payment_mechanism": "Card recurring",
    "cancellation_steps": [
      "Open the Duolingo app on your device.",
      "Tap the Profile tab and select Settings (gear icon).",
      "Scroll to Subscription and tap Manage Subscription.",
      "Select Cancel Subscription and confirm."
    ],
    "history": [
      {{ "date": "2025-07-01", "description": "POS DEBIT DUOLINGO BIWEEKLY", "amount": "₹149" }},
      {{ "date": "2025-07-15", "description": "POS DEBIT DUOLINGO BIWEEKLY", "amount": "₹149" }},
      {{ "date": "2025-07-29", "description": "POS DEBIT DUOLINGO BIWEEKLY", "amount": "₹149" }},
      {{ "date": "2025-08-12", "description": "POS DEBIT DUOLINGO BIWEEKLY", "amount": "₹149" }},
      {{ "date": "2025-08-26", "description": "POS DEBIT DUOLINGO BIWEEKLY", "amount": "₹149" }}
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
        print(f"DEBUG: Gemini successfully parsed {len(parsed_data)} recurring commitments.")

        for item in parsed_data:
            first_char = item.get("initial", item["name"][0]).upper()
            item["initial"] = first_char
            item["bg"] = BG_COLOR_MAP.get(first_char, "#F1F5F9")

        return parsed_data
    except Exception as e:
        print(f"DEBUG Error parsing Gemini response: {e}")
        print("Raw Response was:", response.text)
        return []
