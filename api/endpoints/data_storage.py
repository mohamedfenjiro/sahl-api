import os
import json
import logging
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from api.core.config import settings
from services.data_service import read_data, write_data
from services.db_service import DatabaseService

router = APIRouter()
logger = logging.getLogger(__name__)

class StoreDataInput(BaseModel):
    id: str
    balance: float
    accountId: str

@router.post("/")
async def store_data(request: Request, api_key: str = Header(..., alias="sahl-api-key")):
    """
    Validates API key, then stores incoming JSON data to Supabase.
    """
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        body = await request.json()
        data_input = StoreDataInput(**body)
        
        # Store in Supabase
        db_success = await DatabaseService.store_transaction(data_input.dict())
        
        # Also keep file-based backup
        write_data(data_input.dict())
        
        return JSONResponse(content={
            "success": db_success,
            "message": "Data saved successfully to database"
        })
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving data")

@router.get("/")
async def get_data(api_key: str = Header(..., alias="sahl-api-key")):
    """
    Returns stored data if the provided API key is valid.
    """
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # Try to get data from file backup
        data = read_data()
        if not data:
            return JSONResponse(content={"success": False, "message": "No data found", "path": settings.FILE_PATH})
        return JSONResponse(content={"success": True, "data": data})
    except Exception as e:
        logger.error(f"Error reading data: {str(e)}")
        raise HTTPException(status_code=500, detail="Error reading data")