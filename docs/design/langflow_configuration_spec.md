# LangFlow Configuration Technical Specification

## 1. Overview

This document outlines the technical specifications for configuring LangFlow to implement the pre-sales chatbot. LangFlow will be used to design and visualize the conversation flow, integrating with LiteLLM (using GPT-4o-mini) for natural language understanding and the Budget & Timeline Tool for providing estimates.

## 2. Purpose and Goals

### 2.1 Primary Purpose

To create a structured, visual representation of the conversation flow that guides the interaction between the user and the pre-sales chatbot, ensuring a smooth and effective lead collection process.

### 2.2 Goals

1. Create a natural and engaging conversation flow
2. Collect essential lead information (name, contact, project details)
3. Integrate with the Budget & Timeline Tool for accurate estimates
4. Provide a consistent user experience
5. Store lead information for follow-up

## 3. LangFlow Components

### 3.1 Nodes

#### 3.1.1 Start / Greeting Node

- **Type**: LLM Node
- **Input**: None
- **Output**: Initial greeting message
- **Configuration**:
  - System Prompt: "You are a pre-sales assistant for a software development company. Your goal is to collect lead information and provide budget and timeline estimates."
  - Initial Message: "Hi there! I'm your pre-sales assistant. May I have your name and the best way to reach you?"

#### 3.1.2 Collect Basic Info Node

- **Type**: LLM Node
- **Input**: User response to greeting
- **Output**: Acknowledgment and request for project details
- **Configuration**:
  - System Prompt: "Extract the user's name and contact information from their response. Then, ask about their project."
  - Memory: Store user's name and contact information

#### 3.1.3 Project Requirements Node

- **Type**: LLM Node
- **Input**: User's project description
- **Output**: Follow-up questions to clarify project details
- **Configuration**:
  - System Prompt: "Extract the project type and details from the user's response. Ask follow-up questions to clarify if needed."
  - Memory: Store project type and details

#### 3.1.4 Budget & Timeline Tool Call Node

- **Type**: Tool Node
- **Input**: Project type from memory
- **Output**: Budget and timeline estimates
- **Configuration**:
  - Tool Name: "BudgetTimelineTool"
  - API Endpoint: "GET /api/estimates?project_type={project_type}"
  - Parameters: project_type (from memory)

#### 3.1.5 Response with Estimates Node

- **Type**: LLM Node
- **Input**: Budget and timeline estimates from the tool
- **Output**: Natural language response with estimates
- **Configuration**:
  - System Prompt: "Present the budget and timeline estimates to the user in a natural way. Ask if the estimates align with their expectations."
  - Memory: Store budget and timeline estimates

#### 3.1.6 Recap & Confirmation Node

- **Type**: LLM Node
- **Input**: User's response to estimates
- **Output**: Summary of collected information and request for follow-up consent
- **Configuration**:
  - System Prompt: "Summarize all collected information in bullet points. Ask for confirmation and follow-up consent."
  - Memory: Store follow-up consent

#### 3.1.7 Store Lead & End Node

- **Type**: Tool Node
- **Input**: All collected information from memory
- **Output**: Confirmation of lead storage
- **Configuration**:
  - Tool Name: "StoreLead"
  - API Endpoint: "POST /api/leads"
  - Parameters: name, contact, project_type, project_details, estimated_budget, estimated_timeline, follow_up_consent

### 3.2 Edges

1. **Start / Greeting Node → Collect Basic Info Node**
   - Condition: User responds with name and contact information

2. **Collect Basic Info Node → Project Requirements Node**
   - Condition: User provides project details

3. **Project Requirements Node → Budget & Timeline Tool Call Node**
   - Condition: Project type is identified

4. **Budget & Timeline Tool Call Node → Response with Estimates Node**
   - Condition: Estimates are retrieved from the tool

5. **Response with Estimates Node → Recap & Confirmation Node**
   - Condition: User acknowledges the estimates

6. **Recap & Confirmation Node → Store Lead & End Node**
   - Condition: User confirms the information and provides follow-up consent

## 4. LiteLLM Integration

### 4.1 System Prompt

