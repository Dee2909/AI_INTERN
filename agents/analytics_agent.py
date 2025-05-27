from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class PortfolioRequest(BaseModel):
    holdings: dict  # {symbol: weight}
    market_data: list  # [{symbol, close, date}]

class EarningsRequest(BaseModel):
    earnings_news: list  # [{title, source}]

@app.post("/analyze_risk")
async def analyze_risk(request: PortfolioRequest):
    """Calculate risk exposure for Asia tech stocks."""
    try:
        df = pd.DataFrame(request.market_data)
        total_aum = sum(request.holdings.values()) or 1.0  # Avoid division by zero
        if df.empty or 'symbol' not in df.columns:
            logger.warning("No valid market data for risk analysis")
            return {"tech_allocation": 0.0}
        tech_weight = sum(request.holdings.get(s, 0) for s in request.holdings if s in df['symbol'].values) / total_aum * 100
        return {"tech_allocation": round(tech_weight, 2)}
    except Exception as e:
        logger.error(f"Error in analyze_risk: {str(e)}")
        return {"tech_allocation": 0.0}

@app.post("/analyze_earnings")
async def analyze_earnings(request: EarningsRequest):
    """Identify earnings surprises."""
    try:
        surprises = []
        for news in request.earnings_news:
            title = news['title'].lower()
            if "beat" in title:
                surprises.append({"company": title.split()[0], "surprise": "positive"})
            elif "missed" in title:
                surprises.append({"company": title.split()[0], "surprise": "negative"})
        return {"earnings_surprises": surprises}
    except Exception as e:
        logger.error(f"Error in analyze_earnings: {str(e)}")
        return {"earnings_surprises": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)