from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from eval_harness.io import deep_merge, read_json
from eval_harness.models import EvaluationStatus, EvaluatorResult
from eval_harness.runner import HarnessRunner

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_deep_merge_replaces_scalars_arrays_and_preserves_objects() -> None:
    base = {"nested": {"left": 1, "right": 2}, "array": [1], "value": 1}
    patch = {"nested": {"right": 3}, "array": [2], "value": None}

    assert deep_merge(base, patch) == {
        "nested": {"left": 1, "right": 3},
        "array": [2],
        "value": None,
    }


def test_contract_suite_passes(tmp_path: Path) -> None:
    summary = HarnessRunner(REPO_ROOT, tmp_path).run_suite(
        REPO_ROOT / "evals/suites/v1_contract.json"
    )

    assert summary["success"] is True
    assert summary["case_count"] == 8
    assert {case["verdict"] for case in summary["cases"]} == {"PASS"}
    assert all(case["expectation_met"] for case in summary["cases"])
    _validate_results(summary)


def test_fault_injection_suite_detects_every_fault(tmp_path: Path) -> None:
    summary = HarnessRunner(REPO_ROOT, tmp_path).run_suite(
        REPO_ROOT / "evals/suites/harness_self_test.json"
    )

    assert summary["success"] is True
    assert summary["case_count"] == 5
    assert {case["verdict"] for case in summary["cases"]} == {"FAIL"}
    assert all(case["expectation_met"] for case in summary["cases"])

    failures = {
        case["case_id"]: set(case["failed_evaluators"]) for case in summary["cases"]
    }
    assert "C001" in failures["fault_schema_version"]
    assert "N003" in failures["fault_probability_sum"]
    assert "N001" in failures["fault_arithmetic"]
    assert "D001" in failures["fault_decision"]
    assert "C002" in failures["fault_missing_artifact"]
    _validate_results(summary)


def test_all_json_schemas_are_valid() -> None:
    schema_paths = [
        REPO_ROOT / "docs/report_schema.json",
        *sorted((REPO_ROOT / "evals/schemas").glob("*.json")),
    ]
    for schema_path in schema_paths:
        Draft202012Validator.check_schema(read_json(schema_path))


def test_failure_takes_precedence_over_review() -> None:
    verdict = HarnessRunner._aggregate_verdict(
        [
            EvaluatorResult("review", EvaluationStatus.REVIEW_REQUIRED, "review"),
            EvaluatorResult("failure", EvaluationStatus.FAIL, "failure"),
        ]
    )

    assert verdict == EvaluationStatus.FAIL


def _validate_results(summary: dict[str, object]) -> None:
    schema = read_json(REPO_ROOT / "evals/schemas/evaluation_result.schema.json")
    validator = Draft202012Validator(schema)
    for case in summary["cases"]:  # type: ignore[index]
        errors = list(validator.iter_errors(case))
        assert errors == []
