# LangFlow Setup and Usage Guide

## 1. Introduction

This document provides instructions for setting up and using LangFlow with the pre-sales chatbot. LangFlow is used to design and visualize the conversation flow, integrating with LiteLLM for natural language understanding and the Budget & Timeline Tool for providing estimates.

## 2. Installation

### 2.1 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### 2.2 Installing LangFlow

LangFlow can be installed using pip:

```bash
pip install langflow==1.2.0
```

## 3. Configuration

### 3.1 Environment Variables

LangFlow requires the following environment variables to be set in the `.env` file:

```
# LangFlow
LANGFLOW_API_KEY=your_langflow_api_key
LANGFLOW_HOST=http://localhost
LANGFLOW_PORT=7860
```

### 3.2 Running LangFlow

You can run LangFlow using the provided script:

```bash
python run_langflow.py
```

This script performs the following actions:
1. Registers custom tools with LangFlow (Budget & Timeline Tool, Store Lead Tool)
2. Configures LangFlow with the appropriate host and port settings
3. Starts the LangFlow server

The script automatically handles environment variables and logging, making it the recommended way to run LangFlow for this project.

Alternatively, you can run LangFlow directly with the LangFlow CLI:

```bash
langflow run --host 0.0.0.0 --port 7860
```

However, this method won't register the custom tools automatically.

Once LangFlow is running, you can access the UI at:

```
http://localhost:7860
```

## 4. Importing the Flow Definition

### 4.1 Accessing the LangFlow UI

1. Open your browser and navigate to `http://localhost:7860`
2. Log in with your credentials (if required)

### 4.2 Importing the Flow

1. Click on the "Import" button in the top right corner
2. Select the flow definition file from `src/langflow/flows/presales_chatbot_flow.json`
3. Click "Import"

## 5. Testing the Flow

### 5.1 Running the Backend

Before testing the flow, make sure the backend is running:

```bash
python run.py
```

The backend API will be available at:
```
http://localhost:8001/api
```

### 5.2 Understanding the Flow Structure

The flow consists of the following components:

1. **Chat Input**: Receives user messages from the chat interface
2. **Conversation Memory**: Stores the conversation history
3. **System Prompt**: Provides instructions to the LLM on how to behave as a pre-sales assistant
4. **LLM Model**: The GPT-4o-mini model that processes user inputs and generates responses
5. **Budget & Timeline Tool**: API tool that retrieves budget and timeline estimates for project types
6. **Store Lead Tool**: API tool that stores lead information in the database
7. **Chat Output**: Displays the LLM's responses to the user

The flow is connected as follows:
- User messages go from Chat Input to the LLM Model
- The System Prompt provides instructions to the LLM Model
- The Conversation Memory stores the chat history and provides context to the LLM Model
- The LLM Model can call the Budget & Timeline Tool and Store Lead Tool when needed
- The LLM Model's responses are sent to Chat Output and stored in Conversation Memory

### 5.3 Testing the Conversation Flow

1. In the LangFlow UI, click on the imported flow to open it
2. Click on the "Chat" button in the top right corner
3. Start a conversation with the chatbot
4. Test the following scenarios:
   - Providing name and contact information
   - Describing a project (e.g., "I need an e-commerce website")
   - Receiving budget and timeline estimates
   - Confirming lead information

### 5.4 Verifying Tool Integration

1. Check that the Budget & Timeline Tool is called when the user describes a project
2. Verify that the estimates are displayed correctly
3. Confirm that the lead information is stored in the database

## 6. Troubleshooting

### 6.1 Common Issues

1. **LangFlow not starting**
   - Check that LangFlow is installed correctly
   - Verify that the port is not in use by another application

2. **Tool calls failing**
   - Ensure the backend is running
   - Check the API endpoints are correctly configured in the flow
   - Verify the API keys are set correctly

3. **Flow not loading**
   - Check that the flow definition file is valid JSON
   - Ensure all required nodes and edges are present

### 6.2 Logs

LangFlow logs can be found in the following locations:

- Console output when running LangFlow
- `langflow_logs/` directory (if enabled)

## 7. Advanced Configuration

### 7.1 Custom Nodes

LangFlow supports custom nodes for advanced functionality. To create a custom node:

1. Create a Python file with the node definition
2. Register the node with LangFlow
3. Restart LangFlow to load the custom node

Our project includes custom tool components that are automatically registered with LangFlow when you run the application using `run_langflow.py`. These tools are:

