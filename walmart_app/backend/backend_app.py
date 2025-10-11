
from flask import Flask, request, jsonify, abort
import sqlite3, uuid, datetime, math

DEFAULT_TAX_RATE = 0.1044

DB_PATH = "walmart_app/backend/database/walmart_lab3.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn, open("walmart_app/backend/database/schema.sql", "r") as f:
        conn.executescript(f.read())

def calc_totals(items):
    subtotal = sum(round(i["price"] * i["quantity"], 2) for i in items)
    tax_total = sum(round(i["price"] * i["quantity"] * i["tax_rate"], 2) for i in items)
    grand_total = round(subtotal + tax_total, 2)
    return round(subtotal, 2), round(tax_total, 2), grand_total

def make_receipt(header_title, when, items):
    subtotal, tax_total, grand_total = calc_totals(items)
    lines = [
        "----------------------------------------",
        f"             {header_title}              ",
        "----------------------------------------",
        f"Date: {when}",
        "----------------------------------------",
        "Item            Qty   Price    Tax      Line Total",
        "----------------------------------------"
    ]
    for it in items:
        before = round(it["price"] * it["quantity"], 2)
        tax = round(before * it["tax_rate"], 2)
        line_total = round(before + tax, 2)
        lines.append(f"{it['name']:<15} {it['quantity']:<5} ${it['price']:<7.2f} ${tax:<7.2f} ${line_total:<7.2f}")
    lines.extend([
        "----------------------------------------",
        f"Items purchased: {sum(i['quantity'] for i in items)}",
        f"Subtotal (before tax): ${subtotal:.2f}",
        f"Tax: ${tax_total:.2f}",
        f"Total (after tax): ${grand_total:.2f}",
        "----------------------------------------"
    ])
    return "\n".join(lines)

app = Flask(__name__)

# @app.before_first_request
# # def setup():
#     init_db()

# Health check
@app.get("/health")
def health():
    return {"ok": True}

# Create a new cart
@app.post("/cart")
def create_cart():
    cart_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute("INSERT INTO carts (id, status) VALUES (?, 'open')", (cart_id,))
    return {"cart_id": cart_id}, 201

# Get cart (items + totals)
@app.get("/cart/<cart_id>")
def get_cart(cart_id):
    with get_db() as conn:
        cart = conn.execute("SELECT id, created_at, status FROM carts WHERE id = ?", (cart_id,)).fetchone()
        if not cart:
            abort(404, "Cart not found")
        rows = conn.execute("SELECT id, name, price, quantity, tax_rate FROM cart_items WHERE cart_id = ?", (cart_id,)).fetchall()
        items = [dict(r) for r in rows]
    subtotal, tax_total, grand_total = calc_totals(items)
    return {
        "cart": dict(cart),
        "items": items,
        "totals": {"subtotal": subtotal, "tax_total": tax_total, "grand_total": grand_total}
    }

# Add item to cart
@app.post("/cart/<cart_id>/items")
def add_item(cart_id):
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    price = data.get("price")
    quantity = data.get("quantity", 1)
    tax_rate = data.get("tax_rate", DEFAULT_TAX_RATE)
    if not name:
        abort(400, "name is required")
    try:
        price = float(price)
        quantity = int(quantity)
        tax_rate = float(tax_rate)
    except Exception:
        abort(400, "price, quantity, and tax_rate must be numeric")
    if price < 0 or quantity < 0 or tax_rate < 0:
        abort(400, "price, quantity, and tax_rate must be non-negative")

    with get_db() as conn:
        cart = conn.execute("SELECT id FROM carts WHERE id = ? AND status='open'", (cart_id,)).fetchone()
        if not cart:
            abort(404, "Open cart not found")
        cur = conn.execute(
            "INSERT INTO cart_items (cart_id, name, price, quantity, tax_rate) VALUES (?, ?, ?, ?, ?)",
            (cart_id, name, price, quantity, tax_rate)
        )
        item_id = cur.lastrowid
    return {"item_id": item_id}, 201

# Update item (name/price/quantity/tax_rate)
@app.patch("/cart/<cart_id>/items/<int:item_id>")
def update_item(cart_id, item_id):
    data = request.get_json(force=True, silent=True) or {}
    fields = []
    values = []
    for key in ("name", "price", "quantity", "tax_rate"):
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if not fields:
        abort(400, "No updatable fields provided")
    values.extend([cart_id, item_id])
    with get_db() as conn:
        res = conn.execute(f"UPDATE cart_items SET {', '.join(fields)} WHERE cart_id = ? AND id = ?", values)
        if res.rowcount == 0:
            abort(404, "Item not found")
    return {"updated": True}

