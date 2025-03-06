# Budget & Timeline Tool Technical Specification

## 1. Overview

The Budget & Timeline Tool is a critical component of the pre-sales chatbot system. It provides consistent, database-driven budget and timeline estimates for various project types, ensuring that the chatbot delivers reliable information to potential clients.

## 2. Purpose and Goals

### 2.1 Primary Purpose

To provide accurate and consistent budget and timeline estimates for different project types based on predefined data rather than relying on the LLM to generate estimates.

### 2.2 Goals

1. Ensure consistency in budget and timeline estimates
2. Provide reliable information to potential clients
3. Support the pre-sales process with factual data
4. Handle various project types, including those not explicitly defined in the database

## 3. Technical Specifications

### 3.1 Architecture

The Budget & Timeline Tool is implemented as a Python module that interacts with a database containing predefined project estimates. It exposes a FastAPI endpoint that can be called by LiteLLM during the conversation flow.

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│     LiteLLM   │────▶│  Budget &     │────▶│   Database    │
│ (GPT-4o-mini) │     │ Timeline Tool │     │ (SQLite/SQL)  │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────────────────────────────────────────────────┐
│                      Response to User                      │
└───────────────────────────────────────────────────────────┘
```

### 3.2 Components

#### 3.2.1 Database Schema

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

#### 3.2.2 API Endpoint

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

#### 3.2.3 Fuzzy Matching Algorithm

The tool implements a fuzzy matching algorithm to handle project types that don't exactly match the predefined categories in the database. This ensures that the tool can provide reasonable estimates even when the user's project description doesn't perfectly align with the database entries.

```python
def fuzzy_match_project_type(project_type, threshold=0.7):
    """
    Match the user's project type to the closest match in the database.
    
    Args:
        project_type (str): The project type provided by the user
        threshold (float): The minimum similarity score to consider a match
        
    Returns:
        str: The matched project type from the database, or None if no match is found
    """
    # Implementation details...
```

## 4. Implementation Details

### 4.1 Database Operations

#### 4.1.1 Initialize Database

```python
def initialize_database():
    """
    Initialize the database with tables and initial data.
    """
    # Create tables if they don't exist
    # Populate project_estimates table with initial data
```

#### 4.1.2 Get Estimate

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

### 4.2 FastAPI Implementation

```python
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.get("/api/estimates")
async def get_estimates(project_type: str = Query(..., description="The type of project")):
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

## 5. Error Handling

### 5.1 Missing Project Type

If the project type is not provided, the API returns a 400 Bad Request error with an appropriate error message.

### 5.2 Unknown Project Type

If the project type is not found in the database and cannot be matched using fuzzy matching, the tool returns a default response indicating that the project type is not recognized and suggesting that the user provide more details.

```json
{
  "project_type": "unknown",
  "budget_range": "Requires more information",
  "typical_timeline": "Requires more information",
  "message": "We need more details about your project to provide an accurate estimate."
}
```

## 6. Testing

### 6.1 Unit Tests

1. Test exact matching of project types
2. Test fuzzy matching of project types
3. Test error handling for missing or unknown project types

### 6.2 Integration Tests

1. Test the API endpoint with various project types
2. Test the integration with LiteLLM and GPT-4o-mini

## 7. Future Enhancements

### 7.1 Advanced Matching

Implement more sophisticated matching algorithms, such as semantic similarity using embeddings, to better match user project descriptions to predefined categories.

### 7.2 Dynamic Estimates

Allow for dynamic adjustment of estimates based on additional project parameters, such as complexity, number of features, or specific requirements.

### 7.3 Historical Data

Incorporate historical project data to refine and improve estimates over time.

### 7.4 User Feedback

Collect feedback from users on the accuracy of estimates and use this feedback to improve the tool.

## 8. Conclusion

The Budget & Timeline Tool is a critical component of the pre-sales chatbot system, providing reliable and consistent estimates to potential clients. By using a database-driven approach rather than relying on the LLM to generate estimates, the tool ensures that the information provided to users is accurate and based on factual data. 