import json
import argparse
from typing import Dict, Any


def generate_markdown_report(regression_data: Dict[str, Any]) -> str:
    gate = regression_data["gate_decision"]
    cases = regression_data["case_results"]

    md = [
        "# Regression Suite Report",
        "",
        f"**Gate Decision**: `{gate['decision'].upper()}`",
    ]

    if "reason" in gate:
        md.append(f"**Reason**: {gate['reason']}")
    if "p_value" in gate:
        md.append(f"**Wilcoxon p-value**: {gate['p_value']:.4f}")

    md.extend([
        "",
        "## Changed Verdicts",
        ""
    ])

    changed_cases = [c for c in cases if c["verdict"] != "unchanged"]

    if not changed_cases:
        md.append("No cases changed verdict.")
    else:
        for c in changed_cases:
            emoji = "🔴" if "failing" in c["verdict"] or c["verdict"] == "regressed" else "🟢"
            md.append(f"### {emoji} {c['verdict'].replace('_', ' ').title()}")
            md.append(f"- **Case Hash**: `{c['case_hash'][:8]}`")
            md.append(f"- **Category**: {c['category']}")
            md.append(f"- **Severity**: {c['severity']}")
            md.append(
                f"- **Delta**: {c['delta']:+.2f} "
                f"(Base: {c['baseline_score']}, Cand: {c['candidate_score']})"
            )
            md.append("")

    return "\n".join(md)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-file", required=True,
        help="JSON file output from runner"
    )
    parser.add_argument(
        "--output-file", required=True,
        help="Markdown file to write"
    )
    args = parser.parse_args()

    with open(args.data_file, "r") as f:
        data = json.load(f)

    report = generate_markdown_report(data)

    with open(args.output_file, "w") as f:
        f.write(report)

    print(f"Report written to {args.output_file}")
