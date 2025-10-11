# walmart_app/backend/db_helper.py
import sqlite3
import uuid
from pathlib import Path
from walmart_app.config import *
import datetime
import uuid
from datetime import datetime
# from walmart_app.backend.db_connection import get_connection




DB_PATH = Path(__file__).resolve().parents[1] / "backend/database/walmart_lab3.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- Cart Management ---
def get_open_cart():
    """Return open cart ID or create one if none exists."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM carts LIMIT 1")
        # cur.execute("SELECT id FROM carts WHERE status = 'open' LIMIT 1")
        row = cur.fetchone()
        print(f"Captured Cart ID: {row}")
        if row:
            return row[0]
        # Create a new open cart
        new_id = str(uuid.uuid4())
        new_id = CART_ID
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

# --- Checkout / Transactions ---
def checkout_cart():
    """Move open cart to transactions and clear it."""
    cart_id = get_open_cart()

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get all cart items
        cur.execute("SELECT * FROM cart_items WHERE cart_id = ?", (cart_id,))
        items = cur.fetchall()
        if not items:
            return None  # nothing to checkout

        # Calculate totals
        subtotal = sum(row["price"] * row["quantity"] for row in items)
        tax_total = sum((row["price"] * row["quantity"]) * row["tax_rate"] for row in items)
        grand_total = subtotal + tax_total

        # Create transaction
        tx_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO transactions (id, cart_id, created_at, subtotal, tax_total, grand_total)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                tx_id,
                cart_id,
                datetime.now().isoformat(timespec="seconds"),
                subtotal,
                tax_total,
                grand_total,
            ),
        )

        # Insert transaction items
        for row in items:
            line_total = (row["price"] * row["quantity"]) + (
                row["price"] * row["quantity"] * row["tax_rate"]
            )
            cur.execute(
                """
                INSERT INTO transaction_items
                    (transaction_id, name, unit_price, quantity, tax_amount, line_total)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    tx_id,
                    row["name"],
                    row["price"],
                    row["quantity"],
                    (row["price"] * row["quantity"]) * row["tax_rate"],
                    line_total,
                ),
            )

        # Close cart
        cur.execute("UPDATE carts SET status = 'checked_out' WHERE id = ?", (cart_id,))
        conn.commit()

        return {
            "transaction_id": tx_id,
            "subtotal": subtotal,
            "tax_total": tax_total,
            "grand_total": grand_total,
            "items": [dict(row) for row in items],
        }

def get_transactions():
    """Fetch all past transactions (most recent first)."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions ORDER BY created_at DESC")
        return [dict(row) for row in cur.fetchall()]

def get_transaction_items(transaction_id):
    """Fetch items belonging to a specific transaction."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, name, unit_price, quantity, tax_amount, line_total
            FROM transaction_items
            WHERE transaction_id = ?
            """,
            (transaction_id,),
        )
        return [dict(row) for row in cur.fetchall()]

def complete_checkout(items, subtotal, tax_total, grand_total):
    """
    Finalize checkout:
      - Create a transaction record
      - Copy items into transaction_items
      - Mark cart as checked_out
      - Clear cart_items
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get current open cart
        cur.execute("SELECT id FROM carts WHERE status = 'open' LIMIT 1")
        cart_row = cur.fetchone()
        if not cart_row:
            raise Exception("No open cart found.")
        cart_id = cart_row[0]

        # Create transaction
        tx_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        cur.execute(
            """
            INSERT INTO transactions (id, cart_id, created_at, subtotal, tax_total, grand_total)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (tx_id, cart_id, now, subtotal, tax_total, grand_total),
        )

        # Copy items into transaction_items
        for item in items:
            name = item["name"]
            price = float(item["price"])
            qty = int(item["quantity"])
            tax_rate = float(item.get("tax_rate", 0.1))
            tax_amount = price * qty * tax_rate
            line_total = price * qty + tax_amount

            cur.execute(
                """
                INSERT INTO transaction_items (transaction_id, name, unit_price, quantity, tax_amount, line_total)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (tx_id, name, price, qty, tax_amount, line_total),
            )

        # Mark cart as checked_out
        cur.execute("UPDATE carts SET status = 'checked_out' WHERE id = ?", (cart_id,))

        # Clear cart items
        cur.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))

        # Create a new empty cart for next session
        new_cart_id = str(uuid.uuid4())
        cur.execute("INSERT INTO carts (id, created_at, status) VALUES (?, ?, 'open')", (new_cart_id, now))

        conn.commit()
        return tx_id

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
