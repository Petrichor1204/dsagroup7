# walmart_app/backend/db_helper.py
import sqlite3
import uuid
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "backend/database/walmart_lab3.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- Cart Management ---
def get_open_cart():
    """Return open cart ID or create one if none exists."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM carts WHERE status = 'open' LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]
        # Create a new open cart
        new_id = str(uuid.uuid4())
        cur.execute("INSERT INTO carts (id, status) VALUES (?, 'open')", (new_id,))
        conn.commit()
        return new_id

# --- Cart Items ---
def get_cart_items():
    cart_id = get_open_cart()
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, price, quantity FROM cart_items WHERE cart_id = ?",
            (cart_id,),
        )
        return [dict(row) for row in cur.fetchall()]

def add_item(name, price, quantity, tax_rate=0.1):
    cart_id = get_open_cart()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO cart_items (cart_id, name, price, quantity, tax_rate)
            VALUES (?, ?, ?, ?, ?)
            """,
            (cart_id, name, price, quantity, tax_rate),
        )
        conn.commit()

def update_item_qty(item_id, new_qty):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE cart_items SET quantity = ? WHERE id = ?",
            (new_qty, item_id),
        )
        conn.commit()

def remove_item(item_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM cart_items WHERE id = ?", (item_id,))
        conn.commit()

def clear_cart():
    cart_id = get_open_cart()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))
        conn.commit()
