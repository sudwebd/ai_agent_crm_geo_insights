import logging
import json
import pandas as pd
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from typing import Optional
from fetch_and_process_data import ProcessCustomerData
from generate_llm_insights import generate_llm_insights
from generate_alerts import generate_alerts
from keys.constants import FULL_PROMPT

# Configure logging with default level DEBUG
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Insights Alerting System",
    description="This is a prototype of an AI generated Insights Alerting System",
    version="0.1"
)

router = APIRouter(prefix="/ai_insight_alerts", tags=["AI Insights Alerts"])

# MODEL = "deepseek/deepseek-r1:free"
MODEL = "google/gemini-2.0-flash-thinking-exp:free"

def get_processor():
    return ProcessCustomerData()

def get_llm():
    return generate_llm_insights()

def get_alerts():
    return generate_alerts()

@router.post("/get_insights_alerts")
async def get_insights_alerts(
    prompt: Optional[str] = FULL_PROMPT,
    processor: ProcessCustomerData = Depends(get_processor), 
    llm: generate_llm_insights = Depends(get_llm), 
    alerts: generate_alerts = Depends(get_alerts)
):
    logger.debug("Received request to generate insights alerts.")
    try:
        # Step 1: Fetch and process customer data
        logger.debug("Fetching customer data.")
        data: pd.DataFrame = processor.get_data()
        
        if data.empty:
            logger.error("No customer data found.")
            raise HTTPException(status_code=404, detail="Failure: No customer data found")

        # Step 2: Generate insights using LLM
        logger.debug("Generating insights using LLM.")
        insights = llm.call_llm(
            model=MODEL,  
            prompt=prompt,
            content=json.dumps(data.to_string(), indent=2)
        )
        logger.debug("LLM generated insights.")
        
        # Step 3: Generate alerts
        logger.debug("Generating alerts.")
        alerts_response = alerts.gmail_alert(llm.extract_html(insights))
        logger.debug("Alerts generated successfully.")
        
        logger.info("Successfully generated insights alerts.")
        return {"insights": insights, "alerts": alerts_response}
    
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

app.include_router(router)