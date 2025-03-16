from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.scraping_service import scrape_balance

router = APIRouter()

class ScrapeInput(BaseModel):
    username: str
    password: str
    otp: str = None

@router.post("/")
async def scrape_endpoint(input_data: ScrapeInput):
    """
    Handles login and scraping flow.
    - If no OTP is provided, initiates login and returns "OTP_REQUIRED".
    - If OTP is provided, submits it and returns the extracted balance.
    """
    try:
        result = scrape_balance(input_data.username, input_data.password, input_data.otp)
        return JSONResponse(content=result)
    except Exception as e:
        print("Error in scraping endpoint:", e)
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")