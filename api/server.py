from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

from model.predict import predict_stock_signal
from llm.deepseek_explain import explain_signal_with_deepseek

app = FastAPI(title="Stock AI Suggestion API")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/price-history")
def price_history(ticker: str = Query(..., description="Stock ticker, e.g. NVDA")):
    try:
        df = yf.download(ticker.upper(), period="6mo", auto_adjust=False)

        if df.empty:
            raise ValueError("No price data found for this ticker.")

        df = df.reset_index()

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
        raise HTTPException(
            status_code=500,
            detail=f"/price-history failed: {str(e)}"
        )