# Remove item
@app.delete("/cart/<cart_id>/items/<int:item_id>")
def delete_item(cart_id, item_id):
    with get_db() as conn:
        res = conn.execute("DELETE FROM cart_items WHERE cart_id = ? AND id = ?", (cart_id, item_id))
        if res.rowcount == 0:
            abort(404, "Item not found")
    return {"deleted": True}

# Checkout a cart -> creates a transaction snapshot and closes the cart
@app.post("/cart/<cart_id>/checkout")
def checkout(cart_id):
    with get_db() as conn:
        cart = conn.execute("SELECT id, status FROM carts WHERE id = ?", (cart_id,)).fetchone()
        if not cart:
            abort(404, "Cart not found")
        if cart["status"] != "open":
            abort(400, "Cart is not open")
        rows = conn.execute("SELECT name, price, quantity, tax_rate FROM cart_items WHERE cart_id = ?", (cart_id,)).fetchall()
        items = [dict(r) for r in rows]
        if not items:
            abort(400, "Cart is empty")

        subtotal, tax_total, grand_total = calc_totals(items)
        tx_id = str(uuid.uuid4())
        now = datetime.datetime.now().isoformat(timespec="seconds")
        conn.execute(
            "INSERT INTO transactions (id, cart_id, created_at, subtotal, tax_total, grand_total) VALUES (?, ?, ?, ?, ?, ?)",
            (tx_id, cart_id, now, subtotal, tax_total, grand_total)
        )
        for it in items:
            before = round(it["price"] * it["quantity"], 2)
            tax = round(before * it["tax_rate"], 2)
            line_total = round(before + tax, 2)
            conn.execute(
                "INSERT INTO transaction_items (transaction_id, name, unit_price, quantity, tax_amount, line_total) VALUES (?, ?, ?, ?, ?, ?)",
                (tx_id, it["name"], it["price"], it["quantity"], tax, line_total)
            )
        conn.execute("UPDATE carts SET status='checked_out' WHERE id = ?", (cart_id,))

    receipt = make_receipt("WALMART", now, items)
    return {"transaction_id": tx_id, "receipt": receipt}

# List transactions (simple pagination)
@app.get("/transactions")
def list_transactions():
    try:
        limit = max(1, min(100, int(request.args.get("limit", 20))))
        offset = max(0, int(request.args.get("offset", 0)))
    except Exception:
        abort(400, "Invalid limit/offset")
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, created_at, subtotal, tax_total, grand_total FROM transactions ORDER BY datetime(created_at) DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
    return {"transactions": [dict(r) for r in rows]}

# Get a transaction with items
@app.get("/transactions/<tx_id>")
def get_transaction(tx_id):
    with get_db() as conn:
        tx = conn.execute("SELECT id, cart_id, created_at, subtotal, tax_total, grand_total FROM transactions WHERE id = ?", (tx_id,)).fetchone()
        if not tx:
            abort(404, "Transaction not found")
        items = conn.execute(
            "SELECT id, name, unit_price AS price, quantity, tax_amount AS tax, line_total FROM transaction_items WHERE transaction_id = ?",
            (tx_id,)
        ).fetchall()
    return {"transaction": dict(tx), "items": [dict(r) for r in items]}

# Receipt text endpoint
@app.get("/transactions/<tx_id>/receipt")
def get_receipt(tx_id):
    with get_db() as conn:
        items_rows = conn.execute(
            "SELECT name, unit_price AS price, quantity, (tax_amount / (unit_price*quantity)) as tax_rate FROM transaction_items WHERE transaction_id = ?",
            (tx_id,)
        ).fetchall()
        if not items_rows:
            abort(404, "Transaction not found")
        items = []
        for r in items_rows:
            # guard division by zero
            if r["price"] * r["quantity"] == 0:
                tax_rate = 0.0
            else:
                tax_rate = float(r["tax_rate"]) if r["tax_rate"] is not None else DEFAULT_TAX_RATE
            items.append({"name": r["name"], "price": r["price"], "quantity": r["quantity"], "tax_rate": tax_rate})
        # fetch tx date
        tx = conn.execute("SELECT created_at FROM transactions WHERE id = ?", (tx_id,)).fetchone()
        when = tx["created_at"] if tx else datetime.datetime.now().isoformat(timespec="seconds")
    receipt = make_receipt("WALMART", when, items)
    return {"receipt": receipt}

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=True)
