import json
from pathlib import Path
from typing import List

from monitoring.golden_set.schema import GoldenSetCase
from monitoring.golden_set.versioning import golden_set_hash


def load_golden_set(file_path: str | Path) -> List[GoldenSetCase]:
    """Loads a JSONL golden set file and validates each case."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Golden set file not found: {path}")

    cases = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                case = GoldenSetCase.model_validate(data)
                cases.append(case)
            except Exception as e:
                raise ValueError(
                    f"Failed to validate line {line_num} in {path}: {e}")

    return cases


def verify_golden_set_integrity(cases: List[GoldenSetCase]) -> str:
    """Computes the overall golden set hash from the individual case hashes."""
    case_hashes = [str(case.case_hash) for case in cases if case.case_hash is not None]
    return golden_set_hash(case_hashes)
