"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from .config import settings
from .database import test_connection
from .routers import rules, recommendations
from .models import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="""
    ## Market Basket Analysis API
    
    This API provides product recommendations based on FP-Growth association rules.
    
    ### Features:
    - 🎯 Real-time product recommendations
    - 📊 Association rules exploration
    - 📈 Statistics and analytics
    - 🔍 Search rules by item
    
    ### Algorithm:
    Uses **FP-Growth** algorithm for efficient frequent pattern mining.
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rules.router)
app.include_router(recommendations.router)

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """
    API root endpoint
    """
    return {
        "message": "Market Basket Analysis API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health"
    }

# Health check
@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint
    """
    db_status = "connected" if test_connection() else "disconnected"
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        database=db_status,
        timestamp=datetime.now()
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup
    """
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    
    # Test database connection
    if test_connection():
        logger.info("✓ Database connection established")
    else:
        logger.error("✗ Database connection failed")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown
    """
    logger.info("Shutting down API")

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )