#!/usr/bin/env python3
"""
Web Interface for LangFlow Memory Chatbot.

This script implements a web interface for the LangFlow Memory Chatbot using FastAPI and WebSockets.
It loads the LangFlow JSON configuration and uses it to create a chatbot that maintains conversation history.
"""

import json
import os
import logging
import uuid
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# Import LangChain components
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

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
app = FastAPI(title="LangFlow Memory Chatbot")

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
    with open("src/langflow/flows/LangFlow_Memory_Chatbot.json", "r") as file:
        return json.load(file)

# Extract components from LangFlow JSON
def build_chain_from_langflow(flow_config, session_id: str):
    # Find the prompt template
    prompt_template = None
    for node in flow_config["data"]["nodes"]:
        if node["type"] == "Prompt":
            prompt_template = node["data"]["node"]["template"]["template"]["value"]
            break
    
    if not prompt_template:
        prompt_template = "You are a helpful assistant that answers questions.\n\nUse markdown to format your answer, properly embedding images and urls.\n\nHistory: \n\n{memory}\n"
    
    # Create prompt template
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Find the OpenAI model configuration
    model_name = "gpt-4o-mini"
    temperature = 0.1
    
    for node in flow_config["data"]["nodes"]:
        if node["type"] == "OpenAIModel":
            model_name = node["data"]["node"]["template"]["model_name"]["value"]
            temperature = node["data"]["node"]["template"]["temperature"]["value"]
            break
    
    # Create chat message history instead of ConversationBufferMemory
    chat_history = ChatMessageHistory()
    
    # Create LLM
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        api_key=OPENAI_API_KEY
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
                formatted_messages.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                formatted_messages.append(f"AI: {message.content}")
        
        return "\n".join(formatted_messages)
    
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
    return {"chain": chain, "chat_history": chat_history}

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
        
        try:
            # Add user message to history
            chat_history.add_user_message(message)
            
            # Invoke the chain with the input
            response = chain.invoke({"input": message})
            
            # Add AI response to history
            chat_history.add_ai_message(response)
            
            return response
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I'm sorry, I encountered an error: {str(e)}"

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
        <title>LangFlow Memory Chatbot</title>
        <!-- Add Marked.js for Markdown rendering -->
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #f5f5f5;
            }
            .chat-container {
                width: 80%;
                max-width: 800px;
                height: 80vh;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
            }
            .chat-header {
                background-color: #4a6fa5;
                color: white;
                padding: 15px;
                text-align: center;
            }
            .chat-messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background-color: white;
            }
            .message {
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 5px;
                max-width: 70%;
            }
            .user-message {
                background-color: #e6f7ff;
                margin-left: auto;
            }
            .bot-message {
                background-color: #f0f0f0;
                margin-right: auto;
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
            .chat-input {
                display: flex;
                padding: 10px;
                background-color: #f9f9f9;
            }
            .chat-input input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-right: 10px;
            }
            .chat-input button {
                padding: 10px 15px;
                background-color: #4a6fa5;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h2>LangFlow Memory Chatbot</h2>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="message bot-message">
                    Hi there! I'm your memory-enabled assistant. How can I help you today?
                </div>
            </div>
            <div class="chat-input">
                <input type="text" id="user-input" placeholder="Type your message here...">
                <button id="send-button">Send</button>
            </div>
        </div>

        <script>
            // Generate a unique client ID
            const clientId = Date.now().toString();
            
            // WebSocket connection
            const socket = new WebSocket(`ws://${window.location.host}/ws/${clientId}`);
            
            // DOM elements
            const chatMessages = document.getElementById('chat-messages');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            
            // Send message function
            function sendMessage() {
                const message = userInput.value.trim();
                if (message) {
                    // Add user message to chat
                    addMessage(message, 'user');
                    
                    // Send message to server
                    socket.send(message);
                    
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
            
            // WebSocket event handlers
            socket.onmessage = (event) => {
                addMessage(event.data, 'bot');
            };
            
            socket.onclose = () => {
                addMessage('Connection closed. Please refresh the page.', 'bot');
            };
            
            socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                addMessage('Error connecting to the server.', 'bot');
            };
        </script>
    </body>
    </html>
    """
    
    # Write HTML template to file
    with open("templates/chat.html", "w") as file:
        file.write(html_template)
    
    return templates.TemplateResponse("chat.html", {"request": request})

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
    logger.info("Starting web interface for LangFlow Memory Chatbot")
    uvicorn.run(app, host="0.0.0.0", port=8000) 