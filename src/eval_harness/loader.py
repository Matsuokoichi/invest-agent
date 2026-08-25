from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .io import read_json, resolve_inside


def _validate(document: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    if errors:
        rendered = "; ".join(
            f"{'/'.join(map(str, error.path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ValueError(f"Invalid {label}: {rendered}")


def load_suite(repo_root: Path, suite_path: Path) -> tuple[dict[str, Any], list[tuple[Path, dict[str, Any]]]]:
    suite_path = resolve_inside(repo_root, suite_path)
    suite = read_json(suite_path)
    _validate(suite, repo_root / "evals/schemas/suite.schema.json", "suite")

    cases: list[tuple[Path, dict[str, Any]]] = []
    for relative_case_path in suite["cases"]:
        case_path = resolve_inside(repo_root, suite_path.parent / relative_case_path)
        case = read_json(case_path)
        _validate(case, repo_root / "evals/schemas/case.schema.json", f"case {case_path}")
        cases.append((case_path, case))
    return suite, cases

