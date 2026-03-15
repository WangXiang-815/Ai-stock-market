from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

from model.predict import predict_stock_signal
from llm.deepseek_explain import explain_signal_with_deepseek
from llm.gpt_explain import explain_signal_with_gpt

app = FastAPI(title="Stock AI Suggestion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


STOCK_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "NVDA": "NVIDIA Corporation",
    "TSLA": "Tesla Inc.",
    "AMZN": "Amazon.com Inc.",
    "GOOGL": "Alphabet Inc.",
    "META": "Meta Platforms Inc.",
    "AMD": "Advanced Micro Devices Inc.",
    "NFLX": "Netflix Inc.",
    "SPY": "SPDR S&P 500 ETF Trust"
}


@app.get("/")
def home():
    return {"message": "Stock AI backend is running."}


@app.get("/predict")
def predict(ticker: str = Query(..., description="Stock ticker, e.g. NVDA")):
    try:
        signal = predict_stock_signal(ticker.upper())
        return signal
    except Exception as e:
        print("ERROR in /predict:", repr(e))
        raise HTTPException(status_code=500, detail=f"/predict failed: {str(e)}")


@app.get("/explain")
def explain(ticker: str = Query(..., description="Stock ticker, e.g. NVDA")):
    try:
        signal = predict_stock_signal(ticker.upper())
        explanation = explain_signal_with_deepseek(signal)

        return {
            "status": "success",
            "model_signal": signal,
            "llm_explanation": explanation
        }

    except Exception as e:
        print("ERROR in /explain:", repr(e))
        raise HTTPException(status_code=500, detail=f"/explain failed: {str(e)}")


@app.get("/compare")
def compare(ticker: str = Query(..., description="Stock ticker, e.g. NVDA")):
    try:
        signal = predict_stock_signal(ticker.upper())
        deepseek_result = explain_signal_with_deepseek(signal)
        other_result = explain_signal_with_gpt(signal)

        return {
            "status": "success",
            "model_signal": signal,
            "deepseek_explanation": deepseek_result,
            "other_llm_explanation": other_result
        }

    except Exception as e:
        print("ERROR in /compare:", repr(e))
        raise HTTPException(status_code=500, detail=f"/compare failed: {str(e)}")


@app.get("/price-history")
def price_history(ticker: str = Query(..., description="Stock ticker, e.g. NVDA")):
    try:
        df = yf.download(ticker.upper(), period="6mo", auto_adjust=False)

        if df.empty:
            raise ValueError("No price data found for this ticker.")

        df = df.reset_index()

        if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
            df.columns = df.columns.get_level_values(0)

        prices = []
        for _, row in df.iterrows():
            prices.append({
                "date": str(row["Date"])[:10],
                "close": float(row["Close"])
            })

        return {
            "ticker": ticker.upper(),
            "prices": prices
        }

    except Exception as e:
        print("ERROR in /price-history:", repr(e))
        raise HTTPException(status_code=500, detail=f"/price-history failed: {str(e)}")


@app.get("/stocks-overview")
def stocks_overview():
    """
    Return dashboard cards for a preset list of stocks.
    """
    try:
        tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA"]
        results = []

        for ticker in tickers:
            df = yf.download(ticker, period="5d", auto_adjust=False)
            if df.empty:
                continue

            df = df.reset_index()
            if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
                df.columns = df.columns.get_level_values(0)

            latest_close = float(df["Close"].iloc[-1])
            prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else latest_close
            change = latest_close - prev_close
            change_pct = (change / prev_close * 100) if prev_close != 0 else 0

            signal = predict_stock_signal(ticker)
            probs = signal["probabilities"]

            confidence = max(probs.values()) * 100

            volume = float(df["Volume"].iloc[-1]) / 1_000_000

            results.append({
                "ticker": ticker,
                "company_name": STOCK_NAMES.get(ticker, ticker),
                "price": round(latest_close, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "action": signal["action"],
                "confidence": round(confidence, 2),
                "probabilities": probs,
                "volume_m": round(volume, 2)
            })

        return {"stocks": results}

    except Exception as e:
        print("ERROR in /stocks-overview:", repr(e))
        raise HTTPException(status_code=500, detail=f"/stocks-overview failed: {str(e)}")