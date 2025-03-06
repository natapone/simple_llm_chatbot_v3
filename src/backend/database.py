"""
Database module for the pre-sales chatbot.

This module defines the database models and utility functions for interacting with the database.
"""

import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
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

# Get database path from environment variables
DB_PATH = os.getenv('DB_PATH', 'sqlite:///database.db')

# Create engine and session
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class ProjectEstimate(Base):
    """
    Model for project estimates.
    
    Attributes:
        id (int): Primary key
        project_type (str): Type of project
        budget_range (str): Budget range for the project
        typical_timeline (str): Typical timeline for the project
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = 'project_estimates'

    id = Column(Integer, primary_key=True)
    project_type = Column(String(255), nullable=False)
    budget_range = Column(String(255), nullable=False)
    typical_timeline = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProjectEstimate(id={self.id}, project_type='{self.project_type}')>"


class Lead(Base):
    """
    Model for leads.
    
    Attributes:
        id (int): Primary key
        name (str): Name of the lead
        contact (str): Contact information of the lead
        project_type (str): Type of project
        project_details (str): Additional details about the project
        estimated_budget (str): Estimated budget range
        estimated_timeline (str): Estimated timeline
        follow_up_consent (bool): Whether the lead has consented to follow-up
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    contact = Column(String(255), nullable=False)
    project_type = Column(String(255), nullable=False)
    project_details = Column(Text)
    estimated_budget = Column(String(255))
    estimated_timeline = Column(String(255))
    follow_up_consent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.name}', project_type='{self.project_type}')>"


def initialize_database():
    """
    Initialize the database with tables and initial data.
    
    This function creates the tables if they don't exist and populates the project_estimates table with initial data.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Initializing database...")
    try:
        # Create tables
        Base.metadata.create_all(engine)
        logger.info("Tables created successfully.")
        
        # Check if project_estimates table is empty
        session = Session()
        if session.query(ProjectEstimate).count() == 0:
            logger.info("Populating project_estimates table with initial data...")
            
            # Initial data
            initial_data = [
                ProjectEstimate(
                    project_type="e-commerce website",
                    budget_range="$3k-$6k",
                    typical_timeline="2-3 months"
                ),
                ProjectEstimate(
                    project_type="mobile restaurant app",
                    budget_range="$5k-$8k",
                    typical_timeline="3-4 months"
                ),
                ProjectEstimate(
                    project_type="CRM system",
                    budget_range="$4k-$7k",
                    typical_timeline="4-6 months"
                ),
                ProjectEstimate(
                    project_type="chatbot integration",
                    budget_range="$2k-$4k",
                    typical_timeline="2-3 months"
                ),
                ProjectEstimate(
                    project_type="custom logistics",
                    budget_range="$10k-$20k",
                    typical_timeline="5-6 months"
                )
            ]
            
            # Add initial data to the session
            session.add_all(initial_data)
            session.commit()
            logger.info("Initial data added successfully.")
        
        session.close()
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False


def get_all_project_types():
    """
    Get all project types from the database.
    
    Returns:
        list: List of project types
    """
    logger.info("Getting all project types...")
    try:
        session = Session()
        project_types = [pe.project_type for pe in session.query(ProjectEstimate).all()]
        session.close()
        return project_types
    except Exception as e:
        logger.error(f"Error getting project types: {e}")
        return []


def get_estimate_by_project_type(project_type):
    """
    Get budget and timeline estimates for a project type.
    
    Args:
        project_type (str): The type of project
        
    Returns:
        dict: A dictionary containing the project_type, budget_range, and typical_timeline,
              or None if the project type is not found
    """
    logger.info(f"Getting estimate for project type: {project_type}")
    try:
        session = Session()
        project_estimate = session.query(ProjectEstimate).filter(
            ProjectEstimate.project_type.ilike(f"%{project_type}%")
        ).first()
        
        if project_estimate:
            result = {
                "project_type": project_estimate.project_type,
                "budget_range": project_estimate.budget_range,
                "typical_timeline": project_estimate.typical_timeline
            }
        else:
            result = None
            
        session.close()
        return result
    except Exception as e:
        logger.error(f"Error getting estimate: {e}")
        return None


def store_lead(name, contact, project_type, project_details=None, estimated_budget=None, estimated_timeline=None, follow_up_consent=False):
    """
    Store lead information in the database.
    
    Args:
        name (str): The name of the lead
        contact (str): The contact information of the lead
        project_type (str): The type of project
        project_details (str, optional): Additional details about the project
        estimated_budget (str, optional): The estimated budget range
        estimated_timeline (str, optional): The estimated timeline
        follow_up_consent (bool, optional): Whether the lead has consented to follow-up
        
    Returns:
        int: The ID of the newly created lead, or None if an error occurred
    """
    logger.info(f"Storing lead: {name}, {contact}, {project_type}")
    try:
        session = Session()
        
        # Create new lead
        lead = Lead(
            name=name,
            contact=contact,
            project_type=project_type,
            project_details=project_details,
            estimated_budget=estimated_budget,
            estimated_timeline=estimated_timeline,
            follow_up_consent=follow_up_consent
        )
        
        # Add lead to the session
        session.add(lead)
        session.commit()
        
        # Get the ID of the newly created lead
        lead_id = lead.id
        
        session.close()
        logger.info(f"Lead stored successfully with ID: {lead_id}")
        return lead_id
    except Exception as e:
        logger.error(f"Error storing lead: {e}")
        return None


def get_all_leads():
    """
    Get all leads from the database.
    
    Returns:
        list: List of leads as dictionaries, or None if an error occurred
    """
    logger.info("Getting all leads...")
    try:
        session = Session()
        leads = session.query(Lead).all()
        
        # Convert leads to dictionaries
        result = []
        for lead in leads:
            result.append({
                'id': lead.id,
                'name': lead.name,
                'contact': lead.contact,
                'project_type': lead.project_type,
                'project_details': lead.project_details,
                'estimated_budget': lead.estimated_budget,
                'estimated_timeline': lead.estimated_timeline,
                'follow_up_consent': lead.follow_up_consent,
                'created_at': lead.created_at.isoformat(),
                'updated_at': lead.updated_at.isoformat()
            })
            
        session.close()
        return result
    except Exception as e:
        logger.error(f"Error getting leads: {e}")
        return None


def add_project_estimate(project_type, budget_range, typical_timeline):
    """
    Add a new project estimate to the database.
    
    Args:
        project_type (str): The type of project
        budget_range (str): The budget range for the project
        typical_timeline (str): The typical timeline for the project
        
    Returns:
        int: The ID of the newly created project estimate, or None if an error occurred
    """
    logger.info(f"Adding project estimate: {project_type}, {budget_range}, {typical_timeline}")
    try:
        session = Session()
        
        # Create new project estimate
        project_estimate = ProjectEstimate(
            project_type=project_type,
            budget_range=budget_range,
            typical_timeline=typical_timeline
        )
        
        # Add project estimate to the session
        session.add(project_estimate)
        session.commit()
        
        # Get the ID of the newly created project estimate
        project_estimate_id = project_estimate.id
        
        session.close()
        logger.info(f"Project estimate added successfully with ID: {project_estimate_id}")
        return project_estimate_id
    except Exception as e:
        logger.error(f"Error adding project estimate: {e}")
        return None


# Initialize the database when the module is imported
if __name__ == "__main__":
    initialize_database() 