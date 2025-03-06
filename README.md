# Simple LLM Chatbot v3 - Pre-Sales Assistant

A pre-sales chatbot that leverages LangFlow, LiteLLM with GPT-4o-mini model, and Python to engage with potential clients, gather lead information, and provide consistent budget and timeline estimates using a database-driven approach.

## Features

- Conversational interface for engaging with potential clients
- Collection of essential lead data (name, contact info, project requirements)
- Database-driven Budget & Timeline Tool for reliable cost and duration estimates
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

5. Edit the .env file with your configuration.

## Usage

### Running the Backend

```bash
cd src/backend
uvicorn main:app --reload
```

### Running LangFlow Locally

```bash
langflow run
```

### Accessing the Chatbot

Open your browser and navigate to:
```
http://localhost:7860
```

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Project Types

To add new project types to the Budget & Timeline Tool, update the project_estimates table in the database:

```python
# Example code to add a new project type
from src.backend.database import add_project_estimate

add_project_estimate(
    project_type="new project type",
    budget_range="$X-$Y",
    typical_timeline="A-B months"
)
```

## License

[MIT License](LICENSE)

## Contributors

- Your Name <your.email@example.com>
