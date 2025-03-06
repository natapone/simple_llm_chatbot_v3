"""
Tests for the API endpoints.

This module contains tests for the API endpoints.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.main import app
from src.backend.api import LeadCreate

# Create a test client
client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the health endpoint."""

    def test_health_check(self):
        """Test that the health check endpoint returns a 200 status code."""
        # Act
        response = client.get("/api/health")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestEstimatesEndpoint:
    """Tests for the estimates endpoint."""

    @patch('src.backend.api.get_estimate')
    def test_get_estimates_success(self, mock_get_estimate):
        """Test that the estimates endpoint returns the correct estimate."""
        # Arrange
        mock_estimate = {
            'project_type': 'e-commerce website',
            'budget_range': '$3k-$6k',
            'typical_timeline': '2-3 months'
        }
        mock_get_estimate.return_value = mock_estimate
        
        # Act
        response = client.get("/api/estimates?project_type=e-commerce%20website")
        
        # Assert
        assert response.status_code == 200
        # The API adds a message field with None as default
        expected_response = mock_estimate.copy()
        expected_response['message'] = None
        assert response.json() == expected_response
        mock_get_estimate.assert_called_once_with('e-commerce website')

    @patch('src.backend.api.get_estimate')
    def test_get_estimates_no_match(self, mock_get_estimate):
        """Test that the estimates endpoint returns a default response when no match is found."""
        # Arrange
        mock_estimate = {
            'project_type': 'unknown',
            'budget_range': 'Requires more information',
            'typical_timeline': 'Requires more information',
            'message': 'We need more details about your project to provide an accurate estimate.'
        }
        mock_get_estimate.return_value = mock_estimate
        
        # Act
        response = client.get("/api/estimates?project_type=something%20completely%20different")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_estimate
        mock_get_estimate.assert_called_once_with('something completely different')

    def test_get_estimates_missing_parameter(self):
        """Test that the estimates endpoint returns a 422 status code when the project_type parameter is missing."""
        # Act
        response = client.get("/api/estimates")
        
        # Assert
        assert response.status_code == 422
        assert 'detail' in response.json()


class TestLeadsEndpoint:
    """Tests for the leads endpoint."""

    @patch('src.backend.api.store_lead')
    def test_create_lead_success(self, mock_store_lead):
        """Test that the leads endpoint successfully creates a lead."""
        # Arrange
        mock_store_lead.return_value = 1
        lead_data = {
            'name': 'John Doe',
            'contact': 'john.doe@example.com',
            'project_type': 'e-commerce website',
            'project_details': 'I need an online store for my business.',
            'estimated_budget': '$3k-$6k',
            'estimated_timeline': '2-3 months',
            'follow_up_consent': True
        }
        
        # Act
        response = client.post("/api/leads", json=lead_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {'id': 1, 'status': 'success'}
        mock_store_lead.assert_called_once_with(
            name='John Doe',
            contact='john.doe@example.com',
            project_type='e-commerce website',
            project_details='I need an online store for my business.',
            estimated_budget='$3k-$6k',
            estimated_timeline='2-3 months',
            follow_up_consent=True
        )

    @patch('src.backend.api.store_lead')
    def test_create_lead_failure(self, mock_store_lead):
        """Test that the leads endpoint returns a 500 status code when the lead creation fails."""
        # Arrange
        mock_store_lead.return_value = None
        lead_data = {
            'name': 'John Doe',
            'contact': 'john.doe@example.com',
            'project_type': 'e-commerce website'
        }
        
        # Act
        response = client.post("/api/leads", json=lead_data)
        
        # Assert
        assert response.status_code == 500
        assert 'detail' in response.json()
        mock_store_lead.assert_called_once()

    def test_create_lead_missing_required_fields(self):
        """Test that the leads endpoint returns a 422 status code when required fields are missing."""
        # Arrange
        lead_data = {
            'name': 'John Doe',
            'project_type': 'e-commerce website'
            # Missing 'contact' field
        }
        
        # Act
        response = client.post("/api/leads", json=lead_data)
        
        # Assert
        assert response.status_code == 422
        assert 'detail' in response.json()

    @patch('src.backend.api.get_all_leads')
    def test_get_leads_success(self, mock_get_all_leads):
        """Test that the leads endpoint successfully returns all leads."""
        # Arrange
        mock_leads = [
            {
                'id': 1,
                'name': 'John Doe',
                'contact': 'john.doe@example.com',
                'project_type': 'e-commerce website',
                'project_details': 'I need an online store for my business.',
                'estimated_budget': '$3k-$6k',
                'estimated_timeline': '2-3 months',
                'follow_up_consent': True,
                'created_at': '2023-01-01T00:00:00',
                'updated_at': '2023-01-01T00:00:00'
            }
        ]
        mock_get_all_leads.return_value = mock_leads
        
        # Act
        response = client.get("/api/leads")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {'leads': mock_leads}
        mock_get_all_leads.assert_called_once()

    @patch('src.backend.api.get_all_leads')
    def test_get_leads_failure(self, mock_get_all_leads):
        """Test that the leads endpoint returns a 500 status code when the leads retrieval fails."""
        # Arrange
        mock_get_all_leads.return_value = None
        
        # Act
        response = client.get("/api/leads")
        
        # Assert
        assert response.status_code == 500
        assert 'detail' in response.json()
        mock_get_all_leads.assert_called_once() 