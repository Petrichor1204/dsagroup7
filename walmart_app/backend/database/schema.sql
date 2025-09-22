
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS carts (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    status TEXT NOT NULL DEFAULT 'open'  -- 'open' | 'checked_out' | 'abandoned'
);

CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id TEXT NOT NULL,
    name TEXT NOT NULL,
    price REAL NOT NULL,        -- unit price
    quantity INTEGER NOT NULL CHECK(quantity >= 0),
    tax_rate REAL NOT NULL,     -- e.g. 0.1044
    FOREIGN KEY(cart_id) REFERENCES carts(id) ON DELETE CASCADE
);

-- We snapshot checked out carts into immutable transactions for historical analysis
CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    cart_id TEXT, -- original cart reference (nullable if created externally)
    created_at TEXT NOT NULL,
    subtotal REAL NOT NULL,
    tax_total REAL NOT NULL,
    grand_total REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS transaction_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL,
    name TEXT NOT NULL,
    unit_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    tax_amount REAL NOT NULL,
    line_total REAL NOT NULL,   -- unit_price*quantity + tax_amount
    FOREIGN KEY(transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_tx_items_tx ON transaction_items(transaction_id);
