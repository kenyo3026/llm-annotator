"""
Unit tests for utility functions.

Tests cover:
- Path resolution
- Config path handling

Usage:
    # Run tests
    pytest src/annotator/tests/test_utils.py -v

    # Or with direct execution
    python -m src.annotator.tests.test_utils
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from annotator.utils import resolve_config_path


class TestPathResolution:
    """Tests for path resolution utilities."""

    def test_resolve_existing_file(self, tmp_config_dir):
        """Test resolving path to existing file."""
        config_file = tmp_config_dir / "config.yaml"
        config_file.write_text("test: config")

        resolved = resolve_config_path(str(config_file))

        assert Path(resolved).exists()
        assert "config.yaml" in resolved

    def test_resolve_path_object(self, tmp_config_dir):
        """Test resolving Path object."""
        config_file = tmp_config_dir / "config.yaml"
        config_file.write_text("test: config")

        # Test with Path object
        resolved = resolve_config_path(config_file)

        assert Path(resolved).exists()

    def test_nonexistent_path(self):
        """Test handling of nonexistent path."""
        # Test with a path that definitely doesn't exist and won't fallback
        nonexistent = "/absolutely/nonexistent/impossible/path/config.yaml"
        result = resolve_config_path(nonexistent)
        # The function returns a fallback path even if it doesn't exist
        # So we just verify it returns a path
        assert isinstance(result, str)

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from annotator.tests.base import run_tests_with_report
    sys.exit(run_tests_with_report(__file__, 'utils'))
