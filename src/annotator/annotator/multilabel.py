import json
from dataclasses import dataclass, asdict
from typing import List

from .base import AnnotatorBase, AnnotationResponse, AnnotationResponseMetadata, AnnotationResponseStatus

SYSTEM_INSTRUCTION_MULTILABEL = """You are a specialized text classification assistant. Your task is to analyze text content and assign relevant tags from a predefined label set.

<rules>
1. You MUST select tags ONLY from the provided available labels
2. Select 1-5 most relevant tags based on the content
3. Return response in strict JSON format: {{"tags": ["label1", "label2"]}}
4. Do NOT add any explanation, markdown formatting, or additional text
5. If no labels are relevant, return {{"tags": []}}
</rules>

<available_labels>
{labels}
</available_labels>

<examples>
Example 1:
Available labels: ["US Stock", "Taiwan Stock", "Accounting", "Technical Analysis", "Fundamental Analysis", "Cryptocurrency"]
Context: "Tesla Q3 earnings beat EPS expectations, technical chart breaks through 120 support level"
Response: {{"tags": ["US Stock", "Accounting", "Technical Analysis"]}}

Example 2:
Available labels: "US Stock", "Taiwan Stock", "Accounting", "Technical Analysis", "Fundamental Analysis", "Cryptocurrency"
Context: "Is TSMC's P/E ratio of 15 cheap? Looking at the balance sheet..."
Response: {{"tags": ["Taiwan Stock", "Accounting", "Fundamental Analysis"]}}

Example 3:
Available labels: "US Stock", "Taiwan Stock", "Accounting", "Technical Analysis", "Fundamental Analysis", "Cryptocurrency"
Context: "Bitcoin breaks through $60,000, crypto market warming up"
Response: {{"tags": ["Cryptocurrency"]}}
</examples>

<user_instruction>
{instruction}
</user_instruction>"""

USER_PROMPT_MULTILABEL = """<context>
{context}
</context>

Analyze the above context and return relevant tags in JSON format."""


class MultiLabelAnnotator(AnnotatorBase):
    """Multi-label classifier (can only select from predefined labels)"""

    def __init__(
        self,
        instruction: str,
        labels: List[str],
        **completion_kwargs
    ):
        super().__init__(instruction, **completion_kwargs)
        self.labels = labels

    def annotate(
        self,
        context: str,
        return_as_dict: bool = False,
    ) -> AnnotationResponse:
        """Select from predefined labels"""
        system_prompt = SYSTEM_INSTRUCTION_MULTILABEL.format(
            instruction=self.instruction,
            labels=', '.join(f'"{label}"' for label in self.labels),
        )
        user_prompt = USER_PROMPT_MULTILABEL.format(context=context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response_text = self._call_llm(messages)

        try:
            # Extract JSON from response (handles markdown code blocks)
            cleaned_response = self._extract_json_from_response(response_text)

            # Parse JSON response
            data = json.loads(cleaned_response)
            raw_tags = data.get("tags", [])

            # Filter: only keep predefined labels
            tags = [t for t in raw_tags if t in self.labels]

            metadata = AnnotationResponseMetadata(
                raw_tags=raw_tags,
                raw_response=response_text[:200]  # Keep first 200 chars for debugging
            )
            response = AnnotationResponse(
                tags=tags,
                status=AnnotationResponseStatus.success,
                metadata=metadata,
            )

        except Exception as e:
            # Return empty result on error
            response = AnnotationResponse(
                tags=[],
                status=AnnotationResponseStatus.failed,
                metadata=AnnotationResponseMetadata(
                    error=str(e),
                    raw_response=response_text[:200]  # Keep first 200 chars for debugging
                )
            )

        if return_as_dict:
            return asdict(response)
        return response
