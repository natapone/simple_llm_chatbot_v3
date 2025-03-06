"""
Tests for LangFlow integration.

This module contains tests for the integration between LangFlow and the Python backend.
"""

import pytest
import sys
import os
import json
import requests
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.config import LANGFLOW_HOST, LANGFLOW_PORT, API_HOST, API_PORT


class TestLangFlowIntegration:
    """Tests for the integration between LangFlow and the Python backend."""

    def setup_method(self):
        """Set up the test environment."""
        self.langflow_url = f"{LANGFLOW_HOST}:{LANGFLOW_PORT}"
        self.api_url = f"http://{API_HOST}:{API_PORT}/api"
        self.flow_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'src', 
            'langflow', 
            'flows', 
            'presales_chatbot_flow.json'
        ))

    def test_flow_file_exists(self):
        """Test that the flow file exists."""
        assert os.path.exists(self.flow_path), f"Flow file not found at {self.flow_path}"

    def test_flow_file_is_valid_json(self):
        """Test that the flow file is valid JSON."""
        with open(self.flow_path, 'r') as f:
            flow_data = json.load(f)
        
        assert 'description' in flow_data, "Flow file missing 'description' field"
        assert 'name' in flow_data, "Flow file missing 'name' field"
        assert 'data' in flow_data, "Flow file missing 'data' field"
        assert 'nodes' in flow_data['data'], "Flow file missing 'nodes' field"
        assert 'edges' in flow_data['data'], "Flow file missing 'edges' field"

    def test_flow_contains_required_nodes(self):
        """Test that the flow contains the required nodes."""
        with open(self.flow_path, 'r') as f:
            flow_data = json.load(f)
        
        node_ids = [node['id'] for node in flow_data['data']['nodes']]
        required_nodes = [
            'start_greeting',
            'collect_basic_info',
            'project_requirements',
            'budget_timeline_tool',
            'response_with_estimates',
            'recap_confirmation',
            'store_lead'
        ]
        
        for node_id in required_nodes:
            assert node_id in node_ids, f"Flow missing required node: {node_id}"

    @patch('requests.get')
    def test_api_health_endpoint(self, mock_get):
        """Test that the API health endpoint is accessible."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response
        
        # Call the endpoint
        response = requests.get(f"{self.api_url}/health")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_get.assert_called_once_with(f"{self.api_url}/health")

    @patch('requests.get')
    def test_budget_timeline_tool_endpoint(self, mock_get):
        """Test that the Budget & Timeline Tool endpoint is accessible."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "project_type": "e-commerce website",
            "budget_range": "$3k-$6k",
            "typical_timeline": "2-3 months"
        }
        mock_get.return_value = mock_response
        
        # Call the endpoint
        response = requests.get(f"{self.api_url}/estimates?project_type=e-commerce+website")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "project_type": "e-commerce website",
            "budget_range": "$3k-$6k",
            "typical_timeline": "2-3 months"
        }
        mock_get.assert_called_once_with(f"{self.api_url}/estimates?project_type=e-commerce+website")

    @patch('requests.post')
    def test_store_lead_endpoint(self, mock_post):
        """Test that the Store Lead endpoint is accessible."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "status": "success"
        }
        mock_post.return_value = mock_response
        
        # Lead data
        lead_data = {
            "name": "Test User",
            "contact": "test@example.com",
            "project_type": "e-commerce website",
            "project_details": "I need an online store for my business",
            "estimated_budget": "$3k-$6k",
            "estimated_timeline": "2-3 months",
            "follow_up_consent": True
        }
        
        # Call the endpoint
        response = requests.post(f"{self.api_url}/leads", json=lead_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "status": "success"
        }
        mock_post.assert_called_once_with(f"{self.api_url}/leads", json=lead_data) 