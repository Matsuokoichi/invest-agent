from __future__ import annotations

from jsonschema import Draft202012Validator, FormatChecker

from eval_harness.io import read_json
from eval_harness.models import EvaluationContext, EvaluatorResult

from .base import failed, passed


class ReportSchemaEvaluator:
    evaluator_id = "C001"

    def evaluate(self, context: EvaluationContext) -> EvaluatorResult:
        if context.report is None:
            return failed(
                self.evaluator_id,
                "report.json could not be loaded",
                [{"actual": context.report_load_error or "missing report.json"}],
            )

        schema = read_json(context.repo_root / "docs/report_schema.json")
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(
            validator.iter_errors(context.report),
            key=lambda error: [str(part) for part in error.absolute_path],
        )
        if not errors:
            return passed(self.evaluator_id, "report.json satisfies the V1 schema")

        details = [
            {
                "path": "/" + "/".join(map(str, error.absolute_path)),
                "actual": error.instance,
                "reason": error.message,
            }
            for error in errors
        ]
        return failed(
            self.evaluator_id,
            f"{len(details)} report schema violation(s)",
            details,
        )
