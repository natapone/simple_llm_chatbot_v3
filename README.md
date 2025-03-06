# Simple LLM Chatbot v3 - Pre-Sales Assistant

A pre-sales chatbot that leverages LangFlow, LiteLLM with GPT-4o-mini model, and Python to engage with potential clients, gather lead information, and provide consistent budget and timeline estimates using a database-driven approach.

## Features

- Conversational interface for engaging with potential clients
- Collection of essential lead data (name, contact info, project requirements)
- Database-driven Budget & Timeline Tool for reliable cost and duration estimates
- LiteLLM-powered project type extraction for accurate matching
- Lead storage and management for follow-up
- Consistent and fact-based responses

## Project Structure

```
simple_llm_chatbot_v3/
├── brief/                  # Project brief and requirements
├── docs/                   # Documentation
│   ├── design/             # Design documents
│   ├── api/                # API documentation
│   └── test/               # Test documentation
├── src/                    # Source code
│   ├── backend/            # Python backend
│   │   ├── main.py         # Main application entry point (FastAPI)
│   │   ├── database.py     # Database models and operations
│   │   ├── tools.py        # Budget & Timeline Tool implementation
│   │   ├── api.py          # API endpoints
│   │   └── config.py       # Configuration settings
│   ├── langflow/           # LangFlow configuration
│   │   └── flows/          # LangFlow flow definitions
│   └── prompts/            # LLM prompts
├── tests/                  # Test files
│   ├── test_database.py    # Tests for database operations
│   ├── test_tools.py       # Tests for Budget & Timeline Tool
│   └── test_api.py         # Tests for API endpoints
├── run.py                  # Script to run the application
├── run_tests.py            # Script to run the tests
├── .env.example            # Example environment variables
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore file
├── project_info.txt        # Project information and changelog
└── README.md               # Project overview
```

## Requirements

- Python 3.11
- LangFlow (installed and run locally)
- LiteLLM with GPT-4o-mini model
- FastAPI
- SQLite (for MVP)

## Setup

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

4. Create a .env file:
   ```bash
   cp .env.example .env
   ```

5. Edit the .env file with your configuration:
   - Set your LiteLLM API key
   - Set your LangFlow API key
   - Configure other settings as needed

## Usage

### Running the Backend

You can run the backend using the provided run.py script:

```bash
python run.py
```

Or directly with uvicorn:

```bash
uvicorn src.backend.main:app --host 0.0.0.0 --port 8001 --reload
```

### Running LangFlow Locally

```bash
langflow run --host 0.0.0.0 --port 7860
```

### Running the Web Interface

You can run the web interface that loads the LangFlow Memory Chatbot configuration:

```bash
python run_web_chatbot.py
```

This will start both the backend API and the web interface. The web interface will be available at:

```
http://localhost:8000
```

The web interface provides a user-friendly chat experience with memory capabilities, allowing the chatbot to reference previous messages in the conversation.

### Accessing the API

The API will be available at:
```
http://localhost:8001/api
```

API documentation is available at:
```
http://localhost:8001/docs
```

### Accessing the Chatbot

After starting LangFlow, open your browser and navigate to:
```
http://localhost:7860
```

Then import the flow definition from:
```
src/langflow/flows/presales_chatbot_flow.json
```

## Development

### Running Tests

You can run the tests using the provided run_tests.py script:

```bash
python run_tests.py
```

Or directly with pytest:

```bash
pytest tests/
```

### Adding New Project Types

To add new project types to the Budget & Timeline Tool, you can use the Python shell:

```python
from src.backend.database import Session, ProjectEstimate

session = Session()
new_project = ProjectEstimate(
    project_type="new project type",
    budget_range="$X-$Y",
    typical_timeline="A-B months"
)
session.add(new_project)
session.commit()
session.close()
```

## License

[MIT License](LICENSE)

## Contributors

- Your Name <your.email@example.com>
