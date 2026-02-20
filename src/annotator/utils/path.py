"""
Path resolution utilities for LLM Tag Annotator

This module provides utilities for resolving configuration file paths
across different runtime environments (CLI, API, MCP).
"""

import pathlib
from typing import Union


def resolve_config_path(config_path: Union[str, pathlib.Path]) -> str:
    """
    Resolve configuration file path

    Tries multiple locations in order:
    1. Absolute path or path relative to current working directory
    2. Path relative to project root (configs/config.yaml)
    3. Path relative to home directory (~/.annotator/config.yaml)

    Args:
        config_path: Path to configuration file

    Returns:
        Resolved absolute path to config file

    Raises:
        FileNotFoundError: If config file cannot be found in any location

    Examples:
        >>> resolve_config_path("configs/config.yaml")
        '/path/to/project/configs/config.yaml'

        >>> resolve_config_path("~/.annotator/config.yaml")
        '/Users/username/.annotator/config.yaml'
    """
    # Convert to Path object
    path = pathlib.Path(config_path)

    # Try as-is (absolute or relative to cwd)
    if path.exists():
        return str(path.absolute())

    # Try relative to project root
    # Navigate from src/annotator/utils/path.py -> project root
    project_root = pathlib.Path(__file__).parent.parent.parent.parent
    path = project_root / config_path
    if path.exists():
        return str(path.absolute())

    # Try in configs/ directory
    path = project_root / "configs" / "config.yaml"
    if path.exists():
        return str(path.absolute())

    # Try in home directory
    path = pathlib.Path.home() / ".annotator" / "config.yaml"
    if path.exists():
        return str(path.absolute())

    # If nothing found, raise error with helpful message
    raise FileNotFoundError(
        f"Configuration file not found. Tried:\n"
        f"  - {config_path}\n"
        f"  - {project_root / config_path}\n"
        f"  - {project_root / 'configs' / 'config.yaml'}\n"
        f"  - {pathlib.Path.home() / '.annotator' / 'config.yaml'}"
    )
