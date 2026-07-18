import sys
import argparse
from pathlib import Path
from monitoring.golden_set.loader import load_golden_set


def format_diff_markdown(old_path: str, new_path: str) -> str:
    old_cases_list = load_golden_set(old_path) if Path(old_path).exists() else []
    new_cases_list = load_golden_set(new_path)

    old_cases = {case.case_hash: case for case in old_cases_list}
    new_cases = {case.case_hash: case for case in new_cases_list}

    added = []
    removed = []
    modified = []

    for case_hash, new_case in new_cases.items():
        if case_hash not in old_cases:
            added.append(new_case)
        else:
            old_case = old_cases[case_hash]
            if new_case.model_dump() != old_case.model_dump():
                modified.append((old_case, new_case))

    for case_hash, old_case in old_cases.items():
        if case_hash not in new_cases:
            removed.append(old_case)

    # Format Markdown
    md = [
        "## Golden Set Diff",
        f"- **Old Version**: `{old_path}` ({len(old_cases)} cases)",
        f"- **New Version**: `{new_path}` ({len(new_cases)} cases)",
        "",
        f"**Summary**: {len(added)} added, {len(removed)} removed, {len(modified)} modified.",
        ""
    ]

    if added:
        md.append("### 🟢 Added Cases")
        for c in added:
            md.append(f"- `[{c.severity.upper()}]` {c.category}: {str(c.case_hash)[:8]}")
        md.append("")

    if removed:
        md.append("### 🔴 Removed Cases")
        for c in removed:
            md.append(f"- `[{c.severity.upper()}]` {c.category}: {str(c.case_hash)[:8]}")
        md.append("")

    if modified:
        md.append("### 🟡 Modified Cases (Metadata/Criteria)")
        for old_c, new_c in modified:
            md.append(f"- Case: {str(new_c.case_hash)[:8]}")
        md.append("")

    return "\n".join(md)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diff two golden set JSONL versions.")
    parser.add_argument("--old", required=True, help="Path to old version JSONL")
    parser.add_argument("--new", required=True, help="Path to new version JSONL")
    args = parser.parse_args()

    try:
        markdown_output = format_diff_markdown(args.old, args.new)
        print(markdown_output)
    except Exception as e:
        print(f"Error computing diff: {e}", file=sys.stderr)
        sys.exit(1)
