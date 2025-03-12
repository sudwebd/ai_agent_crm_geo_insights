from fastapi import FastAPI
from routers import customer_data_router
from routers import llm_insights_router
from routers import alerts_router

app = FastAPI(title = "ai_crm_geo_insights_bot", description = "This is an API to get AI powered customer insights from CRM data", version = "0.1")
app.include_router(customer_data_router.router)
app.include_router(llm_insights_router.router)
app.include_router(alerts_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI powered CRM insights API"}