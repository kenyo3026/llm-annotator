"""
Unit tests for Main class functionality.

Tests cover:
- Config loading and parsing
- Annotator setup and selection
- Model selection
- List commands

Usage:
    # Run tests
    pytest src/annotator/tests/test_main.py -v

    # Or with direct execution
    python -m src.annotator.tests.test_main
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from annotator.main import Main, AnnotatorType
from annotator.annotator import MultiLabelAnnotator, ZeroShotMultiLabelAnnotator


class TestMainConfiguration:
    """Tests for Main class configuration handling."""

    def test_load_config(self, sample_config_yaml):
        """Test loading configuration from file."""
        main = Main(config_path=str(sample_config_yaml))

        # Verify config is loaded
        assert main.config_morpher is not None
        annotators = main.list_annotators()
        assert len(annotators) > 0

    def test_list_annotators(self, sample_config_yaml):
        """Test listing available annotators."""
        main = Main(config_path=str(sample_config_yaml))
        annotators = main.list_annotators()

        # Verify
        assert "test-multilabel" in annotators
        assert "test-zeroshot" in annotators

    def test_list_models(self, sample_config_yaml):
        """Test listing available models."""
        main = Main(config_path=str(sample_config_yaml))
        models = main.list_models()

        # Verify
        assert "test-model" in models


class TestMainAnnotatorSetup:
    """Tests for annotator setup and selection."""

    def test_setup_multilabel_annotator(self, sample_config_yaml):
        """Test setting up MultiLabel annotator."""
        main = Main(config_path=str(sample_config_yaml))
        annotator = main.setup_annotator(
            annotator_name="test-multilabel",
            model_name="test-model"
        )

        # Verify correct annotator type
        assert isinstance(annotator, MultiLabelAnnotator)
        assert annotator.labels == ["Label A", "Label B", "Label C"]

    def test_setup_zeroshot_annotator(self, sample_config_yaml):
        """Test setting up ZeroShot annotator."""
        main = Main(config_path=str(sample_config_yaml))
        annotator = main.setup_annotator(
            annotator_name="test-zeroshot",
            model_name="test-model"
        )

        # Verify correct annotator type
        assert isinstance(annotator, ZeroShotMultiLabelAnnotator)

    def test_setup_default_annotator(self, sample_config_yaml):
        """Test setup with default (first) annotator and model."""
        main = Main(config_path=str(sample_config_yaml))
        annotator = main.setup_annotator()

        # Should use first annotator
        assert annotator is not None

    def test_invalid_annotator_name(self, sample_config_yaml):
        """Test error handling for invalid annotator name."""
        main = Main(config_path=str(sample_config_yaml))

        with pytest.raises(ValueError, match="No item in list matches condition"):
            main.setup_annotator(annotator_name="nonexistent")

    def test_invalid_model_name(self, sample_config_yaml):
        """Test error handling for invalid model name."""
        main = Main(config_path=str(sample_config_yaml))

        with pytest.raises(ValueError, match="No item in list matches condition"):
            main.setup_annotator(model_name="nonexistent")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from annotator.tests.base import run_tests_with_report
    sys.exit(run_tests_with_report(__file__, 'main'))
