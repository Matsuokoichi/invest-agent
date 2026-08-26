from __future__ import annotations

from typing import ClassVar

from eval_harness.models import EvaluationContext, EvaluatorResult

from .base import failed, passed


class RequiredContractEvaluator:
    evaluator_id = "C002"
    required_artifacts: ClassVar[frozenset[str]] = frozenset(
        {
            "report.json",
            "report.md",
            "trace.jsonl",
            "sources.json",
            "calculations.json",
            "run_manifest.json",
        }
    )

    def evaluate(self, context: EvaluationContext) -> EvaluatorResult:
        details: list[dict[str, object]] = []
        actual_artifacts = {
            path.name for path in context.run_directory.iterdir() if path.is_file()
        }
        missing = sorted(self.required_artifacts - actual_artifacts)
        if missing:
            details.append(
                {
                    "path": str(context.run_directory),
                    "expected": sorted(self.required_artifacts),
                    "actual": sorted(actual_artifacts),
                    "reason": f"Missing artifacts: {', '.join(missing)}",
                }
            )

        expected_report = context.case.get("expected_report", {})
        if context.report is None:
            details.append(
                {
                    "path": "report.json",
                    "expected": "loadable JSON object",
                    "actual": context.report_load_error,
                }
            )
        else:
            for field, expected in (
                ("status", expected_report.get("status")),
                (
                    "recommendation/action",
                    expected_report.get("recommendation"),
                ),
            ):
                if expected is None:
                    continue
                actual = (
                    context.report.get("status")
                    if field == "status"
                    else context.report.get("recommendation", {}).get("action")
                )
                if actual != expected:
                    details.append(
                        {
                            "path": field,
                            "expected": expected,
                            "actual": actual,
                        }
                    )

        if details:
            return failed(
                self.evaluator_id,
                "Required Agent artifact contract is not satisfied",
                details,
            )
        return passed(self.evaluator_id, "Required Agent artifacts are present")
