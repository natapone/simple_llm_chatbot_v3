"""
API module for the pre-sales chatbot.

This module defines the API endpoints for the pre-sales chatbot.
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from .database import get_estimate_by_project_type, store_lead, get_all_leads
from .tools import get_estimate

# Configure logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()


class LeadCreate(BaseModel):
    """
    Model for creating a lead.
    
    Attributes:
        name (str): The name of the lead
        contact (str): The contact information of the lead
        project_type (str): The type of project
        project_details (str, optional): Additional details about the project
        estimated_budget (str, optional): The estimated budget range
        estimated_timeline (str, optional): The estimated timeline
        follow_up_consent (bool, optional): Whether the lead has consented to follow-up
    """
    name: str = Field(..., description="The name of the lead")
    contact: str = Field(..., description="The contact information of the lead")
    project_type: str = Field(..., description="The type of project")
    project_details: Optional[str] = Field(None, description="Additional details about the project")
    estimated_budget: Optional[str] = Field(None, description="The estimated budget range")
    estimated_timeline: Optional[str] = Field(None, description="The estimated timeline")
    follow_up_consent: bool = Field(False, description="Whether the lead has consented to follow-up")


class LeadResponse(BaseModel):
    """
    Model for lead response.
    
    Attributes:
        id (int): The ID of the lead
        status (str): The status of the operation
    """
    id: int
    status: str = "success"


class Lead(BaseModel):
    """
    Model for a lead.
    
    Attributes:
        id (int): The ID of the lead
        name (str): The name of the lead
        contact (str): The contact information of the lead
        project_type (str): The type of project
        project_details (str, optional): Additional details about the project
        estimated_budget (str, optional): The estimated budget range
        estimated_timeline (str, optional): The estimated timeline
        follow_up_consent (bool): Whether the lead has consented to follow-up
        created_at (str): The creation timestamp
        updated_at (str): The last update timestamp
    """
    id: int
    name: str
    contact: str
    project_type: str
    project_details: Optional[str] = None
    estimated_budget: Optional[str] = None
    estimated_timeline: Optional[str] = None
    follow_up_consent: bool
    created_at: str
    updated_at: str


class LeadsResponse(BaseModel):
    """
    Model for leads response.
    
    Attributes:
        leads (List[Lead]): The list of leads
    """
    leads: List[Lead]


class EstimateResponse(BaseModel):
    """
    Model for estimate response.
    
    Attributes:
        project_type (str): The type of project
        budget_range (str): The budget range for the project
        typical_timeline (str): The typical timeline for the project
        message (str, optional): Additional message
    """
    project_type: str
    budget_range: str
    typical_timeline: str
    message: Optional[str] = None


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: A dictionary with the status
    """
    logger.info("Health check requested")
    return {"status": "ok"}


@router.get("/estimates", response_model=EstimateResponse, tags=["Estimates"])
async def get_estimates(project_type: str = Query(..., description="The type of project")):
    """
    Get budget and timeline estimates for a project type.
    
    Args:
        project_type (str): The type of project
        
    Returns:
        EstimateResponse: The budget and timeline estimates
    """
    logger.info(f"Estimate requested for project type: {project_type}")
    
    if not project_type:
        logger.warning("Missing project_type parameter")
        raise HTTPException(status_code=400, detail="Missing project_type parameter")
    
    estimate = get_estimate(project_type)
    
    if not estimate:
        logger.warning(f"No estimate found for project type: {project_type}")
        return EstimateResponse(
            project_type="unknown",
            budget_range="Requires more information",
            typical_timeline="Requires more information",
            message="We need more details about your project to provide an accurate estimate."
        )
    
    return EstimateResponse(**estimate)


@router.post("/leads", response_model=LeadResponse, tags=["Leads"])
async def create_lead(lead: LeadCreate):
    """
    Store lead information.
    
    Args:
        lead (LeadCreate): The lead information
        
    Returns:
        LeadResponse: The response with the lead ID
    """
    logger.info(f"Lead creation requested for: {lead.name}")
    
    lead_id = store_lead(
        name=lead.name,
        contact=lead.contact,
        project_type=lead.project_type,
        project_details=lead.project_details,
        estimated_budget=lead.estimated_budget,
        estimated_timeline=lead.estimated_timeline,
        follow_up_consent=lead.follow_up_consent
    )
    
    if not lead_id:
        logger.error(f"Failed to store lead: {lead.name}")
        raise HTTPException(status_code=500, detail="Failed to store lead")
    
    logger.info(f"Lead created with ID: {lead_id}")
    return LeadResponse(id=lead_id)


@router.get("/leads", response_model=LeadsResponse, tags=["Leads"])
async def get_leads():
    """
    Get all leads.
    
    Returns:
        LeadsResponse: The response with the list of leads
    """
    logger.info("Leads requested")
    
    leads = get_all_leads()
    
    if leads is None:
        logger.error("Failed to get leads")
        raise HTTPException(status_code=500, detail="Failed to get leads")
    
    return LeadsResponse(leads=leads) 