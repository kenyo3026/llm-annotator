"""
Unit tests for ZeroShot MultiLabel Annotator.

Tests cover:
- Basic annotation with suggested labels
- New label generation capability
- Max new labels limiting
- Separation of predefined vs new tags
- JSON parsing with markdown code blocks
- Error handling

Usage:
    # Run tests
    pytest src/annotator/tests/test_zeroshot_multilabel.py -v

    # Or with direct execution
    python -m src.annotator.tests.test_zeroshot_multilabel
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from annotator.annotator import ZeroShotMultiLabelAnnotator, AnnotationResponseStatus
from annotator.annotator.zeroshot_multilabel import ZeroShotMultiLabelAnnotationResponseMetadata


class TestZeroShotAnnotatorBasic:
    """Basic ZeroShot annotator functionality tests."""

    @patch('annotator.annotator.base.completion')
    def test_annotation_with_predefined_labels(self, mock_completion):
        """Test annotation using only predefined labels."""
        # Mock LLM response with only predefined labels
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"tags": ["Label A", "Label B"]}'
        mock_completion.return_value = mock_response

        annotator = ZeroShotMultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B", "Label C"],
            max_new_labels=3,
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify
        assert result.status == AnnotationResponseStatus.success
        assert set(result.tags) == {"Label A", "Label B"}
        assert isinstance(result.metadata, ZeroShotMultiLabelAnnotationResponseMetadata)
        assert result.metadata.predefined_tags == ["Label A", "Label B"]
        assert result.metadata.new_tags == []

    @patch('annotator.annotator.base.completion')
    def test_annotation_with_new_labels(self, mock_completion):
        """Test annotation generating new labels."""
        # Mock LLM response with mix of predefined and new labels
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"tags": ["Label A", "New Label 1", "New Label 2"]}'
        mock_completion.return_value = mock_response

        annotator = ZeroShotMultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B"],
            max_new_labels=3,
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify
        assert result.status == AnnotationResponseStatus.success
        assert set(result.tags) == {"Label A", "New Label 1", "New Label 2"}
        assert result.metadata.predefined_tags == ["Label A"]
        assert result.metadata.new_tags == ["New Label 1", "New Label 2"]


class TestZeroShotAnnotatorLimits:
    """Tests for max_new_labels limiting."""

    @patch('annotator.annotator.base.completion')
    def test_max_new_labels_limit(self, mock_completion):
        """Test that new labels are limited by max_new_labels."""
        # Mock LLM response with more new labels than allowed
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"tags": ["Label A", "New 1", "New 2", "New 3", "New 4"]}'
        mock_completion.return_value = mock_response

        annotator = ZeroShotMultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B"],
            max_new_labels=2,  # Only allow 2 new labels
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify: Should have 1 predefined + 2 new (limited)
        assert result.status == AnnotationResponseStatus.success
        assert len(result.metadata.predefined_tags) == 1
        assert len(result.metadata.new_tags) == 2  # Limited to max_new_labels
        assert len(result.tags) == 3  # Total = 1 predefined + 2 new

    @patch('annotator.annotator.base.completion')
    def test_zero_new_labels_allowed(self, mock_completion):
        """Test behavior when max_new_labels=0."""
        # Mock LLM response with new labels
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"tags": ["Label A", "New Label"]}'
        mock_completion.return_value = mock_response

        annotator = ZeroShotMultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B"],
            max_new_labels=0,  # No new labels allowed
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify: Should only have predefined labels
        assert result.status == AnnotationResponseStatus.success
        assert result.tags == ["Label A"]
        assert result.metadata.predefined_tags == ["Label A"]
        assert result.metadata.new_tags == []  # New labels filtered out


class TestZeroShotAnnotatorEdgeCases:
    """Edge case tests for ZeroShot annotator."""

    @patch('annotator.annotator.base.completion')
    def test_markdown_code_block_parsing(self, mock_completion):
        """Test parsing JSON from markdown code blocks."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '```json\n{"tags": ["Label A", "New Label"]}\n```'
        mock_completion.return_value = mock_response

        annotator = ZeroShotMultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B"],
            max_new_labels=3,
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify
        assert result.status == AnnotationResponseStatus.success
        assert "Label A" in result.tags
        assert "New Label" in result.tags

    @patch('annotator.annotator.base.completion')
    def test_all_new_labels(self, mock_completion):
        """Test annotation with all new labels (no predefined)."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"tags": ["New 1", "New 2"]}'
        mock_completion.return_value = mock_response

        annotator = ZeroShotMultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B"],
            max_new_labels=3,
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify
        assert result.status == AnnotationResponseStatus.success
        assert result.metadata.predefined_tags == []
        assert result.metadata.new_tags == ["New 1", "New 2"]
        assert result.tags == ["New 1", "New 2"]

    @patch('annotator.annotator.base.completion')
    def test_empty_tags_response(self, mock_completion):
        """Test handling of empty tags response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"tags": []}'
        mock_completion.return_value = mock_response

        annotator = ZeroShotMultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B"],
            max_new_labels=3,
            model="test/model"
        )

        result = annotator.annotate("Test context")

        # Verify
        assert result.status == AnnotationResponseStatus.success
        assert result.tags == []
        assert result.metadata.predefined_tags == []
        assert result.metadata.new_tags == []

    @patch('annotator.annotator.base.completion')
    def test_invalid_json_response(self, mock_completion):
        """Test error handling for invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'This is not valid JSON'
        mock_completion.return_value = mock_response

        annotator = ZeroShotMultiLabelAnnotator(
            instruction="Test instruction",
            labels=["Label A", "Label B"],
            max_new_labels=3,
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
    sys.exit(run_tests_with_report(__file__, 'zeroshot_multilabel'))
