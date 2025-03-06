"""
LangFlow Tools Registration Module.

This module registers our custom tools with LangFlow, making them available in the LangFlow UI.
"""

import logging
import os
from typing import Dict, Any, List, Optional, Type
from langchain.tools import BaseTool
from langflow import CustomComponent
from langflow.interface.tools.base import ToolComponent
from langflow.interface.tools.util import get_tool_params

# Import our tools
from src.backend.tools import BudgetTimelineTool, StoreLeadTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class BudgetTimelineToolComponent(ToolComponent):
    """Budget & Timeline Tool Component for LangFlow."""
    
    display_name: str = "Budget & Timeline Tool"
    description: str = "Get budget and timeline estimates for a project type"
    
    def build_config(self) -> Dict[str, Any]:
        """Build the configuration for the tool."""
        return {
            "project_type": {
                "display_name": "Project Type",
                "description": "The type of project (e.g., e-commerce website, mobile app)",
                "type": "str",
                "required": True,
            }
        }
    
    def build(self, project_type: str) -> BaseTool:
        """Build the tool."""
        return BudgetTimelineTool()


class StoreLeadToolComponent(ToolComponent):
    """Store Lead Tool Component for LangFlow."""
    
    display_name: str = "Store Lead Tool"
    description: str = "Store lead information in the database"
    
    def build_config(self) -> Dict[str, Any]:
        """Build the configuration for the tool."""
        return {
            "name": {
                "display_name": "Name",
                "description": "The name of the lead",
                "type": "str",
                "required": True,
            },
            "contact": {
                "display_name": "Contact",
                "description": "The contact information of the lead",
                "type": "str",
                "required": True,
            },
            "project_type": {
                "display_name": "Project Type",
                "description": "The type of project",
                "type": "str",
                "required": True,
            },
            "project_details": {
                "display_name": "Project Details",
                "description": "Additional details about the project",
                "type": "str",
                "required": False,
            },
            "estimated_budget": {
                "display_name": "Estimated Budget",
                "description": "The estimated budget range",
                "type": "str",
                "required": False,
            },
            "estimated_timeline": {
                "display_name": "Estimated Timeline",
                "description": "The estimated timeline",
                "type": "str",
                "required": False,
            },
            "follow_up_consent": {
                "display_name": "Follow-up Consent",
                "description": "Whether the lead has consented to follow-up",
                "type": "bool",
                "required": False,
                "default": False,
            }
        }
    
    def build(
        self,
        name: str,
        contact: str,
        project_type: str,
        project_details: Optional[str] = None,
        estimated_budget: Optional[str] = None,
        estimated_timeline: Optional[str] = None,
        follow_up_consent: bool = False
    ) -> BaseTool:
        """Build the tool."""
        return StoreLeadTool()


def register_tools():
    """Register our tools with LangFlow."""
    try:
        # Register the Budget & Timeline Tool
        CustomComponent.add_component(
            BudgetTimelineToolComponent, "BudgetTimelineTool", "Tools"
        )
        
        # Register the Store Lead Tool
        CustomComponent.add_component(
            StoreLeadToolComponent, "StoreLeadTool", "Tools"
        )
        
        logger.info("Successfully registered custom tools with LangFlow")
    except Exception as e:
        logger.error(f"Error registering tools with LangFlow: {e}")


if __name__ == "__main__":
    register_tools() 