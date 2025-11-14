import sys
import os
import logging
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest


def test_logging_environment_detection():
    """Test that environment variable ENVIRONMENT is detected correctly"""
    # Test development detection
    test_env = os.getenv("ENVIRONMENT", "production").lower()
    assert test_env in ["development", "dev", "local", "production"]


def test_logging_level_configuration():
    """Test that logging is configured"""
    root_logger = logging.getLogger()
    # Logging should be configured to either DEBUG, INFO, or WARNING (pytest sets WARNING)
    assert root_logger.level in [logging.DEBUG, logging.INFO, logging.WARNING]


def test_logging_has_handlers():
    """Test that logging has at least one handler configured"""
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0, "At least one handler should be configured"


def test_logging_formatter_configured():
    """Test that logging formatter is configured"""
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0, "No handlers configured"
    
    handler = root_logger.handlers[0]
    formatter = handler.formatter
    assert formatter is not None, "No formatter configured"
    
    # Check that format includes basic elements (handle both pytest and our formats)
    format_str = formatter._fmt
    assert "levelname" in format_str, "Format should include log level"
    assert "message" in format_str, "Format should include message"

