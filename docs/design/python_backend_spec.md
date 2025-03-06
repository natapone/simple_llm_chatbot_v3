# Python Backend Technical Specification

## 1. Overview

This document outlines the technical specifications for the Python backend of the pre-sales chatbot. The backend is responsible for storing lead information, providing budget and timeline estimates, and serving as the integration point between the LangFlow conversation flow and the database.

## 2. Purpose and Goals

### 2.1 Primary Purpose

To provide a reliable and scalable backend for the pre-sales chatbot, handling data storage, retrieval, and API endpoints for integration with LangFlow.

### 2.2 Goals

1. Store and manage lead information
2. Provide budget and timeline estimates based on project types
3. Expose API endpoints for integration with LangFlow
4. Ensure data integrity and security
5. Support future scalability and enhancements

## 3. Architecture

### 3.1 High-Level Architecture

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   LangFlow    │────▶│    Python     │────▶│   Database    │
│  (Frontend)   │     │    Backend    │     │  (SQLite)     │
└───────────────┘     └───────────────┘     └───────────────┘
                             │
                             │
                             ▼
                      ┌───────────────┐
                      │  Budget &     │
                      │ Timeline Tool │
                      └───────────────┘
```

### 3.2 Components

1. **API Server**: FastAPI application serving API endpoints
2. **Database**: SQLite database for storing lead information and project estimates
3. **Budget & Timeline Tool**: Module for retrieving budget and timeline estimates
4. **Utilities**: Helper functions and utilities for common operations

## 4. Database Schema

### 4.1 Project Estimates Table

```sql
CREATE TABLE project_estimates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_type TEXT NOT NULL,
    budget_range TEXT NOT NULL,
    typical_timeline TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Leads Table

```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT NOT NULL,
    project_type TEXT NOT NULL,
    project_details TEXT,
    estimated_budget TEXT,
    estimated_timeline TEXT,
    follow_up_consent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 5. API Endpoints

### 5.1 Health Check

```
GET /api/health
```

Response:
```json
{
  "status": "ok"
}
```

### 5.2 Get Estimates

```
GET /api/estimates?project_type=<project_type>
```

Response:
```json
{
  "project_type": "string",
  "budget_range": "string",
  "typical_timeline": "string"
}
```

### 5.3 Store Lead

```
POST /api/leads
```

Request Body:
```json
{
  "name": "string",
  "contact": "string",
  "project_type": "string",
  "project_details": "string",
  "estimated_budget": "string",
  "estimated_timeline": "string",
  "follow_up_consent": boolean
}
```

Response:
```json
{
  "id": integer,
  "status": "success"
}
```

### 5.4 Get Leads (Admin)

```
GET /api/leads
```

Response:
```json
{
  "leads": [
    {
      "id": integer,
      "name": "string",
      "contact": "string",
      "project_type": "string",
      "project_details": "string",
      "estimated_budget": "string",
      "estimated_timeline": "string",
      "follow_up_consent": boolean,
      "created_at": "string",
      "updated_at": "string"
    }
  ]
}
```

## 6. Implementation Details

### 6.1 Project Structure

```
src/
├── backend/
│   ├── main.py             # Main application entry point (FastAPI)
│   ├── database.py         # Database models and operations
│   ├── tools.py            # Budget & Timeline Tool implementation
│   ├── api.py              # API endpoints
│   ├── utils.py            # Utility functions
│   └── config.py           # Configuration settings
```

### 6.2 Database Operations

#### 6.2.1 Initialize Database

```python
def initialize_database():
    """
    Initialize the database with tables and initial data.
    """
    # Create tables if they don't exist
    # Populate project_estimates table with initial data
```

#### 6.2.2 Store Lead

```python
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
        int: The ID of the newly created lead
    """
    # Insert lead information into the leads table
    # Return the ID of the newly created lead
```

#### 6.2.3 Get Estimate

```python
def get_estimate(project_type):
    """
    Get budget and timeline estimates for a project type.
    
    Args:
        project_type (str): The type of project
        
    Returns:
        dict: A dictionary containing the project_type, budget_range, and typical_timeline
    """
    # Try exact match first
    # If no exact match, try fuzzy matching
    # Return the estimates or a default response
```

### 6.3 FastAPI Implementation

#### 6.3.1 Health Check

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: A dictionary with the status
    """
    return {"status": "ok"}
