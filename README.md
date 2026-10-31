# The Missing Rupee 💸

> **Financial Discovery & Anti-Dark Patterns Engine**  
> Uncover recurring subscription commitments, detect sneaky price hikes and trial conversions, and take back control of your recurring debit mandates.

---

## Overview

Modern digital subscriptions frequently rely on obscure billing narratives and sneaky pricing escalations (dark patterns). **The Missing Rupee** is a desktop personal finance dashboard that extracts debitn history from a PostgreSQL/Supabase database[cite: 2, 3], passes cryptic transaction strings to Google Gemini to parse and identify repeating commitments[cite: 2], and delivers an actionable interface to track and cancel unwanted debits.

---

## Key Features

* **AI-Powered Descriptor Normalization**: Uses `gemini-3.8-flash` to clean cryptic bank descriptors (e.g., `ACH DEBIT PAYPAL *NETFLIX DIGI` to `Netflix`) and extract category, billing cadence, and latest transaction dates[cite: 2].
* **Anti-Dark Pattern & Anomaly Alerts**:
  * **Price Hikes**: Detects whenever a recurring charge quietly increases (e.g., `₹649 → ₹799 (+23%)`).
  * **Free-Trial Conversions**: Flags when a `₹0` trial converts into a paid recurring billing charge.
  * **New Recurring Debits**: Highlights newly started subscription mandates.
* **Indian Payment Mechanism Detection**: Categorizes debits by payment rail (UPI Autopay, Card recurring, e-Mandate)[cite: 2, 3].
* **Guided Cancellation Instructions**: Generates exact, merchant-specific step-by-step navigation instructions to cancel or turn off auto-renew[cite: 2, 3].
* **Financial Health Summary**: Aggregates recurring commitments to estimate overall monthly spend and annualized baseline cost.
* **Offline / Quota Fallback**: Features a built-in mock dataset to keep the desktop interface functional if database connectivity or LLM API calls fail.

---

## Tech Stack

## Tech Stack & Dependencies

* **Frontend / GUI**: `customtkinter` (modern desktop UI components), `Pillow` (image loading and asset rendering)
* **AI Analysis**: `google-genai` (Gemini API SDK for parsing bank statements)
* **Database & ORM**: `psycopg2-binary` (PostgreSQL client driver)
* **Configuration**: `python-dotenv` (management of local `.env` variables)

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
├── main.py                  # (renamed from trying everything with tkinter.py)
├── requirements.txt
└── README.md
```


## Database Requirements

This project requires a **PostgreSQL** database (such as Supabase or Neon).

## Schema Setup

Run the following SQL migration query in your database console before starting the application:

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_date DATE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('debit', 'credit'))
);

