from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class EvaluationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    ERROR = "ERROR"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(slots=True)
class EvaluatorResult:
    evaluator_id: str
    status: EvaluationStatus
    summary: str
    details: list[dict[str, Any]] = field(default_factory=list)
    version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluator_id": self.evaluator_id,
            "version": self.version,
            "status": self.status.value,
            "summary": self.summary,
            "details": self.details,
        }


@dataclass(slots=True)
class EvaluationContext:
    repo_root: Path
    case_path: Path
    case: dict[str, Any]
    run_directory: Path
    report: dict[str, Any] | None
    report_load_error: str | None = None


@dataclass(slots=True)
class CaseResult:
    case_id: str
    run_id: str
    verdict: EvaluationStatus
    expectation_met: bool
    evaluator_results: list[EvaluatorResult]
    run_directory: Path

    def to_dict(self) -> dict[str, Any]:
        failed = [
            result.evaluator_id
            for result in self.evaluator_results
            if result.status == EvaluationStatus.FAIL
        ]
        review = [
            result.evaluator_id
            for result in self.evaluator_results
            if result.status == EvaluationStatus.REVIEW_REQUIRED
        ]
        errors = [
            result.evaluator_id
            for result in self.evaluator_results
            if result.status == EvaluationStatus.ERROR
        ]
        return {
            "case_id": self.case_id,
            "run_id": self.run_id,
            "verdict": self.verdict.value,
            "expectation_met": self.expectation_met,
            "hard_gates": {
                "passed": sum(
                    result.status == EvaluationStatus.PASS
                    for result in self.evaluator_results
                ),
                "failed": len(failed),
                "review_required": len(review),
                "errors": len(errors),
            },
            "quality": None,
            "forward_outcome": None,
            "failed_evaluators": failed,
            "review_evaluators": review,
            "error_evaluators": errors,
            "evaluator_results": [
                result.to_dict() for result in self.evaluator_results
            ],
            "artifact_paths": {
                "run_directory": str(self.run_directory),
            },
            "versions": {
                "harness": __import__("eval_harness").__version__,
                "protocol": "1.0.0",
            },
        }

