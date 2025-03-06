"""
Budget & Timeline Tool for the pre-sales chatbot.

This module implements the Budget & Timeline Tool, which provides budget and timeline estimates
for various project types using LiteLLM for project type extraction.
"""

import logging
import os
import json
from dotenv import load_dotenv
from litellm import completion
from .database import get_all_project_types, get_estimate_by_project_type, store_lead
from typing import Dict, Any, Optional, List, Union, ClassVar
from pydantic import BaseModel, Field

# LangChain imports for tool compatibility
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# LiteLLM configuration
LITELLM_API_KEY = os.getenv('LITELLM_API_KEY', '')
LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gpt-4o-mini')


def extract_project_type(user_input):
    """
    Extract the project type from user input using LiteLLM.
    
    Args:
        user_input (str): The user's description of their project
        
    Returns:
        str: The extracted project type that matches one in our database, or None if no match is found
        
    Example:
        >>> extract_project_type("I need an online shop for my business")
        "e-commerce website"
    """
    logger.info(f"Extracting project type from: {user_input}")
    
    try:
        # Get all project types from the database
        project_types = get_all_project_types()
        
        if not project_types:
            logger.warning("No project types found in the database")
            return None
        
        # Create a prompt for the LLM
        prompt = f"""
        You are a project type classifier for a software development company.
        
        Given a user's description of their project, classify it into one of the following project types:
        {', '.join(project_types)}
        
        If the user's description doesn't match any of these project types, respond with "unknown".
        
        User's project description: "{user_input}"
        
        Project type (respond with only the project type, no other text):
        """
        
        # Call LiteLLM
        response = completion(
            model=LITELLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for more deterministic results
            max_tokens=50
        )
        
        # Extract the project type from the response
        extracted_type = response.choices[0].message.content.strip().lower()
        logger.info(f"Extracted project type: {extracted_type}")
        
        # Match the extracted type to one of our project types
        for pt in project_types:
            if pt.lower() == extracted_type:
                return pt
            
        # If the extracted type is "unknown" or doesn't match any of our project types
        if extracted_type == "unknown":
            logger.info("Project type classified as unknown")
            return None
        
        # Try to find a partial match
        for pt in project_types:
            if extracted_type in pt.lower() or pt.lower() in extracted_type:
                logger.info(f"Found partial match: {pt}")
                return pt
        
        logger.info("No matching project type found")
        return None
    
    except Exception as e:
        logger.error(f"Error extracting project type: {e}")
        return None


def get_estimate(project_type):
    """
    Get budget and timeline estimates for a project type.
    
    This function first tries to find an exact match for the project type.
    If no exact match is found, it uses LiteLLM to extract the project type.
    
    Args:
        project_type (str): The type of project or a description of the project
        
    Returns:
        dict: A dictionary containing the project_type, budget_range, and typical_timeline,
              or a default response if no match is found
              
    Example:
        >>> get_estimate("e-commerce website")
        {
            "project_type": "e-commerce website",
            "budget_range": "$3k-$6k",
            "typical_timeline": "2-3 months"
        }
    """
    logger.info(f"Getting estimate for project type: {project_type}")
    
    try:
        # Try to get an exact match first
        estimate = get_estimate_by_project_type(project_type)
        
        # If no exact match, try extracting the project type using LiteLLM
        if not estimate:
            logger.info(f"No exact match found for {project_type}, trying LiteLLM extraction")
            extracted_project_type = extract_project_type(project_type)
            
            if extracted_project_type:
                logger.info(f"Extracted {project_type} to {extracted_project_type}")
                estimate = get_estimate_by_project_type(extracted_project_type)
        
        # If we still don't have an estimate, return a default response
        if not estimate:
            logger.warning(f"No match found for {project_type}")
            return {
                "project_type": "unknown",
                "budget_range": "Requires more information",
                "typical_timeline": "Requires more information",
                "message": "We need more details about your project to provide an accurate estimate."
            }
        
        return estimate
    
    except Exception as e:
        logger.error(f"Error getting estimate: {e}")
        return {
            "project_type": "error",
            "budget_range": "Unavailable",
            "typical_timeline": "Unavailable",
            "message": "An error occurred while retrieving the estimate. Please try again later."
        }


# LangChain Tool Implementations for LangFlow compatibility

class BudgetTimelineInput(BaseModel):
    """Input for the Budget & Timeline Tool."""
    project_type: str = Field(..., description="The type of project (e.g., e-commerce website, mobile app)")


class BudgetTimelineTool(BaseTool):
    """Tool for getting budget and timeline estimates for a project type."""
    name: ClassVar[str] = "budget_timeline_tool"
    description: ClassVar[str] = "Get budget and timeline estimates for a project type"
    args_schema: ClassVar[type] = BudgetTimelineInput
    
    def _run(self, project_type: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[str, Any]:
        """Run the tool."""
        logger.info(f"BudgetTimelineTool called with project_type: {project_type}")
        return get_estimate(project_type)


class StoreLeadInput(BaseModel):
    """Input for the Store Lead Tool."""
    name: str = Field(..., description="The name of the lead")
    contact: str = Field(..., description="The contact information of the lead")
    project_type: str = Field(..., description="The type of project")
    project_details: Optional[str] = Field(None, description="Additional details about the project")
    estimated_budget: Optional[str] = Field(None, description="The estimated budget range")
    estimated_timeline: Optional[str] = Field(None, description="The estimated timeline")
    follow_up_consent: bool = Field(False, description="Whether the lead has consented to follow-up")


class StoreLeadTool(BaseTool):
    """Tool for storing lead information in the database."""
    name: ClassVar[str] = "store_lead_tool"
    description: ClassVar[str] = "Store lead information in the database"
    args_schema: ClassVar[type] = StoreLeadInput
    
    def _run(
        self,
        name: str,
        contact: str,
        project_type: str,
        project_details: Optional[str] = None,
        estimated_budget: Optional[str] = None,
        estimated_timeline: Optional[str] = None,
        follow_up_consent: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Run the tool."""
        logger.info(f"StoreLeadTool called with name: {name}, contact: {contact}")
        
        lead_id = store_lead(
            name=name,
            contact=contact,
            project_type=project_type,
            project_details=project_details,
            estimated_budget=estimated_budget,
            estimated_timeline=estimated_timeline,
            follow_up_consent=follow_up_consent
        )
        
        if not lead_id:
            return {"status": "error", "message": "Failed to store lead"}
        
        return {"status": "success", "id": lead_id}


# Create tool instances for direct use
budget_timeline_tool = BudgetTimelineTool()
store_lead_tool = StoreLeadTool()

# Function to get all available tools
def get_tools() -> List[BaseTool]:
    """Get all available tools for use with LangFlow."""
    return [budget_timeline_tool, store_lead_tool] 