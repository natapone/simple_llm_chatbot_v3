"""
Tests for the database operations.

This module contains tests for the database operations.
"""

import pytest
import sys
import os
import sqlite3
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.database import (
    initialize_database,
    get_all_project_types,
    get_estimate_by_project_type,
    store_lead,
    ProjectEstimate,
    Lead
)


class TestInitializeDatabase:
    """Tests for the initialize_database function."""

    @patch('src.backend.database.Base.metadata.create_all')
    @patch('src.backend.database.Session')
    def test_initialize_database_success(self, mock_session, mock_create_all):
        """Test that the database is initialized successfully."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.query.return_value.count.return_value = 0
        
        # Act
        result = initialize_database()
        
        # Assert
        assert result is True
        mock_create_all.assert_called_once()
        mock_session_instance.add_all.assert_called_once()
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()

    @patch('src.backend.database.Base.metadata.create_all')
    @patch('src.backend.database.Session')
    def test_initialize_database_already_populated(self, mock_session, mock_create_all):
        """Test that the database is not populated if it already has data."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.query.return_value.count.return_value = 5
        
        # Act
        result = initialize_database()
        
        # Assert
        assert result is True
        mock_create_all.assert_called_once()
        mock_session_instance.add_all.assert_not_called()
        mock_session_instance.commit.assert_not_called()
        mock_session_instance.close.assert_called_once()

    @patch('src.backend.database.Base.metadata.create_all')
    @patch('src.backend.database.Session')
    def test_initialize_database_exception(self, mock_session, mock_create_all):
        """Test that exceptions are handled gracefully."""
        # Arrange
        mock_create_all.side_effect = Exception('Test exception')
        
        # Act
        result = initialize_database()
        
        # Assert
        assert result is False
        mock_create_all.assert_called_once()


class TestGetAllProjectTypes:
    """Tests for the get_all_project_types function."""

    @patch('src.backend.database.Session')
    def test_get_all_project_types_success(self, mock_session):
        """Test that all project types are returned successfully."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_project_estimate_1 = MagicMock()
        mock_project_estimate_1.project_type = 'e-commerce website'
        mock_project_estimate_2 = MagicMock()
        mock_project_estimate_2.project_type = 'mobile restaurant app'
        mock_session_instance.query.return_value.all.return_value = [
            mock_project_estimate_1,
            mock_project_estimate_2
        ]
        
        # Act
        result = get_all_project_types()
        
        # Assert
        assert result == ['e-commerce website', 'mobile restaurant app']
        mock_session_instance.query.assert_called_once_with(ProjectEstimate)
        mock_session_instance.close.assert_called_once()

    @patch('src.backend.database.Session')
    def test_get_all_project_types_empty(self, mock_session):
        """Test that an empty list is returned when there are no project types."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.query.return_value.all.return_value = []
        
        # Act
        result = get_all_project_types()
        
        # Assert
        assert result == []
        mock_session_instance.query.assert_called_once_with(ProjectEstimate)
        mock_session_instance.close.assert_called_once()

    @patch('src.backend.database.Session')
    def test_get_all_project_types_exception(self, mock_session):
        """Test that exceptions are handled gracefully."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.query.side_effect = Exception('Test exception')
        
        # Act
        result = get_all_project_types()
        
        # Assert
        assert result == []
        mock_session_instance.query.assert_called_once_with(ProjectEstimate)


class TestGetEstimateByProjectType:
    """Tests for the get_estimate_by_project_type function."""

    @patch('src.backend.database.Session')
    def test_get_estimate_by_project_type_success(self, mock_session):
        """Test that the correct estimate is returned for a project type."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_project_estimate = MagicMock()
        mock_project_estimate.project_type = 'e-commerce website'
        mock_project_estimate.budget_range = '$3k-$6k'
        mock_project_estimate.typical_timeline = '2-3 months'
        mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_project_estimate
        
        # Act
        result = get_estimate_by_project_type('e-commerce website')
        
        # Assert
        assert result == {
            'project_type': 'e-commerce website',
            'budget_range': '$3k-$6k',
            'typical_timeline': '2-3 months'
        }
        mock_session_instance.query.assert_called_once_with(ProjectEstimate)
        mock_session_instance.close.assert_called_once()

    @patch('src.backend.database.Session')
    def test_get_estimate_by_project_type_not_found(self, mock_session):
        """Test that None is returned when the project type is not found."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = get_estimate_by_project_type('nonexistent project type')
        
        # Assert
        assert result is None
        mock_session_instance.query.assert_called_once_with(ProjectEstimate)
        mock_session_instance.close.assert_called_once()

    @patch('src.backend.database.Session')
    def test_get_estimate_by_project_type_exception(self, mock_session):
        """Test that exceptions are handled gracefully."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.query.side_effect = Exception('Test exception')
        
        # Act
        result = get_estimate_by_project_type('e-commerce website')
        
        # Assert
        assert result is None
        mock_session_instance.query.assert_called_once_with(ProjectEstimate)


class TestStoreLead:
    """Tests for the store_lead function."""

    @patch('src.backend.database.Session')
    def test_store_lead_success(self, mock_session):
        """Test that a lead is stored successfully."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_lead = MagicMock()
        mock_lead.id = 1
        mock_session_instance.add.return_value = None
        
        # Mock the Lead class to return our mock_lead
        with patch('src.backend.database.Lead', return_value=mock_lead):
            # Act
            result = store_lead(
                name='John Doe',
                contact='john.doe@example.com',
                project_type='e-commerce website',
                project_details='I need an online store for my business.',
                estimated_budget='$3k-$6k',
                estimated_timeline='2-3 months',
                follow_up_consent=True
            )
        
        # Assert
        assert result == 1
        mock_session_instance.add.assert_called_once()
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()

    @patch('src.backend.database.Session')
    def test_store_lead_exception(self, mock_session):
        """Test that exceptions are handled gracefully."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.add.side_effect = Exception('Test exception')
        
        # Act
        result = store_lead(
            name='John Doe',
            contact='john.doe@example.com',
            project_type='e-commerce website'
        )
        
        # Assert
        assert result is None
        mock_session_instance.add.assert_called_once() 