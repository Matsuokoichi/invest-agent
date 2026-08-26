from __future__ import annotations

import math
from typing import Any

from eval_harness.models import EvaluationContext, EvaluatorResult

from .base import failed, not_applicable, passed


def _annualize(total_return: float, horizon_months: int) -> float:
    return math.pow(1.0 + total_return, 12.0 / horizon_months) - 1.0


def _close(actual: Any, expected: Any, tolerance: float) -> bool:
    if actual is None or expected is None:
        return actual is expected
    return math.isclose(
        float(actual),
        float(expected),
        rel_tol=tolerance,
        abs_tol=tolerance,
    )


class ReturnArithmeticEvaluator:
    evaluator_id = "N001"

    def evaluate(self, context: EvaluationContext) -> EvaluatorResult:
        report = context.report
        if report is None:
            return not_applicable(self.evaluator_id, "report.json is unavailable")
        if report.get("status") == "UNSUPPORTED":
            return not_applicable(self.evaluator_id, "UNSUPPORTED report")

        tolerance = float(context.case.get("numeric_tolerance", 1e-9))
        details: list[dict[str, Any]] = []
        market = report["market"]
        scope = report["scope"]
        recommendation = report["recommendation"]
        current_price = float(market["current_price"])
        horizon = int(scope["investment_horizon_months"])
        scenario_results: dict[str, float] = {}

        for index, scenario in enumerate(report["scenarios"]):
            expected_total = (
                float(scenario["target_value_at_horizon"])
                + float(scenario["cumulative_dividends"])
                - current_price
            ) / current_price
            expected_annualized = _annualize(expected_total, horizon)
            scenario_results[scenario["name"]] = expected_total
            self._compare(
                details,
                f"/scenarios/{index}/total_return",
                scenario["total_return"],
                expected_total,
                tolerance,
            )
            self._compare(
                details,
                f"/scenarios/{index}/annualized_return",
                scenario["annualized_return"],
                expected_annualized,
                tolerance,
            )

        probabilities = [scenario["probability"] for scenario in report["scenarios"]]
        if all(probability is not None for probability in probabilities):
            expected_total_return = sum(
                float(scenario["probability"]) * scenario_results[scenario["name"]]
                for scenario in report["scenarios"]
            )
            expected_annualized_return = _annualize(expected_total_return, horizon)
            risk_premium = expected_annualized_return - float(market["treasury_yield"])
        else:
            expected_total_return = None
            expected_annualized_return = None
            risk_premium = None

        base_return = scenario_results.get("Base")
        base_intrinsic = float(recommendation["intrinsic_value_as_of_range"]["base"])
        margin_of_safety = (base_intrinsic - current_price) / base_intrinsic
        decision_hurdle = max(0.10, float(market["treasury_yield"]) + 0.05)

        expected_fields = {
            "/recommendation/base_case_total_return": base_return,
            "/recommendation/expected_total_return": expected_total_return,
            "/recommendation/expected_annualized_return": expected_annualized_return,
            "/recommendation/risk_premium": risk_premium,
            "/recommendation/margin_of_safety": margin_of_safety,
            "/recommendation/decision_hurdle": decision_hurdle,
        }
        for path, expected in expected_fields.items():
            key = path.rsplit("/", 1)[-1]
            self._compare(
                details,
                path,
                recommendation.get(key),
                expected,
                tolerance,
            )

        if details:
            return failed(
                self.evaluator_id,
                f"{len(details)} arithmetic discrepancy(s)",
                details,
            )
        return passed(self.evaluator_id, "Return arithmetic is reproducible")

    @staticmethod
    def _compare(
        details: list[dict[str, Any]],
        path: str,
        actual: Any,
        expected: Any,
        tolerance: float,
    ) -> None:
        if not _close(actual, expected, tolerance):
            details.append(
                {
                    "path": path,
                    "expected": expected,
                    "actual": actual,
                    "tolerance": tolerance,
                }
            )


class ScenarioIntegrityEvaluator:
    evaluator_id = "N003"

    def evaluate(self, context: EvaluationContext) -> EvaluatorResult:
        report = context.report
        if report is None:
            return not_applicable(self.evaluator_id, "report.json is unavailable")
        if report.get("status") == "UNSUPPORTED":
            return not_applicable(self.evaluator_id, "UNSUPPORTED report")

        tolerance = float(context.case.get("numeric_tolerance", 1e-9))
        scenarios = report.get("scenarios", [])
        details: list[dict[str, Any]] = []
        names = [scenario.get("name") for scenario in scenarios]
        if len(scenarios) != 3 or set(names) != {"Bear", "Base", "Bull"}:
            details.append(
                {
                    "path": "/scenarios",
                    "expected": ["Bear", "Base", "Bull"],
                    "actual": names,
                }
            )

        probabilities = [scenario.get("probability") for scenario in scenarios]
        all_null = all(value is None for value in probabilities)
        all_numeric = all(
            isinstance(value, (int, float)) and not isinstance(value, bool)
            for value in probabilities
        )
        if not all_null and not all_numeric:
            details.append(
                {
                    "path": "/scenarios/*/probability",
                    "expected": "all numeric or all null",
                    "actual": probabilities,
                }
            )
        elif all_numeric:
            probability_sum = sum(float(value) for value in probabilities)
            if not math.isclose(
                probability_sum, 1.0, rel_tol=tolerance, abs_tol=tolerance
            ):
                details.append(
                    {
                        "path": "/scenarios/*/probability",
                        "expected": 1.0,
                        "actual": probability_sum,
                    }
                )
            invalid_steps = [
                value
                for value in probabilities
                if not math.isclose(
                    float(value) * 20,
                    round(float(value) * 20),
                    rel_tol=tolerance,
                    abs_tol=tolerance,
                )
            ]
            if invalid_steps:
                details.append(
                    {
                        "path": "/scenarios/*/probability",
                        "expected": "5% increments",
                        "actual": invalid_steps,
                    }
                )

        by_name = {
            scenario.get("name"): scenario
            for scenario in scenarios
            if scenario.get("name") in {"Bear", "Base", "Bull"}
        }
        if len(by_name) == 3:
            for field in (
                "intrinsic_value_as_of",
                "target_value_at_horizon",
                "total_return",
            ):
                values = [
                    float(by_name[name][field]) for name in ("Bear", "Base", "Bull")
                ]
                if values != sorted(values):
                    details.append(
                        {
                            "path": f"/scenarios/*/{field}",
                            "expected": "Bear <= Base <= Bull",
                            "actual": values,
                        }
                    )

        recommendation = report.get("recommendation", {})
        if all_null:
            for field in (
                "expected_total_return",
                "expected_annualized_return",
                "risk_premium",
            ):
                if recommendation.get(field) is not None:
                    details.append(
                        {
                            "path": f"/recommendation/{field}",
                            "expected": None,
                            "actual": recommendation.get(field),
                        }
                    )
            if recommendation.get("action") != "WATCH":
                details.append(
                    {
                        "path": "/recommendation/action",
                        "expected": "WATCH",
                        "actual": recommendation.get("action"),
                    }
                )

        if details:
            return failed(
                self.evaluator_id,
                f"{len(details)} scenario integrity violation(s)",
                details,
            )
        return passed(self.evaluator_id, "Scenario structure is internally consistent")
