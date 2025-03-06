#!/usr/bin/env python3
"""
Run script for LangFlow.

This script runs LangFlow locally and registers our custom tools.
"""

import os
import logging
import subprocess
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our tools registration module
from src.langflow.langflow_tools import register_tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Get LangFlow configuration from environment variables
LANGFLOW_HOST = os.getenv('LANGFLOW_HOST', 'http://localhost').replace('http://', '')
LANGFLOW_PORT = os.getenv('LANGFLOW_PORT', '7860')

if __name__ == "__main__":
    # Register our custom tools with LangFlow
    logger.info("Registering custom tools with LangFlow")
    try:
        register_tools()
        logger.info("Custom tools registered successfully")
    except Exception as e:
        logger.error(f"Error registering custom tools: {e}")
        logger.warning("Continuing with LangFlow startup without custom tools")
    
    logger.info(f"Starting LangFlow on {LANGFLOW_HOST}:{LANGFLOW_PORT}")
    
    try:
        # Run LangFlow
        subprocess.run([
            "langflow", "run",
            "--host", LANGFLOW_HOST,
            "--port", LANGFLOW_PORT
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running LangFlow: {e}")
    except FileNotFoundError:
        logger.error("LangFlow not found. Make sure it's installed with 'pip install langflow'")
    except KeyboardInterrupt:
        logger.info("LangFlow stopped by user") 