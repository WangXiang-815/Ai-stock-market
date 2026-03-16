import sqlite3
import pandas as pd
import glob

conn = sqlite3.connect("data/stock.db")

csv_files = glob.glob("data/*.csv")

for file in csv_files:

    ticker = file.split("/")[-1].replace(".csv","")

    df = pd.read_csv(file)

    df = df.rename(columns={
        "Date":"date",
        "Open":"open",
        "High":"high",
        "Low":"low",
        "Close":"close",
        "Volume":"volume"
    })

    df["ticker"] = ticker

    df = df[[
        "ticker","date","open","high","low","close","volume"
    ]]

    df.to_sql(
        "stock_prices",
        conn,
        if_exists="append",
        index=False
    )

    print("Imported", ticker)

conn.close()