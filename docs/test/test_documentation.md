# Test Documentation

This document provides information about the testing strategy and test cases for the pre-sales chatbot.

## Testing Strategy

The testing strategy for the pre-sales chatbot includes unit tests, integration tests, and end-to-end tests.

### Unit Tests

Unit tests focus on testing individual components in isolation. These tests ensure that each component functions correctly on its own.

### Integration Tests

Integration tests focus on testing the interaction between components. These tests ensure that the components work together correctly.

### End-to-End Tests

End-to-end tests focus on testing the complete system from the user's perspective. These tests ensure that the system as a whole functions correctly.

## Running Tests

Tests can be run using the `run_tests.py` script:

```bash
python run_tests.py
```

This script uses pytest to run all tests in the `tests` directory and displays the results.

You can also run specific tests by providing the path to the test file:

```bash
python -m pytest tests/test_database.py -v
```

Or run tests with specific markers:

```bash
python -m pytest -m "database" -v
```

## Test Cases

### Unit Tests

#### Database Operations

1. **Test Database Initialization**
   - Verify that the database tables are created correctly
   - Verify that the initial data is inserted correctly

2. **Test Get Estimate**
   - Verify that the correct estimate is returned for a known project type
   - Verify that fuzzy matching works for similar project types
   - Verify that an appropriate response is returned for unknown project types

3. **Test Store Lead**
   - Verify that lead information is stored correctly
   - Verify that required fields are validated
   - Verify that optional fields are handled correctly

#### API Endpoints

1. **Test Health Check Endpoint**
   - Verify that the endpoint returns a 200 status code
   - Verify that the response includes the correct status

2. **Test Get Estimates Endpoint**
   - Verify that the endpoint returns the correct estimate for a known project type
   - Verify that the endpoint returns an appropriate response for an unknown project type
   - Verify that the endpoint returns an error for missing parameters

3. **Test Store Lead Endpoint**
   - Verify that the endpoint stores lead information correctly
   - Verify that the endpoint validates required fields
   - Verify that the endpoint returns an error for missing required fields

4. **Test Get Leads Endpoint**
   - Verify that the endpoint returns all leads
   - Verify that the endpoint returns the correct lead information

#### Budget & Timeline Tool

1. **Test Exact Matching**
   - Verify that the tool returns the correct estimate for an exact match
   - Verify that the tool is case-insensitive

2. **Test Fuzzy Matching**
   - Verify that the tool returns the correct estimate for a similar project type
   - Verify that the tool returns an appropriate response for a project type that is too different

### Integration Tests

1. **Test LangFlow and Python Backend Integration**
   - Verify that LangFlow can call the Python backend API endpoints
   - Verify that the responses are correctly processed by LangFlow

2. **Test Tool Calling**
   - Verify that the Budget & Timeline Tool is called with the correct parameters
   - Verify that the tool's response is correctly processed

### End-to-End Tests

1. **Test Complete Conversation Flow**
   - Verify that the chatbot collects the user's name and contact information
   - Verify that the chatbot collects the project type and details
   - Verify that the chatbot provides budget and timeline estimates
   - Verify that the chatbot summarizes the conversation
   - Verify that the chatbot stores the lead information

2. **Test Error Handling**
   - Verify that the chatbot handles missing information gracefully
   - Verify that the chatbot handles unknown project types gracefully
   - Verify that the chatbot recovers from errors

## Running Tests

### Unit Tests

```bash
pytest tests/unit/
```

### Integration Tests

```bash
pytest tests/integration/
```

### End-to-End Tests

```bash
pytest tests/e2e/
```

### All Tests

```bash
pytest
```

### Test Coverage

```bash
pytest --cov=src
```

## Test Directory Structure

```
tests/
├── unit/                  # Unit tests
│   ├── test_database.py   # Tests for database operations
│   ├── test_api.py        # Tests for API endpoints
│   └── test_tools.py      # Tests for Budget & Timeline Tool
├── integration/           # Integration tests
│   ├── test_langflow.py   # Tests for LangFlow integration
│   └── test_tool_call.py  # Tests for tool calling
└── e2e/                   # End-to-end tests
    └── test_conversation.py  # Tests for complete conversation flow
```

## Test Data

Test data is stored in the `tests/data` directory. This includes:

- Sample project types
- Sample lead information
- Sample conversation flows

## Mocking

External dependencies are mocked in unit and integration tests to ensure that tests are isolated and repeatable.

## Continuous Integration

Tests are run automatically on each commit to the repository using GitHub Actions. The workflow is defined in `.github/workflows/test.yml`. 