1. **Budget & Timeline Tool**: Gets budget and timeline estimates for a project type
2. **Store Lead Tool**: Stores lead information in the database

The tools are implemented as LangChain tools and registered with LangFlow using the `CustomComponent` API. This allows them to be used directly in the LangFlow UI.

#### Tool Implementation

Our tools are implemented in `src/backend/tools.py` as LangChain `BaseTool` subclasses:

```python
class BudgetTimelineTool(BaseTool):
    """Tool for getting budget and timeline estimates for a project type."""
    name = "budget_timeline_tool"
    description = "Get budget and timeline estimates for a project type"
    args_schema = BudgetTimelineInput
    
    def _run(self, project_type: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[str, Any]:
        """Run the tool."""
        return get_estimate(project_type)
```

#### Tool Registration

The tools are registered with LangFlow in `src/langflow/langflow_tools.py`:

```python
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
```

### 7.2 API Integration

LangFlow can be integrated with external APIs using the Tool nodes. Our custom tools connect to the backend API endpoints:

1. **Budget & Timeline Tool**: Connects to `GET /api/estimates?project_type={project_type}`
2. **Store Lead Tool**: Connects to `POST /api/leads`

The tools handle the API communication internally, so you don't need to configure the API endpoints in the LangFlow UI.

### 7.3 Using Custom Tools in LangFlow

To use our custom tools in LangFlow:

1. Run LangFlow using the provided script: `python run_langflow.py`
2. Open the LangFlow UI at `http://localhost:7860`
3. Create a new flow or open an existing one
4. Search for "Budget & Timeline Tool" or "Store Lead Tool" in the components panel
5. Drag and drop the tools into your flow
6. Connect the tools to an agent component (like ConversationalAgent)
7. Configure the tool parameters as needed

The tools will appear in the "Tools" category in the components panel. They can be connected to any agent component that supports tools, such as ConversationalAgent or OpenAIFunctions.

When an agent uses a tool, it will call the tool's `_run` method with the parameters provided by the agent. The tool will then execute the appropriate logic and return the result to the agent.

## 8. Conclusion

LangFlow provides a powerful visual interface for designing and testing conversation flows. By integrating with the Budget & Timeline Tool, it enables the pre-sales chatbot to provide accurate estimates and collect lead information effectively.

## 9. Web Interface for LangFlow Memory Chatbot

The project includes a web interface that loads the LangFlow Memory Chatbot JSON configuration and provides a user-friendly chat interface.

### 9.1 Running the Web Interface

You can run the web interface using the provided script:

```bash
python run_web_chatbot.py
```

This script will:
1. Start the backend API on port 8001
2. Start the web interface on port 8000

### 9.2 Accessing the Web Interface

Once the web interface is running, you can access it at:

```
http://localhost:8000
```

### 9.3 Features of the Web Interface

The web interface provides the following features:

1. **Memory-Enabled Chat**: The chatbot maintains conversation history, allowing it to reference previous messages.
2. **Real-Time Communication**: Uses WebSockets for real-time communication between the client and server.
3. **Responsive Design**: The interface is responsive and works on desktop and mobile devices, with optimized layouts for different screen sizes.
4. **Dynamic Configuration**: Loads the LangFlow JSON configuration dynamically, allowing for easy updates.
5. **Markdown Rendering**: Supports rendering of Markdown content in bot responses, including headings, lists, code blocks, and images.
6. **Dark Mode Support**: Includes a toggle for light/dark mode with system preference detection and persistent settings.
7. **Loading States**: Visual feedback when messages are being processed with an animated typing indicator.
8. **Error Handling**: Graceful error handling with automatic reconnection attempts and user-friendly error messages.

### 9.4 How It Works

The web interface works by:

1. Loading the LangFlow Memory Chatbot JSON configuration
2. Extracting the prompt template and model configuration
3. Creating a LangChain chain with conversation memory
4. Providing a WebSocket endpoint for real-time communication
5. Maintaining separate conversation contexts for each client

### 9.5 Memory Implementation Details

The memory implementation uses LangChain's ConversationBufferMemory to store and retrieve conversation history. Here's how it works:

1. **Memory Creation**: A ConversationBufferMemory instance is created for each client session.
2. **Memory Integration**: The memory is integrated with the LangChain RunnableSequence to provide conversation context.
3. **Memory Storage**: After each interaction, the user input and AI response are saved to memory.
4. **Memory Retrieval**: When generating a response, the memory is loaded to provide context to the LLM.
5. **Session Management**: Each client has its own memory instance, ensuring conversations don't mix.

