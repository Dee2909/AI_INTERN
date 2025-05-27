import yfinance as yf
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class MarketRequest(BaseModel):
    symbols: list[str]
    date: str = None

@app.post("/fetch_market_data")
async def fetch_market_data(request: MarketRequest):
    """Fetch market data for given symbols using yfinance."""
    if not request.date:
        request.date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')  # Use yesterday to avoid market close issues
    
    data = []
    for symbol in request.symbols:
        for _ in range(3):  # Retry up to 3 times
            try:
                ticker = yf.Ticker(symbol)
                # Fetch data for the past 7 days to ensure availability
                hist = ticker.history(period="7d", end=request.date)
                if not hist.empty:
                    data.append({
                        "symbol": symbol,
                        "close": hist['Close'].iloc[-1],
                        "volume": hist['Volume'].iloc[-1],
                        "date": request.date
                    })
                    break
                else:
                    logger.warning(f"No data found for {symbol}")
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
                time.sleep(1)  # Wait before retrying
        else:
            logger.error(f"Failed to fetch data for {symbol} after retries")
    
    return {"market_data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)