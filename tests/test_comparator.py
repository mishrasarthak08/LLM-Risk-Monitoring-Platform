from monitoring.regression.comparator import compare_case, gate_decision, CaseComparison


def test_compare_case_improved():
    comp = compare_case("c1", "minor", baseline_score=0.5, candidate_score=0.8)
    assert comp.verdict == "newly_passing"

    comp = compare_case("c2", "minor", baseline_score=0.8, candidate_score=0.9)
    assert comp.verdict == "improved"


def test_compare_case_regressed():
    comp = compare_case(
        "c1", "blocking", baseline_score=0.9, candidate_score=0.4)
    assert comp.verdict == "newly_failing"

    comp = compare_case(
        "c2", "blocking", baseline_score=0.9, candidate_score=0.8)
    assert comp.verdict == "regressed"


def test_gate_decision_blocking_failure():
    comparisons = [
        CaseComparison("c1", "blocking", 0.9, 0.4, -0.5, "newly_failing"),
        CaseComparison("c2", "minor", 0.4, 0.9, 0.5, "newly_passing")
    ]
    gate = gate_decision(comparisons)
    assert gate["decision"] == "block"
    assert "blocking-severity" in gate["reason"]


def test_gate_decision_major_failures():
    comparisons = [
        CaseComparison("c1", "major", 0.9, 0.4, -0.5, "newly_failing"),
        CaseComparison("c2", "major", 0.9, 0.4, -0.5, "newly_failing"),
        CaseComparison("c3", "major", 0.9, 0.4, -0.5, "newly_failing")
    ]
    gate = gate_decision(comparisons)
    assert gate["decision"] == "block"
    assert "major-severity" in gate["reason"]


def test_gate_decision_wilcoxon_warning():
    # Subtle regressions across many cases that don't flip a binary gate but shift the median
    comparisons = [
        CaseComparison(f"c{i}", "minor", 0.9, 0.8, -0.1, "regressed")
        for i in range(15)
    ]
    gate = gate_decision(comparisons)
    assert gate["decision"] == "allow_with_warning"
    assert "Statistically significant net score decline" in gate["reason"]


def test_gate_decision_allow():
    comparisons = [
        CaseComparison("c1", "blocking", 0.9, 0.9, 0.0, "unchanged"),
        CaseComparison("c2", "major", 0.8, 0.9, 0.1, "improved")
    ]
    gate = gate_decision(comparisons)
    assert gate["decision"] == "allow"