Example of how memory is used in the code:

```python
# Create memory
memory = ConversationBufferMemory(
    memory_key="memory",
    return_messages=True,
)

# Create a function to get memory
def get_memory(input_dict):
    memory_dict = memory.load_memory_variables({})
    return memory_dict["memory"]

# Create chain using the modern RunnableSequence approach
chain = (
    {
        "memory": get_memory,
        "input": lambda x: x["input"]
    }
    | prompt
    | llm
    | StrOutputParser()
)

# Save to memory after getting the response
memory.save_context({"input": message}, {"output": response})
```

### 9.6 Customizing the Web Interface

You can customize the web interface by:

1. Modifying the HTML template in `web_interface.py`
2. Updating the CSS styles in the template
3. Adding new features to the JavaScript code
4. Modifying the LangFlow JSON configuration

### 9.7 Markdown Rendering

The web interface includes support for rendering Markdown content in bot responses. This allows the chatbot to provide rich, formatted responses with:

1. **Headings**: Different levels of headings for structured content
2. **Lists**: Ordered and unordered lists
3. **Emphasis**: Bold and italic text
4. **Links**: Clickable hyperlinks
5. **Images**: Embedded images with captions
6. **Code**: Inline code and code blocks with syntax highlighting
7. **Tables**: Structured data in tabular format

