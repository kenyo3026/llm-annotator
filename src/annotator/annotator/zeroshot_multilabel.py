import json
from dataclasses import dataclass, asdict
from typing import List

from .base import AnnotatorBase, AnnotationResponse, AnnotationResponseStatus


SYSTEM_INSTRUCTION_ZEROSHOT_MULTILABEL = """You are a specialized text classification assistant with zero-shot capability. Your task is to analyze text content and assign relevant tags, preferring suggested labels but allowing creation of new ones when necessary.

<rules>
1. PREFER selecting tags from the provided suggested labels
2. If suggested labels are insufficient, you MAY create new relevant tags (max {max_new_labels} new tags)
3. Select 1-5 most relevant tags total based on the content
4. Return response in strict JSON format: {{"tags": ["label1", "label2", "new_label1"]}}
5. Do NOT add any explanation, markdown formatting, or additional text
6. If no labels are relevant, return {{"tags": []}}
</rules>

<suggested_labels>
{labels}
</suggested_labels>

<examples>
Example 1:
Suggested labels: ["US Stock", "Taiwan Stock", "Accounting", "Technical Analysis"]
Context: "Tesla Q3 earnings beat EPS expectations, technical chart breaks through 120 support level"
Response: {{"tags": ["US Stock", "Accounting", "Technical Analysis"]}}

Example 2:
Suggested labels: "US Stock", "Taiwan Stock", "Accounting", "Technical Analysis"
Context: "Fed rate hike impacts bond market, investors turn to gold for safe haven"
Response: {{"tags": ["US Stock", "Bonds", "Gold", "Safe Haven"]}}

Example 3:
Suggested labels: "US Stock", "Taiwan Stock", "Accounting", "Technical Analysis"
Context: "Bitcoin breaks through $60,000, crypto market warming up"
Response: {{"tags": ["Cryptocurrency", "Bitcoin"]}}
</examples>

<user_instruction>
{instruction}
</user_instruction>"""

USER_PROMPT_ZEROSHOT_MULTILABEL = """<context>
{context}
</context>

Analyze the above context and return relevant tags in JSON format."""

@dataclass
class AnnotationResponseMetadata:
    raw_tags: List[str] = None
    predefined_tags: List[str] = None
    new_tags: List[str] = None
    error: str = None
    raw_response: str = None

class ZeroShotMultiLabelAnnotator(AnnotatorBase):
    """Zero-shot multi-label classifier (allows generating new labels)"""

    def __init__(
        self,
        instruction: str,
        labels: List[str],
        max_new_labels: int = 3,
        **completion_kwargs
    ):
        super().__init__(instruction, **completion_kwargs)
        self.labels = labels
        self.max_new_labels = max_new_labels

    def annotate(
        self,
        context: str,
        return_as_dict: bool = True,
    ) -> AnnotationResponse:
        """Can select from predefined labels or generate new ones"""
        system_prompt = SYSTEM_INSTRUCTION_ZEROSHOT_MULTILABEL.format(
            instruction=self.instruction,
            labels=', '.join(f'"{label}"' for label in self.labels),
            max_new_labels=self.max_new_labels,
        )
        user_prompt = USER_PROMPT_ZEROSHOT_MULTILABEL.format(context=context)

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

            # Post-process: separate predefined vs new tags
            predefined_tags = [t for t in raw_tags if t in self.labels]
            new_tags = [t for t in raw_tags if t not in self.labels]

            # Limit new tags by max_new_labels
            new_tags = new_tags[:self.max_new_labels]

            # Combine for final result
            tags = predefined_tags + new_tags

            metadata = AnnotationResponseMetadata(
                raw_tags=raw_tags,
                predefined_tags=predefined_tags,
                new_tags=new_tags,
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
                ),
            )

        if return_as_dict:
            return asdict(response)
        return response