from __future__ import annotations

from eval_harness.models import EvaluationContext, EvaluatorResult

from .base import failed, not_applicable, passed


class DecisionPolicyEvaluator:
    evaluator_id = "D001"

    def evaluate(self, context: EvaluationContext) -> EvaluatorResult:
        report = context.report
        if report is None:
            return not_applicable(self.evaluator_id, "report.json is unavailable")

        status = report.get("status")
        recommendation = report.get("recommendation", {})
        actual = recommendation.get("action")
        decision_context = context.case.get("decision_context", {})

        if status == "UNSUPPORTED":
            expected = "NO_RATING"
        elif status == "INCOMPLETE":
            expected = "WATCH"
        elif (
            decision_context.get("thesis_invalidated")
            or decision_context.get("severe_governance_issue")
            or decision_context.get("downside_asymmetry_unacceptable")
        ):
            expected = "AVOID"
        elif decision_context.get("critical_evidence_gaps"):
            expected = "WATCH"
        else:
            expected_return = recommendation.get("expected_annualized_return")
            confidence = recommendation.get("confidence")
            current_price = float(report["market"]["current_price"])
            base_intrinsic = float(
                recommendation["intrinsic_value_as_of_range"]["base"]
            )
            if expected_return is None:
                expected = "WATCH"
            elif float(expected_return) <= 0 or (
                confidence in {"Medium", "High"} and base_intrinsic <= current_price
            ):
                expected = "AVOID"
            elif (
                confidence == "Low"
                or float(expected_return) < float(recommendation["decision_hurdle"])
                or float(recommendation["margin_of_safety"]) < 0.15
            ):
                expected = "WATCH"
            else:
                expected = "BUY"

        if actual != expected:
            return failed(
                self.evaluator_id,
                "Recommendation violates the V1 decision policy",
                [
                    {
                        "path": "/recommendation/action",
                        "expected": expected,
                        "actual": actual,
                    }
                ],
            )
        return passed(
            self.evaluator_id,
            f"Recommendation {actual} is policy-consistent",
        )
