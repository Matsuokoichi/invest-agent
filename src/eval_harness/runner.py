from __future__ import annotations

import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .adapter import FixtureAdapter
from .evaluators import EVALUATOR_REGISTRY
from .io import read_json, write_json
from .loader import load_suite
from .models import (
    CaseResult,
    EvaluationContext,
    EvaluationStatus,
    EvaluatorResult,
)


class HarnessRunner:
    def __init__(self, repo_root: Path, output_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.output_root = output_root.resolve()
        self.adapter = FixtureAdapter()

    def run_suite(self, suite_path: Path) -> dict[str, Any]:
        started_at = datetime.now(UTC)
        suite, cases = load_suite(self.repo_root, suite_path)
        run_id = self._new_run_id(suite["suite_id"])
        suite_directory = self.output_root / run_id
        suite_directory.mkdir(parents=True, exist_ok=False)

        results = [
            self._run_case(run_id, case_path, case, suite_directory)
            for case_path, case in cases
        ]
        summary = {
            "suite_id": suite["suite_id"],
            "run_id": run_id,
            "protocol_version": suite["protocol_version"],
            "started_at": started_at.isoformat(),
            "completed_at": datetime.now(UTC).isoformat(),
            "cases": [result.to_dict() for result in results],
            "case_count": len(results),
            "expectations_met": sum(result.expectation_met for result in results),
            "success": all(result.expectation_met for result in results),
        }
        write_json(suite_directory / "suite_summary.json", summary)
        return summary

    def _run_case(
        self,
        run_id: str,
        case_path: Path,
        case: dict[str, Any],
        suite_directory: Path,
    ) -> CaseResult:
        case_directory = suite_directory / case["case_id"]
        self.adapter.execute(self.repo_root, case_path, case, case_directory)

        report = None
        report_load_error = None
        report_path = case_directory / "report.json"
        try:
            report = read_json(report_path)
        except Exception as error:  # noqa: BLE001 - C001/C002 report the failure.
            report_load_error = str(error)

        context = EvaluationContext(
            repo_root=self.repo_root,
            case_path=case_path,
            case=case,
            run_directory=case_directory,
            report=report,
            report_load_error=report_load_error,
        )
        evaluator_results = [
            self._run_evaluator(evaluator_id, context)
            for evaluator_id in case["evaluators"]
        ]
        verdict = self._aggregate_verdict(evaluator_results)
        expectation_met = self._expectation_met(case, verdict, evaluator_results)
        result = CaseResult(
            case_id=case["case_id"],
            run_id=run_id,
            verdict=verdict,
            expectation_met=expectation_met,
            evaluator_results=evaluator_results,
            run_directory=case_directory,
        )
        write_json(case_directory / "evaluation.json", result.to_dict())
        return result

    def _run_evaluator(
        self, evaluator_id: str, context: EvaluationContext
    ) -> EvaluatorResult:
        evaluator_type = EVALUATOR_REGISTRY.get(evaluator_id)
        if evaluator_type is None:
            return EvaluatorResult(
                evaluator_id,
                EvaluationStatus.ERROR,
                f"Unknown evaluator: {evaluator_id}",
            )
        try:
            return evaluator_type().evaluate(context)
        except Exception as error:  # noqa: BLE001 - isolate evaluator failures.
            return EvaluatorResult(
                evaluator_id,
                EvaluationStatus.ERROR,
                str(error),
                [{"traceback": traceback.format_exc()}],
            )

    @staticmethod
    def _aggregate_verdict(
        evaluator_results: list[EvaluatorResult],
    ) -> EvaluationStatus:
        statuses = {result.status for result in evaluator_results}
        if EvaluationStatus.ERROR in statuses:
            return EvaluationStatus.ERROR
        if EvaluationStatus.FAIL in statuses:
            return EvaluationStatus.FAIL
        if EvaluationStatus.REVIEW_REQUIRED in statuses:
            return EvaluationStatus.REVIEW_REQUIRED
        return EvaluationStatus.PASS

    @staticmethod
    def _expectation_met(
        case: dict[str, Any],
        verdict: EvaluationStatus,
        evaluator_results: list[EvaluatorResult],
    ) -> bool:
        expectation = case["expected_harness"]
        if verdict.value != expectation["verdict"]:
            return False
        actual_failed = {
            result.evaluator_id
            for result in evaluator_results
            if result.status == EvaluationStatus.FAIL
        }
        return set(expectation.get("failed_evaluators_contains", [])).issubset(
            actual_failed
        )

    @staticmethod
    def _new_run_id(suite_id: str) -> str:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        return f"{suite_id}-{timestamp}-{uuid4().hex[:8]}"


def render_summary(summary: dict[str, Any]) -> str:
    lines = [
        f"Suite: {summary['suite_id']}",
        f"Run: {summary['run_id']}",
        (f"Expectations: {summary['expectations_met']}/{summary['case_count']}"),
    ]
    for case in summary["cases"]:
        marker = "OK" if case["expectation_met"] else "MISMATCH"
        lines.append(f"[{marker}] {case['case_id']}: {case['verdict']}")
    lines.append("SUCCESS" if summary["success"] else "FAILED")
    return "\n".join(lines)
