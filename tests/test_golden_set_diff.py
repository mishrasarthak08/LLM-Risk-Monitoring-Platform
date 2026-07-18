import tempfile
import json
from pathlib import Path
from ci.golden_set_diff import format_diff_markdown


def test_format_diff_markdown():
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = Path(tmpdir) / "old.jsonl"
        new_path = Path(tmpdir) / "new.jsonl"

        # Case 1: Unmodified
        case1 = {"category": "happy_path", "input_payload": {"id": 1}, "expected_output": None,
                 "severity": "minor", "source": "test", "added_by": "test", "added_at": "2026-07-17T10:00:00Z"}

        # Case 2: Removed in new
        case2 = {"category": "edge_case", "input_payload": {"id": 2}, "expected_output": None,
                 "severity": "minor", "source": "test", "added_by": "test", "added_at": "2026-07-17T10:00:00Z"}

        # Case 3: Added in new
        case3 = {"category": "edge_case", "input_payload": {"id": 3}, "expected_output": None,
                 "severity": "minor", "source": "test", "added_by": "test", "added_at": "2026-07-17T10:00:00Z"}

        # Case 4: Modified (severity changed, so same case_hash but different content)
        case4_old = {"category": "happy_path", "input_payload": {"id": 4}, "expected_output": None,
                     "severity": "minor", "source": "test", "added_by": "test", "added_at": "2026-07-17T10:00:00Z"}
        case4_new = {"category": "happy_path", "input_payload": {"id": 4}, "expected_output": None,
                     "severity": "major", "source": "test", "added_by": "test", "added_at": "2026-07-17T10:00:00Z"}

        with open(old_path, "w") as f:
            f.write(json.dumps(case1) + "\n")
            f.write(json.dumps(case2) + "\n")
            f.write(json.dumps(case4_old) + "\n")

        with open(new_path, "w") as f:
            f.write(json.dumps(case1) + "\n")
            f.write(json.dumps(case3) + "\n")
            f.write(json.dumps(case4_new) + "\n")

        diff_md = format_diff_markdown(str(old_path), str(new_path))

        assert "1 added, 1 removed, 1 modified" in diff_md
        assert "### 🟢 Added Cases" in diff_md
        assert "### 🔴 Removed Cases" in diff_md
        assert "### 🟡 Modified Cases (Metadata/Criteria)" in diff_md
