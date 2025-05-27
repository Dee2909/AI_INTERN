import requests
from fastapi import FastAPI
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class OrchestratorRequest(BaseModel):
    query: str
    audio_path: str = None

@app.post("/orchestrate")
async def orchestrate(request: OrchestratorRequest):
    """Orchestrate agent interactions."""
    try:
        # Step 1: Convert voice to text if audio provided
        query = request.query
        if request.audio_path:
            try:
                voice_response = requests.post("http://localhost:8006/speech_to_text", json={"audio_path": request.audio_path}).json()
                query = voice_response["transcription"]
            except Exception as e:
                logger.error(f"Voice agent failed: {str(e)}")
                query = request.query or "Default query"

        # Step 2: Fetch market data
        try:
            market_response = requests.post("http://localhost:8001/fetch_market_data", json={"symbols": ["2330.TW", "005930.KS"]}).json()
        except Exception as e:
            logger.error(f"Market data fetch failed: {str(e)}")
            market_response = {"market_data": []}

        # Step 3: Scrape earnings
        try:
            earnings_response = requests.post("http://localhost:8002/scrape_earnings", json={"query": "2330.TW"}).json()
        except Exception as e:
            logger.error(f"Earnings scrape failed: {str(e)}")
            earnings_response = {"earnings_news": []}

        # Step 4: Retrieve relevant docs
        try:
            retrieve_response = requests.post("http://localhost:8003/retrieve", json={"query": query, "top_k": 5}).json()
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            retrieve_response = {"retrieved_docs": []}

        # Step 5: Analyze risk and earnings
        try:
            risk_response = requests.post("http://localhost:8004/analyze_risk", json={
                "holdings": {"2330.TW": 0.1, "005930.KS": 0.12},
                "market_data": market_response["market_data"]
            }).json()
        except Exception as e:
            logger.error(f"Risk analysis failed: {str(e)}")
            risk_response = {"tech_allocation": 0.0}

        try:
            earnings_analysis = requests.post("http://localhost:8004/analyze_earnings", json={"earnings_news": earnings_response["earnings_news"]}).json()
        except Exception as e:
            logger.error(f"Earnings analysis failed: {str(e)}")
            earnings_analysis = {"earnings_surprises": []}

        # Step 6: Generate narrative
        try:
            narrative_response = requests.post("http://localhost:8005/generate_narrative", json={
                "risk_data": risk_response,
                "earnings_data": earnings_analysis["earnings_surprises"],
                "retrieved_docs": retrieve_response.get("retrieved_docs", [])
            }).json()
        except Exception as e:
            logger.error(f"Narrative generation failed: {str(e)}")
            narrative_response = {"narrative": "Unable to generate market brief due to data issues. Please check data sources."}

        # Step 7: Convert to speech
        try:
            requests.post("http://localhost:8006/text_to_speech", json={"text": narrative_response["narrative"]})
        except Exception as e:
            logger.error(f"Text-to-speech failed: {str(e)}")

        return {"brief": narrative_response["narrative"]}
    except Exception as e:
        logger.error(f"Orchestrator failed: {str(e)}")
        return {"brief": "Error processing request. Please try again."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)