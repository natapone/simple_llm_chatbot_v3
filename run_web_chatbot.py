#!/usr/bin/env python3
"""
Run script for Web Chatbot.

This script runs both the backend API and the web interface for the chatbot.
"""

import os
import logging
import subprocess
import threading
import time
from dotenv import load_dotenv

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
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = os.getenv('API_PORT', '8001')
WEB_HOST = '0.0.0.0'
WEB_PORT = '8000'

def run_backend():
    """Run the backend API."""
    logger.info(f"Starting backend API on {API_HOST}:{API_PORT}")
    try:
        subprocess.run(["python", "run.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running backend API: {e}")
    except KeyboardInterrupt:
        logger.info("Backend API stopped by user")

def run_web_interface():
    """Run the web interface."""
    logger.info(f"Starting web interface on {WEB_HOST}:{WEB_PORT}")
    try:
        subprocess.run(["python", "web_interface.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running web interface: {e}")
    except KeyboardInterrupt:
        logger.info("Web interface stopped by user")

if __name__ == "__main__":
    logger.info("Starting Web Chatbot")
    
    # Start backend API in a separate thread
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Wait for backend API to start
    logger.info("Waiting for backend API to start...")
    time.sleep(5)
    
    # Run web interface in the main thread
    run_web_interface() 