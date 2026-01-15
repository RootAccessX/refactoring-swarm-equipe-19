"""
Logger Tests Package

This package contains comprehensive test suites for the logging system:
- test_logger.py: Manual testing and validation
- test_logger_pytest.py: Unit tests using pytest framework
- test_logger_e2e.py: End-to-end integration and workflow tests
- conftest.py: Pytest configuration and shared fixtures

Run all manual tests:
    python tests/logger/test_logger.py
    python tests/logger/test_logger_e2e.py

Run pytest tests:
    pytest tests/logger/test_logger_pytest.py -v

For detailed information, see tests/logger/README.md
"""

__all__ = [
    "test_logger",
    "test_logger_pytest",
    "test_logger_e2e"
]
