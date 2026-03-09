import joblib
import numpy as np
import pandas as pd
import yfinance as yf
from tensorflow.keras.models import load_model

# Load trained model and scaler
model = load_model("model/lstm_model.h5")
scaler = joblib.load("model/scaler.pkl")

label_map = {
    0: "SELL",
    1: "HOLD",
    2: "BUY"
}

WINDOW = 60
HORIZON_DAYS = 20

FEATURE_COLS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "ret1",
    "ma5",
    "ma20",
    "vol10",
    "mom10"
]


def load_ticker_data(ticker: str, start="2019-01-01", end=None) -> pd.DataFrame:
    """
    Download ticker data from Yahoo Finance.
    """
    df = yf.download(ticker, start=start, end=end, auto_adjust=False)
    df = df.reset_index()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build technical features for prediction.
    """
    df = df.copy()

    df["open"] = df["Open"]
    df["high"] = df["High"]
    df["low"] = df["Low"]
    df["close"] = df["Close"]
    df["volume"] = df["Volume"]

    df["ret1"] = df["close"].pct_change()
    df["ma5"] = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["vol10"] = df["ret1"].rolling(10).std()
    df["mom10"] = df["close"] / df["close"].shift(10) - 1

    df = df.dropna(subset=FEATURE_COLS).copy()
    return df


def prepare_input(df_feat: pd.DataFrame) -> np.ndarray:
    """
    Prepare the latest rolling window for LSTM input.
    """
    if len(df_feat) < WINDOW:
        raise ValueError(f"Not enough data to build a {WINDOW}-day window.")

    latest_features = df_feat[FEATURE_COLS].values[-WINDOW:]
    latest_scaled = scaler.transform(latest_features)

    X_input = latest_scaled.reshape(1, WINDOW, len(FEATURE_COLS)).astype(np.float32)
    return X_input


def predict_stock_signal(ticker: str) -> dict:
    """
    Generate structured JSON signal for one ticker.
    """
    df = load_ticker_data(ticker)
    df_feat = build_features(df)
    X_input = prepare_input(df_feat)

    probs = model.predict(X_input, verbose=0)[0]
    pred_class = int(np.argmax(probs))
    action = label_map[pred_class]

    latest_date = str(pd.to_datetime(df_feat["Date"].iloc[-1]).date())

    signal_json = {
        "ticker": ticker,
        "prediction_date": latest_date,
        "horizon_days": HORIZON_DAYS,
        "model_name": "lstm_multiclass_v1",
        "action": action,
        "probabilities": {
            "SELL": round(float(probs[0]), 4),
            "HOLD": round(float(probs[1]), 4),
            "BUY": round(float(probs[2]), 4)
        },
        "features_used": FEATURE_COLS,
        "notes": [
            "Prediction is based on historical technical indicators only.",
            "This output is for decision support, not profit guarantee."
        ]
    }

    return signal_json