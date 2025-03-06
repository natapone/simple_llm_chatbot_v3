#!/usr/bin/env python3
"""
Web Interface for Presales Chatbot.

This script implements a web interface for the Presales Chatbot using FastAPI and WebSockets.
It loads the LangFlow JSON configuration and uses it to create a chatbot that maintains conversation history
and provides budget and timeline estimates.
"""

import json
import os
import logging
import uuid
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import LangChain components
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Import our tools
from src.backend.tools import BudgetTimelineTool, StoreLeadTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('LITELLM_API_KEY')
if not OPENAI_API_KEY:
    logger.error("LITELLM_API_KEY not found in environment variables")
    raise ValueError("LITELLM_API_KEY not found in environment variables")

# Create FastAPI app
app = FastAPI(title="Presales Chatbot")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Create templates
templates = Jinja2Templates(directory="templates")

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load LangFlow JSON configuration
def load_langflow_config():
    with open("src/langflow/flows/presales_chatbot_flow.json", "r") as file:
        return json.load(file)

# Extract components from LangFlow JSON
def build_chain_from_langflow(flow_config, session_id: str):
    # Find the system prompt
    system_prompt = None
    for node in flow_config["data"]["nodes"]:
        if node["id"] == "system_prompt":
            system_prompt = node["data"]["template"]
            break
    
    if not system_prompt:
        system_prompt = """You are a pre-sales assistant for a software development company. Your role is to:

1. Collect lead information (name, contact, project details)
2. Identify the project type
3. Call the Budget & Timeline Tool for accurate estimates
4. Summarize the conversation
5. Ask for follow-up consent

IMPORTANT GUIDELINES:

1. Be professional, friendly, and helpful at all times.
2. Always collect the client's name and contact information early in the conversation.
3. Ask clarifying questions to understand the project requirements.
4. Do NOT make up budget or timeline estimates. Always use the Budget & Timeline Tool.
5. When the client asks about budget or timeline, call the Budget & Timeline Tool with the project type.
6. Present budget and timeline estimates in a natural way, explaining that these are typical ranges.
7. At the end of the conversation, summarize all collected information in bullet points.
8. Ask for confirmation and follow-up consent.
9. Thank the client for their time and interest."""
    
    # Find the LLM model configuration
    model_name = "gpt-4o-mini"
    temperature = 0.7
    max_tokens = 1024
    
    for node in flow_config["data"]["nodes"]:
        if node["id"] == "llm_model":
            model_name = node["data"]["model_name"]
            temperature = node["data"]["temperature"]
            max_tokens = node["data"]["max_tokens"]
            break
    
    # Create chat message history
    chat_history = ChatMessageHistory()
    
    # Create LLM
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=OPENAI_API_KEY
    )
    
    # Create prompt template
    prompt = PromptTemplate.from_template(
        system_prompt + "\n\nConversation History:\n{memory}\n\nUser: {input}\n\nAI:"
    )
    
    # Create a function to get memory
    def get_memory(input_dict):
        messages = chat_history.messages
        if not messages:
            return ""
        
        # Format messages as a string
        formatted_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                formatted_messages.append(f"User: {message.content}")
            elif isinstance(message, AIMessage):
                formatted_messages.append(f"AI: {message.content}")
        
        return "\n".join(formatted_messages)
    
    # Create tools
    budget_timeline_tool = BudgetTimelineTool()
    store_lead_tool = StoreLeadTool()
    
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
    
    # Return both the chain and chat history
    return {
        "chain": chain, 
        "chat_history": chat_history,
        "tools": {
            "budget_timeline_tool": budget_timeline_tool,
            "store_lead_tool": store_lead_tool
        }
    }

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.chat_chains: Dict[str, object] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # Create a new chain for this client if it doesn't exist
        if client_id not in self.chat_chains:
            flow_config = load_langflow_config()
            self.chat_chains[client_id] = build_chain_from_langflow(flow_config, client_id)
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Keep the chain in memory for now
        # In a production environment, you might want to clean up after some time
    
    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
    
    async def process_message(self, message: str, client_id: str):
        if client_id not in self.chat_chains:
            flow_config = load_langflow_config()
            self.chat_chains[client_id] = build_chain_from_langflow(flow_config, client_id)
        
        chain_data = self.chat_chains[client_id]
        chain = chain_data["chain"]
        chat_history = chain_data["chat_history"]
        tools = chain_data["tools"]
        
        try:
            # Add user message to history
            chat_history.add_user_message(message)
            
            # Check if we need to call a tool
            if "budget" in message.lower() or "timeline" in message.lower() or "estimate" in message.lower() or "cost" in message.lower():
                # Extract project type from the conversation
                project_type = self.extract_project_type(chat_history)
                if project_type:
                    # Call the Budget & Timeline Tool
                    tool_response = tools["budget_timeline_tool"]._run(project_type)
                    # Add tool response to history
                    tool_message = f"I've checked our database for {project_type} projects. Here's what I found:\n\n" \
                                  f"- Budget Range: {tool_response['budget_range']}\n" \
                                  f"- Typical Timeline: {tool_response['typical_timeline']}\n\n" \
                                  f"These are typical ranges based on our past projects. The actual budget and timeline " \
                                  f"may vary depending on your specific requirements."
                    chat_history.add_ai_message(tool_message)
                    return tool_message
            
            # Check if we need to store lead information
            if self.should_store_lead(message, chat_history):
                lead_info = self.extract_lead_info(chat_history)
                if lead_info.get("name") and lead_info.get("contact"):
                    # Call the Store Lead Tool
                    tools["store_lead_tool"]._run(**lead_info)
            
            # Invoke the chain with the input
            response = chain.invoke({"input": message})
            
            # Add AI response to history
            chat_history.add_ai_message(response)
            
            return response
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    def extract_project_type(self, chat_history):
        """Extract project type from conversation history."""
        # Combine all messages into a single string
        all_messages = "\n".join([msg.content for msg in chat_history.messages])
        
        # Look for common project types
        project_types = [
            "e-commerce website", "mobile app", "web application", 
            "desktop application", "API integration", "CRM system",
            "content management system", "database design", "data migration",
            "AI/ML solution", "chatbot", "automation tool"
        ]
        
        for project_type in project_types:
            if project_type.lower() in all_messages.lower():
                return project_type
        
        return None
    
    def should_store_lead(self, message, chat_history):
        """Determine if we should store lead information."""
        # Check if we have enough messages
        if len(chat_history.messages) < 6:
            return False
        
        # Check if the conversation is ending
        ending_phrases = ["thank you", "thanks for your help", "that's all", "goodbye", "bye"]
        for phrase in ending_phrases:
            if phrase in message.lower():
                return True
        
        return False
    
    def extract_lead_info(self, chat_history):
        """Extract lead information from conversation history."""
        all_messages = "\n".join([msg.content for msg in chat_history.messages])
        
        # Initialize lead info
        lead_info = {
            "name": None,
            "contact": None,
            "project_type": None,
            "project_details": None,
            "estimated_budget": None,
            "estimated_timeline": None,
            "follow_up_consent": False
        }
        
        # Extract name (look for patterns like "my name is [name]" or "I'm [name]")
        import re
        name_patterns = [
            r"my name is ([A-Za-z\s]+)",
            r"I'm ([A-Za-z\s]+)",
            r"I am ([A-Za-z\s]+)",
            r"([A-Za-z\s]+) here"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, all_messages, re.IGNORECASE)
            if match:
                lead_info["name"] = match.group(1).strip()
                break
        
        # Extract contact (email or phone)
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        phone_pattern = r"(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
        
        email_match = re.search(email_pattern, all_messages)
        if email_match:
            lead_info["contact"] = email_match.group(0)
        else:
            phone_match = re.search(phone_pattern, all_messages)
            if phone_match:
                lead_info["contact"] = phone_match.group(0)
        
        # Extract project type
        lead_info["project_type"] = self.extract_project_type(chat_history)
        
        # Extract project details (everything after project type mention)
        if lead_info["project_type"]:
            project_type_index = all_messages.lower().find(lead_info["project_type"].lower())
            if project_type_index > 0:
                details_text = all_messages[project_type_index + len(lead_info["project_type"]):]
                # Limit to 500 characters
                lead_info["project_details"] = details_text[:500].strip()
        
        # Check for follow-up consent
        consent_phrases = ["yes, you can follow up", "follow up", "contact me", "reach out"]
        for phrase in consent_phrases:
            if phrase in all_messages.lower():
                lead_info["follow_up_consent"] = True
                break
        
        return lead_info

