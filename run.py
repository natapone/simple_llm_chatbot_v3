#!/usr/bin/env python3
"""
Run script for the pre-sales chatbot.

This script runs the FastAPI application.
"""

import logging
import uvicorn
from src.backend.config import API_HOST, API_PORT, DEBUG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting server on {API_HOST}:{API_PORT} (debug={DEBUG})")
    uvicorn.run(
        "src.backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG
    ) 