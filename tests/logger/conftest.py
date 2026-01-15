"""
Pytest Configuration and Fixtures for Logger Tests

Provides shared fixtures and configuration for all logger tests.
"""

import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_log_entry():
    """Provide a sample log entry for testing"""
    return {
        "input_prompt": "Sample test prompt",
        "output_response": "Sample test response",
        "test_metadata": "Sample metadata"
    }


@pytest.fixture
def all_action_types():
    """Provide all ActionTypes for iteration in tests"""
    from src.utils.logger import ActionType
    return list(ActionType)


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
