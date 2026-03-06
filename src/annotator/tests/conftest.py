"""
Pytest configuration and fixtures for annotator tests.

This module provides:
- tmp_config_dir fixture for temporary config directories
- mock_llm_response fixture for mocking LLM responses
- pytest_sessionfinish hook for automatic report generation
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock


@pytest.fixture
def tmp_config_dir():
    """
    Create a temporary config directory for annotator tests.

    This fixture creates a temporary directory that can be used
    for storing test configuration files.
    """
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_config_yaml(tmp_config_dir):
    """
    Create a sample config YAML file for testing.

    Returns:
        Path: Path to the created config file
    """
    config_content = """
annotators:
  - name: test-multilabel
    type: multilabel
    instruction: Test classification
    labels:
      - "Label A"
      - "Label B"
      - "Label C"

  - name: test-zeroshot
    type: zeroshot-multilabel
    instruction: Test zeroshot classification
    labels:
      - "Label X"
      - "Label Y"
    max_new_labels: 3

models:
  - name: test-model
    model: test/model
    api_key: test_key
"""
    config_path = tmp_config_dir / "config.yaml"
    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def mock_llm_response():
    """
    Create a mock LLM response for testing.

    Returns:
        MagicMock: Mock completion function that returns predefined responses
    """
    mock = MagicMock()

    def mock_completion(messages, **kwargs):
        """Mock LLM completion that returns a simple tag response"""
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message = MagicMock()
        response.choices[0].message.content = '{"tags": ["Label A", "Label B"]}'
        return response

    mock.side_effect = mock_completion
    return mock
