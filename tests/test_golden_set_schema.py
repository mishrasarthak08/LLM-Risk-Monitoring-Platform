import pytest
from pydantic import ValidationError
from datetime import datetime, UTC

from monitoring.golden_set.schema import GoldenSetCase


def test_golden_set_case_valid_happy_path():
    case = GoldenSetCase(
        category="happy_path",
        input_payload={"test": "data"},
        severity="minor",
        source="manually_authored",
        added_by="test_user",
        added_at=datetime.now(UTC)
    )
    assert case.case_hash is not None
    assert len(case.case_hash) == 64  # SHA-256


def test_golden_set_case_known_failure_requires_notes():
    with pytest.raises(ValidationError) as exc_info:
        GoldenSetCase(
            category="known_failure",
            input_payload={"test": "data"},
            severity="blocking",
            source="incident:123",
            added_by="test_user",
            added_at=datetime.now(UTC),
            notes=""  # Missing notes
        )
    assert "notes field is required" in str(exc_info.value)


def test_golden_set_case_adversarial_requires_notes():
    with pytest.raises(ValidationError) as exc_info:
        GoldenSetCase(
            category="adversarial",
            input_payload={"test": "data"},
            severity="blocking",
            source="redteam",
            added_by="test_user",
            added_at=datetime.now(UTC),
            notes=""  # Missing notes
        )
    assert "notes field is required" in str(exc_info.value)
