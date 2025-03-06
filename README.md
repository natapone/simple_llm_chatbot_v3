# Simple LLM Chatbot v3 - Pre-Sales Assistant

A pre-sales chatbot that leverages LangFlow, LiteLLM with OpenAI's GPT-4o-mini model, and Python to engage with potential clients, gather lead information, and provide consistent budget and timeline estimates.

## Features

- **Memory-Enabled Chat**: Maintains conversation history for context-aware responses
- **Budget & Timeline Tool**: Provides accurate estimates based on project type
- **Lead Information Extraction**: Automatically extracts lead information from conversations
- **Markdown Rendering**: Supports rich formatted responses
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode Support**: Includes light/dark mode toggle with system preference detection
- **Multiple Chatbot Options**: Choose between the Memory Chatbot and Presales Chatbot

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/simple_llm_chatbot_v3.git
cd simple_llm_chatbot_v3
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example` and add your API keys:
```
LITELLM_API_KEY=your_openai_api_key
```

## Run Scripts Overview

The project includes several run scripts for different purposes:

| Script | Purpose | Usage |
|--------|---------|-------|
| `run.py` | Runs the FastAPI backend application | Used by other scripts, can be run directly for backend only |
| `run_web_chatbot.py` | Runs the Memory Chatbot web interface and backend | Main entry point for Memory Chatbot |
| `run_presales_chatbot.py` | Runs the Presales Chatbot web interface and backend | Main entry point for Presales Chatbot |
| `run_langflow.py` | Runs LangFlow for editing chatbot flows | Used for flow development and customization |
| `run_tests.py` | Runs all tests in the project | Used for testing and quality assurance |

## Running the Chatbots

### Option 1: Memory Chatbot

The Memory Chatbot is a general-purpose chatbot that maintains conversation history.

```bash
python run_web_chatbot.py
```

This will start:
- The backend API on port 8001
- The Memory Chatbot web interface on port 8000

Access the Memory Chatbot at: http://localhost:8000

### Option 2: Presales Chatbot

The Presales Chatbot is specifically designed for lead generation and providing budget and timeline estimates.

```bash
python run_presales_chatbot.py
```

This will start:
- The backend API on port 8001
- The Presales Chatbot web interface on port 8000

Access the Presales Chatbot at: http://localhost:8000

### Running the Backend API Only

If you need to run just the backend API (for development or testing):

```bash
python run.py
```

This will start:
- The backend API on port 8001 (or the port specified in your .env file)

### Running LangFlow

To run LangFlow for editing the chatbot flows:

```bash
python run_langflow.py
```

Access LangFlow at: http://localhost:7860

## Chatbot Flows

### Memory Chatbot Flow

The Memory Chatbot uses the `LangFlow_Memory_Chatbot.json` flow, which includes:
- Chat Input
- Memory
- Prompt
- OpenAI Model
- Chat Output

### Presales Chatbot Flow

The Presales Chatbot uses the `presales_chatbot_flow.json` flow, which includes:
- Chat Input
- Memory
- System Prompt
- LLM Model
- Budget & Timeline Tool
- Store Lead Tool
- Chat Output

## Documentation

For more detailed documentation, see the `/docs` directory:

- [LangFlow Setup](docs/langflow_setup.md): Instructions for setting up and using LangFlow
- [API Documentation](docs/api/README.md): Documentation for the API endpoints
- [Design Documents](docs/design/README.md): Design documents for the project
- [Development Journey](docs/development_journey.md): Comprehensive chronicle of the project's development process

## Testing

Run the tests with:

```bash
python run_tests.py
```

This will execute all tests in the `tests` directory and display the results.

## Project Maintenance

To keep the project clean and optimized:

```bash
# Remove Python cache files
find ./src -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove temporary files
find . -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" | grep -v "venv" | xargs rm -f
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
