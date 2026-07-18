
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Stubbed in-memory storage for our mock "reference distributions" table
_MOCK_DB_FILE = Path("monitoring/drift/mock_reference_db.json")


def _load_mock_db() -> List[Dict[str, Any]]:
    if not _MOCK_DB_FILE.exists():
        return []
    with open(_MOCK_DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_mock_db(data: List[Dict[str, Any]]):
    _MOCK_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_MOCK_DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


def build_reference_distribution(feature_name: str, metric: str, distribution_data: Any, start_time: str, end_time: str) -> str:
    """
    Builds a baseline reference distribution for a specific metric over a stable time window.
    Saves it to the mock database.
    """
    db = _load_mock_db()

    # Mark existing active references for this feature/metric as superseded
    for ref in db:
        if ref["feature_name"] == feature_name and ref["metric"] == metric and ref.get("superseded_by") is None:
            # Simplified mock linking
            ref["superseded_by"] = "NEW_REFERENCE_ID"

    new_id = f"ref_{len(db)+1}"

    new_reference = {
        "id": new_id,
        "feature_name": feature_name,
        "metric": metric,
        "distribution_summary": distribution_data,
        "built_from_window": [start_time, end_time],
        "superseded_by": None,
        "created_at": datetime.utcnow().isoformat()
    }

    db.append(new_reference)
    _save_mock_db(db)

    return new_id


def get_active_reference(feature_name: str, metric: str) -> list | None:
    """
    Retrieves the currently active (not superseded) reference distribution data.
    """
    db = _load_mock_db()
    for ref in reversed(db):
        if ref["feature_name"] == feature_name and ref["metric"] == metric and ref.get("superseded_by") is None:
            return ref["distribution_summary"]
    return None