```

#### 6.3.2 Get Estimates

```python
@app.get("/api/estimates")
async def get_estimates(project_type: str):
    """
    API endpoint to get budget and timeline estimates for a project type.
    
    Args:
        project_type (str): The type of project
        
    Returns:
        dict: A dictionary containing the project_type, budget_range, and typical_timeline
    """
    if not project_type:
        raise HTTPException(status_code=400, detail="Missing project_type parameter")
    
    estimate = get_estimate(project_type)
    if not estimate:
        return {
            "project_type": "unknown",
            "budget_range": "Requires more information",
            "typical_timeline": "Requires more information",
            "message": "We need more details about your project to provide an accurate estimate."
        }
    
    return estimate
```

#### 6.3.3 Store Lead

```python
class Lead(BaseModel):
    name: str
    contact: str
    project_type: str
    project_details: str = None
    estimated_budget: str = None
    estimated_timeline: str = None
    follow_up_consent: bool = False

@app.post("/api/leads")
async def store_lead_api(lead: Lead):
    """
    API endpoint to store lead information.
    
    Args:
        lead (Lead): The lead information
        
    Returns:
        dict: A dictionary with the ID of the newly created lead and the status
    """
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
        raise HTTPException(status_code=500, detail="Failed to store lead")
    
    return {"id": lead_id, "status": "success"}
```

#### 6.3.4 Get Leads (Admin)

```python
@app.get("/api/leads")
async def get_leads():
    """
    API endpoint to get all leads (admin only).
    
    Returns:
        dict: A dictionary containing all leads
    """
    # TODO: Add authentication for admin access
    
    leads = get_all_leads()
    return {"leads": leads}
```

### 6.4 Fuzzy Matching Algorithm

```python
from fuzzywuzzy import fuzz

def fuzzy_match_project_type(project_type, threshold=0.7):
    """
    Match the user's project type to the closest match in the database.
    
    Args:
        project_type (str): The project type provided by the user
        threshold (float): The minimum similarity score to consider a match
        
    Returns:
        str: The matched project type from the database, or None if no match is found
    """
    # Get all project types from the database
    all_project_types = get_all_project_types()
    
    # Calculate similarity scores
    scores = []
    for db_project_type in all_project_types:
        score = fuzz.ratio(project_type.lower(), db_project_type.lower()) / 100.0
        scores.append((db_project_type, score))
    
    # Sort by score in descending order
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return the best match if it's above the threshold
    if scores and scores[0][1] >= threshold:
        return scores[0][0]
    
    return None
```

## 7. Error Handling

### 7.1 API Errors

1. **400 Bad Request**: Missing required parameters or invalid data
2. **404 Not Found**: Resource not found
3. **500 Internal Server Error**: Unexpected server error

### 7.2 Database Errors

1. **Connection Error**: Unable to connect to the database
2. **Query Error**: Error executing a database query
3. **Integrity Error**: Violation of database integrity constraints

### 7.3 Error Responses

```json
{
  "detail": "Error message"
}
```

## 8. Logging

### 8.1 Log Levels

1. **DEBUG**: Detailed information for debugging
2. **INFO**: General information about the application
3. **WARNING**: Warning messages
4. **ERROR**: Error messages
5. **CRITICAL**: Critical error messages

### 8.2 Log Format

```
[TIMESTAMP] [LEVEL] [MODULE] - Message
```

### 8.3 Log Storage

Logs will be stored in a log file with rotation to prevent excessive disk usage.

## 9. Testing

### 9.1 Unit Tests

1. Test database operations
2. Test API endpoints
3. Test Budget & Timeline Tool
4. Test fuzzy matching algorithm

### 9.2 Integration Tests

1. Test the complete backend with mock requests
2. Test database interactions
3. Test error handling

### 9.3 Load Tests

1. Test the backend with multiple concurrent requests
2. Measure response times and resource usage

## 10. Deployment

### 10.1 Environment Variables

```
# Database
DB_PATH=sqlite:///database.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### 10.2 Deployment Options

1. **Development**: Local deployment for development and testing
2. **Production**: Docker containers for production deployment
3. **Scaling**: Consider using a more robust database (PostgreSQL) for production

## 11. Future Enhancements

### 11.1 Authentication

Add authentication for admin access to the leads API.

### 11.2 Dashboard

Create a dashboard for viewing and managing leads.

### 11.3 Email Notifications

Send email notifications for new leads.

### 11.4 Analytics

Track conversation metrics and lead conversion rates.

### 11.5 Multi-language Support

Add support for multiple languages.

### 11.6 Integration with CRM

Integrate with existing CRM systems.

## 12. Conclusion

The Python backend provides a reliable and scalable foundation for the pre-sales chatbot. By handling data storage, retrieval, and API endpoints, it enables the LangFlow conversation flow to focus on the user interaction while ensuring that lead information is securely stored and budget and timeline estimates are consistently provided. 