#!/usr/bin/env python3
"""
Run script for LangFlow Memory Chatbot Web Interface.

This script runs both the backend API and the web interface for the memory chatbot.
"""

import os
import logging
import asyncio
import subprocess
import sys
import threading
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the web interface
from web_interface import app as web_app

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
BACKEND_HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
BACKEND_PORT = int(os.getenv('BACKEND_PORT', '8001'))
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
WEB_PORT = int(os.getenv('WEB_PORT', '8000'))

def run_backend():
    """Run the backend API."""
    logger.info(f"Starting backend API on {BACKEND_HOST}:{BACKEND_PORT}")
    try:
        subprocess.run([
            "python", "run.py",
            "--host", BACKEND_HOST,
            "--port", str(BACKEND_PORT)
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running backend API: {e}")
    except KeyboardInterrupt:
        logger.info("Backend API stopped by user")

def run_web_interface():
    """Run the web interface."""
    import uvicorn
    logger.info(f"Starting web interface on {WEB_HOST}:{WEB_PORT}")
    try:
        uvicorn.run(web_app, host=WEB_HOST, port=WEB_PORT)
    except KeyboardInterrupt:
        logger.info("Web interface stopped by user")

if __name__ == "__main__":
    logger.info("Starting Memory Chatbot")
    
    # Start the backend API in a separate thread
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Run the web interface in the main thread
    run_web_interface() 