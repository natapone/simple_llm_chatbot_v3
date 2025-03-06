"""
Configuration module for the pre-sales chatbot.

This module loads and provides access to configuration settings from environment variables.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=os.getenv('LOG_FILE', None)
)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = os.getenv('DB_PATH', 'sqlite:///database.db')

# API configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5000'))
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

# LangFlow configuration
LANGFLOW_API_KEY = os.getenv('LANGFLOW_API_KEY', '')
LANGFLOW_HOST = os.getenv('LANGFLOW_HOST', 'http://localhost')
LANGFLOW_PORT = int(os.getenv('LANGFLOW_PORT', '7860'))

# LiteLLM configuration
LITELLM_API_KEY = os.getenv('LITELLM_API_KEY', '')
LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gpt-4o-mini')

# Log configuration settings
logger.info("Configuration loaded:")
logger.info(f"API_HOST: {API_HOST}")
logger.info(f"API_PORT: {API_PORT}")
logger.info(f"DEBUG: {DEBUG}")
logger.info(f"LANGFLOW_HOST: {LANGFLOW_HOST}")
logger.info(f"LANGFLOW_PORT: {LANGFLOW_PORT}")
logger.info(f"LITELLM_MODEL: {LITELLM_MODEL}") 