# Pre-Sales Chatbot Implementation Design

## 1. Overview

This document outlines the detailed implementation design for the pre-sales chatbot that leverages LangFlow, LiteLLM with OpenAI's GPT-4o-mini model, and Python 3.11 with a database-driven Budget & Timeline Tool. The chatbot will engage potential clients, collect lead information, and provide consistent budget and timeline estimates.

## 2. System Architecture

### 2.1 High-Level Architecture

```
   ┌──────────────┐
   │   Front-End   │ (Web or LangFlow UI)
   └──────┬───────┘
          │
          │ (User messages)
          ▼
   ┌───────────────────┐
   │   LangFlow (Flow) │
   │  + LiteLLM (GPT-4o-mini) │
   └──────┬───────┬────┘
          │       │ (Tool Call)
          │       ▼
          │  ┌───────────────────┐
          │  │   Budget &       │
          │  │ Timeline Tool    │
          │  │ (Python + DB)    │
          │  └───────────────────┘
          │         (Estimates)
          ▼
   ┌────────────────────┐
   │   Python Backend   │
   │  (Lead Storage)    │
   └────────────────────┘
```

### 2.2 Component Interactions

1. **User → LangFlow**: User interacts with the chatbot through a web interface.
2. **LangFlow → LiteLLM**: LangFlow processes the conversation flow and uses LiteLLM with GPT-4o-mini for natural language understanding.
3. **LiteLLM → Budget & Timeline Tool**: When budget/timeline estimates are needed, LiteLLM calls the Budget & Timeline Tool.
4. **Budget & Timeline Tool → Database**: The tool retrieves estimates from a database.
5. **LiteLLM → Python Backend**: Lead information is stored in the backend database.

## 3. Component Specifications

### 3.1 Database Schema

#### 3.1.1 Project Estimates Table

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

Initial data:

| project_type          | budget_range | typical_timeline |
|-----------------------|--------------|------------------|
| e-commerce website    | $3k–$6k      | 2–3 months       |
| mobile restaurant app | $5k–$8k      | 3–4 months       |
| CRM system            | $4k–$7k      | 4–6 months       |
| chatbot integration   | $2k–$4k      | 2–3 months       |
| custom logistics      | $10k–$20k    | 5–6 months       |

#### 3.1.2 Leads Table

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

### 3.2 Python Backend (FastAPI)

#### 3.2.1 API Endpoints

1. **GET /api/health**
   - Description: Health check endpoint
   - Response: `{"status": "ok"}`

2. **POST /api/leads**
   - Description: Store lead information
   - Request Body:
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
   - Response: `{"id": integer, "status": "success"}`

3. **GET /api/estimates**
   - Description: Get budget and timeline estimates for a project type
   - Query Parameters: `project_type=string`
   - Response:
     ```json
     {
       "project_type": "string",
       "budget_range": "string",
       "typical_timeline": "string"
     }
     ```

#### 3.2.2 Database Operations

1. **Initialize Database**
   - Create tables if they don't exist
   - Populate project_estimates table with initial data

2. **Store Lead**
   - Insert lead information into the leads table

3. **Get Estimate**
   - Retrieve budget and timeline estimates for a given project type
   - Handle fuzzy matching for project types not exactly matching the database entries

### 3.3 LangFlow Configuration

#### 3.3.1 Conversation Flow Nodes

1. **Start / Greeting Node**
   - System prompt: "You are a pre-sales assistant for a software development company. Your goal is to collect lead information and provide budget and timeline estimates."
   - Initial message: "Hi there! I'm your pre-sales assistant. May I have your name and the best way to reach you?"

2. **Collect Basic Info Node**
   - Extract and store user's name and contact information
   - Transition to project requirements

3. **Project Requirements Node**
   - Prompt: "Thanks, [Name]! Can you tell me about your project?"
   - Extract project type and details

4. **Budget & Timeline Tool Call Node**
   - Call the Budget & Timeline Tool with the extracted project type
   - Format: `GET /api/estimates?project_type=[project_type]`

5. **Response with Estimates Node**
   - Present the budget and timeline estimates to the user
   - Ask for confirmation or clarification

6. **Recap & Confirmation Node**
   - Summarize all collected information in bullet points
   - Ask for confirmation and follow-up consent

7. **Store Lead & End Node**
   - Store lead information in the database
   - Thank the user and end the conversation

#### 3.3.2 LiteLLM Configuration

1. **System Prompt**:
   ```
   You are a pre-sales assistant for a software development company. Your role is to:
   1. Collect lead information (name, contact, project details)
   2. Identify the project type
   3. Call the Budget & Timeline Tool for accurate estimates
   4. Summarize the conversation
   5. Ask for follow-up consent

   IMPORTANT: Do NOT make up budget or timeline estimates. Always use the Budget & Timeline Tool.
   ```

2. **Model Configuration**:
   - Model: `gpt-4o-mini`
   - Provider: OpenAI (via LiteLLM)
   - Temperature: 0.7
   - Max tokens: 1024

3. **Tool Definition**:
   ```json
   {
     "name": "BudgetTimelineTool",
     "description": "Get budget and timeline estimates for a project type",
     "parameters": {
       "type": "object",
       "properties": {
         "project_type": {
           "type": "string",
           "description": "The type of project (e.g., e-commerce website, mobile app)"
         }
       },
       "required": ["project_type"]
     }
   }
   ```

## 4. Implementation Plan

### 4.1 Phase 1: Setup and Basic Structure

1. Create project directory structure
2. Set up Python 3.11 virtual environment
3. Install required dependencies (FastAPI, SQLAlchemy, LiteLLM, etc.)
4. Create database schema and initialization script
5. Implement basic API endpoints with FastAPI

### 4.2 Phase 2: Budget & Timeline Tool

1. Implement the Budget & Timeline Tool
2. Create database with initial project estimates
3. Implement fuzzy matching for project types
4. Test the tool with various project types

### 4.3 Phase 3: LangFlow Configuration

1. Set up LangFlow
2. Configure conversation flow nodes
3. Implement tool calling mechanism with LiteLLM using GPT-4o-mini
4. Test the conversation flow

### 4.4 Phase 4: Integration and Testing

1. Integrate all components
2. Test end-to-end conversation flow
3. Verify lead storage
4. Optimize performance and reliability

## 5. Testing Strategy

### 5.1 Unit Tests

1. Test database operations
2. Test API endpoints
3. Test Budget & Timeline Tool
4. Test fuzzy matching algorithm

### 5.2 Integration Tests

1. Test LangFlow and LiteLLM integration
2. Test tool calling mechanism
3. Test lead storage

### 5.3 End-to-End Tests

1. Test complete conversation flow
2. Verify budget and timeline estimates
3. Verify lead storage

## 6. Deployment Considerations

### 6.1 Environment Variables

```
# Database
DB_PATH=sqlite:///database.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# LangFlow
LANGFLOW_API_KEY=your_langflow_api_key

# LiteLLM
LITELLM_API_KEY=your_openai_api_key
LITELLM_MODEL=gpt-4o-mini
```

### 6.2 Deployment Options

1. **Development**: Local deployment for development and testing
2. **Production**: Docker containers for each component
3. **Scaling**: Consider using a more robust database (PostgreSQL) for production

## 7. Future Enhancements

1. **User Authentication**: Add user authentication for accessing the admin panel
2. **Dashboard**: Create a dashboard for viewing and managing leads
3. **Email Notifications**: Send email notifications for new leads
4. **Analytics**: Track conversation metrics and lead conversion rates
5. **Multi-language Support**: Add support for multiple languages
6. **Integration with CRM**: Integrate with existing CRM systems 