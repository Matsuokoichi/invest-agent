from __future__ import annotations

from typing import Any

from eval_harness.models import EvaluationStatus, EvaluatorResult


def passed(evaluator_id: str, summary: str) -> EvaluatorResult:
    return EvaluatorResult(evaluator_id, EvaluationStatus.PASS, summary)


def failed(
    evaluator_id: str, summary: str, details: list[dict[str, Any]]
) -> EvaluatorResult:
    return EvaluatorResult(evaluator_id, EvaluationStatus.FAIL, summary, details)


def not_applicable(evaluator_id: str, summary: str) -> EvaluatorResult:
    return EvaluatorResult(evaluator_id, EvaluationStatus.NOT_APPLICABLE, summary)
