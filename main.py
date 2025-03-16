# main.py
import logging
import time
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import APIKeyHeader
from mangum import Mangum  # This adapter allows your app to run on AWS Lambda

# Import application modules
from api.endpoints import pdf_parser, data_storage, scraper
from api.endpoints.bank import router as bank_router
from api.core.config import settings
from services.db_service import init_db, get_supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("sahl-api")

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Sahl API Service",
    description="Secure API for financial data processing",
    version="1.0.0",
    docs_url=None if settings.is_production else "/docs",  # Disable docs in production
    redoc_url=None if settings.is_production else "/redoc",
)

# Security middleware
if settings.is_production:
    app.add_middleware(HTTPSRedirectMiddleware)  # Force HTTPS in production

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*.sahlfinancial.com", "localhost", "127.0.0.1", "*"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Generate request ID for tracing
    request_id = f"req_{time.time()}"
    logger.info(f"Request started: {request_id} - {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Request completed: {request_id} - Status: {response.status_code} - Time: {process_time:.4f}s")
        return response
    except Exception as e:
        logger.error(f"Request failed: {request_id} - Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Include API routers
app.include_router(pdf_parser.router, prefix="/parse-pdf", tags=["PDF Parser"])
app.include_router(data_storage.router, prefix="/store-data", tags=["Data Storage"])
app.include_router(scraper.router, prefix="/scrape", tags=["Scraper"])
app.include_router(bank_router.router, prefix="/bank", tags=["Sahl Bank API"])

# Root route for health checks
@app.get("/")
async def read_root():
    return {
        "status": "healthy",
        "service": "Sahl API Service",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    # Check database connection
    try:
        client = get_supabase_client()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }

# Add an event handler to initialize the database on startup
@app.on_event("startup")
async def on_startup():
    logger.info("Starting Sahl API Service")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        if settings.is_production:
            # In production, we might want to exit if DB init fails
            # import sys
            # sys.exit(1)
            pass

# Create the Lambda handler using Mangum
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)