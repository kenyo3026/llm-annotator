"""
Unit tests for MultiLabel Annotator.

Tests cover:
- Basic annotation with predefined labels
- Label filtering (only predefined labels returned)
- JSON parsing with markdown code blocks
- Error handling

Usage:
    # Run tests
    pytest src/annotator/tests/test_multilabel.py -v

    # Or with direct execution
    python -m src.annotator.tests.test_multilabel
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from annotator.annotator import MultiLabelAnnotator, AnnotationResponseStatus


class TestMultiLabelAnnotatorBasic:
    """Basic MultiLabel annotator functionality tests."""

    @patch('annotator.annotator.base.completion')
    def test_successful_annotation(self, mock_completion):
        """Test successful annotation with valid labels."""
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"tags": ["Label A", "Label B"]}'
        mock_completion.return_value = mock_response

        # Create annotator
        annotator = MultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B", "Label C"],
            model="test/model"
        )

        # Execute annotation
        result = annotator.annotate("Test context")

        # Verify
        assert result.status == AnnotationResponseStatus.success
        assert set(result.tags) == {"Label A", "Label B"}
        assert result.metadata is not None
        assert result.metadata.raw_tags == ["Label A", "Label B"]

    @patch('annotator.annotator.base.completion')
    def test_label_filtering(self, mock_completion):
        """Test that only predefined labels are returned."""
        # Mock LLM response with extra labels
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"tags": ["Label A", "Invalid Label", "Label B"]}'
        mock_completion.return_value = mock_response

        annotator = MultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B", "Label C"],
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify: Invalid label should be filtered out
        assert result.status == AnnotationResponseStatus.success
        assert set(result.tags) == {"Label A", "Label B"}
        assert "Invalid Label" not in result.tags


class TestMultiLabelAnnotatorEdgeCases:
    """Edge case tests for MultiLabel annotator."""

    @patch('annotator.annotator.base.completion')
    def test_markdown_code_block_parsing(self, mock_completion):
        """Test parsing JSON from markdown code blocks."""
        # Mock LLM response with markdown code blocks
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '```json\n{"tags": ["Label A"]}\n```'
        mock_completion.return_value = mock_response

        annotator = MultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B"],
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify: Should parse correctly despite markdown
        assert result.status == AnnotationResponseStatus.success
        assert result.tags == ["Label A"]

    @patch('annotator.annotator.base.completion')
    def test_empty_tags_response(self, mock_completion):
        """Test handling of empty tags response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"tags": []}'
        mock_completion.return_value = mock_response

        annotator = MultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B"],
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify
        assert result.status == AnnotationResponseStatus.success
        assert result.tags == []

    @patch('annotator.annotator.base.completion')
    def test_invalid_json_response(self, mock_completion):
        """Test error handling for invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'This is not valid JSON'
        mock_completion.return_value = mock_response

        annotator = MultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B"],
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify: Should handle error gracefully
        assert result.status == AnnotationResponseStatus.failed
        assert result.tags == []
        assert result.metadata.error is not None


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from annotator.tests.base import run_tests_with_report
    sys.exit(run_tests_with_report(__file__, 'multilabel'))
