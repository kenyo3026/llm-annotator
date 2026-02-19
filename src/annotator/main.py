import pathlib
from dataclasses import dataclass, asdict
from typing import Union, List, Dict, Any
from config_morpher import ConfigMorpher

from .annotator import (
    MultiLabelAnnotator,
    ZeroShotMultiLabelAnnotator,
    AnnotationResponse
)


@dataclass(frozen=True)
class AnnotatorType:
    """Annotator type constants"""
    MULTILABEL = 'multilabel'
    ZEROSHOT_MULTILABEL = 'zeroshot-multilabel'

    def get_fields(self):
        return list(self.__dataclass_fields__.keys())


# Default values (following drowcoder pattern)
DEFAULT_ANNOTATOR_TYPE = AnnotatorType.MULTILABEL
DEFAULT_MAX_NEW_LABELS = 3


class Main:
    """Core main class for LLM Tag Annotator"""

    def __init__(
        self,
        config_path: Union[str, pathlib.Path, List[Union[str, pathlib.Path]]] = '../configs/config.yaml'
    ):
        """
        Initialize Main with configuration

        Args:
            config_path: Path(s) to config file(s). Can be a single path or list of paths.
                        If list, configs will be merged by config-morpher.
        """
        # Load configuration using config-morpher (following drowcoder pattern)
        self.config_morpher = ConfigMorpher(config_path)

    def _get_completion_kwargs(self, name: str = None) -> Dict[str, Any]:
        # Select model: by name or first one
        if name:
            # Use config_morpher path syntax (following drowcoder)
            kwargs = self.config_morpher.fetch(f'models[name={name}]', None)
            if not kwargs:
                raise ValueError(f"Model '{name}' not found in config")
        else:
            # Use first model (following drowcoder pattern: models[0])
            kwargs = self.config_morpher.fetch('models[0]', None)
            if not kwargs:
                raise ValueError("No models configured")

        return kwargs

    def _get_annotator_kwargs(self, name: str = None) -> Dict[str, Any]:
        # Select model: by name or first one
        if name:
            # Use config_morpher path syntax (following drowcoder)
            kwargs = self.config_morpher.fetch(f'annotators[name={name}]', None)
            if not kwargs:
                raise ValueError(f"Annotator '{name}' not found in config")
        else:
            # Use first model (following drowcoder pattern: models[0])
            kwargs = self.config_morpher.fetch('annotators[0]', None)
            if not kwargs:
                raise ValueError("No annotators configured")

        return kwargs

    def setup_annotator(
        self,
        annotator_name: str = None,
        model_name: str = None
    ):
        annotator_kwargs = self._get_annotator_kwargs(name=annotator_name)
        annotator_kwargs.pop("name", None)
        annotator_type = annotator_kwargs.pop('type')

        completion_kwargs = self._get_completion_kwargs(name=model_name)
        completion_kwargs.pop("name", None)

        # Create annotator based on type
        if annotator_type == AnnotatorType.MULTILABEL:
            return MultiLabelAnnotator(
                **annotator_kwargs,
                **completion_kwargs,
            )
        elif annotator_type == AnnotatorType.ZEROSHOT_MULTILABEL:
            return ZeroShotMultiLabelAnnotator(
                **annotator_kwargs,
                **completion_kwargs,
            )
        else:
            raise ValueError(
                f"Unknown annotator type: '{annotator_type}'. "
                f"Supported types: {AnnotatorType.get_fields()}"
            )

    def annotate(
        self,
        context: str,
        annotator_name: str = None,
        model_name: str = None
    ) -> AnnotationResponse:
        """
        Execute annotation

        Args:
            text: Text to annotate
            annotator_id: Annotator ID to use. If None, uses first annotator.
            model_name: Model name to use. If None, uses first model.

        Returns:
            AnnotationResponse with tags and metadata
        """
        annotator = self.setup_annotator(annotator_name, model_name)
        return annotator.annotate(context, return_as_dict=False)

    def list_annotators(self) -> List[str]:
        """List all available annotator IDs"""
        annotators = self.config_morpher.fetch('annotators', [])
        return [a.get('name', 'unnamed') for a in annotators]

    def list_models(self) -> List[str]:
        """List all available model names"""
        models = self.config_morpher.fetch('models', [])
        return [m.get('name', 'unnamed') for m in models]