The Markdown rendering is implemented using the [marked.js](https://marked.js.org/) library, which is loaded from a CDN. The rendering is applied only to bot messages, while user messages are displayed as plain text.

Example of how Markdown content is rendered:

```javascript
// Add message to chat
function addMessage(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    // If it's a bot message, render markdown
    if (sender === 'bot') {
        messageElement.innerHTML = marked.parse(message);
    } else {
        messageElement.textContent = message;
    }
    
    chatMessages.appendChild(messageElement);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
```

CSS styles are also added to properly display the rendered Markdown elements:

```css
/* Add styles for Markdown content */
.bot-message img {
    max-width: 100%;
    height: auto;
    margin: 10px 0;
    border-radius: 5px;
}
.bot-message h1, .bot-message h2, .bot-message h3, .bot-message h4 {
    margin-top: 10px;
    margin-bottom: 5px;
    color: #333;
}
.bot-message ul, .bot-message ol {
    margin-left: 20px;
}
.bot-message code {
    background-color: #f8f8f8;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: monospace;
}
.bot-message pre {
    background-color: #f8f8f8;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
}
```

This ensures that the chatbot can provide rich, formatted responses that are easy to read and visually appealing.

### 9.8 Responsive Design and Accessibility

The web interface is designed to be responsive and accessible across different devices and screen sizes:

1. **Mobile Optimization**: The layout adjusts for smaller screens, with appropriate sizing and spacing.
2. **Flexible Container**: The chat container uses percentage-based sizing with maximum widths to ensure readability.
3. **Responsive Typography**: Text sizes are set in relative units for better scaling.
4. **Touch-Friendly Controls**: Input fields and buttons are sized appropriately for touch interaction.

Example of responsive design CSS:

```css
/* Responsive design */
@media (max-width: 768px) {
    .chat-container {
        width: 95%;
        height: 95vh;
    }
    
    .message {
        max-width: 90%;
    }
}
```

### 9.9 Dark Mode Implementation

The interface includes a dark mode feature that respects user preferences:

1. **System Preference Detection**: Automatically detects the user's system color scheme preference.
2. **Manual Toggle**: Allows users to override the system preference with a toggle button.
3. **Persistent Settings**: Saves the user's preference in localStorage for future visits.
4. **CSS Variables**: Uses CSS custom properties (variables) for seamless theme switching.

The dark mode implementation uses CSS variables to define color schemes:

```css
:root {
    --primary-color: #4a6fa5;
    --background-color: #f5f5f5;
    --card-background: #ffffff;
    --text-color: #333333;
    /* Other color variables */
}

[data-theme="dark"] {
    --primary-color: #5d87c6;
    --background-color: #1a1a1a;
    --card-background: #2d2d2d;
    --text-color: #f0f0f0;
    /* Dark theme color variables */
}
```

### 9.10 Loading States and Error Handling

The interface provides visual feedback during message processing and handles errors gracefully:

1. **Typing Indicator**: An animated typing indicator shows when the bot is processing a message.
2. **Connection Status**: Visual feedback on WebSocket connection status.
3. **Automatic Reconnection**: Attempts to reconnect automatically if the connection is lost.
4. **Error Messages**: User-friendly error messages with retry options.
5. **Graceful Degradation**: Continues to function with limited capabilities when services are unavailable.

Example of the typing indicator implementation:

```css
.typing-indicator {
    display: none;
    background-color: var(--message-bot-bg);
    margin-right: auto;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.typing-indicator span {
    height: 8px;
    width: 8px;
    background-color: var(--text-color);
    display: inline-block;
    border-radius: 50%;
    margin-right: 5px;
    animation: typing 1s infinite;
}

@keyframes typing {
    0% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
    100% { transform: translateY(0); }
}
```

The error handling includes automatic reconnection attempts:

```javascript
function connectWebSocket() {
    socket = new WebSocket(`ws://${window.location.host}/ws/${clientId}`);
    
    // WebSocket event handlers
    socket.onclose = (event) => {
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            setTimeout(connectWebSocket, 1000 * reconnectAttempts);
        } else {
            document.getElementById('error-message').style.display = 'block';
        }
    };
}
```

## 10. Presales Chatbot Web Interface

The project includes a dedicated web interface for the Presales Chatbot that leverages the LangFlow flow configuration and provides a user-friendly chat experience focused on lead generation and providing budget and timeline estimates.

### 10.1 Running the Presales Chatbot Web Interface

You can run the presales chatbot web interface using the provided script:

```bash
python run_presales_chatbot.py
```

This script will:
1. Start the backend API on port 8001
2. Start the presales web interface on port 8000

### 10.2 Accessing the Presales Chatbot Web Interface

Once the web interface is running, you can access it at:

```
http://localhost:8000
```

### 10.3 Features of the Presales Chatbot Web Interface

The presales chatbot web interface provides the following features:

1. **Memory-Enabled Chat**: The chatbot maintains conversation history, allowing it to reference previous messages.
2. **Real-Time Communication**: Uses WebSockets for real-time communication between the client and server.
3. **Responsive Design**: The interface is responsive and works on desktop and mobile devices, with optimized layouts for different screen sizes.
4. **Dynamic Configuration**: Loads the LangFlow JSON configuration dynamically, allowing for easy updates.
5. **Markdown Rendering**: Supports rendering of Markdown content in bot responses, including headings, lists, code blocks, and images.
6. **Dark Mode Support**: Includes a toggle for light/dark mode with system preference detection and persistent settings.
7. **Loading States**: Visual feedback when messages are being processed with an animated typing indicator.
8. **Error Handling**: Graceful error handling with automatic reconnection attempts and user-friendly error messages.
9. **Tool Integration**: Automatically detects when to call the Budget & Timeline Tool and Store Lead Tool based on conversation context.
10. **Lead Information Extraction**: Extracts lead information (name, contact, project type) from the conversation.

### 10.4 How It Works

The presales chatbot web interface works by:

1. Loading the Presales Chatbot LangFlow JSON configuration
2. Extracting the system prompt and model configuration
3. Creating a LangChain chain with conversation memory
4. Providing a WebSocket endpoint for real-time communication
5. Maintaining separate conversation contexts for each client
6. Automatically detecting when to call tools based on conversation context
7. Extracting lead information from the conversation

### 10.5 Tool Integration

The presales chatbot web interface integrates with the following tools:

1. **Budget & Timeline Tool**: Automatically called when the user asks about budget or timeline estimates. The tool extracts the project type from the conversation and provides accurate estimates.

2. **Store Lead Tool**: Automatically called when the conversation is ending. The tool extracts lead information (name, contact, project type) from the conversation and stores it in the database.

### 10.6 Lead Information Extraction

The presales chatbot web interface extracts the following information from the conversation:

1. **Name**: Extracted from patterns like "my name is [name]" or "I'm [name]"
2. **Contact**: Extracted email addresses or phone numbers
3. **Project Type**: Identified from common project types mentioned in the conversation
4. **Project Details**: Extracted from the context around the project type mention
5. **Follow-up Consent**: Detected from phrases like "yes, you can follow up" or "contact me"

### 10.7 Customizing the Presales Chatbot Web Interface

You can customize the presales chatbot web interface by:

1. Modifying the HTML template in `presales_web_interface.py`
2. Updating the CSS styles in the template
3. Adding new features to the JavaScript code
4. Modifying the LangFlow JSON configuration
5. Updating the tool integration logic in the `ConnectionManager` class 