from fastapi import APIRouter, Depends, HTTPException, Request
from fetch_and_process_data import ProcessCustomerData

router = APIRouter(prefix="/customer_data", tags=["Customer Data"])

def get_processor(request: Request):
    return ProcessCustomerData(request.app.state.logger)

@router.get("/processed_data")
def get_processed_data(processor: ProcessCustomerData = Depends(get_processor)):
    try:
        data = processor.get_data()
        return data.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))