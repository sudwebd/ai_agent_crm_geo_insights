from fastapi import FastAPI, Depends
from routers import customer_data_router, llm_insights_router, alerts_router
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI(title = "ai_crm_geo_insights_bot", description = "This is an API to get AI powered customer insights from CRM data", version = "0.1")

app.state.logger = logging.getLogger("ai_agent_crm_geo_insights")

app.include_router(customer_data_router.router)
app.include_router(llm_insights_router.router)
app.include_router(alerts_router.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI powered CRM insights API"}