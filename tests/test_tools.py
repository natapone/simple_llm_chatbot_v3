"""
Tests for the Budget & Timeline Tool.

This module contains tests for the Budget & Timeline Tool.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.backend.tools import extract_project_type, get_estimate


class TestExtractProjectType:
    """Tests for the extract_project_type function."""

    @patch('src.backend.tools.get_all_project_types')
    @patch('src.backend.tools.completion')
    def test_exact_match(self, mock_completion, mock_get_all_project_types):
        """Test that an exact match returns the correct project type."""
        # Arrange
        mock_get_all_project_types.return_value = [
            'e-commerce website',
            'mobile restaurant app',
            'CRM system',
            'chatbot integration',
            'custom logistics'
        ]
        
        # Mock the LiteLLM response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "e-commerce website"
        mock_completion.return_value = mock_response
        
        # Act
        result = extract_project_type("I need an online shop for my business")
        
        # Assert
        assert result == 'e-commerce website'
        mock_get_all_project_types.assert_called_once()
        mock_completion.assert_called_once()

    @patch('src.backend.tools.get_all_project_types')
    @patch('src.backend.tools.completion')
    def test_no_match(self, mock_completion, mock_get_all_project_types):
        """Test that no match returns None."""
        # Arrange
        mock_get_all_project_types.return_value = [
            'e-commerce website',
            'mobile restaurant app',
            'CRM system',
            'chatbot integration',
            'custom logistics'
        ]
        
        # Mock the LiteLLM response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "unknown"
        mock_completion.return_value = mock_response
        
        # Act
        result = extract_project_type("I need something completely different")
        
        # Assert
        assert result is None
        mock_get_all_project_types.assert_called_once()
        mock_completion.assert_called_once()

    @patch('src.backend.tools.get_all_project_types')
    def test_empty_project_types(self, mock_get_all_project_types):
        """Test that empty project types returns None."""
        # Arrange
        mock_get_all_project_types.return_value = []
        
        # Act
        result = extract_project_type("I need an online shop")
        
        # Assert
        assert result is None
        mock_get_all_project_types.assert_called_once()

    @patch('src.backend.tools.get_all_project_types')
    @patch('src.backend.tools.completion')
    def test_exception_handling(self, mock_completion, mock_get_all_project_types):
        """Test that exceptions are handled properly."""
        # Arrange
        mock_get_all_project_types.return_value = [
            'e-commerce website',
            'mobile restaurant app',
            'CRM system',
            'chatbot integration',
            'custom logistics'
        ]
        
        # Mock the LiteLLM response to raise an exception
        mock_completion.side_effect = Exception("Test exception")
        
        # Act
        result = extract_project_type("I need an online shop")
        
        # Assert
        assert result is None
        mock_get_all_project_types.assert_called_once()
        mock_completion.assert_called_once()


class TestGetEstimate:
    """Tests for the get_estimate function."""

    @patch('src.backend.tools.get_estimate_by_project_type')
    def test_exact_match(self, mock_get_estimate_by_project_type):
        """Test that an exact match returns the correct estimate."""
        # Arrange
        mock_estimate = {
            'project_type': 'e-commerce website',
            'budget_range': '$3k-$6k',
            'typical_timeline': '2-3 months'
        }
        mock_get_estimate_by_project_type.return_value = mock_estimate
        
        # Act
        result = get_estimate('e-commerce website')
        
        # Assert
        assert result == mock_estimate
        mock_get_estimate_by_project_type.assert_called_once_with('e-commerce website')

    @patch('src.backend.tools.get_estimate_by_project_type')
    @patch('src.backend.tools.extract_project_type')
    def test_llm_extraction(self, mock_extract_project_type, mock_get_estimate_by_project_type):
        """Test that LiteLLM extraction is used when no exact match is found."""
        # Arrange
        mock_estimate = {
            'project_type': 'e-commerce website',
            'budget_range': '$3k-$6k',
            'typical_timeline': '2-3 months'
        }
        mock_get_estimate_by_project_type.side_effect = [None, mock_estimate]
        mock_extract_project_type.return_value = 'e-commerce website'
        
        # Act
        result = get_estimate('online shop')
        
        # Assert
        assert result == mock_estimate
        mock_get_estimate_by_project_type.assert_called_with('e-commerce website')
        mock_extract_project_type.assert_called_once_with('online shop')

    @patch('src.backend.tools.get_estimate_by_project_type')
    @patch('src.backend.tools.extract_project_type')
    def test_no_match(self, mock_extract_project_type, mock_get_estimate_by_project_type):
        """Test that a default response is returned when no match is found."""
        # Arrange
        mock_get_estimate_by_project_type.return_value = None
        mock_extract_project_type.return_value = None
        
        # Act
        result = get_estimate('something completely different')
        
        # Assert
        assert result['project_type'] == 'unknown'
        assert result['budget_range'] == 'Requires more information'
        assert result['typical_timeline'] == 'Requires more information'
        assert 'message' in result
        mock_get_estimate_by_project_type.assert_called_once_with('something completely different')
        mock_extract_project_type.assert_called_once_with('something completely different')

    @patch('src.backend.tools.get_estimate_by_project_type')
    def test_exception_handling(self, mock_get_estimate_by_project_type):
        """Test that exceptions are handled properly."""
        # Arrange
        mock_get_estimate_by_project_type.side_effect = Exception("Test exception")
        
        # Act
        result = get_estimate('e-commerce website')
        
        # Assert
        assert result['project_type'] == 'error'
        assert result['budget_range'] == 'Unavailable'
        assert result['typical_timeline'] == 'Unavailable'
        assert 'message' in result
        mock_get_estimate_by_project_type.assert_called_once_with('e-commerce website') 