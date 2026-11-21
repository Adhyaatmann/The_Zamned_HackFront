import os, psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv
load_dotenv()

@contextmanager
def get_conn():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), connect_timeout=5)
    try:
        yield conn
    finally:
        conn.close()

def fetch_debits():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, transaction_date::text, description, amount::float
            FROM transactions
            WHERE LOWER(transaction_type) = 'debit'
            ORDER BY transaction_date ASC
        """)
        return [{"id": r[0], "date": r[1][:10], "description": r[2], "amount": r[3]}
                for r in cur.fetchall()]