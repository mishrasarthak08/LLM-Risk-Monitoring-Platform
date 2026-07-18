from datetime import datetime
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field, model_validator

from monitoring.golden_set.versioning import content_hash


class GoldenSetCase(BaseModel):
    case_hash: Optional[str] = None  # Computed if not provided
    category: Literal["happy_path", "edge_case",
                      "adversarial", "known_failure"]
    input_payload: dict[str, Any]
    expected_output: Optional[str] = None
    expected_criteria: dict[str, Any] = Field(default_factory=dict)
    severity: Literal["blocking", "major", "minor"]
    tags: list[str] = Field(default_factory=list)
    source: str
    added_by: str
    added_at: datetime
    notes: str = ""

    @model_validator(mode="before")
    @classmethod
    def compute_case_hash(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # If case_hash is not explicitly set, compute it from core fields
            if not data.get("case_hash"):
                hash_input = {
                    "category": data.get("category"),
                    "input_payload": data.get("input_payload"),
                    "expected_output": data.get("expected_output")
                }
                data["case_hash"] = content_hash(hash_input)
        return data

    @model_validator(mode="after")
    def validate_notes_required(self):
        if self.category in ("known_failure", "adversarial") and not self.notes:
            raise ValueError(
                f"notes field is required for category '{self.category}'")
        return self
