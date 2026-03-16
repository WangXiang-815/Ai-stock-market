import sqlite3

conn = sqlite3.connect("data/stock.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_prices (
    ticker TEXT,
    date TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    ticker TEXT,
    prediction_date TEXT,
    action TEXT,
    sell_prob REAL,
    hold_prob REAL,
    buy_prob REAL
)
""")

conn.commit()
conn.close()

print("Database initialized")