```
You are a pre-sales assistant for a software development company. Your role is to:
1. Collect lead information (name, contact, project details)
2. Identify the project type
3. Call the Budget & Timeline Tool for accurate estimates
4. Summarize the conversation
5. Ask for follow-up consent

IMPORTANT: Do NOT make up budget or timeline estimates. Always use the Budget & Timeline Tool.
```

### 4.2 LiteLLM Configuration

```python
from litellm import completion

# Configure LiteLLM
litellm_config = {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 1024,
    "api_key": os.getenv("LITELLM_API_KEY")
}

# Example function to generate a response
def generate_response(prompt, system_message, tools=None):
    response = completion(
        model=litellm_config["model"],
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        temperature=litellm_config["temperature"],
        max_tokens=litellm_config["max_tokens"],
        tools=tools
    )
    return response
```

### 4.3 Tool Definition

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

```json
{
  "name": "StoreLead",
  "description": "Store lead information in the database",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "The name of the lead"
      },
      "contact": {
        "type": "string",
        "description": "The contact information of the lead"
      },
      "project_type": {
        "type": "string",
        "description": "The type of project"
      },
      "project_details": {
        "type": "string",
        "description": "Additional details about the project"
      },
      "estimated_budget": {
        "type": "string",
        "description": "The estimated budget range"
      },
      "estimated_timeline": {
        "type": "string",
        "description": "The estimated timeline"
      },
      "follow_up_consent": {
        "type": "boolean",
        "description": "Whether the lead has consented to follow-up"
      }
    },
    "required": ["name", "contact", "project_type"]
  }
}
```

## 5. Memory Management

### 5.1 Memory Variables

1. **user_name**: The name of the user
2. **user_contact**: The contact information of the user
3. **project_type**: The type of project
4. **project_details**: Additional details about the project
5. **estimated_budget**: The estimated budget range
6. **estimated_timeline**: The estimated timeline
7. **follow_up_consent**: Whether the user has consented to follow-up

### 5.2 Memory Operations

1. **Set Memory**: Store values in memory
2. **Get Memory**: Retrieve values from memory
3. **Clear Memory**: Clear all memory variables at the end of the conversation

## 6. Error Handling

### 6.1 Missing Information

If the user does not provide essential information (name, contact, project details), the chatbot should politely ask for the missing information again.

### 6.2 Tool Failure

If the Budget & Timeline Tool fails to provide estimates, the chatbot should inform the user that it cannot provide estimates at the moment and offer to follow up later.

### 6.3 Conversation Restart

If the conversation gets off track or the user wants to start over, the chatbot should provide a way to restart the conversation.

## 7. Testing

### 7.1 Unit Tests

1. Test each node individually with sample inputs
2. Verify that memory variables are correctly set and retrieved
3. Test tool integration with mock responses

### 7.2 Integration Tests

1. Test the complete conversation flow with various scenarios
2. Verify that the chatbot handles different user responses appropriately
3. Test error handling and recovery

### 7.3 User Testing

1. Conduct user testing with sample conversations
2. Gather feedback on the conversation flow and user experience
3. Refine the flow based on feedback

## 8. Deployment

### 8.1 LangFlow Export

Export the LangFlow configuration as a JSON file for deployment.

### 8.2 Environment Variables

```
# LangFlow
LANGFLOW_API_KEY=your_langflow_api_key

# LiteLLM
LITELLM_API_KEY=your_openai_api_key
LITELLM_MODEL=gpt-4o-mini
```

### 8.3 Deployment Steps

1. Import the LangFlow configuration into the LangFlow instance
2. Configure the API endpoints for the Budget & Timeline Tool and lead storage
3. Test the deployed flow with sample conversations

## 9. Future Enhancements

### 9.1 Multi-language Support

Add support for multiple languages by detecting the user's language and using appropriate prompts.

### 9.2 Conversation Branching

Implement more complex conversation branching based on user responses and project types.

### 9.3 Integration with CRM

Integrate with existing CRM systems to automatically create leads and follow-up tasks.

### 9.4 Analytics

Add analytics to track conversation metrics and lead conversion rates.

## 10. Conclusion

The LangFlow configuration provides a structured and visual representation of the conversation flow for the pre-sales chatbot. By integrating with LiteLLM (using GPT-4o-mini) for natural language understanding and the Budget & Timeline Tool for accurate estimates, the chatbot can effectively collect lead information and provide consistent budget and timeline estimates. 