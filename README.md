# The Missing Rupee 💸

> **Financial Discovery & Anti-Dark Patterns Engine**  
> Uncover recurring subscription commitments, detect sneaky price hikes and trial conversions, and take back control of your recurring debit mandates.

---

## Overview

Modern digital subscriptions frequently rely on obscure billing narratives and sneaky pricing escalations (dark patterns)[cite: 2]. **The Missing Rupee** is a desktop personal finance dashboard that extracts debit history from a PostgreSQL/Supabase database[cite: 2, 3], passes cryptic transaction strings to Google Gemini to parse and identify repeating commitments[cite: 2], and delivers an actionable interface to track and cancel unwanted debits[cite: 3].

---

## Key Features

- **AI-Powered Descriptor Normalization**: Uses `gemini-3.8-flash` to clean cryptic bank descriptors (e.g., `ACH DEBIT PAYPAL *NETFLIX DIGI` → `Netflix`) and extract category, billing cadence, and latest transaction dates[cite: 2].
- **Anti-Dark Pattern & Anomaly Alerts**:
  - **Price Hikes**: Detects whenever a recurring charge quietly increases (e.g., `₹649 → ₹799 (+23%)`)[cite: 3].
  - **Free-Trial Conversions**: Flags when a `₹0` trial converts into a paid recurring billing charge[cite: 3].
  - **New Recurring Debits**: Highlights newly started subscription mandates[cite: 3].
- **Indian Payment Mechanism Detection**: Categorizes debits by payment rail (UPI Autopay, Card recurring, e-Mandate)[cite: 2, 3].
- **Guided Cancellation Instructions**: Generates exact, merchant-specific step-by-step navigation instructions to cancel or turn off auto-renew[cite: 2, 3].
- **Financial Health Summary**: Aggregates recurring commitments to estimate overall monthly spend and annualized baseline cost[cite: 3].
- **Offline / Quota Fallback**: Features a built-in mock dataset to keep the desktop interface functional if database connectivity or LLM API calls fail[cite: 3].

---

## Tech Stack & Dependencies

- **Frontend / GUI**: `customtkinter`(modern desktop UI components), `Pillow` (image loading and asset rendering)[cite: 3]
- **AI Analysis**: `google-genai`(Gemini API SDK for parsing bank statements)[cite: 2]
- **Database & Driver**: `psycopg2-binary`(PostgreSQL client driver)[cite: 2, 3]
- **Configuration**: `python-dotenv`(management of local .env variables)[cite: 2, 3]

---

## Project Structure

```text
├── assets/
│   ├── App Logo.jpeg
│   ├── bell.png
│   ├── profile.png
│   └── settings.jpg
├── .env
├── gemini_analyzer.py
├── main.py
├── requirements.txt
└── README.md
```

---

## Database Setup

This project connects to a **PostgreSQL** database (such as Supabase)[cite: 1, 2]. 

Run this query in your SQL editor before running the application[cite: 2]:

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_date DATE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('debit', 'credit'))
);
```

---

## Getting Started & Installation

### 1. Prerequisites
- Python 3.10+
- Google Gemini API Key
- PostgreSQL / Supabase Database URL[cite: 1, 2]

---

### 2. Clone the Repository
```bash
git clone [https://github.com/](https://github.com/)<your-username>/the-missing-rupee.git
cd the-missing-rupee
```

---

### 3. Install Required Libraries
```bash
pip install customtkinter pillow psycopg2-binary python-dotenv google-genai os datetime
```

---

### 4. Add Your Keys (`.env`)
Create a file named `.env` in the root folder:

```ini
DATABASE_URL="postgresql://<username>:<password>@<host>:<port>/<dbname>"
GEMINI_API_KEY="your-gemini-api-key-here"
```

> **Note**: Ensure the image files (`App Logo.jpeg`, `bell.png`, `profile.png`, `settings.jpg`) are placed inside the `assets/` folder[cite: 3].

---

### 5. Run the App
```bash
python main.py
```
