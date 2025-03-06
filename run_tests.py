#!/usr/bin/env python3
"""
Run tests script for the pre-sales chatbot.

This script runs the tests for the pre-sales chatbot.
"""

import pytest
import sys
import os

if __name__ == "__main__":
    # Add the current directory to the path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Run the tests
    pytest.main(["-v", "tests"]) 