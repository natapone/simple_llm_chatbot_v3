"""
Main application entry point for the pre-sales chatbot.

This module initializes the FastAPI application and sets up the API endpoints.
"""

import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from contextlib import asynccontextmanager

from .config import API_HOST, API_PORT, DEBUG
from .database import initialize_database
from .api import router

# Configure logging
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    
    This handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up the application...")
    
    # Initialize the database
    if initialize_database():
        logger.info("Database initialized successfully.")
    else:
        logger.error("Failed to initialize database.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down the application...")

# Create FastAPI application
app = FastAPI(
    title="Pre-Sales Chatbot API",
    description="API for the pre-sales chatbot",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all requests.
    
    Args:
        request (Request): The request object
        call_next (callable): The next middleware or route handler
        
    Returns:
        Response: The response from the next middleware or route handler
    """
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process the request
    try:
        response = await call_next(request)
        
        # Log response details
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} (took {process_time:.4f}s)")
        
        return response
    except Exception as e:
        # Log error details
        process_time = time.time() - start_time
        logger.error(f"Error: {str(e)} (took {process_time:.4f}s)")
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Include API router
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: A dictionary with a welcome message
    """
    return {"message": "Welcome to the Pre-Sales Chatbot API"}

# Run the application
if __name__ == "__main__":
    logger.info(f"Starting server on {API_HOST}:{API_PORT} (debug={DEBUG})")
    uvicorn.run(
        "src.backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG
    ) 