# Create connection manager
manager = ConnectionManager()

# HTML template for the chat interface
@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    # Create HTML template if it doesn't exist
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Presales Chatbot</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- Add Marked.js for Markdown rendering -->
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            :root {
                --primary-color: #4a6fa5;
                --secondary-color: #e6f7ff;
                --background-color: #f5f5f5;
                --card-background: #ffffff;
                --text-color: #333333;
                --message-user-bg: #e6f7ff;
                --message-bot-bg: #f0f0f0;
                --input-border: #dddddd;
                --code-background: #f8f8f8;
                --accent-color: #5d87c6;
                --success-color: #4caf50;
                --warning-color: #ff9800;
                --error-color: #f44336;
            }
            
            [data-theme="dark"] {
                --primary-color: #5d87c6;
                --secondary-color: #2c3e50;
                --background-color: #1a1a1a;
                --card-background: #2d2d2d;
                --text-color: #f0f0f0;
                --message-user-bg: #2c3e50;
                --message-bot-bg: #3d3d3d;
                --input-border: #444444;
                --code-background: #383838;
                --accent-color: #7fa9e9;
                --success-color: #81c784;
                --warning-color: #ffb74d;
                --error-color: #e57373;
            }
            
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background-color: var(--background-color);
                color: var(--text-color);
                transition: all 0.3s ease;
            }
            
            .chat-container {
                width: 90%;
                max-width: 800px;
                height: 90vh;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                background-color: var(--card-background);
            }
            
            .chat-header {
                background-color: var(--primary-color);
                color: white;
                padding: 15px;
                text-align: center;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .theme-toggle {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                font-size: 1.2rem;
            }
            
            .chat-messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background-color: var(--card-background);
            }
            
            .message {
                margin-bottom: 15px;
                padding: 12px;
                border-radius: 8px;
                max-width: 80%;
                word-wrap: break-word;
                position: relative;
                animation: fadeIn 0.3s ease;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .user-message {
                background-color: var(--message-user-bg);
                margin-left: auto;
                color: var(--text-color);
            }
            
            .bot-message {
                background-color: var(--message-bot-bg);
                margin-right: auto;
                color: var(--text-color);
            }
            
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
            
            .typing-indicator span:nth-child(2) {
                animation-delay: 0.2s;
            }
            
            .typing-indicator span:nth-child(3) {
                animation-delay: 0.4s;
                margin-right: 0;
            }
            
            @keyframes typing {
                0% { transform: translateY(0); }
                50% { transform: translateY(-5px); }
                100% { transform: translateY(0); }
            }
            
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
                color: var(--text-color);
            }
            
            .bot-message ul, .bot-message ol {
                margin-left: 20px;
            }
            
            .bot-message code {
                background-color: var(--code-background);
                padding: 2px 4px;
                border-radius: 3px;
                font-family: monospace;
            }
            
            .bot-message pre {
                background-color: var(--code-background);
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            
            .bot-message table {
                border-collapse: collapse;
                width: 100%;
                margin: 10px 0;
            }
            
            .bot-message th, .bot-message td {
                border: 1px solid var(--input-border);
                padding: 8px;
                text-align: left;
            }
            
            .bot-message th {
                background-color: var(--primary-color);
                color: white;
            }
            
            .chat-input {
                display: flex;
                padding: 15px;
                background-color: var(--card-background);
                border-top: 1px solid var(--input-border);
            }
            
            .chat-input input {
                flex: 1;
                padding: 12px;
                border: 1px solid var(--input-border);
                border-radius: 5px;
                margin-right: 10px;
                background-color: var(--card-background);
                color: var(--text-color);
            }
            
            .chat-input button {
                padding: 12px 20px;
                background-color: var(--primary-color);
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            
            .chat-input button:hover {
                background-color: var(--accent-color);
            }
            
            .error-message {
                background-color: #ffdddd;
                color: #ff0000;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                text-align: center;
                display: none;
            }
            
            /* Welcome message */
            .welcome-message {
                background-color: var(--primary-color);
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
                text-align: center;
            }
            
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
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h2>Presales Assistant</h2>
                <button class="theme-toggle" id="theme-toggle">🌓</button>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="welcome-message">
                    <h3>Welcome to our Presales Assistant!</h3>
                    <p>I'm here to help you with your project needs. I can provide budget and timeline estimates, and collect your information to help our team follow up with you.</p>
                    <p>How can I assist you today?</p>
                </div>
            </div>
            <div class="typing-indicator" id="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div class="error-message" id="error-message">
                An error occurred. <button id="retry-button">Retry</button>
            </div>
            <div class="chat-input">
                <input type="text" id="user-input" placeholder="Type your message here...">
                <button id="send-button">Send</button>
            </div>
        </div>

        <script>
            // Theme toggle functionality
            const themeToggle = document.getElementById('theme-toggle');
            const body = document.body;
            
            // Check for saved theme preference or use preferred color scheme
            const savedTheme = localStorage.getItem('theme') || 
                (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            
            // Apply the theme
            if (savedTheme === 'dark') {
                body.setAttribute('data-theme', 'dark');
            }
            
            // Toggle theme
            themeToggle.addEventListener('click', () => {
                if (body.getAttribute('data-theme') === 'dark') {
                    body.removeAttribute('data-theme');
                    localStorage.setItem('theme', 'light');
                } else {
                    body.setAttribute('data-theme', 'dark');
                    localStorage.setItem('theme', 'dark');
                }
            });
            
            // Generate a unique client ID
            const clientId = Date.now().toString();
            
            // WebSocket connection
            let socket;
            let reconnectAttempts = 0;
            const maxReconnectAttempts = 3;
            
            function connectWebSocket() {
                socket = new WebSocket(`ws://${window.location.host}/ws/${clientId}`);
                
                // WebSocket event handlers
                socket.onopen = () => {
                    console.log('WebSocket connected');
                    document.getElementById('error-message').style.display = 'none';
                    reconnectAttempts = 0;
                };
                
                socket.onmessage = (event) => {
                    document.getElementById('typing-indicator').style.display = 'none';
                    addMessage(event.data, 'bot');
                };
                
                socket.onclose = (event) => {
                    console.log('WebSocket closed:', event);
                    if (reconnectAttempts < maxReconnectAttempts) {
                        reconnectAttempts++;
                        setTimeout(connectWebSocket, 1000 * reconnectAttempts);
                    } else {
                        document.getElementById('error-message').style.display = 'block';
                    }
                };
                
                socket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    document.getElementById('error-message').style.display = 'block';
                };
            }
            
            // Initial connection
            connectWebSocket();
            
            // DOM elements
            const chatMessages = document.getElementById('chat-messages');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            const retryButton = document.getElementById('retry-button');
            const typingIndicator = document.getElementById('typing-indicator');
            
            // Retry connection
            retryButton.addEventListener('click', () => {
                document.getElementById('error-message').style.display = 'none';
                reconnectAttempts = 0;
                connectWebSocket();
            });
            
            // Send message function
            function sendMessage() {
                const message = userInput.value.trim();
                if (message) {
                    // Add user message to chat
                    addMessage(message, 'user');
                    
                    // Show typing indicator
                    typingIndicator.style.display = 'block';
                    
                    // Send message to server if socket is open
                    if (socket.readyState === WebSocket.OPEN) {
                        socket.send(message);
                    } else {
                        document.getElementById('error-message').style.display = 'block';
                        typingIndicator.style.display = 'none';
                    }
                    
                    // Clear input
                    userInput.value = '';
                }
            }
            
            // Add message to chat
            function addMessage(message, sender) {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message');
                messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
                
                // If it's a bot message, render markdown
                if (sender === 'bot') {
                    messageElement.innerHTML = marked.parse(message);
                    
                    // Make links open in new tab
                    const links = messageElement.querySelectorAll('a');
                    links.forEach(link => {
                        link.setAttribute('target', '_blank');
                        link.setAttribute('rel', 'noopener noreferrer');
                    });
                } else {
                    messageElement.textContent = message;
                }
                
                chatMessages.appendChild(messageElement);
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Focus input on page load
            window.onload = () => {
                userInput.focus();
            };
        </script>
    </body>
    </html>
    """
    
    # Write HTML template to file
    with open("templates/presales_chat.html", "w") as file:
        file.write(html_template)
    
    return templates.TemplateResponse("presales_chat.html", {"request": request})

# WebSocket endpoint for chat
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Process message
            response = await manager.process_message(data, client_id)
            
            # Send response back to client
            await manager.send_message(response, client_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")

# Run the app
if __name__ == "__main__":
    logger.info("Starting web interface for Presales Chatbot")
    uvicorn.run(app, host="0.0.0.0", port=8000) 