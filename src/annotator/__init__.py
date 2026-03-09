"""
LLM Tag Annotator - Multi-label text classification tool
"""

from .annotator import (
    AnnotatorBase,
    MultiLabelAnnotator,
    ZeroShotMultiLabelAnnotator,
    AnnotationResponse,
    AnnotationResponseMetadata,
    AnnotationResponseStatus,
)
from .main import Main, AnnotatorType
from .utils import resolve_config_path

__version__ = "0.1.0"

__all__ = [
    'AnnotatorBase',
    'MultiLabelAnnotator',
    'ZeroShotMultiLabelAnnotator',
    'AnnotationResponse',
    'AnnotationResponseMetadata',
    'AnnotationResponseStatus',
    'Main',
    'AnnotatorType',
    'resolve_config_path',
]
