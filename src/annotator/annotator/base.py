from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from litellm import completion


@dataclass(frozen=True)
class AnnotationResponseStatus:
    success: str = "success"
    failed: str = "failed"

@dataclass
class AnnotationResponse:
    """Annotation result data structure"""
    tags: List[str]
    confidence: float = None
    metadata: Optional[Dict[str, Any]] = None
    status: str = AnnotationResponseStatus.success

@dataclass
class AnnotatorConfig:
    """Annotator configuration"""
    id: str
    type: str
    instruction: str
    labels: List[str] = field(default_factory=list)
    max_new_labels: int = 0


class AnnotatorBase(ABC):
    """Base annotator abstract class"""

    def __init__(
        self,
        instruction: str,
        **completion_kwargs
    ):
        self.instruction = instruction
        self.completion_kwargs = completion_kwargs

    @abstractmethod
    def annotate(self, text: str) -> AnnotationResponse:
        """Execute annotation"""
        pass

    def _call_llm(self, messages: List[Dict]) -> str:
        """Call LLM (unified interface)"""
        response = completion(
            messages=messages,
            **self.completion_kwargs
        )
        return response.choices[0].message.content

    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from response, handling markdown code blocks"""
        import re
        # Remove markdown code blocks (```json ... ``` or ``` ... ```)
        response_text = re.sub(r'^```(?:json)?\s*\n?', '', response_text, flags=re.MULTILINE)
        response_text = re.sub(r'\n?```\s*$', '', response_text, flags=re.MULTILINE)
        return response_text.strip()
