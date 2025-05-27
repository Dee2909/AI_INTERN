from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
llm = HuggingFacePipeline.from_model_id(
    model_id="distilgpt2",
    task="text-generation",
    pipeline_kwargs={"max_length": 200, "truncation": True}
)

class NarrativeRequest(BaseModel):
    risk_data: dict
    earnings_data: list
    retrieved_docs: list

prompt_template = PromptTemplate(
    input_variables=["risk", "earnings", "docs"],
    template="Generate a concise market brief: Risk exposure: {risk}%. Earnings: {earnings}. Context: {docs}"
)

@app.post("/generate_narrative")
async def generate_narrative(request: NarrativeRequest):
    """Generate a narrative brief using LLM."""
    try:
        earnings_str = ", ".join([f"{e['company']} {e['surprise']}" for e in request.earnings_data]) if request.earnings_data else "No earnings data"
        narrative = llm.invoke(
            prompt_template.format(
                risk=request.risk_data.get('tech_allocation', 0.0),
                earnings=earnings_str,
                docs="; ".join(request.retrieved_docs) if request.retrieved_docs else "No context available"
            )
        )
        return {"narrative": narrative}
    except Exception as e:
        logger.error(f"Error generating narrative: {str(e)}")
        return {"narrative": "Failed to generate narrative due to processing error."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)