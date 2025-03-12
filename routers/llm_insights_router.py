from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from typing import Optional
from fetch_and_process_data import ProcessCustomerData
from generate_llm_insights import GenerateLLMInsights
from utils.constants import FULL_PROMPT
import pandas as pd
import json

app = FastAPI(title="LLM Insights API", description="API for generating LLM based insights from processed CRM data")

router = APIRouter(prefix="/insights", tags=["LLM Insights"])

MODEL = "google/gemini-2.0-flash-thinking-exp:free"

def get_processor(request: Request):
    return ProcessCustomerData(request.app.state.logger)

def get_llm(request: Request):
    return GenerateLLMInsights(request.app.state.logger)

@router.post("/analyze")
async def get_insights(
    prompt: Optional[str] = FULL_PROMPT,
    processor: ProcessCustomerData = Depends(get_processor),
    llm: GenerateLLMInsights = Depends(get_llm)
):
    try:
        # Step 1: Fetch and process customer data
        data: pd.DataFrame = processor.get_data()
        
        if data.empty:
            raise HTTPException(status_code=404, detail="Failure: No customer data found")
            
        # Step 2: Generate insights using LLM
        insights = llm.call_llm(
            model=MODEL,  
            prompt=prompt,
            content= json.dumps(data.to_string(), indent=2)
        )
        
        return {
            "insights": insights,
            "data_points_analyzed": len(data),
            "prompt_used": prompt
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

app.include_router(router)